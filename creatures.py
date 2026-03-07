# -*- coding: utf-8 -*-
"""
creatures.py — pygame drawing functions for every discoverable creature/plant.

draw_creature(surf, creature_id, cx, cy, size) dispatches to a per-species
function.  All drawings are self-contained pygame.draw calls — no image files.
"""

import math
import pygame
from pygame import Rect


def draw_creature(surf, creature_id: str, cx: int, cy: int, size: int = 90) -> None:
    """Draw a creature centred at (cx, cy) scaled to `size` pixels."""
    _DISPATCH = {
        # Animals
        "morpho_butterfly":  _butterfly,
        "blue_morpho_beetle":_blue_beetle,
        "toucan":            _toucan,
        "macaw":             _macaw,
        "jaguar":            _jaguar,
        "anaconda":          _anaconda,
        "pink_dolphin":      _pink_dolphin,
        "poison_dart_frog":  _dart_frog,
        "capybara":          _capybara,
        "sloth":             _sloth,
        "howler_monkey":     _monkey,
        "giant_otter":       _otter,
        "harpy_eagle":       _eagle,
        "piranha":           _piranha,
        "pygmy_owl":         _owl,
        "amazon_tree_frog":  _tree_frog,
        "ornamental_fish":   _tetra_fish,
        "river_crab":        _crab,
        "flower_beetle":     _flower_beetle,
        "forest_mouse":      _mouse,
        "orchid_bee":        _orchid_bee,
        "green_parrot":      _parrot,
        "tapir":             _tapir,
        # Plants
        "giant_water_lily":  _water_lily,
        "heliconia":         _heliconia,
        "orchid":            _orchid,
        "bromeliad":         _bromeliad,
        "rubber_tree":       _rubber_tree,
        "kapok_tree":        _kapok_tree,
        "cacao":             _cacao,
        "passion_flower":    _passion_flower,
        "banana_plant":      _banana_plant,
        "amazon_lily":       _amazon_lily,
        "strangler_fig":     _strangler_fig,
        "brazil_nut":        _brazil_nut_plant,
        "cashew_nut":        _cashew_plant,
    }
    fn = _DISPATCH.get(creature_id, _generic)
    fn(surf, cx, cy, size)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _s(size, frac):
    return max(1, int(size * frac))


def _wing(surf, cx, cy, dx, dy, w, h, color, alpha=200):
    s = pygame.Surface((w * 2, h * 2), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (*color, alpha), (0, 0, w * 2, h * 2))
    surf.blit(s, (cx + dx - w, cy + dy - h))


# ── Animals ───────────────────────────────────────────────────────────────────

