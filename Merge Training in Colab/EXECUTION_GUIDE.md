# M-S2C Execution Flow & Dependencies Guide

## File Status Summary

### ✅ ACTIVE FILES (E2E Joint Training)

#### 1. **model_training_colab.py** [PRIMARY TRAINING SCRIPT]
- **Purpose:** E2E Joint Training with dual-stream triplet loss
- **Inputs:** 
  - `mutated_dataset_25k.json` ✅ (exists)
  - `03_screenshots/` folder ✅ (exists)
  - `ms2c_phase1_BEST.pt` (optional - for transfer learning)
- **Outputs:**
  - `ms2c_E2E_JOINT_BEST.pt` (best checkpoint)
  - `ms2c_E2E_JOINT_FINAL.pt` (final checkpoint)
  - `logs_e2e_joint_training.txt`
- **Status:** ✅ READY - Run first
- **Command:** `python model_training_colab.py`

---

#### 2. **indexer.py** [BUILD FAISS INDEX]
- **Purpose:** Create FAISS index from codebase for retrieval
- **Inputs:**
  - `ms2c_E2E_JOINT_BEST.pt` (from model_training_colab.py)
  - `github_test_dataset.json` ⚠️ (MISSING)
- **Outputs:**
  - `ms2c_codebase.index` (FAISS vector database)
  - `node_mapping.json` (code metadata - id→{file_path, line_number, code})
  - `retrieval_logs.txt`
- **Status:** ⚠️ BLOCKED - Needs `github_test_dataset.json`
- **Dependency Chain:** training → indexer → (all downstream tools)
- **Command:** `python indexer.py`

---

#### 3. **retrieve.py** [RETRIEVAL ENGINE]
- **Purpose:** Retrieve top-k buggy code nodes from query (image + text)
- **Inputs:**
  - `ms2c_E2E_JOINT_BEST.pt` (from training)
  - `ms2c_codebase.index` (from indexer.py)
  - `node_mapping.json` (from indexer.py)
  - `github_test_dataset.json` ⚠️ (MISSING)
  - `03_screenshots/` folder
- **Outputs:**
  - Console: Top-k ranked code snippets with scores
  - File: Results appended to logs
- **Status:** ⚠️ BLOCKED - Needs indexer to run first
- **Command:** `python retrieve.py`

---

#### 4. **evaluate_metrics.py** [EVALUATION SCRIPT]
- **Purpose:** Measure retrieval performance (Hit@1, Hit@5, MRR, etc.)
- **Inputs:**
  - `ms2c_E2E_JOINT_BEST.pt` (from training)
  - `ms2c_codebase.index` (from indexer.py)
  - `node_mapping.json` (from indexer.py)
  - `github_test_dataset.json` ⚠️ (MISSING)
  - `03_screenshots/` folder
- **Outputs:**
  - Evaluation metrics (Hit@1, Hit@5, Hit@10, MRR, etc.)
  - Logs saved to `metrics_logs.txt`
- **Status:** ⚠️ BLOCKED - Needs indexer to run first
- **Command:** `python evaluate_metrics.py`

---

#### 5. **test_inference.py** [QUICK INFERENCE TEST]
- **Purpose:** Test inference on dummy samples
- **Inputs:**
  - `ms2c_E2E_JOINT_BEST.pt` (from training)
- **Outputs:**
  - Inference results on sample embeddings
- **Status:** ✅ Can run after training (independent of indexer)
- **Command:** `python test_inference.py`

---

#### 6. **ablation_study.py** [ABLATION STUDY]
- **Purpose:** Compare unimodal (text-only) vs multimodal (text+image)
- **Inputs:**
  - `ms2c_E2E_JOINT_BEST.pt` (from training)
  - `ms2c_codebase.index` (from indexer.py)
  - `node_mapping.json` (from indexer.py)
  - `github_test_dataset.json` ⚠️ (MISSING)
  - `03_screenshots/` folder
