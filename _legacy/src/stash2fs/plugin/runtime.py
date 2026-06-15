"""Stash plugin runtime."""

from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path
from typing import Any

from stash2fs.config.settings import build_settings, plugin_ui_to_overrides
from stash2fs.core.models import BulkFilters, Item, MediaType
from stash2fs.core.mover import (
    PLUGIN_ID,
    format_outcome_line,
    process_bulk,
    process_item,
    summarize,
)
from stash2fs.logging import configure_logging, get_logger
from stash2fs.plugin.io import StashLogSink, read_fragment
from stash2fs.stash.connection import from_fragment
from stash2fs.stash.queries import HttpStashClient, StashError

TYPE_MAP: dict[str, MediaType] = {
    "Scene": "scene",
    "Image": "image",
    "Gallery": "gallery",
}


def _state_file(plugin_dir: str) -> Path:
    return Path(plugin_dir) / "stash2fs_state.json"


def _load_state(plugin_dir: str) -> dict[str, Any]:
    path = _state_file(plugin_dir)
    if path.exists():
        loaded: dict[str, Any] = json.loads(path.read_text())
        return loaded
    return {}


def _save_state(plugin_dir: str, state: dict[str, Any]) -> None:
    _state_file(plugin_dir).write_text(json.dumps(state, indent=2))


def _persist_toggle(
    client: HttpStashClient,
    plugin_dir: str,
    key: str,
    value: bool,
) -> None:
    try:
        client.set_plugin_setting(PLUGIN_ID, key, value)
    except StashError:
        state = _load_state(plugin_dir)
        state[key] = value
        _save_state(plugin_dir, state)


def _load_plugin_settings(client: HttpStashClient, plugin_dir: str) -> dict[str, Any]:
    try:
        ui = client.get_plugin_settings(PLUGIN_ID)
        if ui:
            return ui
    except StashError:
        pass
    return _load_state(plugin_dir)


def main() -> None:
    configure_logging(StashLogSink())
    log = get_logger()

    try:
        fragment = read_fragment()
        server_connection = fragment.get("server_connection") or {}
        if not isinstance(server_connection, dict):
            raise ValueError("invalid server_connection in FRAGMENT")
        plugin_dir = str(server_connection.get("PluginDir", ""))
        args = fragment.get("args") or {}
        if not isinstance(args, dict):
            args = {}

        connection = from_fragment(server_connection)
        client = HttpStashClient(connection)

        ui_settings = _load_plugin_settings(client, plugin_dir)
        plugin_overrides = plugin_ui_to_overrides(ui_settings)
        state = _load_state(plugin_dir)
        for key in ("enabled", "dry_run"):
            if key in state and key not in plugin_overrides:
                ui_key = "dryRun" if key == "dry_run" else key
                if ui_key not in ui_settings:
                    plugin_overrides[key if key != "dry_run" else "dry_run"] = state[key]

        settings = build_settings(plugin_overrides=plugin_overrides)
        mode = args.get("mode")
        hook_context = args.get("hookContext")

        if mode == "enable":
            _persist_toggle(client, plugin_dir, "enabled", True)
            log.info("stash2fs enabled")
            return
        if mode == "disable":
            _persist_toggle(client, plugin_dir, "enabled", False)
            log.info("stash2fs disabled")
            return
        if mode == "dryrun":
            new_value = not settings.dry_run
            _persist_toggle(client, plugin_dir, "dryRun", new_value)
            log.info(f"dry_run={'on' if new_value else 'off'}")
            return
        if mode == "bulk":
            _run_bulk(client, settings, log)
            return

        if hook_context and isinstance(hook_context, dict):
            if not settings.enabled:
                log.info("stash2fs disabled; skipping hook")
                return
            entity_type = hook_context.get("type")
            entity_id = hook_context.get("id")
            hook_media_type = TYPE_MAP.get(str(entity_type))
            if hook_media_type is None or not entity_id:
                log.warning(f"unrecognized hook context: {hook_context}")
                return
            outcomes = process_item(client, settings, hook_media_type, str(entity_id))
            for outcome in outcomes:
                log.info(format_outcome_line(outcome, dry_run=settings.dry_run))
            summary = summarize(outcomes)
            log.info(
                f"Summary: moved={summary.moved} unchanged={summary.unchanged} "
                f"skipped={summary.skipped} failed={summary.failed}"
            )
            return

        log.warning(f"unknown plugin invocation: {args}")

    except Exception:
        log.error(traceback.format_exc())
        sys.exit(0)
    finally:
        if "client" in locals():
            client.close()


def _run_bulk(client: HttpStashClient, settings: Any, log: Any) -> None:
    all_outcomes = []
    types = ["scene", "image", "gallery"]
    for type_index, media_type in enumerate(types):
        def progress(current: int, total: int, item: Any, idx: int = type_index) -> None:
            overall = (idx + (current / max(total, 1))) / len(types)
            log.progress(overall)

        outcomes = process_bulk(
            client,
            settings,
            media_type,  # type: ignore[arg-type]
            BulkFilters(),
            progress_callback=progress,
        )
        all_outcomes.extend(outcomes)
        for outcome in outcomes:
            log.info(format_outcome_line(outcome, dry_run=settings.dry_run))

    summary = summarize(all_outcomes)
    log.info(
        f"Summary: moved={summary.moved} unchanged={summary.unchanged} "
        f"skipped={summary.skipped} failed={summary.failed}"
    )
