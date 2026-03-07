# -*- coding: utf-8 -*-
"""
scenes.py — All pygame rendering.  Zero game logic lives here.

Rules:
  - Pure draw functions; all receive surface + fonts as arguments.
  - All Hebrew strings come via localization.t(), never hardcoded.
  - engine.py handles action dispatch after player input.
"""

import math
import random
import re
import pygame
from pygame import Rect

# Strip emoji and symbols that Arial/David can't render (supplementary planes + dingbats)
_EMOJI_RE = re.compile(r'[\U00010000-\U0010FFFF\u2600-\u27BF\uFE00-\uFE0F]')

import localization as loc
import creatures

# ── Generated image cache ──────────────────────────────────────────────────────
# Populated once by load_scene_images(); keyed by tile_type.
_scene_surfaces: dict = {}   # tile_type → list of full-scene Surfaces (1024×560)
_tile_surfaces:  dict = {}   # tile_type → Surface (100×100) for map tiles (first variant)

# ── Constants ─────────────────────────────────────────────────────────────────

W, H = 1024, 700
MAP_AREA_H = 560     # height of map/scene art area; bottom bar is H - MAP_AREA_H
TILE_W, TILE_H = 104, 104
TILE_COLS, TILE_ROWS = 5, 5
MAP_OFFSET_X = (W - TILE_COLS * TILE_W) // 2
MAP_OFFSET_Y = 60

# Colours
C_BG          = (15,  25,  15)
C_BAR_BG      = (20,  30,  20)
C_WHITE       = (255, 255, 255)
C_DIM         = (140, 140, 140)
C_GOLD        = (255, 215,   0)
C_GREEN       = ( 60, 180,  60)
C_GREEN_DARK  = ( 30, 100,  30)
C_BLUE        = ( 60, 130, 220)
C_CYAN        = ( 80, 220, 210)
C_ORANGE      = (220, 130,  40)
C_RED         = (200,  60,  60)
C_YELLOW      = (220, 200,  50)
C_PANEL_BG    = ( 20,  35,  20)
C_PANEL_EDGE  = ( 70, 130,  70)

# Tile accent colours used for borders / glows
TILE_COLORS = {
    "Forest":       ( 60, 200,  80),
    "River":        ( 60, 140, 230),
    "Clearing":     (220, 200,  50),
    "Dense Jungle": ( 30, 130,  50),
    "Camp":         (220, 130,  40),
    "Unknown":      ( 60,  60,  60),
}

# Object hotspot rects within the 1024×MAP_AREA_H scene area
_OBJECT_RECTS = {
    "Forest":       [Rect( 60, 120, 220, 390), Rect(380, 290, 250, 230), Rect(700, 100, 220, 420)],
    "River":        [Rect(350, 220, 220, 290), Rect( 90, 310, 230, 190), Rect(580, 180, 240, 260)],
    "Clearing":     [Rect( 70, 260, 260, 270), Rect(390, 350, 240, 190), Rect(680, 160, 250, 360)],
    "Dense Jungle": [Rect( 70,  50, 230, 480), Rect(380,  70, 270, 470), Rect(680, 360, 250, 170)],
    "Camp":         [Rect(380, 270, 260, 250), Rect( 90, 330, 210, 180), Rect(730, 330, 200, 180)],
}

# Seeded decorative elements so they don't shift every frame
_rng = random.Random(42)


# ── Font loader ───────────────────────────────────────────────────────────────

def load_fonts() -> dict:
    """Return a dict of pygame fonts keyed by size name.

    Loads by direct TTF path so Hebrew glyphs are guaranteed present.
    Falls back through several Windows Hebrew-capable fonts.
    """
    from pathlib import Path
    candidates = [
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\david.ttf",
        r"C:\Windows\Fonts\calibri.ttf",
        r"C:\Windows\Fonts\frank.ttf",
    ]
    font_path = None
    for p in candidates:
        if Path(p).exists():
            font_path = p
            break

    def _f(size):
        if font_path:
            return pygame.font.Font(font_path, size)
        return pygame.font.SysFont("arial", size)

    return {
        "sm":  _f(18),
        "md":  _f(24),
        "lg":  _f(32),
        "xl":  _f(48),
        "xxl": _f(64),
    }


# ── Image loader ──────────────────────────────────────────────────────────────

def load_scene_images() -> int:
    """Load AI-generated PNG backgrounds into pygame surfaces.

    Loads all variants (scene_forest.png, scene_forest_2.png, …) for each
    tile type. draw_scene_bg() picks a variant using the tile's seed so every
    tile of the same type can look different.

    Returns the number of image files successfully loaded.
    Call this after pygame.init() and after asset generation completes.
    """
    from pathlib import Path
    images_dir = Path(__file__).parent / "data" / "images"
    count = 0
    for tile_type in ("Forest", "River", "Clearing", "Dense Jungle", "Camp"):
        slug = tile_type.lower().replace(" ", "_")
        variants = []
        # Load base image then numbered variants (_2, _3, …)
        for suffix in ("", "_2", "_3", "_4", "_5"):
            path = images_dir / f"scene_{slug}{suffix}.png"
            if not path.exists():
                continue
            try:
                raw = pygame.image.load(str(path)).convert()
                variants.append(pygame.transform.smoothscale(raw, (W, MAP_AREA_H)))
                count += 1
            except Exception as e:
                print(f"[scenes] Could not load {path}: {e}")
        if variants:
            _scene_surfaces[tile_type] = variants
            # Map thumbnail uses the first variant
            raw_thumb = pygame.image.load(
                str(images_dir / f"scene_{slug}.png")
            ).convert()
            _tile_surfaces[tile_type] = pygame.transform.smoothscale(
                raw_thumb, (TILE_W - 6, TILE_H - 6)
            )
    return count


# ── Text helpers ──────────────────────────────────────────────────────────────

def _bidi(text: str) -> str:
    """Apply bidi visual reordering for Hebrew in LTR pygame surface."""
    try:
        from bidi.algorithm import get_display
        return get_display(str(text))
    except Exception:
        return str(text)


def draw_text(surf, text: str, pos: tuple, font, color, align: str = "left") -> Rect:
    """Render bidi-processed text onto surf. Returns the blit rect."""
    clean = _EMOJI_RE.sub('', str(text)).strip()
    img = font.render(_bidi(clean), True, color)
    x, y = pos
    if align == "right":
        x -= img.get_width()
    elif align == "center":
        x -= img.get_width() // 2
    r = surf.blit(img, (x, y))
    return r


def draw_button(surf, rect: Rect, label: str, font, hover: bool = False,
                locked: bool = False, lock_label: str = "") -> None:
    """Draw a rounded button rectangle with label text."""
    if locked:
        bg = (40, 40, 40)
        edge = (90, 90, 90)
        text_col = (100, 100, 100)
    elif hover:
        bg = (60, 100, 60)
        edge = C_GREEN
        text_col = C_WHITE
    else:
        bg = (30, 60, 30)
        edge = (80, 140, 80)
        text_col = (200, 230, 200)

    pygame.draw.rect(surf, bg, rect, border_radius=8)
    pygame.draw.rect(surf, edge, rect, 2, border_radius=8)
    draw_text(surf, label, (rect.centerx, rect.y + 10), font, text_col, align="center")
    if locked and lock_label:
        draw_text(surf, lock_label, (rect.centerx, rect.y + rect.h - 26), font, (150, 130, 50), align="center")


# ── Panel helper ──────────────────────────────────────────────────────────────

def draw_panel(surf, rect: Rect, title: str = "", font=None,
               bg=C_PANEL_BG, edge=C_PANEL_EDGE) -> None:
    """Draw a rounded panel with optional title bar."""
    pygame.draw.rect(surf, bg, rect, border_radius=12)
    pygame.draw.rect(surf, edge, rect, 2, border_radius=12)
    if title and font:
        title_r = Rect(rect.x, rect.y, rect.w, 36)
        pygame.draw.rect(surf, edge, title_r, border_radius=10)
        draw_text(surf, title, (title_r.centerx, title_r.y + 8), font, C_WHITE, align="center")


# ── Bottom status bar ─────────────────────────────────────────────────────────

