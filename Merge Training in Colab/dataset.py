"""
MS2C E2E JOINT TRAINING DATASET
================================
Dual-Stream Triplet Dataset for Multimodal Semantic-to-Code Learning
Combines: Screenshot Anchor, Text Description, Positive Code Node, Negative Code Node
"""
import torch
import json
import os
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, ViTImageProcessor
from PIL import Image

class MS2CTripletDataset(Dataset):
    def __init__(self, data_list, text_model_name="microsoft/codebert-base", vision_model_name="google/vit-base-patch16-224-in21k", max_len=512, fast_img_dir="/content/03_screenshots"):
        self.data_list = data_list
        self.max_len = max_len
        
        print("\n" + "="*60)
        print("Initializing MS2C E2E Joint Training Dataset")
        print("="*60)
        
        print("Loading Tokenizer and Image Processor...")
        self.tokenizer = AutoTokenizer.from_pretrained(text_model_name)
        self.image_processor = ViTImageProcessor.from_pretrained(vision_model_name)
        print(f"✅ Models loaded | Dataset size: {len(self.data_list)}")

        # 🛠️ BUILD THE FAST PATH MAP
        # This scans the local unzipped folder and maps "filename.png" -> "/content/03_screenshots/subfolder/filename.png"
        self.path_map = {}
        if os.path.exists(fast_img_dir):
            print(f"🔍 Scanning high-speed local directory: {fast_img_dir}")
            for root, _, files in os.walk(fast_img_dir):
                for f in files:
                    if f.endswith(('.png', '.jpg', '.jpeg')):
                        self.path_map[f] = os.path.join(root, f)
            print(f"✅ Indexed {len(self.path_map)} images in local memory.\n")
        else:
            print(f"⚠️ WARNING: High-speed directory {fast_img_dir} not found!\n")

    def __len__(self):
        return len(self.data_list)

    def __getitem__(self, idx):
        item = self.data_list[idx]
        
        # --- 1. VISUAL STREAM ---
        raw_img_path = item.get('image_anchor', '')
        
        # Extract JUST the filename, ignoring whatever Google Drive path is in the JSON
        img_name = os.path.basename(raw_img_path)
        
        # Look it up in our fast local dictionary
        img_path = self.path_map.get(img_name)
        
        try:
            if not img_path:
                raise FileNotFoundError(f"Image {img_name} not found in path_map")
            image = Image.open(img_path).convert("RGB")
            pixel_values = self.image_processor(images=image, return_tensors="pt").pixel_values.squeeze(0)
        except Exception as e:
            # Fallback: Black placeholder if image is truly missing so training doesn't crash
            print(f"⚠️ Missing/Corrupt file: {img_name}")
            image = Image.new('RGB', (224, 224), color='black')
            pixel_values = self.image_processor(images=image, return_tensors="pt").pixel_values.squeeze(0)
        
        # --- 2. TEXTUAL STREAM (Description) ---
        text_anchor = str(item.get('description_anchor') or item.get('text_anchor') or "UI Screenshot")
        anchor_enc = self.tokenizer(text_anchor, truncation=True, padding='max_length', max_length=128, return_tensors="pt")
        
        # --- 3. CODE SPACE (Positive/Negative Nodes) ---
        pos_code = str(item.get('code_positive') or item.get('positive_node') or " ")
        neg_code = str(item.get('code_negative') or item.get('negative_node') or " ")

        pos_enc = self.tokenizer(pos_code, truncation=True, padding='max_length', max_length=self.max_len, return_tensors="pt")
        neg_enc = self.tokenizer(neg_code, truncation=True, padding='max_length', max_length=self.max_len, return_tensors="pt")
        
        return {
            'pixel_values': pixel_values,
            'anchor_input_ids': anchor_enc.input_ids.squeeze(0),
            'anchor_attention_mask': anchor_enc.attention_mask.squeeze(0),
            'pos_input_ids': pos_enc.input_ids.squeeze(0),
            'pos_attention_mask': pos_enc.attention_mask.squeeze(0),
            'neg_input_ids': neg_enc.input_ids.squeeze(0),
            'neg_attention_mask': neg_enc.attention_mask.squeeze(0)
        }

# --- LOCAL TESTING SCRIPT (VERIFY E2E JOINT DATASET) ---
if __name__ == "__main__":
    print("\n" + "="*70)
    print("MS2C E2E JOINT TRAINING DATASET - VERIFICATION TEST")
    print("="*70)
    
    # Safely construct the path to the dataset
    json_file_path = "/content/mutated_dataset_25k.json"
    
    print(f"\n📁 Looking for dataset at: {json_file_path}")
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            real_data = json.load(f)
        
        print(f"✅ Successfully loaded {len(real_data)} triplet samples!")
        
        # Test with first 2 samples
        test_subset = real_data[:2] 
        
        print(f"\n🔍 Testing with subset of {len(test_subset)} samples...")
        dataset = MS2CTripletDataset(test_subset)
        dataloader = DataLoader(dataset, batch_size=2, shuffle=False) 

        print("\n" + "-"*70)
        print("BATCH STRUCTURE FOR E2E JOINT TRAINING:")
        print("-"*70)
        
        for batch_idx, batch in enumerate(dataloader):
            print(f"\nVisual Stream (Screenshot):")
            print(f"  pixel_values shape: {batch['pixel_values'].shape}")
            print(f"  → Input to ViT-base (3, 224, 224)")
            
            print(f"\nTextual Stream (Bug Description):")
            print(f"  anchor_input_ids shape: {batch['anchor_input_ids'].shape}")
            print(f"  anchor_attention_mask shape: {batch['anchor_attention_mask'].shape}")
            print(f"  → Input to CodeBERT")
            
            print(f"\nCode Space (Positive Node):")
            print(f"  pos_input_ids shape: {batch['pos_input_ids'].shape}")
            print(f"  pos_attention_mask shape: {batch['pos_attention_mask'].shape}")
            
            print(f"\nCode Space (Negative Node):")
            print(f"  neg_input_ids shape: {batch['neg_input_ids'].shape}")
            print(f"  neg_attention_mask shape: {batch['neg_attention_mask'].shape}")
            
            print("\n" + "="*70)
            print("✅ SUCCESS! Dataset ready for E2E Joint Training")
            print("="*70)
            break 

    except FileNotFoundError:
        print(f"\n❌ ERROR: Could not find '{json_file_path}'")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")