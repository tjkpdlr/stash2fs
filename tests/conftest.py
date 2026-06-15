"""Fake Stash client for tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from stash2fs.core.models import BulkFilters, Item, MediaType
from stash2fs.stash.queries import _parse_item

FIXTURES = Path(__file__).parent / "fixtures"


class FakeStashClient:
    def __init__(
        self,
        *,
        library_paths: list[str] | None = None,
        existing_paths: set[str] | None = None,
    ) -> None:
        self.library_paths = library_paths or ["/media/library", "/media/incoming"]
        self.existing_paths = existing_paths or set()
        self.move_calls: list[dict[str, str]] = []
        self.plugin_settings: dict[str, Any] = {}
        self._items: dict[tuple[MediaType, str], Item] = {}
        self._load_fixtures()

    def _load_fixture(self, name: str) -> dict[str, Any]:
        return json.loads((FIXTURES / name).read_text())

    def _load_fixtures(self) -> None:
        scene = self._load_fixture("scene_multi_file.json")["findScene"]
        self._items[("scene", "100")] = _parse_item(scene, "scene")
        image = self._load_fixture("image.json")["findImage"]
        self._items[("image", "200")] = _parse_item(image, "image")
        zip_g = self._load_fixture("gallery_zip.json")["findGallery"]
        self._items[("gallery", "300")] = _parse_item(zip_g, "gallery")
        folder_g = self._load_fixture("gallery_folder.json")["findGallery"]
        self._items[("gallery", "301")] = _parse_item(folder_g, "gallery")

    def get_library_paths(self) -> list[str]:
        return self.library_paths

    def find_scene(self, scene_id: str) -> Item | None:
        return self._items.get(("scene", scene_id))

    def find_image(self, image_id: str) -> Item | None:
        return self._items.get(("image", image_id))

    def find_gallery(self, gallery_id: str) -> Item | None:
        return self._items.get(("gallery", gallery_id))

    def find_scenes(self, filters: BulkFilters) -> list[Item]:
        return [item for (t, _), item in self._items.items() if t == "scene"]

    def find_images(self, filters: BulkFilters) -> list[Item]:
        return [item for (t, _), item in self._items.items() if t == "image"]

    def find_galleries(self, filters: BulkFilters) -> list[Item]:
        return [item for (t, _), item in self._items.items() if t == "gallery"]

    def move_file(
        self, file_id: str, destination_folder: str, destination_basename: str
    ) -> bool:
        self.move_calls.append(
            {
                "file_id": file_id,
                "destination_folder": destination_folder,
                "destination_basename": destination_basename,
            }
        )
        return True

    def file_exists_at_path(self, path: str) -> bool:
        return path in self.existing_paths

    def get_plugin_settings(self, plugin_id: str) -> dict[str, Any]:
        return dict(self.plugin_settings)

    def set_plugin_setting(self, plugin_id: str, key: str, value: Any) -> None:
        self.plugin_settings[key] = value

    def close(self) -> None:
        return None
