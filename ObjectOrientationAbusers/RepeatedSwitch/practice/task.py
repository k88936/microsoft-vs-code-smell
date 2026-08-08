# Not a good example
import json
import uuid
from abc import abstractmethod, ABC
from typing import List


class Tool(ABC):
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def description(self):
        pass

    @abstractmethod
    def call(self, args):
        pass


class ImageGenTool(Tool):
    def name(self):
        return "image-gen"

    def description(self):
        return "Generate a image. args: [{description}]"

    def call(self, args):
        desc: str = args[0]
        image_id = uuid.uuid4()
        return f"generated an image (id: {image_id}) with description: {desc}"


class EditImageTool(Tool):
    def name(self):
        return "edit-image"

    def description(self):
        return "Edit src image, and generate a new image. args: [{src_id}, {description}]"

    def call(self, args):
        src = args[0]
        desc = args[1]
        result = uuid.uuid4()
        return f"generated result image (id={result}) with description: {desc} from src image (id={src})"


class VideoGenTool(Tool):
    def name(self):
        return "video-gen"

    def description(self):
        return "Generate a video. args: [{description}]"

    def call(self, args):
        desc: str = args[0]
        video_id = uuid.uuid4()
        return f"it generated a video (id: {video_id}) with description: {desc}"


# example usage:

available_tools = [ImageGenTool(), EditImageTool(), VideoGenTool()]


def get_system_prompt():
    def format_tool_info(tool: Tool):
        return f"name: {tool.name()}, description: {tool.description()}"

    tool_prompts = "\n".join([format_tool_info(t) for t in available_tools])
    return f"""
    You are a helpful assistant.
    ...
    {tool_prompts}
    """


def prompt(prompt: str):
    def external_llm_provider_call(prompt: str):
        pass
        return ""
    def parse_some_tool_call(resp: str):
        return "name", "arg"

    response = external_llm_provider_call(prompt)
    (tool_name, args) = parse_some_tool_call(response)

    for tool in available_tools:
        if tool.name() == tool_name:
            return tool.call(args)

    return f"unknown tool: {tool_name}"
