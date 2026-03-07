import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
import json
import os

from ms2c_model import MS2CFusionEngine
from dataset import MS2CTripletDataset

# --- EXPLICIT PATH RESOLVER ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.join(BASE_DIR, "Seed-and-Mutate", "ms2c-local")

def train_phase3_stabilization():
    print("Initializing M-S2C Engine for Phase 3: Stabilization...")
    model = MS2CFusionEngine()

    # 1. Load the Visually-Aligned Phase 2 Brain
    checkpoint_file = "ms2c_phase2_epoch_1.pt" 
    print(f"Loading dual-aligned modalities from {checkpoint_file}...")
    model.load_state_dict(torch.load(checkpoint_file, map_location="cpu"))
    print("✅ Successfully locked in Phase 2 weights!")
    
    # --- PHASE 3: HARDWARE LOGIC ---
    print("-> Freezing CodeBERT completely...")
    for param in model.codebert.parameters():
        param.requires_grad = False
        
    print("-> Freezing ViT completely...")
    for param in model.vit.parameters():
        param.requires_grad = False

    print("-> Waking up ONLY the MLP and Gating Network...")
    # Because both massive encoders are frozen, this phase will run lightning fast!

    model.train() 

    # Optimizer automatically grabs only the unfrozen MLP and Gating layers
    optimizer = torch.optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=1e-5) 

    json_file_path = os.path.join(REPO_DIR, "data", "manifests", "spacing.json")
    with open(json_file_path, 'r', encoding='utf-8') as f:
        real_data = json.load(f)
        
    dataset = MS2CTripletDataset(real_data)
    
    # We can keep batch size at 4
    dataloader = DataLoader(dataset, batch_size=4, shuffle=True)

    print(f"\nStarting Phase 3 Stabilization Loop on ALL {len(real_data)} Spacing samples...")
    margin = 0.5 

    # We only need 1 single epoch to let Alpha settle
    for epoch in range(1, 2): 
        total_loss = 0.0
        alpha_tracker = []
        
        for batch_idx, batch in enumerate(dataloader):
            optimizer.zero_grad()

            # The Alpha Override is GONE. The model must balance itself natively!
            v_text, v_visual_aligned, alpha = model(
                input_ids=batch['anchor_input_ids'], 
                attention_mask=batch['anchor_attention_mask'], 
                pixel_values=batch['pixel_values']
            )
            
            v_anchor = (alpha * v_text) + ((1.0 - alpha) * v_visual_aligned)
            v_anchor = F.normalize(v_anchor, p=2, dim=1)

            with torch.no_grad():
                pos_outputs = model.codebert(input_ids=batch['pos_input_ids'], attention_mask=batch['pos_attention_mask'])
                v_pos = F.normalize(pos_outputs.last_hidden_state[:, 0, :], p=2, dim=1)

                neg_outputs = model.codebert(input_ids=batch['neg_input_ids'], attention_mask=batch['neg_attention_mask'])
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
                print(f"   Phase 3 - Epoch {epoch} | Batch {batch_idx}/{len(dataloader)} | Current Loss: {loss.item():.4f} | Alpha: {alpha.mean().item():.4f}")

        avg_loss = total_loss / len(dataloader)
        avg_alpha = sum(alpha_tracker) / len(alpha_tracker)
        print(f"\n✅ END OF PHASE 3 EPOCH {epoch} | Avg Triplet Loss: {avg_loss:.4f} | Final Alpha Balance: {avg_alpha:.4f}\n")
        
        torch.save(model.state_dict(), f"ms2c_phase3_FINAL.pt")

if __name__ == "__main__":
    train_phase3_stabilization()