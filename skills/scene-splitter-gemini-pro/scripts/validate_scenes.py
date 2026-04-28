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

def validate(original_file):
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
        
    combined_content = ""
    for sf in scene_files:
        with open(sf, 'r', encoding='utf-8') as f:
            # We normalize each scene file individually and strip headers if the model accidentally included them
            combined_content += normalize_text(f.read(), strip_headers=True) + "\n"
            
    with open(original_file, 'r', encoding='utf-8') as f:
        original_lines = f.readlines()
        
    # Remove chapter title from original if it exists at the top
    start_idx = 0
    for i, line in enumerate(original_lines):
        trimmed = line.strip()
        if not trimmed:
            continue
        if HEADER_PATTERN.match(trimmed):
            start_idx = i + 1
            break
        else:
            break
            
    original_prose = "".join(original_lines[start_idx:])
    
    norm_original = normalize_text(original_prose)
    norm_combined = normalize_text(combined_content)
    
    if norm_original == norm_combined:
        print("✅ SUCCESS: The scenes perfectly match the original prose.")
        sys.exit(0)
    else:
        print("❌ FAILURE: Data loss or content mismatch detected.")
        print("\n--- DIFF (Original vs. Combined) ---")
        
        orig_split = norm_original.splitlines()
        comb_split = norm_combined.splitlines()
        
        diff = difflib.unified_diff(orig_split, comb_split, fromfile='Original', tofile='Combined', lineterm='')
        for line in diff:
            print(line)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate.py <path-to-original-file>")
        sys.exit(1)
    validate(sys.argv[1])
