from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class Frame:
    object_key: str


class AssetKind(Enum):
    IMAGE = 1
    VIDEO = 2
    IMAGE_SEQUENCE = 3


# For historical reasons, the database schema has this shape. Let us make the
# application code more comfortable without rewriting the whole system.
@dataclass(frozen=True)
class CanvaResourceDTO:
    resource_id: str
    asset_kind: AssetKind
    object_key: str | None
    width: int | None
    height: int | None
    duration_ms: int | None
    image_sequence: Frame | None


@dataclass(frozen=True)
class CanvaResource:
    resource_id: str
    asset_kind: AssetKind
    object_key: str | None
    width: int | None
    height: int | None
    duration_ms: int | None
    image_sequence: Frame | None


# Newly fetched DTOs trigger a refresh. The current implementation simply
# mirrors the DTO structure in the application state.
app_canva_resource_state: dict[str, CanvaResource] = {}


def refresh_canva_resources(dtos: list[CanvaResourceDTO]) -> None:
    app_canva_resource_state.clear()
    for dto in dtos:
        resource = CanvaResource(
            resource_id=dto.resource_id,
            asset_kind=dto.asset_kind,
            object_key=dto.object_key,
            width=dto.width,
            height=dto.height,
            duration_ms=dto.duration_ms,
            image_sequence=dto.image_sequence,
        )
        app_canva_resource_state[resource.resource_id] = resource


def draw_image_widget(res: CanvaResource) -> None:
    assert res.asset_kind == AssetKind.IMAGE
    assert res.object_key is not None
    assert res.width is not None
    assert res.height is not None
    # Do the real drawing work.


def draw_video_widget(res: CanvaResource) -> None:
    assert res.asset_kind == AssetKind.VIDEO
    assert res.object_key is not None
    assert res.width is not None
    assert res.height is not None
    assert res.duration_ms is not None
    # Do the real drawing work.


def draw_image_sequence_widget(res: CanvaResource) -> None:
    assert res.asset_kind == AssetKind.IMAGE_SEQUENCE
    assert res.duration_ms is not None
    assert res.width is not None
    assert res.height is not None
    assert res.image_sequence is not None
    # Do the real drawing work.


# What happens as we add more asset kinds and operations?
def draw_music_widget(res: CanvaResource) -> None:
    pass


def scale_image(res: CanvaResource) -> None:
    pass
