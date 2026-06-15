# 07 — Media Types

> **CLI agents:** use [`commands/<type>.md`](./commands/) instead of this file.
> Read this only for consolidated cross-type notes or non-CLI work.

`moveFiles` operates on **file IDs**. Each media type resolves to one or more files; the
mover issues one `moveFiles` call per file so each can receive a templated basename.

## Common flow per item

1. Fetch item metadata + its files via GraphQL ([`03`](./03-stash-integration.md)).
2. For each file:
   - Build `RenderContext` from item fields + that file's fields.
   - Select template ([`04`](./04-templating.md)), render, split into folder + basename,
     re-append original extension.
   - Validate (library path + collision, [`08`](./08-error-handling-logging.md)).
   - If valid and not a no-op and not dry-run: call `moveFiles` for that single file id.

## Scenes

- `type = scene`. Use `findScene(id)`.
- A scene may have **multiple files** (duplicates/versions/parts). Process each file.
- Rich metadata available for templates: codecs, resolution, frame rate, duration, etc.
- Template defaults SHOULD assume a single primary file but MUST not break with multiple.

## Images

- `type = image`. Use `findImage(id)`.
- Files come from `visual_files` (Stash `ImageFile`). Process each.
- Fewer technical fields than scenes (dimensions available; codec/duration typically not).

## Galleries

- `type = gallery`. **v1: zip-based galleries only.**
- A zip gallery is backed by a file (the `.zip`); move that file via `moveFiles`.
- **Folder-based galleries are out of scope for v1** (a gallery whose images are loose files
  in a directory). When `mv` encounters a folder-based gallery:
  - It MUST detect this (gallery has no movable zip file / is folder-backed),
  - **skip** it, and log a warning: `skipped: folder-based gallery not supported in v1`.
  - It MUST NOT attempt to move the directory or its images.
- Document this clearly in the user-facing README.

## Extension handling

- The original extension of each file MUST be preserved in `destination_basename`.
- Stash validates the basename extension against supported media extensions; an attempt to
  change it is unsupported and MUST be avoided by always re-appending the source extension.

## No-op detection

- If the rendered `destination_folder` + `destination_basename` equals the file's current
  parent folder + basename (after normalization), the file is `unchanged` and skipped (debug
  log). This guarantees idempotency and avoids redundant hook churn.

## Edge cases to handle gracefully

- Item with **no files** → skip + warn.
- File whose path is outside all library paths (already misplaced) → still compute; if the
  destination is valid (inside a library path) the move proceeds.
- Missing/empty title, date, studio → templates render empty for those; basename must remain
  non-empty (fall back to original basename stem if the rendered stem is empty).
- Duplicate destination basename across multiple files of the same item → second triggers a
  collision skip (it would otherwise overwrite); log it.
