# 03 — Stash Integration

All metadata reads and the move itself go through the Stash **GraphQL API**. There is no
direct SQLite access and no direct filesystem mutation.

## Transport

- Use `httpx` (sync client is sufficient for v1).
- Endpoint: `{stash.url}/graphql`.
- Auth: when `stash.api_key` is set, send header `ApiKey: <key>`. In plugin mode, use the
  session cookie / connection provided by Stash (see [Plugin I/O](#plugin-io)).
- Map non-200 responses and GraphQL `errors[]` to a typed `StashError` with the query name
  and message. Never leak the API key into logs or exceptions.

## Connection resolution

- **Standalone:** build from `Settings.stash`.
- **Plugin:** build from `FRAGMENT["server_connection"]`:
  `{ Scheme, Host, Port, SessionCookie, PluginDir, ... }`. If `Host == "0.0.0.0"`, use
  `localhost`. Send the session cookie. (Mirror `renamerOnUpdate.callGraphQL`.)

## Reads — metadata needed for templating/validation

Implementers MUST fetch, per item, enough to populate `RenderContext`
(see [`04-templating.md`](./04-templating.md)) and the file list. At minimum:

- **Scene** (`findScene(id)`): `id, title, code, details, date, rating100, organized,
  studio { name, parent_studio { name } }, tags { name }, performers { name, gender },
  files { id, path, basename, parent_folder_id, width, height, video_codec, audio_codec,
  frame_rate, bit_rate, duration }`.
- **Image** (`findImage(id)`): `id, title, date, rating100, organized,
  studio { name, parent_studio { name } }, tags { name }, performers { name },
  visual_files { ... id, path, basename, width, height }` (handle `ImageFile`).
- **Gallery** (`findGallery(id)`): `id, title, date, rating100, organized,
  studio { name, parent_studio { name } }, tags { name }, performers { name },
  files { id, path, basename }` — v1 targets **zip** galleries (a gallery backed by a file).

> Field availability varies across Stash versions. Implementers MUST guard optional fields
> and degrade gracefully (missing → empty), never crash on a null.

### Library paths (for validation)

Query `configuration { general { stashes { path } } }` and cache for the run. A destination
folder is valid iff it is equal to, or a descendant of, one of these paths
(after normalization). See [`08-error-handling-logging.md`](./08-error-handling-logging.md).

## Write — the only mutation: `moveFiles`

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

Semantics (from Stash):

- Either `destination_folder` or `destination_folder_id` is required;
  `destination_folder_id` wins if both are given. v1 uses `destination_folder`.
- `destination_basename` is only valid when `ids` has exactly **one** element.
- `destination_folder` MUST be within a Stash library path.
- Stash creates the folder hierarchy, moves the file(s), updates the DB, and rolls back on
  failure. Returns `Boolean`.

### How `stash2fs` calls it

Because `destination_basename` requires a single file id, `stash2fs` MUST issue **one
`moveFiles` call per file** so each file gets its templated basename:

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

- The rendered basename MUST preserve the original file's extension (Stash validates the
  extension against allowed media extensions; changing it is unsupported in v1).
- A `false` return or GraphQL error MUST be treated as a failed move for that file: log at
  error level and continue with remaining files/items (do not abort the whole run).

## Plugin I/O

When invoked as a plugin, Stash runs the configured `exec` and passes a JSON **FRAGMENT** on
**stdin**:

```json
{
  "server_connection": { "Scheme": "http", "Host": "0.0.0.0", "Port": 9999,
                          "SessionCookie": { "Value": "..." }, "PluginDir": "..." },
  "args": { "mode": "<task or hook context>", "hookContext": { "id": "...", "type": "Scene" } }
}
```

- Read and parse the entire stdin once at startup.
- `args` carries either a task `mode` (from the `.yml` task `defaultArgs`) or hook context
  identifying the updated entity (id + type). See [`06-plugin.md`](./06-plugin.md) for the
  exact hook payload handling.
- Logging goes to **stderr** using Stash's prefixed protocol (SOH + level char + STX); the
  helper mirrors `references/.../renamerOnUpdate/log.py`. Levels: trace `t`, debug `d`,
  info `i`, warning `w`, error `e`, progress `p` (0..1). See [`08-error-handling-logging.md`](./08-error-handling-logging.md).

## Out of scope

- `deleteFiles`, `destroyFiles`, fingerprinting, scanning mutations.
- Any direct DB read/write or `shutil`/`os` file moves.
