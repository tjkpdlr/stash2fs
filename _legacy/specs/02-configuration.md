# 02 — Configuration

Configuration is managed with
[`pydantic-settings`](https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings).

## Sources and precedence

Highest priority wins (D10):

1. **CLI arguments / options** (standalone mode; per-invocation overrides).
2. **Stash plugin UI settings** (plugin mode; read from Stash configuration — see below).
3. **Environment variables** (prefix `STASH2FS_`).
4. **`config.py` defaults** — the in-repo default values.

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

## Stash plugin UI settings

- Settings exposed to the Stash UI MUST be declared in the plugin `.yml` `settings:` block
  (see [`06-plugin.md`](./06-plugin.md)).
- At runtime the plugin reads their values via the GraphQL `configuration` query
  (`configuration.plugins` keyed by the plugin id) and maps them onto `Settings`.
- Keep the UI-exposed subset small (connection is provided by Stash itself in plugin mode):
  at minimum `dry_run`, `enabled`, and the active template selection.

## Settings reference

Connection (used in standalone mode; in plugin mode the connection comes from the plugin
`FRAGMENT["server_connection"]` and overrides these):

| Setting | Env | Type | Default | Notes |
|---|---|---|---|---|
| `stash.url` | `STASH2FS_STASH__URL` | str (URL) | `http://localhost:9999` | Base URL; `/graphql` appended. |
| `stash.api_key` | `STASH2FS_STASH__API_KEY` | secret str | `None` | Sent as `ApiKey` header when set. |
| `stash.timeout_seconds` | `STASH2FS_STASH__TIMEOUT_SECONDS` | int | `30` | Per-request timeout. |

Behavior:

| Setting | Env | Type | Default | Notes |
|---|---|---|---|---|
| `dry_run` | `STASH2FS_DRY_RUN` | bool | `false` | Compute & log plans, never call `moveFiles`. |
| `enabled` | `STASH2FS_ENABLED` | bool | `true` | Plugin hooks respect this; CLI ignores it. |
| `on_collision` | `STASH2FS_ON_COLLISION` | enum | `skip` | v1 supports only `skip` (skip + log). |
| `validate_library_paths` | `STASH2FS_VALIDATE_LIBRARY_PATHS` | bool | `true` | Skip + log destinations outside library paths. |
| `path_separator` | `STASH2FS_PATH_SEPARATOR` | enum(`auto`,`/`,`\\`) | `auto` | Normalization for rendered paths. |

Templates (per media type: `scene`, `image`, `gallery`). See [`04-templating.md`](./04-templating.md):

| Setting | Type | Default | Notes |
|---|---|---|---|
| `templates.<type>.default` | str (Jinja2) | required | Full destination path template. |
| `templates.<type>.by_tag` | dict[str, str] | `{}` | tag name → template. |
| `templates.<type>.by_studio` | dict[str, str] | `{}` | studio name → template. |
| `templates.<type>.by_path` | dict[str, str] | `{}` | source-path prefix → template. |

Logging:

| Setting | Env | Type | Default |
|---|---|---|---|
| `log.level` | `STASH2FS_LOG__LEVEL` | enum | `INFO` |
| `log.dry_run_report` | `STASH2FS_LOG__DRY_RUN_REPORT` | path | `None` (optional file of `id\|from\|to`) |

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
