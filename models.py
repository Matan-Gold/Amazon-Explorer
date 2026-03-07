# -*- coding: utf-8 -*-
"""
models.py — Core data structures for the Amazon Rainforest Explorer game.

All player-facing text is loaded from data/text_he.json via localization.py.
No Hebrew strings live in this file.

Grid convention: grid[y][x]  (y=0 is the top row, x=0 is the left column)
"""

from dataclasses import dataclass, field


# ── Constants ─────────────────────────────────────────────────────────────────

MAX_FOOD: float = 15.0
FOOD_COST_PER_MOVE: float = 1.0

# Cost to reach a given skill level (key = target level)
UPGRADE_COSTS: dict = {1: 5, 2: 10}

# Display symbols for each tile type (used by map.py)
TILE_SYMBOLS: dict = {
    "Forest":       "🌿",
    "River":        "🌊",
    "Clearing":     "☀️",
    "Dense Jungle": "🌳",
    "Camp":         "🏕️",
    "Unknown":      "❓",
}

# Avatar choices shown during setup
AVATAR_OPTIONS: list = ["👧", "🧒", "🦋", "🐰"]


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclass
class Tile:
    """A single cell in the 5×5 world grid."""
    tile_type: str          # "Forest" | "River" | "Clearing" | "Dense Jungle" | "Camp"
    explored: bool = False  # False = renders as Unknown until player visits


@dataclass
class Discovery:
    """One discoverable animal or plant loaded from animals.json / plants.json."""
    id: str
    category: str           # "animal" | "plant"
    name: str               # Hebrew display name
    title: str              # Hebrew short playful subtitle
    description: str        # Hebrew 2-sentence educational text
    fun_fact: str           # Hebrew 1-sentence fun fact
    knowledge_reward: int   # Base knowledge granted on first discovery
    tile_types: list        # e.g. ["River"] or ["Forest", "Dense Jungle"]
    emoji: str              # Decorative emoji for displays


@dataclass
class Item:
    """A carryable tool found in the world. Permanent — never dropped."""
    id: str
    emoji: str
    name: str               # Hebrew display name
    description: str        # Hebrew flavour text shown on discovery


@dataclass
class Skill:
    """One of the three upgradeable player skills."""
    id: str
    level: int = 0          # 0–3; 3 is max


@dataclass
class Player:
    """All mutable state belonging to the player."""
    name: str
    avatar: str             # One of AVATAR_OPTIONS
    x: int = 2             # Column in the 5×5 grid (0-indexed)
    y: int = 2             # Row    in the 5×5 grid (0-indexed)
    food: float = 10.0
    knowledge: int = 0
    discovered: set = field(default_factory=set)    # Set of Discovery.id strings
    items: set = field(default_factory=set)         # Set of Item.id strings (permanent tools)
    skills: dict = field(default_factory=lambda: {
        "explorer":        Skill(id="explorer"),
        "nature_friend":   Skill(id="nature_friend"),
        "survival_helper": Skill(id="survival_helper"),
    })


@dataclass
class World:
    """The 5×5 exploration grid.

    Access a tile with: world.grid[y][x]
    """
    grid: list              # list[list[Tile]]
    width: int = 5
    height: int = 5


@dataclass
class GameState:
    """Top-level container passed through engine, scenes, and main."""
    player: Player
    world: World
    discoveries_db: list    # list[Discovery] — full set loaded at startup
    items_db: list = field(default_factory=list)        # list[Item]
    running: bool = True
    message_queue: list = field(default_factory=list)   # Strings/tuples drained by main.py
