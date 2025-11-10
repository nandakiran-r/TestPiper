# app.py
import io
import wave
from pathlib import Path
import streamlit as st

DEFAULT_MODEL = "models/ml_IN-arjun-medium.onnx"
DEFAULT_TEXT = (
    "ഡൽഹി സ്ഫോടനത്തിൽ പൊട്ടിത്തെറിച്ചത് ഐ20 കാറെന്ന് ഡൽഹി പൊലീസ്. "
    "വാഹനത്തിൽ ഉണ്ടായിരുന്നത് മൂന്ന് പേർ എന്നതാണ് വിവരം. "
    "സ്ഫോടനം സംഭവിച്ചത് വാഹനത്തിന്റെ പുറകിൽ നിന്ന് എന്നും സൂചന. "
    "ഓൾഡ് ഡൽഹി മുതൽ ഉള്ള സിസിടിവി ദൃശ്യങ്ങൾ പോലീസ് ശേഖരിക്കുന്നു. "
    "ക്രമത്തിൽ, വിമാനത്താവളങ്ങൾ, ഡൽഹി മെട്രോ, സർക്കാർ കെട്ടിടങ്ങൾ, "
    "മറ്റ് പ്രധാന സ്ഥാപനങ്ങൾ എന്നിവയുൾപ്പെടെ സിഐഎസ്എഫ് അതീവ ജാഗ്രതാ നിർദേശം നൽകി."
)

st.title("Piper Malayalam TTS — Streamlit")
model_path = st.text_input("Model path (.onnx)", value=DEFAULT_MODEL)
text = st.text_area("Text (Malayalam)", value=DEFAULT_TEXT, height=200)

@st.cache_resource
def load_voice(model_path_str: str):
    try:
        from piper.voice import PiperVoice
        return PiperVoice.load(model_path_str)
    except Exception:
        from piper import PiperVoice
        return (PiperVoice.load(model_path_str) if hasattr(PiperVoice, "load") else PiperVoice(model_path_str))

def synthesize_bytes(voice, txt: str) -> bytes:
    """
    Prefer voice.synthesize_wav(wave_write). Fallback to voice.synthesize(...) iterable.
    Returns WAV bytes.
    """
    # Try synthesize_wav into BytesIO
    bio = io.BytesIO()
    try:
        with wave.open(bio, "wb") as wf:
            # let voice set WAV format/header if it supports that (it writes frames to the wave_write)
            if hasattr(voice, "synthesize_wav"):
                voice.synthesize_wav(txt, wf)
            else:
                raise AttributeError("no synthesize_wav")
        bio.seek(0)
        if bio.getbuffer().nbytes > 44:  # simple sanity check for non-empty WAV
            return bio.read()
    except Exception:
        pass

    # Fallback: iterable of chunks -> coerce to raw frames, then write WAV header
    try:
        chunks = list(voice.synthesize(txt))
        if not chunks:
            raise RuntimeError("empty synthesis result")
        frames = []
        first = chunks[0]
        # gather bytes from each chunk
        for c in chunks:
            if isinstance(c, (bytes, bytearray)):
                frames.append(bytes(c))
            elif hasattr(c, "data"):
                frames.append(bytes(getattr(c, "data")))
            elif hasattr(c, "samples"):
                frames.append(bytes(getattr(c, "samples")))
            else:
                frames.append(bytes(c))
        raw = b"".join(frames)
        # heuristics for rate/channels/width
        def _getattr_any(obj, names, default=None):
            for n in names:
                if hasattr(obj, n):
                    return getattr(obj, n)
            return default
        sr = int(_getattr_any(first, ("sample_rate","rate","sampleRate")) or 24000)
        ch = int(_getattr_any(first, ("channels","num_channels","numChannels")) or 1)
        sw = int(_getattr_any(first, ("sample_width","sampleWidth","bytes_per_sample")) or 2)
        bio = io.BytesIO()
        with wave.open(bio, "wb") as wf:
            wf.setnchannels(ch)
            wf.setsampwidth(int(sw))
            wf.setframerate(int(sr))
            wf.writeframes(raw)
        bio.seek(0)
        return bio.read()
    except Exception as e:
        raise RuntimeError(f"Synthesis failed: {e}")

col1, col2 = st.columns([3,1])
with col1:
    if st.button("Synthesize"):
        mp = Path(model_path)
        if not mp.exists():
            st.error(f"Model not found: {mp}")
        else:
            try:
                with st.spinner("Loading model..."):
                    voice = load_voice(str(mp))
                with st.spinner("Synthesizing..."):
                    wav_bytes = synthesize_bytes(voice, text)
                st.success("Synthesis complete")
                st.audio(wav_bytes, format="audio/wav")
                st.download_button("Download WAV", wav_bytes, file_name="output.wav", mime="audio/wav")
            except Exception as e:
                st.exception(e)

with col2:
    st.write("Model status")
    st.write(f"Path: `{model_path}`")
    st.write("Tip: put `.onnx` and `.onnx.json` in same folder.")
    st.markdown("Run: `streamlit run app.py`")

st.caption("Requires: piper-tts, streamlit. Install via `pip install piper-tts streamlit`")
