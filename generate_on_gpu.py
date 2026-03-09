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

# ── Creature / Plant Portrait Prompts ─────────────────────────────────────────
# Square 768×768 portraits for the Discovery Journal detail view.
# Output to output_images/creatures/ → copy to data/images/creatures/

STYLE = "Amazon rainforest, painterly fantasy illustration portrait, highly detailed, vivid colors, magical atmosphere, masterpiece"

CREATURES = {
    # Animals
    "macaw": {
        "seed": 3001,
        "prompt": f"blue-and-yellow macaw parrot, vibrant rainbow plumage, perched on branch, {STYLE}",
    },
    "sloth": {
        "seed": 3002,
        "prompt": f"three-toed sloth hanging upside-down, fluffy grey fur, gentle expression, green leaves, {STYLE}",
    },
    "anaconda": {
        "seed": 3003,
        "prompt": f"green anaconda snake coiled on mossy rock, iridescent scales, river bank setting, {STYLE}",
    },
    "tapir": {
        "seed": 3004,
        "prompt": f"Brazilian tapir, stocky body, prehensile snout, tropical plants background, {STYLE}",
    },
    "jaguar": {
        "seed": 3005,
        "prompt": f"jaguar big cat, golden fur with black rosettes, piercing golden eyes, jungle shadows, {STYLE}",
    },
    "pink_dolphin": {
        "seed": 3006,
        "prompt": f"Amazon pink river dolphin, pink skin, leaping from turquoise river water, magical glow, {STYLE}",
    },
    "poison_dart_frog": {
        "seed": 3007,
        "prompt": f"poison dart frog, vivid blue and black colors, sitting on bright green leaf, macro detail, {STYLE}",
    },
    "capybara": {
        "seed": 3008,
        "prompt": f"capybara, large friendly rodent, sitting by river bank, wet fur, lush tropical plants, {STYLE}",
    },
    "toucan": {
        "seed": 3009,
        "prompt": f"toucan bird, enormous colorful orange and yellow beak, perched on jungle branch, {STYLE}",
    },
    "howler_monkey": {
        "seed": 3010,
        "prompt": f"howler monkey, dark fur, open mouth calling loudly, hanging in forest canopy, {STYLE}",
    },
    "giant_otter": {
        "seed": 3011,
        "prompt": f"giant river otter, sleek brown fur, playful expression, Amazonian river, splashing water, {STYLE}",
    },
    "morpho_butterfly": {
        "seed": 3012,
        "prompt": f"blue morpho butterfly, enormous iridescent blue wings spread open, sunlit forest clearing, {STYLE}",
    },
    "harpy_eagle": {
        "seed": 3013,
        "prompt": f"harpy eagle, fierce gaze, dramatic grey and white plumage, fan crest, jungle canopy perch, {STYLE}",
    },
    "piranha": {
        "seed": 3014,
        "prompt": f"red-bellied piranha fish, sharp teeth showing, underwater Amazon river, dappled light, {STYLE}",
    },
    "pygmy_owl": {
        "seed": 3015,
        "prompt": f"pygmy owl, tiny and cute, huge yellow eyes, fluffy brown feathers, tree hollow at night, {STYLE}",
    },
    "amazon_tree_frog": {
        "seed": 3016,
        "prompt": f"Amazon tree frog, bright vivid green, enormous golden eyes, clinging to tropical leaf, {STYLE}",
    },
    "blue_morpho_beetle": {
        "seed": 3017,
        "prompt": f"blue morpho beetle, jewel-like iridescent cobalt shell, Amazon forest floor, macro detail, {STYLE}",
    },
    "ornamental_fish": {
        "seed": 3018,
        "prompt": f"neon tetra fish school, glowing blue and red stripe, crystal Amazon river water, {STYLE}",
    },
    "river_crab": {
        "seed": 3019,
        "prompt": f"Amazon freshwater crab, patterned shell, one large claw raised, mossy tropical rock, {STYLE}",
    },
    "flower_beetle": {
        "seed": 3020,
        "prompt": f"flower chafer beetle, jewel-like iridescent shell, perched on tropical flower bloom, macro, {STYLE}",
    },
    "forest_mouse": {
        "seed": 3021,
        "prompt": f"tiny Amazon forest mouse, large round eyes, delicate whiskers, holding a nut, fallen leaf, {STYLE}",
    },
    "orchid_bee": {
        "seed": 3022,
        "prompt": f"male orchid bee, brilliant metallic green iridescent body, hovering at orchid flower, macro, {STYLE}",
    },
    "green_parrot": {
        "seed": 3023,
        "prompt": f"Amazon parrot, vivid green plumage with red and blue accents, jungle branch, expressive, {STYLE}",
    },
    # Plants
    "giant_water_lily": {
        "seed": 3024,
        "prompt": f"Victoria amazonica giant water lily, enormous circular pad on river, white and pink flower, {STYLE}",
    },
    "heliconia": {
        "seed": 3025,
        "prompt": f"heliconia flower, dramatic red lobster-claw bracts, vivid tropical foliage, {STYLE}",
    },
    "orchid": {
        "seed": 3026,
        "prompt": f"Amazon rainforest orchid, intricate purple and white flower, epiphyte on mossy tree bark, {STYLE}",
    },
    "bromeliad": {
        "seed": 3027,
        "prompt": f"bromeliad rosette, vivid red and green leaves, central water pool, growing on tree trunk, {STYLE}",
    },
    "rubber_tree": {
        "seed": 3028,
        "prompt": f"Amazon rubber tree trunk, white latex dripping from cut, massive tropical leaves, forest light, {STYLE}",
    },
    "kapok_tree": {
        "seed": 3029,
        "prompt": f"kapok tree, enormous buttress roots, towering trunk, fluffy white seed pods drifting, {STYLE}",
    },
    "cacao": {
        "seed": 3030,
        "prompt": f"cacao tree, colorful football-shaped pods growing directly from trunk, Amazon forest, {STYLE}",
    },
    "passion_flower": {
        "seed": 3031,
        "prompt": f"passionflower, intricate purple and white petals, complex crown filaments, tropical vine, {STYLE}",
    },
    "banana_plant": {
        "seed": 3032,
        "prompt": f"wild Amazon banana plant, enormous paddle-shaped leaves, green fruit cluster, jungle clearing, {STYLE}",
    },
    "amazon_lily": {
        "seed": 3033,
        "prompt": f"Amazon lily, pure white fragrant flower, tropical waterside, lush green leaves, morning dew, {STYLE}",
    },
    "strangler_fig": {
        "seed": 3034,
        "prompt": f"strangler fig, lattice of aerial roots wrapping ancient tree, dramatic jungle interior, {STYLE}",
    },
    "brazil_nut": {
        "seed": 3035,
        "prompt": f"Brazil nut tree pod, round woody capsule cracked open showing seeds, forest floor, {STYLE}",
    },
    "cashew_nut": {
        "seed": 3036,
        "prompt": f"cashew plant, red-yellow cashew apple with nut attached, tropical clearing, unusual fruit, {STYLE}",
    },
}

