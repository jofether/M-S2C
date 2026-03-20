# indexer_component.py
import os
import json
import re


def extract_all_nodes_per_component(jsx_filepath):
    """
    Parses a React JSX file and extracts EVERY opening tag as an AST node.
    This includes <div>, <svg>, <path>, <span>, <li>, etc.
    Multi-line tags are reconstructed into single lines for similarity matching.
    """
    if not os.path.exists(jsx_filepath):
        raise FileNotFoundError(f"Could not find {jsx_filepath}")

    with open(jsx_filepath, 'r', encoding='utf-8') as file:
        content = file.read()

    component_dict = {}

    # Split the file by components to isolate the search space per component
    blocks = re.split(r'(?=export\s+const)', content)

    for block in blocks:
        match = re.search(r"export\s+const\s+([A-Za-z0-9_]+)", block)
        if not match:
            continue

        comp_name = match.group(1)
        nodes = []

        # Regex explanation:
        # <[a-zA-Z0-9]+ -> Matches the start of any tag
        # (?:\s+[^>]+?)? -> Non-capturing group for attributes (optional), handles multi-line
        # \s*\/?> -> Matches the end of the opening or self-closing tag
        tag_pattern = re.compile(r"<[a-zA-Z0-9]+(?:\s+[^>]+?)*\s*/?>", re.DOTALL)

        raw_tags = tag_pattern.findall(block)

        for tag in raw_tags:
            # Flatten multi-line tags into a single line to match the ground truth JSON
            clean_tag = " ".join(tag.split())

            # We exclude closing tags (e.g., </div>) as they contain no styling logic
            if not clean_tag.startswith("</"):
                nodes.append(clean_tag)

        # Use set to remove exact duplicates, then convert back to list
        component_dict[comp_name] = list(set(nodes))

    return component_dict


def run_indexer():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # FOR VALIDATION
    components_dir = os.path.join(base_dir, "validation_component", "components")
    output_path = os.path.join(base_dir, "validation_component_results", "indexed_nodes.json")

    # FOR TESTING
    # components_dir = os.path.join(base_dir, "testing_component", "components")
    # output_path = os.path.join(base_dir, "testing_component_results", "indexed_nodes.json")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print(f"[TRACE] indexing all tags from {components_dir}...")

    master_corpus_dict = {}

    # Iterate through all the batch files in the components directory
    if os.path.exists(components_dir):
        for filename in os.listdir(components_dir):
            if filename.endswith((".jsx", ".js", ".tsx", ".ts")):
                filepath = os.path.join(components_dir, filename)
                # Extract nodes from this specific batch file
                corpus_dict = extract_all_nodes_per_component(filepath)
                # Merge the results into our master dictionary
                master_corpus_dict.update(corpus_dict)
    else:
        print(f"[ERROR] Directory not found: {components_dir}")
        return

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(master_corpus_dict, f, indent=4)

    for comp, nodes in master_corpus_dict.items():
        print(f"   -> {comp}: {len(nodes)} nodes indexed.")

    print(f"[TRACE] SUCCESS: Results saved to {output_path}")


if __name__ == "__main__":
    run_indexer()
