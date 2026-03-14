"""
Multimodal Bug Localization Retrieval Script
============================================
This script simulates the final user experience of the M-S2C model.
It takes a Bug Report (text) and a Screenshot (image), fuses them using 
the trained Adaptive Gating Network, and searches the FAISS Vector Database 
to retrieve the exact line of buggy code (AST node) causing the issue.
"""

import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, ViTImageProcessor
from PIL import Image
import faiss
import json
import os
import logging
import sys

from ms2c_model import MS2CFusionEngine

# --- EXPLICIT PATH RESOLVER ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.join(BASE_DIR)

# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s", # Keeping format simple here so the UI prints look nice
    handlers=[
        logging.FileHandler("retrieval_logs.txt", mode='a', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def simulate_bug_localization(k=3):
    """
    Runs the inference pipeline to locate a bug based on multimodal inputs.
    
    Args:
        k (int): The number of top candidate code snippets to retrieve.
    """
    logger.info("1. Booting up M-S2C Diagnosis Engine...")
    model = MS2CFusionEngine()
    
    # LOAD THE TRAINED BRAIN!
    weights_path = "ms2c_E2E_JOINT_BEST.pt"
    if os.path.exists(weights_path):
        model.load_state_dict(torch.load(weights_path, map_location="cpu"))
        logger.info(f"✅ Successfully loaded {weights_path}")
    else:
        logger.warning("⚠️ E2E Joint weights not found! Running with untrained model.")
        
    model.eval() # Strictly evaluation mode for inference

    tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
    image_processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224-in21k")

    # 2. Load the FAISS Index and Mapping
    logger.info("2. Connecting to FAISS Vector Database...")
    index = faiss.read_index("ms2c_codebase.index")
    with open("node_mapping.json", "r", encoding='utf-8') as f:
        node_mapping = json.load(f)

    # Load validation dataset
    json_file_path = os.path.join(REPO_DIR, "validation", "spacing.json")
    with open(json_file_path, 'r', encoding='utf-8') as f:
        real_data = json.load(f)
        
    query_sample = real_data[0] 
    query_text = query_sample['text_anchor']
    image_path = os.path.normpath(os.path.join(REPO_DIR, "validation", query_sample['image_anchor']))

    logger.info(f"\n--- USER BUG REPORT ---")
    logger.info(f"Text: '{query_text}'")
    logger.info(f"Image: Loaded from {os.path.basename(image_path)}")
    logger.info(f"-----------------------\n")
    
    logger.info(f"🎯 GROUND TRUTH TARGET: {query_sample['positive_node'][:100]}...")

    # 4. Process Inputs
    text_enc = tokenizer(query_text, padding='max_length', truncation=True, max_length=512, return_tensors="pt")
    image = Image.open(image_path).convert("RGB")
    pixel_values = image_processor(images=image, return_tensors="pt").pixel_values

    # 5. Generate Multimodal Anchor Embedding
    logger.info("3. Fusing Modalities and calculating Alpha...")
    with torch.no_grad():
        v_text, v_visual_aligned, alpha = model(
            input_ids=text_enc.input_ids, 
            attention_mask=text_enc.attention_mask, 
            pixel_values=pixel_values
        )
        
        # S_final Aggregation Strategy (Adaptive Gating)
        v_anchor = (alpha * v_text) + ((1.0 - alpha) * v_visual_aligned)
        v_anchor = F.normalize(v_anchor, p=2, dim=1)

    logger.info(f"   -> Calculated Alpha Weight: {alpha.item():.4f}")

    # 6. FAISS Top-K Search
    logger.info(f"\n4. Searching {index.ntotal}-node Knowledge Base for Top-{k} Matches...")
    query_vector = v_anchor.numpy() 
    
    scores, indices = index.search(query_vector, k)

    logger.info("\n✅ TOP-K RETRIEVAL RESULTS:")
    for rank, (score, node_id) in enumerate(zip(scores[0], indices[0])):
        # result_data is now a dictionary containing code, file_path, and line_number
        result_data = node_mapping[str(node_id)] 
        
        logger.info(f"Rank {rank + 1} (Score: {score:.4f})")
        # --- NEW: DISPLAY THE FILE PATH AND LINE ---
        logger.info(f"📍 Location: {result_data['file_path']} (Line: {result_data['line_number']})")
        logger.info(f"Code Snippet: {result_data['code'][:100]}... [TRUNCATED]")
        logger.info("-" * 50)

if __name__ == "__main__":
    simulate_bug_localization(k=3)