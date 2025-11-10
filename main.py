#!/usr/bin/env python3
from pathlib import Path
import wave, sys

MODEL = Path("models/ml_IN-arjun-medium.onnx")
OUT = Path("output.wav")
TEXT = (
    "ഡൽഹി സ്ഫോടനത്തിൽ പൊട്ടിത്തെറിച്ചത് ഐ20 കാറെന്ന് ഡൽഹി പോലീസ്. "
    "വാഹനത്തിൽ ഉണ്ടായിരുന്നത് മൂന്ന് പേർ എന്ന് വിവരം. "
    "സ്ഫോടനം സംഭവിച്ചത് വാഹനത്തിന്റെ പുറകിൽ നിന്ന് എന്നും സൂചന. "
    "ഓൾഡ് ഡൽഹി മുതൽ ഉള്ള സിസിടിവി ദൃശ്യങ്ങൾ പോലീസ് ശേഖരിക്കുന്നു. "
    "സ്ഫോടനത്തെത്തുടർന്ന്, വിമാനത്താവളങ്ങൾ, ഡൽഹി മെട്രോ, സർക്കാർ കെട്ടിടങ്ങൾ, "
    "മറ്റ് പ്രധാന സ്ഥാപനങ്ങൾ എന്നിവയുയൽകൊണ്ട് സിഐഎസ്എഫ് അതീവ ജാഗ്രത നിര്‍ദേശിച്ചു."
)

def load():
    try:
        from piper.voice import PiperVoice
        return PiperVoice.load(str(MODEL))
    except Exception:
        from piper import PiperVoice
        return (PiperVoice.load(str(MODEL)) if hasattr(PiperVoice, "load") else PiperVoice(str(MODEL)))

def write_wav_bytes(b: bytes, rate=24000, chans=1, width=2):
    with wave.open(str(OUT), "wb") as w:
        w.setnchannels(chans); w.setsampwidth(width); w.setframerate(rate)
        w.writeframes(b)

def main():
    if not MODEL.exists(): 
        print("Model not found:", MODEL); sys.exit(1)
    v = load()
    # Preferred API
    if hasattr(v, "synthesize_wav"):
        try:
            with wave.open(str(OUT), "wb") as wf:
                v.synthesize_wav(TEXT, wf)
            if OUT.stat().st_size:
                print("✅", OUT); return
        except Exception as e:
            print("synthesize_wav failed:", e)
    # Fallback: iterable of chunks
    if hasattr(v, "synthesize"):
        try:
            chunks = list(v.synthesize(TEXT))
            if not chunks:
                raise RuntimeError("empty chunks")
            # prefer .data attr or raw bytes
            frames = []
            for c in chunks:
                if isinstance(c, (bytes, bytearray)): frames.append(bytes(c))
                elif hasattr(c, "data"): frames.append(bytes(getattr(c, "data")))
                elif hasattr(c, "samples"): frames.append(bytes(getattr(c, "samples")))
                else: frames.append(bytes(c))
            raw = b"".join(frames)
            # heuristics for sample rate/width/channels
            first = chunks[0]
            rate = next((int(getattr(first, a)) for a in ("sample_rate","rate","sampleRate") if hasattr(first,a)), 24000)
            chans = next((int(getattr(first, a)) for a in ("channels","num_channels") if hasattr(first,a)), 1)
            width = next((int(getattr(first, a)) for a in ("sample_width","sampleWidth","bytes_per_sample") if hasattr(first,a)), 2)
            write_wav_bytes(raw, rate, chans, width)
            if OUT.stat().st_size:
                print("✅", OUT); return
        except Exception as e:
            print("fallback failed:", e)
    print("❌ synthesis failed. Run the debug script if needed.")

if __name__ == "__main__":
    main()
