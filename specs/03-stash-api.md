# Stash API

## Overview

`stash2fs` uses [gql](https://gql.readthedocs.io/en/stable/) to interact with the Stash GraphQL API both for collecting data about files and to move files through the `moveFiles` mutation. This documet describes how the GraphQL queries are executed and what data they collect.

## Queries

### Scenes

- `type = scene`. Use `findScene(id)`.
- A scene may have **multiple files** (duplicates/versions/parts). Process each file.
- Rich metadata available for templates: codecs, resolution, frame rate, duration, etc.
- Template defaults SHOULD assume a single primary file but MUST not break with multiple.

### Images

- `type = image`. Use `findImage(id)`.
- Files come from `visual_files` (Stash `ImageFile`). Process each.
- Fewer technical fields than scenes (dimensions available; codec/duration typically not).

### Galleries

- `type = gallery`. **v1: zip-based galleries only.**
- A zip gallery is backed by a file (the `.zip`); move that file via `moveFiles`.
- **Folder-based galleries are out of scope for v1** (a gallery whose images are loose files in a directory). When `mv` encounters a folder-based gallery:
  - It MUST detect this (gallery has no movable zip file / is folder-backed),
  - **skip** it, and log a warning: `skipped: folder-based gallery not supported in v1`.
  - It MUST NOT attempt to move the directory or its images.
- Document this clearly in the user-facing README.

## Mutations

The **only** mutation used by `stash2fs` is `moveFiles` which is leveraged to effectivelly move the managed file to their new destination, ensuring Stash handles database consistency in the process.

This is the mutation signature as the time of this writing:

```graphql
mutation MoveFiles($input: MoveFilesInput!) {
  moveFiles(input: $input)
}
```

```graphql
input MoveFilesInput {
  ids: [ID!]!            # FILE ids (not item ids)
  destination_folder: String     # full path to destination parent folder, within a library path
  destination_folder_id: ID      # alternative to destination_folder
  destination_basename: String   # valid ONLY for a single file id; must keep a supported extension
}
```

### Semantics (from Stash):

- Either `destination_folder` or `destination_folder_id` is required;
  - `destination_folder_id` wins if both are given.
  - `stash2fs` uses `destination_folder`.
- `destination_basename` is only valid when `ids` has exactly **one** element.
- `destination_folder` **must** be within a Stash library path.
- Stash creates the folder hierarchy, moves the file(s), updates the DB, and rolls back on failure.

### How `stash2fs` calls it

Because `destination_basename` requires a single file id, `stash2fs` MUST issue **one** `moveFiles` **call per file** so each file gets its templated basename:

For each `MovePlan`:

```json
{
  "input": {
    "ids": ["<file_id>"],
    "destination_folder": "<rendered folder>",
    "destination_basename": "<rendered filename incl. extension>"
  }
}
```

- A `false` return or GraphQL error MUST be treated as a failed move for that file: log at error level and continue with remaining files/items (do not abort the whole run).

