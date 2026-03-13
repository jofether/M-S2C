"""
M-S2C Component-Based Validation Script
=======================================
This script runs a batch evaluation over the test dataset to calculate
the official performance metrics defined in the thesis:
- Top-K Accuracy (Hit@1, Hit@5, Hit@10)
- Mean Reciprocal Rank (MRR)
- Mean Average Precision (MAP)
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
    format="%(message)s",
    handlers=[
        logging.FileHandler("evaluation_results.txt", mode='w', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def evaluate_model():
    """
    Evaluates the model on the full GitHub dataset and calculates Top-K, MRR, and MAP.
    """
    logger.info("==================================================")
    logger.info("🚀 INITIALIZING M-S2C GITHUB REAL-WORLD VALIDATION")
    logger.info("==================================================\n")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 1. Load the Trained Model
    model = MS2CFusionEngine().to(device)
    weights_path = "ms2c_E2E_JOINT_BEST.pt"
    if os.path.exists(weights_path):
        model.load_state_dict(torch.load(weights_path, map_location=device))
        logger.info(f"✅ Loaded Trained Brain: {weights_path}")
    else:
        logger.warning("⚠️ E2E Joint weights not found! Running with untrained model.")
    model.eval()

    tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
    image_processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224-in21k")

    # 2. Load the Node Library (FAISS + Mapping)
    logger.info("✅ Loading FAISS Node Library (ms2c_codebase.index)...")
    try:
        index = faiss.read_index("ms2c_codebase.index")
        with open("node_mapping.json", "r", encoding='utf-8') as f:
            node_mapping = json.load(f)
    except Exception as e:
        logger.error(f"❌ Failed to load Node Library. Did you run indexer.py first? Error: {e}")
        return

    # 3. Load the GitHub Real-World Dataset
    json_file_path = os.path.join(REPO_DIR, "github_test_dataset.json")
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            test_set = json.load(f) 
    except FileNotFoundError:
        logger.error(f"❌ Could not find {json_file_path}. Make sure your GitHub dataset is named correctly!")
        return
    
    logger.info(f"✅ Loaded {len(test_set)} real-world test samples for validation.\n")
    logger.info("⏳ Running Batch Inference... This may take a few minutes depending on GPU.\n")

    # Metric Trackers
    hits_at_1 = 0
    hits_at_5 = 0
    hits_at_10 = 0
    reciprocal_ranks = []
    average_precisions = []

    k_max = 10 # We search up to Top 10 to calculate our metrics

    for i, sample in enumerate(test_set):
        query_text = sample['text_anchor']
        image_path = os.path.normpath(os.path.join(REPO_DIR, "03_screenshots", sample['image_anchor']))
        ground_truth_code = sample['positive_node'].strip()

        # Process Modalities
        text_enc = tokenizer(query_text, padding='max_length', truncation=True, max_length=512, return_tensors="pt").to(device)
        
        try:
            image = Image.open(image_path).convert("RGB")
            pixel_values = image_processor(images=image, return_tensors="pt").pixel_values.to(device)
        except Exception as e:
            logger.warning(f"⚠️ Skipping sample {i}: Image not found ({sample['image_anchor']})")
            continue

        # Forward Pass
        with torch.no_grad():
            v_text, v_visual_aligned, alpha = model(
                input_ids=text_enc.input_ids, 
                attention_mask=text_enc.attention_mask, 
                pixel_values=pixel_values
            )
            # Adaptive Fusion
            v_anchor = (alpha * v_text) + ((1.0 - alpha) * v_visual_aligned)
            v_anchor = F.normalize(v_anchor, p=2, dim=1)

        # FAISS Search
        query_vector = v_anchor.cpu().numpy()
        scores, indices = index.search(query_vector, k_max)

        # Evaluate against Ground Truth
        target_rank = 0
        is_hit = False

        for rank, node_id in enumerate(indices[0]):
            retrieved_data = node_mapping[str(node_id)]
            retrieved_code = retrieved_data['code'].strip()

            # Check if retrieved code matches the target component exactly
            if retrieved_code == ground_truth_code:
                target_rank = rank + 1
                is_hit = True
                break
        
        # Calculate Metrics for this specific query
        if is_hit:
            if target_rank == 1: hits_at_1 += 1
            if target_rank <= 5: hits_at_5 += 1
            if target_rank <= 10: hits_at_10 += 1
            
            rr = 1.0 / target_rank
            reciprocal_ranks.append(rr)
            average_precisions.append(rr) # For single-target retrieval, AP = RR
        else:
            reciprocal_ranks.append(0.0)
            average_precisions.append(0.0)

        # Print progress every 10 samples
        if (i + 1) % 10 == 0:
            logger.info(f"Processed {i + 1}/{len(test_set)} queries...")

    # --- FINAL MATH & OUTPUT ---
    total_queries = len(reciprocal_ranks)
    
    if total_queries == 0:
        logger.error("❌ No queries processed successfully. Check your image paths!")
        return

    top_1_acc = (hits_at_1 / total_queries) * 100
    top_5_acc = (hits_at_5 / total_queries) * 100
    top_10_acc = (hits_at_10 / total_queries) * 100
    
    mrr = sum(reciprocal_ranks) / total_queries
    map_score = sum(average_precisions) / total_queries

    logger.info("\n" + "="*50)
    logger.info("🏆 FINAL M-S2C PERFORMANCE METRICS 🏆")
    logger.info("="*50)
    logger.info(f"Test Set Size: {total_queries} Component Queries")
    logger.info(f"Node Library Searched: ms2c_codebase.index ({index.ntotal} AST Nodes)")
    logger.info("-" * 50)
    logger.info(f"TOP-K ACCURACY:")
    logger.info(f"  ➜ Hit@1:  {top_1_acc:.2f}% (Found exact bug on first try)")
    logger.info(f"  ➜ Hit@5:  {top_5_acc:.2f}% (Found bug in top 5 suggestions)")
    logger.info(f"  ➜ Hit@10: {top_10_acc:.2f}% (Found bug in top 10 suggestions)")
    logger.info("-" * 50)
    logger.info(f"RANKING QUALITY:")
    logger.info(f"  ➜ MRR (Mean Reciprocal Rank): {mrr:.4f}")
    logger.info(f"  ➜ MAP (Mean Average Precision): {map_score:.4f}")
    logger.info("="*50)
    logger.info("Results saved to 'evaluation_results.txt'")

if __name__ == "__main__":
    evaluate_model()