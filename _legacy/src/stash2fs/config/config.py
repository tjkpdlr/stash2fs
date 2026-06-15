"""Default configuration values for stash2fs."""

DEFAULT_STASH_URL = "http://localhost:9999"
DEFAULT_STASH_TIMEOUT_SECONDS = 30

DEFAULT_DRY_RUN = False
DEFAULT_ENABLED = True
DEFAULT_ON_COLLISION = "skip"
DEFAULT_VALIDATE_LIBRARY_PATHS = True
DEFAULT_PATH_SEPARATOR = "auto"

DEFAULT_LOG_LEVEL = "INFO"

DEFAULT_SCENE_TEMPLATE = (
    "{{ library }}/{{ studio }}/{% if date %}{{ date }} - {% endif %}{{ title }}{{ ext }}"
)
DEFAULT_IMAGE_TEMPLATE = (
    "{{ library }}/Images/{% if studio %}{{ studio }}/{% endif %}{{ title }}{{ ext }}"
)
DEFAULT_GALLERY_TEMPLATE = (
    "{{ library }}/Galleries/{% if studio %}{{ studio }}/{% endif %}{{ title }}{{ ext }}"
)

DEFAULT_TEMPLATES: dict[str, dict[str, object]] = {
    "scene": {
        "default": DEFAULT_SCENE_TEMPLATE,
        "by_tag": {},
        "by_studio": {},
        "by_path": {},
    },
    "image": {
        "default": DEFAULT_IMAGE_TEMPLATE,
        "by_tag": {},
        "by_studio": {},
        "by_path": {},
    },
    "gallery": {
        "default": DEFAULT_GALLERY_TEMPLATE,
        "by_tag": {},
        "by_studio": {},
        "by_path": {},
    },
}

DEFAULTS: dict[str, object] = {
    "stash": {
        "url": DEFAULT_STASH_URL,
        "api_key": None,
        "timeout_seconds": DEFAULT_STASH_TIMEOUT_SECONDS,
    },
    "dry_run": DEFAULT_DRY_RUN,
    "enabled": DEFAULT_ENABLED,
    "on_collision": DEFAULT_ON_COLLISION,
    "validate_library_paths": DEFAULT_VALIDATE_LIBRARY_PATHS,
    "path_separator": DEFAULT_PATH_SEPARATOR,
    "templates": DEFAULT_TEMPLATES,
    "log": {
        "level": DEFAULT_LOG_LEVEL,
        "dry_run_report": None,
    },
}
