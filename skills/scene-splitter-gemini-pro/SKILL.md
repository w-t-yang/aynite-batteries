---
name: scene-splitter-gemini-pro
description: Split a novel chapter markdown file into individual scene files. Trigger this skill whenever a user mentions analyzing, splitting, dividing, or extracting scenes from a chapter file.
---

# Scene Splitter

This skill helps you analyze a novel chapter markdown file, cleanly split it into individual scenes, save those scenes sequentially in a sibling directory, and mathematically validate that zero prose was lost during the extraction.

## Step 1: Input Verification

When the user provides an input file, verify that the file exists and that it constitutes a novel chapter.
- Read the initial contents of the file.
- Check for literary structure (chapter headings, paragraphs of prose, dialogue characters, etc).
- **If the file is NOT a novel chapter** (e.g. it's code, a JSON configuration, or a changelog): Immediately stop what you are doing and politely inform the user that this skill is only intended to split narrative chapters.

## Step 2: Content Analysis and Splitting

If the input file is a chapter, analyze the text and split it into discrete scenes.

**How to identify a scene break:**
- Explicit dinkuses/asterisks like `***`, `* * *`, or `---`
- Hard perspective changes or location skips
- Large chronological jumps

**Important Rules for Splitting:**
- Do NOT include the overarching chapter title (e.g. `# Chapter One`) inside the individual scene files. The overarching header belongs to the parent file, not the scene slices.
- Preserve **ALL** original prose exactly as it is written. No modifications or corrections to the source text are allowed. 
- Ensure you do NOT delete asterisks `***` or separator lines; place them logically at the end of the preceding scene or the start of the next scene. 

## Step 3: Scene Extraction and Routing

Create a folder to hold the scenes, and write the split scenes into individual files.

1. Create a `scenes/` folder in the **exact same directory path** as the original input file.
2. Formulate the filenames for each scene. Use the base name of the input file and append `-scene-XX.md` where `XX` is the 1-indexed serialized number, zero-padded to two digits (e.g., `01`, `02`).
   - Example DataFrame: If the user provides `/books/drafts/ch01.md`, and it splits into 3 scenes:
     - `/books/drafts/scenes/ch01-scene-01.md`
     - `/books/drafts/scenes/ch01-scene-02.md`
     - `/books/drafts/scenes/ch01-scene-03.md`
3. Write the extracted text into the corresponding files using your standard file write tool.

## Step 4: Validation against Original Text

Because text slicing carries a high risk of dropping paragraphs or mangling formatting, you must programmatically validate your extraction output using the bundled validation tool.

1. Run the validation script using your terminal `run_command` tool. The exact absolute path is provided below. Pass the path to the original un-split chapter file as the first argument:
   ```bash
   python /home/wentao/repos/aynite-res/skills/scene-splitter-gemini-pro/scripts/validate_scenes.py "<absolute/path/to/original/file.md>"
   ```

2. Read the script validation output.
   - If the script reports **SUCCESS**: Inform the user the split is completed effectively and error-free.
   - If the script reports **FAILURE (DATA LOSS DETECTED)**: Explicitly apologize to the user. Inform them that the split missed or altered text. Attempt to identify where the split failed and offer to try the extraction again.
