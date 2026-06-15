"""Scene CLI commands."""

from __future__ import annotations

import click

from stash2fs.cli.main import cli


@cli.group()
def scene() -> None:
    """Scene operations."""


@scene.command("mv")
@click.argument("item_id", required=False)
@click.option("--all", "all_items", is_flag=True, help="Process all scenes.")
@click.option("--template-name", default=None, help="Force a named template override.")
@click.option("--tag", "tags", multiple=True)
@click.option("--studio", "studios", multiple=True)
@click.option("--path-prefix", "path_prefixes", multiple=True)
@click.option("--organized/--unorganized", default=None)
@click.pass_context
def scene_mv(
    ctx: click.Context,
    item_id: str | None,
    all_items: bool,
    template_name: str | None,
    tags: tuple[str, ...],
    studios: tuple[str, ...],
    path_prefixes: tuple[str, ...],
    organized: bool | None,
) -> None:
    """Move scene file(s) to template-derived locations."""
    from stash2fs.cli.main import _run_mv

    _run_mv(
        ctx,
        "scene",
        item_id,
        all_items,
        template_name,
        tags,
        studios,
        path_prefixes,
        organized,
    )
