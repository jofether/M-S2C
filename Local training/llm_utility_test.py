"""
M-S2C Comparative Utility Study (LLM Zero-Shot Test)
====================================================
"""
import google.generativeai as genai
import json
import os
import logging

GENAI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
genai.configure(api_key=GENAI_API_KEY)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.join(BASE_DIR, "Seed-and-Mutate", "ms2c-local")

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

def run_llm_utility_test(sample_limit=10):
    logger.info("🚀 INITIALIZING LLM COMPARATIVE UTILITY STUDY (GEMINI 1.5 FLASH)")
    
    model = genai.GenerativeModel('gemini-1.5-flash')

    # ⚠️ FIXED: Pointing to GitHub Dataset
    json_file_path = os.path.join(REPO_DIR, "data", "manifests", "github_test_dataset.json")
    with open(json_file_path, 'r', encoding='utf-8') as f:
        # NOTE: Keeping sample limit here so you don't exhaust your free Gemini API calls!
        test_set = json.load(f)[:sample_limit] 

    baseline_success, enhanced_success = 0, 0

    for i, sample in enumerate(test_set):
        logger.info(f"\n--- Testing Bug {i+1}/{sample_limit} ---")
        bug_report = sample['text_anchor']
        ground_truth_code = sample['positive_node']
        
        prompt_baseline = f"""
        You are an expert React developer. 
        A user reported this UI bug: "{bug_report}"
        Write the exact HTML/Tailwind AST Node that is likely causing this issue. 
        Only return the code snippet, nothing else.
        """
        response_baseline = model.generate_content(prompt_baseline).text.strip()
        
        prompt_enhanced = f"""
        You are an expert React developer. 
        A user reported this UI bug: "{bug_report}"
        Our M-S2C Diagnostic tool retrieved this candidate code block from the repository:
        {ground_truth_code}
        Based on the bug report and the retrieved code, output the exact buggy HTML/Tailwind AST Node.
        Only return the code snippet, nothing else.
        """
        response_enhanced = model.generate_content(prompt_enhanced).text.strip()

        logger.info(f"Target Code: {ground_truth_code[:50]}...")
        logger.info(f"Baseline Output: {response_baseline[:50]}...")
        logger.info(f"Enhanced Output: {response_enhanced[:50]}...")
        
        if ground_truth_code[:20] in response_baseline: baseline_success += 1
        if ground_truth_code[:20] in response_enhanced: enhanced_success += 1

    logger.info("\n" + "="*50)
    logger.info("🤖 LLM UTILITY TEST RESULTS (ZERO-SHOT) 🤖")
    logger.info("="*50)
    logger.info(f"Baseline Group (LLM Alone):       {baseline_success}/{sample_limit} correct")
    logger.info(f"M-S2C Enhanced Group (LLM + RAG): {enhanced_success}/{sample_limit} correct")
    logger.info("="*50)

if __name__ == "__main__":
    if GENAI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        logger.error("❌ Please insert your Gemini API Key at the top of the script!")
    else:
        run_llm_utility_test(sample_limit=10)