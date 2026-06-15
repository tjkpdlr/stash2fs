# 06 — Stash Plugin

The plugin reuses the same core/CLI logic; it is a thin runtime that reads the Stash FRAGMENT
from stdin and dispatches to the same `mover` used by the CLI. Model the ergonomics on
`references/stash-plugins-fabio/plugins/renamerOnUpdate`.

## Plugin manifest (`stash2fs.yml`)

```yaml
name: stash2fs
description: Organize scenes, images, and galleries on disk from Stash metadata.
url: https://github.com/guhcampos/stash2fs   # adjust to final repo
version: 0.1.0
exec:
  - python
  - "{pluginDir}/stash2fs_plugin.py"
interface: raw
settings:
  enabled:
    displayName: Enabled
    description: React to update hooks.
    type: BOOLEAN
  dryRun:
    displayName: Dry Run
    description: Log planned moves without performing them.
    type: BOOLEAN
hooks:
  - name: hook_rename_scene
    description: Move scene file(s) when a scene is updated.
    triggeredBy:
      - Scene.Update.Post
  - name: hook_rename_image
    description: Move image file(s) when an image is updated.
    triggeredBy:
      - Image.Update.Post
  - name: hook_rename_gallery
    description: Move gallery file(s) when a gallery is updated.
    triggeredBy:
      - Gallery.Update.Post
tasks:
  - name: "Enable"
    description: Enable the update hooks.
    defaultArgs:
      mode: enable
  - name: "Disable"
    description: Disable the update hooks.
    defaultArgs:
      mode: disable
  - name: "Dry-run"
    description: Toggle dry-run mode.
    defaultArgs:
      mode: dryrun
  - name: "Organize all"
    description: Process all scenes, images, and galleries (bulk).
    defaultArgs:
      mode: bulk
```

> The `exec` entrypoint name (`stash2fs_plugin.py`) is a thin shim that imports
> `stash2fs.plugin.runtime` and calls `main()`. Bundling is described in
> [`08`](#packaging--bundling) below and in `tasks/`.

## Runtime dispatch

On invocation:

1. Read & parse stdin FRAGMENT (`server_connection`, `args`). See [`03`](./03-stash-integration.md#plugin-io).
2. Build the Stash connection from `server_connection`.
3. Load `Settings` and overlay plugin UI settings (precedence in [`02`](./02-configuration.md)).
4. Branch on `args.mode` / hook context:

| Trigger | `args` | Action |
|---|---|---|
| Task **Enable** | `mode: enable` | Persist `enabled=true` (see persistence note) and log. |
| Task **Disable** | `mode: disable` | Persist `enabled=false` and log. |
| Task **Dry-run** | `mode: dryrun` | Toggle/persist `dry_run` and log new state. |
| Task **Organize all** | `mode: bulk` | Run bulk over all three types with `LogProgress`. |
| Hook (no `mode`) | `hookContext: {id, type}` | If `enabled`, process that single item; else no-op log. |

### Hook handling

- The hook payload identifies the updated entity by `id` and `type`
  (`Scene`/`Image`/`Gallery`). Map to the corresponding `mv` single-item flow.
- If `enabled` is false, exit quickly with an info log (do nothing).
- Respect `dry_run` exactly as the CLI does.
- Hooks MUST be resilient: any error for one item is logged at error level; the plugin exits
  cleanly (non-fatal to Stash). Never raise unhandled exceptions back to Stash.

### Enable/Disable/Dry-run persistence

- Prefer persisting these toggles through Stash plugin configuration (so the UI reflects
  state), via the appropriate `configurePlugin`/plugin-settings mutation. If that is not
  feasible across supported Stash versions, fall back to a small state file under
  `PluginDir` (document the chosen mechanism). This mirrors renamerOnUpdate's enable/disable
  task behavior.

## Logging

Use the Stash stderr log protocol (SOH + level + STX), levels `t/d/i/w/e` and progress `p`.
See [`08-error-handling-logging.md`](./08-error-handling-logging.md). In plugin mode, do NOT
write to stdout except for any required plugin output contract.

## Packaging / bundling

The plugin bundle placed in Stash's `plugins/<stash2fs>/` MUST contain everything Python
needs at runtime with no external install step beyond the plugin's declared deps:

- `stash2fs.yml`
- `stash2fs_plugin.py` (entry shim)
- the `stash2fs` package (vendored or installed into the bundle)
- third-party deps (`httpx`, `jinja2`, `pydantic`, `pydantic-settings`) must be importable;
  document the bundling method (e.g. `uv pip install --target` into the bundle, or a build
  script). See `tasks/TASK-07` and `tasks/TASK-09`.

## Out of scope (plugin v1)

- Per-hook configuration in UI beyond `enabled`/`dryRun`.
- Folder-based galleries (zip only).
