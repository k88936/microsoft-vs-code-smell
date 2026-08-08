# Introduce

This is part of a web service that forwards user's image generation request to real model providers.
This is adapted from my real experience.

Assume we have the need to post process the raw image from providers.
There are some problems:
* the provider's doc uses 2 different formats for the size param for different models:
    `{width}x{height}` for gpt `{width}` for nano banana 2 (square only)
* the whole module is vibed, not providing a strong typing for such string-typed fields.

But you don't know and are required to implement the post-processing. It needs to know the width and height of the image.
And you thought it easy and vibed code like this:

```python
def do_some_crop_and_scaling(image: DrawResult, req: GenerationRequest):
    # TODO
    # THIS WILL CRASH ON nano-banana-2 result!
    width = int(req.size.split("x")[0])
    height = int(req.size.split("x")[1])
    # do some crop and scaling to image
    pass
    return image
```

And our service crashed midnight.

# Task

Not only to fix this, we should prevent such bugs once for all:

* refactor `GenerationRequest`: make `model` field an enum `GenerationModel` size a struct `GenerationSize`
* write a convert func from `GenerationRequest` to `ExternalGenerationCallParam`