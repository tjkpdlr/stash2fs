# Configuration

Configuration in `stash2fs` is managed by [pydantic-settings](https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings), which gives us input validation and environment variable overriding basically for free. 

## Global Settings


| Setting                 | Type      | Default | Description                                                                                                                                                                                                                |
| ----------------------- | --------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `mode_dry_run`          | `boolean` | `True`  | Enable/Disable the **Dry Run** mode. It's `True` by default as the user is expected to try out the tool multiple times until they are comfortable with the results before enabling this setting on the Stash GUI           |
| `filter_organized_only` | `boolean` | `True`  | Enable/Disable moving **only** items marked as `organized` in Stash. This ensures the **Library** contains only files the user considers to have the proper metadata, lowering the changes for improperly named resources. |


