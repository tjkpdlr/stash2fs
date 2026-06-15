"""Tests for templating engine."""

from stash2fs.config.settings import TypeTemplates
from stash2fs.core.models import File, Item, Performer, Studio, Tag
from stash2fs.core.templating import (
    build_render_context,
    render,
    sanitize_filename,
    select_template,
)


def test_render_context_variables() -> None:
    item = Item(
        id="1",
        type="scene",
        title="Title",
        code="CODE",
        date="2020-03-04",
        rating100=85,
        studio=Studio(name="Child", parent=Studio(name="Parent")),
        tags=[Tag(name="tag1")],
        performers=[Performer(name="Alice"), Performer(name="Bob")],
    )
    file = File(
        id="f1",
        path="/media/library/foo/bar.mp4",
        basename="bar.mp4",
        height=1080,
        width=1920,
        video_codec="h264",
    )
    ctx = build_render_context(
        item, file, library_paths=["/media/library"], path_separator="/"
    )
    assert ctx.library == "/media/library"
    assert ctx.title == "Title"
    assert ctx.year == "2020"
    assert ctx.studio == "Child"
    assert ctx.studio_hierarchy == "Parent/Child"
    assert ctx.resolution == "1080p"
    assert ctx.performer == "Alice"
    assert ctx.performers == ["Alice", "Bob"]


def test_missing_metadata_renders_empty() -> None:
    item = Item(id="1", type="image")
    file = File(id="f", path="/media/x.jpg", basename="x.jpg")
    ctx = build_render_context(item, file, library_paths=["/media"])
    rendered = render("{{ studio }}/{{ date }}/{{ title }}{{ ext }}", ctx)
    assert rendered == "//x.jpg"


def test_sanitize_removes_illegal_chars() -> None:
    assert sanitize_filename('bad<>:"/\\|?* name') == "bad name"


def test_template_selection_priority() -> None:
    templates = TypeTemplates(
        default="default",
        by_tag={"Animation": "by-tag"},
        by_studio={"Blender": "by-studio"},
        by_path={"/media/incoming": "by-path"},
    )
    item = Item(
        id="1",
        type="scene",
        tags=[Tag(name="Animation")],
        studio=Studio(name="Blender"),
    )
    file = File(id="f", path="/media/incoming/x.mp4", basename="x.mp4")

    tpl, reason, name = select_template(item, file, templates)
    assert tpl == "by-tag"
    assert reason == "tag"

    item2 = Item(id="2", type="scene", studio=Studio(name="Blender"))
    tpl2, reason2, _ = select_template(item2, file, templates)
    assert tpl2 == "by-studio"
    assert reason2 == "studio"

    item3 = Item(id="3", type="scene")
    tpl3, reason3, _ = select_template(item3, file, templates)
    assert tpl3 == "by-path"
    assert reason3 == "path"

    file4 = File(id="f4", path="/elsewhere/x.mp4", basename="x.mp4")
    tpl4, reason4, _ = select_template(item3, file4, templates)
    assert tpl4 == "default"
    assert reason4 == "default"


def test_path_longest_prefix_wins() -> None:
    templates = TypeTemplates(
        default="default",
        by_path={
            "/media": "short",
            "/media/incoming": "long",
        },
    )
    item = Item(id="1", type="scene")
    file = File(id="f", path="/media/incoming/x.mp4", basename="x.mp4")
    tpl, reason, name = select_template(item, file, templates)
    assert tpl == "long"
    assert name == "/media/incoming"
