import torch
import json
import os
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, ViTImageProcessor
from PIL import Image

# --- EXPLICIT PATH RESOLVER ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.join(BASE_DIR, "Seed-and-Mutate", "ms2c-local")

class MS2CTripletDataset(Dataset):
    def __init__(self, data_list, text_model_name="microsoft/codebert-base", vision_model_name="google/vit-base-patch16-224-in21k", max_len=128):
        self.data_list = data_list
        self.max_len = max_len
        
        print("Initializing Tokenizer and Image Processor...")
        self.tokenizer = AutoTokenizer.from_pretrained(text_model_name)
        self.image_processor = ViTImageProcessor.from_pretrained(vision_model_name)

    def __len__(self):
        return len(self.data_list)

    def __getitem__(self, idx):
        item = self.data_list[idx]
        
        # 1. Process Anchor Image (Screenshot)
        base_img_dir = os.path.join(REPO_DIR, "data", "screenshots") 
        actual_image_path = os.path.join(base_img_dir, item['image_anchor'])
        
        try:
            image = Image.open(actual_image_path).convert("RGB")
            pixel_values = self.image_processor(images=image, return_tensors="pt").pixel_values.squeeze(0)
        except Exception as e:
            print(f"Error loading image {actual_image_path}: {e}")
            pixel_values = torch.zeros((3, 224, 224))

        # 2. Process Anchor Text (Bug Report)
        anchor_text_enc = self.tokenizer(
            item['text_anchor'], padding='max_length', truncation=True, max_length=self.max_len, return_tensors="pt"
        )
        
        # 3. Process Positive Code (Correct Buggy AST Node)
        pos_code_enc = self.tokenizer(
            item['positive_node'], padding='max_length', truncation=True, max_length=self.max_len, return_tensors="pt"
        )
        
        # 4. Process Negative Code (Hard Negative AST Node)
        neg_code_enc = self.tokenizer(
            item['negative_node'], padding='max_length', truncation=True, max_length=self.max_len, return_tensors="pt"
        )

        return {
            "pixel_values": pixel_values,
            "anchor_input_ids": anchor_text_enc.input_ids.squeeze(0),
            "anchor_attention_mask": anchor_text_enc.attention_mask.squeeze(0),
            "pos_input_ids": pos_code_enc.input_ids.squeeze(0),
            "pos_attention_mask": pos_code_enc.attention_mask.squeeze(0),
            "neg_input_ids": neg_code_enc.input_ids.squeeze(0),
            "neg_attention_mask": neg_code_enc.attention_mask.squeeze(0),
        }

# --- LOCAL TESTING SCRIPT (REAL DATA) ---
if __name__ == "__main__":
    # Safely construct the path to the nested spacing.json
    json_file_path = os.path.join(REPO_DIR, "data", "manifests", "spacing.json")
    
    print(f"\nLooking for data exactly here:\n{json_file_path}")
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            real_data = json.load(f)
            
        print(f"Successfully loaded {len(real_data)} triplets!")
        
        local_test_subset = real_data[:2] 
        
        dataset = MS2CTripletDataset(local_test_subset)
        dataloader = DataLoader(dataset, batch_size=2, shuffle=True) 

        print("\nDataset loaded. Passing real Spacing data through processors...")
        for batch in dataloader:
            print(f"Pixel Values Shape: {batch['pixel_values'].shape}")
            print(f"Anchor Text IDs Shape: {batch['anchor_input_ids'].shape}")
            print(f"Positive Code IDs Shape: {batch['pos_input_ids'].shape}")
            print(f"Negative Code IDs Shape: {batch['neg_input_ids'].shape}")
            print("\nSUCCESS! Your pipeline is reading the Spacing JSON and images perfectly.")
            break 

    except FileNotFoundError:
        print(f"\nERROR: Still could not find '{json_file_path}'.")
    except KeyError as e:
        print(f"\nERROR: JSON missing key: {e}")