- **Outputs:**
  - Comparison metrics (multimodal vs unimodal performance)
  - Logs to `ablation_logs.txt`
- **Status:** ⚠️ BLOCKED - Needs indexer to run first
- **Command:** `python ablation_study.py`

---

#### 7. **benchmark_bm25.py** [LEXICAL BASELINE]
- **Purpose:** Benchmark against traditional BM25 lexical retrieval
- **Inputs:**
  - `node_mapping.json` (from indexer.py)
  - `github_test_dataset.json` ⚠️ (MISSING)
- **Outputs:**
  - BM25 baseline metrics (Hit@1, Hit@5, MRR, etc.)
  - Logs to console
- **Status:** ⚠️ BLOCKED - Needs indexer to run first AND github_test_dataset.json
- **Command:** `python benchmark_bm25.py`

---

### 📦 UTILITY FILES (Helper/Optional)

#### 8. **build_github_dataset.py** [DATASET BUILDER]
- **Purpose:** Manually append GitHub bug entries to dataset
- **Usage:** Edit the script's `if __name__ == "__main__"` section to add bugs
- **Inputs:** None (user defines bugs directly in code)
- **Outputs:** `github_test_dataset.json` (creates fresh or appends)
- **Status:** ⚠️ NEEDS USER ACTION - Must run this to create github_test_dataset.json
- **Command:** `python build_github_dataset.py`
- **Note:** Repeat this to add multiple bugs, or manually create `github_test_dataset.json` with your test data

---

#### 9. **llm_utility_test.py** [LLM COMPARISON]
- **Purpose:** Compare M-S2C vs LLM (Gemini) on bug localization
- **Inputs:**
  - `github_test_dataset.json` ⚠️ (MISSING)
  - Google Gemini API key (needs to be set in code)
- **Outputs:**
  - LLM vs M-S2C comparison metrics
  - Logs to console
- **Status:** ⚠️ BLOCKED - Needs github_test_dataset.json AND API key setup
- **Command:** `python llm_utility_test.py`
- **Note:** Requires `GENAI_API_KEY` to be set. Uses 10 samples by default (to preserve free quota)

---

#### 10. **dataset.py** [DATASET MODULE]
- **Purpose:** Data loading utilities (imported by training/eval scripts)
- **Status:** ✅ OK - Not meant to run standalone
- **Contains:** `MS2CTripletDataset` class for loading mutated_dataset_25k.json

---

#### 11. **ms2c_model.py** [MODEL ARCHITECTURE]
- **Purpose:** Model definition (imported by training/eval scripts)
- **Status:** ✅ OK - Not meant to run standalone
- **Contains:** `MS2CFusionEngine` class with dual-stream architecture

---

### 🗑️ OBSOLETE FILES (3-Phase Training - No Longer Used)

#### ❌ train_phase1_text.py
- **Status:** Obsolete - Use model_training_colab.py instead
- **Note:** Kept for reference only

#### ❌ train_phase2_vision.py
- **Status:** Obsolete - Use model_training_colab.py instead
- **Note:** Kept for reference only

#### ❌ train_phase3_fusion.py
- **Status:** Obsolete - Use model_training_colab.py instead
- **Note:** Kept for reference only

---

## 🎯 RECOMMENDED EXECUTION ORDER

### Phase 1: Training
```bash
python model_training_colab.py
```
**Output:** `ms2c_E2E_JOINT_BEST.pt`, `ms2c_E2E_JOINT_FINAL.pt`, `logs_e2e_joint_training.txt`

### Phase 2: Create Test Dataset (⚠️ CRITICAL BLOCKER)
**One of these:**
- **Option A:** Manually create `github_test_dataset.json` with test cases
- **Option B:** Use the helper script:
  ```bash
  python build_github_dataset.py
  ```

### Phase 3: Build FAISS Index
```bash
python indexer.py
```
**Output:** `ms2c_codebase.index`, `node_mapping.json`, `retrieval_logs.txt`

