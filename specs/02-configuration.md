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
| `progress`                  | `boolean` | `True`                          | Displays a Progress Bar when running **Bulk** operations. Disabled by default when running as a **Stash Plugin**                                                                                                                                                                                                                                                                                           |
| `log_format`                | `string`  | `default`                       | The log format for the tool output. Maybe be one of `default`, `json` or `stash`.                                                                                                                                                                                                                                                                                                                          |


## Path Templates

These are [Jinja](https://jinja.palletsprojects.com/en/stable/) templates used to compute the destination path.


| Setting                 | Type     | Default                                                                            | Notes                             |
| ----------------------- | -------- | ---------------------------------------------------------------------------------- | --------------------------------- |
| `scene_path_template`   | `string` | `scenes/{{ studio }}/{{ date }}{{ sep }}{{ title }}.{{ extension }}`               | Template Path for Scenes          |
| `gallery_path_template` | `string` | `images/{{ date }}{{ sep }}{{ title }}/{{ datetime }}{{ unique }}.{{ extension }}` | Template Path for Galleries       |
| `image_path_template`   | `string` | `images/misc/{{ datetime }}{{ unique }}.{{ extension }}`                           | Template Path for Unsorted Images |


## Template Tag Mappings

This is the list of available template tags for building **Path Templates** and their fallbacks.


| Setting                     | Metadata Field         | Default / Fallback String | Notes                                                                                                                                                                   |
| --------------------------- | ---------------------- | ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `{{ sep }}`                 | N/A                    | `' - ', not '-'`          | A fied separator for filenames, used when a folder or filename is composed of multiple Template Tags.                                                                   |
| `{{ date }}`                | `release_date`         | N/A                       | The release date of a media file. Does not have a default or fallback string.                                                                                          |
| `{{ studio }}`              | `studio.name`          | `misc`                    | The media file **Studio** from Stash                                                                                                                                    |
| `{{ performer.name }}`      | `performer.name`       | N/A                       | The performer name. Does not have a default of fallback string.                                                                                                         |
| `{{ performer.birthyear }}` | `performer.birth_year` | `__unknown`__             | The performer birth year.                                                                                                                                               |
| `{{ performer.country }}`   | `performer.country`    | `__unknown`__             | The performer country of birth.                                                                                                                                         |
| `{{ extension }}`           | N/A                    | N/A                       | The `MIME` extension of the file being moved. This **should** be the correct extension for the real file type, we do not trust the file extension of the original file. |


### A Note on `{{ sep }}`

The `{{ sep }}` tag is the default conditional separator for directory or file names containing multiple template tags. It defaults to  `-`  so templates with `{{ date }}` = `1979-01-01` get rendered as such:

- `{{ date }}{{ sep }}{{ studio }}` is rendered as `1979-01-01 - Studio Name`
- `{{ studio }}/{{ date }}{{ sep }}{{ title }}.{{ extension }}` is rendered as `Studio Name/1979-01-01 - Title.ext`

The use of `{{ sep }}` however allows for empty fallbacks to be omitted without breaking the filename, which is why we call it a *conditional separator* - it will only be rendered if the preceding tag is not empty.

This way, if `{{ date }}` evaluates to *empty* in the examples above:

- `{{ date }}{{ sep }}{{ studio }}` is rendered as `Studio Name`
- `{{ studio }}/{{ date }}{{ sep }}{{ title }}.{{ extension }}` is rendered as `Studio Name/Title.ext`

For this reason, the use of `{{ sep }}` should be preferred over using a literal  `-`  since, with an empty `{{ date }}`:

- `{{ studio }}/{{ date }}{{ sep }}{{ title }}.{{ extension }}` is rendered as `Studio Name/Title.ext`
- `{{ studio }}/{{ date }} - {{ title }}.{{ extension }}` is rendered as `Studio Name/ - Title.ext`

## Stash UI Only Settings


| Setting   | Type      | Default | Description                                                                              |
| --------- | --------- | ------- | ---------------------------------------------------------------------------------------- |
| `enabled` | `boolean` | `True`  | Used by Stash to enable/disable plugin hooks. Does not need to exist in the code itself. |


