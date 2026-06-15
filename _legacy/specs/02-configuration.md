# 02 — Configuration

Configuration is managed with
`[pydantic-settings](https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings)`.

## Sources and precedence

Highest priority wins (D10):

1. **CLI arguments / options** (standalone mode; per-invocation overrides).
2. **Stash plugin UI settings** (plugin mode; read from Stash configuration — see below).
3. **Environment variables** (prefix `STASH2FS_`).
4. `**config.py` defaults** — the in-repo default values.

Implementers MUST implement this as an explicit settings-merge with a documented order,
not rely on `pydantic-settings` source ordering alone (because source #2 is dynamic and
only present in plugin mode, and #1 is only present in CLI mode).

Recommended approach:

- Define a `Settings(BaseSettings)` whose defaults live in `config/config.py` and whose env
source uses `env_prefix="STASH2FS_"` and nested delimiter `__`.
- In CLI mode: build `Settings`, then apply non-`None` CLI option overrides on top.
- In plugin mode: build `Settings`, then overlay plugin UI settings fetched from Stash,
ordered below CLI but above env (note: CLI options are absent in plugin mode, so effective
order there is plugin UI > env > defaults).



Templates (per media type: `scene`, `image`, `gallery`). See `[04-templating.md](./04-templating.md)`:


Logging:


| Setting              | Env                            | Type | Default                      |
| -------------------- | ------------------------------ | ---- | ---------------------------- |
| `log.level`          | `STASH2FS_LOG__LEVEL`          | enum | `INFO`                       |
| `log.dry_run_report` | `STASH2FS_LOG__DRY_RUN_REPORT` | path | `None` (optional file of `id |


## Validation rules

- `stash.url` MUST be a valid http(s) URL.
- Each media type MUST have a non-empty `default` template, else the corresponding `mv`
command/hook fails fast with a clear error.
- `on_collision` MUST reject any value other than `skip` in v1 (forward-compatible enum).
- Unknown env vars under the prefix SHOULD be ignored (not error) to ease forward compat.

## Example `config.py` defaults (illustrative)

```python
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class StashConn(BaseSettings):
    url: str = "http://localhost:9999"
    api_key: SecretStr | None = None
    timeout_seconds: int = 30


class TypeTemplates(BaseSettings):
    default: str
    by_tag: dict[str, str] = {}
    by_studio: dict[str, str] = {}
    by_path: dict[str, str] = {}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="STASH2FS_", env_nested_delimiter="__")

    stash: StashConn = StashConn()
    dry_run: bool = False
    enabled: bool = True
    on_collision: str = "skip"
    validate_library_paths: bool = True
    # templates.* provided per type; see 04-templating.md
```

The exact class names are at the implementer's discretion; the **setting names, defaults,
env var names, and precedence above are normative.**
