import sys
import threading
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ChangePreventers.GlobalData.practice.task import (  # noqa: E402
    CAMERA_MAX_ZOOM,
    CAMERA_MIN_ZOOM,
    CameraManager,
)


def pan(camera: CameraManager, steps: int) -> None:
    for _ in range(steps):
        camera.delta_pos((1, 2))


def zoom(camera: CameraManager, factor: float) -> None:
    camera.factor_zoom(factor)


def run_all(threads: list[threading.Thread]) -> None:
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


class CameraBehaviourTest(unittest.TestCase):
    """Encapsulating the camera must not change what it does."""

    def setUp(self) -> None:
        self.camera = CameraManager()

    def test_starts_at_the_origin_with_unit_zoom(self) -> None:
        self.assertEqual(self.camera.camera_pos, (0.0, 0.0))
        self.assertEqual(self.camera.camera_zoom, 1.0)

    def test_pan_moves_the_camera(self) -> None:
        self.camera.delta_pos((1, 2))
        self.camera.delta_pos((-0.5, 3.5))

        self.assertEqual(self.camera.camera_pos, (0.5, 5.5))

    def test_zoom_multiplies(self) -> None:
        self.camera.factor_zoom(2)
        self.camera.factor_zoom(1.5)

        self.assertEqual(self.camera.camera_zoom, 3.0)

    def test_zoom_clamps_to_the_camera_limits(self) -> None:
        self.camera.factor_zoom(1_000)
        self.assertEqual(self.camera.camera_zoom, CAMERA_MAX_ZOOM)

        self.camera.factor_zoom(0.000_001)
        self.assertEqual(self.camera.camera_zoom, CAMERA_MIN_ZOOM)

    def test_zoom_rejects_a_non_positive_factor(self) -> None:
        for factor in (0, -1.5):
            with self.subTest(factor=factor):
                with self.assertRaises(ValueError):
                    self.camera.factor_zoom(factor)

    def test_the_camera_commands_are_commands(self) -> None:
        self.assertIsNone(self.camera.delta_pos((1, 2)), "delta_pos is a command, not a query")
        self.assertIsNone(self.camera.factor_zoom(2), "factor_zoom is a command, not a query")

    def test_every_camera_owns_its_own_state(self) -> None:
        other = CameraManager()
        self.camera.delta_pos((1, 2))
        other.factor_zoom(4)

        self.assertEqual(other.camera_pos, (0.0, 0.0), "one camera must not move the other")
        self.assertEqual(other.camera_zoom, 4.0)
        self.assertEqual(self.camera.camera_zoom, 1.0, "one camera must not zoom the other")
        self.assertIsNot(
            self.camera._mutex,
            other._mutex,
            "every camera must own its own lock",
        )


class ConcurrentCameraTest(unittest.TestCase):
    """The threads share one camera, and none of their updates may get lost."""

    def test_concurrent_pans_keep_every_update(self) -> None:
        camera = CameraManager()

        run_all([threading.Thread(target=pan, args=(camera, 5)) for _ in range(4)])

        self.assertEqual(camera.camera_pos, (20, 40))

    def test_concurrent_zooms_keep_every_update(self) -> None:
        camera = CameraManager()

        run_all([threading.Thread(target=zoom, args=(camera, factor)) for factor in (2, 1.5)])

        self.assertEqual(camera.camera_zoom, 3.0)

    def test_many_writers_lose_nothing(self) -> None:
        camera = CameraManager()

        run_all([threading.Thread(target=pan, args=(camera, 50)) for _ in range(8)])

        self.assertEqual(camera.camera_pos, (400, 800))

    def test_the_demo_ends_where_it_used_to(self) -> None:
        camera = CameraManager()
        threads = [threading.Thread(target=pan, args=(camera, 5)) for _ in range(4)]
        threads += [threading.Thread(target=zoom, args=(camera, factor)) for factor in (2, 1.5)]

        run_all(threads)

        self.assertEqual(camera.camera_pos, (20, 40))
        self.assertEqual(camera.camera_zoom, 3.0)


if __name__ == "__main__":
    unittest.main()