CREATURE_NEGATIVE = (
    "text, watermark, signature, human face, person, ugly, blurry, low quality, "
    "nsfw, multiple animals, cluttered background, worst quality, cartoon, anime, sketch"
)

CREATURE_W = CREATURE_H = 768   # SDXL square portrait
CREATURE_SAVE_SIZE = 512        # saved at 512×512 for storage efficiency

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

    print(f"\nDone with scene backgrounds! Copy PNGs from:\n  {OUTPUT_DIR}\nto:\n  data/images/")

    # ── Creature / Plant Portraits ─────────────────────────────────────────────
    creature_dir = OUTPUT_DIR / "creatures"
    creature_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'-'*60}")
    print(f"Now generating {len(CREATURES)} creature/plant portraits for the Discovery Journal...")
    print(f"{'-'*60}")

    total_c = len(CREATURES)
    for i, (creature_id, info) in enumerate(CREATURES.items(), 1):
        out_path = creature_dir / f"{creature_id}.png"
        if out_path.exists():
            print(f"[{i}/{total_c}] '{creature_id}' already exists — skipping.")
            continue

        print(f"\n[{i}/{total_c}] Painting '{creature_id}'...")
        gen    = torch.Generator(device="cpu").manual_seed(info["seed"])
        result = pipe(
            prompt          = info["prompt"],
            negative_prompt = CREATURE_NEGATIVE,
            width           = CREATURE_W,
            height          = CREATURE_H,
            num_inference_steps = 25,
            guidance_scale  = 7.5,
            generator       = gen,
        )
        img: Image.Image = result.images[0]
        img = img.resize((CREATURE_SAVE_SIZE, CREATURE_SAVE_SIZE), Image.LANCZOS)
        img.save(str(out_path), "PNG", optimize=True)
        print(f"  Saved: {out_path}")

    print(f"\nAll done!")
    print(f"\nCopy creature portraits:")
    print(f"  {creature_dir}/*.png  ->  data/images/creatures/")


if __name__ == "__main__":
    main()
