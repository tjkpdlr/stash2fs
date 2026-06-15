"""Click CLI entrypoint."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import click

from stash2fs.config.settings import Settings, build_settings
from stash2fs.logging import PythonLogSink, configure_logging, get_logger
from stash2fs.stash.connection import from_settings
from stash2fs.stash.queries import HttpStashClient, StashError

PASS_SETTINGS = "settings"
PASS_CLIENT = "client"


def _verbosity_to_level(verbose: int, log_level: str | None) -> str:
    if log_level:
        return log_level.upper()
    if verbose >= 2:
        return "DEBUG"
    if verbose >= 1:
        return "DEBUG"
    return "INFO"


@click.group()
@click.option("--stash-url", default=None, help="Stash base URL.")
@click.option("--api-key", default=None, help="Stash API key.")
@click.option("--dry-run/--no-dry-run", default=None, help="Preview moves without executing.")
@click.option("--config", "config_path", type=click.Path(path_type=Path), default=None)
@click.option("-v", "--verbose", count=True)
@click.option("--log-level", default=None)
@click.pass_context
def cli(
    ctx: click.Context,
    stash_url: str | None,
    api_key: str | None,
    dry_run: bool | None,
    config_path: Path | None,
    verbose: int,
    log_level: str | None,
) -> None:
    """Organize Stash media files on disk from metadata templates."""
    cli_overrides: dict[str, Any] = {}
    if stash_url is not None:
        cli_overrides["stash"] = {"url": stash_url}
    if api_key is not None:
        stash_override = cli_overrides.get("stash", {})
        if not isinstance(stash_override, dict):
            stash_override = {}
        stash_override["api_key"] = api_key
        cli_overrides["stash"] = stash_override
    if dry_run is not None:
        cli_overrides["dry_run"] = dry_run
    level = _verbosity_to_level(verbose, log_level)
    cli_overrides["log"] = {"level": level}

    try:
        settings = build_settings(config_path=config_path, cli_overrides=cli_overrides)
    except (ValueError, TypeError) as exc:
        click.echo(f"Configuration error: {exc}", err=True)
        sys.exit(1)

    configure_logging(PythonLogSink(settings.log.level))
    ctx.obj = {PASS_SETTINGS: settings}

    try:
        connection = from_settings(settings)
        client = HttpStashClient(connection)
        ctx.obj[PASS_CLIENT] = client
    except Exception as exc:
        click.echo(f"Connection error: {exc}", err=True)
        sys.exit(1)


def _run_mv(
    ctx: click.Context,
    media_type: str,
    item_id: str | None,
    all_items: bool,
    template_name: str | None,
    tags: tuple[str, ...],
    studios: tuple[str, ...],
    path_prefixes: tuple[str, ...],
    organized: bool | None,
) -> None:
    from stash2fs.core.models import BulkFilters
    from stash2fs.core.mover import format_outcome_line, process_bulk, process_item, summarize

    settings: Settings = ctx.obj[PASS_SETTINGS]
    client: HttpStashClient = ctx.obj[PASS_CLIENT]
    log = get_logger()

    if all_items and item_id:
        click.echo("Cannot specify both an ID and --all", err=True)
        sys.exit(1)
    if not all_items and not item_id:
        click.echo("Specify an item ID or --all", err=True)
        sys.exit(1)

    try:
        settings.get_type_templates(media_type)  # type: ignore[arg-type]
    except ValueError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)

    outcomes = []
    try:
        if item_id:
            outcomes = process_item(
                client,
                settings,
                media_type,  # type: ignore[arg-type]
                item_id,
                forced_template_name=template_name,
            )
        else:
            filters = BulkFilters(
                tags=list(tags),
                studios=list(studios),
                path_prefixes=list(path_prefixes),
                organized=organized,
            )

            def progress(current: int, total: int, item: Any) -> None:
                log.info(f"Processing {current}/{total}: {item.type} {item.id}")

            outcomes = process_bulk(
                client,
                settings,
                media_type,  # type: ignore[arg-type]
                filters,
                progress_callback=progress,
            )
    except StashError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)
    finally:
        client.close()

    for outcome in outcomes:
        click.echo(format_outcome_line(outcome, dry_run=settings.dry_run))

    summary = summarize(outcomes)
    click.echo(
        f"Summary: moved={summary.moved} unchanged={summary.unchanged} "
        f"skipped={summary.skipped} failed={summary.failed}"
    )

    if summary.failed > 0:
        sys.exit(2)


# Import subcommands to register them
from stash2fs.cli import gallery, image, scene  # noqa: E402, F401
