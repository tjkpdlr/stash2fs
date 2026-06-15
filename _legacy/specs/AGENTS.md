# stash2fs — Specifications

This directory contains specifications for `stash2fs` commands

## Quick start for agents


| Your task                            | Read                                                                  |
| ------------------------------------ | --------------------------------------------------------------------- |
| Implement `stash2fs scene mv`        | `[commands/scene/mv.md](./commands/scene/mv.md)` (+ its Dependencies) |
| Implement bulk scenes                | `[commands/scene/bulk-mv.md](./commands/scene/bulk-mv.md)`            |
| Same pattern for `image` / `gallery` | `commands/<type>/mv.md` or `bulk-mv.md`                               |
| Shared CLI / validation / output     | `[commands/_global.md](./commands/_global.md)`                        |
| Plugin                               | `[06-plugin.md](./06-plugin.md)` + relevant `commands/<type>/mv.md`   |
| Templating engine                    | `[04-templating.md](./04-templating.md)`                              |
| Stash GraphQL client                 | `[03-stash-integration.md](./03-stash-integration.md)`                |


Typical token budget for one command: **2–4 small files**, not all of `specs/`.

## Directory layout

```
specs/
  README.md                 ← this file (index + decision log)
  commands/                 ← CLI entry points (start here)
    AGENTS.md
    _global.md
    scene.md, image.md, gallery.md
    scene/mv.md, scene/bulk-mv.md, …
  00-overview.md … 09-*.md  ← core reference library (read when linked)
```

## Core reference library

Read these **only when** a command spec or task links to them:


| File                                                             | Topic                                                                 |
| ---------------------------------------------------------------- | --------------------------------------------------------------------- |
| `[00-overview.md](./00-overview.md)`                             | Vision, goals, non-goals, glossary                                    |
| `[01-architecture.md](./01-architecture.md)`                     | Package layout, layering                                              |
| `[02-configuration.md](./02-configuration.md)`                   | pydantic-settings, precedence                                         |
| `[03-stash-integration.md](./03-stash-integration.md)`           | GraphQL, `moveFiles`, plugin I/O                                      |
| `[04-templating.md](./04-templating.md)`                         | Jinja2, variables, selection                                          |
| `[05-cli.md](./05-cli.md)`                                       | Index → `commands/`                                                   |
| `[06-plugin.md](./06-plugin.md)`                                 | Stash plugin manifest & runtime                                       |
| `[07-media-types.md](./07-media-types.md)`                       | Consolidated media notes (superseded by `commands/<type>.md` for CLI) |
| `[08-error-handling-logging.md](./08-error-handling-logging.md)` | Validation, logging, dry-run                                          |
| `[09-testing-quality.md](./09-testing-quality.md)`               | Tests, ruff, types                                                    |


## Rules

- Treat **MUST/SHOULD/MAY** (RFC 2119) literally.
- Do not expand scope beyond `[00-overview.md](./00-overview.md)` non-goals.
- Reference plugin for ergonomics only: `references/stash-plugins-fabio/plugins/renamerOnUpdate`
(do not copy its direct file/DB moves).

## Decision log (authoritative)


| #   | Decision             | Choice                                                    |
| --- | -------------------- | --------------------------------------------------------- |
| D1  | Metadata source      | Stash **GraphQL API only**.                               |
| D2  | Media types (v1)     | Scenes, images, galleries.                                |
| D3  | Filesystem operation | **Move/rename only.**                                     |
| D4  | Move mechanism       | Stash `**moveFiles`** mutation only.                      |
| D5  | DB writeback         | Handled by `moveFiles`.                                   |
| D6  | Template engine      | **Jinja2.**                                               |
| D7  | Template shape       | Single full path → split folder + basename.               |
| D8  | Template selection   | **tag > studio > source-path > default.**                 |
| D9  | Config               | `pydantic-settings` + `config.py`.                        |
| D10 | Precedence           | **CLI > plugin UI > env > defaults.**                     |
| D11 | CLI targeting        | Single ID + bulk (`mv --all`).                            |
| D12 | Collision            | **Skip + log.**                                           |
| D13 | Library paths        | Validate; skip + log if outside.                          |
| D14 | Exclude rules        | Deferred.                                                 |
| D15 | Sidecar files        | Deferred to `moveFiles`.                                  |
| D16 | Empty dir cleanup    | Dropped.                                                  |
| D17 | Galleries            | Zip only in v1.                                           |
| D18 | Distribution         | uv-managed package + plugin bundle.                       |
| D19 | Plugin               | Hooks + Enable/Disable/Dry-run/Bulk tasks.                |
| D20 | Quality              | Unit tests + dry-run integration; ruff; types.            |
| D21 | Python               | 3.11+; develop on 3.12.                                   |
| D22 | Spec layout          | **Progressive disclosure** via `commands/` (this layout). |


Any change to this table is a scope change and must be agreed with the project owner.