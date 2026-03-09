# Amazon Rainforest Explorer 🌿

An educational point-and-click adventure game for kids, set in the Amazon rainforest.
Built with Python + pygame. Hebrew UI. Discovers animals and plants through exploration.

## Quick Start (any machine)

```bash
pip install pygame python-bidi
python main.py
```

The game works immediately with procedural art backgrounds.

## Beautiful AI Backgrounds + Portraits (GPU machine required)

### Scene backgrounds
```bash
pip install torch torchvision diffusers transformers accelerate Pillow
python generate_on_gpu.py
```
Downloads Stable Diffusion XL (~6 GB), generates 13 scene PNGs into `output_images/`.
Copy to `data/images/`.

### Discovery Journal portraits
Same script — after the 13 scene backgrounds it generates 36 creature/plant portraits
(23 animals + 13 plants) into `output_images/creatures/`.
Copy to `data/images/creatures/`.

### Background music
```bash
pip install audiocraft
python generate_music.py
```
Downloads MusicGen (~1.5 GB), generates 7 WAV tracks directly into `data/music/`:
- `music_exploration.wav` — ambient loop for the world map
- `music_forest.wav` — birdsong and flute for Forest tiles
- `music_river.wav` — flowing water and marimba for River tiles
- `music_clearing.wav` — bright guitar and flute for Clearing tiles
- `music_dense_jungle.wav` — deep drums and haunting flute for Dense Jungle tiles
- `music_camp.wav` — peaceful campfire loop for Camp
- `discovery_stinger.wav` — short fanfare played on new discoveries

All generated files are gitignored. Run the scripts to regenerate locally.

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

Skills are upgraded at the Camp → Skills Journal (max level 3).
Each level unlocks real gameplay content, not just numeric bonuses:

| Skill | L1 | L2 | L3 |
|-------|----|----|-----|
| **Explorer** | Listen to the hollow log (focused discovery) | Climb the ancient tree (find Sloth) | Follow jaguar tracks in Dense Jungle |
| **Nature Friend** | Identify medicinal herbs in the Clearing | Call howler monkeys at the Brazil Nut tree | +2 bonus food on every foraging action |
| **Survival Helper** | Cook over the campfire (restore 9 food) | Braid vines into a rope (craft Rope item) | Build a fish trap from scratch at the River |

Rope (crafted via Survival Helper L2) unlocks crossing the water lilies to find the Pink Dolphin.

## Music Generation Prompts

Model: `facebook/musicgen-medium` (fallback: `facebook/musicgen-small`).
Settings: 45s duration for loops, 4s for stinger. Sampling: top_k=250, temperature=1.0.

### World map music (`music_exploration`)
```
Amazon rainforest overworld map music, mysterious adventure theme,
pan flute melody, light marimba, gentle hand drum, magical exploration atmosphere,
looping background, calm and uplifting, no lyrics, instrumental
```

### Forest tiles (`music_forest`)
```
lush Amazon rainforest ambient music, bird calls woven into gentle melody,
wooden flute and soft strings, rustling leaves, warm sunlit atmosphere,
serene and magical, looping background, no lyrics, instrumental
```

### River tiles (`music_river`)
```
Amazon river ambient music, flowing water sounds layered with marimba melody,
light percussion, peaceful and refreshing, aquatic atmosphere,
relaxing looping background, no lyrics, instrumental
```

### Clearing tiles (`music_clearing`)
```
sunny Amazon jungle clearing music, bright uplifting melody,
acoustic guitar and flute duet, cheerful percussion, warm open-air atmosphere,
light and joyful, looping background, no lyrics, instrumental
```

### Dense Jungle tiles (`music_dense_jungle`)
```
dense Amazon jungle music, mysterious and atmospheric, deep bass drones,
distant tribal drums, haunting bamboo flute echoes, night atmosphere,
tense and magical, looping background, no lyrics, instrumental
```

### Camp tiles (`music_camp`)
```
peaceful jungle campfire night music, warm acoustic guitar fingerpicking,
gentle bongo and soft shaker, distant cricket sounds, cozy adventure camp atmosphere,
serene and comforting, soft ambient pads, no lyrics, instrumental loop
```

