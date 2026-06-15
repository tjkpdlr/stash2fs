# Stash Plugin

The Stash plugin interface allows `stash2fs` to be executed directly from Stash in response to activity hooks. Each hook calls a `stash2fs` command under the hood.


| Stash Hook            | `stash2fs` command    |
| --------------------- | --------------------- |
| `Gallery.Update.Post` | `stash2fs gallery mv` |
| `Image.Update.Post`   | `stash2fs image mv`   |
| `Scene.Update.Post`   | `stash2fs scene mv`   |


This process is intermediated by a standalone python script `stash-plugin-wrapper` - the sole purpose of this script is to serve as the call point of `stash2fs` from the Stash Plugin Raw Interface, receiving the `stdin` inputs sent by Stash and formatting them as a `stash2fs` command line with the appropriate parameters; then calling `stash2fs` with this command line.