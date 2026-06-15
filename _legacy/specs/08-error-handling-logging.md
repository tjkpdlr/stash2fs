# 08 — Error Handling, Validation, Logging & Dry-run

## Validation (before any move)

For each candidate `MovePlan`, in order:

1. **Template present** — the selected/default template exists and is non-empty. Missing →
  fail the item (usage/config error). In bulk, log error and continue.
2. **Rendered destination is absolute** — else skip + log.
3. **Library-path containment** (when `validate_library_paths` is true, default) —
  `destination_folder` MUST equal or be a descendant of a configured Stash library path
   (`configuration.general.stashes[].path`). Otherwise **skip + log**
   (`skipped: destination outside library paths: <folder>`). Rationale: `moveFiles` would
   reject it anyway; we pre-empt with a clear message.
4. **No-op** — destination equals current path → `unchanged`, skip (debug).
5. **Collision** — if a different file already exists at the destination path, **skip + log**
  (`on_collision = skip`, the only v1 strategy). Detection: prefer querying Stash for a file
   at the destination path; a filesystem stat is acceptable only when the path is locally
   reachable. Document the chosen detection method.

Only plans passing all checks proceed to `moveFiles`.

## Failure semantics

- A `moveFiles` GraphQL error or `false` return = **failed** move for that file: log at
error with file id, from, to, and the error. Continue with remaining files/items.
- Connection/auth errors at startup = fatal: exit `1` (CLI) / clean error log (plugin).
- One item's failure MUST never abort a bulk run.
- CLI exit code is `2` if any move failed (see `[05](./05-cli.md)`); `0` if only skips.

## Run summary

At the end of every run (CLI and plugin bulk), emit a summary with counts:
`moved`, `unchanged`, `skipped` (by reason), `failed`.

## Logging

Two contexts, one logical interface:

- **CLI:** use Python `logging` to stderr; `--verbose`/`--log-level` control level; concise
human-readable lines as in `[05](./05-cli.md)`. stdout reserved for primary output.
- **Plugin:** use Stash's stderr protocol — each message prefixed with `SOH (\x01)` + level
char + `STX (\x02)`:
  - `t` trace, `d` debug, `i` info, `w` warning, `e` error, `p` progress (a float 0..1).
  - Mirror `references/.../renamerOnUpdate/log.py`.

Implement a small logging adapter so `core/` code logs through one API and the entrypoint
selects the sink (Python logging vs Stash protocol). Never log secrets (API key, cookies).

### Progress

- Bulk runs MUST report progress: CLI via a counter/progress line; plugin via `LogProgress`
(0..1) at a reasonable cadence.

## Dry-run

- When `dry_run` is true, compute everything (resolve, render, validate) but **do not** call
`moveFiles`.
- Emit one line per planned move prefixed `DRY-RUN`:
`DRY-RUN MOVE <id> <type>: <from> -> <to> [template=<name> reason=<...>]`.
- If `log.dry_run_report` path is set, also append/write lines `id|from|to` to that file
(overwrite at start of run unless an append option is added later). This mirrors
renamerOnUpdate's dry-run file feature.
- Skips and would-be failures (e.g. outside library path) MUST also be reported in dry-run so
users can fix configuration before a real run.

