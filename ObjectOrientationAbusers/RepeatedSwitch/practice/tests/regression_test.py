import base64
import re
import sys
import unittest
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ObjectOrientationAbusers.RepeatedSwitch.practice.task import (  # noqa: E402
    Env,
    get_system_prompt,
    on_tool_call,
)

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MP4_MAGIC = b"\x00\x00\x00\x18ftyp"

ADVERTISED_NAME_RE = re.compile(r"name:\s*([\w.-]+)\s*,")

TOOL_CALLS = (
    ("image-gen", ["a cat"], "image", PNG_MAGIC),
    ("edit-image", ["src-001", "a cat with a hat"], "image", PNG_MAGIC),
    ("video-gen", ["a cat dancing", 3.0], "video", MP4_MAGIC),
)

REJECTED_CALLS = (
    ("image-gen", []),
    ("image-gen", ["a cat", "a dog"]),
    ("image-gen", [""]),
    ("image-gen", ["x" * 2000]),
    ("edit-image", ["src-001"]),
    ("edit-image", ["", "a cat"]),
    ("edit-image", ["src-001", "a cat", "extra"]),
    ("video-gen", ["a cat"]),
    ("video-gen", ["a cat", 0]),
    ("video-gen", ["a cat", 99.0]),
    ("video-gen", ["a cat", "3 seconds"]),
)


def payload_of(result: str) -> bytes:
    longest_token = max(result.split(), key=len)
    return base64.b64decode(longest_token)


def credits_spent(tool_name: str, args: list[Any], credits: float = 20.0) -> float:
    env = Env(credits=credits)
    before = env.credits
    on_tool_call(tool_name, args, env)
    return before - env.credits


class SystemPromptRegressionTest(unittest.TestCase):

    def test_prompt_advertises_every_tool_once(self) -> None:
        advertised = ADVERTISED_NAME_RE.findall(get_system_prompt())

        for name, _, _, _ in TOOL_CALLS:
            with self.subTest(tool=name):
                self.assertIn(name, advertised, f'"{name}" must stay advertised in the system prompt')
        self.assertEqual(len(advertised), len(TOOL_CALLS), "each tool must be advertised exactly once")

    def test_prompt_keeps_the_assistant_header(self) -> None:
        self.assertIn("You are a helpful assistant", get_system_prompt())


class ToolCallRegressionTest(unittest.TestCase):

    def test_advertised_tools_are_dispatchable(self) -> None:
        for name, args, media_type, magic in TOOL_CALLS:
            with self.subTest(tool=name):
                result = on_tool_call(name, args, Env())

                self.assertIsInstance(result, str, "a tool result must be text for the model")
                self.assertIn(media_type, result)
                self.assertTrue(
                    payload_of(result).startswith(magic),
                    f"{name} must come back as a {media_type} payload",
                )

    def test_unknown_tool_is_reported_and_free(self) -> None:
        env = Env()
        before = env.credits

        result = on_tool_call("no-such-tool", ["a cat"], env)

        self.assertIsInstance(result, str)
        self.assertIn("no-such-tool", result)
        self.assertEqual(env.credits, before, "an unknown tool must not spend credits")


class ArgValidationRegressionTest(unittest.TestCase):

    def test_bad_args_never_crash_or_charge(self) -> None:
        for name, args in REJECTED_CALLS:
            with self.subTest(tool=name, args=args):
                env = Env()
                before = env.credits

                result = on_tool_call(name, args, env)

                self.assertIsInstance(result, str)
                self.assertIn(name, result)
                self.assertEqual(
                    env.credits,
                    before,
                    f"{name}{args} must be rejected before it is charged",
                )


class BillingRegressionTest(unittest.TestCase):

    def test_a_served_call_spends_credits(self) -> None:
        self.assertGreater(credits_spent("image-gen", ["a cat"]), 0)

    def test_image_cost_does_not_depend_on_the_description(self) -> None:
        self.assertEqual(
            credits_spent("image-gen", ["a cat"]),
            credits_spent("image-gen", ["a cat on a very long leash"]),
        )

    def test_edit_cost_does_not_depend_on_the_args(self) -> None:
        self.assertEqual(
            credits_spent("edit-image", ["src-001", "a cat"]),
            credits_spent("edit-image", ["src-002", "a cat on a very long leash"]),
        )

    def test_video_cost_grows_with_duration(self) -> None:
        short = credits_spent("video-gen", ["a cat dancing", 2.0])
        long = credits_spent("video-gen", ["a cat dancing", 4.0])

        self.assertAlmostEqual(long, 2 * short)

    def test_call_is_rejected_when_credits_run_out(self) -> None:
        env = Env(credits=0.5)

        result = on_tool_call("video-gen", ["a cat dancing", 5.0], env)

        self.assertIsInstance(result, str)
        self.assertEqual(env.credits, 0.5, "a call we cannot afford must not charge anything")


if __name__ == "__main__":
    unittest.main()
