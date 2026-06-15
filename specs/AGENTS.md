# Specifications for `stash2fs`

This directory contains the specifications for `stash2fs` - agents **must** read all files in this directory at the start of a session, then use progressive disclosure to read additional files as required. Files in subdirectories only need to be read when relevant to the current task.

These *specs* are generally **human written only** and should be considered **read only** by agents unless explicitly overriden by a human.

## Rules

- **never** make changes to specifications unless explicitly instructed by a human
- **never** implement unspecified features or behaviors, **always** ask before inferring
- **only** read the specifications required to work on the task at hand

