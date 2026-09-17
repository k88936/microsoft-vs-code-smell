import threading
from typing import Tuple

CAMERA_MIN_ZOOM = 0.1
CAMERA_MAX_ZOOM = 10.0


class CameraManager:
    _camera_pos: Tuple[float, float]
    _camera_zoom: float
    _mutex: threading.Lock

    def __init__(self) -> None:
        self._camera_pos = (0.0, 0.0)
        self._camera_zoom = 1.0
        self._mutex = threading.Lock()

    @property
    def camera_pos(self) -> Tuple[float, float]:
        with self._mutex:
            return self._camera_pos

    @property
    def camera_zoom(self) -> float:
        with self._mutex:
            return self._camera_zoom

    @staticmethod
    def _clamp_zoom(zoom: float) -> float:
        return min(CAMERA_MAX_ZOOM, max(CAMERA_MIN_ZOOM, zoom))

    def delta_pos(self, delta: Tuple[float, float]) -> None:
        with self._mutex:
            self._camera_pos = (self._camera_pos[0] + delta[0], self._camera_pos[1] + delta[1])

    def factor_zoom(self, factor: float) -> None:
        if factor <= 0:
            raise ValueError("zoom factor must be positive")
        with self._mutex:
            self._camera_zoom = self._clamp_zoom(self._camera_zoom * factor)


camera_manager = CameraManager()

# usage: some threads pan, some threads zoom, all against the same camera
if __name__ == "__main__":
    def pan() -> None:
        for _ in range(5):
            camera_manager.delta_pos((1, 2))

    def zoom(factor: float) -> None:
        camera_manager.factor_zoom(factor)

    threads = [threading.Thread(target=pan) for _ in range(4)]
    threads += [threading.Thread(target=zoom, args=(factor,)) for factor in (2, 1.5)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert camera_manager.camera_pos == (20, 40)
    assert camera_manager.camera_zoom == 3
