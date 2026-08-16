import argparse
import json
import re
from pathlib import Path

from str_replace_placeholder import (
    find_file_block,
    find_placeholders_block,
    placeholder_ranges,
    read_text,
)


def parse_block_scalar(lines: list[str], header: str) -> str:
    match = re.fullmatch(r"\|(\d)?([+-])?", header)
    if not match:
        raise ValueError(f"unsupported block scalar {header!r}")
    indentation = int(match.group(1) or 2)
    prefix = " " * (8 + indentation)
    content: list[str] = []
    for line in lines:
        if not line.rstrip("\r\n").strip():
            content.append("\r\n" if line.endswith("\r\n") else "\n")
        else:
            content.append(line[len(prefix):] if line.startswith(prefix) else line)
    text = "".join(content)
    chomping = match.group(2)
    if chomping == "-":
        return text.rstrip("\r\n")
    if chomping == "+":
        return text
    return text.rstrip("\r\n") + ("\n" if text else "")


def parse_placeholder(lines: list[str]) -> tuple[int, int, str]:
    offset_match = re.fullmatch(r"      - offset:\s*(\d+)\s*", lines[0].rstrip("\r\n"))
    length_match = re.fullmatch(r"        length:\s*(\d+)\s*", lines[1].rstrip("\r\n"))
    text_match = re.fullmatch(
        r"        placeholder_text:\s*(.*?)\s*", lines[2].rstrip("\r\n")
    )
    if not offset_match or not length_match or not text_match:
        raise ValueError("invalid placeholder entry")

    value = text_match.group(1)
    if value.startswith("|"):
        replacement = parse_block_scalar(lines[3:], value)
    elif value.startswith('"'):
        replacement = json.loads(value)
    elif value.startswith("'"):
        replacement = value[1:-1].replace("''", "'")
    else:
        replacement = value
    return int(offset_match.group(1)), int(length_match.group(1)), replacement


def load_placeholders(task_info: Path, file_name: str) -> list[tuple[int, int, str]]:
    lines = read_text(task_info).splitlines(keepends=True)
    file_start, file_end = find_file_block(lines, file_name)
    block = find_placeholders_block(lines, file_start, file_end)
    if block is None:
        return []
    block_start, block_end = block
    return [
        parse_placeholder(lines[start:end])
        for start, end in placeholder_ranges(lines, block_start, block_end)
    ]


def apply_placeholders(source: str, placeholders: list[tuple[int, int, str]]) -> str:
    ordered = sorted(placeholders)
    previous_end = 0
    for offset, length, _ in ordered:
        if offset < previous_end:
            raise ValueError(f"overlapping placeholder at offset {offset}")
        if offset < 0 or length < 0 or offset + length > len(source):
            raise ValueError(f"placeholder outside source at offset {offset}")
        previous_end = offset + length

    rendered = source
    for offset, length, replacement in reversed(ordered):
        rendered = rendered[:offset] + replacement + rendered[offset + length:]
    return rendered


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("path", type=Path)
    result.add_argument("--task-info", type=Path)
    result.add_argument("--output", type=Path)
    return result


def main() -> None:
    arguments = parser().parse_args()
    source_path = arguments.path.resolve()
    task_info = (
        arguments.task_info.resolve()
        if arguments.task_info
        else source_path.parent / "task-info.yaml"
    )
    try:
        file_name = source_path.relative_to(task_info.parent).as_posix()
    except ValueError:
        file_name = source_path.name

    try:
        rendered = apply_placeholders(
            read_text(source_path), load_placeholders(task_info, file_name)
        )
        if arguments.output:
            arguments.output.write_text(rendered, encoding="utf-8", newline="")
        else:
            print(rendered, end="")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise SystemExit(f"error: {error}") from error

if __name__ == "__main__":
    main()
