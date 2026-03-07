import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
import faiss
import json
import os
import numpy as np

# --- EXPLICIT PATH RESOLVER ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.join(BASE_DIR, "Seed-and-Mutate", "ms2c-local")

def build_faiss_index():
    print("Loading CodeBERT for Offline Indexing...")
    # We only need the text/code encoder for the offline phase
    tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
    model = AutoModel.from_pretrained("microsoft/codebert-base")
    model.eval() # Strictly evaluation mode

    # 1. Load the "Codebase" (Simulating AST nodes extracted by Tree-sitter)
    json_file_path = os.path.join(REPO_DIR, "data", "manifests", "spacing.json")
    with open(json_file_path, 'r', encoding='utf-8') as f:
        real_data = json.load(f)
        
    # To keep the local test fast, we will index a "repository" of 100 AST nodes
    test_subset = real_data[:100]
    
    # We must keep a mapping of ID -> Code so we know what FAISS retrieves later
    node_mapping = {}
    vector_list = []

    print(f"\nEncoding {len(test_subset)} AST nodes into the Semantic Space...")
    
    for idx, item in enumerate(test_subset):
        code_snippet = item['positive_node']
        node_mapping[idx] = code_snippet
        
        # Tokenize AST Node
        inputs = tokenizer(
            code_snippet, padding='max_length', truncation=True, max_length=128, return_tensors="pt"
        )
        
        # Encode and L2 Normalize (CRUCIAL for Cosine Similarity in FAISS)
        with torch.no_grad():
            outputs = model(**inputs)
            v_code = outputs.last_hidden_state[:, 0, :]
            v_code = F.normalize(v_code, p=2, dim=1)
            vector_list.append(v_code.numpy())

    # Stack all individual vector arrays into one giant 2D matrix [100, 768]
    embeddings = np.vstack(vector_list)

    # 2. Initialize FAISS Vector Database
    d = 768 # CodeBERT's embedding dimension
    
    # We use IndexFlatIP (Inner Product). 
    # Because we L2-normalized the vectors above, Inner Product is mathematically identical to Cosine Similarity!
    index = faiss.IndexFlatIP(d) 
    
    print("\nAdding vectors to FAISS Database...")
    index.add(embeddings)
    print(f"Total vectors successfully indexed: {index.ntotal}")

    # 3. Save the Index and Mapping to Disk
    faiss.write_index(index, "ms2c_codebase.index")
    with open("node_mapping.json", "w") as map_file:
        json.dump(node_mapping, map_file)
        
    print("SUCCESS: Saved 'ms2c_codebase.index' and 'node_mapping.json' to disk.")

if __name__ == "__main__":
    build_faiss_index()