# validate_component.py
import sys
import os
import json
import csv
import torch

# Force Python to look in the exact directory this script is located in
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from bm25 import BM25ComponentRetriever
from ms2c_component import MS2CComponentRetriever

"""
=========================================================================================
Component Validation & Benchmarking Script
=========================================================================================
This script evaluates the performance of the Multimodal Sequence-to-Code (MS2C) Retriever
against a baseline Unimodal model and a standard BM25 lexical retriever.

Metrics Evaluated:
1. Mean Reciprocal Rank (MRR): Evaluates the overall ranking quality, heavily rewarding Rank 1.
2. Hit@K (1, 3, 5, 10): Measures the percentage of times the exact buggy node is in the Top K.
3. Mean Rank (MeanR): Calculates the average absolute rank of the target node across all queries.
   * Note: If the target node is not found in the Top 10, it is penalized with a rank of 11.
     A lower MeanR indicates better overall localization performance.
=========================================================================================
"""


def ensure_dir(path):
    """Utility function to safely create directories for logs."""
    if not os.path.exists(path):
        os.makedirs(path)


def calculate_metrics(rank, metrics_dict):
    """
    Updates the Hit@K, MRR, and Mean Rank sums based on the achieved rank.
    If the rank is 0 (Failed to retrieve in Top 10), it applies a penalty rank of 11 for MeanR.
    """
    if rank > 0:
        metrics_dict["mrr_sum"] += (1.0 / rank)
        if rank <= 1: metrics_dict["hits_at_1"] += 1
        if rank <= 3: metrics_dict["hits_at_3"] += 1
        if rank <= 5: metrics_dict["hits_at_5"] += 1
        if rank <= 10: metrics_dict["hits_at_10"] += 1
        metrics_dict["rank_sum"] += rank
    else:
        # Penalty for missing the Top 10 bounds
        metrics_dict["rank_sum"] += 11

    return metrics_dict


def format_summary(metrics, total):
    """Calculates final percentages, MRR, and Mean Rank for the global summary output."""
    if total == 0: return "No queries evaluated."

    mrr = metrics["mrr_sum"] / total
    mean_r = metrics["rank_sum"] / total
    acc1 = (metrics["hits_at_1"] / total) * 100
    acc3 = (metrics["hits_at_3"] / total) * 100
    acc5 = (metrics["hits_at_5"] / total) * 100
    acc10 = (metrics["hits_at_10"] / total) * 100

    return f"MeanR: {mean_r:.2f} | MRR: {mrr:.4f} | Hit@1: {acc1:.2f}% | Hit@3: {acc3:.2f}% | Hit@5: {acc5:.2f}% | Hit@10: {acc10:.2f}%"


