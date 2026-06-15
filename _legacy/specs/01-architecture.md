# 01 — Architecture

## Principles

- **One core, two entrypoints.** All business logic lives in a reusable core package used
identically by the CLI and the plugin runtime. Entrypoints only adapt I/O and config.
- **Stash is the only side-effecting backend.** The core never writes the filesystem or DB;
it calls Stash GraphQL (`moveFiles`) and reads metadata via GraphQL.
- **Pure where possible.** Template rendering, destination computation, and validation are
pure functions of (metadata + config). They are unit-tested without a running Stash.

## Package layout

Proposed module structure (implementers may refine names but MUST keep the layering):

```
stash2fs/
  __init__.py
  __main__.py              # enables `python -m stash2fs`
  cli/
    __init__.py
    main.py                # click root group
    scene.py              # `scene mv` and friends
    image.py
    gallery.py
  plugin/
    __init__.py
    runtime.py             # reads stdin FRAGMENT, dispatches hooks/tasks
    io.py                  # Stash plugin stderr log protocol (SOH/level/STX)
  core/
    __init__.py
    models.py              # pydantic models for Item, File, RenderContext
    planner.py             # compute MovePlan(s) for an item (pure)
    templating.py          # Jinja2 environment, variable mapping, selection logic
    validation.py          # library-path + collision checks (pure given inputs)
    mover.py               # orchestrates: resolve -> plan -> validate -> moveFiles
  stash/
    __init__.py
    client.py              # GraphQL transport (httpx), auth, error mapping
    queries.py             # query/mutation strings + typed wrappers
    connection.py          # build connection from config or plugin FRAGMENT
  config/
    __init__.py
    settings.py            # pydantic-settings Settings classes
    config.py              # default values (the "config.py" surface from AGENTS.md)
  logging.py               # logging setup that works in both CLI and plugin contexts
```

## Layering / dependency rules

- `cli/` and `plugin/` depend on `core/`, `stash/`, `config/`, `logging.py`.
- `core/` depends on `stash/` (for `moveFiles` and metadata) and `config/` and `templating`.
- `core/templating.py`, `core/validation.py`, `core/planner.py` MUST be importable and
testable without network access. Network calls live behind `stash/`.
- No module imports from `cli/` or `plugin/` upward.

## End-to-end flow (single item)

```
                 +-------------------+
 CLI args /      |  config/settings  |  precedence: CLI > plugin UI > env > defaults
 plugin FRAGMENT |  (pydantic)       |
                 +---------+---------+
                           |
                           v
 +----------+   resolve   +----------+   plan    +-----------+  validate  +-----------+
 | item id  +-----------> |  stash   +---------> | planner   +----------> |validation |
 | + type   |  GraphQL    |  client  | metadata  | (Jinja2)  | MovePlan   |  (paths,  |
 +----------+             +----------+           +-----------+            | collision)|
                                                                          +-----+-----+
                                                                                |
                                              dry-run? log plan & stop          |
                                                                                v
                                                                        +---------------+
                                                                        | moveFiles     |
                                                                        | mutation      |
                                                                        +---------------+
```

## Key domain objects

- `Item` — `{ id, type, title, ..., files: list[File], studio, tags, performers, date, ... }`
populated from GraphQL. Only fields needed for templating/validation are required.
- `File` — `{ id, path, basename, parent_folder, extension, ... }`.
- `RenderContext` — flattened, template-facing variables derived from `Item` + `File`
(see `[04-templating.md](./04-templating.md)`).
- `MovePlan` — `{ file_id, current_path, destination_folder, destination_basename, selected_template, reason }`. The unit passed to `moveFiles` and reported in dry-run.

## Idempotency

A move where the rendered destination equals the current path MUST be a no-op (logged at
debug). Re-running after a successful move MUST produce zero changes.

## Concurrency

v1 is single-threaded and processes items sequentially. Bulk mode MUST emit progress (CLI
progress + Stash `LogProgress` in plugin mode). Parallelism is out of scope.