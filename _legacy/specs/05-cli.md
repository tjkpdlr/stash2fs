# 05 — CLI (index)

CLI specifications live under **[`commands/`](./commands/)** using progressive disclosure.

**Agents:** read [`commands/AGENTS.md`](./commands/AGENTS.md) first; do not use this file as
the implementation spec.

## Command index

| CLI | Spec |
|---|---|
| Global options, pipeline, output, exit codes | [`commands/_global.md`](./commands/_global.md) |
| `stash2fs scene …` | [`commands/scene.md`](./commands/scene.md) |
| `stash2fs scene mv <ID>` | [`commands/scene/mv.md`](./commands/scene/mv.md) |
| `stash2fs scene mv --all` | [`commands/scene/bulk-mv.md`](./commands/scene/bulk-mv.md) |
| `stash2fs image …` | [`commands/image.md`](./commands/image.md) |
| `stash2fs image mv <ID>` | [`commands/image/mv.md`](./commands/image/mv.md) |
| `stash2fs image mv --all` | [`commands/image/bulk-mv.md`](./commands/image/bulk-mv.md) |
| `stash2fs gallery …` | [`commands/gallery.md`](./commands/gallery.md) |
| `stash2fs gallery mv <ID>` | [`commands/gallery/mv.md`](./commands/gallery/mv.md) |
| `stash2fs gallery mv --all` | [`commands/gallery/bulk-mv.md`](./commands/gallery/bulk-mv.md) |

Built with [`click`](https://click.palletsprojects.com/). Entrypoint: `stash2fs`.
