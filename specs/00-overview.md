# 00 Overview

## Features

- Move scenes, images and galleries to a standard location (**Library**) following a name convention
- Create an filesystem-based **Index** of the managed files
- **dry-run** execution for debugging and prediction

### Execution Modes

`stash2fs` has two execution modes: **Standalone CLI** and **Stash Plugin**.

#### Standalone CLI

This is the default execution mode and consists of a tradictional Click CLI. It provides commands such as `stash2fs scene mv` to move scenes and `stash2fs image mv` to move images.

Contextual configuration can be managed via environment variables or command line parameters.

#### Stash Plugin

This is a Stash Plugin interface designed as a wrapper to the **Standalone CLI**: each listened hook calls the appropriate `stash2fs` command overriding configuration with data from the Stash Plugin Configuration UI.

## Glossary

- **File** — a concrete file row in Stash (an item may own multiple files). `moveFiles` operates on **file IDs**, not item IDs.
- **Index** - a filesystem path containing symbolic links to `stash2fs` managed files for easy browsing through network shares, this does not need to be a directory managed by Stash
- **Item** — a Stash entity that owns files: a scene, image, or gallery.
- **Library** - the base directory where `stash2fs` saves files, this **must** be a directory managed by Stash and ideally should not contain any files not managed by `stash2fs` to avoid conflicts
- **Template** — a Jinja2 string rendered against an item's metadata to produce a full destination path (folder + filename).
- **Dry-run** — compute and report planned moves without calling `moveFiles`.

