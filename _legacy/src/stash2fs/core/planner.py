"""Pure path planning from templates."""

from __future__ import annotations

import os
from pathlib import PurePosixPath, PureWindowsPath

from stash2fs.config.settings import Settings
from stash2fs.core.models import File, Item, MovePlan
from stash2fs.core.templating import (
    build_render_context,
    render,
    sanitize_filename,
    select_template,
)


def _separator_for(settings: Settings, library_paths: list[str]) -> str:
    if settings.path_separator == "auto":
        if library_paths and "\\" in library_paths[0]:
            return "\\"
        return os.sep
    return settings.path_separator


def _normalize_path(path: str, sep: str) -> str:
    if sep == "\\":
        parts = PureWindowsPath(path).parts
        return str(PureWindowsPath(*parts) if parts else PureWindowsPath(path))
    parts = PurePosixPath(path).parts
    return str(PurePosixPath(*parts) if parts else PurePosixPath(path))


def _split_destination(rendered: str, sep: str) -> tuple[str, str]:
    if sep == "\\":
        folder = str(PureWindowsPath(rendered).parent)
        basename = PureWindowsPath(rendered).name
    else:
        folder = str(PurePosixPath(rendered).parent)
        basename = PurePosixPath(rendered).name
    return folder, basename


def _ensure_extension(basename: str, original_ext: str) -> str:
    if not original_ext:
        return basename
    stem = basename
    if "." in basename:
        stem = basename.rsplit(".", 1)[0]
    if not stem:
        stem = "untitled"
    sanitized_stem = sanitize_filename(stem)
    if not sanitized_stem:
        sanitized_stem = "untitled"
    return sanitized_stem + original_ext


def plan_move(
    item: Item,
    file: File,
    settings: Settings,
    library_paths: list[str],
    *,
    forced_template_name: str | None = None,
) -> MovePlan:
    """Compute a MovePlan for a single file (pure, no I/O)."""
    type_templates = settings.get_type_templates(item.type)
    sep = _separator_for(settings, library_paths)
    template_str, reason, template_name = select_template(
        item,
        file,
        type_templates,
        forced_name=forced_template_name,
    )
    context = build_render_context(
        item,
        file,
        library_paths=library_paths,
        path_separator=sep,
    )
    rendered = render(template_str, context)
    rendered = _normalize_path(rendered, sep)
    destination_folder, destination_basename = _split_destination(rendered, sep)
    destination_basename = _ensure_extension(destination_basename, file.extension)
    destination_basename = sanitize_filename(
        destination_basename.rsplit(".", 1)[0]
    ) + file.extension

    return MovePlan(
        file_id=file.id,
        item_id=item.id,
        item_type=item.type,
        current_path=file.path,
        destination_folder=destination_folder,
        destination_basename=destination_basename,
        selected_template=template_str,
        template_name=template_name,
        selection_reason=reason,
    )


def is_noop(plan: MovePlan, file: File, sep: str) -> bool:
    current_folder = _normalize_path(file.parent_dir, sep)
    current_basename = file.basename
    dest_folder = _normalize_path(plan.destination_folder, sep)
    return current_folder == dest_folder and current_basename == plan.destination_basename
