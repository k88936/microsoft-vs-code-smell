---
name: patch-edu-placeholders
description:  patch the before-refactor to after-refactor as placeholder for JetBrains edu Task
---
## Facts

* the physics file is the after-refactor answer, the original before-refactor is it with the placeholders  applied.

## Tools

- `str_replace_placeholder.py` writes one exact old-to-new placeholder for any selected source file.
- `render_placeholders.py` applies placeholders for any selected source file; inspect its output directly.

## Tool guarantees

* Placeholder text that does not start with a `# TODO` comment is rejected.
* A multi-line replacement is widened to the whole physical line, also when a one-line `old_string` was matched inside a deeper indentation. So the lines that follow keep their indentation and their length. If real code sits before the region on that line, the patch is rejected instead of corrupting the file.
* A region never keeps the line break that ends its last line: whenever both sides end with a line break the tool drops it from both, so a `length` stops on the last visible character and carries no tail into the next line.
* To rebuild a placeholder set, drop the `placeholders:` block and append every entry again with `--append`.

# Rules

1. Render into a temporary file. Read it directly; inspect syntax, indentation, blank lines, and intended before-refactor behavior.
2. All placeholders should start from a TODO comment
3. NEVER edit the source file during the placeholder patch to ensure the offset is valid.
4. Split the placeholder properly by refactor purpose when possible. 
5. Use small, light placeholders instead of a long ugly patch when possible.
6. Use (multi)token level placeholders instead of a whole line level if when.
7. Never placeholder the whole method/class, leave the method/class name and the def structure, since we need a stable name to do ast check in the refactor test. 
8. Never require the renderred-after-patch exactly the same to before-refactor code, since we may leave method/class frameworks.
