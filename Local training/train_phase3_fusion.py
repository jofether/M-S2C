"""
Training Script for M-S2C Phase 3: Stabilization (Gating Awake)
=============================================================
"""
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
import json
import os
import logging
import sys

from ms2c_model import MS2CFusionEngine
from dataset import MS2CTripletDataset

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.join(BASE_DIR, "Seed-and-Mutate", "ms2c-local")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | Phase 3 | %(message)s",
    handlers=[
        logging.FileHandler("logs_phase3.txt", mode='w', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def train_phase3_stabilization():
    logger.info("Initializing M-S2C Engine for Phase 3: Stabilization...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"🚀 Pushing model to: {device.type.upper()}")
    
    model = MS2CFusionEngine()
    
    # Load Phase 2 BEST Brain
    checkpoint_file = "ms2c_phase2_BEST.pt" 
    if os.path.exists(checkpoint_file):
        model.load_state_dict(torch.load(checkpoint_file, map_location="cpu"))
        logger.info(f"✅ Loaded Phase 2 weights from {checkpoint_file}")
    else:
        logger.warning(f"⚠️ {checkpoint_file} not found. Using untrained weights.")
    
    model = model.to(device)
    
    logger.info("-> Freezing CodeBERT and ViT completely...")
    for param in model.codebert.parameters():
        param.requires_grad = False
    for param in model.vit.parameters():
        param.requires_grad = False

    logger.info("-> Waking up ONLY the MLP and Gating Network...")
    for param in model.mlp_projection.parameters():
        param.requires_grad = True
    for param in model.gating_network.parameters():
        param.requires_grad = True

    model.train() 
    optimizer = torch.optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=1e-5) 

    json_file_path = os.path.join(REPO_DIR, "data", "manifests", "spacing.json")
    with open(json_file_path, 'r', encoding='utf-8') as f:
        real_data = json.load(f)
        
    dataset = MS2CTripletDataset(real_data)
    dataloader = DataLoader(dataset, batch_size=4, shuffle=True)

    logger.info(f"Starting Phase 3 Loop on {len(real_data)} samples...")
    margin = 0.5 

    # --- EARLY STOPPING SETUP ---
    best_loss = float('inf')
    patience_counter = 0
    patience_limit = 3
    max_epochs = 50

    for epoch in range(1, max_epochs + 1): 
        total_loss = 0.0
        alpha_tracker = []
        
        for batch_idx, batch in enumerate(dataloader):
            optimizer.zero_grad()

            anchor_ids = batch['anchor_input_ids'].to(device)
            anchor_mask = batch['anchor_attention_mask'].to(device)
            pixel_vals = batch['pixel_values'].to(device)
            
            v_text, v_visual_aligned, alpha = model(
                input_ids=anchor_ids, 
                attention_mask=anchor_mask, 
                pixel_values=pixel_vals
            )
            
            v_anchor = (alpha * v_text) + ((1.0 - alpha) * v_visual_aligned)
            v_anchor = F.normalize(v_anchor, p=2, dim=1)

            with torch.no_grad():
                pos_ids = batch['pos_input_ids'].to(device)
                pos_mask = batch['pos_attention_mask'].to(device)
                neg_ids = batch['neg_input_ids'].to(device)
                neg_mask = batch['neg_attention_mask'].to(device)
                
                pos_outputs = model.codebert(input_ids=pos_ids, attention_mask=pos_mask)
                v_pos = F.normalize(pos_outputs.last_hidden_state[:, 0, :], p=2, dim=1)

                neg_outputs = model.codebert(input_ids=neg_ids, attention_mask=neg_mask)
                v_neg = F.normalize(neg_outputs.last_hidden_state[:, 0, :], p=2, dim=1)

            d_ap = 1.0 - F.cosine_similarity(v_anchor, v_pos, dim=1)
            d_an = 1.0 - F.cosine_similarity(v_anchor, v_neg, dim=1)
            
            losses = F.relu(d_ap - d_an + margin) 
            loss = losses.mean()

            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            alpha_tracker.append(alpha.mean().item())

            if batch_idx % 50 == 0:
                logger.info(f"Epoch {epoch} | Batch {batch_idx}/{len(dataloader)} | Loss: {loss.item():.4f} | Alpha: {alpha.mean().item():.4f}")

        avg_loss = total_loss / len(dataloader)
        avg_alpha = sum(alpha_tracker) / len(alpha_tracker)
        logger.info(f"✅ END OF EPOCH {epoch} | Avg Triplet Loss: {avg_loss:.4f} | Final Alpha Balance: {avg_alpha:.4f}")
        
        # --- EARLY STOPPING LOGIC ---
        if avg_loss < best_loss:
            best_loss = avg_loss
            patience_counter = 0
            torch.save(model.state_dict(), "ms2c_phase3_FINAL.pt")
            logger.info(f"🌟 New best model saved with loss {best_loss:.4f}")
        else:
            patience_counter += 1
            logger.info(f"⚠️ No improvement. Patience: {patience_counter}/{patience_limit}")
            if patience_counter >= patience_limit:
                logger.info("🛑 EARLY STOPPING TRIGGERED! The model has stopped learning.")
                break

if __name__ == "__main__":
    train_phase3_stabilization()