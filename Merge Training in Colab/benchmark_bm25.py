"""
M-S2C External Benchmarking: Okapi BM25 Lexical Baseline
========================================================
"""
import json
import os
import logging
import sys
from rank_bm25 import BM25Okapi

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.join(BASE_DIR)

# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | BM25 Benchmark | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("benchmark_bm25_logs.txt", mode='w', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def run_bm25_benchmark():
    logger.info("🚀 INITIALIZING OKAPI BM25 LEXICAL BASELINE")
    
    with open("node_mapping.json", "r", encoding='utf-8') as f:
        node_mapping = json.load(f)
        
    corpus = [data['code'] for data in node_mapping.values()]
    tokenized_corpus = [doc.lower().split(" ") for doc in corpus]
    
    logger.info(f"Indexing {len(corpus)} AST nodes with BM25...")
    bm25 = BM25Okapi(tokenized_corpus)

    # ⚠️ FIXED: Using mutated_dataset_25k.json for consistency with training
    json_file_path = os.path.join(REPO_DIR, "mutated_dataset_25k.json")
    with open(json_file_path, 'r', encoding='utf-8') as f:
        test_set = json.load(f)[:1000]
    logger.info(f"📊 Using training dataset: {json_file_path} (1000 samples)")

    reciprocal_ranks = []
    hits_at_1 = 0

    for i, sample in enumerate(test_set):
        query_text = sample['text_anchor']
        ground_truth = sample['positive_node'].strip()

        tokenized_query = query_text.lower().split(" ")
        doc_scores = bm25.get_scores(tokenized_query)
        
        top_10_indices = sorted(range(len(doc_scores)), key=lambda i: doc_scores[i], reverse=True)[:10]

        target_rank = 0
        for rank, idx in enumerate(top_10_indices):
            # Bulletproof comparison: remove ALL whitespace variations
            if "".join(corpus[idx].split()) == "".join(ground_truth.split()):
                target_rank = rank + 1
                break
                
        if target_rank == 1: hits_at_1 += 1
        reciprocal_ranks.append(1.0 / target_rank if target_rank > 0 else 0.0)
        
        # Print progress every 10 samples
        if (i + 1) % 10 == 0:
            logger.info(f"Processed {i + 1}/{len(test_set)} queries...")

    mrr = sum(reciprocal_ranks) / len(test_set)
    top_1_acc = (hits_at_1 / len(test_set)) * 100

    logger.info("\n" + "="*50)
    logger.info("📉 EXTERNAL BENCHMARK: BM25 PERFORMANCE 📉")
    logger.info("="*50)
    logger.info(f"Top-1 Accuracy: {top_1_acc:.2f}%")
    logger.info(f"BM25 MRR:       {mrr:.4f}")
    logger.info("="*50)
    logger.info("Results saved to 'benchmark_bm25_logs.txt'")

if __name__ == "__main__":
    run_bm25_benchmark()