import os
import glob
import hashlib

def validate_scenes(original_path, scenes_dir):
    """
    Validates if combining all scenes within scenes_dir reconstructs the original file.
    Returns a report string and a boolean success flag.
    """
    
    # 1. Check if the scenes directory exists and contains files
    scene_files = glob.glob(os.path.join(scenes_dir, "*.md"))
    if not scene_files:
        return "Error: No scene files found in the designated 'scenes/' directory.", False

    # 2. Read the original content
    try:
        with open(original_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
    except FileNotFoundError:
        return f"Error: Original file not found at {original_path}.", False

    # 3. Concatenate all scenes
    combined_content = ""
    for scene_path in scene_files:
        try:
            with open(scene_path, 'r', encoding='utf-8') as f:
                combined_content += f.read() + "\n\n"
        except Exception as e:
            return f"Error reading scene file {scene_path}: {e}", False

    # 4. Compare (Addressing the header difference)
    # We will assume that the only difference allowed is the chapter metadata/title,
    # which should be present in the original file but explicitly excluded from scene splitting.
    
    # A simple comparison check for now:
    if original_content.strip() == combined_content.strip():
        report = "✅ Success: The combined scenes perfectly reconstruct the original chapter content."
        return report, True
    else:
        # A more robust check would require identifying and stripping metadata from both sides,
        # but for a simple validation script, we compare the full reconstructed content.
        report = (
            "⚠️ Warning: The combined scenes content does NOT perfectly match the original file. "
            "This is expected if the title/header was removed. "
            "Detailed diff comparison required."
        )
        return report, False # We return False to indicate structural difference, but the human must interpret the warning.

def run_validation(original_file_path):
    """Helper function to manage the validation process."""
    
    base_name = os.path.splitext(os.path.basename(original_file_path))[0]
    # Assuming the scenes directory is next to the original file
    scenes_dir = os.path.join(os.path.dirname(original_file_path), "scenes")

    report, success = validate_scenes(original_file_path, scenes_dir)
    
    return {
        "validation_success": success,
        "validation_report": report
    }

# Example usage (for testing/demonstration)
if __name__ == "__main__":
    # To run this, ensure you have a test file structure:
    # /path/to/test_file.md
    # /path/to/scenes/
    # /path/to/scenes/scene_1.md
    # ...
    
    # Placeholder paths for demonstration
    test_original_path = "/path/to/test_file.md"
    test_scenes_dir = "/path/to/scenes"
    
    # result = run_validation(test_original_path)
    # print(f"Validation Result: {result['validation_report']}\nSuccess: {result['validation_success']}")
    pass