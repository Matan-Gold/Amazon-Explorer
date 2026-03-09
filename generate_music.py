#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_music.py - Generate ambient music for Amazon Rainforest Explorer using MusicGen.

Uses the transformers library (Python 3.13 compatible).

Requirements:
    pip install transformers torch scipy

Run:
    python generate_music.py

Copy generated WAV files to:
    data/music/
"""

import sys
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "data" / "music"

TRACKS = {
    "music_exploration": {
        "prompt": (
            "Amazon rainforest overworld map music, mysterious adventure theme, "
            "pan flute melody, light marimba, gentle hand drum, magical exploration atmosphere, "
            "looping background, calm and uplifting, no lyrics, instrumental"
        ),
        "duration": 30,
    },
    "music_forest": {
        "prompt": (
            "lush Amazon rainforest ambient music, bird calls woven into gentle melody, "
            "wooden flute and soft strings, rustling leaves, warm sunlit atmosphere, "
            "serene and magical, looping background, no lyrics, instrumental"
        ),
        "duration": 30,
    },
    "music_river": {
        "prompt": (
            "Amazon river ambient music, flowing water sounds layered with marimba melody, "
            "light percussion, peaceful and refreshing, aquatic atmosphere, "
            "relaxing looping background, no lyrics, instrumental"
        ),
        "duration": 30,
    },
    "music_clearing": {
        "prompt": (
            "sunny Amazon jungle clearing music, bright uplifting melody, "
            "acoustic guitar and flute duet, cheerful percussion, warm open-air atmosphere, "
            "light and joyful, looping background, no lyrics, instrumental"
        ),
        "duration": 30,
    },
    "music_dense_jungle": {
        "prompt": (
            "dense Amazon jungle music, mysterious and atmospheric, deep bass drones, "
            "distant tribal drums, haunting bamboo flute echoes, night atmosphere, "
            "tense and magical, looping background, no lyrics, instrumental"
        ),
        "duration": 30,
    },
    "music_camp": {
        "prompt": (
            "peaceful jungle campfire night music, warm acoustic guitar fingerpicking, "
            "gentle bongo and soft shaker, distant cricket sounds, cozy adventure camp atmosphere, "
            "serene and comforting, soft ambient pads, no lyrics, instrumental loop"
        ),
        "duration": 30,
    },
    "discovery_stinger": {
        "prompt": (
            "short triumphant discovery fanfare, orchestral sting, "
            "adventure game reveal, bright brass and string ensemble, joyful and majestic, "
            "exciting discovery sound, cinematic"
        ),
        "duration": 4,
    },
}

PREFERRED_MODELS = [
    "facebook/musicgen-small",    # ~300 MB VRAM — reliable on most GPUs
    "facebook/musicgen-medium",   # ~1.5 GB VRAM — better quality if enough memory
]


def save_wav(audio, sample_rate, path):
    try:
        import torchaudio
        torchaudio.save(str(path), audio, sample_rate)
    except ImportError:
        import numpy as np
        import scipy.io.wavfile
        arr = audio.cpu().numpy()
        if arr.ndim == 2:
            arr = arr.T
        arr_int16 = (arr * 32767).clip(-32768, 32767).astype("int16")
        scipy.io.wavfile.write(str(path), sample_rate, arr_int16)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        import torch
        from transformers import AutoProcessor, MusicgenForConditionalGeneration
    except ImportError:
        print("ERROR: Missing packages. Run:")
        print("  pip install transformers torch scipy")
        sys.exit(1)

    # Force CPU — GPU state is unreliable after prior CUDA errors in this session.
    # CPU generation is slow (~5-10 min/track) but stable.
    device = "cpu"
    dtype = torch.float32
    print(f"\nDevice: {device}")

    model = None
    processor = None
    for model_id in PREFERRED_MODELS:
        print(f"\nLoading {model_id}...")
        try:
            processor = AutoProcessor.from_pretrained(model_id)
            model = MusicgenForConditionalGeneration.from_pretrained(
                model_id, torch_dtype=dtype
            )
            model = model.to(device)
            print(f"  Loaded: {model_id}")
            break
        except Exception as e:
            print(f"  Failed ({e}), trying next...")

    if model is None:
        print("ERROR: Could not load any model. Check your internet connection.")
        sys.exit(1)

    sample_rate = model.config.audio_encoder.sampling_rate
    total = len(TRACKS)

    for i, (name, info) in enumerate(TRACKS.items(), 1):
        out_path = OUTPUT_DIR / f"{name}.wav"
        if out_path.exists():
            print(f"\n[{i}/{total}] '{name}' already exists - skipping.")
            continue

        print(f"\n[{i}/{total}] Composing '{name}' ({info['duration']}s)...")

        inputs = processor(
            text=[info["prompt"]],
            padding=True,
            return_tensors="pt",
        ).to(device)

        # MusicGen generates at 50 tokens/second regardless of audio sample rate.
        # musicgen-small hard limit is 1503 tokens (~30 s); cap to be safe.
        max_tokens = min(int(info["duration"] * 50), 1500)

        import torch
        with torch.no_grad():
            audio_values = model.generate(**inputs, max_new_tokens=max_tokens)

        # audio_values: [batch, channels, samples]
        audio = audio_values[0]  # [channels, samples]
        save_wav(audio, sample_rate, out_path)
        print(f"  Saved: {out_path}")

    print(f"\nDone! Music files in:\n  {OUTPUT_DIR}")
    print("\nTracks:")
    for name in TRACKS:
        p = OUTPUT_DIR / f"{name}.wav"
        size_mb = p.stat().st_size / 1_048_576 if p.exists() else 0
        print(f"  {name}.wav  ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
