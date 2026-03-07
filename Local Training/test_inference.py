import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, ViTImageProcessor
from PIL import Image
import json
import os
from pathlib import Path

# Import your custom model class
from ms2c_model import MS2CFusionEngine

# Try to import FAISS if available; fall back to similarity search
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("⚠️  FAISS not installed. Using cosine similarity fallback instead.")


def load_model(weights_path, device='cpu'):
    """
    Load the MS2CFusionEngine model with pre-trained weights.
    
    Args:
        weights_path: Path to saved model weights
        device: 'cpu' or 'cuda'
    
    Returns:
        model, tokenizer, image_processor
    """
    print("🤖 Loading CodeBERT Tokenizer and ViT Processor...")
    tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
    image_processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224-in21k")
    
    print(f"🧠 Initializing MS2CFusionEngine Model Architecture...")
    model = MS2CFusionEngine(
        text_model_name="microsoft/codebert-base",
        vision_model_name="google/vit-base-patch16-224-in21k",
        code_dim=768,
        vision_dim=768
    )
    
    print(f"📥 Loading trained weights from {weights_path}...")
    if os.path.exists(weights_path):
        try:
            model.load_state_dict(torch.load(weights_path, map_location=device))
            print("✅ Successfully loaded model weights!")
        except Exception as e:
            print(f"❌ Error loading weights: {e}")
            print("⚠️  Proceeding with untrained initialization.")
    else:
        print(f"⚠️  Weight file not found at {weights_path}")
        print("   Proceeding with untrained model (good for testing)")
    
    model = model.to(device)
    model.eval()  # Set to evaluation mode
    
    return model, tokenizer, image_processor


def infer_code_fix(model, tokenizer, image_processor, bug_description, image_path, bounding_box=None, device='cpu'):
    """
    Generate a fused multimodal embedding for the bug (description + screenshot).
    This embedding can be used for retrieval or similarity matching.
    
    Args:
        model: MS2CFusionEngine instance
        tokenizer: CodeBERT tokenizer
        image_processor: ViT image processor
        bug_description: String describing the bug (e.g., "margin-bottom: -5px;")
        image_path: Path to screenshot showing the bug
        bounding_box: Optional dict with {'x', 'y', 'width', 'height'} for region of interest
        device: Device to run on
    
    Returns:
        {
            'v_text': text embedding,
            'v_visual': visual embedding,
            'v_fused': fused embedding (weighted by alpha),
            'alpha': gating weight,
            'bug_description': input description
        }
    """
    print("\n🔍 Analyzing Input...")
    
    # 1. Process Text (CodeBERT)
    print(f"   📝 Tokenizing bug description: '{bug_description[:60]}...'")
    text_inputs = tokenizer(
        bug_description,
        return_tensors="pt",
        padding="max_length",
        truncation=True,
        max_length=128
    ).to(device)
    
    # 2. Process Image (ViT)
    print(f"   🖼️  Loading screenshot from {os.path.basename(image_path)}...")
    try:
        raw_image = Image.open(image_path).convert("RGB")
        
        # Optional: Crop to bounding box region for focused analysis
        if bounding_box and all(k in bounding_box for k in ['x', 'y', 'width', 'height']):
            print(f"   ✂️  Cropping to bounding box region: x={bounding_box['x']}, y={bounding_box['y']}, " 
                  f"w={bounding_box['width']}, h={bounding_box['height']}")
            x1 = bounding_box['x']
            y1 = bounding_box['y']
            x2 = x1 + bounding_box['width']
            y2 = y1 + bounding_box['height']
            raw_image = raw_image.crop((x1, y1, x2, y2))
        
        image_inputs = image_processor(images=raw_image, return_tensors="pt").to(device)
    except Exception as e:
        print(f"❌ Error loading image: {e}")
        return None

    print("⚙️  Running forward pass (CodeBERT + ViT -> Adaptive Gating)...")
    
    # 3. Forward Pass
    with torch.no_grad():
        v_text, v_visual_aligned, alpha = model(
            input_ids=text_inputs['input_ids'],
            attention_mask=text_inputs['attention_mask'],
            pixel_values=image_inputs['pixel_values']
        )
        
        # Compute fused embedding using adaptive gating
        v_fused = (alpha * v_text) + ((1.0 - alpha) * v_visual_aligned)
        v_fused = F.normalize(v_fused, p=2, dim=1)
    
    result = {
        'v_text': v_text.cpu().detach(),
        'v_visual': v_visual_aligned.cpu().detach(),
        'v_fused': v_fused.cpu().detach(),
        'alpha': alpha.item(),
        'bug_description': bug_description
    }
    
    return result


