# validate_repository.py
import sys
import os
import json
import csv

# Force Python to look in the exact directory this script is located in
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from bm25 import BM25Retriever
from ms2c import MS2CRetriever


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
    if total == 0: return "No queries evaluated."
    mrr = metrics["mrr_sum"] / total
    acc1 = (metrics["hits_at_1"] / total) * 100
    acc3 = (metrics["hits_at_3"] / total) * 100
    acc5 = (metrics["hits_at_5"] / total) * 100
    acc10 = (metrics["hits_at_10"] / total) * 100
    return f"MRR: {mrr:.4f} | Hit@1: {acc1:.2f}% | Hit@3: {acc3:.2f}% | Hit@5: {acc5:.2f}% | Hit@10: {acc10:.2f}%"


def run_repo_validation():
    # 1. Setup Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    queries_path = os.path.join(base_dir, "validation_repository", "repository.json")
    images_dir = os.path.join(base_dir, "validation_repository", "images")  # Assuming images are here
    model_weights = os.path.join(base_dir, "ms2c_E2E_JOINT_BEST.pt")

    # Organized Results Folders
    results_base = os.path.join(base_dir, "validation_repository_results")
    folders = {
        "bm25": os.path.join(results_base, "bm25_repo_logs"),
        "uni": os.path.join(results_base, "ms2c_unimodal_repo_logs"),
        "multi": os.path.join(results_base, "ms2c_multimodal_repo_logs")
    }
    for folder in folders.values(): ensure_dir(folder)

    # 2. Load Queries and Group by Repository
    print("[TRACE] Loading repository evaluation dataset...")
    with open(queries_path, 'r', encoding='utf-8') as f:
        queries_data = json.load(f)

    # Group queries so we only load a repository into the GPU once
    repo_groups = {}
    for item in queries_data:
        repo_url = item["github_repo"]
        if repo_url not in repo_groups:
            repo_groups[repo_url] = []
        repo_groups[repo_url].append(item)

    # 3. Tracking Variables
    total_queries = len(queries_data)
    global_metrics = {
        "bm25": {"hits_at_1": 0, "hits_at_3": 0, "hits_at_5": 0, "hits_at_10": 0, "mrr_sum": 0.0},
        "uni": {"hits_at_1": 0, "hits_at_3": 0, "hits_at_5": 0, "hits_at_10": 0, "mrr_sum": 0.0},
        "multi": {"hits_at_1": 0, "hits_at_3": 0, "hits_at_5": 0, "hits_at_10": 0, "mrr_sum": 0.0}
    }

    # Tracking Structures for Paper Visualization
    hero_cases = []
    interference_cases = []
    repo_logs = {}

    # --- NEW: Master CSV Logger Data ---
    master_csv_data = []

    # 4. Evaluation Loop (Iterating repo by repo)
    print(f"\n[TRACE] Starting Repository Evaluation ({total_queries} total queries)...\n")

    for repo_url, queries in repo_groups.items():
        repo_name = repo_url.split("/")[-1]
        index_path = os.path.join(results_base, f"indexed_nodes/{repo_name}_indexed_nodes.json")

        if not os.path.exists(index_path):
            print(f"[WARNING] Skipping {repo_name} - Index file {index_path} not found. Did you run repo_indexer.py?")
            total_queries -= len(queries)  # Adjust total if we skip
            continue

        print(f"==================================================")
        print(f"[TRACE] Loading Search Engine for: {repo_name}")
        print(f"==================================================")

        with open(index_path, 'r', encoding='utf-8') as f:
            repo_index = json.load(f)

        # Initialize the scope-aware retrievers
        bm25_retriever = BM25Retriever(repo_index)
        ms2c_retriever = MS2CRetriever(model_weights, repo_index, batch_size=64)

        if repo_name not in repo_logs: repo_logs[repo_name] = []

        for item in queries:
            text_query = item["text_anchor"]
            target_file = item["file_path"]
            target_node = item["positive_node"]
            img_path = os.path.join(images_dir, item["image_anchor"])

            # The target is now a specific node inside a specific file
            target_tuple = (target_file, target_node)

            print(f"  -> Testing Query: {item['image_anchor']}")

            # --- A. BM25 Retrieval (Global Scope) ---
            res_bm25 = bm25_retriever.retrieve_top_k(text_query, k=10, scope="repository")
            rank_bm25 = (res_bm25.index(target_tuple) + 1) if target_tuple in res_bm25 else 0
            global_metrics["bm25"] = calculate_metrics(rank_bm25, total_queries, global_metrics["bm25"])

            # --- B. MS2C Unimodal (Global Scope) ---
            res_uni, _ = ms2c_retriever.retrieve_top_k(text_query, k=10, mode="unimodal", scope="repository")
            rank_uni = (res_uni.index(target_tuple) + 1) if target_tuple in res_uni else 0
            global_metrics["uni"] = calculate_metrics(rank_uni, total_queries, global_metrics["uni"])

            # --- C. MS2C Multimodal (Global Scope) ---
            res_multi, alpha = ms2c_retriever.retrieve_top_k(text_query, image_path=img_path, k=10, mode="multimodal",
                                                             scope="repository")
            rank_multi = (res_multi.index(target_tuple) + 1) if target_tuple in res_multi else 0
            global_metrics["multi"] = calculate_metrics(rank_multi, total_queries, global_metrics["multi"])

            # --- D. Capture Max Text Score for Logger ---
            # We briefly calculate the max text score again just for logging purposes
            import torch
            with torch.no_grad():
                text_inputs = ms2c_retriever.text_tokenizer(text_query, return_tensors="pt", truncation=True,
                                                            padding="max_length", max_length=128).to(
                    ms2c_retriever.device)
                text_emb = ms2c_retriever.model.forward_text(text_inputs["input_ids"], text_inputs["attention_mask"])
                text_sim = torch.matmul(text_emb, ms2c_retriever.global_embeddings.T).squeeze(0)
                max_text_score = text_sim.max().item()

            # -----------------------------------------------------------------
            # VISUALIZATION DATA GATHERING
            # -----------------------------------------------------------------

            # Identify Hero Cases (Multi beat Uni or saved a failure)
            if rank_multi > 0 and (rank_uni == 0 or rank_multi < rank_uni):
                hero_cases.append({
                    "id": item["image_anchor"],
                    "uni_rank": rank_uni if rank_uni > 0 else "Fail",
                    "multi_rank": rank_multi,
                    "alpha": alpha
                })

            # Identify Interference Cases (Uni beat Multi or Multi failed)
            elif rank_uni > 0 and (rank_multi == 0 or rank_uni < rank_multi):
                interference_cases.append({
                    "id": item["image_anchor"],
                    "uni_rank": rank_uni,
                    "multi_rank": rank_multi if rank_multi > 0 else "Fail",
                    "alpha": alpha
                })

            # Accumulate logs
            repo_logs[repo_name].append({
                "query": text_query,
                "target_file": target_file,
                "target_node": target_node,
                "image": item["image_anchor"],
                "bm25": {"rank": rank_bm25, "top10": res_bm25},
                "uni": {"rank": rank_uni, "top10": res_uni},
                "multi": {"rank": rank_multi, "top10": res_multi, "alpha": alpha}
            })

            # Add to Master CSV Data
            master_csv_data.append({
                "Query_ID": item["image_anchor"],
                "BM25_Rank": rank_bm25 if rank_bm25 > 0 else "Fail",
                "Uni_Rank": rank_uni if rank_uni > 0 else "Fail",
                "Multi_Rank": rank_multi if rank_multi > 0 else "Fail",
                "Alpha_Used": f"{alpha:.4f}",
                "Max_Text_Score": f"{max_text_score:.4f}"
            })

    # 5. Generate Logs
    print("\n[TRACE] Writing detailed logs to subdirectories...")
    for r_name, logs in repo_logs.items():
        for m_type in ["bm25", "uni", "multi"]:
            f_path = os.path.join(folders[m_type], f"{r_name}_{m_type.upper()}_repo_logs.txt")
            with open(f_path, 'w', encoding='utf-8') as f:
                f.write(f"=== {m_type.upper()} REPOSITORY RESULTS: {r_name} ===\n\n")
                for l in logs:
                    f.write(f"Image / ID: {l['image']}\n")
                    f.write(f"Query: {l['query']}\n")
                    f.write(f"Target File: {l['target_file']}\n")
                    f.write(f"Target Node: {l['target_node']}\n")
                    f.write(
                        f"Rank Achieved: {l[m_type]['rank'] if l[m_type]['rank'] > 0 else 'FAILED (Not in Top 10)'}\n")
                    if m_type == "multi":
                        a_val = l[m_type]['alpha']
                        tag = "[VISUAL DOMINANT]" if a_val < 0.3 else "[TEXT DOMINANT]" if a_val > 0.7 else "[BALANCED]"
                        f.write(f"Gating Alpha: {a_val:.4f} {tag}\n")
                    f.write("--- Top 10 Retrieved (File -> Node) ---\n")
                    for i, (res_file, res_node) in enumerate(l[m_type]['top10'], 1):
                        marker = "  <--- [GROUND TRUTH HIT]" if (
                                res_file == l['target_file'] and res_node == l['target_node']) else ""
                        f.write(f"{i}. [{res_file}] {res_node}{marker}\n")
                    f.write("\n" + "=" * 70 + "\n\n")

    # 6. Global Summary & Analytical Tables
    summary_path = os.path.join(results_base, "GLOBAL_REPO_BENCHMARK_SUMMARY.txt")
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("GLOBAL REPOSITORY EVALUATION SUMMARY\n")
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

    print(f"\n[TRACE] COMPLETE! Repository evaluation finished successfully.")
    print(f"[TRACE] Check {summary_path} for your final results table.")
    print(f"[TRACE] Check {csv_path} for your Master Query Breakdown.")


if __name__ == "__main__":
    run_repo_validation()