### Discovery stinger (played on new discoveries)
```
short triumphant discovery fanfare, 3-second orchestral sting,
adventure game reveal, bright brass and string ensemble, joyful and majestic,
exciting discovery sound effect, cinematic
```

---

## Creature Portrait Prompts

Model: Stable Diffusion XL. Format: 768×768 → saved at 512×512.

**Style suffix applied to all:** `Amazon rainforest, painterly fantasy illustration portrait, highly detailed, vivid colors, magical atmosphere, masterpiece`

**Negative prompt:**
```
text, watermark, signature, human face, person, ugly, blurry, low quality,
nsfw, multiple animals, cluttered background, worst quality, cartoon, anime, sketch
```

| ID | Seed | Subject |
|----|------|---------|
| macaw | 3001 | blue-and-yellow macaw parrot, vibrant rainbow plumage |
| sloth | 3002 | three-toed sloth hanging upside-down |
| anaconda | 3003 | green anaconda coiled on mossy rock |
| tapir | 3004 | Brazilian tapir with prehensile snout |
| jaguar | 3005 | jaguar with rosettes and golden eyes |
| pink_dolphin | 3006 | Amazon pink river dolphin leaping |
| poison_dart_frog | 3007 | vivid blue and black dart frog on leaf |
| capybara | 3008 | friendly capybara by river bank |
| toucan | 3009 | toucan with enormous colorful beak |
| howler_monkey | 3010 | howler monkey calling in canopy |
| giant_otter | 3011 | giant river otter splashing |
| morpho_butterfly | 3012 | blue morpho butterfly wings spread |
| harpy_eagle | 3013 | harpy eagle with dramatic crest |
| piranha | 3014 | red-bellied piranha underwater |
| pygmy_owl | 3015 | tiny pygmy owl in tree hollow |
| amazon_tree_frog | 3016 | vivid green tree frog on leaf |
| blue_morpho_beetle | 3017 | iridescent cobalt beetle macro |
| ornamental_fish | 3018 | neon tetra school in river |
| river_crab | 3019 | Amazon freshwater crab on rock |
| flower_beetle | 3020 | jewel-like beetle on tropical flower |
| forest_mouse | 3021 | tiny forest mouse holding a nut |
| orchid_bee | 3022 | metallic green orchid bee at flower |
| green_parrot | 3023 | vivid green Amazon parrot |
| giant_water_lily | 3024 | Victoria amazonica giant lily pad |
| heliconia | 3025 | red lobster-claw heliconia flower |
| orchid | 3026 | purple and white Amazon orchid |
| bromeliad | 3027 | vivid red-green bromeliad rosette |
| rubber_tree | 3028 | rubber tree with dripping latex |
| kapok_tree | 3029 | kapok with buttress roots and seed pods |
| cacao | 3030 | cacao pods growing on trunk |
| passion_flower | 3031 | intricate passionflower crown |
| banana_plant | 3032 | wild banana with paddle-shaped leaves |
| amazon_lily | 3033 | white Amazon lily at waterside |
| strangler_fig | 3034 | fig roots wrapping ancient tree |
| brazil_nut | 3035 | cracked Brazil nut pod showing seeds |
| cashew_nut | 3036 | red-yellow cashew apple with attached nut |

---

## Image Generation Prompts

Scene backgrounds are generated with Stable Diffusion XL (model: `Lykon/dreamshaper-xl-1-0`,
fallback: `stabilityai/stable-diffusion-xl-base-1.0`).

**Generation settings:** 30 inference steps, guidance scale 7.5, output 1024×576 cropped to 1024×560.

**Negative prompt (all scenes):**
```
text, watermark, signature, human face, person, ugly, blurry, low quality,
nsfw, scary, dark horror, violence, realistic photography, 3d render,
worst quality, cartoon, anime, sketch
```

### Forest (seed 42)
```
lush Amazon rainforest scene, painterly fantasy illustration, ancient towering kapok trees
with massive textured trunks, golden sunbeams through leafy green canopy, colorful macaw
perched on branch, vibrant tropical orchids and heliconias in foreground, rich layered
depth, warm afternoon light, magical adventure game background, no humans, masterpiece
```

