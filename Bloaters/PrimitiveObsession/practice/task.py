from dataclasses import dataclass
from enum import Enum
from typing import List


class GenerationModel(Enum):
    NANO_BANANA_2 = "nano-banana-2"
    GPT_IMAGE_2 = "gpt-image-2"

@dataclass
class GenerationSize:
    width: int
    height: int



@dataclass
class GenerationRequest:
    # TODO
    model: str
    prompt: str
    # TODO
    size: str


def handle_generation_request(req: GenerationRequest):
    # assume we verified the request here.
    param = ExternalGenerationCallParam(req.model, req.prompt, req.size)

    result = call_external_provider(param)

    post_processed = do_some_crop_and_scaling(result,req)
    return post_processed


@dataclass
class ExternalGenerationCallParam:
    model: str
    prompt: str
    size: str


@dataclass
class DrawResult:
    image_data: List[int]


def call_external_provider(param: ExternalGenerationCallParam) -> DrawResult:
    # call a model provider api with `param`
    # actually these parts of code are invisible to us.
    # they have such requirements
    if param.model == "gpt-image-2":
        width = int(param.size.split("x")[0])
        height = int(param.size.split("x")[1])
        assert width * height >= 635_000
        assert width * height < 1240_000

        return DrawResult([])
    if param.model == "nano-banana-2":
        size = int(param.size)
        assert size >= 256
        assert size < 1024

        return DrawResult([])
    raise ValueError(f"unknown model: {param.model}")

def do_some_crop_and_scaling(image: DrawResult, req: GenerationRequest):
    # TODO
    # THIS WILL CRASH ON nano-banana-2 result!
    width = int(req.size.split("x")[0])
    height = int(req.size.split("x")[1])
    # do some crop and scaling to image
    pass
    return image

