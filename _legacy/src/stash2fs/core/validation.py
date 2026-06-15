"""Validation for move plans (pure given injected existence checker)."""

from __future__ import annotations

import os
from collections.abc import Callable
from typing import TYPE_CHECKING

from stash2fs.core.models import MovePlan

if TYPE_CHECKING:
    pass

ExistenceChecker = Callable[[str], bool]


def _normalize(path: str) -> str:
    return os.path.normpath(path)


def is_absolute_path(path: str) -> bool:
    return os.path.isabs(path)


def is_under_library_path(destination_folder: str, library_paths: list[str]) -> bool:
    normalized_dest = _normalize(destination_folder)
    for lib in library_paths:
        normalized_lib = _normalize(lib)
        if normalized_dest == normalized_lib:
            return True
        if normalized_dest.startswith(normalized_lib + os.sep):
            return True
    return False


def validate_plan(
    plan: MovePlan,
    *,
    validate_library_paths: bool,
    library_paths: list[str],
    existence_checker: ExistenceChecker,
    planned_destinations: set[str],
) -> str | None:
    """Return skip reason if invalid, else None."""
    if not is_absolute_path(plan.destination_folder):
        return "destination is not absolute"

    if validate_library_paths and not is_under_library_path(
        plan.destination_folder, library_paths
    ):
        return f"destination outside library paths: {plan.destination_folder}"

    dest_full = _normalize(
        os.path.join(plan.destination_folder, plan.destination_basename)
    )
    current_full = _normalize(plan.current_path)

    if dest_full == current_full:
        return "unchanged"

    if dest_full in planned_destinations:
        return f"collision: duplicate destination within item: {dest_full}"

    if existence_checker(dest_full) and dest_full != current_full:
        return f"collision: file exists at destination: {dest_full}"

    return None