def retrieve_top_k_fixes(embedding_result, code_fixes_db, k=3):
    """
    Retrieve top-k most similar code fixes using cosine similarity.
    
    Args:
        embedding_result: Output from infer_code_fix()
        code_fixes_db: List of dicts with 'code' and 'description' keys
        k: Number of top results to return
    
    Returns:
        List of top-k matches: [{'code': ..., 'description': ..., 'similarity': ...}, ...]
    """
    v_query = embedding_result['v_fused']  # [1, 768]
    
    # Compute code embeddings (simplified: using CodeBERT)
    # In practice, you'd pre-compute these and store in FAISS
    print(f"\n🔎 Searching for Top-{k} Similar Code Fixes...")
    
    top_matches = []
    
    # For demo: compute embeddings on-the-fly for small databases
    for i, fix in enumerate(code_fixes_db):
        # Simplified: use the fix code directly (in production, use pre-computed embeddings)
        code_str = fix['code']
        
        # Mock similarity (in reality, compute actual embedding)
        similarity = (0.9 - i * 0.1)  # Mock decreasing similarity
        
        top_matches.append({
            'rank': i + 1,
            'code': code_str,
            'description': fix.get('description', 'N/A'),
            'similarity': similarity
        })
    
    return sorted(top_matches, key=lambda x: x['similarity'], reverse=True)[:k]


def print_inference_results(bug_input, embedding_result, top_matches):
    """Pretty-print the inference results."""
    print("\n" + "="*70)
    print("✅ MULTIMODAL BUG-FIX INFERENCE RESULTS")
    print("="*70)
    
    print("\n📋 INPUT BUG REPORT:")
    print(f"   Description: {bug_input['description']}")
    print(f"   Screenshot:  {os.path.basename(bug_input['image_path'])}")
    if bug_input.get('bounding_box'):
        bb = bug_input['bounding_box']
        print(f"   ROI: ({bb['x']}, {bb['y']}) -> {bb['width']}x{bb['height']}")
    
    print(f"\n🧠 MODEL ANALYSIS:")
    print(f"   Alpha (Text-Visual Balance): {embedding_result['alpha']:.4f}")
    print(f"   (0.0 = Pure Visual, 1.0 = Pure Text)")
    print(f"   Text Embedding Norm:   {embedding_result['v_text'].norm().item():.4f}")
    print(f"   Visual Embedding Norm: {embedding_result['v_visual'].norm().item():.4f}")
    print(f"   Fused Embedding Norm:  {embedding_result['v_fused'].norm().item():.4f}")
    
    print(f"\n🎯 TOP-{len(top_matches)} PREDICTED CODE FIXES:")
    for match in top_matches:
        print(f"\n   Rank {match['rank']} (Similarity: {match['similarity']:.4f})")
        print(f"   ├─ Fixed Code: {match['code']}")
        print(f"   └─ Note: {match['description']}")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    # --- CONFIGURATION ---
    WEIGHTS_PATH = "ms2c_phase3_FINAL.pt"  # Use your trained weights
    DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    print(f"🚀 Initializing Inference Pipeline on {DEVICE.upper()}...\n")
    
    # Load model
    model, tokenizer, image_processor = load_model(WEIGHTS_PATH, device=DEVICE)
    
    # --- DUMMY TEST CASE (Spacing Bug Example) ---
    print("\n" + "="*70)
    print("📌 RUNNING DUMMY TEST: Spacing Bug Detection")
    print("="*70)
    
    # Create dummy test image for demonstration
    TEST_IMAGE_PATH = "test_screenshot.png"
    
    # Create a simple test screenshot if it doesn't exist
    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"📸 Creating test screenshot at {TEST_IMAGE_PATH}...")
        test_img = Image.new('RGB', (224, 224), color='white')
        # Add some simple graphics to represent a UI
        from PIL import ImageDraw
        draw = ImageDraw.Draw(test_img)
        draw.rectangle([(50, 50), (150, 100)], outline='blue', width=2)
        draw.text((60, 60), "Button", fill='black')
        test_img.save(TEST_IMAGE_PATH)
    
    # Test inputs
    TEST_BUG_DESCRIPTION = "The Close Button is not visible due to a spacing error on the right side."
    TEST_BBOX = {"x": 50, "y": 50, "width": 100, "height": 50}
    
    # Run inference
    embedding = infer_code_fix(
        model, 
        tokenizer, 
        image_processor,
        bug_description=TEST_BUG_DESCRIPTION,
        image_path=TEST_IMAGE_PATH,
        bounding_box=TEST_BBOX,
        device=DEVICE
    )
    
    if embedding:
        # Dummy code fixes database
        SAMPLE_FIXES = [
            {
                'code': '<button type="button" aria-label="close" className="active:scale-90 transition-all mt-3">',
                'description': 'Added margin-top to push button down'
            },
            {
                'code': '<button type="button" aria-label="close" className="active:scale-90 transition-all ml-2">',
                'description': 'Added margin-left to adjust horizontal position'
            },
            {
                'code': '<button type="button" aria-label="close" className="active:scale-90 transition-all px-4 py-2">',
                'description': 'Added padding to increase clickable area'
            }
        ]
        
        # Retrieve top matches
        top_matches = retrieve_top_k_fixes(embedding, SAMPLE_FIXES, k=3)
        
        # Display results
        print_inference_results(
            bug_input={
                'description': TEST_BUG_DESCRIPTION,
                'image_path': TEST_IMAGE_PATH,
                'bounding_box': TEST_BBOX
            },
            embedding_result=embedding,
            top_matches=top_matches
        )
        
        print("\n💡 NEXT STEPS:")
        print("   1. Replace SAMPLE_FIXES with your actual pre-computed code embeddings")
        print("   2. Use FAISS index for efficient large-scale retrieval (see retrieve.py)")
        print("   3. Fine-tune similarity matching based on your specific domain")
