# Command group: `stash2fs gallery`

Media type **`gallery`**. Shared by `gallery mv` and `gallery mv --all`.

## Dependencies

- [`_global.md`](./_global.md) — CLI globals, move pipeline, validation, output.

## GraphQL

- Single item: `findGallery(id)`.
- Bulk listing: `findGalleries(filter)` with pagination.

Minimum fields: `id, title, date, rating100, organized, studio { name, parent_studio { name } },
tags { name }, performers { name }, files { id, path, basename }`.

## v1 scope: zip galleries only

- **Zip gallery** — backed by a `.zip` file; move via `moveFiles` on that file.
- **Folder gallery** — loose images in a directory; **not supported in v1**:
  - Detect folder-backed gallery (no movable zip file).
  - Skip + warn: `skipped: folder-based gallery not supported in v1`.
  - Do not move the directory or contained images.

## Template config

- Settings key: `templates.gallery`.

## Subcommands

| Spec | CLI |
|---|---|
| [`gallery/mv.md`](./gallery/mv.md) | `stash2fs gallery mv <ID>` |
| [`gallery/bulk-mv.md`](./gallery/bulk-mv.md) | `stash2fs gallery mv --all [filters]` |

## Plugin

Hook `Gallery.Update.Post` → same pipeline as [`gallery/mv.md`](./gallery/mv.md).
