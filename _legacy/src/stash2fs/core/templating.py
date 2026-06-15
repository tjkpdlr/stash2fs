"""Jinja2 templating, variable mapping, and template selection."""

from __future__ import annotations

import os
import re
from typing import TYPE_CHECKING

from jinja2 import Environment, Undefined

from stash2fs.core.models import File, Item, RenderContext, SelectionReason, Studio

if TYPE_CHECKING:
    from stash2fs.config.settings import TypeTemplates

_ILLEGAL_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_WHITESPACE = re.compile(r"\s+")


class SilentUndefined(Undefined):
    """Render missing variables as empty string."""

    def __str__(self) -> str:
        return ""

    def __iter__(self):  # type: ignore[no-untyped-def]
        return iter([])

    def __bool__(self) -> bool:
        return False


def sanitize_filename(value: str) -> str:
    """Strip/replace characters illegal in filenames; collapse whitespace."""
    cleaned = _ILLEGAL_FILENAME_CHARS.sub("", value)
    return _WHITESPACE.sub(" ", cleaned).strip()


def _resolution_label(height: int | None) -> str:
    if height is None:
        return ""
    thresholds = [
        (2160, "2160p"),
        (1440, "1440p"),
        (1080, "1080p"),
        (720, "720p"),
        (480, "480p"),
        (360, "360p"),
    ]
    for threshold, label in thresholds:
        if height >= threshold:
            return label
    return f"{height}p"


def _studio_from_data(data: dict[str, object] | None) -> Studio | None:
    if not data:
        return None
    parent_raw = data.get("parent_studio")
    parent = _studio_from_data(parent_raw) if isinstance(parent_raw, dict) else None
    name = str(data.get("name") or "")
    return Studio(name=name, parent=parent)


def build_render_context(
    item: Item,
    file: File,
    *,
    library_paths: list[str],
    path_separator: str = "/",
) -> RenderContext:
    """Build template-facing variables from item + file."""
    library = _find_library_root(file.path, library_paths)
    current_dir = file.parent_dir
    ext = file.extension
    title = item.title.strip() or file.stem
    date = item.date or ""
    year = date[:4] if len(date) >= 4 else ""
    studio_obj = item.studio
    studio = studio_obj.name if studio_obj else ""
    hierarchy = studio_obj.hierarchy_names() if studio_obj else []
    sep = path_separator if path_separator != "auto" else os.sep
    studio_hierarchy = sep.join(hierarchy)
    rating = str(item.rating100) if item.rating100 is not None else ""
    performers = [p.name for p in item.performers if p.name]
    performer = performers[0] if performers else ""
    tags = [t.name for t in item.tags if t.name]

    return RenderContext(
        library=library,
        current_dir=current_dir,
        ext=ext,
        title=title,
        date=date,
        year=year,
        studio=studio,
        studio_hierarchy=studio_hierarchy,
        code=item.code or "",
        rating=rating,
        performers=performers,
        performer=performer,
        tags=tags,
        resolution=_resolution_label(file.height),
        width=str(file.width) if file.width is not None else "",
        height=str(file.height) if file.height is not None else "",
        video_codec=file.video_codec or "",
        audio_codec=file.audio_codec or "",
        frame_rate=str(file.frame_rate) if file.frame_rate is not None else "",
        bit_rate=str(file.bit_rate) if file.bit_rate is not None else "",
        duration=str(file.duration) if file.duration is not None else "",
        id=item.id,
        type=item.type,
    )


def _find_library_root(file_path: str, library_paths: list[str]) -> str:
    normalized_file = os.path.normpath(file_path)
    best = ""
    best_len = -1
    for lib in library_paths:
        normalized_lib = os.path.normpath(lib)
        if (
            normalized_file == normalized_lib or normalized_file.startswith(normalized_lib + os.sep)
        ) and len(normalized_lib) > best_len:
            best = normalized_lib
            best_len = len(normalized_lib)
    return best


def _create_environment() -> Environment:
    env = Environment(
        undefined=SilentUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=False,
    )
    env.filters["sanitize"] = sanitize_filename
    return env


_ENV = _create_environment()


def render(template_str: str, context: RenderContext) -> str:
    """Render a template string against a RenderContext."""
    template = _ENV.from_string(template_str)
    return template.render(**context.as_dict())


def select_template(
    item: Item,
    file: File,
    type_templates: TypeTemplates,
    *,
    forced_name: str | None = None,
) -> tuple[str, SelectionReason, str]:
    """Select template by priority: tag > studio > path > default."""
    if forced_name:
        for mapping, _reason in (
            (type_templates.by_tag, "tag"),
            (type_templates.by_studio, "studio"),
            (type_templates.by_path, "path"),
        ):
            if forced_name in mapping:
                return mapping[forced_name], "forced", forced_name
        raise ValueError(f"template name '{forced_name}' not found in overrides")

    tag_names = {t.name for t in item.tags}
    for tag_key, template in type_templates.by_tag.items():
        if tag_key in tag_names:
            return template, "tag", tag_key

    studio_names: list[str] = []
    if item.studio:
        studio_names = item.studio.hierarchy_names()

    for studio_key, template in type_templates.by_studio.items():
        if studio_key in studio_names:
            return template, "studio", studio_key

    best_prefix = ""
    best_template = ""
    for path_prefix, template in type_templates.by_path.items():
        if file.path.startswith(path_prefix) and len(path_prefix) > len(best_prefix):
            best_prefix = path_prefix
            best_template = template
    if best_template:
        return best_template, "path", best_prefix

    return type_templates.default, "default", "default"
