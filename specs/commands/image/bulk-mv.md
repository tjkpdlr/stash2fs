# `stash2fs image mv --all` — bulk images

Move many images matching optional filters.

## Dependencies

- [`../_global.md`](../_global.md)
- [`../image.md`](../image.md)
- Per-item: [`mv.md`](./mv.md)

## CLI

```
stash2fs image mv --all [--tag NAME]... [--studio NAME]... [--path-prefix PREFIX]...
                    [--organized | --unorganized]
```

Filter semantics: same as [`../scene/bulk-mv.md`](../scene/bulk-mv.md).

## Behavior

1. `findImages(filter)` with pagination.
2. Per image: pipeline from [`mv.md`](./mv.md).
3. Progress + summary.

## Acceptance criteria

- [ ] Parity with scene bulk-mv behavior, scoped to images.
- [ ] Uses `findImages` and `visual_files` resolution.

## Examples

```bash
stash2fs image mv --all --studio "Blender Institute" --dry-run
```
