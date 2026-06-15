"""Build Stash connection from settings or plugin FRAGMENT."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydantic import SecretStr

from stash2fs.config.settings import Settings


@dataclass(frozen=True)
class StashConnection:
    url: str
    api_key: SecretStr | None = None
    session_cookie: str | None = None
    timeout_seconds: int = 30


def from_settings(settings: Settings) -> StashConnection:
    return StashConnection(
        url=f"{settings.stash.url.rstrip('/')}/graphql",
        api_key=settings.stash.api_key,
        timeout_seconds=settings.stash.timeout_seconds,
    )


def from_fragment(server_connection: dict[str, Any]) -> StashConnection:
    scheme = server_connection.get("Scheme", "http")
    host = server_connection.get("Host", "localhost")
    if host == "0.0.0.0":
        host = "localhost"
    port = server_connection.get("Port", 9999)
    cookie_obj = server_connection.get("SessionCookie") or {}
    cookie = cookie_obj.get("Value") if isinstance(cookie_obj, dict) else None
    url = f"{scheme}://{host}:{port}/graphql"
    return StashConnection(url=url, session_cookie=cookie)
