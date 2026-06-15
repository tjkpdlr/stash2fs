# `stash2fs gallery mv --all` — bulk galleries

Move many galleries matching optional filters.

## Dependencies

- [`../_global.md`](../_global.md)
- [`../gallery.md`](../gallery.md)
- Per-item: [`mv.md`](./mv.md)

## CLI

```
stash2fs gallery mv --all [--tag NAME]... [--studio NAME]... [--path-prefix PREFIX]...
                      [--organized | --unorganized]
```

Filter semantics: same as [`../scene/bulk-mv.md`](../scene/bulk-mv.md).

## Behavior

1. `findGalleries(filter)` with pagination.
2. Per gallery: pipeline from [`mv.md`](./mv.md) (folder galleries skipped individually).
3. Progress + summary.

## Acceptance criteria

- [ ] Bulk processes all matching galleries.
- [ ] Folder galleries counted as skipped (not failed).
- [ ] Zip galleries moved when filters match.

## Examples

```bash
stash2fs gallery mv --all --unorganized --path-prefix /incoming
```
