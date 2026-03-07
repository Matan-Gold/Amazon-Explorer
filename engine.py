# -*- coding: utf-8 -*-
"""
engine.py — All game logic: discovery, movement cost, skills, action dispatch.

Rules:
  - No printing here. All output goes through state.message_queue (strings or tuples)
    which main.py drains and prints after every action.
  - No Hebrew strings. All messages are t() calls.
  - Mutates GameState in place.

Message queue contents:
  - Plain str  → main.py prints directly
  - ("discovery_new", Discovery, int)  → main.py renders full celebration banner
  - ("discovery_old", Discovery, int)  → main.py renders "already known" banner
  - ("item_found", Item)               → main.py renders item discovery banner
"""

import json
import random
from pathlib import Path

import localization as loc
from models import (
    Discovery, GameState, Item, Player, Skill,
    MAX_FOOD, FOOD_COST_PER_MOVE, UPGRADE_COSTS,
)


# ── Data Loading ──────────────────────────────────────────────────────────────

def load_discoveries(
    animals_path: str | None = None,
    plants_path:  str | None = None,
) -> list:
    """Load animals.json + plants.json and return a flat list of Discovery objects."""
    base = Path(__file__).parent / "data"
    a_path = Path(animals_path) if animals_path else base / "animals.json"
    p_path = Path(plants_path)  if plants_path  else base / "plants.json"

    discoveries = []

    with open(a_path, encoding="utf-8") as f:
        for item in json.load(f)["animals"]:
            discoveries.append(_make_discovery(item, "animal"))

    with open(p_path, encoding="utf-8") as f:
        for item in json.load(f)["plants"]:
            discoveries.append(_make_discovery(item, "plant"))

    return discoveries


def _make_discovery(data: dict, category: str) -> Discovery:
    return Discovery(
        id=data["id"],
        category=category,
        name=data["name"],
        title=data["title"],
        description=data["description"],
        fun_fact=data["fun_fact"],
        knowledge_reward=data["knowledge_reward"],
        tile_types=data["tile_types"],
        emoji=data["emoji"],
    )


def load_items(path: str | None = None) -> list:
    """Load items.json and return a list of Item objects."""
    base = Path(__file__).parent / "data"
    target = Path(path) if path else base / "items.json"
    items = []
    with open(target, encoding="utf-8") as f:
        for data in json.load(f)["items"]:
            items.append(Item(
                id=data["id"],
                emoji=data["emoji"],
                name=data["name"],
                description=data["description"],
            ))
    return items


# ── Action Dispatcher ─────────────────────────────────────────────────────────

def process_action(action: str, params: dict, state: GameState) -> None:
    """Dispatch a scene action string to the correct handler.

    Actions:
      "discover"          — roll for a random discovery on the current tile
      "discover_specific" — trigger a specific discovery by id
      "give_item"         — give the player a permanent tool item
      "message_only"      — queue a single localised string (comedic/atmospheric)
      "knowledge_gain"    — silently add knowledge points
      "rest"              — restore food (params: food_restore)
      "food_gain"         — add food (params: amount)
      "close_scene"       — no-op; main.py exits the scene loop on return
      "open_skills"       — handled by main.py
      "open_book"         — handled by main.py
    """
    if action == "discover":
        do_discover(state)
    elif action == "discover_specific":
        do_discover_specific(params.get("discovery_id", ""), state)
    elif action == "give_item":
        do_give_item(params.get("item_id", ""), int(params.get("knowledge_reward", 3)), state)
    elif action == "message_only":
        msg_key = params.get("message_key", "")
        if msg_key:
            state.message_queue.append(loc.t(msg_key))
    elif action == "knowledge_gain":
        state.player.knowledge += int(params.get("amount", 1))
    elif action == "rest":
        do_rest(int(params.get("food_restore", 2)), state)
    elif action == "food_gain":
        do_food_gain(int(params.get("amount", 1)), state)
    elif action in ("close_scene", "open_skills", "open_book"):
        pass  # main.py handles scene exit and screen transitions
    # Unknown actions are silently ignored — never crash the game.


# ── Discovery ─────────────────────────────────────────────────────────────────

