# `stash2fs scene mv` — single scene

Move one scene (and each of its files) to template-derived locations.

## Dependencies

- [`../_global.md`](../_global.md)
- [`../scene.md`](../scene.md)

Do **not** read `scene/bulk-mv.md`, `image/*`, or `gallery/*` for this task.

## CLI

```
stash2fs scene mv <ID> [--template-name NAME]
```

| Argument / option | Required | Description |
|---|---|---|
| `<ID>` | yes | Stash **scene** id (not file id). |
| `--template-name NAME` | no | Force a named entry from `templates.scene.by_tag`, `.by_studio`, or `.by_path` instead of auto-selection. |

Global options: see [`../_global.md`](../_global.md).

## Behavior

1. Resolve scene via `findScene(<ID>)`.
2. Run the shared move pipeline for each file on the scene.
3. Emit per-file lines + summary (see global output spec).
4. Respect `--dry-run` (no `moveFiles`).

Idempotent: destination equals current → `unchanged`.

## Implementation notes

- Register under `click` group `scene`, command name `mv`.
- Reuse `core.mover.process_item(client, settings, "scene", id)` (or equivalent) so the
  plugin hook can call the same function.

## Acceptance criteria

- [ ] `stash2fs scene mv <valid-id>` moves all scene files via `moveFiles` (one call per file).
- [ ] `--dry-run` prints plans; zero `moveFiles` calls.
- [ ] `--template-name` forces the named override when it exists; error if name not found.
- [ ] Invalid/missing scene id → exit `1`.
- [ ] Scene with no files → skip + warn; exit `0`.
- [ ] Multi-file scene: each file gets its own destination basename.
- [ ] Output lines match global format with `type=scene`.

## Examples

```bash
stash2fs scene mv 1234
stash2fs scene mv 1234 --dry-run
stash2fs scene mv 1234 --template-name rename_tag
```
