#!/usr/bin/env python3
"""Derive the console presenter glow from this episode's imported voice.wav."""
from array import array
import hashlib
import json
import math
from pathlib import Path
import sys
import wave


def voice_envelope(path: Path, fps: int = 60) -> list[float]:
    with wave.open(str(path), "rb") as stream:
        if stream.getsampwidth() != 2 or stream.getcomptype() != "NONE":
            raise ValueError("Imported voice.wav must be uncompressed 16-bit PCM")
        rate, channels, count = stream.getframerate(), stream.getnchannels(), stream.getnframes()
        if not count or channels < 1:
            raise ValueError("Imported voice.wav is empty")
        samples = array("h", stream.readframes(count))
    if sys.byteorder != "little":
        samples.byteswap()
    envelope = []
    for frame in range(math.ceil(count * fps / rate)):
        first, last = frame * rate // fps, min(count, (frame + 1) * rate // fps)
        values = samples[first * channels:last * channels]
        envelope.append(math.sqrt(sum(float(v) * v for v in values) / max(1, len(values))) / 32768)
    ordered = sorted(envelope)
    ceiling = max(ordered[min(len(ordered) - 1, round(len(ordered) * .95))], 1e-8)
    # Fixed, seek-independent envelope. No source narration samples are copied.
    return [round(min(1, level / ceiling), 6) for level in envelope]


def prepare(project: Path) -> dict:
    project = project.resolve()
    voice = project / "voice.wav"
    values = voice_envelope(voice)
    report = {"schema": "adu-doubao-episode/1", "fps": 60, "clock": "output",
              "voiceSha256": hashlib.sha256(voice.read_bytes()).hexdigest(),
              "frames": len(values), "method": "per-frame-pcm-rms/p95-clamp",
              "limits": ["New narration envelope; original voice-derived vox.js is not reused."]}
    (project / "doubao_episode.js").write_text("window.DOUBAO_OUTPUT_VOX=" + json.dumps(values) + ";\n")
    (project / "doubao_episode.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    try:
        if len(sys.argv) != 2:
            raise ValueError("Usage: prepare_episode.py PROJECT_WITH_IMPORTED_VOICE")
        print(json.dumps(prepare(Path(sys.argv[1]))))
    except (ValueError, OSError, wave.Error) as exc:
        raise SystemExit(f"Doubao episode preparation failed: {exc}") from exc
