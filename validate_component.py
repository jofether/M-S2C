# validate_component.py
import sys
import os
import json
import torch

# Force Python to look in the exact directory this script is located in
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from bm25 import BM25ComponentRetriever
from ms2c import MS2CComponentRetriever


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def calculate_metrics(rank, total_queries, metrics_dict):
    """Updates the Hit@K and MRR sums based on the achieved rank."""
    if rank > 0:
        metrics_dict["mrr_sum"] += (1.0 / rank)
        if rank <= 1: metrics_dict["hits_at_1"] += 1
        if rank <= 3: metrics_dict["hits_at_3"] += 1
        if rank <= 5: metrics_dict["hits_at_5"] += 1
        if rank <= 10: metrics_dict["hits_at_10"] += 1
    return metrics_dict


def format_summary(metrics, total):
    """Calculates final percentages and MRR."""
    mrr = metrics["mrr_sum"] / total
    acc1 = (metrics["hits_at_1"] / total) * 100
    acc3 = (metrics["hits_at_3"] / total) * 100
    acc5 = (metrics["hits_at_5"] / total) * 100
    acc10 = (metrics["hits_at_10"] / total) * 100
    return f"MRR: {mrr:.4f} | Hit@1: {acc1:.2f}% | Hit@3: {acc3:.2f}% | Hit@5: {acc5:.2f}% | Hit@10: {acc10:.2f}%"


def run_validation():
    # 1. Setup Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    queries_path = os.path.join(base_dir, "validation_component", "component.json")
    corpus_path = os.path.join(base_dir, "validation_component_results", "indexed_nodes.json")
    images_dir = os.path.join(base_dir, "validation_component", "images")
    model_weights = os.path.join(base_dir, "ms2c_E2E_JOINT_BEST.pt")

    # Organized Results Folders
    results_base = os.path.join(base_dir, "validation_component_results")
    # UPDATED KEYS: Using 'uni' and 'multi' to match the loop logic
    folders = {
        "bm25": os.path.join(results_base, "bm25_logs"),
        "uni": os.path.join(results_base, "ms2c_unimodal_logs"),
        "multi": os.path.join(results_base, "ms2c_multimodal_logs")
    }
    for folder in folders.values(): ensure_dir(folder)

    # 2. Load Data and Initialize Retrievers
    with open(corpus_path, 'r', encoding='utf-8') as f:
        component_dict = json.load(f)
    with open(queries_path, 'r', encoding='utf-8') as f:
        queries_data = json.load(f)

    bm25_retriever = BM25ComponentRetriever(component_dict)
    ms2c_retriever = MS2CComponentRetriever(model_weights, component_dict)

    # 3. Tracking Variables
    total_queries = len(queries_data)
    global_metrics = {
        "bm25": {"hits_at_1": 0, "hits_at_3": 0, "hits_at_5": 0, "hits_at_10": 0, "mrr_sum": 0.0},
        "uni": {"hits_at_1": 0, "hits_at_3": 0, "hits_at_5": 0, "hits_at_10": 0, "mrr_sum": 0.0},
        "multi": {"hits_at_1": 0, "hits_at_3": 0, "hits_at_5": 0, "hits_at_10": 0, "mrr_sum": 0.0}
    }

    component_logs = {}

    # 4. Evaluation Loop
    print(f"Benchmarking {total_queries} queries...")
    for item in queries_data:
        comp_id = item["id"]
        comp_name = comp_id.split("_")[1]
        text_query = item["text_anchor"]
        pos_node = item["positive_node"]
        img_path = os.path.join(images_dir, item["image_anchor"])

        # --- A. BM25 Retrieval ---
        res_bm25 = bm25_retriever.retrieve_top_k(text_query, comp_name, k=10)
        rank_bm25 = (res_bm25.index(pos_node) + 1) if pos_node in res_bm25 else 0
        global_metrics["bm25"] = calculate_metrics(rank_bm25, total_queries, global_metrics["bm25"])

        # --- B. MS2C Unimodal ---
        res_uni, _ = ms2c_retriever.retrieve_top_k(text_query, comp_name, k=10, mode="unimodal")
        rank_uni = (res_uni.index(pos_node) + 1) if pos_node in res_uni else 0
        global_metrics["uni"] = calculate_metrics(rank_uni, total_queries, global_metrics["uni"])

        # --- C. MS2C Multimodal ---
        res_multi, alpha = ms2c_retriever.retrieve_top_k(text_query, comp_name, image_path=img_path, k=10,
                                                         mode="multimodal")
        rank_multi = (res_multi.index(pos_node) + 1) if pos_node in res_multi else 0
        global_metrics["multi"] = calculate_metrics(rank_multi, total_queries, global_metrics["multi"])

        # Accumulate logs for file writing
        if comp_id not in component_logs: component_logs[comp_id] = []
        component_logs[comp_id].append({
            "query": text_query,
            "target": pos_node,
            "bm25": {"rank": rank_bm25, "top10": res_bm25},
            "uni": {"rank": rank_uni, "top10": res_uni},
            "multi": {"rank": rank_multi, "top10": res_multi, "alpha": alpha}
        })

    # 5. Generate Logs
    print("Writing logs to subdirectories...")
    for cid, logs in component_logs.items():
        # m_type now correctly iterates through "bm25", "uni", and "multi"
        for m_type in ["bm25", "uni", "multi"]:
            f_path = os.path.join(folders[m_type], f"{cid}_{m_type.upper()}_logs.txt")
            with open(f_path, 'w', encoding='utf-8') as f:
                f.write(f"=== {m_type.upper()} RESULTS: {cid} ===\n\n")
                for l in logs:
                    f.write(f"Query: {l['query']}\nTarget: {l['target']}\n")
                    f.write(f"Rank: {l[m_type]['rank'] if l[m_type]['rank'] > 0 else 'FAILED'}\n")
                    if m_type == "multi": f.write(f"Gating Alpha: {l[m_type]['alpha']:.4f}\n")
                    f.write("--- Top 10 ---\n")
                    for i, node in enumerate(l[m_type]['top10'], 1):
                        marker = " <--- [HIT]" if node == l['target'] else ""
                        f.write(f"{i}. {node}{marker}\n")
                    f.write("\n" + "=" * 50 + "\n\n")

    # 6. Global Summary
    with open(os.path.join(results_base, "GLOBAL_BENCHMARK_SUMMARY.txt"), 'w') as f:
        f.write("GLOBAL EVALUATION SUMMARY\n" + "=" * 30 + "\n")
        f.write(f"BM25:        {format_summary(global_metrics['bm25'], total_queries)}\n")
        f.write(f"MS2C (Uni):  {format_summary(global_metrics['uni'], total_queries)}\n")
        f.write(f"MS2C (Multi): {format_summary(global_metrics['multi'], total_queries)}\n")

    print(f"Complete! Logs in: {results_base}")


if __name__ == "__main__":
    run_validation()