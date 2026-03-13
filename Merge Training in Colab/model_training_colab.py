"""
M-S2C END-TO-END JOINT TRAINING
================================
Dual-Stream Triplet Loss Architecture:
- Visual Stream: Image Anchor → Positive/Negative Code Nodes
- Textual Stream: Text Anchor → Positive/Negative Code Nodes
- Combined Loss: 0.7 * Loss_visual + 0.3 * Loss_textual
- Margin: 0.5, Distance: Cosine Distance, All L2-normalized

Multimodal Gap Focus: Priority on visual alignment
Optimized for NVIDIA A100 with gradient accumulation (steps=4)
"""
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
import json
import os
from pathlib import Path
import logging
import sys

from ms2c_model import MS2CFusionEngine
from dataset import MS2CTripletDataset

BASE_DIR = Path(__file__).resolve().parent
REPO_DIR = BASE_DIR  # Points to workspace root (Merge Training in Colab)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | E2E Joint | %(message)s",
    handlers=[
        logging.FileHandler("logs_e2e_joint_training.txt", mode='w', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


# ==================== DUAL-STREAM TRIPLET LOSS ====================
def compute_dual_stream_triplet_loss(v_visual_anchor, v_text_anchor, v_pos, v_neg, margin=0.5):
    """
    Dual-Stream Triplet Loss:
    - Visual Stream: image anchor vs pos/neg
    - Textual Stream: text anchor vs pos/neg
    
    Returns: (loss_visual, loss_textual, combined_loss)
    """
    # Visual stream loss
    d_visual_ap = 1.0 - F.cosine_similarity(v_visual_anchor, v_pos, dim=1)
    d_visual_an = 1.0 - F.cosine_similarity(v_visual_anchor, v_neg, dim=1)
    losses_visual = F.relu(d_visual_ap - d_visual_an + margin)
    loss_visual = losses_visual.mean()
    
    # Textual stream loss
    d_text_ap = 1.0 - F.cosine_similarity(v_text_anchor, v_pos, dim=1)
    d_text_an = 1.0 - F.cosine_similarity(v_text_anchor, v_neg, dim=1)
    losses_text = F.relu(d_text_ap - d_text_an + margin)
    loss_text = losses_text.mean()
    
    # Weighted combined loss (0.7 visual priority + 0.3 textual grounding)
    combined_loss = (0.7 * loss_visual) + (0.3 * loss_text)
    
    return loss_visual, loss_text, combined_loss


# ==================== JOINT TRAINING LOOP ====================
def run_joint_training(model, dataloader, optimizers, epochs, accumulation_steps, device):
    """
    E2E Joint Training with Dual-Stream Triplet Loss
    
    Args:
        optimizers: dict with keys 'codebert', 'vit', 'projection', 'gating'
    """
    logger.info(f"\n{'='*70}")
    logger.info("Starting E2E JOINT TRAINING - Dual-Stream Triplet Loss")
    logger.info(f"{'='*70}\n")
    
    best_combined_loss = float('inf')
    patience_counter = 0
    patience_limit = 3
    margin = 1
    
    for epoch in range(1, epochs + 1):
        total_loss_visual = 0.0
        total_loss_text = 0.0
        total_loss_combined = 0.0
        alpha_tracker = []
        
        # Zero gradients at epoch start
        for opt in optimizers.values():
            opt.zero_grad()
        
        for batch_idx, batch in enumerate(dataloader):
            # --- Load batch to device ---
            image_anchor = batch['pixel_values'].to(device)
            text_anchor_ids = batch['anchor_input_ids'].to(device)
            text_anchor_mask = batch['anchor_attention_mask'].to(device)
            pos_ids = batch['pos_input_ids'].to(device)
            pos_mask = batch['pos_attention_mask'].to(device)
            neg_ids = batch['neg_input_ids'].to(device)
            neg_mask = batch['neg_attention_mask'].to(device)
            
            # --- Forward pass: get all embeddings ---
            # Visual branch: image → visual embedding
            v_visual_aligned, _, _ = model(
                input_ids=None,
                attention_mask=None,
                pixel_values=image_anchor
            )
            v_visual_anchor = F.normalize(v_visual_aligned, p=2, dim=1)
            
            # Textual branch: text → text embedding
            _, v_text, _ = model(
                input_ids=text_anchor_ids,
                attention_mask=text_anchor_mask,
                pixel_values=None
            )
            v_text_anchor = F.normalize(v_text, p=2, dim=1)
            
            # Get alpha from gating network (via full forward pass)
            _, _, alpha = model(
                input_ids=text_anchor_ids,
                attention_mask=text_anchor_mask,
                pixel_values=image_anchor
            )
            alpha_tracker.append(alpha.mean().item())
            
            # Positive/Negative code nodes (frozen, only pass through CodeBERT)
            with torch.no_grad():
                pos_outputs = model.codebert(input_ids=pos_ids, attention_mask=pos_mask)
                v_pos = F.normalize(pos_outputs.last_hidden_state[:, 0, :], p=2, dim=1)
                
                neg_outputs = model.codebert(input_ids=neg_ids, attention_mask=neg_mask)
                v_neg = F.normalize(neg_outputs.last_hidden_state[:, 0, :], p=2, dim=1)
            
            # --- Compute dual-stream triplet loss ---
            loss_visual, loss_text, loss_combined = compute_dual_stream_triplet_loss(
                v_visual_anchor, v_text_anchor, v_pos, v_neg, margin
            )
            
            # Scale for gradient accumulation
            loss = loss_combined / accumulation_steps
            loss.backward()
            
            # Optimizer step every accumulation_steps or at end of epoch
            if (batch_idx + 1) % accumulation_steps == 0 or (batch_idx + 1 == len(dataloader)):
                for opt in optimizers.values():
                    opt.step()
                for opt in optimizers.values():
                    opt.zero_grad()
            
            # Track unscaled losses
            total_loss_visual += loss_visual.item()
            total_loss_text += loss_text.item()
            total_loss_combined += loss_combined.item()
            
            # Logging every 50 batches
            if batch_idx % 50 == 0:
                logger.info(
                    f"Epoch {epoch} | Batch {batch_idx}/{len(dataloader)} | "
                    f"Loss_visual: {loss_visual.item():.4f} | "
                    f"Loss_textual: {loss_text.item():.4f} | "
                    f"Combined: {loss_combined.item():.4f} | "
                    f"Alpha: {alpha.mean().item():.4f}"
                )
        
        # --- Epoch summary ---
        avg_loss_visual = total_loss_visual / len(dataloader)
        avg_loss_text = total_loss_text / len(dataloader)
        avg_loss_combined = total_loss_combined / len(dataloader)
        avg_alpha = sum(alpha_tracker) / len(alpha_tracker)
        
        logger.info(
            f"\n✅ EPOCH {epoch} SUMMARY:\n"
            f"  Avg Loss_visual: {avg_loss_visual:.4f}\n"
            f"  Avg Loss_textual: {avg_loss_text:.4f}\n"
            f"  Avg Combined Loss: {avg_loss_combined:.4f}\n"
            f"  Avg Alpha Balance: {avg_alpha:.4f}\n"
        )
        
        # --- Early stopping on combined loss ---
        if avg_loss_combined < best_combined_loss:
            best_combined_loss = avg_loss_combined
            patience_counter = 0
            torch.save(model.state_dict(), "ms2c_E2E_JOINT_BEST.pt")
            logger.info(f"🌟 New best model saved! Combined Loss: {best_combined_loss:.4f}\n")
        else:
            patience_counter += 1
            logger.info(f"⚠️ No improvement. Patience: {patience_counter}/{patience_limit}\n")
            if patience_counter >= patience_limit:
                logger.info("🛑 EARLY STOPPING TRIGGERED!")
                break




# ==================== OPTIMIZER SETUP ====================
def setup_optimizers(model):
    """
    Differential learning rates for joint training:
    - CodeBERT: 2e-6 (prevent catastrophic forgetting)
    - ViT: 2e-5 (standard fine-tuning)
    - MLP & Gating: 5e-5 (aggressive learning)
    
    Returns: dict of AdamW optimizers
    """
    optimizers = {
        'codebert': torch.optim.AdamW(model.codebert.parameters(), lr=2e-6, weight_decay=0.01),
        'vit': torch.optim.AdamW(model.vit.parameters(), lr=2e-5, weight_decay=0.01),
        'projection': torch.optim.AdamW(model.mlp_projection.parameters(), lr=5e-5, weight_decay=0.01),
        'gating': torch.optim.AdamW(model.gating_network.parameters(), lr=5e-5, weight_decay=0.01),
    }
    return optimizers


# ==================== MAIN JOINT TRAINING ====================
def main():
    """E2E Joint Training Entry Point"""
    logger.info("🚀 M-S2C E2E JOINT TRAINING - Starting...")
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Device: {device.type.upper()}\n")
    
    # --- Load dataset ---
    json_file_path = REPO_DIR / "mutated_dataset_25k.json"
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            real_data = json.load(f)
        logger.info(f"✅ Loaded dataset with {len(real_data)} samples")
        logger.info(f"📁 Dataset: {json_file_path}\n")
    except FileNotFoundError:
        logger.error(f"❌ Could not find {json_file_path}")
        logger.error(f"Expected location: {json_file_path}")
        return
    
    # --- Initialize model ---
    model = MS2CFusionEngine().to(device)
    
    # --- Load Phase 1 weights if available ---
    if os.path.exists("ms2c_phase1_BEST.pt"):
        try:
            model.load_state_dict(torch.load("ms2c_phase1_BEST.pt", map_location=device))
            logger.info("✅ Loaded Phase 1 pre-training weights\n")
        except Exception as e:
            logger.warning(f"⚠️ Could not load Phase 1 weights: {e}. Using fresh weights.\n")
    else:
        logger.info("⚠️ No Phase 1 checkpoint found. Starting from scratch.\n")
    
    # --- Setup differential optimizers ---
    optimizers = setup_optimizers(model)
    logger.info("✅ Optimizers configured with differential learning rates:\n"
                "  CodeBERT: 2e-6 | ViT: 2e-5 | MLP: 5e-5 | Gating: 5e-5\n")
    
    # --- Prepare dataloader ---
    dataset = MS2CTripletDataset(real_data)
    dataloader = DataLoader(dataset, batch_size=4, shuffle=True)
    logger.info(f"✅ Dataloader ready: {len(dataloader)} batches (size=4)\n")
    
    # --- Set model to train mode ---
    model.train()
    
    # --- Run joint training ---
    run_joint_training(
        model, dataloader, optimizers,
        epochs=50,
        accumulation_steps=4,
        device=device
    )
    
    # --- Final checkpoint and summary ---
    torch.save(model.state_dict(), "ms2c_E2E_JOINT_FINAL.pt")
    logger.info("\n" + "="*70)
    logger.info("🎉 E2E JOINT TRAINING COMPLETED!")
    logger.info("="*70)
    logger.info("Checkpoints saved:")
    logger.info("  - ms2c_E2E_JOINT_BEST.pt (best combined loss)")
    logger.info("  - ms2c_E2E_JOINT_FINAL.pt (final state)")
    logger.info("\nTraining Architecture:")
    logger.info("  Loss Function: Dual-Stream Triplet Loss")
    logger.info("  Visual Priority: 0.7 | Textual Grounding: 0.3")
    logger.info("  Margin: 0.5 | Distance Metric: Cosine Distance")
    logger.info("  All embeddings L2-normalized")



if __name__ == "__main__":
    main()
