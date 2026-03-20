# ms2c.py
import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer, ViTModel, ViTImageProcessor
from PIL import Image

"""
=========================================================================================
Multimodal Semantic-to-Code (MS2C) Engine - Global Repository Scope
=========================================================================================
This module contains the core neural network architecture for bug localization.
It defines the late-fusion mechanism combining CodeBERT (Text/Code) and Vision 
Transformer (Image) embeddings via a dynamically learned gating network.

The retriever in this file is strictly designed for Repository-Level searches 
(evaluating thousands of nodes across an entire system).
=========================================================================================
"""


class MS2CModel(nn.Module):
    """
    The PyTorch neural network model defining the MS2C architecture.
    It encapsulates the unimodal encoders (CodeBERT and ViT) and the gating network
    used to calculate the dynamic fusion weight (alpha).
    """

    def __init__(self, hidden_dim=768):
        super(MS2CModel, self).__init__()

        # 1. Unimodal Encoders
        self.codebert = AutoModel.from_pretrained("microsoft/codebert-base")
        self.vit = ViTModel.from_pretrained("google/vit-base-patch16-224-in21k")

        # 2. Vision Projection Head
        # Projects the ViT output to match the hidden dimensionality of CodeBERT
        self.mlp_projection = nn.Sequential(
            nn.Linear(self.vit.config.hidden_size, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )

        # 3. Gating Network (Late Fusion Router)
        # Learns to predict the reliability (alpha) of the text modality vs vision modality
        self.gating_network = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()  # Outputs a value between 0.0 and 1.0
        )

    def forward_text(self, input_ids, attention_mask):
        """Generates L2-normalized embeddings for Code/Text sequences."""
        outputs = self.codebert(input_ids=input_ids, attention_mask=attention_mask)
        cls_embedding = outputs.last_hidden_state[:, 0, :]
        return F.normalize(cls_embedding, p=2, dim=1)

    def forward_image(self, pixel_values):
        """Generates L2-normalized embeddings for UI screenshots."""
        outputs = self.vit(pixel_values=pixel_values)
        cls_embedding = outputs.last_hidden_state[:, 0, :]
        projected_embedding = self.mlp_projection(cls_embedding)
        return F.normalize(projected_embedding, p=2, dim=1)

    def compute_gating_weight(self, text_emb, visual_emb):
        """Concatenates the multimodal embeddings to predict the alpha fusion weight."""
        fused_features = torch.cat([text_emb, visual_emb], dim=1)
        return self.gating_network(fused_features)


class MS2CRetriever:
    """
    The Global Repository pipeline. Manages data ingestion, AST node encoding,
    and Top-K similarity calculations across the entire software repository.
    """

    def __init__(self, model_path, index_dict, batch_size=64):
        print("\n[TRACE] --- Initializing MS2C Repository Retriever ---")
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")

        self.model = MS2CModel().to(self.device)
        if os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path, map_location=self.device, weights_only=True))
            print("[TRACE] Weights loaded successfully.")

        self.model.eval()
        self.text_tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
        self.image_processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224-in21k")

        self.global_corpus = []  # List of (file_path, ast_node_string)
        self.global_embeddings = None  # Nx768 Tensor of pre-computed embeddings

        self._flatten_and_encode(index_dict, batch_size)

    def _flatten_and_encode(self, index_dict, batch_size):
        """Flattens the repository index and batch-encodes all AST nodes."""
        print("[TRACE] Flattening index and batch-encoding repository nodes...")

        for key, nodes in index_dict.items():
            for node in nodes:
                self.global_corpus.append((key, node))

        total_nodes = len(self.global_corpus)
        print(f"[TRACE] Global Repository Search Space: {total_nodes} nodes.")

        all_embeddings = []
        with torch.no_grad():
            for i in range(0, total_nodes, batch_size):
                batch_tuples = self.global_corpus[i: i + batch_size]

                # Context Injection: Includes the file path to aid global localization
                batch_texts = [f"[{item[0]}] {item[1]}" for item in batch_tuples]

                inputs = self.text_tokenizer(batch_texts, return_tensors="pt", truncation=True, padding="max_length",
                                             max_length=128).to(self.device)
                embeddings = self.model.forward_text(inputs["input_ids"], inputs["attention_mask"])
                all_embeddings.append(embeddings.cpu())

        if all_embeddings:
            self.global_embeddings = torch.cat(all_embeddings, dim=0).to(self.device)
            print("[TRACE] Repository Batch Encoding complete.")
        else:
            print("[WARNING] No nodes found to encode!")

    def retrieve_top_k(self, text_query, image_path=None, k=10, mode="multimodal"):
        """Executes Multimodal retrieval across the entire repository."""
        if self.global_embeddings is None or len(self.global_corpus) == 0:
            return [], 0.0

        # Global scope: Look at ALL nodes containing className
        valid_indices = [i for i, item in enumerate(self.global_corpus) if "className" in item[1]]

        if not valid_indices:
            return [], 0.0

        with torch.no_grad():
            text_inputs = self.text_tokenizer(text_query, return_tensors="pt", truncation=True, padding="max_length",
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

                base_alpha = self.model.compute_gating_weight(text_emb, vis_emb).squeeze()

                # Node-Level Confidence Bypassing (Strict threshold for large search spaces)
                text_threshold = 0.90
                alpha_vector = torch.where(text_sim > text_threshold, torch.tensor(0.95, device=self.device),
                                           base_alpha)
                alpha_val = alpha_vector.mean().item()

                final_scores = (alpha_vector * text_sim) + ((1.0 - alpha_vector) * vis_sim)

            if final_scores.dim() > 1:
                final_scores = final_scores.squeeze()

            filtered_scores = final_scores[valid_indices]
            top_k_val = min(k, len(valid_indices))
            top_k_res = torch.topk(filtered_scores, top_k_val)

            top_k_indices = [valid_indices[idx] for idx in top_k_res.indices.tolist()]
            raw_results = [self.global_corpus[i] for i in top_k_indices]

            return raw_results, alpha_val