from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, override

MAX_DESC_LEN = 500

IMAGE_PRICE = 1.0
EDIT_PRICE = 0.8
VIDEO_PRICE_PER_SECOND = 2.0
VIDEO_MAX_DURATION = 10.0

IMAGE_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAAB"
EDIT_IMAGE_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAAC"
VIDEO_B64 = "AAAAGGZ0eXBpc29tAAACAGlzb21pc28y"


@dataclass
class Env:
    credits: float = 20.0

    def charge(self, credits: float) -> None:
        if credits > self.credits:
            raise Exception(f"not enough credits: need {credits}, have {self.credits}")
        self.credits -= credits


@dataclass(frozen=True)
class Asset:
    class MediaType(Enum):
        Image = "image"
        Audio = "audio"
        Video = "video"

    b64_json: str
    media_type: Asset.MediaType


class GenerationTool(ABC):
    name: str
    desc: str

    def describe(self) -> str:
        return f"name: {self.name}, description: {self.desc}"

    @abstractmethod
    def validate_arg(self, args: list[Any]) -> None:
        pass

    @abstractmethod
    def execute(self, args: list[Any], env: Env) -> Asset:
        pass


class ImageGenTool(GenerationTool):
    name = "image-gen"
    desc = "Generate a image. args: [{description}]"

    @override
    def validate_arg(self, args: list[Any]) -> None:
        if len(args) != 1:
            raise ValueError("image-gen expects 1 arg: [description]")
        desc = args[0]
        if not isinstance(desc, str) or not desc:
            raise ValueError("description must be a non-empty string")
        if len(desc) > MAX_DESC_LEN:
            raise ValueError(f"description too long: {len(desc)} > {MAX_DESC_LEN}")

    @override
    def execute(self, args: list[Any], env: Env) -> Asset:
        env.charge(IMAGE_PRICE)
        return Asset(b64_json=IMAGE_B64, media_type=Asset.MediaType.Image)


class EditImageTool(GenerationTool):
    name = "edit-image"
    desc = "Edit src image, and generate a new image. args: [{src_id}, {description}]"

    @override
    def validate_arg(self, args: list[Any]) -> None:
        if len(args) != 2:
            raise ValueError("edit-image expects 2 args: [src_id, description]")
        src_id = args[0]
        if not isinstance(src_id, str) or not src_id:
            raise ValueError("src_id must be a non-empty string")
        desc = args[1]
        if not isinstance(desc, str) or not desc:
            raise ValueError("description must be a non-empty string")
        if len(desc) > MAX_DESC_LEN:
            raise ValueError(f"description too long: {len(desc)} > {MAX_DESC_LEN}")

    @override
    def execute(self, args: list[Any], env: Env) -> Asset:
        env.charge(EDIT_PRICE)
        return Asset(b64_json=EDIT_IMAGE_B64, media_type=Asset.MediaType.Image)


class VideoGenTool(GenerationTool):
    name = "video-gen"
    desc = "Generate a video. args: [{description}, {duration_seconds}]"

    @override
    def validate_arg(self, args: list[Any]) -> None:
        if len(args) != 2:
            raise ValueError("video-gen expects 2 args: [description, duration_seconds]")
        desc = args[0]
        if not isinstance(desc, str) or not desc:
            raise ValueError("description must be a non-empty string")
        if len(desc) > MAX_DESC_LEN:
            raise ValueError(f"description too long: {len(desc)} > {MAX_DESC_LEN}")
        duration = args[1]
        if not isinstance(duration, (int, float)):
            raise ValueError("duration_seconds must be a number")
        if duration <= 0:
            raise ValueError("duration_seconds must be positive")
        if duration > VIDEO_MAX_DURATION:
            raise ValueError(f"duration too long: {duration} > {VIDEO_MAX_DURATION}")

    @override
    def execute(self, args: list[Any], env: Env) -> Asset:
        env.charge(round(args[1] * VIDEO_PRICE_PER_SECOND, 2))
        return Asset(b64_json=VIDEO_B64, media_type=Asset.MediaType.Video)


available_tools: list[GenerationTool] = [
    ImageGenTool(),
    EditImageTool(),
    VideoGenTool(),
]

tools_by_name: dict[str, GenerationTool] = {tool.name: tool for tool in available_tools}


def get_system_prompt() -> str:
    tool_prompts = "\n".join(tool.describe() for tool in available_tools)
    return f"""
    You are a helpful assistant.
    ...
    {tool_prompts}
    """


def on_tool_call(tool_name: str, args: list[Any], env: Env) -> str:
    tool = tools_by_name.get(tool_name)
    if tool is None:
        return f"unknown tool: {tool_name}"
    try:
        tool.validate_arg(args)
        asset = tool.execute(args, env)
    except Exception as exc:
        return f"{tool_name} failed: {exc}"

    return f"{tool_name} returned {asset.media_type.value}: {asset.b64_json}"
