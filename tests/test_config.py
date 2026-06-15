"""Tests for configuration settings."""

import pytest

from stash2fs.config.settings import Settings, build_settings


def test_defaults_load() -> None:
    settings = build_settings()
    assert settings.stash.url == "http://localhost:9999"
    assert settings.dry_run is False
    assert settings.get_type_templates("scene").default


def test_env_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("STASH2FS_DRY_RUN", "true")
    monkeypatch.setenv("STASH2FS_STASH__URL", "http://stash:8080")
    settings = build_settings()
    assert settings.dry_run is True
    assert settings.stash.url == "http://stash:8080"


def test_precedence_cli_beats_plugin_beats_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("STASH2FS_DRY_RUN", "false")
    settings = build_settings(
        plugin_overrides={"dry_run": True},
        cli_overrides={"dry_run": False},
    )
    assert settings.dry_run is False

    settings2 = build_settings(plugin_overrides={"dry_run": True})
    assert settings2.dry_run is True


def test_invalid_url() -> None:
    with pytest.raises(ValueError):
        Settings(stash={"url": "not-a-url", "timeout_seconds": 30})


def test_on_collision_rejects_non_skip() -> None:
    with pytest.raises(ValueError):
        build_settings(cli_overrides={"on_collision": "overwrite"})


def test_api_key_not_in_repr() -> None:
    settings = build_settings(cli_overrides={"stash": {"api_key": "secret123"}})
    assert "secret123" not in repr(settings)
    assert "secret123" not in settings.model_dump_json()
