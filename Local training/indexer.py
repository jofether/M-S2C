"""
Offline Vector Database Indexer for M-S2C
=========================================
This script acts as the "Memory Builder" for the Multimodal Bug Localization system.
It loads the fully trained Phase 3 M-S2C model, extracts the AST source code nodes 
from the dataset, encodes them into the trained semantic space, and saves them 
into a highly efficient FAISS vector database (ms2c_codebase.index).
"""

import torch
import torch.nn.functional as F
from transformers import AutoTokenizer
import faiss
import json
import os
import numpy as np
import logging
import sys

# Import your custom architecture
from ms2c_model import MS2CFusionEngine

# --- EXPLICIT PATH RESOLVER ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.join(BASE_DIR, "Seed-and-Mutate", "ms2c-local")

# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | Indexer | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("indexer_logs.txt", mode='w', encoding='utf-8'), # 'w' overwrites old logs each time you re-index
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def build_faiss_index():
    logger.info("Loading TRAINED M-S2C Model for Offline Indexing...")
    tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
    
    # LOAD YOUR TRAINED BRAIN!
    model = MS2CFusionEngine()
    weights_path = "ms2c_phase3_FINAL.pt"
    
    if os.path.exists(weights_path):
        model.load_state_dict(torch.load(weights_path, map_location="cpu"))
        logger.info(f"✅ Successfully loaded Phase 3 weights from {weights_path}")
    else:
        logger.warning(f"⚠️ {weights_path} not found. Indexing with untrained weights!")
        
    model.eval() # Strictly evaluation mode

    # 1. Load the "Codebase"
    json_file_path = os.path.join(REPO_DIR, "data", "manifests", "spacing.json")
    with open(json_file_path, 'r', encoding='utf-8') as f:
        real_data = json.load(f)
        
    # Indexing 500 nodes to create a robust searchable codebase
    test_subset = real_data[:500] 
    
    node_mapping = {}
    vector_list = []

    logger.info(f"Encoding {len(test_subset)} AST nodes into the TRAINED Semantic Space...")
    
    for idx, item in enumerate(test_subset):
        code_snippet = item['positive_node']
        node_mapping[idx] = code_snippet
        
        inputs = tokenizer(
            code_snippet, padding='max_length', truncation=True, max_length=128, return_tensors="pt"
        )
        
        # Use your TRAINED CodeBERT encoder to map the code
        with torch.no_grad():
            outputs = model.codebert(**inputs)
            v_code = outputs.last_hidden_state[:, 0, :]
            v_code = F.normalize(v_code, p=2, dim=1)
            vector_list.append(v_code.numpy())

    embeddings = np.vstack(vector_list)

    d = 768 
    index = faiss.IndexFlatIP(d) 
    
    logger.info("Adding vectors to FAISS Database...")
    index.add(embeddings)
    logger.info(f"Total vectors successfully indexed: {index.ntotal}")

    faiss.write_index(index, "ms2c_codebase.index")
    with open("node_mapping.json", "w", encoding='utf-8') as map_file:
        json.dump(node_mapping, map_file)

        # --- DEMO VISUALIZATION EXPORT ---
    with open("node_library_visualization.txt", "w", encoding="utf-8") as txt_file:
        txt_file.write("=== M-S2C SEARCHABLE NODE LIBRARY ===\n")
        txt_file.write(f"Total AST Nodes Indexed: {len(node_mapping)}\n\n")
        for node_id, code_text in node_mapping.items():
            txt_file.write(f"--- AST NODE ID: {node_id} ---\n")
            txt_file.write(f"{code_text}\n")
            txt_file.write("="*50 + "\n\n")
        
    logger.info("SUCCESS: Saved 'ms2c_codebase.index' and 'node_mapping.json' to disk.")

if __name__ == "__main__":
    build_faiss_index()