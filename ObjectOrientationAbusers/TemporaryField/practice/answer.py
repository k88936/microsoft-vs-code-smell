from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class Frame:
    object_key: str


class AssetKind(Enum):
    IMAGE = 1
    VIDEO = 2
    IMAGE_SEQUENCE = 3


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
class ImageResource:
    resource_id: str
    width: int
    height: int
    object_key: str
    # omitted operation examples


@dataclass(frozen=True)
class VideoResource:
    resource_id: str
    width: int
    height: int
    object_key: str
    duration_ms: int
    # omitted operation examples


@dataclass(frozen=True)
class ImageSequenceResource:
    resource_id: str
    width: int
    height: int
    image_sequence: Frame
    duration_ms: int
    # omitted operation examples

CanvaResource = ImageResource | VideoResource | ImageSequenceResource

def to_canva_resource(dto: CanvaResourceDTO) -> CanvaResource:
    assert dto.width is not None
    assert dto.height is not None

    match dto.asset_kind:
        case AssetKind.IMAGE:
            assert dto.object_key is not None
            return ImageResource(
                resource_id=dto.resource_id,
                width=dto.width,
                height=dto.height,
                object_key=dto.object_key,
            )
        case AssetKind.VIDEO:
            assert dto.object_key is not None
            assert dto.duration_ms is not None
            return VideoResource(
                resource_id=dto.resource_id,
                width=dto.width,
                height=dto.height,
                object_key=dto.object_key,
                duration_ms=dto.duration_ms,
            )
        case AssetKind.IMAGE_SEQUENCE:
            assert dto.image_sequence is not None
            assert dto.duration_ms is not None
            return ImageSequenceResource(
                resource_id=dto.resource_id,
                width=dto.width,
                height=dto.height,
                image_sequence=dto.image_sequence,
                duration_ms=dto.duration_ms,
            )
        case _:
            raise Exception("Unknown asset_kind")

app_canva_resource_state: dict[str, CanvaResource] = {}

def refresh_canva_resources(dtos: list[CanvaResourceDTO]) -> None:
    resources = [to_canva_resource(dto) for dto in dtos]

    app_canva_resource_state.clear()
    app_canva_resource_state.update(
        {resource.resource_id: resource for resource in resources}
    )