### Forest variant 2 (seed 500)
```
Amazon rainforest at misty dawn, painterly fantasy illustration, ancient kapok trees
emerging from soft morning fog, gentle golden light filtering through mist, giant
dewdrop-covered tropical leaves, glowing orchids in foreground, serene magical
atmosphere, adventure game background, no humans, masterpiece
```

### Forest variant 3 (seed 501)
```
Amazon rainforest at twilight, painterly fantasy illustration, warm amber and violet
sky glimpsed through canopy, fireflies beginning to glow among ancient trees, exotic
heliconia flowers lit by last sunlight, mysterious magical atmosphere,
adventure game background, no humans, masterpiece
```

### River (seed 123)
```
Amazon river scene, painterly fantasy illustration, wide crystal-clear turquoise river
with shimmering reflections, lush tropical banks, pink Amazon river dolphin leaping,
giant Victoria lily pads with pink flowers, colorful butterflies, tropical blue sky
with clouds, magical adventure game background, no humans, masterpiece
```

### River variant 2 (seed 502)
```
Amazon jungle stream and waterfall, painterly fantasy illustration, crystal-clear
shallow rapids over mossy rocks, lush overhanging ferns and bromeliads, colorful
tropical fish visible in water, dappled sunlight through canopy, small hidden
waterfall, magical adventure game background, no humans, masterpiece
```

### River variant 3 (seed 503)
```
Amazon river at golden sunset, painterly fantasy illustration, vast glowing river
reflecting warm orange and pink sky, silhouetted tropical trees lining the banks,
giant Victoria lily pads in foreground, a heron standing still, tranquil magical
atmosphere, adventure game background, no humans, masterpiece
```

### Clearing (seed 456)
```
Amazon rainforest sunny clearing, painterly fantasy illustration, bright open meadow
with vivid green grass, colorful wildflowers and orchids, towering jungle trees forming
a ring, brilliant blue sky, warm golden light, a morpho butterfly flying,
magical adventure game background, no humans, masterpiece
```

### Clearing variant 2 (seed 504)
```
Amazon rainforest clearing at misty morning, painterly fantasy illustration, soft
white mist drifting over vivid green meadow, rainbow orchids and exotic wildflowers
blooming, colorful tropical butterflies, ancient trees forming misty border, soft
golden light, magical adventure game background, no humans, masterpiece
```

### Clearing variant 3 (seed 505)
```
Amazon rainforest clearing at dusk, painterly fantasy illustration, warm golden-orange
sky above open meadow, fireflies beginning to emerge, glowing tropical flowers,
surrounding jungle trees lit by last rays of sun, magical serene atmosphere,
adventure game background, no humans, masterpiece
```

### Dense Jungle (seed 789)
```
dense Amazon jungle interior, painterly fantasy illustration, dramatic mysterious
atmosphere, ancient massive trees, dramatic shafts of golden light cutting through
dark green canopy, hanging lianas and vines, giant exotic leaves, glowing
bioluminescent mushrooms and flowers, deep rich greens, magical adventure game
background, no humans, masterpiece
```

### Dense Jungle variant 2 (seed 506)
```
ancient Amazon jungle depths, painterly fantasy illustration, massive twisted tree
roots and trunks, glowing bioluminescent fungi carpeting the forest floor, mysterious
shafts of blue-green light, enormous exotic leaves, hidden misty waterfall in
distance, deep mystical atmosphere, adventure game background, no humans, masterpiece
```

### Dense Jungle variant 3 (seed 507)
```
Amazon dense jungle interior looking upward, painterly fantasy illustration, massive
tree canopy far above, dramatic golden god rays piercing dark green atmosphere,
hanging aerial roots and lianas draped between trees, exotic parrots silhouetted
high in canopy, magical adventure game background, no humans, masterpiece
```

### Camp (seed 1011)
```
cozy jungle campsite at night, painterly fantasy illustration, warm glowing campfire
center stage, two colorful explorer tents flanking the fire, brilliant starry sky
through jungle canopy clearing, fireflies dancing, warm orange firelight reflecting
on surrounding trees, a cozy magical atmosphere, adventure game background,
no humans, masterpiece
```
