# ms2c_component.py
import os
import re
import torch
from transformers import AutoTokenizer, ViTImageProcessor
from PIL import Image

# Import the base neural network architecture from the core file
from ms2c import MS2CModel

"""
=========================================================================================
MS2C Engine - Local Component Scope (Validation & Testing)
=========================================================================================
This module is utilized for component-level validation with Semantic Enrichment.
It applies Runtime Document Expansion to nodes and queries to bridge the gap 
between abstract Tailwind syntax and human visual bug reports.
=========================================================================================
"""


class MS2CComponentRetriever:
    def __init__(self, model_path, index_dict, batch_size=64):
        print("\n[TRACE] --- Initializing MS2C Component Retriever ---")
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")

        self.model = MS2CModel().to(self.device)
        if os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path, map_location=self.device, weights_only=True))

        self.model.eval()
        self.text_tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
        self.image_processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224-in21k")

        # Regex Patterns for "Smart Filter" classification
        self.patterns = {
            "[Feature: Layering]": r'\b(?:z-(?:\d+|\[-?\d+\])|relative|absolute|fixed|sticky)\b',
            "[Feature: Layout]": r'\b(?:flex|inline-flex|grid|block|flex-row|flex-col|items-|justify-|content-|gap-|grid-cols-|grid-rows-|col-span-|row-span-)\b',
            "[Feature: Spacing]": r'\b(?:p|px|py|pt|pb|pl|pr|ps|pe|m|mx|my|mt|mb|ml|mr|ms|me)-(?!auto)(\d+)\b',
            "[Feature: Typo]": r'\b(?:text-|font-|uppercase|lowercase|capitalize|normal-case)\b',
            "[Feature: Visibility]": r'\b(?:opacity-|visible|invisible|hidden|contents)\b'
        }

        self.global_corpus = []
        self.global_embeddings = None

        self._flatten_and_encode(index_dict, batch_size)

    def enrich_semantics(self, text, is_query=False):
        """
        Runtime Semantic Enrichment Engine.
        Appends Role and Feature tags to nodes and queries to create a similarity spike.
        """
        tags = []
        text_lower = text.lower()

        if not is_query:
            # 1. Role Identification (Structural)
            if any(tag in text_lower for tag in ["<div", "<section", "<nav", "<main", "<header", "<footer"]):
                tags.append("[Role: Container]")
            elif any(tag in text_lower for tag in ["<button", "<a "]):
                tags.append("[Role: Interactive]")
            elif any(tag in text_lower for tag in ["<p", "<span", "<h1", "<h2", "<h3", "<h4", "<h5", "<h6"]):
                tags.append("[Role: Content]")
            elif any(tag in text_lower for tag in ["<input", "<textarea", "<select"]):
                tags.append("[Role: Input]")

            # 2. Feature Classification (Regex Smart Filter)
            for label, pattern in self.patterns.items():
                if re.search(pattern, text):
                    tags.append(label)
        else:
            # 3. Query-Side Bridge (Synonym Mapping)
            # This maps human words to the same tags we put on the code
            if any(w in text_lower for w in ["overlap", "stacking", "depth", "behind", "front", "z-index", "layer"]):
                tags.append("[Feature: Layering]")
            if any(w in text_lower for w in ["spacing", "margin", "padding", "gap", "squished", "pushed", "offset"]):
                tags.append("[Feature: Spacing]")
            if any(w in text_lower for w in ["hidden", "missing", "invisible", "transparency", "opacity", "gone"]):
                tags.append("[Feature: Visibility]")
            if any(w in text_lower for w in ["layout", "column", "row", "align", "flex", "grid", "center", "position"]):
                tags.append("[Feature: Layout]")
            if any(w in text_lower for w in ["text", "font", "bold", "typography", "heading", "size", "capital"]):
                tags.append("[Feature: Typo]")

        if tags:
            return f"{text} | TAGS: {' '.join(tags)}"
        return text

    def _flatten_and_encode(self, index_dict, batch_size):
        """Encodes nodes with Runtime Semantic Enrichment."""
        print("[TRACE] Batch-encoding localized component nodes with Enrichment...")

        for key, nodes in index_dict.items():
            for node in nodes:
                self.global_corpus.append((key, node))

        total_nodes = len(self.global_corpus)

        all_embeddings = []
        with torch.no_grad():
            for i in range(0, total_nodes, batch_size):
                batch_tuples = self.global_corpus[i: i + batch_size]

                # Apply Semantic Enrichment to every node before tokenization
                batch_texts = [self.enrich_semantics(item[1]) for item in batch_tuples]

                inputs = self.text_tokenizer(batch_texts, return_tensors="pt", truncation=True, padding="max_length",
                                             max_length=128).to(self.device)
                embeddings = self.model.forward_text(inputs["input_ids"], inputs["attention_mask"])
                all_embeddings.append(embeddings.cpu())

        if all_embeddings:
            self.global_embeddings = torch.cat(all_embeddings, dim=0).to(self.device)
        else:
            print("[WARNING] No nodes found to encode!")

    def retrieve_top_k(self, text_query, target_key, image_path=None, k=10, mode="multimodal"):
        """
        Executes localized retrieval with Semantic Enrichment and Asymmetric Gating.
        """
        if self.global_embeddings is None or len(self.global_corpus) == 0:
            return [], 0.0

        # Noise Reduction Pruning
        invalid_markers = ["<svg", "<path", "<g ", "<circle", "<rect", "<line", "<polygon"]

        valid_indices = [
            i for i, item in enumerate(self.global_corpus)
            if item[0] == target_key
               and "className" in item[1]
               and not any(marker in item[1] for marker in invalid_markers)
        ]

        if not valid_indices:
            return [], 0.0

        # Enrich the Query to match the Corpus tags
        enriched_query = self.enrich_semantics(text_query, is_query=True)

        with torch.no_grad():
            text_inputs = self.text_tokenizer(enriched_query, return_tensors="pt", truncation=True,
                                              padding="max_length",
                                              max_length=128).to(self.device)
            text_emb = self.model.forward_text(text_inputs["input_ids"], text_inputs["attention_mask"])
            text_sim = torch.matmul(text_emb, self.global_embeddings.T).squeeze(0)

            if mode == "unimodal" or image_path is None:
                final_scores = text_sim
                alpha_val = 1.0
            else:
                image = Image.open(image_path).convert("RGB")
                img_inputs = self.image_processor(images=image, return_tensors="pt").to(self.device)
                vis_emb = self.model.forward_image(img_inputs["pixel_values"])
                vis_sim = torch.matmul(vis_emb, self.global_embeddings.T).squeeze(0)

                # ASYMMETRIC GATING: Protect Text from Vision noise
                base_alpha = self.model.compute_gating_weight(text_emb, vis_emb).squeeze()
                biased_alpha = torch.clamp(base_alpha + 0.20, min=0.70, max=0.95)

                # Confidence Bypass
                text_threshold = 0.80
                alpha_vector = torch.where(text_sim > text_threshold, torch.tensor(0.95, device=self.device),
                                           biased_alpha)
                alpha_val = alpha_vector.mean().item()

                # Late Fusion on Raw Scores
                final_scores = (alpha_vector * text_sim) + ((1.0 - alpha_vector) * vis_sim)

            if final_scores.dim() > 1:
                final_scores = final_scores.squeeze()

            filtered_scores = final_scores[valid_indices]
            top_k_val = min(k, len(valid_indices))
            top_k_res = torch.topk(filtered_scores, top_k_val)

            top_k_indices = [valid_indices[idx] for idx in top_k_res.indices.tolist()]
            raw_results = [self.global_corpus[i][1] for i in top_k_indices]

            return raw_results, alpha_val