"""CLI tests using CliRunner and mocked client."""

from __future__ import annotations

from click.testing import CliRunner

from stash2fs.cli.main import cli
from conftest import FakeStashClient


def test_cli_help() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "scene" in result.output or "Organize" in result.output


def test_scene_mv_dry_run(monkeypatch) -> None:
    runner = CliRunner()

    def fake_client_init(*args, **kwargs):
        return FakeStashClient()

    monkeypatch.setattr("stash2fs.cli.main.HttpStashClient", fake_client_init)

    result = runner.invoke(cli, ["--dry-run", "scene", "mv", "100"])
    assert result.exit_code == 0
    assert "DRY-RUN" in result.output or "MOVE" in result.output
    assert "Summary:" in result.output


def test_missing_id_and_all_exits_1(monkeypatch) -> None:
    runner = CliRunner()
    monkeypatch.setattr("stash2fs.cli.main.HttpStashClient", lambda *a, **k: FakeStashClient())
    result = runner.invoke(cli, ["scene", "mv"])
    assert result.exit_code == 1
