# CLI

The `stash2fs` CLI is the default execution mode of the tool.

## Dry Run

All commands in `stash2fs` support a **dry run** mode, which outputs the operations which would have been executed without actually executing them. This can be used to evaluate the eventual results of the execution without touching any files or the Stash database.

The **dry run** mode can be enabled on any command by providing the `--dry-run` flag.

## Commands

Each command's specifications are stored in `./commands` - read `./commands/AGENTS.md` for instructions on how to use this directory.
