# Specifications for `stash2fs` commands

This directory contains individual specifications for `stash2fs` commands, one-per-file, organized in subdirectories which respect Click's [command hierarchy.](https://click.palletsprojects.com/en/stable/commands/)

## Rules

## How specs are organized

```
specs/
  README.md              ← decision log + index (read once if unsure about scope)
  commands/
    AGENTS.md              ← you are here
    _global.md             ← shared CLI behavior (always read for any command work)
    <type>.md              ← media-type context (scene | image | gallery)
    <type>/
      mv.md                ← single-item move
      bulk-mv.md           ← bulk move (CLI: `mv --all`)
  01-architecture.md …     ← core reference library (read only when linked)
```

**Command specs are the entry point.** Each file lists exactly which other files you need.
Everything else in `specs/` is optional reference material — follow links only when your
command spec says so.

## Workflow

1. **Identify your command** — e.g. implement `stash2fs scene mv`.
2. **Open the leaf spec** — `specs/commands/scene/mv.md`.
3. **Read its *Dependencies* section only** — typically `_global.md` + `scene.md`, sometimes
  one core doc (e.g. templating) if you are changing shared logic.
4. **Implement only what that spec defines.** Do not pull in plugin, bulk, or other media
  types unless your task explicitly includes them.
5. **Verify against the spec's *Acceptance criteria*.**

## Dependency rules


| Task                            | Read                                                                                                                        |
| ------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Any CLI command                 | Assigned `commands/<type>/<action>.md` + its listed dependencies                                                            |
| Shared move/validate logic      | `commands/_global.md` → link to `../03-stash-integration.md#write--the-only-mutation-movefiles` if implementing `moveFiles` |
| Template engine                 | `../04-templating.md` (skip command specs)                                                                                  |
| Configuration                   | `../02-configuration.md`                                                                                                    |
| Plugin hook for one type        | `../06-plugin.md` + `commands/<type>/mv.md` (hook = single-item pipeline)                                                   |
| Plugin bulk task                | `../06-plugin.md` + all three `commands/*/bulk-mv.md`                                                                       |
| Project scaffold / architecture | `../01-architecture.md` + `../00-overview.md`                                                                               |


## RFC 2119

Treat **MUST / SHOULD / MAY** literally in every spec file.

## Naming note

Spec file `bulk-mv.md` documents bulk behavior. The CLI surface is `**mv --all`**, not a
separate `bulk-mv` subcommand (unless a future spec changes that).

## When to read `specs/README.md`

- First time on the project (decision log, deferred scope).
- Unsure whether a feature is in or out of v1.
- Resolving a conflict between command spec and core spec — command spec wins for CLI
behavior; core spec wins for shared infrastructure; escalate if they disagree.

