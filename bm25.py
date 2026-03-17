# bm25.py
import os
import json
import re
from rank_bm25 import BM25Okapi


def tokenize(text):
    """
    Tokenization breaks down strings into words. We use a regex split to
    separate Tailwind CSS classes and JSX syntax cleanly (e.g., matching 'mb-[-50px]').
    """
    text = text.lower()
    tokens = re.split(r'[\s\'"=\[\]{}()<>]+', text)
    return [t for t in tokens if t]


class BM25Retriever:
    """
    Scope-Aware Okapi BM25 Lexical Baseline.
    Supports local (component) and global (repository) search scopes.
    """

    def __init__(self, index_dict):
        print("\n[TRACE] --- Initializing Scope-Aware BM25 Lexical Search ---")
        self.index_dict = index_dict

        # 1. COMPONENT-LEVEL INDEXES (Local Scope)
        self.bm25_indexes = {}
        for comp_name, nodes in index_dict.items():
            tokenized_corpus = [tokenize(node) for node in nodes]
            if tokenized_corpus:
                self.bm25_indexes[comp_name] = BM25Okapi(tokenized_corpus)

        # 2. REPOSITORY-LEVEL INDEX (Global Scope)
        self.global_corpus = []
        tokenized_global_corpus = []

        for key, nodes in index_dict.items():
            for node in nodes:
                # Store the tuple (file_path, node) for repo-level retrieval
                self.global_corpus.append((key, node))
                tokenized_global_corpus.append(tokenize(node))

        if tokenized_global_corpus:
            self.global_bm25 = BM25Okapi(tokenized_global_corpus)
        else:
            self.global_bm25 = None

        print(
            f"[TRACE] Built {len(self.bm25_indexes)} local indexes and 1 global index ({len(self.global_corpus)} total nodes).")

    def retrieve_top_k(self, query, target_key=None, k=10, scope="component"):
        """
        Scope-Aware Retrieval:
        - scope="component": target_key is 'comp_name'. Returns [node1, node2, ...]
        - scope="repository": target_key is ignored. Returns [(file_path, node), ...]
        """
        tokenized_query = tokenize(query)

        if scope == "component":
            # --- LOCAL SEARCH ---
            if target_key not in self.bm25_indexes:
                print(f"[WARNING] Component '{target_key}' not found in BM25 index.")
                return []

            bm25_engine = self.bm25_indexes[target_key]
            component_nodes = self.index_dict[target_key]

            return bm25_engine.get_top_n(tokenized_query, component_nodes, n=k)

        elif scope == "repository":
            # --- GLOBAL SEARCH ---
            if not self.global_bm25 or not self.global_corpus:
                return []

            # Get IDF scores against the entire repository
            scores = self.global_bm25.get_scores(tokenized_query)

            # Pair scores with their corresponding (file_path, node) tuples
            scored_corpus = list(zip(scores, self.global_corpus))

            # Sort by score in descending order
            scored_corpus.sort(key=lambda x: x[0], reverse=True)

            # Extract just the (file_path, node) tuples for the Top-K
            top_k_results = [item[1] for item in scored_corpus[:k]]

            return top_k_results


# Backward compatibility for validate_component.py
BM25ComponentRetriever = BM25Retriever

# ==========================================
# QUICK TEST BLOCK
# ==========================================
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "validation_component_results", "indexed_nodes.json")

    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            corpus_dict = json.load(f)

        retriever = BM25Retriever(corpus_dict)
        test_query = "The oversized inner buffer needs a fix."

        # Test Local
        print("\n--- LOCAL TEST ---")
        res_local = retriever.retrieve_top_k(test_query, target_key="ExperienceCard", k=3, scope="component")
        for i, res in enumerate(res_local, 1): print(f"{i}. {res}")

        # Test Global
        print("\n--- GLOBAL TEST ---")
        res_global = retriever.retrieve_top_k(test_query, k=3, scope="repository")
        for i, res in enumerate(res_global, 1): print(f"{i}. {res[0]} -> {res[1]}")
