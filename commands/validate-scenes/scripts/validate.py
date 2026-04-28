import sys
import os
import glob
import re
import difflib

# Global pattern for chapter headers (Markdown headings, Chinese 第x章, English Chapter X, etc.)
HEADER_PATTERN = re.compile(r'^(#\s*|第\s*\d+\s*章|Chapter\s*\d+|[一二三四五六七八九十百\d]+\s*、)', re.IGNORECASE)

def normalize_text(text, strip_headers=False):
    """Remove leading/trailing whitespace per line, drop empty lines, and strip separators/headers."""
    # Strip horizontal rules often added by models
    text = re.sub(r'^\s*(\*\*\*|---|---|\* \* \*)\s*$', '', text, flags=re.MULTILINE)
    
    lines = text.split('\n')
    
    # Optionally strip headers (used for individual scene files that might contain them)
    if strip_headers:
        temp_lines = []
        found_header = False
        for line in lines:
            trimmed = line.strip()
            if not trimmed: continue
            if not found_header and HEADER_PATTERN.match(trimmed):
                found_header = True
                continue
            temp_lines.append(line)
        lines = temp_lines

    lines = [line.strip() for line in lines]
    lines = [line for line in lines if line]
    return '\n'.join(lines)

def validate_and_fix(original_file, do_fix=False):
    if not os.path.isfile(original_file):
        print(f"FAILURE: Original file {original_file} not found.")
        sys.exit(1)
        
    parent_dir = os.path.dirname(os.path.abspath(original_file))
    scenes_dir = os.path.join(parent_dir, 'scenes')
    
    if not os.path.isdir(scenes_dir):
        print(f"FAILURE: Scenes directory {scenes_dir} not found.")
        sys.exit(1)
        
    base_name = os.path.splitext(os.path.basename(original_file))[0]
    scene_files = sorted(glob.glob(os.path.join(scenes_dir, f"{base_name}-scene-*.md")))
    
    if not scene_files:
        print(f"FAILURE: No scene files found matching {base_name}-scene-*.md in {scenes_dir}")
        sys.exit(1)

    # 1. Prepare Original Prose
    with open(original_file, 'r', encoding='utf-8') as f:
        original_lines = f.readlines()
    
    start_idx = 0
    for i, line in enumerate(original_lines):
        trimmed = line.strip()
        if not trimmed: continue
        if HEADER_PATTERN.match(trimmed):
            start_idx = i + 1
            break
        else: break
    
    original_prose_raw = "".join(original_lines[start_idx:])
    norm_original = normalize_text(original_prose_raw)
    orig_paras = norm_original.split('\n')
    
    # 2. Get Scenes Content
    scenes_data = [] # List of {path, norm_list}
    combined_norm_lines = []
    line_to_scene_map = [] # (scene_idx, line_content)
    
    for idx, sf in enumerate(scene_files):
        with open(sf, 'r', encoding='utf-8') as f:
            norm = normalize_text(f.read(), strip_headers=True)
            lines = norm.split('\n') if norm else []
            scenes_data.append({'path': sf, 'lines': lines})
            for line in lines:
                combined_norm_lines.append(line)
                line_to_scene_map.append((idx, line))

    # 3. Validation Check
    combined_norm = "\n".join(combined_norm_lines)
    if norm_original == combined_norm:
        print("✅ SUCCESS: The scenes perfectly match the original prose.")
        return

    if not do_fix:
        print("❌ FAILURE: Data loss or content mismatch detected.")
        print("\n--- DIFF (Original vs. Combined) ---")
        diff = difflib.unified_diff(orig_paras, combined_norm_lines, fromfile='Original', tofile='Combined', lineterm='')
        for line in diff:
            print(line)
        sys.exit(1)

    # 4. Surgical Fix
    print("❌ FAILURE: Data loss detected. 🛠 Attempting to Surgical Fix...")
    
    # Map each original paragraph to the FIRST scene it appears in, if any.
    matcher = difflib.SequenceMatcher(None, orig_paras, combined_norm_lines)
    
    # para_assignment[para_idx] = scene_idx
    para_assignment = [None] * len(orig_paras)
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            for offset in range(i2 - i1):
                raw_idx = j1 + offset
                if raw_idx < len(line_to_scene_map):
                    para_assignment[i1 + offset] = line_to_scene_map[raw_idx][0]

    # Fill Gaps
    current_scene = 0
    for i in range(len(para_assignment)):
        if para_assignment[i] is not None:
            current_scene = para_assignment[i]
        else:
            # Paragraph is missing! Assign to current last-seen scene.
            para_assignment[i] = current_scene
            print(f"  + Patching lost paragraph into {os.path.basename(scene_files[current_scene])}: {orig_paras[i][:50]}...")

    # Group into final contents
    new_scenes_content = {idx: [] for idx in range(len(scene_files))}
    for i, scene_idx in enumerate(para_assignment):
        new_scenes_content[scene_idx].append(orig_paras[i])

    # 5. Write back to disk
    for idx, sf in enumerate(scene_files):
        with open(sf, 'w', encoding='utf-8') as f:
            f.write("\n\n".join(new_scenes_content[idx]))
            
    print("\n✅ SURGICAL FIX COMPLETE. All scenes intact. Re-verifying...")
    validate_and_fix(original_file, False)

if __name__ == "__main__":
    do_fix = "--fix" in sys.argv
    args = [a for a in sys.argv if not a.startswith("--")]
    
    if len(args) < 2:
        print("Usage: python validate.py <path-to-original-file> [--fix]")
        sys.exit(1)
        
    validate_and_fix(args[1], do_fix=do_fix)
