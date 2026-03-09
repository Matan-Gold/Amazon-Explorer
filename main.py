# -*- coding: utf-8 -*-
"""
main.py — GameApp: pygame window, state machine, event handling.

States:
  TITLE  → SETUP_NAME → SETUP_AVATAR → MAP
  MAP ↔ SCENE_OBJECTS ↔ SCENE_INTERACTIONS → POPUP
  MAP → BOOK / SKILLS
"""

import math
import sys
import threading
import pygame

import localization as loc
import engine
import map as game_map
import scenes
import asset_generator
from models import Player, GameState, AVATAR_OPTIONS


# ── GameApp ────────────────────────────────────────────────────────────────────

class GameApp:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        self.win = pygame.display.set_mode((scenes.W, scenes.H))
        pygame.display.set_caption("Amazon Rainforest Explorer")
        self.clock = pygame.time.Clock()

        # State machine
        self.state = "TITLE"
        self.game_state: GameState | None = None

        # Setup flow
        self.name_input = ""
        self.avatar_hover = -1
        self.avatar_selected = -1

        # Map
        self.hover_tile: tuple | None = None
        self._tile_rects: dict = {}

        # Map character animation
        self._map_char_px: float = 0.0   # current rendered x pixel of explorer
        self._map_char_py: float = 0.0   # current rendered y pixel
        self._map_move_pending: str | None = None   # tile_type to open after walk anim

        # Scene
        self.scene_tile: str = ""
        self.scene_tile_pos: tuple = (2, 2)   # grid (x,y) of current scene
        self.scene_objects: list = []
        self.hover_obj: int = -1

        # Interaction
        self.selected_obj: dict | None = None
        self.hover_btn: int = -1

        # Popup queue
        self.popup_queue: list = []
        self.current_popup: dict | None = None

        # Book
        self.book_hover: int = -1
        self.book_detail = None
        self._book_entry_data: list = []
        self._book_rects: list = []

        # Skills
        self.skills_hover: int = -1

        # UI rects (rebuilt each draw)
        self._ui: dict = {}

        # Music
        self._music_enabled: bool = False
        self._current_track: str | None = None
        self._discovery_sfx: object = None  # pygame.mixer.Sound
        self._init_music()

        # Fonts
        self.fonts = scenes.load_fonts()

    # ── Music ─────────────────────────────────────────────────────────────────

    def _init_music(self):
        """Load music files if present; silently skip if missing."""
        from pathlib import Path
        if not pygame.mixer.get_init():
            return
        music_dir = Path(__file__).parent / "data" / "music"
        if not music_dir.exists():
            return
        if not list(music_dir.glob("music_*.wav")):
            return
        self._music_enabled = True
        # Discovery stinger (short one-shot sound, uses mixer channel not music channel)
        stinger = music_dir / "discovery_stinger.wav"
        if stinger.exists():
            try:
                self._discovery_sfx = pygame.mixer.Sound(str(stinger))
                self._discovery_sfx.set_volume(0.75)
            except Exception as e:
                print(f"[music] Could not load stinger: {e}")
        # Start exploration track immediately
        self._play_music("music_exploration")

    def _play_music(self, track_name: str):
        """Switch background music to track_name (no-op if already playing)."""
        if not self._music_enabled or track_name == self._current_track:
            return
        from pathlib import Path
        path = Path(__file__).parent / "data" / "music" / f"{track_name}.wav"
        if not path.exists():
            return
        try:
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.set_volume(0.45)
            pygame.mixer.music.play(-1)   # -1 = loop forever
            self._current_track = track_name
        except Exception as e:
            print(f"[music] Could not play {track_name}: {e}")

    # Maps tile_type → music track name (slugified to match file names)
    _TILE_MUSIC = {
        "Forest":       "music_forest",
        "River":        "music_river",
        "Clearing":     "music_clearing",
        "Dense Jungle": "music_dense_jungle",
        "Camp":         "music_camp",
    }

    def _update_music(self):
        """Called every frame; switches track based on current state and tile."""
        if not self._music_enabled:
            return
        if self.state in ("SCENE_OBJECTS", "SCENE_INTERACTIONS"):
            track = self._TILE_MUSIC.get(self.scene_tile, "music_exploration")
        else:
            track = "music_exploration"
        self._play_music(track)

    # ── Main loop ─────────────────────────────────────────────────────────────

    def run(self):
        while True:
            self.clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self._handle_event(event)
            self._draw()
            pygame.display.flip()

    # ── Event dispatcher ──────────────────────────────────────────────────────

    def _handle_event(self, event):
        if self.state == "TITLE":
            self._ev_title(event)
        elif self.state == "SETUP_NAME":
            self._ev_setup_name(event)
        elif self.state == "SETUP_AVATAR":
            self._ev_setup_avatar(event)
        elif self.state == "MAP":
            self._ev_map(event)
        elif self.state == "SCENE_OBJECTS":
            self._ev_scene_objects(event)
        elif self.state == "SCENE_INTERACTIONS":
            self._ev_scene_interactions(event)
        elif self.state == "POPUP":
            self._ev_popup(event)
        elif self.state == "BOOK":
            self._ev_book(event)
        elif self.state == "SKILLS":
            self._ev_skills(event)

    # ── Draw dispatcher ───────────────────────────────────────────────────────

    def _draw(self):
        self._update_music()
        if self.state == "TITLE":
            self._ui = scenes.draw_title(self.win, self.fonts)

        elif self.state == "SETUP_NAME":
            self._ui = scenes.draw_setup_name(self.win, self.fonts, self.name_input)

        elif self.state == "SETUP_AVATAR":
            self._ui = scenes.draw_setup_avatar(self.win, self.fonts,
                                                self.avatar_hover, self.avatar_selected)

        elif self.state == "MAP":
            # Lerp explorer toward the player's actual tile each frame
            tx_c, ty_c = self._tile_map_center(
                self.game_state.player.x, self.game_state.player.y)
            self._map_char_px += (tx_c - self._map_char_px) * 0.18
            self._map_char_py += (ty_c - self._map_char_py) * 0.18

            # Once close enough, trigger the pending scene open
            if self._map_move_pending:
                dist = (abs(tx_c - self._map_char_px) +
                        abs(ty_c - self._map_char_py))
                if dist < 3.0:
                    pending = self._map_move_pending
                    self._map_move_pending = None
                    self._open_scene(pending)
                    return   # state changed; skip MAP draw this frame

            self._ui = scenes.draw_map(
                self.win, self.fonts, self.game_state, self.hover_tile,
                player_anim=(int(self._map_char_px), int(self._map_char_py)),
            )
            self._tile_rects = self._ui.get("tiles", {})

        elif self.state == "SCENE_OBJECTS":
            tx, ty = self.scene_tile_pos
            self._ui = scenes.draw_scene_objects(
                self.win, self.fonts, self.scene_tile,
                self.scene_objects, self.hover_obj,
                self.game_state.player.items, self.game_state.items_db,
                tile_seed=tx * 7 + ty * 13 + 1,
            )

        elif self.state == "SCENE_INTERACTIONS":
            tx, ty = self.scene_tile_pos
            self._ui = scenes.draw_scene_interactions(
                self.win, self.fonts, self.scene_tile,
                self.selected_obj, self.game_state.player.items,
                self.game_state.items_db, self.hover_btn,
                tile_seed=tx * 7 + ty * 13 + 1,
                player_skills=self.game_state.player.skills,
            )

        elif self.state == "POPUP":
            if self.current_popup:
                scenes.draw_popup(self.win, self.fonts, self.current_popup)

        elif self.state == "BOOK":
            result = scenes.draw_book(
                self.win, self.fonts, self.game_state,
                self.game_state.discoveries_db,
                self.book_detail, self.book_hover,
            )
            self._ui = result
            self._book_rects = result.get("entries", [])
            self._book_entry_data = result.get("entry_data", [])

        elif self.state == "SKILLS":
            self._ui = scenes.draw_skills(self.win, self.fonts,
                                          self.game_state, self.skills_hover)

    # ── Title ─────────────────────────────────────────────────────────────────

    def _ev_title(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            start_btn = self._ui.get("start")
            if start_btn and start_btn.collidepoint(event.pos):
                self.state = "SETUP_NAME"
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.state = "SETUP_NAME"

    # ── Setup: Name ───────────────────────────────────────────────────────────

    def _ev_setup_name(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.name_input.strip():
                    self.state = "SETUP_AVATAR"
            elif event.key == pygame.K_BACKSPACE:
                self.name_input = self.name_input[:-1]
            else:
                ch = event.unicode
                if ch and len(self.name_input) < 20:
                    self.name_input += ch

    # ── Setup: Avatar ─────────────────────────────────────────────────────────

    def _ev_setup_avatar(self, event):
        btns = self._ui.get("btns", [])
        if event.type == pygame.MOUSEMOTION:
            self.avatar_hover = -1
            for i, r in enumerate(btns):
                if r.collidepoint(event.pos):
                    self.avatar_hover = i
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(btns):
                if r.collidepoint(event.pos):
                    self.avatar_selected = i
            confirm = self._ui.get("confirm")
            if confirm and confirm.collidepoint(event.pos) and self.avatar_selected >= 0:
                self._start_game()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            if self.avatar_selected >= 0:
                self._start_game()

    def _tile_map_center(self, tx: int, ty: int) -> tuple:
        """Pixel centre used to position the explorer sprite on a map tile."""
        return (
            scenes.MAP_OFFSET_X + tx * scenes.TILE_W + (scenes.TILE_W - 4) // 2,
            scenes.MAP_OFFSET_Y + ty * scenes.TILE_H + (scenes.TILE_H - 4) // 2 + 4,
        )

    def _start_game(self):
        avatar = AVATAR_OPTIONS[self.avatar_selected]
        world = game_map.build_world()
        discoveries_db = engine.load_discoveries()
        items_db = engine.load_items()
        player = Player(name=self.name_input.strip(), avatar=avatar)
        self.game_state = GameState(
            player=player,
            world=world,
            discoveries_db=discoveries_db,
            items_db=items_db,
        )
        scenes.set_player_ref(self.game_state.player)
        # Place explorer instantly at the starting tile (camp = 2, 2)
        self._map_char_px, self._map_char_py = self._tile_map_center(2, 2)
        self.state = "MAP"

    # ── Map ───────────────────────────────────────────────────────────────────

    def _ev_map(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover_tile = self._tile_at(event.pos)

        # Block tile clicks while the explorer is walking to a new tile
        if self._map_move_pending:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            clicked = self._tile_at(event.pos)
            if clicked:
                self._handle_map_click(clicked)

    def _tile_at(self, pos) -> tuple | None:
        for (tx, ty), rect in self._tile_rects.items():
            if rect.collidepoint(pos):
                return (tx, ty)
        return None

    def _is_adjacent(self, tx, ty) -> bool:
        px, py = self.game_state.player.x, self.game_state.player.y
        return abs(tx - px) + abs(ty - py) == 1

    def _handle_map_click(self, tile_pos):
        tx, ty = tile_pos
        px, py = self.game_state.player.x, self.game_state.player.y

        # Clicking own tile opens scene
        if tx == px and ty == py:
            self._open_scene(game_map.get_tile(self.game_state.world, px, py).tile_type)
            return

        # Must be adjacent to move
        if not self._is_adjacent(tx, ty):
            return

        # Move player
        direction = self._pos_to_dir(tx - px, ty - py)
        if not direction:
            return

        moved = game_map.move(self.game_state.player, self.game_state.world, direction)
        if not moved:
            return

        still_alive = engine.apply_move_cost(self.game_state)
        self._drain_to_popups(auto_open_tile=not still_alive)

        if not still_alive:
            # Teleported to camp; show popup then MAP
            return

        new_tile = game_map.get_tile(self.game_state.world, tx, ty)
        # Queue the scene — the explorer walks there first, then it opens
        self._map_move_pending = new_tile.tile_type

    def _pos_to_dir(self, dx, dy) -> str | None:
        return {(0, -1): "W", (0, 1): "S", (-1, 0): "A", (1, 0): "D"}.get((dx, dy))

    def _open_scene(self, tile_type: str):
        import json
        from pathlib import Path
        data_path = Path(__file__).parent / "data" / "scenes.json"
        with open(data_path, encoding="utf-8") as f:
            scenes_data = json.load(f)["scenes"]
        self.scene_tile = tile_type
        self.scene_tile_pos = (self.game_state.player.x, self.game_state.player.y)
        self.scene_objects = scenes_data.get(tile_type, {}).get("objects", [])
        self.hover_obj = -1
        self.state = "SCENE_OBJECTS"

    # ── Scene Objects ─────────────────────────────────────────────────────────

    def _ev_scene_objects(self, event):
        obj_rects = self._ui.get("objects", [])
        back_btn = self._ui.get("back")

        if event.type == pygame.MOUSEMOTION:
            self.hover_obj = -1
            for i, r in enumerate(obj_rects):
                if r.collidepoint(event.pos):
                    self.hover_obj = i

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if back_btn and back_btn.collidepoint(event.pos):
                self.state = "MAP"
                return
            for i, r in enumerate(obj_rects):
                if r.collidepoint(event.pos) and i < len(self.scene_objects):
                    self.selected_obj = self.scene_objects[i]
                    self.hover_btn = -1
                    self.state = "SCENE_INTERACTIONS"
                    return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = "MAP"

    # ── Scene Interactions ────────────────────────────────────────────────────

    def _ev_scene_interactions(self, event):
        if not self.selected_obj:
            self.state = "SCENE_OBJECTS"
            return

        btns = self._ui.get("btns", [])
        back_btn = self._ui.get("back")
        interactions = self.selected_obj.get("interactions", [])

        if event.type == pygame.MOUSEMOTION:
            self.hover_btn = -1
            for i, r in enumerate(btns):
                if r.collidepoint(event.pos):
                    self.hover_btn = i
            if back_btn and back_btn.collidepoint(event.pos):
                self.hover_btn = len(interactions)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if back_btn and back_btn.collidepoint(event.pos):
                self.state = "SCENE_OBJECTS"
                return
            for i, r in enumerate(btns):
                if r.collidepoint(event.pos):
                    self._handle_interaction_click(i)
                    return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = "SCENE_OBJECTS"

    def _handle_interaction_click(self, idx: int):
        interactions = self.selected_obj.get("interactions", [])
        if idx >= len(interactions):
            return

        inter = interactions[idx]
        action = inter["action"]
        params = inter.get("params", {})
        requires_item = inter.get("requires_item")

        # Item lock check
        if requires_item and requires_item not in self.game_state.player.items:
            hint_key = inter.get("hint_key")
            if hint_key:
                self.popup_queue.append({"kind": "message", "text": loc.t(hint_key),
                                         "tile_type": self.scene_tile})
            self._show_next_popup()
            return

        # Skill lock check
        requires_skill = inter.get("requires_skill")
        if requires_skill:
            skill_id, min_level_str = requires_skill.split(":")
            min_level   = int(min_level_str)
            actual_skill = self.game_state.player.skills.get(skill_id)
            if actual_skill is None or actual_skill.level < min_level:
                hint_key = inter.get("hint_key")
                if hint_key:
                    self.popup_queue.append({"kind": "message", "text": loc.t(hint_key),
                                             "tile_type": self.scene_tile})
                self._show_next_popup()
                return

        # Special actions
        if action == "close_scene":
            self.state = "MAP"
            return
        if action == "open_book":
            self.book_detail = None
            self.book_hover = -1
            self._prev_state = "SCENE_INTERACTIONS"
            self.state = "BOOK"
            return
        if action == "open_skills":
            self.skills_hover = -1
            self._prev_state = "SCENE_INTERACTIONS"
            self.state = "SKILLS"
            return

        # Engine action
        engine.process_action(action, params, self.game_state)

        secondary = inter.get("secondary_action")
        if secondary:
            engine.process_action(secondary, inter.get("secondary_params", {}), self.game_state)

        self._drain_to_popups()

    def _drain_to_popups(self, auto_open_tile: bool = False):
        """Convert engine message_queue into popup dicts and show the first."""
        for msg in self.game_state.message_queue:
            if isinstance(msg, tuple):
                kind = msg[0]
                if kind == "discovery_new":
                    _, disc, kg = msg
                    self.popup_queue.append({
                        "kind": "discovery_new", "discovery": disc,
                        "knowledge_gained": kg, "tile_type": self.scene_tile,
                    })
                    if self._discovery_sfx:
                        self._discovery_sfx.play()
                elif kind == "discovery_old":
                    _, disc, kg = msg
                    self.popup_queue.append({
                        "kind": "discovery_old", "discovery": disc,
                        "knowledge_gained": kg, "tile_type": self.scene_tile,
                    })
                elif kind == "item_found":
                    _, item = msg
                    self.popup_queue.append({
                        "kind": "item_found", "item": item,
                        "tile_type": self.scene_tile,
                    })
            else:
                self.popup_queue.append({
                    "kind": "message", "text": str(msg),
                    "tile_type": self.scene_tile,
                })
        self.game_state.message_queue.clear()
        self._show_next_popup()

    def _show_next_popup(self):
        if self.popup_queue:
            self.current_popup = self.popup_queue.pop(0)
            self._prev_state = self.state
            self.state = "POPUP"

    # ── Popup ─────────────────────────────────────────────────────────────────

    def _ev_popup(self, event):
        dismiss = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            dismiss = True
        if event.type == pygame.KEYDOWN:
            dismiss = True

        if dismiss:
            if self.popup_queue:
                self.current_popup = self.popup_queue.pop(0)
            else:
                self.current_popup = None
                self.state = getattr(self, "_prev_state", "MAP")

    # ── Book ──────────────────────────────────────────────────────────────────

    def _ev_book(self, event):
        if self.book_detail:
            # Any key/click dismisses detail
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                self.book_detail = None
            return

        back_btn = self._ui.get("back")
        entry_rects = self._book_rects
        entry_data  = self._book_entry_data

        if event.type == pygame.MOUSEMOTION:
            self.book_hover = -1
            for i, r in enumerate(entry_rects):
                if r.collidepoint(event.pos):
                    self.book_hover = i

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if back_btn and back_btn.collidepoint(event.pos):
                self.state = "MAP"
                return
            for i, r in enumerate(entry_rects):
                if r.collidepoint(event.pos) and i < len(entry_data):
                    self.book_detail = entry_data[i]
                    return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = "MAP"

    # ── Skills ────────────────────────────────────────────────────────────────

    def _ev_skills(self, event):
        back_btn = self._ui.get("back")
        skill_btns = self._ui.get("btns", [])
        skill_ids = ["explorer", "nature_friend", "survival_helper"]

        if event.type == pygame.MOUSEMOTION:
            self.skills_hover = -1
            for i, r in enumerate(skill_btns):
                if r.collidepoint(event.pos):
                    self.skills_hover = i

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if back_btn and back_btn.collidepoint(event.pos):
                self.state = getattr(self, "_prev_state", "MAP")
                self._prev_state = "MAP"
                return
            for i, r in enumerate(skill_btns):
                if r.collidepoint(event.pos):
                    engine.upgrade_skill(skill_ids[i], self.game_state)
                    self._drain_to_popups()
                    return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = getattr(self, "_prev_state", "MAP")
            self._prev_state = "MAP"


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    loc.load()

    # ── One-time asset generation ──────────────────────────────────────────────
    if not asset_generator.assets_complete():
        # Show a pygame loading window while generation runs in background
        pygame.init()
        win  = pygame.display.set_mode((scenes.W, scenes.H))
        pygame.display.set_caption("Amazon Rainforest Explorer — Preparing...")
        fonts = scenes.load_fonts()
        clock = pygame.time.Clock()

        # Shared state updated by the background thread
        gen_status = {"msg": "Starting...", "step": 0, "total": 5, "done": False, "error": None}

        def _run():
            try:
                def _prog(msg, step, total):
                    gen_status.update(msg=msg, step=step, total=max(total, 1))
                asset_generator.generate_all(_prog)
            except Exception as exc:
                gen_status["error"] = str(exc)
            gen_status["done"] = True

        t = threading.Thread(target=_run, daemon=True)
        t.start()

        while not gen_status["done"]:
            clock.tick(10)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            scenes.draw_loading_screen(
                win, fonts,
                gen_status["msg"],
                gen_status["step"],
                gen_status["total"],
            )
            pygame.display.flip()

        if gen_status["error"]:
            print(f"[main] Asset generation failed: {gen_status['error']}")
            print("[main] Continuing with procedural art.")
        pygame.quit()   # teardown so GameApp re-init is clean

    # ── Normal game startup ────────────────────────────────────────────────────
    app = GameApp()
    scenes.load_scene_images()      # scene backgrounds (data/images/)
    scenes.load_creature_images()   # journal portraits (data/images/creatures/)
    app.run()


if __name__ == "__main__":
    main()
