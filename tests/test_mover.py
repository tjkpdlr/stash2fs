"""Integration tests for mover with fake client."""

from stash2fs.config.settings import build_settings
from stash2fs.core.mover import process_item, summarize
from conftest import FakeStashClient


def test_dry_run_never_calls_move_file() -> None:
    client = FakeStashClient()
    settings = build_settings(cli_overrides={"dry_run": True})
    outcomes = process_item(client, settings, "scene", "100")
    assert client.move_calls == []
    assert any(o.status == "moved" for o in outcomes)


def test_move_calls_move_file_per_file() -> None:
    client = FakeStashClient()
    settings = build_settings(cli_overrides={"dry_run": False})
    outcomes = process_item(client, settings, "scene", "100")
    assert len(client.move_calls) == 1
    assert client.move_calls[0]["file_id"] == "f1"
    assert client.move_calls[0]["destination_basename"].endswith(".mp4")
    summary = summarize(outcomes)
    assert summary.moved == 1
    assert summary.skipped == 1


def test_folder_gallery_skipped() -> None:
    client = FakeStashClient()
    settings = build_settings()
    outcomes = process_item(client, settings, "gallery", "301")
    assert client.move_calls == []
    assert outcomes[0].status == "skipped"
    assert "folder-based" in outcomes[0].reason


def test_zip_gallery_moves() -> None:
    client = FakeStashClient()
    settings = build_settings(cli_overrides={"dry_run": False})
    process_item(client, settings, "gallery", "300")
    assert len(client.move_calls) == 1
    assert client.move_calls[0]["file_id"] == "gf1"


def test_collision_skips_move() -> None:
    client = FakeStashClient(
        existing_paths={"/media/library/Blender Institute/2008-05-20 - Big Buck Bunny.mp4"}
    )
    settings = build_settings(cli_overrides={"dry_run": False})
    outcomes = process_item(client, settings, "scene", "100")
    assert client.move_calls == []
    assert any(o.status == "skipped" for o in outcomes)
