import io
import wave
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydub import AudioSegment, effects

# ---------------- CONFIGURATION ----------------
# Path to your .onnx model. Ensure this file exists locally.
MODEL_PATH = "models/ml_IN-arjun-medium.onnx"

# Global variable to store the loaded voice model
voice_model = None

# ---------------- HELPER FUNCTIONS ----------------
def load_piper_model(model_path_str: str):
    """Loads the Piper voice model."""
    print(f"Loading model from: {model_path_str}")
    try:
        from piper.voice import PiperVoice
        return PiperVoice.load(model_path_str)
    except ImportError:
        # Fallback for older versions or specific package structures
        from piper import PiperVoice
        if hasattr(PiperVoice, "load"):
            return PiperVoice.load(model_path_str)
        return PiperVoice(model_path_str)

def synthesize_bytes(voice, txt: str) -> bytes:
    """Generate WAV audio bytes from text using Piper."""
    bio = io.BytesIO()
    try:
        # Try direct wav synthesis first
        with wave.open(bio, "wb") as wf:
            if hasattr(voice, "synthesize_wav"):
                voice.synthesize_wav(txt, wf)
            else:
                raise AttributeError("no synthesize_wav method")
        bio.seek(0)
        # Check if valid wav (header > 44 bytes)
        if bio.getbuffer().nbytes > 44:
            return bio.read()
    except Exception as e:
        print(f"Direct synthesis failed, trying raw stream: {e}")
    
    # Fallback: Synthesize raw PCM and write to WAV container
    chunks = list(voice.synthesize(txt))
    if not chunks:
        raise ValueError("No audio generated")
        
    frames = []
    first = chunks[0]
    for c in chunks:
        # Extract bytes depending on object structure
        data = getattr(c, "data", getattr(c, "samples", c))
        frames.append(bytes(data))
    
    raw = b"".join(frames)
    sr = getattr(first, "sample_rate", 24000)
    ch = getattr(first, "channels", 1)
    sw = getattr(first, "sample_width", 2)
    
    bio = io.BytesIO()
    with wave.open(bio, "wb") as wf:
        wf.setnchannels(ch)
        wf.setsampwidth(sw)
        wf.setframerate(sr)
        wf.writeframes(raw)
    bio.seek(0)
    return bio.read()

def process_audio_effects(
    wav_bytes: bytes,
    pitch: float = 0.0,
    speed: float = 100.0,
    bass: float = 0.0,
    treble: float = 0.0,
    gain: float = 0.0,
    normalize: bool = True,
) -> bytes:
    """Apply pitch, speed, EQ, gain, and normalization using Pydub."""
    # Load into Pydub
    audio = AudioSegment.from_file(io.BytesIO(wav_bytes), format="wav")

    # 1. Pitch Shift (by altering sample rate trick)
    # Note: This changes duration inversely to pitch (chipmunk effect)
    if pitch != 0:
        factor = 2 ** (pitch / 12.0)
        new_rate = int(audio.frame_rate * factor)
        # Keep raw data, just say "play it faster/slower"
        audio = audio._spawn(audio.raw_data, overrides={"frame_rate": new_rate})
        # Reset frame rate to standard (resampling) so player handles it correctly
        audio = audio.set_frame_rate(24000)

    # 2. Speed Adjustment (Playback Speed)
    if speed != 100:
        speed_factor = speed / 100.0
        new_rate = int(audio.frame_rate * speed_factor)
        audio = audio._spawn(audio.raw_data, overrides={"frame_rate": new_rate})
        audio = audio.set_frame_rate(24000)

    # 3. Equalization (Bass/Treble)
    if bass != 0:
        # Low pass filter < 150Hz
        audio = audio.low_pass_filter(150).apply_gain(bass).overlay(audio.high_pass_filter(150))
        # Note: Simple overlay approximation for EQ or use direct filtering + original mix
        # Implementing simple gain on filter for this example as per original logic request:
        # Original logic was: audio.low_pass_filter(150).apply_gain(bass) 
        # (This cuts all high freq and boosts low, creating muffled sound. 
        # Better approach for "Bass Boost" without losing highs is usually needed, 
        # but sticking to user's original logic pattern for consistency):
        # audio = audio.low_pass_filter(150).apply_gain(bass) 
        # HOWEVER, strictly filtering low pass destroys the rest of the speech. 
        # I will leave the original logic pattern but warn it might sound muffled if used alone.
        # To be safe, let's apply a shelf eq logic: 
        # (Boost lows) + (Original - Lows)
        pass # Pydub doesn't have built-in shelf EQ, using basic logic from original script:
        if bass > 0:
             audio = audio.low_pass_filter(200).apply_gain(bass).overlay(audio.high_pass_filter(200))

    if treble != 0:
        if treble > 0:
            audio = audio.high_pass_filter(3000).apply_gain(treble).overlay(audio.low_pass_filter(3000))

    # 4. Volume Gain
    if gain != 0:
        audio = audio.apply_gain(gain)

    # 5. Normalize
    if normalize:
        audio = effects.normalize(audio)

    # Export
    out = io.BytesIO()
    audio.export(out, format="wav")
    out.seek(0)
    return out.read()

# ---------------- LIFESPAN MANAGER ----------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load model on startup
    global voice_model
    path = Path(MODEL_PATH)
    if path.exists():
        try:
            voice_model = load_piper_model(str(path))
            print("✅ Model loaded successfully.")
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
    else:
        print(f"⚠️ Model file not found at {MODEL_PATH}. Requests will fail.")
    yield
    # Clean up resources if needed
    voice_model = None

# ---------------- API APP ----------------
app = FastAPI(title="Piper TTS API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
def home():
    return {"status": "running", "usage": "/tts?text=YourTextHere"}

@app.get("/tts")
async def generate_speech(
    text: str = Query(..., description="Malayalam text to synthesize"),
    pitch: float = Query(0.0, description="Pitch shift in semitones (-12.0 to 12.0)"),
    speed: int = Query(100, description="Speed percentage (50 to 200)"),
    bass: float = Query(0.0, description="Bass gain in dB (-15 to 15)"),
    treble: float = Query(0.0, description="Treble gain in dB (-15 to 15)"),
    gain: float = Query(0.0, description="Volume gain in dB (-20 to 20)"),
    normalize: bool = Query(True, description="Normalize audio volume"),
):
    global voice_model
    
    if not voice_model:
        raise HTTPException(status_code=503, detail="TTS Model is not loaded. Check server logs.")

    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        # 1. Synthesize raw audio
        raw_wav = synthesize_bytes(voice_model, text)
        
        if not raw_wav:
            raise HTTPException(status_code=500, detail="Synthesis failed to produce audio data")

        # 2. Post-process audio (pydub)
        final_audio = process_audio_effects(
            raw_wav,
            pitch=pitch,
            speed=speed,
            bass=bass,
            treble=treble,
            gain=gain,
            normalize=normalize
        )

        # 3. Return audio file
        return Response(content=final_audio, media_type="audio/wav")

    except Exception as e:
        print(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
