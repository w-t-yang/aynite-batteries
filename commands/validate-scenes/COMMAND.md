---
name: validate-scenes
description: Validates extracted scenes against an original chapter file, outputting the exact diff if data loss or formatting changes occurred.
parameters:
  - name: input_file
    description: Absolute path to the original markdown file
    required: false
  - name: fix
    description: "Whether to auto-fix missing lines (--fix)"
    required: false
    default: ""
---

# Validate Scenes Command

This command ensures that after splitting a chapter, no content was lost. It now supports an **Auto-Fix** mode.

## Auto-Fix Mode
If you run with `--fix`, the command will:
1. Identify paragraphs that exist in the original file but are missing from the scenes.
2. Determine which scene file each missing paragraph belongs to (based on surrounding context).
3. Patch the scene files on disk automatically.

## Usage
`>validate-scenes --fix @04.md`

It takes the path to the original chapter markdown file, finds the sibling `scenes/` directory, concatenates all `-scene-*.md` files in numerical order, strips the top header from the original file (if present), normalizes the text spacing, and verifies if the two match perfectly.

If they match, it prints a success message.
If they DO NOT match, it will print a unified diff line-by-line showing exactly what was lost, altered, or added during the split.

## Usage

You can mention the command and provide a file path explicitly:
`>validate-scenes /path/to/my/book/chapter_1.md`

Or if you have the file open in the active editor, you can just call it directly, and it will use the current file automatically:
`>validate-scenes`
