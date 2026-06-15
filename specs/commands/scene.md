# Command group: `stash2fs scene`

Media type **`scene`**. Shared by `scene mv` and `scene mv --all`.

## Dependencies

- [`_global.md`](./_global.md) — CLI globals, move pipeline, validation, output.

## GraphQL

- Single item: `findScene(id)`.
- Bulk listing: `findScenes(filter)` with pagination.

Minimum fields: `id, title, code, date, rating100, organized, studio { name, parent_studio { name } },
tags { name }, performers { name }, files { id, path, basename, width, height, video_codec,
audio_codec, frame_rate, bit_rate, duration }`.

Guard null optional fields; missing → empty in templates.

## Files per item

A scene may have **multiple files** (versions/parts). Process **each file** with its own
`moveFiles` call and templated basename. Duplicate basenames within one scene → second file
collision-skips.

## Template config

- Settings key: `templates.scene` (`default`, `by_tag`, `by_studio`, `by_path`).
- Extra template variables: `resolution`, `video_codec`, `audio_codec`, `frame_rate`,
  `bit_rate`, `duration`, `code` (see [`../04-templating.md`](../04-templating.md) if
  extending variables).

## Edge cases

| Case | Behavior |
|---|---|
| No files on scene | Skip + warn |
| Empty rendered basename | Fall back to original basename stem |
| Item id passed to CLI | Scene id, **not** file id |

## Subcommands

| Spec | CLI |
|---|---|
| [`scene/mv.md`](./scene/mv.md) | `stash2fs scene mv <ID>` |
| [`scene/bulk-mv.md`](./scene/bulk-mv.md) | `stash2fs scene mv --all [filters]` |

## Plugin

Hook `Scene.Update.Post` invokes the same pipeline as [`scene/mv.md`](./scene/mv.md) for
the hook's scene id. See [`../06-plugin.md`](../06-plugin.md) only for plugin wiring.
