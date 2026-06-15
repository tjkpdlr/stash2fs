# Command group: `stash2fs image`

Media type **`image`**. Shared by `image mv` and `image mv --all`.

## Dependencies

- [`_global.md`](./_global.md) — CLI globals, move pipeline, validation, output.

## GraphQL

- Single item: `findImage(id)`.
- Bulk listing: `findImages(filter)` with pagination.

Minimum fields: `id, title, date, rating100, organized, studio { name, parent_studio { name } },
tags { name }, performers { name }, visual_files { id, path, basename, width, height }`.

Use `visual_files` (Stash `ImageFile`). Guard null optional fields.

## Files per item

Process each entry in `visual_files`. Same multi-file and collision rules as scenes.

## Template config

- Settings key: `templates.image`.
- Scene-only variables (`video_codec`, `duration`, etc.) are typically empty for images.

## Edge cases

| Case | Behavior |
|---|---|
| No visual files | Skip + warn |
| Empty rendered basename | Fall back to original basename stem |

## Subcommands

| Spec | CLI |
|---|---|
| [`image/mv.md`](./image/mv.md) | `stash2fs image mv <ID>` |
| [`image/bulk-mv.md`](./image/bulk-mv.md) | `stash2fs image mv --all [filters]` |

## Plugin

Hook `Image.Update.Post` → same pipeline as [`image/mv.md`](./image/mv.md).
