# -*- coding: utf-8 -*-
"""
asset_generator.py — Generates and caches AI scene backgrounds.

On first run downloads the model (~6 GB from HuggingFace) and generates
5 scene PNG files in data/images/.  Subsequent runs load them instantly.

Model used: Lykon/dreamshaper-xl-1-0  (SDXL fine-tune, no auth needed)
Fallback:   stabilityai/stable-diffusion-xl-base-1.0

Required packages (install once):
    pip install torch torchvision diffusers transformers accelerate Pillow
"""

from pathlib import Path
from typing import Callable

ASSETS_DIR = Path(__file__).parent / "data" / "images"

# SDXL generates at 1024×576 (closest 16:9); we crop to 1024×560 (game scene area)
GEN_W, GEN_H = 1024, 576
CROP_H = 560

# Preferred model → fallback model
_MODELS = [
    "Lykon/dreamshaper-xl-1-0",
    "stabilityai/stable-diffusion-xl-base-1.0",
]

# ── Prompts ────────────────────────────────────────────────────────────────────

SCENE_PROMPTS = {
    "Forest": (
        "lush Amazon rainforest scene, painterly fantasy illustration, ancient towering kapok trees "
        "with massive textured trunks, golden sunbeams through leafy green canopy, colorful macaw "
        "perched on branch, vibrant tropical orchids and heliconias in foreground, rich layered "
        "depth, warm afternoon light, magical adventure game background, no humans, masterpiece"
    ),
    "River": (
        "Amazon river scene, painterly fantasy illustration, wide crystal-clear turquoise river "
        "with shimmering reflections, lush tropical banks, pink Amazon river dolphin leaping, "
        "giant Victoria lily pads with pink flowers, colorful butterflies, tropical blue sky "
        "with clouds, magical adventure game background, no humans, masterpiece"
    ),
    "Clearing": (
        "Amazon rainforest sunny clearing, painterly fantasy illustration, bright open meadow "
        "with vivid green grass, colorful wildflowers and orchids, towering jungle trees forming "
        "a ring, brilliant blue sky, warm golden light, a morpho butterfly flying, "
        "magical adventure game background, no humans, masterpiece"
    ),
    "Dense Jungle": (
        "dense Amazon jungle interior, painterly fantasy illustration, dramatic mysterious "
        "atmosphere, ancient massive trees, dramatic shafts of golden light cutting through "
        "dark green canopy, hanging lianas and vines, giant exotic leaves, glowing "
        "bioluminescent mushrooms and flowers, deep rich greens, magical adventure game "
        "background, no humans, masterpiece"
    ),
    "Camp": (
        "cozy jungle campsite at night, painterly fantasy illustration, warm glowing campfire "
        "center stage, two colorful explorer tents flanking the fire, brilliant starry sky "
        "through jungle canopy clearing, fireflies dancing, warm orange firelight reflecting "
        "on surrounding trees, a cozy magical atmosphere, adventure game background, "
        "no humans, masterpiece"
    ),
}

NEGATIVE = (
    "text, watermark, signature, human face, person, ugly, blurry, low quality, "
    "nsfw, scary, dark horror, violence, realistic photography, 3d render, "
    "worst quality, cartoon, anime, sketch"
)

# Fixed seeds — same seed produces same image every run
_SEEDS = {
    "Forest":       42,
    "River":        123,
    "Clearing":     456,
    "Dense Jungle": 789,
    "Camp":         1011,
}


# ── Public API ─────────────────────────────────────────────────────────────────

def assets_complete() -> bool:
    """Return True only if every scene PNG exists on disk."""
    return all(
        (ASSETS_DIR / f"scene_{_slug(name)}.png").exists()
        for name in SCENE_PROMPTS
    )


def missing_scenes() -> list:
    """Return list of scene names that still need to be generated."""
    return [
        name for name in SCENE_PROMPTS
        if not (ASSETS_DIR / f"scene_{_slug(name)}.png").exists()
    ]


def generate_all(progress: Callable = None) -> None:
    """
    Generate all missing scene images using local Stable Diffusion.

    progress(message: str, step: int, total: int) is called at each stage.
    Raises ImportError if diffusers/torch are not installed.
    """
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    _require_packages()

    import torch
    from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler

    missing = missing_scenes()
    total = len(missing)
    if total == 0:
        return

    def _prog(msg, step=0):
        if progress:
            progress(msg, step, total)

    # ── Load model ─────────────────────────────────────────────────────────────
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype  = torch.float16 if device == "cuda" else torch.float32

    _prog("Loading AI model — first time needs ~6 GB download...", 0)

    pipe = None
    for model_id in _MODELS:
        try:
            pipe = StableDiffusionXLPipeline.from_pretrained(
                model_id,
                torch_dtype=dtype,
                use_safetensors=True,
                variant="fp16" if device == "cuda" else None,
            )
            break
        except Exception:
            try:
                pipe = StableDiffusionXLPipeline.from_pretrained(
                    model_id, torch_dtype=dtype
                )
                break
            except Exception:
                continue

    if pipe is None:
        raise RuntimeError("Could not load any Stable Diffusion XL model.")

    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)

    if device == "cuda":
        pipe.enable_model_cpu_offload()   # keeps VRAM usage low
    else:
        pipe = pipe.to(device)

    # ── Generate each missing scene ────────────────────────────────────────────
    from PIL import Image as PILImage

    for step, name in enumerate(missing, 1):
        out_path = ASSETS_DIR / f"scene_{_slug(name)}.png"
        _prog(f"Painting '{name}'...", step - 1)

        seed = _SEEDS.get(name, step * 37)
        gen  = torch.Generator(device="cpu").manual_seed(seed)

        result = pipe(
            prompt          = SCENE_PROMPTS[name],
            negative_prompt = NEGATIVE,
            width           = GEN_W,
            height          = GEN_H,
            num_inference_steps = 30,
            guidance_scale  = 7.5,
            generator       = gen,
        )
        img: PILImage.Image = result.images[0]

        # Crop / resize to exact scene area dimensions
        img = img.resize((1024, CROP_H), PILImage.LANCZOS)
        img.save(str(out_path), "PNG", optimize=True)
        _prog(f"Saved '{name}'.", step)

    # ── Clean up ───────────────────────────────────────────────────────────────
    del pipe
    import gc
    gc.collect()
    if device == "cuda":
        torch.cuda.empty_cache()

    _prog("All backgrounds ready!", total)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _slug(name: str) -> str:
    return name.lower().replace(" ", "_")


def _require_packages():
    missing = []
    for pkg in ("torch", "diffusers", "transformers", "accelerate", "PIL"):
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg if pkg != "PIL" else "Pillow")
    if missing:
        raise ImportError(
            f"Missing packages: {', '.join(missing)}\n"
            f"Install with:  pip install torch torchvision diffusers transformers accelerate Pillow"
        )
