#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_on_gpu.py — Run this on ANY computer that has a GPU.

1. Copy this file to the other computer
2. Install requirements:
       pip install torch torchvision diffusers transformers accelerate Pillow

3. Run:
       python generate_on_gpu.py

4. Copy the generated PNG files back to:
       data/images/
   in the Amazon Forest game folder.

The game will automatically detect and use the images on next launch.
"""

import sys
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "output_images"

# ── Prompts (same as asset_generator.py) ──────────────────────────────────────

SCENES = {
    "Forest": {
        "slug": "scene_forest",
        "seed": 42,
        "prompt": (
            "lush Amazon rainforest scene, painterly fantasy illustration, ancient towering kapok trees "
            "with massive textured trunks, golden sunbeams through leafy green canopy, colorful macaw "
            "perched on branch, vibrant tropical orchids and heliconias in foreground, rich layered "
            "depth, warm afternoon light, magical adventure game background, no humans, masterpiece"
        ),
    },
    "Forest_2": {
        "slug": "scene_forest_2",
        "seed": 500,
        "prompt": (
            "Amazon rainforest at misty dawn, painterly fantasy illustration, ancient kapok trees "
            "emerging from soft morning fog, gentle golden light filtering through mist, giant "
            "dewdrop-covered tropical leaves, glowing orchids in foreground, serene magical "
            "atmosphere, adventure game background, no humans, masterpiece"
        ),
    },
    "Forest_3": {
        "slug": "scene_forest_3",
        "seed": 501,
        "prompt": (
            "Amazon rainforest at twilight, painterly fantasy illustration, warm amber and violet "
            "sky glimpsed through canopy, fireflies beginning to glow among ancient trees, exotic "
            "heliconia flowers lit by last sunlight, mysterious magical atmosphere, "
            "adventure game background, no humans, masterpiece"
        ),
    },
    "River": {
        "slug": "scene_river",
        "seed": 123,
        "prompt": (
            "Amazon river scene, painterly fantasy illustration, wide crystal-clear turquoise river "
            "with shimmering reflections, lush tropical banks, pink Amazon river dolphin leaping, "
            "giant Victoria lily pads with pink flowers, colorful butterflies, tropical blue sky "
            "with clouds, magical adventure game background, no humans, masterpiece"
        ),
    },
    "River_2": {
        "slug": "scene_river_2",
        "seed": 502,
        "prompt": (
            "Amazon jungle stream and waterfall, painterly fantasy illustration, crystal-clear "
            "shallow rapids over mossy rocks, lush overhanging ferns and bromeliads, colorful "
            "tropical fish visible in water, dappled sunlight through canopy, small hidden "
            "waterfall, magical adventure game background, no humans, masterpiece"
        ),
    },
    "River_3": {
        "slug": "scene_river_3",
        "seed": 503,
        "prompt": (
            "Amazon river at golden sunset, painterly fantasy illustration, vast glowing river "
            "reflecting warm orange and pink sky, silhouetted tropical trees lining the banks, "
            "giant Victoria lily pads in foreground, a heron standing still, tranquil magical "
            "atmosphere, adventure game background, no humans, masterpiece"
        ),
    },
    "Clearing": {
        "slug": "scene_clearing",
        "seed": 456,
        "prompt": (
            "Amazon rainforest sunny clearing, painterly fantasy illustration, bright open meadow "
            "with vivid green grass, colorful wildflowers and orchids, towering jungle trees forming "
            "a ring, brilliant blue sky, warm golden light, a morpho butterfly flying, "
            "magical adventure game background, no humans, masterpiece"
        ),
    },
    "Clearing_2": {
        "slug": "scene_clearing_2",
        "seed": 504,
        "prompt": (
            "Amazon rainforest clearing at misty morning, painterly fantasy illustration, soft "
            "white mist drifting over vivid green meadow, rainbow orchids and exotic wildflowers "
            "blooming, colorful tropical butterflies, ancient trees forming misty border, soft "
            "golden light, magical adventure game background, no humans, masterpiece"
        ),
    },
    "Clearing_3": {
        "slug": "scene_clearing_3",
        "seed": 505,
        "prompt": (
            "Amazon rainforest clearing at dusk, painterly fantasy illustration, warm golden-orange "
            "sky above open meadow, fireflies beginning to emerge, glowing tropical flowers, "
            "surrounding jungle trees lit by last rays of sun, magical serene atmosphere, "
            "adventure game background, no humans, masterpiece"
        ),
    },
    "Dense Jungle": {
        "slug": "scene_dense_jungle",
        "seed": 789,
        "prompt": (
            "dense Amazon jungle interior, painterly fantasy illustration, dramatic mysterious "
            "atmosphere, ancient massive trees, dramatic shafts of golden light cutting through "
            "dark green canopy, hanging lianas and vines, giant exotic leaves, glowing "
            "bioluminescent mushrooms and flowers, deep rich greens, magical adventure game "
            "background, no humans, masterpiece"
        ),
    },
    "Dense Jungle_2": {
        "slug": "scene_dense_jungle_2",
        "seed": 506,
        "prompt": (
            "ancient Amazon jungle depths, painterly fantasy illustration, massive twisted tree "
            "roots and trunks, glowing bioluminescent fungi carpeting the forest floor, mysterious "
            "shafts of blue-green light, enormous exotic leaves, hidden misty waterfall in "
            "distance, deep mystical atmosphere, adventure game background, no humans, masterpiece"
        ),
    },
    "Dense Jungle_3": {
        "slug": "scene_dense_jungle_3",
        "seed": 507,
        "prompt": (
            "Amazon dense jungle interior looking upward, painterly fantasy illustration, massive "
            "tree canopy far above, dramatic golden god rays piercing dark green atmosphere, "
            "hanging aerial roots and lianas draped between trees, exotic parrots silhouetted "
            "high in canopy, magical adventure game background, no humans, masterpiece"
        ),
    },
    "Camp": {
        "slug": "scene_camp",
        "seed": 1011,
        "prompt": (
            "cozy jungle campsite at night, painterly fantasy illustration, warm glowing campfire "
            "center stage, two colorful explorer tents flanking the fire, brilliant starry sky "
            "through jungle canopy clearing, fireflies dancing, warm orange firelight reflecting "
            "on surrounding trees, a cozy magical atmosphere, adventure game background, "
            "no humans, masterpiece"
        ),
    },
}

NEGATIVE = (
    "text, watermark, signature, human face, person, ugly, blurry, low quality, "
    "nsfw, scary, dark horror, violence, realistic photography, 3d render, "
    "worst quality, cartoon, anime, sketch"
)

PREFERRED_MODELS = [
    "Lykon/dreamshaper-xl-1-0",         # best illustration quality
    "stabilityai/stable-diffusion-xl-base-1.0",  # official SDXL
]

# Output size: SDXL generates at 1024×576, we crop to 1024×560 (game scene area)
GEN_W, GEN_H, CROP_H = 1024, 576, 560


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        import torch
        from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
        from PIL import Image
    except ImportError:
        print("ERROR: Missing packages. Run:")
        print("  pip install torch torchvision diffusers transformers accelerate Pillow")
        sys.exit(1)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype  = torch.float16 if device == "cuda" else torch.float32

    print(f"\nDevice: {device}  |  dtype: {dtype}")
    if device == "cpu":
        print("WARNING: No CUDA GPU found. Generating on CPU will be VERY slow (~30 min/image).")
        ans = input("Continue anyway? [y/N] ").strip().lower()
        if ans != "y":
            sys.exit(0)

    # Load model
    print("\nLoading model (first time downloads ~6 GB)...")
    pipe = None
    for model_id in PREFERRED_MODELS:
        print(f"  Trying {model_id}...")
        try:
            pipe = StableDiffusionXLPipeline.from_pretrained(
                model_id,
                torch_dtype=dtype,
                use_safetensors=True,
                variant="fp16" if device == "cuda" else None,
            )
            print(f"  Loaded: {model_id}")
            break
        except Exception as e:
            print(f"  Failed ({e}), trying next...")

    if pipe is None:
        print("ERROR: Could not load any model. Check your internet connection.")
        sys.exit(1)

    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config, final_sigmas_type="sigma_min")
    if device == "cuda":
        pipe.enable_model_cpu_offload()
    else:
        pipe = pipe.to(device)

    total = len(SCENES)
    for i, (name, info) in enumerate(SCENES.items(), 1):
        out_path = OUTPUT_DIR / f"{info['slug']}.png"
        if out_path.exists():
            print(f"\n[{i}/{total}] '{name}' already exists — skipping.")
            continue

        print(f"\n[{i}/{total}] Painting '{name}'...")
        gen    = torch.Generator(device="cpu").manual_seed(info["seed"])
        result = pipe(
            prompt          = info["prompt"],
            negative_prompt = NEGATIVE,
            width           = GEN_W,
            height          = GEN_H,
            num_inference_steps = 30,
            guidance_scale  = 7.5,
            generator       = gen,
        )
        img: Image.Image = result.images[0]
        img = img.resize((1024, CROP_H), Image.LANCZOS)
        img.save(str(out_path), "PNG", optimize=True)
        print(f"  Saved: {out_path}")

    print(f"\nDone! Copy all PNG files from:\n  {OUTPUT_DIR}\nto the game folder:\n  data/images/")
    print("\nFiles to copy:")
    for name, info in SCENES.items():
        src = OUTPUT_DIR / f"{info['slug']}.png"
        print(f"  {src.name}  ->  data/images/{src.name}")


if __name__ == "__main__":
    main()