### Phase 4: Run Downstream Tools (in any order)
```bash
python retrieve.py              # Test retrieval
python evaluate_metrics.py      # Get metrics
python test_inference.py        # Quick inference test
python ablation_study.py        # Ablation analysis
python benchmark_bm25.py        # BM25 baseline
python llm_utility_test.py      # LLM comparison (needs API key)
```

---

## ⚠️ CRITICAL BLOCKERS

| File | Blocked By | Solution |
|------|-----------|----------|
| **indexer.py** | `github_test_dataset.json` | Create test dataset manually OR use build_github_dataset.py |
| **retrieve.py** | indexer.py + github_test_dataset.json | See above |
| **evaluate_metrics.py** | indexer.py + github_test_dataset.json | See above |
| **ablation_study.py** | indexer.py + github_test_dataset.json | See above |
| **benchmark_bm25.py** | indexer.py + github_test_dataset.json | See above |
| **llm_utility_test.py** | github_test_dataset.json + API key | Setup Gemini API key first |

---

## 📝 Data Format Requirements

### Required Files for Full Pipeline

1. **mutated_dataset_25k.json** ✅ EXISTS
   - Used by: model_training_colab.py (training)
   - Format: Array of objects with {image_anchor, text_anchor, positive_node, negative_node, ...}
   - Location: Workspace root

2. **github_test_dataset.json** ⚠️ MISSING - CREATE THIS
   - Used by: indexer.py, retrieve.py, evaluate_metrics.py, ablation_study.py, benchmark_bm25.py, llm_utility_test.py
   - Format: Array of test bug objects with {image_anchor, text_anchor, positive_node, negative_node, ...}
   - Location: Workspace root
   - **How to create:**
     - **Option 1:** Run `python build_github_dataset.py` repeatedly to add bugs
     - **Option 2:** Manually create with same schema as mutated_dataset_25k.json
     - **Option 3:** Use subset of mutated_dataset_25k.json

3. **03_screenshots/** ✅ EXISTS
   - Used by: model_training_colab.py, retrieve.py, evaluate_metrics.py, ablation_study.py
   - Contains: Screenshot images referenced by image_anchor paths

---

## 🚀 Quick Start Template

```bash
# Step 1: Train the model (takes ~2-4 hours on A100)
python model_training_colab.py

# Step 2: Create test dataset (one-time setup)
# Option A: Create manually or via build_github_dataset.py
# Option B: For quick testing, can use subset of mutated_dataset_25k.json

# Step 3: Build FAISS index (after test dataset ready)
python indexer.py

# Step 4: Run evaluation tools
python evaluate_metrics.py          # Official metrics
python retrieve.py                  # Test retrieval on first sample
python test_inference.py            # Quick sanity check
python ablation_study.py            # Compare modalities
```

---

## ✅ Dependency Graph

```
model_training_colab.py
    ↓
    ├→ ms2c_E2E_JOINT_BEST.pt ─────┐
    └→ logs_e2e_joint_training.txt  │
                                     │
    + github_test_dataset.json ─────┤
              ↓                      │
         indexer.py ────────────────→ ms2c_codebase.index
              ↓                      │
         node_mapping.json ──────────┼──→ retrieve.py ━━━━━━━━━ Top-k Results
                                     ├──→ evaluate_metrics.py ━━ Metrics
                                     ├──→ ablation_study.py ━━━━ Ablation Report
                                     └──→ benchmark_bm25.py ━━━ BM25 Baseline

    + API_KEY ─→ llm_utility_test.py ━━━━ LLM Comparison
    + test_inference.py (independent) ━━ Inference Test
```

---

## 📋 Checklist Before Running

- [ ] `mutated_dataset_25k.json` exists at workspace root
- [ ] `03_screenshots/` folder exists and contains images
- [ ] `model_training_colab.py` will create E2E checkpoints
- [ ] Create `github_test_dataset.json` (for downstream tools)
- [ ] Run `indexer.py` to generate FAISS index
- [ ] All downstream tools can now run successfully

