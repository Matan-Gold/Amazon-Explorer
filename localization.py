# -*- coding: utf-8 -*-
"""
localization.py — Single bridge between Python logic and Hebrew player-facing text.

Usage:
    import localization
    localization.load()          # call once at startup
    localization.t("ui.title_line1")
    localization.t("food.gain", amount=3)
    localization.t("skills.level_label", level=2)

Rules:
  - NO Hebrew strings live anywhere else in the codebase.
  - t() never raises — returns the key string on miss so the game never crashes.
  - python-bidi converts Hebrew from logical order to visual order so it renders
    correctly in LTR terminals (PowerShell). Gracefully degrades if not installed.
"""

import json
import sys
from pathlib import Path

try:
    from bidi.algorithm import get_display as _bidi
    _HAS_BIDI = True
except ImportError:
    _HAS_BIDI = False

_strings: dict = {}


def load(path: str | None = None) -> None:
    """Load all Hebrew strings from text_he.json into the module-level dict.
    Call exactly once at startup before any call to t().
    """
    global _strings
    target = Path(path) if path else Path(__file__).parent / "data" / "text_he.json"
    with open(target, encoding="utf-8") as f:
        _strings = json.load(f)


def t(key: str, **kwargs) -> str:
    """Return the Hebrew string for a dot-notation key, bidi-converted for LTR terminals.

    Examples:
        t("ui.divider")                     -> "✨────── ... ──✨"
        t("food.gain", amount=3)            -> "+3 🍎 מזון!"
        t("skills.level_label", level=2)    -> "רמה 2/3"

    On missing key: prints a warning to stderr and returns the raw key.
    On format error: prints a warning to stderr and returns the unformatted string.
    """
    value = _resolve(key)
    if value is None:
        print(f"[localization] missing key: {key!r}", file=sys.stderr)
        return key
    if kwargs:
        try:
            result = value.format(**kwargs)
        except (KeyError, IndexError) as exc:
            print(f"[localization] format error for {key!r}: {exc}", file=sys.stderr)
            result = value
    else:
        result = value
    return result


def _resolve(key: str) -> str | None:
    """Walk dot-notation path through _strings. Returns None if not found."""
    parts = key.split(".")
    node = _strings
    for part in parts:
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node if isinstance(node, str) else None
