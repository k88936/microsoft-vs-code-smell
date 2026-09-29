import sys
import unittest
from dataclasses import replace
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ObjectOrientationAbusers.TemporaryField.practice.task import (  # noqa: E402
    AssetKind,
    CanvaResourceDTO,
    Frame,
    ImageResource,
    ImageSequenceResource,
    VideoResource,
    to_canva_resource,
)

# The fields each resource kind cannot be built without.
REQUIRED_FIELDS = {
    AssetKind.IMAGE: ("width", "height", "object_key"),
    AssetKind.VIDEO: ("width", "height", "object_key", "duration_ms"),
    AssetKind.IMAGE_SEQUENCE: ("width", "height", "image_sequence", "duration_ms"),
}

# A DTO that carries every field, so a kind can hand it the ones it needs.
COMPLETE_DTO = CanvaResourceDTO(
    resource_id="resource-1",
    asset_kind=AssetKind.IMAGE,
    object_key="object/key",
    width=1920,
    height=1080,
    duration_ms=2_500,
    image_sequence=Frame("frame/key"),
)

EXPECTED_TYPE = {
    AssetKind.IMAGE: ImageResource,
    AssetKind.VIDEO: VideoResource,
    AssetKind.IMAGE_SEQUENCE: ImageSequenceResource,
}


def dto_for(asset_kind: AssetKind, **overrides) -> CanvaResourceDTO:
    return replace(COMPLETE_DTO, asset_kind=asset_kind, **overrides)


class ToCanvaResourceFieldRequirementTest(unittest.TestCase):
    """to_canva_resource must check exactly the fields each kind requires."""

    def test_a_complete_dto_builds_the_matching_concrete_struct(self) -> None:
        for asset_kind, expected_type in EXPECTED_TYPE.items():
            with self.subTest(asset_kind=asset_kind):
                resource = to_canva_resource(dto_for(asset_kind))

                self.assertIsInstance(resource, expected_type)
                self.assertEqual(resource.resource_id, "resource-1")

    def test_a_missing_required_field_crashes_the_assert(self) -> None:
        for asset_kind, required_fields in REQUIRED_FIELDS.items():
            for field_name in required_fields:
                with self.subTest(asset_kind=asset_kind, missing=field_name):
                    with self.assertRaises(AssertionError):
                        to_canva_resource(dto_for(asset_kind, **{field_name: None}))

    def test_fields_a_kind_does_not_need_may_stay_none(self) -> None:
        for asset_kind, required_fields in REQUIRED_FIELDS.items():
            for field_name in ("object_key", "duration_ms", "image_sequence"):
                if field_name in required_fields:
                    continue
                with self.subTest(asset_kind=asset_kind, unused=field_name):
                    resource = to_canva_resource(dto_for(asset_kind, **{field_name: None}))

                    self.assertIsInstance(resource, EXPECTED_TYPE[asset_kind])

    def test_an_image_sequence_does_not_require_an_object_key(self) -> None:
        resource = to_canva_resource(dto_for(AssetKind.IMAGE_SEQUENCE, object_key=None))

        self.assertIsInstance(resource, ImageSequenceResource)

    def test_each_kind_reads_the_fields_it_requires(self) -> None:
        image = to_canva_resource(dto_for(AssetKind.IMAGE))
        video = to_canva_resource(dto_for(AssetKind.VIDEO))
        sequence = to_canva_resource(dto_for(AssetKind.IMAGE_SEQUENCE))

        self.assertEqual(
            (image.width, image.height, image.object_key),
            (1920, 1080, "object/key"),
        )
        self.assertEqual(
            (video.width, video.height, video.object_key, video.duration_ms),
            (1920, 1080, "object/key", 2_500),
        )
        self.assertEqual(
            (sequence.width, sequence.height, sequence.image_sequence, sequence.duration_ms),
            (1920, 1080, Frame("frame/key"), 2_500),
        )


if __name__ == "__main__":
    unittest.main()
