"""Move orchestration: resolve -> plan -> validate -> moveFiles."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from stash2fs.config.settings import Settings
from stash2fs.core.models import BulkFilters, Item, MediaType, MoveOutcome, MovePlan, MoveStatus, RunSummary
from stash2fs.core.planner import is_noop, plan_move
from stash2fs.core.validation import validate_plan
from stash2fs.logging import get_logger
from stash2fs.stash.queries import StashClient, StashError

ProgressCallback = Callable[[int, int, Item], None]

PLUGIN_ID = "stash2fs"


def _destination_path(plan_folder: str, plan_basename: str) -> str:
    from os.path import join

    return join(plan_folder, plan_basename)


def _outcome_from_plan(
    plan: MovePlan,
    status: MoveStatus,
    reason: str = "",
) -> MoveOutcome:
    return MoveOutcome(
        status=status,
        item_id=plan.item_id,
        item_type=plan.item_type,
        file_id=plan.file_id,
        current_path=plan.current_path,
        destination_path=_destination_path(plan.destination_folder, plan.destination_basename),
        template_name=plan.template_name,
        selection_reason=plan.selection_reason,
        reason=reason,
    )


def _is_folder_gallery(item: Item) -> bool:
    if item.type != "gallery":
        return False
    if item.folder_path and not item.files:
        return True
    if item.files:
        for f in item.files:
            if f.basename.lower().endswith(".zip"):
                return False
        return bool(item.folder_path)
    return bool(item.folder_path)


def process_item_files(
    client: StashClient,
    settings: Settings,
    item: Item,
    library_paths: list[str],
    *,
    forced_template_name: str | None = None,
    dry_run_report: Path | None = None,
) -> list[MoveOutcome]:
    """Process all files for a resolved item."""
    log = get_logger()
    outcomes: list[MoveOutcome] = []

    if item.type == "gallery" and _is_folder_gallery(item):
        log.warning(
            f"skipped: folder-based gallery not supported in v1 (item {item.id})"
        )
        outcomes.append(
            MoveOutcome(
                status="skipped",
                item_id=item.id,
                item_type=item.type,
                reason="folder-based gallery not supported in v1",
            )
        )
        return outcomes

    if not item.files:
        log.warning(f"skipped: item {item.id} has no files")
        outcomes.append(
            MoveOutcome(
                status="skipped",
                item_id=item.id,
                item_type=item.type,
                reason="no files",
            )
        )
        return outcomes

    from stash2fs.core.planner import _separator_for

    sep = _separator_for(settings, library_paths)
    planned_destinations: set[str] = set()

    def existence_checker(path: str) -> bool:
        return client.file_exists_at_path(path)

    for file in item.files:
        plan = plan_move(
            item,
            file,
            settings,
            library_paths,
            forced_template_name=forced_template_name,
        )

        if is_noop(plan, file, sep):
            outcomes.append(_outcome_from_plan(plan, "unchanged"))
            continue

        skip_reason = validate_plan(
            plan,
            validate_library_paths=settings.validate_library_paths,
            library_paths=library_paths,
            existence_checker=existence_checker,
            planned_destinations=planned_destinations,
        )
        if skip_reason:
            if skip_reason == "unchanged":
                outcomes.append(_outcome_from_plan(plan, "unchanged"))
            else:
                outcomes.append(_outcome_from_plan(plan, "skipped", skip_reason))
            continue

        dest_full = _destination_path(plan.destination_folder, plan.destination_basename)
        planned_destinations.add(dest_full)

        if settings.dry_run:
            if dry_run_report:
                dry_run_report.parent.mkdir(parents=True, exist_ok=True)
                with dry_run_report.open("a") as fh:
                    fh.write(f"{item.id}|{plan.current_path}|{dest_full}\n")
            outcomes.append(_outcome_from_plan(plan, "moved"))
            continue

        try:
            success = client.move_file(
                plan.file_id,
                plan.destination_folder,
                plan.destination_basename,
            )
        except StashError as exc:
            log.error(f"move failed for file {plan.file_id}: {exc}")
            outcomes.append(_outcome_from_plan(plan, "failed", str(exc)))
            continue

        if success:
            outcomes.append(_outcome_from_plan(plan, "moved"))
        else:
            log.error(
                f"moveFiles returned false for file {plan.file_id}: "
                f"{plan.current_path} -> {dest_full}"
            )
            outcomes.append(_outcome_from_plan(plan, "failed", "moveFiles returned false"))

    return outcomes


def resolve_item(client: StashClient, media_type: MediaType, item_id: str) -> Item | None:
    if media_type == "scene":
        return client.find_scene(item_id)
    if media_type == "image":
        return client.find_image(item_id)
    return client.find_gallery(item_id)


def process_item(
    client: StashClient,
    settings: Settings,
    media_type: MediaType,
    item_id: str,
    library_paths: list[str] | None = None,
    *,
    forced_template_name: str | None = None,
) -> list[MoveOutcome]:
    paths = library_paths if library_paths is not None else client.get_library_paths()
    item = resolve_item(client, media_type, item_id)
    if item is None:
        raise StashError("resolve_item", f"{media_type} {item_id} not found")
    report_path = settings.log.dry_run_report
    return process_item_files(
        client,
        settings,
        item,
        paths,
        forced_template_name=forced_template_name,
        dry_run_report=report_path,
    )


def process_bulk(
    client: StashClient,
    settings: Settings,
    media_type: MediaType,
    filters: BulkFilters,
    *,
    progress_callback: ProgressCallback | None = None,
    library_paths: list[str] | None = None,
) -> list[MoveOutcome]:
    paths = library_paths if library_paths is not None else client.get_library_paths()
    if media_type == "scene":
        items = client.find_scenes(filters)
    elif media_type == "image":
        items = client.find_images(filters)
    else:
        items = client.find_galleries(filters)

    all_outcomes: list[MoveOutcome] = []
    total = len(items)
    report_path = settings.log.dry_run_report
    if settings.dry_run and report_path and report_path.exists():
        report_path.unlink()

    for index, item in enumerate(items, start=1):
        if progress_callback:
            progress_callback(index, total, item)
        outcomes = process_item_files(
            client,
            settings,
            item,
            paths,
            dry_run_report=report_path,
        )
        all_outcomes.extend(outcomes)

    return all_outcomes


def format_outcome_line(outcome: MoveOutcome, *, dry_run: bool = False) -> str:
    prefix = "DRY-RUN " if dry_run else ""
    dest = outcome.destination_path or outcome.current_path
    if outcome.status == "moved":
        return (
            f"{prefix}MOVE {outcome.item_id} {outcome.item_type}: "
            f"{outcome.current_path} -> {dest} "
            f"[template={outcome.template_name} reason={outcome.selection_reason}]"
        )
    if outcome.status == "unchanged":
        return f"UNCHANGED {outcome.item_id} {outcome.item_type}: {outcome.current_path}"
    if outcome.status == "skipped":
        return f"SKIPPED {outcome.item_id} {outcome.item_type}: {outcome.reason}"
    return f"FAILED {outcome.item_id} {outcome.item_type}: {outcome.reason}"


def summarize(outcomes: list[MoveOutcome]) -> RunSummary:
    summary = RunSummary()
    for outcome in outcomes:
        summary.add(outcome)
    return summary
