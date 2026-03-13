# M-S2C E2E Joint Training - Data Structure & Implementation Guide

## ✅ VERIFIED Implementation Status

### 1. **Folder Structure** - CORRECT
```
d:\Thesis\Merge Training in Colab\
├── 01_raw_seeds/              ← Original seed code files
├── 02_mutated_code/           ← Generated mutated code variants
├── 03_screenshots/            ← UI Screenshots for each mutation
├── mutated_dataset_25k.json   ← Main training dataset
├── model_training_colab.py    ← E2E Joint Training script (MAIN)
├── dataset.py                 ← Dataset loader
├── ms2c_model.py              ← Model architecture
└── ...
```

### 2. **mutated_dataset_25k.json** - CORRECTLY STRUCTURED
```json
[
  {
    "id": "layering_01_AnnotatedGraph",
    "image_anchor": "layering/Mut_01_AnnotatedGraph.png",
    "text_anchor": "The 'AnnotatedGraph' component's depth stacking was intended but failed...",
    "positive_node": "<div className=\"relative z-20 bg-indigo-600...>",
    "negative_node": "<div className=\"absolute z-20 bg-white...>"
  },
  ...25000 more samples
]
```

**Required Keys:**
- ✅ `image_anchor` - Relative path to screenshot in `03_screenshots/`
- ✅ `text_anchor` - Natural language bug description
- ✅ `positive_node` - Correct AST code (ground truth)
- ✅ `negative_node` - Hard negative code (incorrect variant)

### 3. **Data Loading Pipeline** - CORRECTLY IMPLEMENTED

#### model_training_colab.py:
```python
# Loads mutated_dataset_25k.json from workspace root
json_file_path = REPO_DIR / "mutated_dataset_25k.json"
real_data = json.load(f)  # ✅ 25,000 triplet samples
```

#### dataset.py:
```python
# Processes each sample into dual-stream tensors
base_img_dir = os.path.join(REPO_DIR, "03_screenshots")
actual_image_path = os.path.join(base_img_dir, item['image_anchor'])
# Loads: "03_screenshots/layering/Mut_01_AnnotatedGraph.png"
```

### 4. **Folder Usage**

| Folder | Purpose | Used By | Status |
|--------|---------|---------|--------|
| `01_raw_seeds/` | Original unmodified code | Reference only | ✅ Not directly used in training |
| `02_mutated_code/` | Code mutations (AST variants) | Referenced in JSON as `positive_node`/`negative_node` | ✅ Data extracted into JSON |
| `03_screenshots/` | Screenshots of UI bugs | `dataset.py` loads via `image_anchor` | ✅ **CRITICAL - Must exist** |
| `mutated_dataset_25k.json` | Main training data | Loaded by `model_training_colab.py` | ✅ **CRITICAL - Main source** |

### 5. **Data Flow in E2E Joint Training**

```
mutated_dataset_25k.json (25k samples)
        ↓
MS2CTripletDataset.__getitem__()
        ↓
┌───────────────────────────────────────────────────┐
│ For each sample:                                  │
│ • Load image: 03_screenshots/{image_anchor}      │
│ • Tokenize text: {text_anchor}                   │
│ • Tokenize pos code: {positive_node}             │
│ • Tokenize neg code: {negative_node}             │
└───────────────────────────────────────────────────┘
        ↓
DataLoader batches samples (batch_size=4)
        ↓
model_training_colab.py E2E Joint Training Loop
        ↓
Dual-Stream Triplet Loss:
  • Loss_visual: Image → ViT → v_visual
  • Loss_textual: Text → CodeBERT → v_text
  • Combined: 0.7*Loss_visual + 0.3*Loss_textual
        ↓
Save: ms2c_E2E_JOINT_BEST.pt
```

## 📋 Verification Checklist

Before running `model_training_colab.py`:

- [ ] ✅ `mutated_dataset_25k.json` exists in workspace root
- [ ] ✅ JSON contains 25,000 samples with keys: `image_anchor`, `text_anchor`, `positive_node`, `negative_node`
- [ ] ✅ `03_screenshots/` folder exists with all referenced images
- [ ] ✅ Image paths in JSON match actual files (e.g., `layering/Mut_01_AnnotatedGraph.png`)
- [ ] ✅ `dataset.py`, `ms2c_model.py` in same directory as `model_training_colab.py`
- [ ] ✅ CodeBERT and ViT models can be downloaded from HuggingFace

## 🚀 Running E2E Joint Training

```bash
python model_training_colab.py
```

**Output:**
- `logs_e2e_joint_training.txt` - Training logs
- `ms2c_E2E_JOINT_BEST.pt` - Best model (lowest combined loss)
- `ms2c_E2E_JOINT_FINAL.pt` - Final model state

## ⚠️ Common Issues & Solutions

### Issue 1: "Could not find mutated_dataset_25k.json"
**Solution:** Ensure file is in workspace root, not in a subfolder

### Issue 2: "Error loading image..."
**Solution:** 
- Check if `03_screenshots/` folder exists
- Verify image paths in JSON match actual files
- Run dataset.py test: `python dataset.py` to verify

### Issue 3: CUDA Out of Memory
**Solution:**
- Batch size already minimal (4)
- Gradient accumulation active (4 steps = effective batch 16)
- Using A100, should handle fine

## 📊 Dataset Statistics

- **Total Samples:** 25,000
- **Categories:** Layering, Layout, Spacing, Typography, Visibility
- **Duplicates:** Yes (multiple text_anchors → same code node)
- **Image Format:** PNG (RGB, 224×224 after ViT preprocessing)
- **Code Type:** React JSX/HTML with Tailwind CSS
- **Text Length:** Variable (100-300 words)

## 🎯 Implementation Summary

✅ **All components correctly aligned:**
- `mutated_dataset_25k.json` → Correctly structured
- `03_screenshots/` → Correctly referenced
- `dataset.py` → Correctly loads from JSON
- `model_training_colab.py` → Correctly processes data
- `ms2c_model.py` → Correctly outputs embeddings

✅ **E2E joint training ready to run!**
