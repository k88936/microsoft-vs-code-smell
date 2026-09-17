import threading
import uuid
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, List, Any, Sequence

CAMERA_MIN_ZOOM = 0.1
CAMERA_MAX_ZOOM = 10.0


@dataclass
class Node:
    id: uuid.UUID
    children: List["Node"]
    components: List[Any]
    position: Tuple[int, int]
    size: Tuple[int, int]


@dataclass(frozen=True)
class Bounds:
    left: float
    top: float
    right: float
    bottom: float


class CameraManager:
    camera_pos: Tuple[float, float]
    camera_zoom: float
    mutex: threading.Lock

    def __init__(self) -> None:
        self.camera_pos = (0.0, 0.0)
        self.camera_zoom = 1.0
        self.mutex = threading.Lock()

    @staticmethod
    def _clamp_zoom(zoom: float) -> float:
        return min(CAMERA_MAX_ZOOM, max(CAMERA_MIN_ZOOM, zoom))

    def delta_pos(self, delta: Tuple[float, float]) -> None:
        with self.mutex:
            self.camera_pos = (self.camera_pos[0] + delta[0], self.camera_pos[1] + delta[1])

    def factor_zoom(self, factor: float) -> None:
        if factor <= 0:
            raise ValueError("zoom factor must be positive")
        with self.mutex:
            self.camera_zoom = self._clamp_zoom(self.camera_zoom * factor)

    def fit_to_bounds(self, window_size: Tuple[float, float], bounds: Sequence[Bounds]) -> None:
        window_width, window_height = window_size
        if window_width <= 0 or window_height <= 0:
            raise ValueError("window size must be positive")
        if not bounds:
            raise ValueError("cannot fit empty bounds")

        # this is a good boundary to split
        final_bound = Bounds(
            min(bound.left for bound in bounds),
            min(bound.top for bound in bounds),
            max(bound.right for bound in bounds),
            max(bound.bottom for bound in bounds),
        )

        # compute camera zoom and pos from the fit bounds
        content_width = final_bound.right - final_bound.left
        content_height = final_bound.bottom - final_bound.top
        if content_width <= 0 or content_height <= 0:
            raise ValueError("bounds must have a positive size")

        with self.mutex:
            self.camera_pos = (
                (final_bound.left + final_bound.right) / 2,
                (final_bound.top + final_bound.bottom) / 2,
            )
            self.camera_zoom = self._clamp_zoom(
                min(window_width / content_width, window_height / content_height)
            )


@dataclass
class Tree:
    root: Node


@dataclass
class Spirit:
    id: uuid.UUID
    path: Path


class UIEditor:
    ui_trees: List[Tree]
    spirits: List[Spirit]
    camera_manager: CameraManager
    selected_node: Node | None
    mutex: threading.Lock

    def __init__(self, ui_trees: List[Tree], spirits: List[Spirit]) -> None:
        self.ui_trees = ui_trees
        self.spirits = spirits
        self.camera_manager = CameraManager()
        self.selected_node = None
        self.mutex = threading.Lock()

    @staticmethod
    def _find_node(node: Node, node_id: uuid.UUID) -> Node | None:
        if node.id == node_id:
            return node
        for child in node.children:
            found = UIEditor._find_node(child, node_id)
            if found is not None:
                return found
        return None

    @staticmethod
    def _remove_node(node: Node, node_id: uuid.UUID) -> bool:
        for index, child in enumerate(node.children):
            if child.id == node_id:
                del node.children[index]
                return True
            if UIEditor._remove_node(child, node_id):
                return True
        return False

    # camera op
    def on_pan_gesture(self, dx: float, dy: float) -> None:
        self.camera_manager.delta_pos((dx, dy))

    def on_zoom_gesture(self, factor: float) -> None:
        # do something to the state
        self.camera_manager.factor_zoom(factor)

    def fit_to_window(self, window_size: Tuple[int, int]) -> None:
        # simplified: the tree read stays unlocked
        if not self.ui_trees:
            raise ValueError("cannot fit an empty editor")

        tree_bounds = [
            Bounds(
                tree.root.position[0],
                tree.root.position[1],
                tree.root.position[0] + tree.root.size[0],
                tree.root.position[1] + tree.root.size[1],
            )
            for tree in self.ui_trees
        ]
        # this is a good boundary to split
        self.camera_manager.fit_to_bounds(window_size, tree_bounds)

    # node op
    def on_select_node(self, node_id: uuid.UUID) -> Node:
        # do something to the state
        with self.mutex:
            selected = None
            for tree in self.ui_trees:
                if (found := self._find_node(tree.root, node_id)) is not None:
                    selected = found
                    break
            if selected is None:
                raise KeyError(f"node not found: {node_id}")
            self.selected_node = selected
            return selected

    def on_del_node(self, node_id: uuid.UUID) -> bool:
        # do something to the state
        with self.mutex:
            for index, tree in enumerate(self.ui_trees):
                if tree.root.id == node_id:
                    del self.ui_trees[index]
                    self.selected_node = None
                    return True
                if self._remove_node(tree.root, node_id):
                    if self.selected_node and self.selected_node.id == node_id:
                        self.selected_node = None
                    return True
            return False

    # persistence op
    def export_to_json(self) -> str:
        # do something to the state
        with self.mutex:
            document = {
                "camera_pos": list(self.camera_manager.camera_pos),
                "camera_zoom": self.camera_manager.camera_zoom,
                # simplified  here use count :)
                "tree_count": len(self.ui_trees),
                "spirit_count": len(self.spirits),
            }
            return json.dumps(document, indent=2, sort_keys=True)

    def export_to_html(self) -> str:
        # do something to the state
        pass

    # operation history
    def on_undo(self):
        # do something to the state
        pass

    def on_redo(self):
        # do something to the state
        pass

    def import_spirit(self, path: str | Path) -> Spirit:
        spirit = Spirit(uuid.uuid4(), Path(path))
        with self.mutex:
            self.spirits.append(spirit)
        return spirit

    # even ai functions ...
    def on_ai_recognition(self):
        with self.mutex:
            ai_recognition_result = []
            # do a whole replacement for current tree
            self.ui_trees = ai_recognition_result
            pass
