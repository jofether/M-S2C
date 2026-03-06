import json
import subprocess
import re

def normalize_code(code_string):
    """Strips ALL whitespace, tabs, and newlines for a pure logic comparison."""
    if not code_string:
        return ""
    # Standardizing for fuzzy match: removing whitespace and newlines
    return re.sub(r'\s+', '', code_string)

def run_verification():
    print("🔍 Starting Deep Verification...")
    
    try:
        with open('github_finetune.json', 'r', encoding='utf-8') as f:
            dataset = json.load(f)
    except FileNotFoundError:
        print("❌ Error: github_finetune.json not found.")
        return

    passed = 0
    failed = 0

    for index, item in enumerate(dataset):
        # Extract repo and bug ID from the path
        filename = item['image_path'].split('/')[-1]
        repo_name = filename.split('_bug')[0]
        
        # Get Bug ID for easier fixing
        bug_id_match = re.search(r'bug-(\d+)', filename)
        bug_id = bug_id_match.group(1) if bug_id_match else "Unknown"
        
        file_path = item.get('file_modified')
        neg_code = item.get('neg_code', '')
        
        if not file_path or not neg_code:
            print(f"⚠️  [L-FIX] {repo_name} | Bug #{bug_id} (Row {index}): MISSING file_path or neg_code")
            failed += 1
            continue
            
        neg_code_clean = normalize_code(neg_code)
        
        try:
            git_cmd = f'git -C "{repo_name}" show clean:"{file_path}"'
            clean_branch_code = subprocess.check_output(
                git_cmd, 
                shell=True, 
                text=True, 
                encoding='utf-8', 
                errors='ignore', 
                stderr=subprocess.DEVNULL
            )
            
            if neg_code_clean in normalize_code(clean_branch_code):
                passed += 1
            else:
                # DIAGNOSIS PRINT
                print(f"❌ [MISMATCH] {repo_name} | Bug #{bug_id}")
                print(f"   └─ File: {file_path}")
                print(f"   └─ JSON Code: {neg_code[:50]}...") # Shows start of code to identify it
                failed += 1
                
        except subprocess.CalledProcessError:
            print(f"⚠️  [GIT ERROR] {repo_name} | Bug #{bug_id}: Path '{file_path}' not found on clean branch.")
            failed += 1

    print("\n" + "="*40)
    print(f"🎯 VERIFICATION SUMMARY")
    print(f"✅ Verified: {passed}")
    print(f"❌ To be Fixed: {failed}")
    print("="*40)

if __name__ == "__main__":
    run_verification()