def draw_status_bar(surf, fonts, player) -> None:
    """Draw the bottom HUD bar with food bar, knowledge, and inventory."""
    bar_rect = Rect(0, MAP_AREA_H, W, H - MAP_AREA_H)
    pygame.draw.rect(surf, C_BAR_BG, bar_rect)
    pygame.draw.line(surf, C_GREEN_DARK, (0, MAP_AREA_H), (W, MAP_AREA_H), 2)

    y = MAP_AREA_H + 18

    # Food bar
    food_ratio = max(0, player.food / 15.0)
    food_col = C_RED if player.food <= 3 else C_YELLOW if player.food <= 6 else C_GREEN
    food_label = loc.t("map.stats_food", food=int(player.food))
    draw_text(surf, food_label, (20, y), fonts["md"], food_col)
    bar_x, bar_y, bar_w, bar_h = 190, y + 4, 160, 18
    pygame.draw.rect(surf, (50, 50, 50), Rect(bar_x, bar_y, bar_w, bar_h), border_radius=4)
    pygame.draw.rect(surf, food_col, Rect(bar_x, bar_y, int(bar_w * food_ratio), bar_h), border_radius=4)
    pygame.draw.rect(surf, (100, 100, 100), Rect(bar_x, bar_y, bar_w, bar_h), 1, border_radius=4)

    # Knowledge
    know_label = loc.t("map.stats_knowledge", knowledge=player.knowledge)
    draw_text(surf, know_label, (380, y), fonts["md"], C_BLUE)

    # Inventory items
    if player.items:
        draw_text(surf, loc.t("items.inventory_label"), (580, y), fonts["md"], C_GOLD)
        ix = 740
        for item_id in player.items:
            draw_text(surf, item_id, (ix, y), fonts["sm"], C_DIM)
            ix += 80


# ── Map tile art ──────────────────────────────────────────────────────────────

def draw_map_tile(surf, rect: Rect, tile_type: str, explored: bool,
                  is_player: bool, is_hover: bool) -> None:
    """Draw one 104×104 map tile with terrain art."""
    if not explored:
        # Unknown: dark with fog
        pygame.draw.rect(surf, (20, 20, 30), rect, border_radius=6)
        pygame.draw.rect(surf, (45, 45, 55), rect, 1, border_radius=6)
        # Question mark
        _draw_text_centered(surf, "?", rect, (70, 70, 90))
        return

    color = TILE_COLORS.get(tile_type, (60, 60, 60))

    if tile_type in _tile_surfaces:
        # AI-generated thumbnail
        pygame.draw.rect(surf, (0, 0, 0), rect, border_radius=6)
        thumb = _tile_surfaces[tile_type]
        surf.blit(thumb, (rect.x + 3, rect.y + 3))
    else:
        # Procedural fallback
        dim = _darken(color, 0.18)
        pygame.draw.rect(surf, dim, rect, border_radius=6)
        if   tile_type == "Forest":       _map_forest(surf, rect)
        elif tile_type == "River":        _map_river(surf, rect)
        elif tile_type == "Clearing":     _map_clearing(surf, rect)
        elif tile_type == "Dense Jungle": _map_jungle(surf, rect)
        elif tile_type == "Camp":         _map_camp(surf, rect)

    # Border
    border_col = color if (is_player or is_hover) else _darken(color, 0.5)
    thickness = 3 if is_player else (2 if is_hover else 1)
    pygame.draw.rect(surf, border_col, rect, thickness, border_radius=6)

    # Player tile gets a bright inner glow — the sprite itself is drawn by draw_map()
    if is_player:
        inner = Rect(rect.x + 2, rect.y + 2, rect.w - 4, rect.h - 4)
        pygame.draw.rect(surf, color, inner, 2, border_radius=4)


def _darken(color, factor):
    return tuple(max(0, int(c * factor)) for c in color)


