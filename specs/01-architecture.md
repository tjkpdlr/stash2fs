# Architecture

## Project Management and Technology Stack

- `stash2fs` is written in Python as a [click](https://click.palletsprojects.com/en/stable/) application and managed by [uv.](https://github.com/astral-sh/uv)
- configuration is managed internally by [pydantic-settings.](https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings)

## Non-Goals and Constraints

- `stash2fs` **never** moves or deletes files directly.
  - **all** operations are executed through the Stash GraphQL API.
  - **only** symbolic links in the **Index** may be managed directly by `stash2fs`.
- `stash2fs` **never** reads or writes directly to the Stash database.
  - **all** metadata operations are executed through the Stash GraphQL API.
  - **only** the **Index** may be set outside Stash-monitored directories.
- `stash2fs` **never** moves media files outside of Stash managed directories.
- `stash2fs` **never** modifies any files or data when executing in **dry run** mode.
- `stash2fs` **does not** provide its own GUI.

## File Handling

`stash2fs` never moves files directly, instead it **always** relies on the `moveFiles` mutation provided by the Stash GraphQL API. This ensures consistency with the Stash database and prevents bugs caused by drifting, and accidental moves outside the Stash Library which would cause files to be inacessible from Stash.

## The Library

The `stash2fs` **LIbrary** is simply the filesystem root where all files are saved by `stash2fs`. This is a directory managed by Stash, as files managed by `stash2fs` need to be managed by Stash itself.

The library layout is configurable, but defaults to the **template** 

```
{{ media_type }}/{{ studio }}/{{ date }} - {{ title }}.{{ extension }}
```

where:  

#### `{{ media_type }}`

Is the type of media that directory contains, such as `image`, `scene` or `gallery`

#### `{{ studio }}`

Is the studio a media file is atributed to. If that information is missing, this defaults to `__missing-studio__` 

#### `{{ date }}`

Is the date the media was published, as obtained from the Stash metadata for that media file, in the `YYYY-MM-DD` format. If that information is missing, the literal `YYYY-MM-DD` is used instead.

#### `{{ title }}`

Is the scene or gallery title, when available. When this metadata isn't available, like it's usually the case for images, the sanitized filename is used instead.

#### `{{ extension }}`

Is the true extension for the file being saved. That is: the extension for the MIME data type of the file, which may differ from the extension the file was obtained with. 

## The Index

The **Index** is a `stash2fs` concept unavailable in Stash. It consists of a filesystem path containing categorized symbolic links to files managed by `stash2fs`, designed to be easily browseable outside of Stash, such as by a file browser or shell.

The **Index** can be destroyed and rebuilt at anytime without any consequences to the managed files or Stash data. The `stash2fs index build` always deletes the whole **Index** and re-creates it from scratch, ensuring any broken symbolic links are cleared in the process.

### Building the Index

To build the **Index**, `stash2fs`:

1. creates all the supported **Index Roots,** then
2. iterates through all files in its **Library**, inspecting metadata of each media file, then
3. creates missing subdirectories inside each **Index Root** for any missing subdirectories
4. creates symbolic links pointing to the  file inside all the directories applicable.

The following index roots are supported:

#### `index/performers/by-name`

This **Index Root** contains one directory for each **performer name** found in Stash metadata for the managed files.

Inside each leaf directory there are symbolic links to all files that **performer** is attributed to.

Media Files with no attributed performers may be linked within a special directory named `index/performers/by-name/_unknown_` if there are no performers attributed in the metadata. This does not account for **media files** with multiple performers where some performers are attributed but others are not. In that case, the missing performers are simply ignored.

#### `index/performers/by-birthyear`

This **Index Root** contains one directory for each **birthday year** found in Stash metadata for the **performers** in managed files, then inside each **year** subdirectory, it contains one directory for each **performer name** born on that year. 

Inside each leaf directory there are symbolic links to all files that **performer** is attributed to.

Media files for performers with no known **birthday year** are linked within a special directory named **`index/performers/by-birthyear/__unknown__`

#### `index/performers/by-country`

This **Index Root** contains one directory for each **country of birth** found in Stash metadata for the **performers** in managed files, then inside each **country** subdirectory, it contains one directory for each **performer name** born on that country.

Inside each leaf directory there are symbolic links to all files that **performer** is attributed to.

Media files for performers with no known country of birth are linked within a special directory named `index/performers/by-country/_unknown_`.

#### `index/scenes/by-year`

This **Index Root** contains one directory for each **production year** found in **scene** metadata in the Stash database. 

Inside each leaf directory, there are symbolic links to all files beloning to **scenes** produced that year.

Scenes with no known production date are linked within a special directory named `index/scenes/by-year/_unknown_`.