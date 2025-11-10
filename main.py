# app.py — Piper Malayalam TTS with full audio control
import io, wave
from pathlib import Path
import streamlit as st
from pydub import AudioSegment, effects

# ---------------- DEFAULT CONFIG ----------------
DEFAULT_MODEL = "models/ml_IN-arjun-medium.onnx"
DEFAULT_TEXT = (
    "ഡൽഹി സ്ഫോടനത്തിൽ പൊട്ടിത്തെറിച്ചത് ഐ20 കാറെന്ന് ഡൽഹി പൊലീസ്. "
    "വാഹനത്തിൽ ഉണ്ടായിരുന്നത് മൂന്ന് പേർ എന്നതാണ് വിവരം. "
    "സ്ഫോടനം സംഭവിച്ചത് വാഹനത്തിന്റെ പുറകിൽ നിന്ന് എന്നും സൂചന. "
    "ഓൾഡ് ഡൽഹി മുതൽ ഉള്ള സിസിടിവി ദൃശ്യങ്ങൾ പോലീസ് ശേഖരിക്കുന്നു. "
    "ക്രമത്തിൽ, വിമാനത്താവളങ്ങൾ, ഡൽഹി മെട്രോ, സർക്കാർ കെട്ടിടങ്ങൾ, "
    "മറ്റ് പ്രധാന സ്ഥാപനങ്ങൾ എന്നിവയുൾപ്പെടെ സിഐഎസ്എഫ് അതീവ ജാഗ്രതാ നിർദേശം നൽകി."
)

# ---------------- PAGE SETUP ----------------
st.set_page_config(page_title="Piper Malayalam TTS", layout="wide")
st.title("🎙️ Piper Malayalam TTS — Full Audio Controls")

# ---------------- SIDEBAR CONTROLS ----------------
with st.sidebar:
    st.header("🎚️ Audio Controls")
    pitch = st.slider("Pitch (semitones)", -12.0, 12.0, 0.0, 0.5)
    speed = st.slider("Speed (%)", 50, 200, 100, 5)
    bass = st.slider("Bass gain (dB)", -15, 15, 0, 1)
    treble = st.slider("Treble gain (dB)", -15, 15, 0, 1)
    gain = st.slider("Volume gain (dB)", -20, 20, 0, 1)
    normalize = st.checkbox("Normalize Volume", True)
    st.markdown("---")
    st.caption("Audio post-processing powered by **pydub + ffmpeg**")

# ---------------- TEXT INPUT ----------------
model_path = st.text_input("Model path (.onnx)", value=DEFAULT_MODEL)
text = st.text_area("Text (Malayalam)", value=DEFAULT_TEXT, height=200)

# ---------------- TTS LOADING ----------------
@st.cache_resource
def load_voice(model_path_str: str):
    try:
        from piper.voice import PiperVoice
        return PiperVoice.load(model_path_str)
    except Exception:
        from piper import PiperVoice
        return (
            PiperVoice.load(model_path_str)
            if hasattr(PiperVoice, "load")
            else PiperVoice(model_path_str)
        )

# ---------------- SYNTHESIS ----------------
def synthesize_bytes(voice, txt: str) -> bytes:
    """Generate WAV audio bytes from text using Piper."""
    bio = io.BytesIO()
    try:
        with wave.open(bio, "wb") as wf:
            if hasattr(voice, "synthesize_wav"):
                voice.synthesize_wav(txt, wf)
            else:
                raise AttributeError("no synthesize_wav")
        bio.seek(0)
        if bio.getbuffer().nbytes > 44:
            return bio.read()
    except Exception:
        pass

    # Fallback if synthesize_wav unavailable
    chunks = list(voice.synthesize(txt))
    frames = []
    first = chunks[0]
    for c in chunks:
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

# ---------------- AUDIO PROCESSING ----------------
def process_audio(
    wav_bytes: bytes,
    pitch: float = 0.0,
    speed: float = 100.0,
    bass: float = 0.0,
    treble: float = 0.0,
    gain: float = 0.0,
    normalize_audio: bool = True,
) -> bytes:
    """Apply pitch, speed, EQ, gain, and normalization to audio."""
    audio = AudioSegment.from_file(io.BytesIO(wav_bytes), format="wav")

    # Pitch shift (change sample rate)
    if pitch != 0:
        factor = 2 ** (pitch / 12.0)
        new_rate = int(audio.frame_rate * factor)
        audio = audio._spawn(audio.raw_data, overrides={"frame_rate": new_rate})
        audio = audio.set_frame_rate(24000)

    # Speed adjustment (change playback rate)
    if speed != 100:
        speed_factor = speed / 100.0
        new_rate = int(audio.frame_rate * speed_factor)
        audio = audio._spawn(audio.raw_data, overrides={"frame_rate": new_rate})
        audio = audio.set_frame_rate(24000)

    # Bass & Treble EQ
    if bass != 0:
        audio = audio.low_pass_filter(150).apply_gain(bass)
    if treble != 0:
        audio = audio.high_pass_filter(3000).apply_gain(treble)

    # Manual volume gain
    if gain != 0:
        audio += gain

    # Normalize
    if normalize_audio:
        audio = effects.normalize(audio)

    # Export back to WAV
    out = io.BytesIO()
    audio.export(out, format="wav")
    out.seek(0)
    return out.read()

# ---------------- UI LOGIC ----------------
if st.button("🎧 Synthesize & Play"):
    mp = Path(model_path)
    if not mp.exists():
        st.error(f"Model not found: {mp}")
    else:
        try:
            with st.spinner("Loading Piper model..."):
                voice = load_voice(str(mp))
            with st.spinner("Generating TTS audio..."):
                wav_bytes = synthesize_bytes(voice, text)
            with st.spinner("Applying audio filters..."):
                final_audio = process_audio(
                    wav_bytes,
                    pitch=pitch,
                    speed=speed,
                    bass=bass,
                    treble=treble,
                    gain=gain,
                    normalize_audio=normalize,
                )
            st.audio(final_audio, format="audio/wav")
            st.download_button(
                "⬇️ Download Processed WAV",
                final_audio,
                file_name="output_processed.wav",
                mime="audio/wav",
            )
            st.success("✅ TTS generation complete!")
        except Exception as e:
            st.exception(e)

st.caption("Requires: `pip install piper-tts streamlit pydub` and `ffmpeg`.")