def _draw_text_centered(surf, text, rect, color):
    from pathlib import Path
    font_path = r"C:\Windows\Fonts\arial.ttf"
    font = pygame.font.Font(font_path if Path(font_path).exists() else None, 32)
    img = font.render(str(text), True, color)
    surf.blit(img, (rect.centerx - img.get_width() // 2,
                    rect.centery - img.get_height() // 2))


def _map_forest(surf, rect):
    r = random.Random(rect.x * 31 + rect.y)
    # Ground
    pygame.draw.rect(surf, (30, 80, 30), rect, border_radius=6)
    # Trees
    for i in range(3):
        tx = rect.x + 14 + i * 30 + r.randint(-4, 4)
        ty = rect.y + 20 + r.randint(-5, 5)
        # trunk
        pygame.draw.rect(surf, (80, 50, 20), Rect(tx + 7, ty + 30, 10, 30))
        # foliage layers
        for radius, shade in [(24, (20,120,20)), (20,(40,160,40)), (14,(60,190,60))]:
            pygame.draw.circle(surf, shade, (tx + 12, ty + 28), radius)


def _map_river(surf, rect):
    # Green banks
    pygame.draw.rect(surf, (30, 90, 30), rect, border_radius=6)
    # River channel
    river_r = Rect(rect.x + 28, rect.y, 48, rect.h)
    pygame.draw.rect(surf, (40, 100, 200), river_r)
    # Wave lines
    for i in range(4):
        wy = rect.y + 18 + i * 20
        pygame.draw.arc(surf, (80, 160, 240),
                        Rect(rect.x + 30, wy, 24, 10), 0, math.pi, 2)
        pygame.draw.arc(surf, (80, 160, 240),
                        Rect(rect.x + 54, wy + 5, 20, 10), 0, math.pi, 2)


def _map_clearing(surf, rect):
    # Bright grass
    pygame.draw.rect(surf, (80, 160, 50), rect, border_radius=6)
    r = random.Random(rect.x + rect.y * 7)
    for _ in range(6):
        fx = rect.x + r.randint(8, rect.w - 8)
        fy = rect.y + r.randint(8, rect.h - 8)
        pygame.draw.circle(surf, (220, 80, 120), (fx, fy), 5)
        pygame.draw.circle(surf, (255, 240, 80), (fx, fy), 3)
    # Sun
    pygame.draw.circle(surf, (255, 230, 60), (rect.right - 16, rect.y + 16), 10)


def _map_jungle(surf, rect):
    # Dark canopy
    pygame.draw.rect(surf, (10, 40, 10), rect, border_radius=6)
    r = random.Random(rect.x * 13 + rect.y)
    for i in range(5):
        lx = rect.x + r.randint(0, rect.w - 20)
        ly = rect.y + r.randint(0, rect.h - 20)
        pygame.draw.ellipse(surf, (20, 80, 20), Rect(lx, ly, 22, 16))
    # Vines
    for i in range(2):
        vx = rect.x + 20 + i * 50
        pygame.draw.line(surf, (30, 100, 30), (vx, rect.y), (vx + 5, rect.bottom), 2)


def _map_camp(surf, rect):
    # Night sky
    pygame.draw.rect(surf, (20, 20, 60), rect, border_radius=6)
    # Stars
    r = random.Random(rect.x + rect.y)
    for _ in range(8):
        sx = rect.x + r.randint(4, rect.w - 4)
        sy = rect.y + r.randint(4, rect.h // 2)
        pygame.draw.circle(surf, (220, 220, 255), (sx, sy), 1)
    # Campfire glow
    cx, cy = rect.centerx, rect.centery + 10
    for rad, col in [(22, (80,30,0)), (15, (180,80,0)), (9, (240,160,0)), (5, (255,230,80))]:
        pygame.draw.ellipse(surf, col, Rect(cx - rad, cy - rad // 2, rad * 2, rad))
    # Tent
    pts = [(rect.centerx - 20, cy - 5), (rect.centerx, cy - 28), (rect.centerx + 20, cy - 5)]
    pygame.draw.polygon(surf, (80, 60, 30), pts)


# ── Scene background art (full 1024×MAP_AREA_H) ───────────────────────────────

def draw_scene_bg(surf, tile_type: str, seed: int = 0) -> None:
    """Draw scene background — uses AI-generated PNG if available, else procedural art.

    When multiple variants exist for a tile type, picks one deterministically
    using `seed` (which is derived from the tile's grid position in main.py),
    so each tile of the same type shows a different image.
    Animated overlays are always drawn on top.
    """
    if tile_type in _scene_surfaces:
        variants = _scene_surfaces[tile_type]
        surf.blit(variants[seed % len(variants)], (0, 0))
    else:
        # Procedural fallback
        area = Rect(0, 0, W, MAP_AREA_H)
        funcs = {
            "Forest":       _draw_forest,
            "River":        _draw_river,
            "Clearing":     _draw_clearing,
            "Dense Jungle": _draw_jungle,
            "Camp":         _draw_camp,
        }
        fn = funcs.get(tile_type, _draw_forest)
        fn(surf, area, seed)
    _draw_scene_animation(surf, tile_type, seed)


def _draw_scene_animation(surf, tile_type: str, seed: int) -> None:
    """Per-frame animated overlays drawn on top of scene background.

    All movement is driven by pygame.time.get_ticks() so it runs continuously.
    Positional variation per tile comes from `seed` via a seeded RNG.
    """
    t   = pygame.time.get_ticks() / 1000.0
    tau = math.pi * 2
    rng = random.Random(seed ^ 0xA4B3C2D1)

    # ── Falling leaves (Forest, Clearing, Dense Jungle) ──────────────────────
    if tile_type in ("Forest", "Clearing", "Dense Jungle"):
        palette = {
            "Forest":       [(55, 150, 35), (75, 130, 25), (170, 110, 25)],
            "Clearing":     [(55, 170, 35), (210, 170, 50), (190,  90, 50)],
            "Dense Jungle": [(15,  80, 15), ( 25, 100, 25), ( 35, 120, 30)],
        }[tile_type]
        for _ in range(6):
            x0  = rng.randint(30, W - 30)
            spd = 30 + rng.random() * 35
            amp = 25 + rng.random() * 35
            swf = 0.5 + rng.random() * 0.8
            ph  = rng.random() * tau
            sz  = 3 + int(rng.random() * 4)
            col = rng.choice(palette)
            period = (MAP_AREA_H + 60) / spd
            t_off  = rng.random() * period
            t_n    = (t + t_off) % period
            lx = int(x0 + amp * math.sin(t * swf + ph))
            ly = int(-20 + (MAP_AREA_H + 40) * t_n / period)
            ang = t * 1.2 + ph
            pts = [
                (lx + int(sz * math.cos(ang + k * 2.094)),
                 ly + int(sz * math.sin(ang + k * 2.094)))
                for k in range(3)
            ]
            pygame.draw.polygon(surf, col, pts)

    # ── Water ripples + sparkles (River) ─────────────────────────────────────
    if tile_type == "River":
        # Water starts ~40 % down in all 3 variants and spans nearly full width
        wy    = MAP_AREA_H * 2 // 5          # ≈ y=224  (was MAP_AREA_H//2 = 280)
        rsurf = pygame.Surface((W, MAP_AREA_H), pygame.SRCALPHA)
        for _ in range(4):
            rx  = rng.randint(160, W - 160)  # wider — water reaches near both edges
            ry  = rng.randint(wy + 20, MAP_AREA_H - 30)
            per = 2.2 + rng.random() * 1.8
            ph  = rng.random() * per
            tn  = (t + ph) % per
            rad = int(tn / per * 70)
            alp = int(160 * (1 - tn / per))
            if rad > 3 and alp > 15:
                pygame.draw.ellipse(rsurf, (140, 200, 255, alp),
                                    Rect(rx - rad, ry - rad // 3, rad * 2, rad * 2 // 3), 2)
        surf.blit(rsurf, (0, 0))
        for _ in range(5):
            sx    = rng.randint(140, W - 140)  # match wider ripple range
            sy    = rng.randint(wy + 10, MAP_AREA_H - 20)
            blink = (math.sin(t * (2.5 + rng.random() * 2) + rng.random() * tau) + 1) / 2
            if blink > 0.65:
                b = int(180 + 75 * blink)
                pygame.draw.circle(surf, (b, b, b), (sx, sy), 2)

    # ── Butterflies (Clearing, Forest) ───────────────────────────────────────
    if tile_type in ("Clearing", "Forest"):
        n = 3 if tile_type == "Clearing" else 2
        for _ in range(n):
            cx  = rng.randint(W // 5, W * 4 // 5)
            cy  = rng.randint(MAP_AREA_H // 5, MAP_AREA_H * 2 // 3)
            fx  = 0.22 + rng.random() * 0.18
            fy  = 0.45 + rng.random() * 0.30
            ax  = 70   + rng.random() * 90
            ay  = 35   + rng.random() * 45
            ph  = rng.random() * tau
            col = rng.choice([(80, 120, 220), (210, 80, 150), (195, 155, 40), (80, 190, 80)])
            bx  = int(cx + ax * math.sin(t * fx + ph))
            by  = int(cy + ay * math.sin(t * fy * 2 + ph))
            flap = abs(math.sin(t * 7 + ph))
            ws   = int(7 + 3 * flap)
            hs   = int(4 + 2 * flap)
            pygame.draw.ellipse(surf, col, Rect(bx - ws - 1, by - hs, ws, hs * 2))
            pygame.draw.ellipse(surf, col, Rect(bx + 2,      by - hs, ws, hs * 2))
            pygame.draw.circle(surf, (35, 25, 15), (bx, by), 2)

    # ── Fireflies (Camp, Dense Jungle) ───────────────────────────────────────
    if tile_type in ("Camp", "Dense Jungle"):
        ffsurf = pygame.Surface((W, MAP_AREA_H), pygame.SRCALPHA)
        n_ff   = 14 if tile_type == "Camp" else 9
        for _ in range(n_ff):
            bx  = rng.randint(40, W - 40)
            by  = rng.randint(30, MAP_AREA_H - 70)
            dxp = rng.random() * tau
            dyp = rng.random() * tau
            blf = 1.2 + rng.random() * 2.0
            blp = rng.random() * tau
            fx  = int(bx + 20 * math.sin(t * 0.28 + dxp))
            fy  = int(by + 12 * math.sin(t * 0.35 + dyp))
            br  = (math.sin(t * blf + blp) + 1) / 2
            if br > 0.25:
                a  = int(br * 210)
                gr = int(3 + br * 5)
                pygame.draw.circle(ffsurf, (210, 245, 120, a), (fx, fy), gr)
                pygame.draw.circle(ffsurf, (240, 255, 190, min(255, a + 60)), (fx, fy), 2)
        surf.blit(ffsurf, (0, 0))

    # ── Swaying vines (Dense Jungle) ─────────────────────────────────────────
    if tile_type == "Dense Jungle":
        vsurf = pygame.Surface((W, MAP_AREA_H), pygame.SRCALPHA)
        # Positions cover: outer-left trunk, inner-left, centre (dominant in v3), inner-right, outer-right
        for vxb in [120, 330, 510, 690, 900]:
            vxb += rng.randint(-25, 25)
            sa  = 7 + rng.random() * 8
            sf  = 0.35 + rng.random() * 0.3
            ph  = rng.random() * tau
            n_seg = 18
            pts = [
                (int(vxb + sa * math.sin(t * sf + ph + s * 0.25)),
                 s * (MAP_AREA_H // n_seg))
                for s in range(n_seg)
            ]
            pygame.draw.lines(vsurf, (35, 115, 25, 170), False, pts, 2)
        surf.blit(vsurf, (0, 0))

    # ── Campfire flicker glow (Camp) ─────────────────────────────────────────
    if tile_type == "Camp":
        # Fire sits slightly left of centre in the generated image (~x=450)
        cx, cy  = W * 9 // 20, MAP_AREA_H * 2 // 3 + 10
        flicker = 0.85 + 0.15 * math.sin(t * 12.3) + 0.08 * math.sin(t * 7.7)
        gsurf   = pygame.Surface((W, MAP_AREA_H), pygame.SRCALPHA)
        for gr, ga in [(55, 30), (40, 50), (28, 65), (18, 80)]:
            gr2 = int(gr * flicker)
            if gr2 > 0:
                pygame.draw.ellipse(gsurf, (240, 140, 30, ga),
                                    Rect(cx - gr2, cy - gr2 // 2, gr2 * 2, gr2))
        surf.blit(gsurf, (0, 0))


def _draw_forest(surf, area, seed=0):
    r = random.Random(seed ^ 0x1A2B)
    # Sky gradient — slight time-of-day shift per tile
    sky_r = r.randint(-15, 25)
    for i in range(area.h // 3):
        t = i / (area.h / 3)
        col = (max(0, min(255, int(80 + 100 * t + sky_r))),
               int(140 + 80 * t),
               max(0, min(255, int(200 - 60 * t - sky_r))))
        pygame.draw.line(surf, col, (0, i), (W, i))
    # Ground
    g_shade = r.randint(-8, 8)
    ground_y = area.h * 2 // 3
    pygame.draw.rect(surf, (30 + g_shade, 90 + g_shade, 30), Rect(0, ground_y, W, area.h - ground_y))
    pygame.draw.rect(surf, (50 + g_shade, 120, 40), Rect(0, ground_y, W, 18))

    # Background trees (3 or 4 clusters, positions vary per tile)
    base_positions = [(80, 320), (440, 370), (800, 310), (240, 345)]
    n_trees = r.choice([3, 3, 4])
    for i in range(n_trees):
        tx, base_h = base_positions[i]
        tx += r.randint(-40, 40)
        _forest_tree_cluster(surf, tx, ground_y, base_h + r.randint(-30, 30))

    # Foreground foliage at bottom
    for x in range(0, W, 60):
        h = 40 + (x % 3) * 10
        pts = [(x, area.h), (x + 30, area.h - h), (x + 60, area.h)]
        pygame.draw.polygon(surf, (20, 70, 20), pts)


def _forest_tree_cluster(surf, cx, ground_y, tree_h):
    # Trunk
    trunk_w = 28
    pygame.draw.rect(surf, (90, 55, 20),
                     Rect(cx - trunk_w // 2, ground_y - tree_h // 2, trunk_w, tree_h // 2))
    # Canopy layers
    for r, col, dy in [
        (tree_h // 3,      (20, 100, 20), 0),
        (tree_h * 27 // 90,(35, 140, 35), -tree_h // 8),
        (tree_h * 20 // 90,(50, 170, 50), -tree_h // 4),
    ]:
        pygame.draw.circle(surf, col, (cx, ground_y - tree_h // 2 + dy), r)


def _draw_river(surf, area, seed=0):
    r = random.Random(seed ^ 0x3C4D)
    sky_shift = r.randint(-10, 20)
    for i in range(area.h // 2):
        t = i / (area.h / 2)
        col = (max(0, min(255, int(100 + 80 * t + sky_shift))),
               int(170 + 50 * t),
               max(0, min(255, int(230 - 40 * t))))
        pygame.draw.line(surf, col, (0, i), (W, i))
    # Banks — width varies slightly per tile
    bank_w = r.randint(230, 290)
    pygame.draw.rect(surf, (40, 110, 40), Rect(0, area.h // 2, bank_w, area.h // 2))
    pygame.draw.rect(surf, (40, 110, 40), Rect(W - bank_w, area.h // 2, bank_w, area.h // 2))
    # Water
    water_x = bank_w
    pygame.draw.rect(surf, (30, 100, 200), Rect(water_x, area.h // 2, W - bank_w * 2, area.h // 2))
    # Water shimmer
    for i in range(6):
        wy = area.h // 2 + 30 + i * 35
        pygame.draw.arc(surf, (80, 160, 255),
                        Rect(water_x + 40, wy, 80, 20), 0, math.pi, 3)
        pygame.draw.arc(surf, (80, 160, 255),
                        Rect(water_x + 160, wy + 15, 70, 18), 0, math.pi, 3)
        pygame.draw.arc(surf, (80, 160, 255),
                        Rect(water_x + 280, wy + 5, 60, 16), 0, math.pi, 2)
    # Lily pads — positions vary per tile
    r2 = random.Random(seed ^ 0x4455)
    for _ in range(3):
        lx = r2.randint(water_x + 30, W - bank_w - 30)
        ly = r2.randint(area.h // 2 + 60, area.h - 50)
        pygame.draw.ellipse(surf, (20, 130, 20), Rect(lx - 25, ly - 12, 50, 24))
        pygame.draw.circle(surf, (220, 80, 120), (lx, ly - 8), 7)
    # Bank trees
    for tx in [60, 160]:
        pygame.draw.rect(surf, (80, 50, 20), Rect(tx, area.h // 2 - 80, 14, 80))
        pygame.draw.circle(surf, (30, 120, 30), (tx + 7, area.h // 2 - 90), 40)
    for tx in [W - 80, W - 180]:
        pygame.draw.rect(surf, (80, 50, 20), Rect(tx, area.h // 2 - 80, 14, 80))
        pygame.draw.circle(surf, (30, 120, 30), (tx + 7, area.h // 2 - 90), 40)


def _draw_clearing(surf, area, seed=0):
    r = random.Random(seed ^ 0x5E6F)
    for i in range(area.h * 2 // 3):
        t = i / (area.h * 2 / 3)
        col = (int(120 + 80 * t), int(180 + 50 * t), int(240 - 30 * t))
        pygame.draw.line(surf, col, (0, i), (W, i))
    # Sun — position varies per tile
    sun_x = r.randint(W - 170, W - 70)
    sun_y = r.randint(50, 100)
    pygame.draw.circle(surf, (255, 240, 80), (sun_x, sun_y), 55)
    for a in range(0, 360, 30):
        rad = math.radians(a)
        x1 = sun_x + int(65 * math.cos(rad))
        y1 = sun_y + int(65 * math.sin(rad))
        x2 = sun_x + int(85 * math.cos(rad))
        y2 = sun_y + int(85 * math.sin(rad))
        pygame.draw.line(surf, (255, 230, 100), (x1, y1), (x2, y2), 3)
    # Ground
    ground_y = area.h * 2 // 3
    pygame.draw.rect(surf, (80, 170, 50), Rect(0, ground_y, W, area.h - ground_y))
    pygame.draw.rect(surf, (100, 200, 70), Rect(0, ground_y, W, 20))
    # Flowers — count and color palette vary per tile
    n_flowers = r.randint(20, 45)
    r2 = random.Random(seed ^ 0x7788)
    palette = [(220, 80, 120), (240, 200, 60), (180, 100, 220), (255, 120, 50), (100, 200, 255)]
    for _ in range(n_flowers):
        fx = r2.randint(20, W - 20)
        fy = r2.randint(ground_y + 10, area.h - 20)
        col = r2.choice(palette)
        pygame.draw.circle(surf, col, (fx, fy), 7)
        pygame.draw.circle(surf, (255, 255, 200), (fx, fy), 3)
    # Edge shrubs
    for sx in [0, W - 100]:
        for i in range(3):
            pygame.draw.circle(surf, (30, 110, 30),
                               (sx + 50 + i * 30, ground_y + 20), 35 - i * 5)


def _draw_jungle(surf, area, seed=0):
    r = random.Random(seed ^ 0x9AAB)
    # Darkness varies slightly per tile
    dark_shift = r.randint(0, 18)
    for i in range(area.h):
        t = i / area.h
        col = (int(5 + 25 * t),
               max(0, int(20 + 60 * t - dark_shift)),
               int(5 + 20 * t))
        pygame.draw.line(surf, col, (0, i), (W, i))
    # Ground
    pygame.draw.rect(surf, (20, 55, 15), Rect(0, area.h - 120, W, 120))

    # Light shafts — positions vary
    r2 = random.Random(seed ^ 0xBCDE)
    for base_sx in [180, 420, 650, 870]:
        sx = base_sx + r2.randint(-50, 50)
        shaft_pts = [(sx - 30, 0), (sx + 30, 0), (sx + 60, area.h), (sx - 60, area.h)]
        shaft_surf = pygame.Surface((W, area.h), pygame.SRCALPHA)
        pygame.draw.polygon(shaft_surf, (255, 255, 200, 18), shaft_pts)
        surf.blit(shaft_surf, (0, 0))

    # Overlapping foliage blobs — density varies
    r3 = random.Random(seed ^ 0xCDEF)
    n_blobs = r3.randint(15, 28)
    for _ in range(n_blobs):
        lx = r3.randint(0, W)
        ly = r3.randint(0, area.h * 2 // 3)
        lw = r3.randint(80, 200)
        lh = r3.randint(40, 100)
        shade = (r3.randint(10, 40), r3.randint(70, 140), r3.randint(10, 40))
        pygame.draw.ellipse(surf, shade, Rect(lx - lw // 2, ly - lh // 2, lw, lh))

    # Hanging vines — x positions vary
    r4 = random.Random(seed ^ 0xDEF0)
    for base_vx in [120, 290, 490, 680, 850]:
        vx = base_vx + r4.randint(-30, 30)
        pts = []
        for seg in range(20):
            px = vx + int(12 * math.sin(seg * 0.6))
            py = seg * (area.h // 20)
            pts.append((px, py))
        pygame.draw.lines(surf, (30, 100, 20), False, pts, 3)


def _draw_camp(surf, area, seed=0):  # noqa: seed unused (camp is unique)
    # Deep night sky
    for i in range(area.h * 2 // 3):
        t = i / (area.h * 2 / 3)
        col = (int(10 + 20 * t), int(10 + 30 * t), int(40 + 60 * t))
        pygame.draw.line(surf, col, (0, i), (W, i))
    # Stars
    r4 = random.Random(12)
    for _ in range(60):
        sx = r4.randint(0, W)
        sy = r4.randint(0, area.h * 2 // 5)
        br = r4.randint(150, 255)
        pygame.draw.circle(surf, (br, br, br), (sx, sy), r4.randint(1, 2))
    # Ground
    ground_y = area.h * 2 // 3
    pygame.draw.rect(surf, (25, 40, 20), Rect(0, ground_y, W, area.h - ground_y))

    # Campfire glow on ground
    for glow_r in range(120, 0, -10):
        alpha = max(0, 40 - (120 - glow_r) // 2)
        gs = pygame.Surface((glow_r * 2, glow_r), pygame.SRCALPHA)
        pygame.draw.ellipse(gs, (220, 120, 20, alpha), gs.get_rect())
        surf.blit(gs, (W // 2 - glow_r, ground_y + 20))

    # Campfire flames
    cx, cy = W // 2, ground_y + 10
    for rad, col in [(50, (100,40,0)), (38, (200,80,0)), (26, (240,150,0)), (14, (255,230,80))]:
        pygame.draw.ellipse(surf, col, Rect(cx - rad, cy - rad // 2, rad * 2, rad))

    # Log cross
    pygame.draw.rect(surf, (80, 45, 15), Rect(cx - 45, cy + 8, 90, 14), border_radius=4)
    pygame.draw.rect(surf, (80, 45, 15), Rect(cx - 10, cy, 20, 30), border_radius=4)

    # Tent (left)
    tent_cx = W // 2 - 250
    tent_pts = [(tent_cx - 80, ground_y + 2), (tent_cx, ground_y - 110), (tent_cx + 80, ground_y + 2)]
    pygame.draw.polygon(surf, (70, 50, 25), tent_pts)
    pygame.draw.polygon(surf, (100, 75, 40), tent_pts, 2)
    pygame.draw.rect(surf, (40, 28, 10),
                     Rect(tent_cx - 20, ground_y - 45, 40, 48), border_radius=4)

    # Tent (right)
    tent_cx2 = W // 2 + 250
    tent_pts2 = [(tent_cx2 - 80, ground_y + 2), (tent_cx2, ground_y - 110), (tent_cx2 + 80, ground_y + 2)]
    pygame.draw.polygon(surf, (70, 50, 25), tent_pts2)
    pygame.draw.polygon(surf, (100, 75, 40), tent_pts2, 2)
    pygame.draw.rect(surf, (40, 28, 10),
                     Rect(tent_cx2 - 20, ground_y - 45, 40, 48), border_radius=4)

    # Journal & skills journal on ground
    pygame.draw.rect(surf, (140, 100, 40), Rect(tent_cx - 35, ground_y + 5, 50, 35), border_radius=3)
    pygame.draw.rect(surf, (160, 120, 60), Rect(tent_cx2 - 15, ground_y + 5, 50, 35), border_radius=3)


# ── Object label overlay on scene ─────────────────────────────────────────────

def _draw_object_label(surf, rect: Rect, label: str, font, hover: bool) -> None:
    """Draw a subtle label/glow at the bottom of an object hotspot."""
    if hover:
        # Glow outline
        glow_s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        pygame.draw.rect(glow_s, (255, 255, 255, 35), glow_s.get_rect(), border_radius=8)
        pygame.draw.rect(glow_s, (255, 255, 255, 80), glow_s.get_rect(), 2, border_radius=8)
        surf.blit(glow_s, rect.topleft)
        # Label badge
        img = font.render(_bidi(_EMOJI_RE.sub('', label)), True, C_WHITE)
        lx = rect.centerx - img.get_width() // 2
        ly = rect.bottom - img.get_height() - 6
        badge = Rect(lx - 6, ly - 4, img.get_width() + 12, img.get_height() + 8)
        pygame.draw.rect(surf, (0, 0, 0, 180), badge, border_radius=6)
        pygame.draw.rect(surf, C_GREEN, badge, 1, border_radius=6)
        surf.blit(img, (lx, ly))
    else:
        # Just a subtle dim outline
        dim_s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        pygame.draw.rect(dim_s, (255, 255, 255, 12), dim_s.get_rect(), border_radius=8)
        surf.blit(dim_s, rect.topleft)


# ── Loading screen (shown during asset generation) ────────────────────────────

def draw_loading_screen(surf, fonts, message: str, step: int, total: int) -> None:
    """Draw the one-time asset-generation loading screen."""
    surf.fill((8, 15, 8))

    # Background tree silhouettes
    for tx in range(0, W + 60, 80):
        h = 100 + (tx % 5) * 28
        pygame.draw.rect(surf, (12, 35, 12), Rect(tx - 20, H - h, 46, h))
        pygame.draw.circle(surf, (18, 50, 18), (tx + 3, H - h), 32)

    # Stars
    r_stars = random.Random(888)
    for _ in range(50):
        sx = r_stars.randint(0, W)
        sy = r_stars.randint(0, H // 2)
        pygame.draw.circle(surf, (180, 180, 240), (sx, sy), 1)

    # Title
    draw_text(surf, loc.t("ui.loading_title"), (W // 2, H // 2 - 120),
              fonts["xl"], C_GOLD, align="center")

    # Progress bar
    bar_w, bar_h = 520, 26
    bar_x = W // 2 - bar_w // 2
    bar_y = H // 2 - 16
    pygame.draw.rect(surf, (25, 45, 25), Rect(bar_x, bar_y, bar_w, bar_h), border_radius=13)
    if total > 0:
        fill = int(bar_w * min(1.0, step / total))
        if fill > 0:
            pygame.draw.rect(surf, C_GOLD, Rect(bar_x, bar_y, fill, bar_h), border_radius=13)
    pygame.draw.rect(surf, C_GREEN, Rect(bar_x, bar_y, bar_w, bar_h), 2, border_radius=13)

    # Step counter
    if total > 0:
        draw_text(surf, f"{step} / {total}", (W // 2, bar_y + bar_h + 8),
                  fonts["sm"], C_DIM, align="center")

    # Status message (plain ASCII — no bidi issues)
    clean_msg = _EMOJI_RE.sub('', str(message)).strip()
    img = fonts["md"].render(clean_msg, True, C_WHITE)
    surf.blit(img, (W // 2 - img.get_width() // 2, H // 2 + 42))

    # Note
    draw_text(surf, loc.t("ui.loading_once"), (W // 2, H // 2 + 90),
              fonts["md"], C_GREEN, align="center")


# ── Full screen: Title ────────────────────────────────────────────────────────

def draw_title(surf, fonts) -> dict:
    """Draw title screen. Returns {'start': Rect}."""
    surf.fill(C_BG)
    # Background forest silhouette
    for tx in range(0, W + 60, 80):
        h = 120 + (tx % 5) * 30
        pygame.draw.rect(surf, (15, 45, 15), Rect(tx - 20, H - h, 50, h))
        pygame.draw.circle(surf, (15, 55, 15), (tx + 5, H - h), 35)

    # Title panel
    panel = Rect(W // 2 - 340, H // 2 - 160, 680, 220)
    draw_panel(surf, panel, font=fonts["lg"],
               bg=(10, 30, 10), edge=(60, 180, 60))

    line1 = loc.t("ui.title_line1")
    line2 = loc.t("ui.title_line2")
    draw_text(surf, line1, (W // 2, panel.y + 45), fonts["xl"], C_GREEN, align="center")
    draw_text(surf, line2, (W // 2, panel.y + 110), fonts["lg"], C_GOLD, align="center")

    # Start button
    btn = Rect(W // 2 - 110, H // 2 + 90, 220, 54)
    draw_button(surf, btn, loc.t("setup.welcome"), fonts["md"], hover=True)

    return {"start": btn}


# ── Full screen: Name Setup ───────────────────────────────────────────────────

def draw_setup_name(surf, fonts, text: str) -> dict:
    """Draw name input screen. Returns {'input': Rect}."""
    surf.fill(C_BG)
    draw_text(surf, loc.t("setup.ask_name"), (W // 2, 200), fonts["xl"], C_GREEN, align="center")

    input_r = Rect(W // 2 - 200, 290, 400, 54)
    pygame.draw.rect(surf, (30, 50, 30), input_r, border_radius=8)
    pygame.draw.rect(surf, C_GREEN, input_r, 2, border_radius=8)
    display = text + "|"
    draw_text(surf, display, (input_r.x + 14, input_r.y + 14), fonts["lg"], C_WHITE)

    draw_text(surf, loc.t("ui.press_enter"), (W // 2, 380), fonts["md"], C_DIM, align="center")
    return {"input": input_r}


# ── Full screen: Avatar Setup ─────────────────────────────────────────────────

def draw_setup_avatar(surf, fonts, hover_idx: int, selected_idx: int) -> dict:
    """Draw avatar selection screen. Returns {'btns': [Rect, ...]}."""
    from models import AVATAR_OPTIONS
    surf.fill(C_BG)
    draw_text(surf, loc.t("setup.choose_avatar"), (W // 2, 160), fonts["xl"], C_GREEN, align="center")

    labels = [
        (AVATAR_OPTIONS[0], loc.t("setup.avatar_1")),
        (AVATAR_OPTIONS[1], loc.t("setup.avatar_2")),
        (AVATAR_OPTIONS[2], loc.t("setup.avatar_3")),
        (AVATAR_OPTIONS[3], loc.t("setup.avatar_4")),
    ]
    btns = []
    bw, bh = 180, 100
    total_w = len(labels) * bw + (len(labels) - 1) * 20
    start_x = (W - total_w) // 2
    for i, (emoji, label_text) in enumerate(labels):
        r = Rect(start_x + i * (bw + 20), 270, bw, bh)
        hover = (i == hover_idx)
        selected = (i == selected_idx)
        bg_col = (50, 100, 50) if selected else (40, 70, 40) if hover else (25, 45, 25)
        edge_col = C_GOLD if selected else C_GREEN if hover else C_GREEN_DARK
        pygame.draw.rect(surf, bg_col, r, border_radius=12)
        pygame.draw.rect(surf, edge_col, r, 3 if selected else 2, border_radius=12)
        draw_text(surf, emoji, (r.centerx, r.y + 14), fonts["xl"], C_WHITE, align="center")
        btns.append(r)

    # Confirm button
    if selected_idx >= 0:
        confirm = Rect(W // 2 - 120, 420, 240, 54)
        draw_button(surf, confirm, loc.t("setup.hello", name=""), fonts["md"], hover=True)
        return {"btns": btns, "confirm": confirm}

    return {"btns": btns}


# ── Full screen: Map ──────────────────────────────────────────────────────────

def _tile_map_center(tx: int, ty: int) -> tuple:
    """Pixel centre of a map tile, shifted down slightly so the character stands on it."""
    return (
        MAP_OFFSET_X + tx * TILE_W + (TILE_W - 4) // 2,
        MAP_OFFSET_Y + ty * TILE_H + (TILE_H - 4) // 2 + 4,
    )


def _draw_map_background(surf) -> None:
    """Rich decorative jungle map background + gold frame around the grid."""
    # Vertical gradient: near-black green top → slightly warmer bottom
    for y in range(MAP_AREA_H):
        t = y / MAP_AREA_H
        pygame.draw.line(surf, (
            int(7  + 10 * t),
            int(14 + 20 * t),
            int(7  +  8 * t),
        ), (0, y), (W, y))

    # Scattered leaf silhouettes — only outside the tile grid area
    gx1 = MAP_OFFSET_X - 16
    gx2 = MAP_OFFSET_X + TILE_COLS * TILE_W + 16
    gy1 = MAP_OFFSET_Y - 16
    gy2 = MAP_OFFSET_Y + TILE_ROWS * TILE_H + 16
    rng = random.Random(0xC0FFEE)
    for _ in range(90):
        lx = rng.randint(4, W - 4)
        ly = rng.randint(4, MAP_AREA_H - 4)
        if gx1 < lx < gx2 and gy1 < ly < gy2:
            continue
        ang = rng.random() * math.pi
        sz  = rng.randint(10, 24)
        g   = rng.randint(45, 90)
        col = (rng.randint(4, 18), g, rng.randint(4, 18))
        pts = [
            (int(lx + sz       * math.cos(ang + k * math.pi / 3)),
             int(ly + sz * 0.4 * math.sin(ang + k * math.pi / 3)))
            for k in range(6)
        ]
        pygame.draw.polygon(surf, col, pts)

    # Gold decorative frame around the grid
    fx = MAP_OFFSET_X - 10
    fy = MAP_OFFSET_Y - 10
    fw = TILE_COLS * TILE_W + 20
    fh = TILE_ROWS * TILE_H + 20
    pygame.draw.rect(surf, (50, 38, 10),  Rect(fx - 3, fy - 3, fw + 6, fh + 6), 0, border_radius=13)
    pygame.draw.rect(surf, (80, 62, 18),  Rect(fx, fy, fw, fh), 4, border_radius=12)
    pygame.draw.rect(surf, (140, 110, 38), Rect(fx + 2, fy + 2, fw - 4, fh - 4), 2, border_radius=10)
    for cx2, cy2 in [(fx, fy), (fx + fw, fy), (fx, fy + fh), (fx + fw, fy + fh)]:
        pygame.draw.circle(surf, (60,  45, 10),  (cx2, cy2), 11)
        pygame.draw.circle(surf, (150, 115, 42), (cx2, cy2),  8)
        pygame.draw.circle(surf, (220, 178, 68), (cx2, cy2),  5)
        pygame.draw.circle(surf, (255, 235, 110),(cx2, cy2),  2)


def _draw_map_paths(surf, world) -> None:
    """Colour the narrow gap between adjacent explored tiles to look like jungle trails."""
    for ty in range(TILE_ROWS):
        for tx in range(TILE_COLS):
            if not world.grid[ty][tx].explored:
                continue
            # Horizontal gap to the right neighbour
            if tx + 1 < TILE_COLS and world.grid[ty][tx + 1].explored:
                gx  = MAP_OFFSET_X + (tx + 1) * TILE_W - 4   # start of 4-px gap
                cy2 = MAP_OFFSET_Y + ty * TILE_H + (TILE_H - 4) // 2
                pygame.draw.rect(surf, (40, 70, 25),  Rect(gx,     cy2 - 6, 4, 12))
                pygame.draw.rect(surf, (55, 95, 35),  Rect(gx,     cy2 - 4, 4,  8))
                pygame.draw.rect(surf, (70, 115, 42), Rect(gx + 1, cy2 - 2, 2,  4))
            # Vertical gap to the bottom neighbour
            if ty + 1 < TILE_ROWS and world.grid[ty + 1][tx].explored:
                cx2 = MAP_OFFSET_X + tx * TILE_W + (TILE_W - 4) // 2
                gy  = MAP_OFFSET_Y + (ty + 1) * TILE_H - 4   # start of 4-px gap
                pygame.draw.rect(surf, (40, 70, 25),  Rect(cx2 - 6, gy,     12, 4))
                pygame.draw.rect(surf, (55, 95, 35),  Rect(cx2 - 4, gy,      8, 4))
                pygame.draw.rect(surf, (70, 115, 42), Rect(cx2 - 2, gy + 1,  4, 2))


def _draw_map_explorer(surf, px: int, py: int) -> None:
    """Draw the explorer sprite on the world map with a pulsing shadow beneath."""
    t = pygame.time.get_ticks() / 1000.0
    pulse = 0.75 + 0.25 * math.sin(t * 3.5)
    sr = int(16 * pulse)
    ssurf = pygame.Surface((sr * 2 + 4, sr // 2 + 6), pygame.SRCALPHA)
    pygame.draw.ellipse(ssurf, (0, 0, 0, 90),
                        Rect(2, 2, sr * 2, sr // 2 + 2))
    surf.blit(ssurf, (px - sr - 2, py + 18))
    frame = (pygame.time.get_ticks() // 380) % 3
    creatures.draw_explorer(surf, px, py, size=44, frame=frame)


def draw_map(surf, fonts, game_state, hover_tile: tuple,
             player_anim: tuple | None = None) -> dict:
    """Draw the overworld map screen. Returns {'tiles': {(tx,ty): Rect}}."""
    surf.fill(C_BG)
    _draw_map_background(surf)
    _draw_map_paths(surf, game_state.world)

    # Header (drawn before tiles so it sits on the background)
    draw_text(surf, loc.t("map.header"), (W // 2, 16), fonts["lg"], C_GREEN, align="center")

    tile_rects = {}
    for ty in range(TILE_ROWS):
        for tx in range(TILE_COLS):
            rx = MAP_OFFSET_X + tx * TILE_W
            ry = MAP_OFFSET_Y + ty * TILE_H
            rect = Rect(rx, ry, TILE_W - 4, TILE_H - 4)
            tile = game_state.world.grid[ty][tx]
            is_player = (tx == game_state.player.x and ty == game_state.player.y)
            is_hover  = (hover_tile == (tx, ty)) and not is_player
            draw_map_tile(surf, rect, tile.tile_type, tile.explored, is_player, is_hover)
            tile_rects[(tx, ty)] = rect

    # Explorer character drawn on top of all tiles
    if player_anim is not None:
        px, py = player_anim
    else:
        px, py = _tile_map_center(game_state.player.x, game_state.player.y)
    _draw_map_explorer(surf, px, py)

    draw_status_bar(surf, fonts, game_state.player)

    # Legend hint
    draw_text(surf, loc.t("map.legend"), (W // 2, MAP_AREA_H - 22), fonts["sm"], C_DIM, align="center")

    return {"tiles": tile_rects}


# ── Full screen: Scene Objects ────────────────────────────────────────────────

_SCENE_HEADER_KEYS = {
    "Forest":       "scene.Forest_header",
    "River":        "scene.River_header",
    "Clearing":     "scene.Clearing_header",
    "Dense Jungle": "scene.Dense Jungle_header",
    "Camp":         "camp.header",
}

# Where the explorer stands in each scene (cx, cy)
_EXPLORER_POS = {
    "Forest":       (W // 2 - 100, MAP_AREA_H - 82),
    "River":        (150,           MAP_AREA_H - 82),
    "Clearing":     (W // 2,        MAP_AREA_H - 82),
    "Dense Jungle": (W // 2 + 80,   MAP_AREA_H - 82),
    "Camp":         (W // 2 - 130,  MAP_AREA_H - 82),
}


def draw_scene_objects(surf, fonts, tile_type: str, objects: list,
                       hover_idx: int, player_items: set, items_db: list,
                       tile_seed: int = 0) -> dict:
    """Draw scene background + object hotspots + explorer. Returns {'objects': [Rect,...], 'back': Rect}."""
    draw_scene_bg(surf, tile_type, seed=tile_seed)

    # Explorer avatar (animated via wall-clock time)
    ex, ey = _EXPLORER_POS.get(tile_type, (W // 2, MAP_AREA_H - 82))
    explorer_frame = (pygame.time.get_ticks() // 350) % 3
    creatures.draw_explorer(surf, ex, ey, size=72, frame=explorer_frame)

    rects = _OBJECT_RECTS.get(tile_type, [])
    for i, (obj, rect) in enumerate(zip(objects, rects)):
        label = loc.t(obj["name_key"])
        _draw_object_label(surf, rect, label, fonts["md"], hover=(i == hover_idx))

    draw_status_bar(surf, fonts, _dummy_player_access[0] if _dummy_player_access else None)

    # Back button
    back_btn = Rect(10, 10, 120, 40)
    draw_button(surf, back_btn, loc.t("obj.back_to_map"), fonts["sm"], hover=False)

    # Scene title
    color = TILE_COLORS.get(tile_type, C_WHITE)
    header_key = _SCENE_HEADER_KEYS.get(tile_type, "scene.Forest_header")
    draw_text(surf, loc.t(header_key), (W // 2, 14), fonts["md"], color, align="center")

    return {"objects": rects[:len(objects)], "back": back_btn}


# Global player ref injected by main.py so status bar works in scene views
_dummy_player_access = []


def set_player_ref(player) -> None:
    """Let main.py inject the player object for status bar rendering in scene screens."""
    _dummy_player_access.clear()
    _dummy_player_access.append(player)


# ── Full screen: Scene Interactions ──────────────────────────────────────────

_SKILL_DISPLAY_NAMES = {
    "explorer":        "\ud83d\udd0d \u05e1\u05d9\u05d9\u05e8\u05ea",
    "nature_friend":   "\ud83c\udf3f \u05d9\u05d3\u05d9\u05d3\u05ea \u05d4\u05d8\u05d1\u05e2",
    "survival_helper": "\ud83c\udf4e \u05e9\u05d5\u05e8\u05d3\u05ea",
}


def draw_scene_interactions(surf, fonts, tile_type: str, obj: dict,
                             player_items: set, items_db: list,
                             hover_btn: int, tile_seed: int = 0,
                             player_skills: dict | None = None) -> dict:
    """Draw scene bg dimmed + interaction panel. Returns {'btns': [Rect,...], 'back': Rect}."""
    draw_scene_bg(surf, tile_type, seed=tile_seed)

    # Dim overlay
    dim_s = pygame.Surface((W, MAP_AREA_H), pygame.SRCALPHA)
    pygame.draw.rect(dim_s, (0, 0, 0, 150), dim_s.get_rect())
    surf.blit(dim_s, (0, 0))

    draw_status_bar(surf, fonts, _dummy_player_access[0] if _dummy_player_access else None)

    # Interaction panel
    interactions = obj.get("interactions", [])
    panel_h = 80 + len(interactions) * 64 + 60
    panel = Rect(W // 2 - 320, MAP_AREA_H // 2 - panel_h // 2, 640, panel_h)
    draw_panel(surf, panel, title=loc.t(obj["name_key"]), font=fonts["md"],
               bg=(15, 30, 15, 230), edge=C_CYAN)

    btns = []
    for i, inter in enumerate(interactions):
        text = loc.t(inter["text_key"])

        # Determine lock state — item lock takes priority over skill lock for display
        requires_item  = inter.get("requires_item")
        requires_skill = inter.get("requires_skill")
        locked     = False
        lock_label = ""

        if requires_item and requires_item not in player_items:
            locked = True
            item = next((it for it in items_db if it.id == requires_item), None)
            if item:
                lock_label = f"{item.emoji} {item.name}"
        elif requires_skill:
            skill_id, min_level_str = requires_skill.split(":")
            min_level    = int(min_level_str)
            actual_skill = (player_skills or {}).get(skill_id)
            actual_level = actual_skill.level if actual_skill else 0
            if actual_level < min_level:
                locked = True
                skill_name = _SKILL_DISPLAY_NAMES.get(skill_id, skill_id)
                lock_label = f"{skill_name} \u05e8\u05de\u05d4 {min_level}"

        btn_r = Rect(panel.x + 30, panel.y + 50 + i * 64, panel.w - 60, 52)
        draw_button(surf, btn_r, text, fonts["md"],
                    hover=(i == hover_btn), locked=locked, lock_label=lock_label)
        btns.append(btn_r)

    # Back link
    back_y = panel.bottom - 44
    back_btn = Rect(panel.x + 30, back_y, panel.w - 60, 36)
    draw_button(surf, back_btn, loc.t("obj.back_to_objects"), fonts["sm"],
                hover=(hover_btn == len(interactions)))

    return {"btns": btns, "back": back_btn}


# ── Popup ─────────────────────────────────────────────────────────────────────

def draw_popup(surf, fonts, popup: dict) -> None:
    """Draw a dismissible popup (discovery / item / message). Click anywhere to dismiss."""
    draw_scene_bg(surf, popup.get("tile_type", "Forest"))

    dim_s = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.rect(dim_s, (0, 0, 0, 170), dim_s.get_rect())
    surf.blit(dim_s, (0, 0))

    kind = popup.get("kind", "message")

    # Panel size depends on kind
    if kind == "discovery_new":
        panel_w, panel_h = 840, 460
    elif kind == "discovery_old":
        panel_w, panel_h = 700, 260
    else:
        panel_w, panel_h = 660, 380
    panel = Rect(W // 2 - panel_w // 2, H // 2 - panel_h // 2, panel_w, panel_h)

    if kind == "discovery_new":
        edge = (255, 200, 0)
        draw_panel(surf, panel, font=fonts["lg"], bg=(25, 35, 10), edge=edge)
        d = popup["discovery"]

        # Full-width banner
        draw_text(surf, loc.t("discovery.new_banner_1"),
                  (panel.centerx, panel.y + 10), fonts["lg"], C_GOLD, align="center")

        # Creature art box — right half of panel
        art_box = Rect(panel.x + 510, panel.y + 54, 290, 330)
        pygame.draw.rect(surf, (12, 22, 12), art_box, border_radius=8)
        pygame.draw.rect(surf, edge, art_box, 1, border_radius=8)
        creatures.draw_creature(surf, d.id, art_box.centerx, art_box.centery, size=230)

        # Text — left column (width 460)
        tx = panel.x + 20
        draw_text(surf, d.name, (tx, panel.y + 48), fonts["xl"], C_WHITE)
        draw_text(surf, f"{loc.t('discovery.label_title')} {d.title}",
                  (tx, panel.y + 108), fonts["md"], C_CYAN)
        _draw_wrapped(surf, d.description, tx, panel.y + 152, 460, fonts["sm"], C_WHITE)
        _draw_wrapped(surf, f"{loc.t('discovery.label_fact')} {d.fun_fact}",
                      tx, panel.y + 258, 460, fonts["sm"], C_GREEN)
        if popup.get("knowledge_gained", 0) > 0:
            draw_text(surf, loc.t("discovery.knowledge_gain", amount=popup["knowledge_gained"]),
                      (tx, panel.y + 370), fonts["md"], C_GOLD)

    elif kind == "discovery_old":
        draw_panel(surf, panel, font=fonts["md"], bg=(20, 25, 20), edge=C_DIM)
        d = popup["discovery"]

        # Small creature art — right side
        art_box = Rect(panel.right - 165, panel.y + 36, 130, 130)
        pygame.draw.rect(surf, (15, 20, 15), art_box, border_radius=8)
        pygame.draw.rect(surf, C_DIM, art_box, 1, border_radius=8)
        creatures.draw_creature(surf, d.id, art_box.centerx, art_box.centery, size=100)

        draw_text(surf, f"{loc.t('discovery.already_known')} {d.name}",
                  (panel.x + 20, panel.y + 50), fonts["lg"], C_DIM)
        if popup.get("knowledge_gained", 0) > 0:
            draw_text(surf, loc.t("discovery.knowledge_gain", amount=popup["knowledge_gained"]),
                      (panel.x + 20, panel.y + 110), fonts["md"], C_BLUE)

    elif kind == "item_found":
        draw_panel(surf, panel, font=fonts["lg"], bg=(25, 35, 10), edge=C_GOLD)
        item = popup["item"]
        draw_text(surf, loc.t("items.found_banner_1"),
                  (W // 2, panel.y + 10), fonts["lg"], C_GOLD, align="center")
        draw_text(surf, f"{item.emoji}  {item.name}",
                  (W // 2, panel.y + 60), fonts["xl"], C_WHITE, align="center")
        _draw_wrapped(surf, item.description, panel.x + 30, panel.y + 130, panel.w - 60, fonts["md"], C_DIM)

    else:
        # Plain message
        draw_panel(surf, panel, bg=(20, 30, 20), edge=C_GREEN_DARK)
        _draw_wrapped(surf, popup.get("text", ""), panel.x + 30, panel.y + 60,
                      panel.w - 60, fonts["lg"], C_WHITE)

    draw_text(surf, loc.t("ui.press_enter"), (W // 2, panel.bottom - 30),
              fonts["sm"], C_DIM, align="center")


def _draw_wrapped(surf, text: str, x: int, y: int, max_w: int, font, color) -> int:
    """Draw word-wrapped text. Returns bottom y."""
    words = _bidi(_EMOJI_RE.sub('', str(text))).split()
    line = ""
    cy = y
    for word in words:
        test = (line + " " + word).strip()
        if font.size(test)[0] <= max_w:
            line = test
        else:
            if line:
                surf.blit(font.render(line, True, color), (x, cy))
                cy += font.get_height() + 4
            line = word
    if line:
        surf.blit(font.render(line, True, color), (x, cy))
        cy += font.get_height() + 4
    return cy


# ── Full screen: Discovery Book ───────────────────────────────────────────────

def draw_book(surf, fonts, game_state, discoveries_db: list,
              detail_entry=None, hover_idx: int = -1) -> dict:
    """Draw discovery book screen. Returns {'entries': [Rect,...], 'back': Rect}."""
    surf.fill(C_BG)
    draw_text(surf, loc.t("book.header"), (W // 2, 16), fonts["lg"], C_BLUE, align="center")

    back_btn = Rect(10, 10, 120, 40)
    draw_button(surf, back_btn, loc.t("obj.back_to_map"), fonts["sm"])

    discovered_ids = game_state.player.discovered
    total = len(discovered_ids)
    grand_total = len(discoveries_db)
    draw_text(surf, loc.t("book.count", count=total, total=grand_total),
              (W // 2, 58), fonts["md"], C_BLUE, align="center")

    if detail_entry:
        # Full entry detail view
        panel = Rect(60, 90, W - 120, H - 180)
        draw_panel(surf, panel, bg=C_PANEL_BG, edge=C_BLUE)

        # Creature art — right portion
        art_box = Rect(panel.right - 310, panel.y + 20, 280, 280)
        pygame.draw.rect(surf, (10, 18, 30), art_box, border_radius=8)
        pygame.draw.rect(surf, C_BLUE, art_box, 1, border_radius=8)
        creatures.draw_creature(surf, detail_entry.id, art_box.centerx, art_box.centery, size=220)

        # Text — left portion
        text_w = panel.w - 330
        y = panel.y + 16
        draw_text(surf, f"{detail_entry.name}", (panel.x + 20, y), fonts["xl"], C_WHITE)
        y += 60
        draw_text(surf, f"{loc.t('discovery.label_title')} {detail_entry.title}",
                  (panel.x + 20, y), fonts["md"], C_CYAN)
        y += 44
        y = _draw_wrapped(surf, detail_entry.description, panel.x + 20, y, text_w, fonts["md"], C_WHITE)
        y += 10
        _draw_wrapped(surf, f"{loc.t('discovery.label_fact')} {detail_entry.fun_fact}",
                      panel.x + 20, y, text_w, fonts["md"], C_GREEN)
        draw_text(surf, loc.t("ui.press_enter"), (W // 2, H - 50), fonts["sm"], C_DIM, align="center")
        return {"entries": [], "back": back_btn}

    # Entry list
    animals = [d for d in discoveries_db if d.id in discovered_ids and d.category == "animal"]
    plants  = [d for d in discoveries_db if d.id in discovered_ids and d.category == "plant"]
    all_entries = []
    entry_rects = []

    if total == 0:
        draw_text(surf, loc.t("book.empty"), (W // 2, 200), fonts["lg"], C_DIM, align="center")
        return {"entries": [], "back": back_btn}

    y = 90
    if animals:
        draw_text(surf, loc.t("book.animals_header"), (60, y), fonts["md"], C_GREEN)
        y += 32
        for entry in animals:
            r = Rect(60, y, W - 120, 42)
            hover = len(all_entries) == hover_idx
            bg = (35, 60, 35) if hover else (20, 35, 20)
            pygame.draw.rect(surf, bg, r, border_radius=6)
            if hover:
                pygame.draw.rect(surf, C_GREEN, r, 1, border_radius=6)
            draw_text(surf, f"{entry.emoji}  {entry.name}  —  {entry.title}",
                      (r.x + 14, r.y + 10), fonts["md"], C_WHITE if hover else C_DIM)
            all_entries.append(entry)
            entry_rects.append(r)
            y += 48

    if plants:
        y += 8
        draw_text(surf, loc.t("book.plants_header"), (60, y), fonts["md"], C_GREEN)
        y += 32
        for entry in plants:
            r = Rect(60, y, W - 120, 42)
            hover = len(all_entries) == hover_idx
            bg = (35, 60, 35) if hover else (20, 35, 20)
            pygame.draw.rect(surf, bg, r, border_radius=6)
            if hover:
                pygame.draw.rect(surf, C_GREEN, r, 1, border_radius=6)
            draw_text(surf, f"{entry.emoji}  {entry.name}  —  {entry.title}",
                      (r.x + 14, r.y + 10), fonts["md"], C_WHITE if hover else C_DIM)
            all_entries.append(entry)
            entry_rects.append(r)
            y += 48

    draw_status_bar(surf, fonts, game_state.player)
    return {"entries": entry_rects, "back": back_btn, "entry_data": all_entries}


# ── Full screen: Skills ───────────────────────────────────────────────────────

def draw_skills(surf, fonts, game_state, hover_row: int = -1) -> dict:
    """Draw skills upgrade screen. Returns {'btns': [Rect,...], 'back': Rect}."""
    from models import UPGRADE_COSTS
    surf.fill(C_BG)
    draw_text(surf, loc.t("skills.header"), (W // 2, 16), fonts["lg"], C_YELLOW, align="center")

    back_btn = Rect(10, 10, 120, 40)
    draw_button(surf, back_btn, loc.t("obj.back_to_map"), fonts["sm"])

    player = game_state.player
    draw_text(surf, loc.t("skills.knowledge_label", knowledge=player.knowledge),
              (W // 2, 58), fonts["md"], C_BLUE, align="center")

    # Per-level unlock descriptions shown in the skill row
    _UNLOCKS = {
        "explorer":        ["skills.explorer_unlock_1", "skills.explorer_unlock_2", "skills.explorer_unlock_3"],
        "nature_friend":   ["skills.nature_unlock_1",   "skills.nature_unlock_2",   "skills.nature_unlock_3"],
        "survival_helper": ["skills.survival_unlock_1", "skills.survival_unlock_2", "skills.survival_unlock_3"],
    }

    skill_display = [
        ("explorer",        loc.t("skills.explorer_name"), loc.t("skills.explorer_desc")),
        ("nature_friend",   loc.t("skills.nature_name"),   loc.t("skills.nature_desc")),
        ("survival_helper", loc.t("skills.survival_name"), loc.t("skills.survival_desc")),
    ]

    btns = []
    for i, (skill_id, name, desc) in enumerate(skill_display):
        skill   = player.skills[skill_id]
        row_r   = Rect(60, 100 + i * 155, W - 120, 135)
        bg      = (35, 55, 35) if i == hover_row else (20, 35, 20)
        pygame.draw.rect(surf, bg, row_r, border_radius=10)
        pygame.draw.rect(surf, C_YELLOW if i == hover_row else C_GREEN_DARK, row_r, 2, border_radius=10)

        # Stars (filled = unlocked, dim = locked)
        stars_x = row_r.x + 20
        for s in range(3):
            col = C_GOLD if s < skill.level else (50, 50, 50)
            pygame.draw.circle(surf, col, (stars_x + s * 28, row_r.y + 28), 10)
            pygame.draw.circle(surf, (200, 180, 60) if s < skill.level else (80, 80, 80),
                               (stars_x + s * 28, row_r.y + 28), 10, 2)

        # Name
        draw_text(surf, name, (row_r.x + 110, row_r.y + 12), fonts["lg"], C_WHITE)

        # Per-level unlock hints (3 in a row, coloured by whether already unlocked)
        unlock_keys = _UNLOCKS[skill_id]
        ux = row_r.x + 110
        for lvl_idx, ukey in enumerate(unlock_keys):
            unlocked = skill.level > lvl_idx
            col = C_GREEN if unlocked else C_DIM
            draw_text(surf, loc.t(ukey), (ux, row_r.y + 56 + lvl_idx * 22), fonts["sm"], col)

        draw_text(surf, loc.t("skills.level_label", level=skill.level),
                  (row_r.x + 110, row_r.y + 110), fonts["sm"], C_DIM)

        # Upgrade button
        if skill.level >= 3:
            cost_text = loc.t("skills.max_level")
            locked = True
            cost_col = C_DIM
        else:
            cost = UPGRADE_COSTS.get(skill.level + 1, 0)
            has_enough = player.knowledge >= cost
            cost_text = loc.t("skills.upgrade_cost", cost=cost)
            locked = not has_enough
            cost_col = C_GREEN if has_enough else C_RED

        btn_r = Rect(row_r.right - 220, row_r.y + 42, 200, 50)
        draw_button(surf, btn_r, cost_text, fonts["md"],
                    hover=(i == hover_row and not locked), locked=locked)
        btns.append(btn_r)

    draw_status_bar(surf, fonts, player)
    return {"btns": btns, "back": back_btn}


# ── Helpers for scene object retrieval (used by main.py) ─────────────────────

def get_object_rects(tile_type: str) -> list:
    """Return the list of hotspot Rects for a tile_type."""
    return _OBJECT_RECTS.get(tile_type, [])
