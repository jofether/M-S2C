# indexer_repository.py
import os
import json
import re
import subprocess


def extract_nodes_from_file(filepath):
    """
    Scans an entire file and extracts every opening JSX/HTML tag.
    Because we are analyzing whole files now, we don't split by 'export const'.
    We scan the entire document to capture all structural elements.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception as e:
        print(f"      -> [WARNING] Could not read {filepath}: {e}")
        return []

    # Our bulletproof regex to capture all opening and self-closing tags across multiple lines
    tag_pattern = re.compile(r"<[a-zA-Z0-9]+(?:\s+[^>]+?)*\s*/?>", re.DOTALL)
    raw_tags = tag_pattern.findall(content)

    nodes = []
    for tag in raw_tags:
        # Flatten multi-line tags into a single line to match the ground truth JSON
        clean_tag = " ".join(tag.split())

        # Exclude closing tags (e.g., </div>) as they contain no styling logic
        if not clean_tag.startswith("</"):
            nodes.append(clean_tag)

    # Return a deduplicated list of nodes
    return list(set(nodes))


def run_repo_indexer():
    # 1. Setup path management
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "validation_repository", "repository.json")

    # We will clone the GitHub repos into this temporary folder
    repos_dir = os.path.join(base_dir, "cloned_repos")
    results_dir = os.path.join(base_dir, "validation_repository_results/indexed_nodes")

    os.makedirs(repos_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    print(f"[TRACE] Loading repository queries from {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        queries_data = json.load(f)

    # 2. Extract unique GitHub repository URLs
    unique_repos = list(set([item["github_repo"] for item in queries_data]))

    # =====================================================================
    # --- TEST LINE: RESTRICT FETCHING TO 1 REPO ---
    # unique_repos = unique_repos[:1]  # TODO: Delete this line for full evaluation!
    print(f"[TRACE] TESTING MODE ACTIVE: Only processing 1 repository -> {unique_repos[0]}")
    # =====================================================================

    # 3. Process each repository
    for repo_url in unique_repos:
        repo_name = repo_url.split("/")[-1]
        repo_path = os.path.join(repos_dir, repo_name)

        # Clone the repository if we haven't already
        if not os.path.exists(repo_path):
            print(f"\n[TRACE] Cloning the 'buggy' branch of {repo_name} from GitHub...")
            # Use -b to specify the branch, and --single-branch to make the download faster
            subprocess.run(["git", "clone", "-b", "buggy", "--single-branch", repo_url, repo_path], check=True)
        else:
            print(f"\n[TRACE] Repository {repo_name} already cloned locally. Skipping download.")

        print(f"[TRACE] Traversing files and indexing AST nodes in {repo_name}...")
        repo_index = {}
        total_nodes = 0

        # 4. Traverse the directory structure
        for root, dirs, files in os.walk(repo_path):
            # Optimization: Skip massive dependency folders and git history
            if "node_modules" in root or ".git" in root:
                continue

            for file in files:
                # We only care about React/JavaScript source files
                if file.endswith((".jsx", ".js", ".tsx", ".ts")):
                    full_filepath = os.path.join(root, file)

                    # Calculate the relative path exactly as it appears in repository.json
                    # Example: "src/components/TimelineHeader.jsx"
                    relative_path = os.path.relpath(full_filepath, repo_path)
                    relative_path = relative_path.replace("\\", "/")  # Windows pathing fix

                    # Extract the nodes
                    nodes = extract_nodes_from_file(full_filepath)

                    # If the file actually contains JSX tags, add it to our index dictionary
                    if nodes:
                        repo_index[relative_path] = nodes
                        total_nodes += len(nodes)

        # 5. Save the generated index library for this specific repository
        output_path = os.path.join(results_dir, f"{repo_name}_indexed_nodes.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(repo_index, f, indent=4)

        print(f"[TRACE] SUCCESS: Indexed {total_nodes} nodes across {len(repo_index)} files in {repo_name}.")
        print(f"[TRACE] Library saved to {output_path}")


if __name__ == "__main__":
    run_repo_indexer()
