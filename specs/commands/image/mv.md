# `stash2fs image mv` — single image

Move one image (each visual file) to template-derived locations.

## Dependencies

- [`../_global.md`](../_global.md)
- [`../image.md`](../image.md)

## CLI

```
stash2fs image mv <ID> [--template-name NAME]
```

| Argument / option | Required | Description |
|---|---|---|
| `<ID>` | yes | Stash **image** id. |
| `--template-name NAME` | no | Force named override from `templates.image`. |

## Behavior

Same as [`scene/mv.md`](./scene/mv.md) but `findImage`, `visual_files`, `type=image`.

## Acceptance criteria

- [ ] `stash2fs image mv <valid-id>` moves all visual files via `moveFiles`.
- [ ] `--dry-run` → plans only.
- [ ] `--template-name` behavior matches scene mv.
- [ ] No visual files → skip + warn; exit `0`.
- [ ] Output uses `type=image`.

## Examples

```bash
stash2fs image mv 5678 --dry-run
```
