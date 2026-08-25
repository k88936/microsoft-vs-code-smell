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
    model: GenerationModel
    prompt: str
    size: GenerationSize


def handle_generation_request(req: GenerationRequest):
    # assume we verified the request here.
    param = to_external_generation_call_param(req)

    result = call_external_provider(param)

    post_processed = do_some_crop_and_scaling(result, req)
    return post_processed


@dataclass
class ExternalGenerationCallParam:
    model: str
    prompt: str
    size: str


def to_external_generation_call_param(
    req: GenerationRequest,
) -> ExternalGenerationCallParam:
    if req.model is GenerationModel.GPT_IMAGE_2:
        size = f"{req.size.width}x{req.size.height}"
    elif req.model is GenerationModel.NANO_BANANA_2:
        if req.size.width != req.size.height:
            raise ValueError("nano-banana-2 only supports square images")
        size = str(req.size.width)
    else:
        raise ValueError(f"unknown model: {req.model}")

    return ExternalGenerationCallParam(
        model=req.model.value,
        prompt=req.prompt,
        size=size,
    )


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
    width = req.size.width
    height = req.size.height
    # do some crop and scaling to image
    return image