def _butterfly(surf, cx, cy, size):
    """Blue morpho butterfly — large iridescent blue wings."""
    s = _s(size, 0.42)
    # Upper wings (larger, slightly tilted)
    for dx, sign in [(-s, -1), (s, 1)]:
        pts_upper = [
            (cx, cy),
            (cx + sign * s * 2, cy - s),
            (cx + sign * int(s * 1.7), cy + s // 2),
        ]
        pygame.draw.polygon(surf, (30, 80, 220), pts_upper)
        pygame.draw.polygon(surf, (60, 140, 255), pts_upper, 2)
        # Iridescent highlight
        h_pts = [
            (cx + sign * _s(size, 0.2), cy - _s(size, 0.1)),
            (cx + sign * _s(size, 0.6), cy - _s(size, 0.25)),
            (cx + sign * _s(size, 0.5), cy + _s(size, 0.05)),
        ]
        pygame.draw.polygon(surf, (120, 200, 255, 160), h_pts)
    # Lower wings (smaller)
    for sign in [-1, 1]:
        lo_pts = [
            (cx, cy),
            (cx + sign * int(s * 1.4), cy + s),
            (cx + sign * int(s * 0.6), cy + int(s * 1.5)),
        ]
        pygame.draw.polygon(surf, (20, 60, 180), lo_pts)
    # Body
    pygame.draw.ellipse(surf, (30, 20, 10), Rect(cx - 3, cy - s, 6, s * 2))
    # Antennae
    pygame.draw.line(surf, (80, 60, 20), (cx, cy - s), (cx - _s(size, 0.4), cy - s - _s(size, 0.35)), 1)
    pygame.draw.line(surf, (80, 60, 20), (cx, cy - s), (cx + _s(size, 0.4), cy - s - _s(size, 0.35)), 1)
    pygame.draw.circle(surf, (80, 60, 20), (cx - _s(size, 0.4), cy - s - _s(size, 0.35)), 2)
    pygame.draw.circle(surf, (80, 60, 20), (cx + _s(size, 0.4), cy - s - _s(size, 0.35)), 2)


def _blue_beetle(surf, cx, cy, size):
    """Blue morpho beetle — metallic blue oval with iridescent sheen."""
    rx, ry = _s(size, 0.32), _s(size, 0.46)
    pygame.draw.ellipse(surf, (20, 60, 180), Rect(cx - rx, cy - ry, rx * 2, ry * 2))
    pygame.draw.ellipse(surf, (80, 160, 255), Rect(cx - rx // 2, cy - ry + 4, rx, ry // 2))
    pygame.draw.ellipse(surf, (60, 120, 240), Rect(cx - rx, cy - ry, rx * 2, ry * 2), 2)
    # Wing seam
    pygame.draw.line(surf, (40, 80, 200), (cx, cy - ry + 2), (cx, cy + ry - 2), 1)
    # Legs
    for i, (bx, by, ex, ey) in enumerate([
        (cx - rx, cy - ry // 3, cx - rx - _s(size, 0.18), cy - ry // 2 - 4),
        (cx - rx, cy,           cx - rx - _s(size, 0.22), cy + 2),
        (cx - rx, cy + ry // 3, cx - rx - _s(size, 0.18), cy + ry // 2 + 4),
        (cx + rx, cy - ry // 3, cx + rx + _s(size, 0.18), cy - ry // 2 - 4),
        (cx + rx, cy,           cx + rx + _s(size, 0.22), cy + 2),
        (cx + rx, cy + ry // 3, cx + rx + _s(size, 0.18), cy + ry // 2 + 4),
    ]):
        pygame.draw.line(surf, (30, 20, 10), (bx, by), (ex, ey), 1)
    # Antennae
    pygame.draw.line(surf, (30, 20, 10), (cx - 3, cy - ry), (cx - _s(size, 0.28), cy - ry - _s(size, 0.28)), 1)
    pygame.draw.line(surf, (30, 20, 10), (cx + 3, cy - ry), (cx + _s(size, 0.28), cy - ry - _s(size, 0.28)), 1)


def _toucan(surf, cx, cy, size):
    """Toucan — black body, massive colorful beak."""
    r = _s(size, 0.28)
    # Body
    pygame.draw.ellipse(surf, (20, 20, 20), Rect(cx - r, cy - r // 2, r * 2, int(r * 1.6)))
    # White chest patch
    pygame.draw.ellipse(surf, (240, 240, 220), Rect(cx - r // 2, cy - r // 3, r, r))
    # Head
    pygame.draw.circle(surf, (20, 20, 20), (cx, cy - r), r)
    # Eye
    pygame.draw.circle(surf, (50, 180, 50), (cx + r // 3, cy - r - 2), _s(size, 0.07))
    pygame.draw.circle(surf, (10, 10, 10), (cx + r // 3 + 1, cy - r - 1), _s(size, 0.04))
    # Big beak (yellow + orange + red gradient bands)
    beak_len = _s(size, 0.52)
    beak_h   = _s(size, 0.22)
    bx = cx + r
    pygame.draw.polygon(surf, (240, 200, 20), [
        (bx, cy - r + 4), (bx + beak_len, cy - r + beak_h // 2),
        (bx + beak_len - 4, cy - r + beak_h), (bx, cy - r + beak_h // 2),
    ])
    # Beak tip stripe
    pygame.draw.polygon(surf, (210, 80, 20), [
        (bx + beak_len - _s(size, 0.14), cy - r + 4),
        (bx + beak_len, cy - r + beak_h // 2),
        (bx + beak_len - 4, cy - r + beak_h),
        (bx + beak_len - _s(size, 0.14), cy - r + beak_h - 2),
    ])
    # Tail feathers
    pygame.draw.polygon(surf, (20, 80, 20), [
        (cx - r, cy + r // 2), (cx - r - _s(size, 0.18), cy + r + _s(size, 0.18)),
        (cx - r // 2, cy + r),
    ])


def _macaw(surf, cx, cy, size):
    """Blue-and-yellow macaw — colourful body, long tail."""
    r = _s(size, 0.22)
    # Tail (long and pointed)
    pygame.draw.polygon(surf, (20, 100, 200), [
        (cx, cy + r), (cx - _s(size, 0.08), cy + r + _s(size, 0.55)),
        (cx + _s(size, 0.08), cy + r + _s(size, 0.5)),
    ])
    # Body — blue back + yellow belly
    pygame.draw.ellipse(surf, (30, 120, 220), Rect(cx - r, cy - r // 2, r * 2, int(r * 1.6)))
    pygame.draw.ellipse(surf, (220, 200, 30), Rect(cx - r // 2, cy, r, int(r * 1.2)))
    # Wing
    wing_pts = [(cx - r, cy), (cx - r - _s(size, 0.2), cy - _s(size, 0.1)),
                (cx - r - _s(size, 0.15), cy + r)]
    pygame.draw.polygon(surf, (20, 100, 200), wing_pts)
    # Head
    pygame.draw.circle(surf, (30, 120, 220), (cx, cy - r), r)
    # Cheek patch (white with lines)
    pygame.draw.ellipse(surf, (240, 235, 220), Rect(cx - r // 4, cy - r + r // 3, r // 2 + 4, r // 3))
    # Eye + hook beak
    pygame.draw.circle(surf, (10, 10, 10), (cx + r // 3, cy - r), _s(size, 0.055))
    pygame.draw.arc(surf, (80, 60, 20),
                    Rect(cx + r // 2, cy - r - 4, _s(size, 0.16), _s(size, 0.14)),
                    math.pi * 1.2, math.pi * 2, 3)


def _jaguar(surf, cx, cy, size):
    """Jaguar — tawny cat body with black rosette spots."""
    r = _s(size, 0.3)
    # Body
    pygame.draw.ellipse(surf, (200, 140, 30), Rect(cx - int(r * 1.3), cy - r // 2, int(r * 2.6), int(r * 1.4)))
    # Head
    pygame.draw.circle(surf, (200, 140, 30), (cx + int(r * 1.1), cy - r // 3), int(r * 0.72))
    # Ears
    hx = cx + int(r * 1.1)
    for ex in [hx - r // 2, hx + r // 2]:
        pygame.draw.polygon(surf, (200, 140, 30), [
            (ex - 5, cy - r // 3 - int(r * 0.6)),
            (ex, cy - r // 3 - int(r * 0.75)),
            (ex + 5, cy - r // 3 - int(r * 0.6)),
        ])
    # Eyes (green)
    pygame.draw.circle(surf, (80, 200, 60), (hx + r // 4, cy - r // 3), _s(size, 0.065))
    pygame.draw.circle(surf, (80, 200, 60), (hx - r // 4, cy - r // 3), _s(size, 0.065))
    pygame.draw.circle(surf, (10, 10, 10), (hx + r // 4, cy - r // 3), _s(size, 0.033))
    pygame.draw.circle(surf, (10, 10, 10), (hx - r // 4, cy - r // 3), _s(size, 0.033))
    # Spots (black rosettes)
    for sx, sy in [(-int(r * 0.7), -4), (0, 0), (-int(r * 0.35), int(r * 0.35)), (-r, int(r * 0.3))]:
        pygame.draw.circle(surf, (40, 25, 5), (cx + sx, cy + sy), _s(size, 0.08))
        pygame.draw.circle(surf, (200, 140, 30), (cx + sx, cy + sy), _s(size, 0.044))
    # Tail
    pygame.draw.arc(surf, (180, 120, 20),
                    Rect(cx - int(r * 1.6), cy - r // 2, int(r * 0.7), int(r * 1.5)),
                    math.pi * 0.9, math.pi * 1.9, 4)
    # Legs (4 stubs)
    for lx in [cx - r, cx - r // 2, cx + r // 3, cx + int(r * 0.8)]:
        pygame.draw.rect(surf, (180, 120, 20), Rect(lx - 5, cy + r // 2, 10, _s(size, 0.22)))


def _anaconda(surf, cx, cy, size):
    """Anaconda — thick coiled green snake with pattern."""
    r = _s(size, 0.38)
    # Coils (multiple arcs)
    for offset, rad_mod, col in [
        (0,       r,        (40, 100, 40)),
        (6,       r - 8,    (60, 140, 30)),
        (-4,      r - 14,   (40, 100, 40)),
    ]:
        pygame.draw.arc(surf, col,
                        Rect(cx - rad_mod + offset, cy - rad_mod // 2,
                             rad_mod * 2, rad_mod),
                        0, math.pi, _s(size, 0.1))
    # Head
    hx, hy = cx + r - 8, cy - _s(size, 0.12)
    pygame.draw.ellipse(surf, (40, 110, 30), Rect(hx - _s(size, 0.12), hy - _s(size, 0.09),
                                                   _s(size, 0.24), _s(size, 0.18)))
    # Eyes
    pygame.draw.circle(surf, (200, 180, 20), (hx + _s(size, 0.04), hy - 1), 3)
    pygame.draw.circle(surf, (10, 10, 10),   (hx + _s(size, 0.04), hy - 1), 2)
    # Tongue
    tx = hx + _s(size, 0.1)
    pygame.draw.line(surf, (220, 30, 30), (tx, hy + 2), (tx + _s(size, 0.1), hy + 4), 1)
    pygame.draw.line(surf, (220, 30, 30), (tx + _s(size, 0.08), hy + 3), (tx + _s(size, 0.1), hy + 1), 1)


def _pink_dolphin(surf, cx, cy, size):
    """Amazon pink river dolphin."""
    r = _s(size, 0.35)
    # Body
    pygame.draw.ellipse(surf, (240, 160, 180), Rect(cx - r, cy - r // 3, r * 2, int(r * 0.8)))
    # Snout (long)
    pygame.draw.polygon(surf, (230, 145, 165), [
        (cx + r, cy - r // 6), (cx + r + _s(size, 0.32), cy + 1),
        (cx + r, cy + r // 4),
    ])
    # Dorsal fin
    pygame.draw.polygon(surf, (210, 130, 150), [
        (cx, cy - r // 3), (cx + r // 3, cy - r // 3 - _s(size, 0.2)),
        (cx + int(r * 0.6), cy - r // 3),
    ])
    # Tail fluke
    pygame.draw.polygon(surf, (210, 130, 150), [
        (cx - r, cy), (cx - r - _s(size, 0.2), cy - r // 3),
        (cx - r - _s(size, 0.18), cy + r // 3),
    ])
    # Eye (small, dark)
    pygame.draw.circle(surf, (60, 30, 40), (cx + int(r * 0.6), cy - r // 6 - 2), 3)
    pygame.draw.circle(surf, (230, 200, 210), (cx + int(r * 0.6) + 1, cy - r // 6 - 3), 1)


def _dart_frog(surf, cx, cy, size):
    """Poison dart frog — tiny, vivid blue/red with spots."""
    r = _s(size, 0.28)
    # Body
    pygame.draw.ellipse(surf, (30, 90, 210), Rect(cx - r, cy - r // 2, r * 2, int(r * 1.3)))
    # Black spots
    for sx, sy in [(-r // 3, -r // 4), (r // 3, r // 4), (0, r // 2), (-r // 2, r // 2)]:
        pygame.draw.circle(surf, (10, 10, 60), (cx + sx, cy + sy), _s(size, 0.065))
    # Head
    pygame.draw.circle(surf, (30, 90, 210), (cx, cy - r // 2), int(r * 0.72))
    # Big buggy eyes
    for ex in [-r // 3, r // 3]:
        pygame.draw.circle(surf, (220, 200, 20), (cx + ex, cy - r // 2 - r // 3), _s(size, 0.1))
        pygame.draw.circle(surf, (10, 10, 10),   (cx + ex, cy - r // 2 - r // 3), _s(size, 0.05))
    # Red stripe down back
    pygame.draw.line(surf, (220, 30, 30), (cx, cy - r // 2), (cx, cy + r // 2), 3)
    # Legs
    for side in [-1, 1]:
        pygame.draw.line(surf, (20, 70, 180),
                         (cx + side * r, cy + r // 2),
                         (cx + side * int(r * 1.5), cy + r + _s(size, 0.1)), 3)
        pygame.draw.line(surf, (20, 70, 180),
                         (cx + side * r, cy - r // 4),
                         (cx + side * int(r * 1.4), cy - r // 2), 2)


def _capybara(surf, cx, cy, size):
    """Capybara — big round brown rodent."""
    r = _s(size, 0.3)
    # Body (large barrel-shape)
    pygame.draw.ellipse(surf, (130, 90, 50), Rect(cx - int(r * 1.5), cy - r // 2, int(r * 3), int(r * 1.4)))
    # Head
    hx = cx + int(r * 1.2)
    pygame.draw.ellipse(surf, (130, 90, 50),
                        Rect(hx - int(r * 0.7), cy - r, int(r * 1.4), r + r // 3))
    # Nostrils
    pygame.draw.circle(surf, (90, 60, 30), (hx + int(r * 0.5), cy - r // 2), 3)
    pygame.draw.circle(surf, (90, 60, 30), (hx + int(r * 0.5) + 6, cy - r // 2), 3)
    # Eye
    pygame.draw.circle(surf, (40, 25, 10), (hx + r // 4, cy - r + r // 4), _s(size, 0.065))
    pygame.draw.circle(surf, (200, 180, 150), (hx + r // 4 + 1, cy - r + r // 4 - 1), 2)
    # Legs
    for lx in [cx - r, cx - r // 3, cx + r // 3, cx + r]:
        pygame.draw.rect(surf, (110, 75, 40), Rect(lx - 5, cy + r // 2, 10, _s(size, 0.24)))
        pygame.draw.ellipse(surf, (90, 60, 30), Rect(lx - 7, cy + r // 2 + _s(size, 0.2), 14, 8))


def _sloth(surf, cx, cy, size):
    """Three-toed sloth hanging upside-down from branch."""
    r = _s(size, 0.24)
    # Branch
    pygame.draw.rect(surf, (100, 65, 25),
                     Rect(cx - int(r * 1.8), cy - int(r * 1.6), int(r * 3.6), _s(size, 0.08)))
    # Arms reaching up to branch
    for arm_x in [-r // 2, r // 2]:
        pygame.draw.line(surf, (160, 120, 70),
                         (cx + arm_x, cy - r),
                         (cx + arm_x, cy - int(r * 1.55)), 5)
        # Claws
        pygame.draw.arc(surf, (80, 60, 30),
                        Rect(cx + arm_x - 6, cy - int(r * 1.6) - 4, 12, 8),
                        0, math.pi, 2)
    # Body
    pygame.draw.ellipse(surf, (160, 140, 90), Rect(cx - r, cy - r, r * 2, r * 2))
    # Face mask (darker)
    pygame.draw.ellipse(surf, (110, 90, 60), Rect(cx - r // 2, cy - r // 2, r, int(r * 0.9)))
    # Sleepy eyes (closed)
    for ex in [-r // 4, r // 4]:
        pygame.draw.arc(surf, (40, 30, 20),
                        Rect(cx + ex - 5, cy - r // 4 - 2, 10, 6),
                        0, math.pi, 2)
    # Smile
    pygame.draw.arc(surf, (100, 70, 40),
                    Rect(cx - r // 4, cy, r // 2, r // 4),
                    math.pi, 2 * math.pi, 2)
    # Algae (green tint streaks on fur)
    for ax in [-r // 3, 0, r // 3]:
        pygame.draw.line(surf, (100, 140, 60), (cx + ax, cy - r // 3), (cx + ax, cy + r // 3), 1)


def _monkey(surf, cx, cy, size):
    """Howler monkey — dark brown with open mouth howl."""
    r = _s(size, 0.25)
    # Body
    pygame.draw.ellipse(surf, (80, 50, 20), Rect(cx - r, cy - r // 2, r * 2, int(r * 1.5)))
    # Prehensile tail curling up
    pygame.draw.arc(surf, (80, 50, 20),
                    Rect(cx - int(r * 1.3), cy - r,
                         int(r * 1.1), int(r * 1.6)),
                    math.pi * 1.2, math.pi * 2.1, 4)
    # Head
    pygame.draw.circle(surf, (80, 50, 20), (cx, cy - r), int(r * 0.9))
    # Beard / throat sac (yellow-brown)
    pygame.draw.ellipse(surf, (160, 120, 50),
                        Rect(cx - r // 2, cy - r // 2, r, int(r * 0.7)))
    # Eyes
    for ex in [-r // 3, r // 3]:
        pygame.draw.circle(surf, (200, 160, 60), (cx + ex, cy - r), _s(size, 0.075))
        pygame.draw.circle(surf, (10, 10, 10),   (cx + ex, cy - r), _s(size, 0.038))
    # Open mouth (howling)
    pygame.draw.arc(surf, (10, 10, 10),
                    Rect(cx - r // 3, cy - r // 2, int(r * 0.66), r // 2),
                    math.pi, 2 * math.pi, 0)
    pygame.draw.ellipse(surf, (180, 60, 60), Rect(cx - r // 4, cy - r // 2 + 2, r // 2, r // 3))


def _otter(surf, cx, cy, size):
    """Giant river otter — long sleek brown body."""
    r = _s(size, 0.2)
    # Streamlined body
    pygame.draw.ellipse(surf, (100, 65, 30), Rect(cx - int(r * 1.8), cy - r // 2, int(r * 3.6), int(r * 1.2)))
    # Chest patch (lighter)
    pygame.draw.ellipse(surf, (190, 160, 110), Rect(cx - r // 2, cy - r // 3, r, int(r * 0.8)))
    # Head
    hx = cx + int(r * 1.6)
    pygame.draw.circle(surf, (100, 65, 30), (hx, cy), int(r * 0.8))
    # Nose (big flat)
    pygame.draw.ellipse(surf, (50, 30, 15), Rect(hx + r // 4, cy - r // 4, r // 2, r // 3))
    # Whiskers
    for wy in [-2, 2]:
        pygame.draw.line(surf, (220, 200, 160), (hx + r // 2, cy + wy), (hx + r, cy + wy), 1)
    # Eyes
    pygame.draw.circle(surf, (40, 25, 10), (hx, cy - r // 3), _s(size, 0.065))
    pygame.draw.circle(surf, (220, 200, 160), (hx + 1, cy - r // 3 - 1), 2)
    # Tail (flat and broad)
    pygame.draw.ellipse(surf, (80, 50, 20),
                        Rect(cx - int(r * 1.9), cy - r // 4, int(r * 0.7), int(r * 0.8)))
    # Webbed feet
    for fx in [cx - r, cx, cx + r]:
        pygame.draw.ellipse(surf, (70, 45, 15), Rect(fx - 6, cy + r // 2, 12, 7))


def _eagle(surf, cx, cy, size):
    """Harpy eagle — large raptor with crest."""
    r = _s(size, 0.28)
    # Body
    pygame.draw.ellipse(surf, (200, 195, 185), Rect(cx - r, cy - r // 2, r * 2, int(r * 1.5)))
    # Dark back
    pygame.draw.ellipse(surf, (50, 45, 40), Rect(cx - r, cy - r // 2, r * 2, r))
    # Spread wings
    for side in [-1, 1]:
        wing_pts = [
            (cx, cy), (cx + side * int(r * 1.8), cy - r // 2),
            (cx + side * int(r * 1.5), cy + r // 2),
        ]
        pygame.draw.polygon(surf, (60, 55, 50), wing_pts)
        # Wing bar
        mid = [(cx + side * r, cy - r // 4), (cx + side * int(r * 1.6), cy - r // 3)]
        pygame.draw.line(surf, (200, 195, 185), mid[0], mid[1], 2)
    # Head
    pygame.draw.circle(surf, (200, 195, 185), (cx, cy - r), int(r * 0.8))
    # Crest feathers (dark)
    for i in range(5):
        angle = math.pi + (i - 2) * 0.22
        fx = cx + int(math.cos(angle) * r * 0.85)
        fy = (cy - r) + int(math.sin(angle) * r * 0.85)
        pygame.draw.line(surf, (40, 35, 30), (cx, cy - r), (fx, fy), 2)
    # Eye ring + hooked beak
    pygame.draw.circle(surf, (220, 180, 30), (cx + r // 3, cy - r), _s(size, 0.1))
    pygame.draw.circle(surf, (10, 10, 10), (cx + r // 3, cy - r), _s(size, 0.055))
    pygame.draw.arc(surf, (200, 160, 20),
                    Rect(cx + r // 2, cy - r - 3, _s(size, 0.16), _s(size, 0.14)),
                    math.pi * 1.3, math.pi * 2, 4)


def _piranha(surf, cx, cy, size):
    """Red-bellied piranha — silver body, red belly, big teeth."""
    r = _s(size, 0.3)
    # Body (streamlined oval)
    pygame.draw.ellipse(surf, (180, 180, 160), Rect(cx - r, cy - r // 2, r * 2, r))
    # Red belly
    pygame.draw.ellipse(surf, (220, 60, 40), Rect(cx - r + 4, cy, r * 2 - 8, r // 2 - 2))
    # Tail fin
    pygame.draw.polygon(surf, (160, 160, 140), [
        (cx - r, cy), (cx - r - _s(size, 0.22), cy - r // 3),
        (cx - r - _s(size, 0.22), cy + r // 3),
    ])
    # Dorsal fin
    pygame.draw.polygon(surf, (150, 150, 130), [
        (cx - r // 3, cy - r // 2), (cx, cy - r // 2 - _s(size, 0.2)),
        (cx + r // 3, cy - r // 2),
    ])
    # Big jaw (jutting)
    pygame.draw.ellipse(surf, (190, 170, 150), Rect(cx + r // 2, cy - r // 4, r // 2 + 4, r // 2))
    # Teeth (white triangles)
    for tx in range(cx + int(r * 0.6), cx + r + 4, 5):
        pygame.draw.polygon(surf, (240, 240, 230), [(tx, cy), (tx + 2, cy - 5), (tx + 4, cy)])
        pygame.draw.polygon(surf, (240, 240, 230), [(tx, cy + r // 4), (tx + 2, cy + r // 4 + 5), (tx + 4, cy + r // 4)])
    # Eye + pupil
    pygame.draw.circle(surf, (220, 60, 30), (cx + int(r * 0.55), cy - r // 4 + 2), _s(size, 0.085))
    pygame.draw.circle(surf, (10, 10, 10), (cx + int(r * 0.55), cy - r // 4 + 2), _s(size, 0.042))


def _owl(surf, cx, cy, size):
    """Pygmy owl — tiny round owl with big yellow eyes."""
    r = _s(size, 0.28)
    # Body (dumpy round)
    pygame.draw.ellipse(surf, (130, 100, 60), Rect(cx - r, cy - r // 3, r * 2, int(r * 1.6)))
    # Wing texture (streaks)
    for i in range(-2, 3):
        pygame.draw.line(surf, (90, 65, 30),
                         (cx + i * r // 3, cy - r // 3),
                         (cx + i * r // 3 - 2, cy + r), 1)
    # Head (big round)
    pygame.draw.circle(surf, (130, 100, 60), (cx, cy - r // 3), r)
    # Facial disc
    pygame.draw.circle(surf, (180, 150, 100), (cx, cy - r // 3), int(r * 0.72))
    # Big eyes
    for ex in [-r // 3, r // 3]:
        pygame.draw.circle(surf, (240, 200, 30), (cx + ex, cy - r // 3), _s(size, 0.12))
        pygame.draw.circle(surf, (10, 10, 10),   (cx + ex, cy - r // 3), _s(size, 0.065))
        pygame.draw.circle(surf, (255, 255, 255), (cx + ex + 2, cy - r // 3 - 2), 2)
    # Beak (tiny hooked)
    pygame.draw.polygon(surf, (200, 160, 20), [
        (cx - 3, cy - r // 3 + r // 6),
        (cx, cy - r // 3 + r // 3),
        (cx + 3, cy - r // 3 + r // 6),
    ])
    # Ear tufts (tiny)
    for ex in [-r // 4, r // 4]:
        pygame.draw.polygon(surf, (110, 80, 40), [
            (cx + ex - 3, cy - r // 3 - r // 2),
            (cx + ex, cy - r // 3 - r),
            (cx + ex + 3, cy - r // 3 - r // 2),
        ])
    # Feet (talons)
    for fx in [-r // 3, r // 3]:
        pygame.draw.line(surf, (180, 140, 60),
                         (cx + fx, cy + int(r * 1.2)), (cx + fx, cy + int(r * 1.5)), 3)
        for toe in [-4, 0, 4]:
            pygame.draw.line(surf, (160, 120, 40),
                             (cx + fx, cy + int(r * 1.5)),
                             (cx + fx + toe, cy + int(r * 1.7)), 2)


def _tree_frog(surf, cx, cy, size):
    """Amazon tree frog — bright green with sticky toe pads."""
    r = _s(size, 0.28)
    # Body
    pygame.draw.ellipse(surf, (80, 200, 80), Rect(cx - r, cy - r // 2, r * 2, int(r * 1.2)))
    # Lighter belly
    pygame.draw.ellipse(surf, (180, 240, 160), Rect(cx - r // 2, cy, r, int(r * 0.7)))
    # Head
    pygame.draw.circle(surf, (80, 200, 80), (cx, cy - r // 2), int(r * 0.8))
    # Giant eyes (gold with vertical pupil)
    for ex in [-r // 3, r // 3]:
        pygame.draw.circle(surf, (220, 180, 30), (cx + ex, cy - r // 2 - r // 4), _s(size, 0.13))
        pygame.draw.ellipse(surf, (10, 10, 10),
                            Rect(cx + ex - 2, cy - r // 2 - r // 4 - _s(size, 0.07),
                                 4, _s(size, 0.14)))
        pygame.draw.circle(surf, (255, 255, 255), (cx + ex + 2, cy - r // 2 - r // 4 - 2), 2)
    # Front legs with toe pads
    for side in [-1, 1]:
        pygame.draw.line(surf, (60, 170, 60),
                         (cx + side * r, cy),
                         (cx + side * int(r * 1.5), cy - r // 3), 4)
        pygame.draw.circle(surf, (50, 160, 50), (cx + side * int(r * 1.5), cy - r // 3), 5)
    # Back legs with toe pads
    for side in [-1, 1]:
        pygame.draw.line(surf, (60, 170, 60),
                         (cx + side * int(r * 0.6), cy + r // 2),
                         (cx + side * int(r * 1.4), cy + r), 4)
        pygame.draw.circle(surf, (50, 160, 50), (cx + side * int(r * 1.4), cy + r), 5)


def _tetra_fish(surf, cx, cy, size):
    """Neon tetra — tiny fish with electric blue stripe."""
    r = _s(size, 0.28)
    # Body
    pygame.draw.ellipse(surf, (200, 200, 180), Rect(cx - r, cy - r // 3, r * 2, int(r * 0.8)))
    # Iridescent blue stripe
    pygame.draw.rect(surf, (20, 160, 240),
                     Rect(cx - r + 4, cy - r // 6, r * 2 - 8, _s(size, 0.07)))
    # Red stripe below
    pygame.draw.rect(surf, (220, 60, 40),
                     Rect(cx - r // 2, cy + r // 6, r, _s(size, 0.065)))
    # Tail fin
    pygame.draw.polygon(surf, (180, 180, 160), [
        (cx - r, cy), (cx - r - _s(size, 0.18), cy - r // 3),
        (cx - r - _s(size, 0.18), cy + r // 3),
    ])
    # Dorsal + anal fins
    pygame.draw.polygon(surf, (190, 185, 170), [
        (cx, cy - r // 3), (cx - r // 4, cy - r // 3 - _s(size, 0.12)), (cx + r // 4, cy - r // 3),
    ])
    # Eye
    pygame.draw.circle(surf, (10, 10, 10), (cx + int(r * 0.62), cy - r // 12), _s(size, 0.065))
    pygame.draw.circle(surf, (240, 240, 240), (cx + int(r * 0.62) + 1, cy - r // 12 - 1), 2)


def _crab(surf, cx, cy, size):
    """River crab — orange-red with big claws."""
    r = _s(size, 0.26)
    # Carapace (oval shell)
    pygame.draw.ellipse(surf, (220, 100, 30), Rect(cx - r, cy - r // 2, r * 2, r))
    pygame.draw.ellipse(surf, (240, 140, 50), Rect(cx - r + 4, cy - r // 2 + 3, r * 2 - 8, r // 2))
    # Big claws
    for side in [-1, 1]:
        clx = cx + side * int(r * 1.1)
        cly = cy - r // 4
        pygame.draw.ellipse(surf, (200, 80, 20), Rect(clx - r // 2 - 4, cly - r // 2, r + 8, r // 2 + 4))
        # Claw gap
        pygame.draw.line(surf, (160, 60, 10), (clx + side * r // 4, cly - 2),
                         (clx + side * r // 2, cly + r // 4), 2)
    # Walking legs (3 pairs)
    for i in range(1, 4):
        for side in [-1, 1]:
            lx = cx + side * int(r * 0.3 * i)
            pygame.draw.line(surf, (180, 70, 20), (cx + side * r, cy),
                             (lx + side * _s(size, 0.2), cy + r // 2 + 4), 3)
    # Eyes on stalks
    for ex in [-r // 3, r // 3]:
        pygame.draw.line(surf, (180, 70, 20), (cx + ex, cy - r // 2), (cx + ex, cy - r // 2 - _s(size, 0.14)), 2)
        pygame.draw.circle(surf, (10, 10, 10), (cx + ex, cy - r // 2 - _s(size, 0.14)), _s(size, 0.06))


def _flower_beetle(surf, cx, cy, size):
    """Flower beetle — rounded green/gold iridescent shell."""
    rx, ry = _s(size, 0.3), _s(size, 0.38)
    pygame.draw.ellipse(surf, (40, 130, 40), Rect(cx - rx, cy - ry, rx * 2, ry * 2))
    pygame.draw.ellipse(surf, (180, 170, 20), Rect(cx - rx + 4, cy - ry + 4, rx * 2 - 8, ry // 2))
    pygame.draw.ellipse(surf, (60, 160, 60), Rect(cx - rx, cy - ry, rx * 2, ry * 2), 2)
    pygame.draw.line(surf, (30, 110, 30), (cx, cy - ry + 2), (cx, cy + ry - 2), 1)
    # Legs
    for bx, by, ex, ey in [
        (cx - rx, cy - ry // 3, cx - rx - _s(size, 0.2), cy - ry // 2),
        (cx - rx, cy, cx - rx - _s(size, 0.22), cy + 2),
        (cx - rx, cy + ry // 3, cx - rx - _s(size, 0.18), cy + ry // 2),
        (cx + rx, cy - ry // 3, cx + rx + _s(size, 0.2), cy - ry // 2),
        (cx + rx, cy, cx + rx + _s(size, 0.22), cy + 2),
        (cx + rx, cy + ry // 3, cx + rx + _s(size, 0.18), cy + ry // 2),
    ]:
        pygame.draw.line(surf, (20, 80, 20), (bx, by), (ex, ey), 1)
    # Head + antennae
    pygame.draw.circle(surf, (30, 110, 30), (cx, cy - ry), _s(size, 0.11))
    pygame.draw.line(surf, (20, 70, 20), (cx - 3, cy - ry - _s(size, 0.08)),
                     (cx - _s(size, 0.22), cy - ry - _s(size, 0.3)), 1)
    pygame.draw.line(surf, (20, 70, 20), (cx + 3, cy - ry - _s(size, 0.08)),
                     (cx + _s(size, 0.22), cy - ry - _s(size, 0.3)), 1)


def _mouse(surf, cx, cy, size):
    """Forest mouse — cute round mouse with big ears."""
    r = _s(size, 0.25)
    # Body
    pygame.draw.ellipse(surf, (160, 120, 80), Rect(cx - r, cy - r // 3, r * 2, int(r * 1.3)))
    # Tail
    pygame.draw.arc(surf, (140, 100, 60),
                    Rect(cx - int(r * 1.4), cy - r // 3, r, int(r * 1.2)),
                    math.pi * 0.9, math.pi * 1.8, 3)
    # Head
    pygame.draw.circle(surf, (160, 120, 80), (cx + int(r * 0.8), cy - r // 3), int(r * 0.72))
    # Big rounded ears
    for ex in [-r // 3, r // 3 + int(r * 0.8)]:
        pygame.draw.circle(surf, (160, 120, 80), (cx + ex, cy - r // 3 - int(r * 0.72)), _s(size, 0.14))
        pygame.draw.circle(surf, (220, 160, 160), (cx + ex, cy - r // 3 - int(r * 0.72)), _s(size, 0.08))
    # Eyes
    pygame.draw.circle(surf, (10, 10, 10), (cx + int(r * 0.9), cy - r // 3 - r // 4), _s(size, 0.065))
    pygame.draw.circle(surf, (255, 255, 255), (cx + int(r * 0.9) + 1, cy - r // 3 - r // 4 - 1), 2)
    # Nose (pink)
    pygame.draw.circle(surf, (230, 140, 150), (cx + int(r * 1.46), cy - r // 3 - r // 8), 4)
    # Whiskers
    for wy in [-2, 0, 2]:
        pygame.draw.line(surf, (200, 180, 160),
                         (cx + int(r * 1.46), cy - r // 3 - r // 8 + wy),
                         (cx + int(r * 1.46) + _s(size, 0.2), cy - r // 3 - r // 8 + wy), 1)


def _orchid_bee(surf, cx, cy, size):
    """Orchid bee — metallic green body, transparent wings."""
    r = _s(size, 0.2)
    # Wings (transparent)
    for wing_x, wing_w in [(-_s(size, 0.28), _s(size, 0.24)), (_s(size, 0.04), _s(size, 0.24))]:
        ws = pygame.Surface((_s(size, 0.28), _s(size, 0.36)), pygame.SRCALPHA)
        pygame.draw.ellipse(ws, (200, 230, 255, 100), ws.get_rect())
        pygame.draw.ellipse(ws, (150, 200, 240, 180), ws.get_rect(), 1)
        surf.blit(ws, (cx + wing_x, cy - _s(size, 0.36)))
    # Abdomen
    pygame.draw.ellipse(surf, (20, 160, 60), Rect(cx - r, cy, r * 2, int(r * 1.6)))
    # Gold stripe
    pygame.draw.rect(surf, (200, 170, 20), Rect(cx - r + 2, cy + int(r * 0.6), r * 2 - 4, _s(size, 0.07)))
    # Thorax
    pygame.draw.ellipse(surf, (20, 130, 50), Rect(cx - r, cy - r // 2, r * 2, r))
    # Head
    pygame.draw.circle(surf, (20, 130, 50), (cx, cy - r), int(r * 0.7))
    # Antennae
    for side in [-1, 1]:
        pygame.draw.line(surf, (10, 80, 30), (cx + side * 3, cy - r - _s(size, 0.08)),
                         (cx + side * _s(size, 0.2), cy - r - _s(size, 0.3)), 1)
        pygame.draw.circle(surf, (10, 80, 30),
                           (cx + side * _s(size, 0.2), cy - r - _s(size, 0.3)), 2)


def _parrot(surf, cx, cy, size):
    """Green parrot — bright green with hooked beak."""
    r = _s(size, 0.26)
    # Body
    pygame.draw.ellipse(surf, (40, 180, 40), Rect(cx - r, cy - r // 2, r * 2, int(r * 1.5)))
    # Wing (darker green)
    pygame.draw.polygon(surf, (20, 140, 30), [
        (cx - r, cy), (cx - r - _s(size, 0.18), cy - _s(size, 0.08)),
        (cx - r - _s(size, 0.12), cy + r),
    ])
    # Tail (long pointed)
    pygame.draw.polygon(surf, (20, 140, 30), [
        (cx - r // 2, cy + r),
        (cx - r // 4, cy + r + _s(size, 0.4)),
        (cx + r // 4, cy + r + _s(size, 0.35)),
        (cx + r // 2, cy + r),
    ])
    # Head
    pygame.draw.circle(surf, (40, 180, 40), (cx, cy - r), int(r * 0.82))
    # Cheek patch (yellow)
    pygame.draw.circle(surf, (230, 210, 30), (cx + r // 4, cy - r + r // 4), _s(size, 0.1))
    # Eye ring (white)
    pygame.draw.circle(surf, (240, 240, 220), (cx + r // 3, cy - r), _s(size, 0.1))
    pygame.draw.circle(surf, (10, 10, 10), (cx + r // 3, cy - r), _s(size, 0.055))
    # Hooked beak
    pygame.draw.polygon(surf, (200, 170, 20), [
        (cx + r // 2, cy - r - r // 4), (cx + r, cy - r + 2), (cx + r // 2, cy - r + r // 4),
    ])
    pygame.draw.arc(surf, (160, 130, 10),
                    Rect(cx + r // 2, cy - r - 2, _s(size, 0.16), _s(size, 0.14)),
                    math.pi * 1.3, math.pi * 2, 3)


def _tapir(surf, cx, cy, size):
    """Brazilian tapir — large with prehensile snout."""
    r = _s(size, 0.28)
    # Body (stocky)
    pygame.draw.ellipse(surf, (80, 65, 55), Rect(cx - int(r * 1.5), cy - r // 2, int(r * 3), int(r * 1.4)))
    # Head
    hx = cx + int(r * 1.2)
    pygame.draw.ellipse(surf, (80, 65, 55),
                        Rect(hx - int(r * 0.8), cy - int(r * 0.9), int(r * 1.5), int(r * 1.1)))
    # Prehensile proboscis (droopy snout)
    pygame.draw.arc(surf, (70, 55, 45),
                    Rect(hx + r // 4, cy - r // 2, _s(size, 0.22), _s(size, 0.42)),
                    math.pi * 0.1, math.pi, 6)
    # Nostrils at tip of proboscis
    nose_x, nose_y = hx + r // 4 + _s(size, 0.1), cy - r // 2 + _s(size, 0.35)
    pygame.draw.circle(surf, (50, 40, 30), (nose_x - 3, nose_y), 3)
    pygame.draw.circle(surf, (50, 40, 30), (nose_x + 3, nose_y), 3)
    # Eye
    pygame.draw.circle(surf, (30, 20, 10), (hx + r // 4, cy - r // 2 - r // 4), _s(size, 0.07))
    pygame.draw.circle(surf, (200, 180, 160), (hx + r // 4 + 1, cy - r // 2 - r // 4 - 1), 2)
    # Legs
    for lx in [cx - r, cx - r // 3, cx + r // 3, cx + r]:
        pygame.draw.rect(surf, (65, 50, 40), Rect(lx - 5, cy + r // 2, 10, _s(size, 0.26)))
        pygame.draw.ellipse(surf, (50, 40, 30), Rect(lx - 7, cy + r // 2 + _s(size, 0.22), 14, 8))


# ── Plants ────────────────────────────────────────────────────────────────────

def _water_lily(surf, cx, cy, size):
    """Giant Amazon water lily — huge round floating leaf, flower."""
    r = _s(size, 0.42)
    # Lily pad
    pygame.draw.circle(surf, (30, 140, 40), (cx, cy), r)
    pygame.draw.circle(surf, (50, 170, 55), (cx, cy), r, 2)
    # Notch in pad
    pygame.draw.polygon(surf, (20, 80, 30), [(cx, cy), (cx + 2, cy - r), (cx + r // 3, cy - r // 2)])
    # Veins
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        pygame.draw.line(surf, (20, 110, 30), (cx, cy),
                         (cx + int(r * 0.9 * math.cos(rad)),
                          cy + int(r * 0.9 * math.sin(rad))), 1)
    # Flower (white petals)
    for a in range(0, 360, 45):
        rad = math.radians(a)
        px = cx + int(_s(size, 0.18) * math.cos(rad))
        py = cy - r // 4 + int(_s(size, 0.18) * math.sin(rad))
        pygame.draw.ellipse(surf, (240, 240, 225), Rect(px - 7, py - 10, 14, 20))
    # Flower centre (yellow)
    pygame.draw.circle(surf, (240, 200, 30), (cx, cy - r // 4), _s(size, 0.09))


def _heliconia(surf, cx, cy, size):
    """Heliconia — stacked red lobster-claw bracts."""
    # Stem
    pygame.draw.line(surf, (60, 140, 40),
                     (cx, cy + _s(size, 0.4)), (cx, cy - _s(size, 0.4)), 6)
    # Bracts (alternating left/right, orange-red)
    for i, (side, col) in enumerate(zip([-1, 1, -1, 1],
                                         [(220, 60, 20), (210, 80, 30), (200, 50, 15), (215, 70, 25)])):
        by = cy - _s(size, 0.1) + i * _s(size, 0.18)
        bx = cx + side * _s(size, 0.1)
        # Lobster claw shape
        pygame.draw.polygon(surf, col, [
            (bx, by),
            (bx + side * _s(size, 0.35), by - _s(size, 0.08)),
            (bx + side * _s(size, 0.3), by + _s(size, 0.1)),
            (bx, by + _s(size, 0.06)),
        ])
        # Yellow tip
        pygame.draw.circle(surf, (240, 210, 30),
                           (bx + side * _s(size, 0.32), by - _s(size, 0.02)), 4)
    # Large leaves at base
    for side in [-1, 1]:
        pts = [(cx, cy + _s(size, 0.3)),
               (cx + side * _s(size, 0.42), cy + _s(size, 0.15)),
               (cx + side * _s(size, 0.36), cy + _s(size, 0.44))]
        pygame.draw.polygon(surf, (40, 150, 40), pts)


def _orchid(surf, cx, cy, size):
    """Rainforest orchid — intricate flower with lip petal."""
    r = _s(size, 0.35)
    # Large petals (5 outer)
    for a in range(0, 360, 72):
        rad = math.radians(a - 90)
        px = cx + int(r * 0.6 * math.cos(rad))
        py = cy + int(r * 0.6 * math.sin(rad))
        pygame.draw.ellipse(surf, (210, 100, 200),
                            Rect(px - _s(size, 0.12), py - _s(size, 0.22),
                                 _s(size, 0.24), _s(size, 0.44)))
    # Lip petal (bigger, bottom centre)
    pygame.draw.ellipse(surf, (240, 60, 180),
                        Rect(cx - _s(size, 0.16), cy, _s(size, 0.32), _s(size, 0.3)))
    # Dark veins on lip
    for i in range(-2, 3):
        pygame.draw.line(surf, (180, 20, 140),
                         (cx + i * _s(size, 0.04), cy + 2),
                         (cx + i * _s(size, 0.03), cy + _s(size, 0.26)), 1)
    # Column (centre)
    pygame.draw.circle(surf, (240, 220, 30), (cx, cy), _s(size, 0.1))
    # Stem
    pygame.draw.line(surf, (60, 140, 40),
                     (cx, cy + _s(size, 0.3)), (cx - _s(size, 0.08), cy + _s(size, 0.46)), 3)


def _bromeliad(surf, cx, cy, size):
    """Bromeliad — rosette of spiky leaves with water pool at centre."""
    # Spiky leaves radiating out
    for a in range(0, 360, 45):
        rad = math.radians(a)
        lx = cx + int(_s(size, 0.42) * math.cos(rad))
        ly = cy + int(_s(size, 0.42) * math.sin(rad))
        pygame.draw.polygon(surf, (50, 160, 50), [
            (cx + int(_s(size, 0.06) * math.cos(rad + 1.2)),
             cy + int(_s(size, 0.06) * math.sin(rad + 1.2))),
            (lx, ly),
            (cx + int(_s(size, 0.06) * math.cos(rad - 1.2)),
             cy + int(_s(size, 0.06) * math.sin(rad - 1.2))),
        ])
        # Spine on leaf
        pygame.draw.line(surf, (30, 120, 30), (cx, cy), (lx, ly), 1)
    # Water pool (blue circle at centre)
    pygame.draw.circle(surf, (60, 140, 220), (cx, cy), _s(size, 0.14))
    pygame.draw.circle(surf, (80, 180, 255), (cx, cy), _s(size, 0.14), 2)
    # Small frog peeking (tiny green spot)
    pygame.draw.circle(surf, (80, 200, 80), (cx + _s(size, 0.06), cy - _s(size, 0.06)), _s(size, 0.055))


def _rubber_tree(surf, cx, cy, size):
    """Rubber tree with dripping white latex."""
    # Trunk
    trunk_w = _s(size, 0.12)
    pygame.draw.rect(surf, (100, 70, 35),
                     Rect(cx - trunk_w // 2, cy - _s(size, 0.1), trunk_w, _s(size, 0.55)))
    # V-shaped cut and latex drip
    pygame.draw.line(surf, (50, 35, 15), (cx - trunk_w // 4, cy + _s(size, 0.06)),
                     (cx, cy + _s(size, 0.16)), 3)
    pygame.draw.line(surf, (50, 35, 15), (cx + trunk_w // 4, cy + _s(size, 0.06)),
                     (cx, cy + _s(size, 0.16)), 3)
    # Dripping latex
    pygame.draw.line(surf, (230, 225, 215), (cx, cy + _s(size, 0.18)),
                     (cx, cy + _s(size, 0.32)), 3)
    pygame.draw.circle(surf, (230, 225, 215), (cx, cy + _s(size, 0.33)), 4)
    # Large oval leaves
    for a, dist in [(0, 0.28), (120, 0.3), (240, 0.28)]:
        rad = math.radians(a - 100)
        lx = cx + int(_s(size, dist) * math.cos(rad))
        ly = cy - _s(size, 0.12) + int(_s(size, dist) * math.sin(rad))
        pygame.draw.ellipse(surf, (40, 150, 40), Rect(lx - _s(size, 0.14), ly - _s(size, 0.22),
                                                       _s(size, 0.28), _s(size, 0.44)))
        pygame.draw.line(surf, (25, 110, 25), (lx, ly - _s(size, 0.2)), (lx, ly + _s(size, 0.2)), 1)


def _kapok_tree(surf, cx, cy, size):
    """Kapok tree — giant trunk with buttress roots, spreading canopy."""
    # Buttress roots (flanges)
    for a in range(0, 360, 90):
        rad = math.radians(a)
        rx = cx + int(_s(size, 0.25) * math.cos(rad))
        ry = cy + _s(size, 0.32) + int(_s(size, 0.12) * math.sin(rad))
        pygame.draw.polygon(surf, (80, 55, 25), [
            (cx, cy + _s(size, 0.32)), (rx, ry), (cx + int(_s(size, 0.08) * math.cos(rad + 1.2)),
                                                    cy + _s(size, 0.32)),
        ])
    # Massive trunk
    tw = _s(size, 0.13)
    pygame.draw.rect(surf, (90, 60, 30),
                     Rect(cx - tw, cy - _s(size, 0.22), tw * 2, _s(size, 0.54)))
    # Large spreading canopy (layered circles)
    for rad_frac, col in [(0.42, (20, 100, 20)), (0.36, (35, 130, 30)), (0.28, (50, 160, 40))]:
        pygame.draw.circle(surf, col, (cx, cy - _s(size, 0.2)), _s(size, rad_frac))
    # Cottony seed pods (white wisps)
    for px, py in [(cx - _s(size, 0.2), cy - _s(size, 0.4)),
                   (cx + _s(size, 0.15), cy - _s(size, 0.35)),
                   (cx, cy - _s(size, 0.48))]:
        pygame.draw.circle(surf, (230, 225, 215), (px, py), _s(size, 0.06))


def _cacao(surf, cx, cy, size):
    """Cacao tree — pods growing directly on trunk."""
    # Trunk
    tw = _s(size, 0.1)
    pygame.draw.rect(surf, (90, 60, 30),
                     Rect(cx - tw, cy - _s(size, 0.2), tw * 2, _s(size, 0.55)))
    # Cacao pods (orange/yellow, ridged ovals) growing from trunk
    for px, py, col in [
        (cx + tw + 2, cy - _s(size, 0.08), (220, 150, 20)),
        (cx - tw - 2, cy + _s(size, 0.06), (200, 100, 15)),
        (cx + tw + 2, cy + _s(size, 0.2), (210, 140, 25)),
    ]:
        pod_w, pod_h = _s(size, 0.16), _s(size, 0.28)
        pygame.draw.ellipse(surf, col, Rect(px, py - pod_h // 2, pod_w, pod_h))
        for ri in range(1, 4):
            lx = px + ri * pod_w // 4
            pygame.draw.line(surf, (170, 110, 10), (lx, py - pod_h // 2 + 2), (lx, py + pod_h // 2 - 2), 1)
    # Leaves
    for a, d in [(0, 0.3), (180, 0.3), (90, 0.28)]:
        rad = math.radians(a - 90)
        lx = cx + int(_s(size, d) * math.cos(rad))
        ly = cy - _s(size, 0.25) + int(_s(size, d) * math.sin(rad))
        pygame.draw.ellipse(surf, (35, 140, 35),
                            Rect(lx - _s(size, 0.1), ly - _s(size, 0.2),
                                 _s(size, 0.2), _s(size, 0.4)))


def _passion_flower(surf, cx, cy, size):
    """Passion flower — exotic layered petals with corona filaments."""
    r = _s(size, 0.38)
    # Outer petals (white, 10)
    for a in range(0, 360, 36):
        rad = math.radians(a - 90)
        px = cx + int(r * 0.6 * math.cos(rad))
        py = cy + int(r * 0.6 * math.sin(rad))
        pygame.draw.ellipse(surf, (240, 240, 235),
                            Rect(px - _s(size, 0.1), py - _s(size, 0.22),
                                 _s(size, 0.2), _s(size, 0.44)))
    # Corona filaments (purple/white striped ring)
    for a in range(0, 360, 8):
        rad = math.radians(a)
        fx1 = cx + int(_s(size, 0.16) * math.cos(rad))
        fy1 = cy + int(_s(size, 0.16) * math.sin(rad))
        fx2 = cx + int(_s(size, 0.32) * math.cos(rad))
        fy2 = cy + int(_s(size, 0.32) * math.sin(rad))
        col = (140, 60, 200) if a % 16 == 0 else (200, 200, 255)
        pygame.draw.line(surf, col, (fx1, fy1), (fx2, fy2), 2)
    # Centre disk (green + stamens)
    pygame.draw.circle(surf, (60, 160, 40), (cx, cy), _s(size, 0.14))
    for a in range(0, 360, 72):
        rad = math.radians(a)
        pygame.draw.circle(surf, (220, 180, 30),
                           (cx + int(_s(size, 0.1) * math.cos(rad)),
                            cy + int(_s(size, 0.1) * math.sin(rad))), 4)
    # Tendril (vine spiral)
    pygame.draw.arc(surf, (50, 150, 40),
                    Rect(cx + r // 2, cy + r // 2, _s(size, 0.22), _s(size, 0.22)),
                    0, math.pi * 1.7, 2)


def _banana_plant(surf, cx, cy, size):
    """Banana plant — huge paddle leaves, banana bunch."""
    # Pseudostem
    pygame.draw.rect(surf, (80, 150, 60),
                     Rect(cx - _s(size, 0.1), cy - _s(size, 0.1), _s(size, 0.2), _s(size, 0.5)))
    # Large paddle leaves
    for a, d in [(-50, 0.44), (50, 0.44), (-20, 0.38), (20, 0.38)]:
        rad = math.radians(a)
        lx = cx + int(_s(size, d) * math.cos(rad))
        ly = cy - _s(size, 0.18) + int(_s(size, d) * math.sin(rad))
        pygame.draw.ellipse(surf, (50, 170, 50),
                            Rect(lx - _s(size, 0.12), ly - _s(size, 0.32),
                                 _s(size, 0.24), _s(size, 0.64)))
        # Mid-rib
        pygame.draw.line(surf, (30, 130, 30), (cx, cy - _s(size, 0.18)), (lx, ly), 2)
    # Banana bunch (hanging below)
    pygame.draw.ellipse(surf, (220, 200, 30),
                        Rect(cx - _s(size, 0.16), cy + _s(size, 0.28),
                             _s(size, 0.32), _s(size, 0.18)))
    # Individual bananas
    for bx in [-_s(size, 0.08), 0, _s(size, 0.08)]:
        pygame.draw.arc(surf, (230, 210, 40),
                        Rect(cx + bx - 6, cy + _s(size, 0.3), 12, 10),
                        0, math.pi, 3)


def _amazon_lily(surf, cx, cy, size):
    """Amazon lily — delicate white lily flower with long petals."""
    # Petals (6, white with pink tinge)
    for a in range(0, 360, 60):
        rad = math.radians(a - 90)
        px = cx + int(_s(size, 0.28) * math.cos(rad))
        py = cy + int(_s(size, 0.28) * math.sin(rad))
        pygame.draw.ellipse(surf, (245, 235, 245),
                            Rect(px - _s(size, 0.09), py - _s(size, 0.22),
                                 _s(size, 0.18), _s(size, 0.44)))
        pygame.draw.line(surf, (220, 180, 220), (cx, cy), (px, py), 1)
    # Stamens
    for a in range(0, 360, 30):
        rad = math.radians(a)
        pygame.draw.line(surf, (240, 200, 30), (cx, cy),
                         (cx + int(_s(size, 0.14) * math.cos(rad)),
                          cy + int(_s(size, 0.14) * math.sin(rad))), 2)
        pygame.draw.circle(surf, (240, 200, 30),
                           (cx + int(_s(size, 0.14) * math.cos(rad)),
                            cy + int(_s(size, 0.14) * math.sin(rad))), 3)
    # Stem and leaves
    pygame.draw.line(surf, (60, 150, 50), (cx, cy), (cx - _s(size, 0.1), cy + _s(size, 0.42)), 3)
    pygame.draw.ellipse(surf, (50, 160, 50),
                        Rect(cx - _s(size, 0.28), cy + _s(size, 0.22),
                             _s(size, 0.24), _s(size, 0.12)))


def _strangler_fig(surf, cx, cy, size):
    """Strangler fig — host tree wrapped in roots."""
    # Host tree trunk (lighter)
    pygame.draw.rect(surf, (110, 80, 45),
                     Rect(cx - _s(size, 0.12), cy - _s(size, 0.28), _s(size, 0.24), _s(size, 0.65)))
    # Strangler fig roots (darker, wrapping)
    for offset in [-_s(size, 0.08), 0, _s(size, 0.08)]:
        for seg in range(8):
            y1 = cy - _s(size, 0.25) + seg * _s(size, 0.08)
            y2 = y1 + _s(size, 0.08)
            wave = int(_s(size, 0.06) * math.sin(seg * 1.5 + offset))
            pygame.draw.line(surf, (60, 40, 20),
                             (cx + offset + wave, y1),
                             (cx + offset - wave, y2), 3)
    # Canopy
    for rad_f, col in [(0.38, (20, 100, 20)), (0.3, (40, 140, 30))]:
        pygame.draw.circle(surf, col, (cx, cy - _s(size, 0.26)), _s(size, rad_f))
    # Figs (small red berries)
    for fx, fy in [(cx - _s(size, 0.08), cy), (cx + _s(size, 0.1), cy + _s(size, 0.05)),
                   (cx - _s(size, 0.04), cy + _s(size, 0.1))]:
        pygame.draw.circle(surf, (200, 60, 30), (fx, fy), 5)


def _brazil_nut_plant(surf, cx, cy, size):
    """Brazil nut tree — tall with spherical seed capsule."""
    # Trunk
    tw = _s(size, 0.1)
    pygame.draw.rect(surf, (100, 70, 35),
                     Rect(cx - tw, cy - _s(size, 0.18), tw * 2, _s(size, 0.54)))
    # Canopy
    pygame.draw.circle(surf, (30, 120, 30), (cx, cy - _s(size, 0.18)), _s(size, 0.36))
    pygame.draw.circle(surf, (50, 150, 40), (cx - _s(size, 0.1), cy - _s(size, 0.24)), _s(size, 0.22))
    pygame.draw.circle(surf, (50, 150, 40), (cx + _s(size, 0.1), cy - _s(size, 0.24)), _s(size, 0.22))
    # Seed pod (brown sphere under branch)
    pod_x, pod_y = cx + _s(size, 0.1), cy - _s(size, 0.02)
    pygame.draw.circle(surf, (140, 90, 30), (pod_x, pod_y), _s(size, 0.14))
    pygame.draw.circle(surf, (160, 110, 45), (pod_x - 3, pod_y - 3), _s(size, 0.06))
    # Fallen nut (on ground)
    nut_x, nut_y = cx - _s(size, 0.16), cy + _s(size, 0.36)
    pygame.draw.ellipse(surf, (120, 80, 25), Rect(nut_x - 8, nut_y - 6, 16, 12))


def _cashew_plant(surf, cx, cy, size):
    """Cashew plant — distinctive apple + dangling nut."""
    # Branch
    pygame.draw.line(surf, (90, 60, 30),
                     (cx, cy + _s(size, 0.42)), (cx, cy - _s(size, 0.2)), 5)
    pygame.draw.line(surf, (90, 60, 30),
                     (cx, cy - _s(size, 0.1)), (cx + _s(size, 0.2), cy), 4)
    # Cashew apple (pear-shaped, red-orange)
    pygame.draw.ellipse(surf, (230, 70, 30),
                        Rect(cx + _s(size, 0.08), cy - _s(size, 0.02),
                             _s(size, 0.24), _s(size, 0.32)))
    # Apple highlight
    pygame.draw.ellipse(surf, (240, 130, 60),
                        Rect(cx + _s(size, 0.1), cy, _s(size, 0.1), _s(size, 0.1)))
    # Cashew nut (kidney-shaped, grey-green, hanging below)
    nut_pts = [
        (cx + _s(size, 0.16), cy + _s(size, 0.3)),
        (cx + _s(size, 0.32), cy + _s(size, 0.28)),
        (cx + _s(size, 0.34), cy + _s(size, 0.38)),
        (cx + _s(size, 0.18), cy + _s(size, 0.42)),
    ]
    pygame.draw.polygon(surf, (130, 150, 80), nut_pts)
    pygame.draw.polygon(surf, (100, 120, 60), nut_pts, 2)
    # Leaves
    for a, d in [(-40, 0.34), (40, 0.3), (0, 0.38)]:
        rad = math.radians(a - 90)
        lx = cx + int(_s(size, d) * math.cos(rad))
        ly = cy - _s(size, 0.15) + int(_s(size, d) * math.sin(rad))
        pygame.draw.ellipse(surf, (45, 160, 50),
                            Rect(lx - _s(size, 0.1), ly - _s(size, 0.18),
                                 _s(size, 0.2), _s(size, 0.36)))


def _generic(surf, cx, cy, size):
    """Generic creature — green circle with question mark."""
    r = _s(size, 0.38)
    pygame.draw.circle(surf, (40, 130, 60), (cx, cy), r)
    pygame.draw.circle(surf, (60, 170, 80), (cx, cy), r, 3)
    font = pygame.font.SysFont(None, size)
    img = font.render("?", True, (255, 255, 200))
    surf.blit(img, (cx - img.get_width() // 2, cy - img.get_height() // 2))


# ── Explorer avatar ───────────────────────────────────────────────────────────

def draw_explorer(surf, cx, cy, size: int = 60, frame: int = 0) -> None:
    """Draw a cute little explorer character.

    frame: 0=standing, 1=left step, 2=right step  (for walking animation)
    """
    s = size
    # Bob up/down based on walk frame
    bob = {0: 0, 1: -3, 2: -3}.get(frame % 3, 0)
    cy += bob

    # === Hat (khaki with brim) ===
    brim_w = int(s * 0.55)
    pygame.draw.ellipse(surf, (170, 145, 80),
                        Rect(cx - brim_w, cy - int(s * 0.62), brim_w * 2, int(s * 0.14)))
    crown_w = int(s * 0.34)
    pygame.draw.rect(surf, (180, 155, 85),
                     Rect(cx - crown_w, cy - int(s * 0.98), crown_w * 2, int(s * 0.38)))
    pygame.draw.rect(surf, (160, 135, 70),
                     Rect(cx - crown_w, cy - int(s * 0.62), crown_w * 2, int(s * 0.06)))

    # === Head ===
    head_r = int(s * 0.24)
    pygame.draw.circle(surf, (240, 195, 150), (cx, cy - int(s * 0.36)), head_r)

    # === Eyes ===
    for ex in [-int(s * 0.07), int(s * 0.07)]:
        pygame.draw.circle(surf, (60, 40, 20), (cx + ex, cy - int(s * 0.38)), int(s * 0.045))
        pygame.draw.circle(surf, (255, 255, 255), (cx + ex + 1, cy - int(s * 0.38) - 1), int(s * 0.02))

    # === Smile ===
    pygame.draw.arc(surf, (180, 100, 80),
                    Rect(cx - int(s * 0.07), cy - int(s * 0.3),
                         int(s * 0.14), int(s * 0.08)),
                    math.pi, 2 * math.pi, 2)

    # === Body (khaki shirt) ===
    body_w = int(s * 0.3)
    pygame.draw.rect(surf, (160, 145, 80),
                     Rect(cx - body_w, cy - int(s * 0.14), body_w * 2, int(s * 0.32)),
                     border_radius=4)
    # Pocket
    pygame.draw.rect(surf, (140, 125, 65),
                     Rect(cx + int(s * 0.06), cy - int(s * 0.06), int(s * 0.12), int(s * 0.1)),
                     border_radius=2)

    # === Backpack ===
    pygame.draw.rect(surf, (110, 80, 40),
                     Rect(cx + body_w - 2, cy - int(s * 0.1), int(s * 0.16), int(s * 0.24)),
                     border_radius=4)

    # === Arms ===
    left_angle  = math.radians(-30 + (frame == 1) * 20)
    right_angle = math.radians(30 - (frame == 2) * 20)
    for angle, side in [(left_angle, -1), (right_angle, 1)]:
        ax = cx + side * body_w
        ay = cy - int(s * 0.1)
        ex = ax + int(s * 0.28 * math.cos(angle + math.pi * 0.5) * side)
        ey = ay + int(s * 0.28 * math.sin(angle + math.pi * 0.5))
        pygame.draw.line(surf, (200, 160, 110), (ax, ay), (ex, ey), int(s * 0.09))
        pygame.draw.circle(surf, (200, 160, 110), (ex, ey), int(s * 0.07))

    # === Legs (khaki shorts/pants) ===
    left_leg_off  = int(s * 0.15) * (1 if frame == 1 else (-1 if frame == 2 else 0))
    right_leg_off = -left_leg_off
    for lx_off, ly_extra in [(-int(s * 0.1), left_leg_off), (int(s * 0.1), right_leg_off)]:
        # Upper leg
        pygame.draw.rect(surf, (155, 130, 70),
                         Rect(cx + lx_off - int(s * 0.08),
                              cy + int(s * 0.17),
                              int(s * 0.16), int(s * 0.24)),
                         border_radius=3)
        # Lower leg / boot
        pygame.draw.rect(surf, (90, 65, 35),
                         Rect(cx + lx_off - int(s * 0.07),
                              cy + int(s * 0.4) + ly_extra,
                              int(s * 0.14), int(s * 0.18)),
                         border_radius=3)
        # Boot sole
        pygame.draw.ellipse(surf, (60, 40, 20),
                            Rect(cx + lx_off - int(s * 0.1),
                                 cy + int(s * 0.55) + ly_extra,
                                 int(s * 0.2), int(s * 0.07)))
