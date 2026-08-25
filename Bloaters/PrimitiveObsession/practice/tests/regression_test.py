import unittest

from Bloaters.PrimitiveObsession.practice.task import (
    GenerationModel,
    GenerationRequest,
    GenerationSize,
    handle_generation_request,
    to_external_generation_call_param,
)


class RegressionTest(unittest.TestCase):
    def test_gpt_request_uses_width_by_height_provider_format(self):
        request = GenerationRequest(
            model=GenerationModel.GPT_IMAGE_2,
            prompt="A sunset",
            size=GenerationSize(width=1024, height=1024),
        )

        parameter = to_external_generation_call_param(request)

        self.assertEqual(parameter.model, "gpt-image-2")
        self.assertEqual(parameter.size, "1024x1024")
        self.assertEqual(handle_generation_request(request).image_data, [])

    def test_nano_banana_request_uses_square_provider_format(self):
        request = GenerationRequest(
            model=GenerationModel.NANO_BANANA_2,
            prompt="A banana",
            size=GenerationSize(width=512, height=512),
        )

        parameter = to_external_generation_call_param(request)

        self.assertEqual(parameter.model, "nano-banana-2")
        self.assertEqual(parameter.size, "512")
        self.assertEqual(handle_generation_request(request).image_data, [])

    def test_nano_banana_rejects_non_square_sizes(self):
        request = GenerationRequest(
            model=GenerationModel.NANO_BANANA_2,
            prompt="A banana",
            size=GenerationSize(width=512, height=768),
        )

        with self.assertRaisesRegex(ValueError, "square"):
            to_external_generation_call_param(request)