def do_discover(state: GameState) -> None:
    """Roll for a random discovery on the player's current tile.

    1. Filter discoveries_db by current tile type.
    2. Roll for success using Explorer skill.
    3. If miss: queue a gentle "nothing found" message.
    4. If hit and new: full celebration + knowledge reward × Nature Friend.
    5. If hit and already known: quiet re-meet + flat 1 knowledge.
    """
    from map import get_tile

    player = state.player
    tile = get_tile(state.world, player.x, player.y)
    tile_type = tile.tile_type

    pool = [d for d in state.discoveries_db if tile_type in d.tile_types]

    if not pool:
        state.message_queue.append(loc.t("scene.exploring"))
        return

    # Explorer skill: base 0.3 + 0.1 per level
    explorer_level = player.skills["explorer"].level
    chance = 0.3 + explorer_level * 0.1

    if random.random() >= chance:
        state.message_queue.append(loc.t("scene.exploring"))
        return

    discovery = random.choice(pool)
    _apply_discovery(discovery, state)


def do_discover_specific(discovery_id: str, state: GameState) -> None:
    """Trigger a specific discovery by ID.

    Same reward logic as do_discover. Falls back to random discover if id not found.
    """
    discovery = next((d for d in state.discoveries_db if d.id == discovery_id), None)

    if discovery is None:
        do_discover(state)
        return

    _apply_discovery(discovery, state)


def _apply_discovery(discovery: Discovery, state: GameState) -> None:
    """Shared reward logic for both random and specific discoveries."""
    player = state.player
    is_new = discovery.id not in player.discovered

    if is_new:
        player.discovered.add(discovery.id)
        nature_level = player.skills["nature_friend"].level
        multiplier = 1.0 + nature_level * 0.15
        knowledge_gained = max(1, int(discovery.knowledge_reward * multiplier))
        player.knowledge += knowledge_gained
        state.message_queue.append(("discovery_new", discovery, knowledge_gained))
    else:
        knowledge_gained = 1
        player.knowledge += knowledge_gained
        state.message_queue.append(("discovery_old", discovery, knowledge_gained))


# ── Items ─────────────────────────────────────────────────────────────────────

def do_give_item(item_id: str, knowledge_reward: int, state: GameState) -> None:
    """Give the player a permanent tool item.

    If the player already owns it: award knowledge_reward instead and queue a message.
    """
    player = state.player
    item = next((i for i in state.items_db if i.id == item_id), None)

    if item is None:
        return

    if item.id not in player.items:
        player.items.add(item.id)
        state.message_queue.append(("item_found", item))
    else:
        player.knowledge += knowledge_reward
        state.message_queue.append(
            loc.t("items.already_have", item_name=item.name, amount=knowledge_reward)
        )


# ── Food & Rest ───────────────────────────────────────────────────────────────

def do_rest(food_restore: int, state: GameState) -> None:
    """Restore food, capped at MAX_FOOD. Queue the 'rested' message."""
    player = state.player
    player.food = min(MAX_FOOD, player.food + food_restore)
    state.message_queue.append(loc.t("camp.rested"))


def do_food_gain(amount: int, state: GameState) -> None:
    """Add food from foraging, capped at MAX_FOOD. Queue gain message."""
    player = state.player
    player.food = min(MAX_FOOD, player.food + amount)
    state.message_queue.append(loc.t("food.gain", amount=amount))


def apply_move_cost(state: GameState) -> bool:
    """Deduct food for one step of movement, applying Survival Helper skill.

    cost = FOOD_COST_PER_MOVE × (1.0 − survival_level × 0.1), minimum 0.1.
    Returns True if the player still has food.
    Returns False if food hits 0 — also teleports player to camp and queues message.
    """
    player = state.player
    survival_level = player.skills["survival_helper"].level
    cost = FOOD_COST_PER_MOVE * max(0.1, 1.0 - survival_level * 0.1)
    player.food = max(0.0, player.food - cost)

    if player.food <= 0:
        player.x = 2
        player.y = 2
        state.message_queue.append(loc.t("movement.food_low"))
        return False

    if player.food <= 3:
        state.message_queue.append(loc.t("movement.food_warning"))

    return True


# ── Skills ────────────────────────────────────────────────────────────────────

def upgrade_skill(skill_id: str, state: GameState) -> None:
    """Attempt to upgrade a skill by one level.

    Checks: skill exists, level < 3, player has enough knowledge.
    Deducts knowledge and increments level on success.
    Queues appropriate message in both cases.
    """
    player = state.player
    skill = player.skills.get(skill_id)

    if skill is None:
        return

    if skill.level >= 3:
        state.message_queue.append(loc.t("skills.max_level"))
        return

    target_level = skill.level + 1
    cost = UPGRADE_COSTS.get(target_level, 999)

    if player.knowledge < cost:
        state.message_queue.append(loc.t("skills.not_enough"))
        return

    player.knowledge -= cost
    skill.level += 1
    state.message_queue.append(loc.t("skills.upgraded"))
