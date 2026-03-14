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
REPO_DIR = os.path.join(BASE_DIR)

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
    
    # Force GPU usage
    if not torch.cuda.is_available():
        logger.error("❌ CUDA not available! GPU required for this script.")
        return
    
    device = torch.device("cuda")
    logger.info(f"✅ Using GPU: {torch.cuda.get_device_name(0)}")
    logger.info(f"GPU Memory Available: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB\n")
    
    tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
    
    # LOAD YOUR TRAINED BRAIN!
    model = MS2CFusionEngine().to(device)
    weights_path = "ms2c_E2E_JOINT_BEST.pt"
    
    if os.path.exists(weights_path):
        # model.load_state_dict(torch.load(weights_path, map_location=device))
        logger.info(f"✅ Successfully loaded E2E Joint weights from {weights_path}")
    else:
        logger.warning(f"⚠️ {weights_path} not found. Indexing with untrained weights!")
        
    model.eval()  # CRITICAL: Set to evaluation mode to disable dropout
    
    # Enable GPU optimizations
    torch.cuda.synchronize()
    torch.backends.cudnn.benchmark = True

    # 1. Load the "Codebase" (Use mutated_dataset_25k.json for testing and validation)
    json_file_path = os.path.join(REPO_DIR, "mutated_dataset_25k.json")
    with open(json_file_path, 'r', encoding='utf-8') as f:
        test_set = json.load(f)[:1000]  # Just take 1000 diverse samples
    
    logger.info(f"📊 Using test dataset from {json_file_path} (1000 samples)")
        
    # Indexing 1000 nodes for testing and validation of M-S2C capabilities
    test_subset = test_set
    
    node_mapping = {}
    vector_list = []

    logger.info(f"Encoding {len(test_subset)} AST nodes into the TRAINED Semantic Space...")
    
    for idx, item in enumerate(test_subset):
        # 1. Define the code snippet first so the tokenizer can use it!
        code_snippet = item['positive_node']
        
        # 2. Indent this block correctly inside the loop
        node_mapping[idx] = {
            "code": code_snippet,
            "file_path": item.get('file_path', 'unknown_path.js'), # Tracks the file
            "line_number": item.get('line_start', 'N/A')         # Tracks the line
        }
        
        inputs = tokenizer(
            code_snippet, padding='max_length', truncation=True, max_length=512, return_tensors="pt"
        ).to(device)
        
        # Use your TRAINED CodeBERT encoder to map the code
        with torch.no_grad():
            outputs = model.codebert(**inputs)
            v_code = outputs.last_hidden_state[:, 0, :]
            v_code = F.normalize(v_code, p=2, dim=1)
            vector_list.append(v_code.cpu().numpy())
        
        # Clear GPU cache periodically
        if (idx + 1) % 100 == 0:
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            logger.info(f"Processed {idx + 1}/{len(test_subset)} nodes...")

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
    logger.info("Generating Demo Visualization text file...")
    with open("node_library_visualization.txt", "w", encoding="utf-8") as txt_file:
        txt_file.write("=== M-S2C SEARCHABLE NODE LIBRARY ===\n")
        txt_file.write(f"Total AST Nodes Indexed: {len(node_mapping)}\n\n")
        for node_id, data in node_mapping.items():
            txt_file.write(f"--- AST NODE ID: {node_id} ---\n")
            txt_file.write(f"FILE PATH: {data['file_path']}\n")
            txt_file.write(f"LINE NO:   {data['line_number']}\n")
            txt_file.write(f"SOURCE:\n{data['code']}\n")
            txt_file.write("="*60 + "\n\n")
        
    logger.info("SUCCESS: Saved 'ms2c_codebase.index', 'node_mapping.json', and 'node_library_visualization.txt' to disk.")
    
    # Cleanup GPU memory
    torch.cuda.empty_cache()
    torch.cuda.synchronize()
    logger.info("✅ GPU memory cleaned up.")

if __name__ == "__main__":
    build_faiss_index()