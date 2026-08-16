import argparse
import json
import os
import re
import tempfile
from pathlib import Path


def read_text(path: Path) -> str:
    with path.open(encoding="utf-8", newline="") as file:
        return file.read()


def read_argument(value: str | None, file_path: Path | None) -> str:
    if value is not None:
        return value
    if file_path is None:
        raise ValueError("a string or string file is required")
    return read_text(file_path)


def leading_spaces(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def yaml_name(value: str) -> str:
    value = value.strip()
    if value.startswith(('"', "'")):
        if value.startswith('"'):
            return json.loads(value)
        return value[1:-1].replace("''", "'")
    return value


def find_file_block(lines: list[str], file_name: str) -> tuple[int, int]:
    entries: list[tuple[int, str]] = []
    pattern = re.compile(r"^  - name:\s*(.*?)\s*$")
    for index, line in enumerate(lines):
        match = pattern.match(line.rstrip("\r\n"))
        if match:
            entries.append((index, yaml_name(match.group(1))))

    matches = [position for position, name in entries if name == file_name]
    if len(matches) != 1:
        raise ValueError(
            f"expected one files entry named {file_name!r}, found {len(matches)}"
        )

    start = matches[0]
    following = [position for position, _ in entries if position > start]
    return start, following[0] if following else len(lines)


def find_placeholders_block(
    lines: list[str], file_start: int, file_end: int
) -> tuple[int, int] | None:
    for index in range(file_start + 1, file_end):
        if lines[index].rstrip("\r\n") == "    placeholders:":
            end = index + 1
            while end < file_end:
                line = lines[end]
                if line.strip() and leading_spaces(line) <= 4:
                    break
                end += 1
            return index, end
    return None


def placeholder_ranges(lines: list[str], start: int, end: int) -> list[tuple[int, int]]:
    starts = [
        index
        for index in range(start + 1, end)
        if re.match(r"^      - offset:\s*\d+\s*$", lines[index].rstrip("\r\n"))
    ]
    return [
        (entry_start, starts[index + 1] if index + 1 < len(starts) else end)
        for index, entry_start in enumerate(starts)
    ]


def placeholder_span(lines: list[str], start: int) -> tuple[int, int]:
    offset_match = re.fullmatch(
        r"      - offset:\s*(\d+)\s*", lines[start].rstrip("\r\n")
    )
    length_match = re.fullmatch(
        r"        length:\s*(\d+)\s*", lines[start + 1].rstrip("\r\n")
    )
    if not offset_match or not length_match:
        raise ValueError("invalid placeholder offset or length")
    return int(offset_match.group(1)), int(length_match.group(1))


def ensure_separated(
    offset: int,
    length: int,
    spans: list[tuple[int, int]],
) -> None:
    end = offset + length
    for other_offset, other_length in spans:
        other_end = other_offset + other_length
        if offset < other_end and other_offset < end:
            raise ValueError(
                f"placeholder [{offset}, {end}) overlaps "
                f"[{other_offset}, {other_end})"
            )
        if end == other_offset or other_end == offset:
            raise ValueError(
                f"placeholder [{offset}, {end}) touches "
                f"[{other_offset}, {other_end}); leave a source character between them"
            )


def normalize_replacement_bounds(
    source: str,
    offset: int,
    old_string: str,
    new_string: str,
) -> tuple[int, str, str]:
    token_replacement = re.fullmatch(
        r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*(?:\([^()\r\n]*\))?",
        new_string,
    )
    if token_replacement and ("\n" in old_string or "\r" in old_string):
        raise ValueError("a token placeholder cannot cross a physical line")

    if "\n" not in old_string and "\r" not in old_string:
        line_end = source.find("\n", offset)
        if line_end != -1 and offset + len(old_string) > line_end:
            raise ValueError("a token placeholder cannot cross a physical line")

    if new_string == "\n" + old_string and old_string.startswith("\n"):
        offset += 1
        old_string = old_string[1:]
        new_string = new_string[1:]

    line_start = source.rfind("\n", 0, offset) + 1
    indentation = source[line_start:offset]
    if indentation and not indentation.strip() and "\n" in old_string:
        offset = line_start
        old_string = indentation + old_string
        new_string = indentation + new_string

    if (
        not new_string
        and old_string.startswith("\n")
        and old_string.endswith("\n")
        and offset > 0
        and source[offset - 1] == "\n"
    ):
        offset -= 1
        old_string = "\n" + old_string[:-1]

    return offset, old_string, new_string


def block_scalar(text: str, newline: str) -> list[str]:
    if "\n" not in text and "\r" not in text:
        encoded = json.dumps(text, ensure_ascii=False)
        return [f"        placeholder_text: {encoded}{newline}"]

    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    trailing_newlines = len(normalized) - len(normalized.rstrip("\n"))
    if trailing_newlines == 0:
        header = "|2-"
    elif trailing_newlines == 1:
        header = "|2"
    else:
        header = "|2+"

    result = [f"        placeholder_text: {header}{newline}"]
    content = normalized.split("\n")
    if trailing_newlines:
        content = content[:-1]
    result.extend(
        f"          {line}{newline}" if line else newline for line in content
    )
    return result


def render_placeholder(offset: int, length: int, text: str, newline: str) -> list[str]:
    return [
        f"      - offset: {offset}{newline}",
        f"        length: {length}{newline}",
        *block_scalar(text, newline),
    ]


def write_atomic(path: Path, text: str) -> None:
    mode = path.stat().st_mode
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as file:
        temporary = Path(file.name)
        file.write(text)
    os.chmod(temporary, mode)
    os.replace(temporary, path)


def update_task_info(
    task_info: Path,
    file_name: str,
    offset: int,
    length: int,
    replacement: str,
    placeholder_index: int,
    append: bool,
) -> None:
    text = read_text(task_info)
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines(keepends=True)
    file_start, file_end = find_file_block(lines, file_name)
    block = find_placeholders_block(lines, file_start, file_end)
    rendered = render_placeholder(offset, length, replacement, newline)

    if block is None:
        if append or placeholder_index == 0:
            insertion = file_start + 1
            while insertion < file_end and leading_spaces(lines[insertion]) > 4:
                insertion += 1
            lines[insertion:insertion] = [f"    placeholders:{newline}", *rendered]
        else:
            raise ValueError("the file entry has no placeholders")
    else:
        block_start, block_end = block
        entries = placeholder_ranges(lines, block_start, block_end)
        if append:
            ensure_separated(
                offset,
                length,
                [placeholder_span(lines, start) for start, _ in entries],
            )
            lines[block_end:block_end] = rendered
        elif 0 <= placeholder_index < len(entries):
            entry_start, entry_end = entries[placeholder_index]
            ensure_separated(
                offset,
                length,
                [
                    placeholder_span(lines, start)
                    for index, (start, _) in enumerate(entries)
                    if index != placeholder_index
                ],
            )
            lines[entry_start:entry_end] = rendered
        elif placeholder_index == 0 and not entries:
            lines[block_end:block_end] = rendered
        else:
            raise ValueError(
                f"placeholder index {placeholder_index} is out of range for {len(entries)} entries"
            )

    write_atomic(task_info, "".join(lines))


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Create a JetBrains Edu placeholder from an exact string replacement."
    )
    result.add_argument("path", type=Path, help="solution file containing old_string")

    old = result.add_mutually_exclusive_group(required=True)
    old.add_argument("--old-string")
    old.add_argument("--old-string-file", type=Path)

    new = result.add_mutually_exclusive_group(required=True)
    new.add_argument("--new-string")
    new.add_argument("--new-string-file", type=Path)

    result.add_argument("--task-info", type=Path)
    placement = result.add_mutually_exclusive_group()
    placement.add_argument("--placeholder-index", type=int, default=0)
    placement.add_argument("--append", action="store_true")
    return result


