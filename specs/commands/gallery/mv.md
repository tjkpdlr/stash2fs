# `stash2fs gallery mv` — single gallery

Move one zip-backed gallery file to a template-derived location.

## Dependencies

- [`../_global.md`](../_global.md)
- [`../gallery.md`](../gallery.md)

## CLI

```
stash2fs gallery mv <ID> [--template-name NAME]
```

| Argument / option | Required | Description |
|---|---|---|
| `<ID>` | yes | Stash **gallery** id. |
| `--template-name NAME` | no | Force named override from `templates.gallery`. |

## Behavior

1. `findGallery(<ID>)`.
2. If folder-based gallery → skip + warn (see [`../gallery.md`](../gallery.md)); exit `0`.
3. Else run move pipeline on the zip file(s).
4. Respect dry-run.

## Acceptance criteria

- [ ] Zip gallery moves via `moveFiles`.
- [ ] Folder gallery skipped with documented warning; no filesystem changes.
- [ ] `--dry-run` → plans only.
- [ ] Output uses `type=gallery`.

## Examples

```bash
stash2fs gallery mv 99 --dry-run
```
