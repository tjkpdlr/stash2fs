# `stash2fs scene mv --all` — bulk scenes

Move many scenes matching optional filters.

## Dependencies

- [`../_global.md`](../_global.md)
- [`../scene.md`](../scene.md)

Per-item logic is identical to [`mv.md`](./mv.md). Do **not** re-read image/gallery specs.

## CLI

```
stash2fs scene mv --all [--tag NAME]... [--studio NAME]... [--path-prefix PREFIX]...
                    [--organized | --unorganized]
```

`--all` is required for bulk mode (mutually exclusive with positional `<ID>`).

| Filter | Repeatable | Semantics |
|---|---|---|
| `--tag NAME` | yes | Item has tag NAME |
| `--studio NAME` | yes | Item studio (or ancestor) matches |
| `--path-prefix PREFIX` | yes | Current file path starts with PREFIX |
| `--organized` | no | `organized == true` |
| `--unorganized` | no | `organized == false` |

Filters: **AND** across categories; **OR** within repeated options of the same flag.

## Behavior

1. Query all matching scenes via `findScenes(filter)` (paginate to completion).
2. For each scene, run the same pipeline as [`mv.md`](./mv.md).
3. Stream progress (current/total or similar).
4. One failure must not stop the batch.
5. Final summary: moved / unchanged / skipped / failed.

## Acceptance criteria

- [ ] `--all` without `<ID>` processes every matching scene.
- [ ] Filters narrow results as specified; empty result set → exit `0` with zero moves.
- [ ] Progress output during run; summary at end.
- [ ] `--dry-run` applies to entire batch.
- [ ] Any `moveFiles` failure → exit `2` after summary.
- [ ] Combines correctly with global `--dry-run`, `--stash-url`, etc.

## Examples

```bash
stash2fs scene mv --all --dry-run
stash2fs scene mv --all --studio "Blender Institute" --unorganized
stash2fs scene mv --all --tag wip --path-prefix /incoming
```
