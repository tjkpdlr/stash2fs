"""Domain models for stash2fs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

MediaType = Literal["scene", "image", "gallery"]
MoveStatus = Literal["moved", "unchanged", "skipped", "failed"]
SelectionReason = Literal["tag", "studio", "path", "default", "forced"]


@dataclass
class Studio:
    name: str = ""
    parent: Studio | None = None

    def hierarchy_names(self) -> list[str]:
        names: list[str] = []
        current: Studio | None = self
        while current is not None and current.name:
            names.insert(0, current.name)
            current = current.parent
        return names


@dataclass
class Performer:
    name: str = ""
    gender: str | None = None


@dataclass
class Tag:
    name: str = ""


@dataclass
class File:
    id: str
    path: str
    basename: str = ""
    width: int | None = None
    height: int | None = None
    video_codec: str | None = None
    audio_codec: str | None = None
    frame_rate: float | None = None
    bit_rate: int | None = None
    duration: float | None = None

    @property
    def extension(self) -> str:
        if "." in self.basename:
            return "." + self.basename.rsplit(".", 1)[-1]
        return ""

    @property
    def stem(self) -> str:
        if "." in self.basename:
            return self.basename.rsplit(".", 1)[0]
        return self.basename

    @property
    def parent_dir(self) -> str:
        from pathlib import PurePosixPath

        return str(PurePosixPath(self.path).parent)


@dataclass
class Item:
    id: str
    type: MediaType
    title: str = ""
    code: str = ""
    date: str = ""
    rating100: int | None = None
    organized: bool = False
    studio: Studio | None = None
    tags: list[Tag] = field(default_factory=list)
    performers: list[Performer] = field(default_factory=list)
    files: list[File] = field(default_factory=list)
    folder_path: str | None = None  # for folder-based galleries


@dataclass
class RenderContext:
    """Template-facing variables derived from item + file."""

    library: str = ""
    current_dir: str = ""
    ext: str = ""
    title: str = ""
    date: str = ""
    year: str = ""
    studio: str = ""
    studio_hierarchy: str = ""
    code: str = ""
    rating: str = ""
    performers: list[str] = field(default_factory=list)
    performer: str = ""
    tags: list[str] = field(default_factory=list)
    resolution: str = ""
    width: str = ""
    height: str = ""
    video_codec: str = ""
    audio_codec: str = ""
    frame_rate: str = ""
    bit_rate: str = ""
    duration: str = ""
    id: str = ""
    type: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "library": self.library,
            "current_dir": self.current_dir,
            "ext": self.ext,
            "title": self.title,
            "date": self.date,
            "year": self.year,
            "studio": self.studio,
            "studio_hierarchy": self.studio_hierarchy,
            "code": self.code,
            "rating": self.rating,
            "performers": self.performers,
            "performer": self.performer,
            "tags": self.tags,
            "resolution": self.resolution,
            "width": self.width,
            "height": self.height,
            "video_codec": self.video_codec,
            "audio_codec": self.audio_codec,
            "frame_rate": self.frame_rate,
            "bit_rate": self.bit_rate,
            "duration": self.duration,
            "id": self.id,
            "type": self.type,
        }


@dataclass
class MovePlan:
    file_id: str
    item_id: str
    item_type: MediaType
    current_path: str
    destination_folder: str
    destination_basename: str
    selected_template: str
    template_name: str
    selection_reason: SelectionReason


@dataclass
class MoveOutcome:
    status: MoveStatus
    item_id: str
    item_type: MediaType
    file_id: str = ""
    current_path: str = ""
    destination_path: str = ""
    template_name: str = ""
    selection_reason: SelectionReason | str = ""
    reason: str = ""


@dataclass
class BulkFilters:
    tags: list[str] = field(default_factory=list)
    studios: list[str] = field(default_factory=list)
    path_prefixes: list[str] = field(default_factory=list)
    organized: bool | None = None


@dataclass
class RunSummary:
    moved: int = 0
    unchanged: int = 0
    skipped: int = 0
    failed: int = 0

    def add(self, outcome: MoveOutcome) -> None:
        if outcome.status == "moved":
            self.moved += 1
        elif outcome.status == "unchanged":
            self.unchanged += 1
        elif outcome.status == "skipped":
            self.skipped += 1
        elif outcome.status == "failed":
            self.failed += 1

    def merge(self, other: RunSummary) -> None:
        self.moved += other.moved
        self.unchanged += other.unchanged
        self.skipped += other.skipped
        self.failed += other.failed
