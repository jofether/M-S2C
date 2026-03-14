"""
M-S2C Ablation Study (Unimodal vs. Multimodal Baseline)
=======================================================
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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.join(BASE_DIR)

# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | Ablation Study | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("ablation_study_logs.txt", mode='w', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def run_ablation_study():
    # Force GPU usage
    if not torch.cuda.is_available():
        logger.error("❌ CUDA not available! GPU required for this script.")
        return
    
    device = torch.device("cuda")
    logger.info(f"✅ Using GPU: {torch.cuda.get_device_name(0)}")
    logger.info(f"GPU Memory Available: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB\n")
    
    model = MS2CFusionEngine().to(device)
    model.load_state_dict(torch.load("ms2c_E2E_JOINT_BEST.pt", map_location=device))
    model.eval()
    
    # Enable GPU optimizations
    torch.cuda.synchronize()
    torch.backends.cudnn.benchmark = True

    tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
    image_processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224-in21k")

    index = faiss.read_index("ms2c_codebase.index")
    with open("node_mapping.json", "r", encoding='utf-8') as f:
        node_mapping = json.load(f)

    # ⚠️ FIXED: Using mutated_dataset_25k.json for consistency with training
    json_file_path = os.path.join(REPO_DIR, "mutated_dataset_25k.json")
    with open(json_file_path, 'r', encoding='utf-8') as f:
        test_set = json.load(f)[:1000]
    
    logger.info(f"📊 Using training dataset: {json_file_path} (1000 samples)")
    screenshot_base = os.path.join(REPO_DIR, "03_screenshots") 

    logger.info("🚀 RUNNING ABLATION STUDY: MULTIMODAL VS UNIMODAL (TEXT-ONLY)")
    metrics = {"multimodal": {"rr": []}, "unimodal": {"rr": []}}

    for i, sample in enumerate(test_set):
        query_text = sample['text_anchor']
        image_path = os.path.normpath(os.path.join(screenshot_base, sample['image_anchor']))
        ground_truth = sample['positive_node'].strip()

        text_enc = tokenizer(query_text, padding='max_length', truncation=True, max_length=512, return_tensors="pt").to(device)
        try:
            image = Image.open(image_path).convert("RGB")
            pixel_values = image_processor(images=image, return_tensors="pt").pixel_values.to(device)
        except Exception:
            continue

        with torch.no_grad():
            v_visual_aligned, v_text, alpha = model(
                input_ids=text_enc.input_ids, attention_mask=text_enc.attention_mask, pixel_values=pixel_values
            )
            
            # 1. MULTIMODAL PASS
            v_multi = (alpha * v_text) + ((1.0 - alpha) * v_visual_aligned)
            v_multi = F.normalize(v_multi, p=2, dim=1)
            
            # 2. UNIMODAL PASS (Force Alpha = 1.0)
            v_uni = v_text 
            v_uni = F.normalize(v_uni, p=2, dim=1)

        for mode, vector in [("multimodal", v_multi), ("unimodal", v_uni)]:
            scores, indices = index.search(vector.cpu().numpy(), 10)
            target_rank = 0
            for rank, node_id in enumerate(indices[0]):
                # Bulletproof comparison: remove ALL whitespace variations
                if "".join(node_mapping[str(node_id)]['code'].split()) == "".join(ground_truth.split()):
                    target_rank = rank + 1
                    break
            metrics[mode]["rr"].append(1.0 / target_rank if target_rank > 0 else 0.0)
        
        # Clear GPU cache periodically
        if (i + 1) % 10 == 0:
            torch.cuda.empty_cache()
            torch.cuda.synchronize()

    mrr_multi = sum(metrics["multimodal"]["rr"]) / len(test_set)
    mrr_uni = sum(metrics["unimodal"]["rr"]) / len(test_set)
    diagnostic_gain = mrr_multi - mrr_uni

    logger.info("\n" + "="*50)
    logger.info("🔬 ABLATION STUDY RESULTS (Diagnostic Gain) 🔬")
    logger.info("="*50)
    logger.info(f"Unimodal MRR (Text Only):   {mrr_uni:.4f}")
    logger.info(f"Multimodal MRR (M-S2C):     {mrr_multi:.4f}")
    logger.info("-" * 50)
    logger.info(f"⭐ DIAGNOSTIC GAIN (ΔMRR):  +{diagnostic_gain:.4f}")
    logger.info("="*50)
    
    # Cleanup GPU memory
    torch.cuda.empty_cache()
    torch.cuda.synchronize()
    logger.info("✅ GPU memory cleaned up.")

if __name__ == "__main__":
    run_ablation_study()