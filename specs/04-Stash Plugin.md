# Stash Plugin

The Stash plugin interface allows `stash2fs` to be executed directly from Stash in response to activity hooks. Each hook calls a `stash2fs` command under the hood.


| Stash Hook            | `stash2fs` command    |
| --------------------- | --------------------- |
| `Gallery.Update.Post` | `stash2fs gallery mv` |
| `Image.Update.Post`   | `stash2fs image mv`   |
| `Scene.Update.Post`   | `stash2fs scene mv`   |


