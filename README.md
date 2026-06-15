# stash2fs

Organize scenes, images, and galleries on disk according to metadata stored in [Stash](https://stashapp.cc/). Computes destination paths from Jinja2 templates and moves files through Stash's GraphQL `moveFiles` mutation (no direct filesystem or SQLite access).

## AI Notice

Please note this tool has been built with heavy use of AI. The author is a professional software developer with a couple decades experience, but no time to hand-code the application as they would like. If you have any issues with the AI use on this project, please feel free to exercise your voice in the way you see fair.

Since the tool is written in Python, the full code is available for inspection, and so is the full specification markdown used to generate the code. The only prompt used is:

> Please implement the tool in this repository as instructed by specifications, start with `AGENTS.md` 

  
As it's natural for LLMs, the results you'll get from running the exact same prompt against the exact same specs will vary greatly, but you are free to fork this and re-generate new code from the same specs using different models. I honestly don't care, and if the results are better than what you get from the current version, by all means feel free to create a PR back to the project!

## Overview

When running as a standalone application, `stash2fs` provides a series of commands to organize each type of media supported by stash, such as `stash2fs image mv`, `stash2fs scene mv` and `stash2fs gallery mv` - these examples move a single item of that type to the new location determined by a configured template and that item metadata.

When running as a Stash plugin, it should behave similarly to [renamerOnUpdate](./references/stash-plugins-fabio/plugins/renamerOnUpdate): listening to `Scene.Update.Post`, `Image.Update.Post` and `Gallery.Update.Post` and calling the appropriate standalone commands to handle that type of file.

## Features

- Standalone CLI: `stash2fs scene mv`, `stash2fs image mv`, `stash2fs gallery mv`
- Stash plugin with update hooks and bulk/tasks (Enable, Disable, Dry-run, Organize all)
- Per-type Jinja2 templates with tag/studio/path overrides
- Dry-run mode and safe-by-default collision / library-path validation

## Installation

```bash
uv sync
uv run stash2fs --help
```

## CLI examples

```bash
# Preview a single scene move
uv run stash2fs scene mv 1234 --dry-run

# Move all unorganized images from a studio
uv run stash2fs image mv --all --studio "Blender Institute" --dry-run
```

Configure templates and behavior via environment variables (`STASH2FS_*`), an optional Python config file (`--config`), or defaults in `src/stash2fs/config/config.py`.

## Stash plugin

1. Build the bundle: `./scripts/build-plugin-bundle.sh`
2. Copy `bundle/stash2fs/` into your Stash `plugins/` directory
3. Reload plugins in Stash and configure **Enabled** / **Dry Run**

Hooks fire on `Scene.Update.Post`, `Image.Update.Post`, and `Gallery.Update.Post`.

### Limitations (v1)

- **Move only** — uses Stash `moveFiles`; no copy/hardlink/symlink
- **Zip galleries only** — folder-based galleries are skipped with a warning
- **Collision policy** — `skip` only

## Development

```bash
uv sync
uv run ruff check .
uv run ruff format --check .
uv run mypy src/stash2fs
uv run pytest
```

## License

MIT