"""Tests for planner and validation."""

from stash2fs.config.settings import build_settings
from stash2fs.core.models import File, Item, Studio
from stash2fs.core.planner import is_noop, plan_move
from stash2fs.core.validation import is_under_library_path, validate_plan

LIBRARY_PATHS = ["/media/library", "/media/incoming"]


def test_plan_move_splits_destination() -> None:
    settings = build_settings()
    item = Item(
        id="100",
        type="scene",
        title="Big Buck Bunny",
        date="2008-05-20",
        studio=Studio(name="Blender Institute"),
    )
    file = File(
        id="f1",
        path="/media/library/scenes/bbb.mp4",
        basename="bbb.mp4",
    )
    plan = plan_move(item, file, settings, LIBRARY_PATHS)
    assert plan.destination_folder == "/media/library/Blender Institute"
    assert plan.destination_basename == "2008-05-20 - Big Buck Bunny.mp4"
    assert plan.selection_reason == "default"


def test_noop_detection() -> None:
    settings = build_settings()
    item = Item(id="1", type="scene", title="Same")
    file = File(
        id="f",
        path="/media/library/Same.mp4",
        basename="Same.mp4",
    )
    plan = plan_move(item, file, settings, LIBRARY_PATHS)
    assert is_noop(plan, file, "/")


def test_library_path_containment() -> None:
    assert is_under_library_path("/media/library/sub", LIBRARY_PATHS)
    assert is_under_library_path("/media/library", LIBRARY_PATHS)
    assert not is_under_library_path("/tmp/outside", LIBRARY_PATHS)


def test_collision_skip() -> None:
    settings = build_settings()
    item = Item(id="1", type="scene", title="X")
    file = File(id="f", path="/media/library/old.mp4", basename="old.mp4")
    plan = plan_move(item, file, settings, LIBRARY_PATHS)

    def exists(path: str) -> bool:
        return path.endswith("X.mp4")

    reason = validate_plan(
        plan,
        validate_library_paths=True,
        library_paths=LIBRARY_PATHS,
        existence_checker=exists,
        planned_destinations=set(),
    )
    assert reason is not None
    assert "collision" in reason


def test_outside_library_skip() -> None:
    settings = build_settings(
        cli_overrides={
            "templates": {
                "scene": {
                    "default": "/tmp/{{ title }}{{ ext }}",
                    "by_tag": {},
                    "by_studio": {},
                    "by_path": {},
                }
            }
        }
    )
    item = Item(id="1", type="scene", title="Outside")
    file = File(id="f", path="/media/library/old.mp4", basename="old.mp4")
    plan = plan_move(item, file, settings, LIBRARY_PATHS)
    reason = validate_plan(
        plan,
        validate_library_paths=True,
        library_paths=LIBRARY_PATHS,
        existence_checker=lambda _: False,
        planned_destinations=set(),
    )
    assert reason is not None
    assert "outside library" in reason