def main() -> None:
    arguments = parser().parse_args()
    source = arguments.path.resolve()
    task_info = (
        arguments.task_info.resolve()
        if arguments.task_info
        else source.parent / "task-info.yaml"
    )
    try:
        old_string = read_argument(arguments.old_string, arguments.old_string_file)
        new_string = read_argument(arguments.new_string, arguments.new_string_file)
        source_text = read_text(source)
    except (OSError, ValueError) as error:
        raise SystemExit(f"error: {error}") from error

    if not old_string:
        raise SystemExit("error: old_string must not be empty")

    try:
        file_name = source.relative_to(task_info.parent).as_posix()
    except ValueError:
        file_name = source.name

    occurrences = source_text.count(old_string)
    if occurrences != 1:
        raise SystemExit(
            f"error: expected old_string to occur exactly once in {source}, found {occurrences}"
        )

    try:
        offset = source_text.index(old_string)
        offset, old_string, new_string = normalize_replacement_bounds(
            source_text, offset, old_string, new_string
        )
        update_task_info(
            task_info=task_info,
            file_name=file_name,
            offset=offset,
            length=len(old_string),
            replacement=new_string,
            placeholder_index=arguments.placeholder_index,
            append=arguments.append,
        )
    except (OSError, ValueError) as error:
        raise SystemExit(f"error: {error}") from error

    action = "appended" if arguments.append else f"updated {arguments.placeholder_index}"
    print(
        f"{task_info}: {file_name} placeholder {action}; "
        f"offset={offset}, length={len(old_string)}"
    )


if __name__ == "__main__":
    main()
