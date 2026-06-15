"""GraphQL transport and typed query wrappers."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

import httpx

from stash2fs.core.models import BulkFilters, File, Item, MediaType, Performer, Studio, Tag
from stash2fs.stash.connection import StashConnection


class StashError(Exception):
    """Raised when a Stash GraphQL request fails."""

    def __init__(self, query_name: str, message: str) -> None:
        self.query_name = query_name
        super().__init__(f"{query_name}: {message}")


@runtime_checkable
class StashClient(Protocol):
    def get_library_paths(self) -> list[str]: ...

    def find_scene(self, scene_id: str) -> Item | None: ...

    def find_image(self, image_id: str) -> Item | None: ...

    def find_gallery(self, gallery_id: str) -> Item | None: ...

    def find_scenes(self, filters: BulkFilters) -> list[Item]: ...

    def find_images(self, filters: BulkFilters) -> list[Item]: ...

    def find_galleries(self, filters: BulkFilters) -> list[Item]: ...

    def move_file(
        self, file_id: str, destination_folder: str, destination_basename: str
    ) -> bool: ...

    def file_exists_at_path(self, path: str) -> bool: ...

    def get_plugin_settings(self, plugin_id: str) -> dict[str, Any]: ...

    def set_plugin_setting(self, plugin_id: str, key: str, value: Any) -> None: ...


FIND_SCENE = """
query FindScene($id: ID!) {
  findScene(id: $id) {
    id title code date rating100 organized
    studio { name parent_studio { name parent_studio { name } } }
    tags { name }
    performers { name gender }
    files {
      id path basename width height
      video_codec audio_codec frame_rate bit_rate duration
    }
  }
}
"""

FIND_IMAGE = """
query FindImage($id: ID!) {
  findImage(id: $id) {
    id title date rating100 organized
    studio { name parent_studio { name parent_studio { name } } }
    tags { name }
    performers { name }
    visual_files {
      ... on ImageFile {
        id path basename width height
      }
    }
  }
}
"""

FIND_GALLERY = """
query FindGallery($id: ID!) {
  findGallery(id: $id) {
    id title date rating100 organized folder_path
    studio { name parent_studio { name parent_studio { name } } }
    tags { name }
    performers { name }
    files { id path basename }
  }
}
"""

FIND_SCENES = """
query FindScenes($filter: FindFilterType, $scene_filter: SceneFilterType) {
  findScenes(filter: $filter, scene_filter: $scene_filter) {
    count
    scenes {
      id title code date rating100 organized
      studio { name parent_studio { name } }
      tags { name }
      performers { name gender }
      files { id path basename width height video_codec audio_codec frame_rate bit_rate duration }
    }
  }
}
"""

FIND_IMAGES = """
query FindImages($filter: FindFilterType, $image_filter: ImageFilterType) {
  findImages(filter: $filter, image_filter: $image_filter) {
    count
    images {
      id title date rating100 organized
      studio { name parent_studio { name } }
      tags { name }
      performers { name }
      visual_files { ... on ImageFile { id path basename width height } }
    }
  }
}
"""

FIND_GALLERIES = """
query FindGalleries($filter: FindFilterType, $gallery_filter: GalleryFilterType) {
  findGalleries(filter: $filter, gallery_filter: $gallery_filter) {
    count
    galleries {
      id title date rating100 organized folder_path
      studio { name parent_studio { name } }
      tags { name }
      performers { name }
      files { id path basename }
    }
  }
}
"""

CONFIGURATION = """
query Configuration {
  configuration {
    general { stashes { path } }
    plugins
  }
}
"""

MOVE_FILES = """
mutation MoveFiles($input: MoveFilesInput!) {
  moveFiles(input: $input)
}
"""

FIND_FILE_BY_PATH = """
query FindFiles($filter: FindFilterType) {
  findFiles(filter: $filter) {
    count
    files { id path }
  }
}
"""

CONFIGURE_PLUGIN = """
mutation ConfigurePlugin($plugin_id: ID!, $enabled: Boolean, $settings: Map) {
  configurePlugin(plugin_id: $plugin_id, enabled: $enabled, settings: $settings) {
    id
  }
}
"""


def _parse_studio(data: dict[str, Any] | None) -> Studio | None:
    if not data:
        return None
    parent_raw = data.get("parent_studio")
    parent = _parse_studio(parent_raw) if isinstance(parent_raw, dict) else None
    return Studio(name=str(data.get("name") or ""), parent=parent)


def _parse_file(data: dict[str, Any]) -> File:
    return File(
        id=str(data.get("id", "")),
        path=str(data.get("path") or ""),
        basename=str(data.get("basename") or ""),
        width=data.get("width"),
        height=data.get("height"),
        video_codec=data.get("video_codec"),
        audio_codec=data.get("audio_codec"),
        frame_rate=data.get("frame_rate"),
        bit_rate=data.get("bit_rate"),
        duration=data.get("duration"),
    )


def _parse_item(data: dict[str, Any], media_type: MediaType) -> Item:
    tags = [Tag(name=str(t.get("name") or "")) for t in (data.get("tags") or [])]
    performers = [
        Performer(name=str(p.get("name") or ""), gender=p.get("gender"))
        for p in (data.get("performers") or [])
    ]
    files_raw = (
        data.get("visual_files") or [] if media_type == "image" else data.get("files") or []
    )
    files = [_parse_file(f) for f in files_raw if isinstance(f, dict)]
    return Item(
        id=str(data.get("id", "")),
        type=media_type,
        title=str(data.get("title") or ""),
        code=str(data.get("code") or ""),
        date=str(data.get("date") or ""),
        rating100=data.get("rating100"),
        organized=bool(data.get("organized")),
        studio=_parse_studio(data.get("studio")),
        tags=tags,
        performers=performers,
        files=files,
        folder_path=data.get("folder_path"),
    )


class HttpStashClient:
    """httpx-based Stash GraphQL client."""

    def __init__(self, connection: StashConnection) -> None:
        self._connection = connection
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if connection.api_key is not None:
            headers["ApiKey"] = connection.api_key.get_secret_value()
        cookies: dict[str, str] = {}
        if connection.session_cookie:
            cookies["session"] = connection.session_cookie
        self._client = httpx.Client(
            headers=headers,
            cookies=cookies,
            timeout=connection.timeout_seconds,
        )
        self._library_paths: list[str] | None = None

    def close(self) -> None:
        self._client.close()

    def _execute(self, query_name: str, query: str, variables: dict[str, Any] | None = None) -> Any:
        payload: dict[str, Any] = {"query": query}
        if variables is not None:
            payload["variables"] = variables
        try:
            response = self._client.post(self._connection.url, json=payload)
        except httpx.HTTPError as exc:
            raise StashError(query_name, str(exc)) from exc
        if response.status_code != 200:
            raise StashError(query_name, f"HTTP {response.status_code}")
        body = response.json()
        if errors := body.get("errors"):
            messages = "; ".join(str(e.get("message", e)) for e in errors)
            raise StashError(query_name, messages)
        return body.get("data")

    def get_library_paths(self) -> list[str]:
        if self._library_paths is not None:
            return self._library_paths
        data = self._execute("Configuration", CONFIGURATION)
        stashes = (
            data.get("configuration", {}).get("general", {}).get("stashes") or []
        )
        self._library_paths = [str(s.get("path")) for s in stashes if s.get("path")]
        return self._library_paths

    def find_scene(self, scene_id: str) -> Item | None:
        data = self._execute("FindScene", FIND_SCENE, {"id": scene_id})
        scene = data.get("findScene")
        if not scene:
            return None
        return _parse_item(scene, "scene")

    def find_image(self, image_id: str) -> Item | None:
        data = self._execute("FindImage", FIND_IMAGE, {"id": image_id})
        image = data.get("findImage")
        if not image:
            return None
        return _parse_item(image, "image")

    def find_gallery(self, gallery_id: str) -> Item | None:
        data = self._execute("FindGallery", FIND_GALLERY, {"id": gallery_id})
        gallery = data.get("findGallery")
        if not gallery:
            return None
        return _parse_item(gallery, "gallery")

    def _build_filter(self, filters: BulkFilters) -> tuple[dict[str, Any], dict[str, Any]]:
        scene_filter: dict[str, Any] = {}
        if filters.tags:
            scene_filter["tags"] = {"value": filters.tags, "modifier": "INCLUDES"}
        if filters.studios:
            scene_filter["studios"] = {"value": filters.studios, "modifier": "INCLUDES"}
        if filters.organized is not None:
            scene_filter["organized"] = filters.organized
        find_filter: dict[str, Any] = {"per_page": 100, "page": 1}
        if filters.path_prefixes:
            scene_filter["path"] = {"value": filters.path_prefixes[0], "modifier": "MATCHES_REGEX"}
        return find_filter, scene_filter

    def _paginate(
        self,
        query_name: str,
        query: str,
        result_key: str,
        items_key: str,
        media_type: MediaType,
        filters: BulkFilters,
        type_filter_key: str,
    ) -> list[Item]:
        find_filter, type_filter = self._build_filter(filters)
        items: list[Item] = []
        page = 1
        while True:
            find_filter["page"] = page
            data = self._execute(
                query_name,
                query,
                {"filter": find_filter, type_filter_key: type_filter},
            )
            block = data.get(result_key) or {}
            batch = block.get(items_key) or []
            for raw in batch:
                if isinstance(raw, dict):
                    items.append(_parse_item(raw, media_type))
            count = block.get("count", 0)
            if len(items) >= count or not batch:
                break
            page += 1
        return items

    def find_scenes(self, filters: BulkFilters) -> list[Item]:
        return self._paginate(
            "FindScenes", FIND_SCENES, "findScenes", "scenes", "scene", filters, "scene_filter"
        )

    def find_images(self, filters: BulkFilters) -> list[Item]:
        return self._paginate(
            "FindImages", FIND_IMAGES, "findImages", "images", "image", filters, "image_filter"
        )

    def find_galleries(self, filters: BulkFilters) -> list[Item]:
        return self._paginate(
            "FindGalleries",
            FIND_GALLERIES,
            "findGalleries",
            "galleries",
            "gallery",
            filters,
            "gallery_filter",
        )

    def move_file(
        self, file_id: str, destination_folder: str, destination_basename: str
    ) -> bool:
        data = self._execute(
            "MoveFiles",
            MOVE_FILES,
            {
                "input": {
                    "ids": [file_id],
                    "destination_folder": destination_folder,
                    "destination_basename": destination_basename,
                }
            },
        )
        result = data.get("moveFiles")
        return bool(result)

    def file_exists_at_path(self, path: str) -> bool:
        data = self._execute(
            "FindFiles",
            FIND_FILE_BY_PATH,
            {"filter": {"q": path, "per_page": 1, "page": 1}},
        )
        files = data.get("findFiles", {}).get("files") or []
        return any(f.get("path") == path for f in files)

    def get_plugin_settings(self, plugin_id: str) -> dict[str, Any]:
        data = self._execute("Configuration", CONFIGURATION)
        plugins = data.get("configuration", {}).get("plugins") or {}
        plugin = plugins.get(plugin_id) or {}
        settings = plugin.get("settings") or {}
        return dict(settings) if isinstance(settings, dict) else {}

    def set_plugin_setting(self, plugin_id: str, key: str, value: Any) -> None:
        current = self.get_plugin_settings(plugin_id)
        current[key] = value
        self._execute(
            "ConfigurePlugin",
            CONFIGURE_PLUGIN,
            {"plugin_id": plugin_id, "settings": current},
        )
