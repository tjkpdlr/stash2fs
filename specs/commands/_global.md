# Global CLI behavior

Applies to all `stash2fs <type> <action>` commands unless a command spec overrides.

## Entrypoint

- Console: `stash2fs` (`click`, via `uv run stash2fs` / `python -m stash2fs`).
- Tree: `stash2fs [GLOBAL OPTIONS] <scene|image|gallery> <action> [ARGS]`.

## Global options

Override config (highest precedence). All optional.

| Option | Setting | Notes |
|---|---|---|
| `--stash-url URL` | `stash.url` | |
| `--api-key KEY` | `stash.api_key` | Prefer env `STASH2FS_STASH__API_KEY`. |
| `--dry-run / --no-dry-run` | `dry_run` | Plan only; no `moveFiles`. |
| `--config PATH` | — | Alternate config module. |
| `-v, --verbose` | `log.level` | `-v`=DEBUG, `-vv`=more verbose. |
| `--log-level LEVEL` | `log.level` | Explicit alternative. |

Precedence: **CLI > plugin UI > env (`STASH2FS_*`) > `config.py` defaults.**  
CLI MUST ignore the `enabled` setting (plugin-only).

## Shared move pipeline (all `mv` commands)

For each targeted **item** (scene/image/gallery id):

1. Fetch item + files via GraphQL.
2. For **each file** on the item:
   - Build render context; select template (`tag > studio > path > default`).
   - Render full path (Jinja2); split into `destination_folder` + `destination_basename`;
     re-append original extension.
   - Validate (below).
   - Unless dry-run: `moveFiles` with **one file id** per call.

`moveFiles` is the only mutation. We never move files or touch SQLite directly.  
Details: [`../03-stash-integration.md`](../03-stash-integration.md) (read only if
implementing the Stash client or mover).

## Validation (per file plan)

Skip + log unless noted:

1. Template present and non-empty.
2. Rendered destination is absolute.
3. `destination_folder` inside a Stash library path (default on).
4. Destination equals current path → `unchanged` (debug).
5. Another file already at destination → collision skip.

Only passing plans call `moveFiles`. One failure must not abort a bulk run.

## Output

One line per outcome:

```
MOVE <id> <type>: <from> -> <to> [template=<name> reason=<tag|studio|path|default>]
```

- Dry-run prefix: `DRY-RUN`.
- Skips/failures include reason (collision, outside-library, etc.).

End-of-run summary: `moved`, `unchanged`, `skipped`, `failed`.

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Completed (skips OK). |
| `1` | Usage/config/connection error. |
| `2` | Completed with one or more move failures. |

## Templating (summary)

- Jinja2; one template → full path → split folder/basename.
- Config: `templates.<type>.default`, `.by_tag`, `.by_studio`, `.by_path`.
- Selection: tag > studio > source-path (longest prefix) > default.

Full variable list and filters: [`../04-templating.md`](../04-templating.md) — read only
when changing templating, not when wiring a command.

## Further reading (on demand)

| Topic | File |
|---|---|
| Settings / env vars | [`../02-configuration.md`](../02-configuration.md) |
| GraphQL queries + `moveFiles` | [`../03-stash-integration.md`](../03-stash-integration.md) |
| Validation / dry-run details | [`../08-error-handling-logging.md`](../08-error-handling-logging.md) |