def run_validation():
    # ====================================================================
    # 1. SETUP PATHS & DIRECTORIES
    # ====================================================================
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # FOR VALIDATION
    # queries_path = os.path.join(base_dir, "validation_component", "validation_dataset.json")
    # corpus_path = os.path.join(base_dir, "validation_component_results", "indexed_nodes.json")
    # images_dir = os.path.join(base_dir, "validation_component", "images")
    # results_base = os.path.join(base_dir, "validation_component_results")

    # FOR TESTING
    queries_path = os.path.join(base_dir, "testing_component", "testing_dataset.json")
    corpus_path = os.path.join(base_dir, "testing_component_results", "indexed_nodes.json")
    images_dir = os.path.join(base_dir, "testing_component", "images")
    results_base = os.path.join(base_dir, "testing_component_results")

    model_weights = os.path.join(base_dir, "ms2c_E2E_JOINT_BEST.pt")

    folders = {
        "bm25": os.path.join(results_base, "bm25_logs"),
        "uni": os.path.join(results_base, "ms2c_unimodal_logs"),
        "multi": os.path.join(results_base, "ms2c_multimodal_logs")
    }
    for folder in folders.values(): ensure_dir(folder)

    # ====================================================================
    # 2. DATA INGESTION & MODEL INITIALIZATION
    # ====================================================================
    with open(corpus_path, 'r', encoding='utf-8') as f:
        component_dict = json.load(f)
    with open(queries_path, 'r', encoding='utf-8') as f:
        queries_data = json.load(f)

    bm25_retriever = BM25ComponentRetriever(component_dict)
    ms2c_retriever = MS2CComponentRetriever(model_weights, component_dict)

    # Tracking Variables
    total_queries = len(queries_data)
    global_metrics = {
        "bm25": {"hits_at_1": 0, "hits_at_3": 0, "hits_at_5": 0, "hits_at_10": 0, "mrr_sum": 0.0, "rank_sum": 0},
        "uni": {"hits_at_1": 0, "hits_at_3": 0, "hits_at_5": 0, "hits_at_10": 0, "mrr_sum": 0.0, "rank_sum": 0},
        "multi": {"hits_at_1": 0, "hits_at_3": 0, "hits_at_5": 0, "hits_at_10": 0, "mrr_sum": 0.0, "rank_sum": 0}
    }

    hero_cases = []
    interference_cases = []
    master_csv_data = []
    component_logs = {}

    # ====================================================================
    # 3. EVALUATION LOOP
    # ====================================================================
    print(f"Benchmarking {total_queries} queries...")
    for item in queries_data:
        comp_id = item["id"]

        # Parse robust batch ID to map to the correct target file key
        parts = comp_id.split("_")
        if len(parts) >= 3 and parts[1].isdigit():
            batch_id = parts[1]
            target_file_key = "_".join(parts[2:])
        else:
            batch_id = "01"
            target_file_key = "_".join(parts[1:])

        # Note: Query expansion has been removed to preserve organic baseline benchmarking
        text_query = item["text_anchor"]
        pos_node = item["positive_node"]

        img_filename = item["image_anchor"]
        if f"_{batch_id}.png" not in img_filename:
            img_filename = img_filename.replace(".png", f"_{batch_id}.png")

        img_path = os.path.join(images_dir, img_filename)

        print(f"  -> Testing Query: {img_filename} (Searching in index for: {target_file_key})")

        # --- A. BM25 Retrieval ---
        res_bm25 = bm25_retriever.retrieve_top_k(text_query, target_file_key, k=10)
        rank_bm25 = (res_bm25.index(pos_node) + 1) if pos_node in res_bm25 else 0
        global_metrics["bm25"] = calculate_metrics(rank_bm25, global_metrics["bm25"])

        # --- B. MS2C Unimodal ---
        res_uni, _ = ms2c_retriever.retrieve_top_k(text_query, target_file_key, k=10, mode="unimodal")
        rank_uni = (res_uni.index(pos_node) + 1) if pos_node in res_uni else 0
        global_metrics["uni"] = calculate_metrics(rank_uni, global_metrics["uni"])

        # --- C. MS2C Multimodal ---
        res_multi, alpha = ms2c_retriever.retrieve_top_k(text_query, target_file_key, image_path=img_path, k=10,
                                                         mode="multimodal")
        rank_multi = (res_multi.index(pos_node) + 1) if pos_node in res_multi else 0
        global_metrics["multi"] = calculate_metrics(rank_multi, global_metrics["multi"])

        # --- D. Capture Max Text Score for Logger ---
        with torch.no_grad():
            text_inputs = ms2c_retriever.text_tokenizer(text_query, return_tensors="pt", truncation=True,
                                                        padding="max_length", max_length=128).to(
                ms2c_retriever.device)
            text_emb = ms2c_retriever.model.forward_text(text_inputs["input_ids"], text_inputs["attention_mask"])
            text_sim = torch.matmul(text_emb, ms2c_retriever.global_embeddings.T).squeeze(0)

            valid_indices = [i for i, data in enumerate(ms2c_retriever.global_corpus) if data[0] == target_file_key]
            if valid_indices:
                filtered_text_sim = text_sim[valid_indices]
                max_text_score = filtered_text_sim.max().item()
            else:
                max_text_score = 0.0

        # ====================================================================
        # 4. VISUALIZATION & ANALYTICS DATA GATHERING
        # ====================================================================
        if rank_multi > 0 and (rank_uni == 0 or rank_multi < rank_uni):
            hero_cases.append({
                "id": item["image_anchor"],
                "uni_rank": rank_uni if rank_uni > 0 else "Fail",
                "multi_rank": rank_multi,
                "alpha": alpha
            })
        elif rank_uni > 0 and (rank_multi == 0 or rank_uni < rank_multi):
            interference_cases.append({
                "id": item["image_anchor"],
                "uni_rank": rank_uni,
                "multi_rank": rank_multi if rank_multi > 0 else "Fail",
                "alpha": alpha
            })

        master_csv_data.append({
            "Query_ID": item["image_anchor"],
            "BM25_Rank": rank_bm25 if rank_bm25 > 0 else "Fail",
            "Uni_Rank": rank_uni if rank_uni > 0 else "Fail",
            "Multi_Rank": rank_multi if rank_multi > 0 else "Fail",
            "Alpha_Used": f"{alpha:.4f}",
            "Max_Text_Score": f"{max_text_score:.4f}"
        })

        if comp_id not in component_logs: component_logs[comp_id] = []
        component_logs[comp_id].append({
            "query": text_query,
            "target": pos_node,
            "bm25": {"rank": rank_bm25, "top10": res_bm25},
            "uni": {"rank": rank_uni, "top10": res_uni},
            "multi": {"rank": rank_multi, "top10": res_multi, "alpha": alpha}
        })

    # ====================================================================
    # 5. LOG & REPORT GENERATION
    # ====================================================================
    print("\n[TRACE] Writing detailed logs to subdirectories...")
    for cid, logs in component_logs.items():
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

    summary_path = os.path.join(results_base, "GLOBAL_BENCHMARK_SUMMARY.txt")
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("GLOBAL COMPONENT EVALUATION SUMMARY\n")
        f.write("=========================================\n")
        f.write(f"Total Valid Queries Evaluated: {total_queries}\n\n")
        f.write(f"BM25:        {format_summary(global_metrics['bm25'], total_queries)}\n")
        f.write(f"MS2C (Uni):  {format_summary(global_metrics['uni'], total_queries)}\n")
        f.write(f"MS2C (Multi): {format_summary(global_metrics['multi'], total_queries)}\n")

        f.write("\n\n")
        f.write("=========================================\n")
        f.write("TABLE 1: MULTIMODAL HERO CASES (VISION BOOST)\n")
        f.write("=========================================\n")
        if not hero_cases:
            f.write("No hero cases found in this run.\n")
        else:
            f.write(f"{'Query ID':<60} | {'Uni Rank':<10} | {'Multi Rank':<12} | {'Alpha'}\n")
            f.write("-" * 100 + "\n")
            hero_cases.sort(key=lambda x: x['multi_rank'])
            for hc in hero_cases:
                f.write(
                    f"{hc['id']:<60} | {str(hc['uni_rank']):<10} | {str(hc['multi_rank']):<12} | {hc['alpha']:.4f}\n")

        f.write("\n\n")
        f.write("=========================================\n")
        f.write("TABLE 2: VISION INTERFERENCE CASES (TEXT DEGRADATION)\n")
        f.write("=========================================\n")
        if not interference_cases:
            f.write("No interference cases found in this run.\n")
        else:
            f.write(f"{'Query ID':<60} | {'Uni Rank':<10} | {'Multi Rank':<12} | {'Alpha'}\n")
            f.write("-" * 100 + "\n")
            interference_cases.sort(key=lambda x: x['uni_rank'])
            for ic in interference_cases:
                f.write(
                    f"{ic['id']:<60} | {str(ic['uni_rank']):<10} | {str(ic['multi_rank']):<12} | {ic['alpha']:.4f}\n")

    # 7. Write Master CSV Logger
    csv_path = os.path.join(results_base, "MASTER_QUERY_COMPARISON.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Query_ID', 'BM25_Rank', 'Uni_Rank', 'Multi_Rank', 'Alpha_Used', 'Max_Text_Score']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in master_csv_data:
            writer.writerow(row)

    print(f"\n[TRACE] COMPLETE! Component evaluation finished successfully.")
    print(f"[TRACE] Check {summary_path} for your final results table.")
    print(f"[TRACE] Check {csv_path} for your Master Query Breakdown.")


if __name__ == "__main__":
    run_validation()