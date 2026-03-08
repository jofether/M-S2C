"""
M-S2C Phase 1: Textual Pre-training (CodeBERT Awake)
====================================================
In this phase, we freeze the Vision Encoder (ViT), the MLP, and the Gating Network.
We wake up CodeBERT and apply an Alpha Override of 1.0 to force the model to 
learn purely from the textual Bug Report and AST source code using Triplet Loss.
Includes GPU acceleration for significantly faster training.
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

# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | Phase 1 | %(message)s",
    handlers=[
        logging.FileHandler("logs_phase1.txt", mode='a', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def train_phase1_text():
    logger.info("Initializing M-S2C Engine for Phase 1: Textual Pre-training...")
    
    # --- GPU SETUP ---
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"🚀 Pushing model to: {device.type.upper()}")
    
    model = MS2CFusionEngine()
    model = model.to(device)

    # --- PHASE 1 FREEZING LOGIC ---
    logger.info("-> Waking up CodeBERT...")
    for param in model.codebert.parameters():
        param.requires_grad = True
        
    logger.info("-> Freezing ViT, MLP, and Gating Network...")
    for param in model.vit.parameters():
        param.requires_grad = False
    for param in model.mlp_projection.parameters():
        param.requires_grad = False
    for param in model.gating_network.parameters():
        param.requires_grad = False

    model.train() 
    optimizer = torch.optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=2e-5) 

    json_file_path = os.path.join(REPO_DIR, "data", "manifests", "spacing.json")
    with open(json_file_path, 'r', encoding='utf-8') as f:
        real_data = json.load(f)
        
    dataset = MS2CTripletDataset(real_data)
    dataloader = DataLoader(dataset, batch_size=4, shuffle=True)

    logger.info(f"Starting Phase 1 Loop on {len(real_data)} samples...")
    margin = 0.5 

    for epoch in range(1, 6): 
        total_loss = 0.0
        
        for batch_idx, batch in enumerate(dataloader):
            optimizer.zero_grad()

            # --- MOVE INPUTS TO GPU ---
            anchor_ids = batch['anchor_input_ids'].to(device)
            anchor_mask = batch['anchor_attention_mask'].to(device)
            pixel_vals = batch['pixel_values'].to(device)

            v_text, v_visual_aligned, _ = model(
                input_ids=anchor_ids, 
                attention_mask=anchor_mask, 
                pixel_values=pixel_vals
            )
            
            # PHASE 1 ALPHA OVERRIDE: 1.0 (100% Text, 0% Vision)
            alpha_override = 1.0 
            v_anchor = (alpha_override * v_text) + ((1.0 - alpha_override) * v_visual_aligned)
            v_anchor = F.normalize(v_anchor, p=2, dim=1)

            # --- MOVE POSITIVE/NEGATIVE INPUTS TO GPU ---
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

            if batch_idx % 50 == 0:
                logger.info(f"Epoch {epoch} | Batch {batch_idx}/{len(dataloader)} | Loss: {loss.item():.4f}")

        avg_loss = total_loss / len(dataloader)
        logger.info(f"✅ END OF EPOCH {epoch} | Avg Loss: {avg_loss:.4f}")
        torch.save(model.state_dict(), f"ms2c_phase1_epoch_{epoch}.pt")

if __name__ == "__main__":
    train_phase1_text()