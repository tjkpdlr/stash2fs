# Error Handling and Observability

## Logging

`stash2fs` uses [rich](https://rich.readthedocs.io/en/latest/) for human readable output, including [log handling](https://rich.readthedocs.io/en/latest/logging.html). The log format, however, depends on the context where the tool is called from and command line parameters.

There are 3 available log formats, which can be specified with the `--log-format` flag:

### `default`

Colorful, human readable format. Dates and Times are printed in ISO format

This is the **default** when running in **Standalone Mode**

### `json`

Machine Readable JSON format, no colors.

### `stash`

Uses the Stash `stderr` protocol for displaying in the Stash GUI:

- each message prefixed with `SOH (\x01)` + level char + `STX (\x02)`
- `t` trace, `d` debug, `i` info, `w` warning, `e` error, `p` progress (a float 0..1).

This is the **default** when running as a **Stash Plugin**

## Progress Feedback

When running **bulk** operations in **Standalone Mode**, `stash2fs` displays a progress bar to inform how many of the total files have been processed. This is provided by the `rich` library [Progress Display](https://rich.readthedocs.io/en/latest/progress.html) feature.

This feature may be disable by using the `--progress=false` parameter.

This feature is disabled when running as a **Stash Plugin**.



## Dry Run Output

When `dry-run` is enabled, no move operations will be fired, but the application reports the potential moves in the output.

If running with either `default` or `stash` log formats, each planned move is printed out in the following format:

```bash
DRY-RUN SRC <old-file-path>
DRU-RUN DST -> <new-file-path>
```

