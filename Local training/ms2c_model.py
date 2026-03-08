"""
M-S2C Fusion Engine Architecture
================================
This file defines the core PyTorch model architecture for the Multimodal 
Source-to-Code (M-S2C) Bug Localization system. It combines a text/code 
encoder (CodeBERT) and an image encoder (ViT) using a custom Adaptive 
Gating Network.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoModel, ViTModel

class MS2CFusionEngine(nn.Module):
    """
    The Multimodal Source-to-Code Fusion Engine.
    
    Architecture:
    1. Code/Text Stream: CodeBERT extracts semantic features from text/code.
    2. Vision Stream: ViT extracts spatial/visual features from UI screenshots.
    3. MLP Projection: Maps the 768-D Vision vector into the Code semantic space.
    4. Adaptive Gating Network: Dynamically computes an 'alpha' weight to balance 
       the importance of Text vs. Vision for a given bug.
    """
    def __init__(self, 
                 text_model_name="microsoft/codebert-base", 
                 vision_model_name="google/vit-base-patch16-224-in21k", 
                 code_dim=768, 
                 vision_dim=768):
        super(MS2CFusionEngine, self).__init__()
        
        # 1. Load Pre-trained Encoders
        print("Loading CodeBERT and ViT models...")
        self.codebert = AutoModel.from_pretrained(text_model_name)
        self.vit = ViTModel.from_pretrained(vision_model_name)
        
        # 2. FREEZE ENCODERS (Crucial for local training to prevent OOM)
        for param in self.codebert.parameters():
            param.requires_grad = False
        for param in self.vit.parameters():
            param.requires_grad = False
            
        # 3. Trainable MLP Projection Head (Projects Vision to Code Semantic Space)
        self.mlp_projection = nn.Sequential(
            nn.Linear(vision_dim, code_dim),
            nn.ReLU(),
            nn.Linear(code_dim, code_dim)
        )
        
        # 4. Trainable Adaptive Gating Network (Calculates alpha parameter)
        # Input is concatenated normalized text and visual vectors (code_dim * 2)
        self.gating_network = nn.Sequential(
            nn.Linear(code_dim * 2, 1),
            nn.Sigmoid() # Constrains output to [0, 1] range
        )

    def forward(self, input_ids, attention_mask, pixel_values):
        """
        Forward pass for the multimodal inputs.
        
        Args:
            input_ids (Tensor): Tokenized text/code inputs for CodeBERT.
            attention_mask (Tensor): Attention masks for CodeBERT.
            pixel_values (Tensor): Processed image tensors for ViT.
            
        Returns:
            v_text (Tensor): The L2-normalized text embedding.
            v_visual_aligned (Tensor): The L2-normalized, projected visual embedding.
            alpha (Tensor): The gating weight balancing the two modalities.
        """
        # --- TEXT STREAM ---
        text_outputs = self.codebert(input_ids=input_ids, attention_mask=attention_mask)
        # Extract [CLS] token representation
        v_text_raw = text_outputs.last_hidden_state[:, 0, :] 
        # L2 Normalization
        v_text = F.normalize(v_text_raw, p=2, dim=1) 
        
        # --- VISION STREAM ---
        vision_outputs = self.vit(pixel_values=pixel_values)
        # Extract [CLS] token representation
        v_visual_raw = vision_outputs.last_hidden_state[:, 0, :] 
        # Project and Normalize
        v_visual_aligned = self.mlp_projection(v_visual_raw)
        v_visual_aligned = F.normalize(v_visual_aligned, p=2, dim=1)
        
        # --- ADAPTIVE GATING ---
        fused_features = torch.cat((v_text, v_visual_aligned), dim=1)
        alpha = self.gating_network(fused_features)
        
        return v_text, v_visual_aligned, alpha

# --- LOCAL TESTING SCRIPT ---
if __name__ == "__main__":
    """
    This block allows you to run `python ms2c_model.py` directly to 
    test if the architecture initializes and processes dummy tensors correctly.
    """
    # Initialize the model
    model = MS2CFusionEngine()
    
    # Initialize the Triplet Margin Loss (margin explicitly set to 0.5)
    criterion = nn.TripletMarginLoss(margin=0.5, p=2)
    
    # Only pass the trainable parameters to the optimizer
    optimizer = torch.optim.Adam([
        {'params': model.mlp_projection.parameters()},
        {'params': model.gating_network.parameters()}
    ], lr=1e-4)

    print("\nModel successfully initialized! Encoders are frozen. Ready for dummy data test.")
    
    # Dummy Data shapes for a batch size of 2 (to simulate local micro-batching)
    # input_ids: [batch_size, sequence_length]
    # pixel_values: [batch_size, channels, height, width] -> ViT requires 224x224
    dummy_input_ids = torch.randint(0, 50000, (2, 128)) 
    dummy_attention_mask = torch.ones((2, 128))
    dummy_pixel_values = torch.randn(2, 3, 224, 224) 
    
    # Forward Pass
    v_text, v_visual_aligned, alpha = model(dummy_input_ids, dummy_attention_mask, dummy_pixel_values)
    
    print(f"Text Vector Shape: {v_text.shape}")
    print(f"Visual Aligned Shape: {v_visual_aligned.shape}")
    print(f"Alpha Weight Shape: {alpha.shape}")
    print(f"Sample Alpha Values: {alpha.squeeze().tolist()}")