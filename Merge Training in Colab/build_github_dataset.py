"""
M-S2C GitHub Dataset Builder
============================
A helper script to safely append real-world GitHub bug cases 
into the `github_test_dataset.json` file without messing up the JSON formatting.
"""

import json
import os

# --- EXPLICIT PATH RESOLVER ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.join(BASE_DIR)
MANIFESTS_DIR = os.path.join(REPO_DIR)
JSON_FILE_PATH = os.path.join(MANIFESTS_DIR, "github_test_dataset.json")

def append_to_dataset(new_bug_entry):
    # Ensure the directory exists
    os.makedirs(MANIFESTS_DIR, exist_ok=True)
    
    # Load existing data or start a new list
    if os.path.exists(JSON_FILE_PATH):
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
            try:
                dataset = json.load(f)
            except json.JSONDecodeError:
                print("⚠️  Warning: JSON file is empty or corrupted. Starting fresh.")
                dataset = []
    else:
        dataset = []

    # Append the new bug
    dataset.append(new_bug_entry)

    # Save it back with beautiful formatting
    with open(JSON_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=4)
        
    print(f"✅ Successfully added bug from '{new_bug_entry['github_repo']}' to the dataset!")
    print(f"📁 Total bugs in dataset: {len(dataset)}")


if __name__ == "__main__":
    # =====================================================================
    # 🛑 PASTE YOUR GITHUB BUG DETAILS HERE 
    # =====================================================================
    
    new_bug = {
        "github_repo": "facebook/react",
        
        # The title or description of the issue on GitHub
        "text_anchor": "The success alert close button is pushed too far to the left and overlapping the text.",
        
        # The filename of the screenshot you saved in data/screenshots/
        "image_anchor": "issue_42_alert_bug.png",
        
        # The exact AST Node / HTML element from the "Fix Commit" (Ground Truth)
        "positive_node": '<button type="button" aria-label="close" className="mr-3">\n  <XIcon className="w-4 h-4" />\n</button>',
        
        # Where did this code come from in the repo?
        "file_path": "src/components/Alerts/SuccessAlert.jsx",
        
        # What line does this component start on?
        "line_start": 14
    }

    # =====================================================================
    # Run the function to save it!
    # =====================================================================
    append_to_dataset(new_bug)