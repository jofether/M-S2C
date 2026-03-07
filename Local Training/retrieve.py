import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, ViTImageProcessor
from PIL import Image
import faiss
import json
import os

from ms2c_model import MS2CFusionEngine

# --- EXPLICIT PATH RESOLVER ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.join(BASE_DIR, "Seed-and-Mutate", "ms2c-local")

def simulate_bug_localization(k=3):
    print("1. Booting up M-S2C Diagnosis Engine...")
    model = MS2CFusionEngine()
    model.eval() # Strictly evaluation mode for inference

    tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
    image_processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224-in21k")

    # 2. Load the FAISS Index and Mapping
    print("2. Connecting to FAISS Vector Database...")
    index = faiss.read_index("ms2c_codebase.index")
    with open("node_mapping.json", "r") as f:
        node_mapping = json.load(f)

    # 3. Simulate a User Query (We will pull the first sample from your dataset to guarantee the files exist)
    json_file_path = os.path.join(REPO_DIR, "data", "manifests", "spacing.json")
    with open(json_file_path, 'r', encoding='utf-8') as f:
        real_data = json.load(f)
        
    query_sample = real_data[0] 
    query_text = query_sample['text_anchor']
    image_path = os.path.join(REPO_DIR, "data", "screenshots", query_sample['image_anchor'])

    print(f"\n--- USER BUG REPORT ---")
    print(f"Text: '{query_text}'")
    print(f"Image: Loaded from {os.path.basename(image_path)}")
    print(f"-----------------------\n")

    # 4. Process Inputs
    # Text
    text_enc = tokenizer(query_text, padding='max_length', truncation=True, max_length=128, return_tensors="pt")
    # Image
    image = Image.open(image_path).convert("RGB")
    pixel_values = image_processor(images=image, return_tensors="pt").pixel_values

    # 5. Generate Multimodal Anchor Embedding
    print("3. Fusing Modalities and calculating Alpha...")
    with torch.no_grad():
        v_text, v_visual_aligned, alpha = model(
            input_ids=text_enc.input_ids, 
            attention_mask=text_enc.attention_mask, 
            pixel_values=pixel_values
        )
        
        # S_final Aggregation Strategy (Adaptive Gating)
        v_anchor = (alpha * v_text) + ((1.0 - alpha) * v_visual_aligned)
        v_anchor = F.normalize(v_anchor, p=2, dim=1)

    print(f"   -> Calculated Alpha Weight: {alpha.item():.4f}")

    # 6. FAISS Top-K Search
    print(f"\n4. Searching 100-node Knowledge Base for Top-{k} Matches...")
    # FAISS requires a numpy array
    query_vector = v_anchor.numpy() 
    
    # The search returns the inner product scores (distances) and the DB IDs (indices)
    scores, indices = index.search(query_vector, k)

    print("\n✅ TOP-K RETRIEVAL RESULTS:")
    for rank, (score, node_id) in enumerate(zip(scores[0], indices[0])):
        # Convert FAISS string ID back to actual ID
        retrieved_code = node_mapping[str(node_id)] 
        print(f"Rank {rank + 1} (Score: {score:.4f})")
        print(f"Code Snippet: {retrieved_code[:100]}... [TRUNCATED]")
        print("-" * 50)

if __name__ == "__main__":
    simulate_bug_localization(k=3)