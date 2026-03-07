# Amazon Rainforest Explorer 🌿

An educational point-and-click adventure game for kids, set in the Amazon rainforest.
Built with Python + pygame. Hebrew UI. Discovers animals and plants through exploration.

## Quick Start (any machine)

```bash
pip install pygame python-bidi
python main.py
```

The game works immediately with procedural art backgrounds.

## Beautiful AI Backgrounds (GPU machine required)

To generate illustrated scene backgrounds using Stable Diffusion:

1. On a machine with a GPU (NVIDIA, 6+ GB VRAM):
   ```bash
   pip install torch torchvision diffusers transformers accelerate Pillow
   python generate_on_gpu.py
   ```
   This downloads the model (~6 GB, one time) and generates 5 PNG files
   into an `output_images/` folder. Takes ~5 min per image.

2. Copy the PNG files to `data/images/` in the game folder.

3. Run `python main.py` — backgrounds load automatically.

## Project Structure

```
Forest game/
├── main.py              # Entry point, game loop, state machine
├── engine.py            # Game logic (discovery, food, skills)
├── scenes.py            # All pygame rendering
├── creatures.py         # Creature + explorer avatar drawings
├── models.py            # Data classes
├── map.py               # World grid and movement
├── localization.py      # Hebrew text via t("key")
├── asset_generator.py   # SD image generation pipeline
├── generate_on_gpu.py   # Standalone script for GPU machine
└── data/
    ├── text_he.json     # All Hebrew strings
    ├── animals.json     # 22 Amazon animals
    ├── plants.json      # 13 Amazon plants
    ├── scenes.json      # 5 scenes with interactive objects
    ├── items.json       # Discoverable items
    └── images/          # Generated PNG backgrounds (gitignored)
```

## Controls

- **Map**: Click an adjacent tile to move there
- **Scene**: Click a glowing object to interact
- **Interaction panel**: Click an action button
- **Popup**: Click anywhere or press any key to dismiss
- **Back**: Back button or Escape

## Skills

| Skill | Effect |
|-------|--------|
| Explorer | +10% discovery chance per level |
| Nature Friend | +15% knowledge reward per level |
| Survival Helper | −10% food cost per level |

Upgrade at the Camp → Skills Journal. Max level 3.
