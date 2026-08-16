---
name: patch-edu-placeholders
description:  patch the before-refactor to after-refactor as placeholder for JetBrains edu Task
---

## Tools

- `str_replace_placeholder.py` writes one exact old-to-new placeholder for any selected source file.
- `render_placeholders.py` applies placeholders for any selected source file; inspect its output directly.

# Rules

1. Render into a temporary file. Read it directly; inspect syntax, indentation, blank lines, and intended before-refactor behavior.
2. Forbidden edit source file during the placeholders patch to unsure offset valid.
3. Split the placeholder properly by refactor purpose when possible. 
4. Use small, light placeholders instead of long patch mud when possible.
5. Use multi token level placeholder instead of a whole line level if when.
