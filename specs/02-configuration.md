# Configuration

Configuration in `stash2fs` is managed by [pydantic-settings](https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings), which gives us input validation and environment variable overriding basically for free.

## Sources and Precedence

**All** configuration settings and its defaults are defined at `src/core/settings.py` onder a `Stash2FSSettings` structure that inherits from `pydantic_settings` `BaseSettings`. This is configured to allow environment variable overrides with the `STASH2FS`_ prefix.

These settings may be further overriden by using command line parameters passed to `stash2fs` in **Standalone Mode**.

When executing in **Plugin Mode**, the `stash-plugin-wrapper` script takes care of parsing the JSON inputs sent by Stash on the `stdin` and formatting those as command line parameters, so they can also be used to override settings.

## Global Settings


| Setting                     | Type      | Default                         | Description                                                                                                                                                                                                                                                                                                                                                                                                |
| --------------------------- | --------- | ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `mode_dry_run`              | `boolean` | `True`                          | Enable/Disable the **Dry Run** mode. It's `True` by default as the user is expected to try out the tool multiple times until they are comfortable with the results before enabling this setting on the Stash GUI                                                                                                                                                                                           |
| `filter_organized_only`     | `boolean` | `True`                          | Enable/Disable moving **only** items marked as `organized` in Stash. This ensures the **Library** contains only files the user considers to have the proper metadata, lowering the changes for improperly named resources.                                                                                                                                                                                 |
| `stash_url`                 | `string`  | `http://localhost:9999/graphql` | The base URL for the Stash GraphQL API.                                                                                                                                                                                                                                                                                                                                                                    |
| `stash_api_key`             | `string`  | `Required`                      | The Stash API Key used for authenticating against the Stash API.                                                                                                                                                                                                                                                                                                                                           |
| `stash_api_timeout_seconds` | `integer` | `30`                            | How long to wait for operations against the Stash API before failing.                                                                                                                                                                                                                                                                                                                                      |
| `collision_behavior`        | `string`  | `skip`                          | The behavior of `stash2fs` when it encounters a colision - that is - tries to move a file to a path already containing the same file. Defaults to `skip` which skips the file and logs a `WARNING`. If running a bulk operation, it may continue normally for other files. Other options: - `fail` terminates the operation entirely and logs an error. If running a bulk operation, it exits immediately. |
| `library_path`              | `string`  | `Required`                      | This is the path to the `stash2fs` **Library** and arguably the most important configuration setting. This **must** be a path managed by Stash, and **should not** contain files not managed by `stash2fs` if possible, to avoid conflicts.                                                                                                                                                                |


## Path Templates

These are [Jinja](https://jinja.palletsprojects.com/en/stable/) templates used to compute the destination path.


| Setting                 | Type     | Default                                                                      | Notes                             |
| ----------------------- | -------- | ---------------------------------------------------------------------------- | --------------------------------- |
| `scene_path_template`   | `string` | `scenes/{{ studio }}/{{ date }} - {{ title }}.{{ extension }}`               | Template Path for Scenes          |
| `gallery_path_template` | `string` | `images/{{ date }} - {{ title }}/{{ datetime }}{{ unique }}.{{ extension }}` | Template Path for Galleries       |
| `image_path_template`   | `string` | `images/misc/{{ datetime }}{{ unique }}.{{ extension }}`                     | Template Path for Unsorted Images |


## Template Tag Mappings

This is the list of available template tags for building **Path Templates** and their fallbacks.


| Setting        | Metadata Field | Fallback | Notes |
| -------------- | -------------- | -------- | ----- |
| `{{ studio }}` | `string`       | ``misc`` |       |


## Stash UI Only Settings


| Setting   | Type      | Default | Description                                                                              |
| --------- | --------- | ------- | ---------------------------------------------------------------------------------------- |
| `enabled` | `boolean` | `True`  | Used by Stash to enable/disable plugin hooks. Does not need to exist in the code itself. |


