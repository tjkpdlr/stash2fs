# Stash Plugin

The Stash plugin interface allows `stash2fs` to be executed directly from Stash in response to activity hooks. Each hook calls a `stash2fs` command under the hood.


| Stash Hook            | `stash2fs` command    |
| --------------------- | --------------------- |
| `Gallery.Update.Post` | `stash2fs gallery mv` |
| `Image.Update.Post`   | `stash2fs image mv`   |
| `Scene.Update.Post`   | `stash2fs scene mv`   |


This process is intermediated by a standalone python script `stash-plugin-wrapper.`

The sole purpose of this script is to serve as the call point of `stash2fs` from the Stash Plugin Raw Interface:

- receiving the `stdin` inputs sent by Stash
- formatting them as a `stash2fs` command line with the appropriate parameters
- injecting the `--log-format=stash` parameter
- injecting the `--progress=false` parameter
- then calling `stash2fs` with this command line.

## Plugin Manifest Template

Stash requires each plugin to provide a `YAML` manifest. This is a minimal template for `../stash2fs.yml` and needs to be filled in with addictional Settings and Tasks as these are implemented in the future.

```yaml
name: stash2fs
description: Organize scenes, images, and galleries on disk from Stash metadata.
url: https://github.com/tjkpdlr/stash2fs
version: 0.1.0 # adjust to actual version
exec:
  - "{pluginDir}/scripts/stash-plugin-wrapper"
interface: raw
settings:
  enabled:
    displayName: Enabled
    description: Enable `stash2fs` plugin.
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
  - name: "Bulk Move Scenes"
    description: |
      Move **ALL** scene file(s) to organized directories.

      Make sure you know what you're doing and to execute a **dry-run** first. You may also want to check if the
      `organized_only` filter is enabled.

```

