"""Pydantic settings models and explicit precedence merge."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Literal

from pydantic import Field, HttpUrl, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from stash2fs.config.config import DEFAULTS

MediaType = Literal["scene", "image", "gallery"]
OnCollision = Literal["skip"]
PathSeparator = Literal["auto", "/", "\\"]
LogLevel = Literal["TRACE", "DEBUG", "INFO", "WARNING", "ERROR"]


class StashConn(BaseSettings):
    url: str = DEFAULTS["stash"]["url"]  # type: ignore[index]
    api_key: SecretStr | None = None
    timeout_seconds: int = DEFAULTS["stash"]["timeout_seconds"]  # type: ignore[index]

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        HttpUrl(v)
        return v.rstrip("/")


class TypeTemplates(BaseSettings):
    default: str
    by_tag: dict[str, str] = Field(default_factory=dict)
    by_studio: dict[str, str] = Field(default_factory=dict)
    by_path: dict[str, str] = Field(default_factory=dict)

    @field_validator("default")
    @classmethod
    def default_non_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("template default must be non-empty")
        return v


class LogSettings(BaseSettings):
    level: LogLevel = "INFO"
    dry_run_report: Path | None = None


def _default_templates() -> dict[str, TypeTemplates]:
    raw = DEFAULTS["templates"]
    assert isinstance(raw, dict)
    return {
        media_type: TypeTemplates.model_validate(values)
        for media_type, values in raw.items()
    }


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="STASH2FS_",
        env_nested_delimiter="__",
        extra="ignore",
    )

    stash: StashConn = Field(default_factory=StashConn)
    dry_run: bool = False
    enabled: bool = True
    on_collision: OnCollision = "skip"
    validate_library_paths: bool = True
    path_separator: PathSeparator = "auto"
    templates: dict[str, TypeTemplates] = Field(default_factory=_default_templates)
    log: LogSettings = Field(default_factory=LogSettings)

    @field_validator("on_collision")
    @classmethod
    def only_skip(cls, v: str) -> str:
        if v != "skip":
            raise ValueError("on_collision only supports 'skip' in v1")
        return v

    def get_type_templates(self, media_type: MediaType) -> TypeTemplates:
        if media_type not in self.templates:
            raise ValueError(f"missing default template for media type '{media_type}'")
        return self.templates[media_type]


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge overlay onto base; overlay wins for scalars."""
    result = dict(base)
    for key, value in overlay.items():
        if value is None:
            continue
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _load_config_file(path: Path) -> dict[str, Any]:
    """Load a Python config file and extract settings dict."""
    spec = importlib.util.spec_from_file_location("stash2fs_user_config", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot load config file: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if hasattr(module, "SETTINGS"):
        data = module.SETTINGS
        if not isinstance(data, dict):
            raise ValueError("config file SETTINGS must be a dict")
        return data
    # Collect module-level overrides matching Settings fields
    keys = {
        "stash",
        "dry_run",
        "enabled",
        "on_collision",
        "validate_library_paths",
        "path_separator",
        "templates",
        "log",
    }
    return {k: getattr(module, k) for k in keys if hasattr(module, k)}


def _flatten_overrides(overrides: dict[str, Any] | None) -> dict[str, Any]:
    if not overrides:
        return {}
    return {k: v for k, v in overrides.items() if v is not None}


def build_settings(
    *,
    config_path: Path | None = None,
    cli_overrides: dict[str, Any] | None = None,
    plugin_overrides: dict[str, Any] | None = None,
) -> Settings:
    """Build effective settings with precedence: CLI > plugin > env > file > defaults.

    pydantic-settings handles env vars; we layer file/plugin/cli on top explicitly.
    """
    base_dict: dict[str, Any] = Settings().model_dump()

    if config_path is not None:
        file_data = _load_config_file(config_path)
        base_dict = _deep_merge(base_dict, file_data)

    # Re-read from env on top of defaults/file
    env_settings = Settings()
    base_dict = _deep_merge(base_dict, env_settings.model_dump())

    plugin = _flatten_overrides(plugin_overrides)
    if plugin:
        base_dict = _deep_merge(base_dict, plugin)

    cli = _flatten_overrides(cli_overrides)
    if cli:
        base_dict = _deep_merge(base_dict, cli)

    return Settings.model_validate(base_dict)


def plugin_ui_to_overrides(plugin_settings: dict[str, Any]) -> dict[str, Any]:
    """Map Stash plugin UI settings keys to Settings fields."""
    overrides: dict[str, Any] = {}
    if "enabled" in plugin_settings:
        overrides["enabled"] = plugin_settings["enabled"]
    if "dryRun" in plugin_settings:
        overrides["dry_run"] = plugin_settings["dryRun"]
    return overrides
