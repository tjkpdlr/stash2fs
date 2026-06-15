# 04 — Templating

## Engine

- **Jinja2.** Each template is a single string that renders the **full destination path**
(folder + filename + extension), e.g.
`"{{ library }}/{{ studio }}/{{ date }} - {{ title }}{{ ext }}"`.
- After rendering, `stash2fs` splits the result into:
  - `destination_folder` = everything up to the last path separator,
  - `destination_basename` = the final path segment.
- The basename MUST end with the original file extension. If the template omits/changes it,
`stash2fs` MUST re-append the original extension (see `[03](./03-stash-integration.md)`).

### Jinja2 configuration

- `undefined`: a custom undefined that renders to empty string (so missing metadata yields
empty, not an error) **but** records that it was used (for group trimming, below).
- `trim_blocks=True`, `lstrip_blocks=True`, `keepends` off.
- Autoescape **off** (these are paths, not HTML).
- Provide custom filters (see below). No access to Python builtins / no arbitrary code.

## Variables (RenderContext)

Variables are derived from item + the specific file being moved. Names are normative;
implementers MAY add more but MUST provide these. Missing values render as empty string.


| Variable                             | Meaning                                                                                                |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------ |
| `library`                            | The library/stash root path the file currently lives under (for `^`*-style "stay in place" templates). |
| `current_dir`                        | Current parent directory of the file.                                                                  |
| `ext`                                | Original file extension including dot (e.g. `.mp4`).                                                   |
| `title`                              | Item title (falls back to current basename without extension if empty).                                |
| `date`                               | Item date (`YYYY-MM-DD`) or empty.                                                                     |
| `year`                               | Year portion of `date`.                                                                                |
| `studio`                             | Studio name.                                                                                           |
| `studio_hierarchy`                   | Parent→child studio chain joined by the OS separator (e.g. `MindGeek/Brazzers`).                       |
| `code`                               | Studio/scene code.                                                                                     |
| `rating`                             | Rating (0–100) or empty.                                                                               |
| `performers`                         | List of performer names (use with `join`).                                                             |
| `performer`                          | First performer name.                                                                                  |
| `tags`                               | List of tag names.                                                                                     |
| `resolution`                         | e.g. `1080p` (derived from height) when available.                                                     |
| `width`, `height`                    | Pixel dimensions when available.                                                                       |
| `video_codec`, `audio_codec`         | Codecs when available (scenes).                                                                        |
| `frame_rate`, `bit_rate`, `duration` | When available (scenes).                                                                               |
| `id`                                 | Item id.                                                                                               |
| `type`                               | `scene` | `image` | `gallery`.                                                                         |


### Custom filters

- `sanitize` — strip/replace characters illegal in filenames on the target OS; collapse
whitespace. MUST be applied implicitly to the final basename even if not called.
- `default(value)` — Jinja2 builtin; usable for fallbacks.
- `join(sep)` — for `performers`/`tags`.
- `lower`, `upper`, `title` — standard.

## Template selection (per item)

For a given item and media type, choose exactly one template using this priority (D8):

1. **By tag** — if any of the item's tags matches a key in `templates.<type>.by_tag`.
  If multiple tags match, the **first match in declaration order** of `by_tag` wins
   (config dict order is significant; document this).
2. **By studio** — else if the item's studio (or any ancestor studio) matches a key in
  `templates.<type>.by_studio`.
3. **By source path** — else if the file's current path starts with (prefix match) a key in
  `templates.<type>.by_path` (longest-prefix wins).
4. **Default** — else `templates.<type>.default`.

The selected template and the selection reason MUST be recorded on the `MovePlan` for
dry-run/debug output.

## Group trimming (optional ergonomic, from renamerOnUpdate)

renamerOnUpdate supports `{ ... }` groups that vanish when an inner variable is empty
(e.g. `{$date -}`). With Jinja2 this is naturally expressed with conditionals
(`{% if date %}{{ date }} - {% endif %}`). v1 MUST support the Jinja2-native form. A
`{...}`-style sugar is **optional**; if implemented, document it, otherwise instruct users to
use `{% if %}`.

## Path normalization

- Collapse duplicate separators; resolve `.`/`..` defensively; normalize separators per
`path_separator` (default `auto` = OS of the Stash server as inferred from library paths).
- The rendered `destination_folder` MUST be absolute. Relative results are an error (skip +
log) unless the template intentionally builds on `{{ library }}`/`{{ current_dir }}`.

## Worked example

Template (scene default):

```
{{ library }}/{{ studio }}/{% if date %}{{ date }} - {% endif %}{{ title }}{{ ext }}
```

Given `library=/media`, `studio=Blender Institute`, `date=2008-05-20`,
`title=Big Buck Bunny`, `ext=.mp4`:

- rendered → `/media/Blender Institute/2008-05-20 - Big Buck Bunny.mp4`
- `destination_folder` → `/media/Blender Institute`
- `destination_basename` → `2008-05-20 - Big Buck Bunny.mp4`

