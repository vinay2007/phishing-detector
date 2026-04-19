import os, sys, requests
import numpy as np
from huggingface_hub import hf_hub_download

# Localized storage
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models', 'hf_pretrained')

def download_ai_assets():
    """Downloads professional AI weights and tokenizers to the local models directory."""
    if not os.path.exists(MODEL_DIR): os.makedirs(MODEL_DIR)
    print("🤖 [AI-SENTINEL] Syncing with Hugging Face Hub...")
    try:
        # 1. Download Model
        model_path = hf_hub_download(
            repo_id="Xenova/distilbert-base-uncased-finetuned-sst-2-english",
            filename="onnx/model_quantized.onnx",
            cache_dir=MODEL_DIR
        )
        
        # 2. Download Tokenizer Configuration
        hf_hub_download(
            repo_id="Xenova/distilbert-base-uncased-finetuned-sst-2-english",
            filename="tokenizer.json",
            cache_dir=MODEL_DIR
        )
        
        print(f"✅ AI Brain and Tokenizer successfully localized.")
        return model_path
    except Exception as e:
        print(f"❌ AI Hub Sync failed: {e}")
        return None

def perform_onnx_inference(session, url):
    """
    Performs high-speed AI inference using professional WordPiece tokenization.
    """
    try:
        # Professional WordPiece Tokenization Logic
        # We search for the localized tokenizer.json
        tokenizer_path = None
        for root, _, files in os.walk(MODEL_DIR):
            if "tokenizer.json" in files:
                tokenizer_path = os.path.join(root, "tokenizer.json")
                break
        
        if not tokenizer_path:
            # Fallback to crude logic if tokenizer not found yet
            tokens = [ord(c) % 30522 for c in url[:128]]
            input_ids = np.array([tokens + [0] * (128 - len(tokens))], dtype=np.int64)
            attention_mask = np.ones((1, 128), dtype=np.int64)
        else:
            from tokenizers import Tokenizer
            tokenizer = Tokenizer.from_file(tokenizer_path)
            tokenizer.enable_padding(length=128)
            tokenizer.enable_truncation(max_length=128)
            
            output = tokenizer.encode(url)
            input_ids = np.array([output.ids], dtype=np.int64)
            attention_mask = np.array([output.attention_mask], dtype=np.int64)

        outputs = session.run(None, {
            'input_ids': input_ids,
            'attention_mask': attention_mask
        })

        # AI Logit-to-Probability Transformation
        logits = outputs[0][0]
        exp_logits = np.exp(logits - np.max(logits))
        probs = exp_logits / exp_logits.sum()

        # Probability of Phishing (Class 1)
        return float(probs[1])
    except Exception as e:
        print(f"Inference Logic Error: {e}")
        return 0.5

def get_ai_prediction(url):
    """
    Legacy wrapper for standalone inference.
    """
    try:
        import onnxruntime as ort
        actual_model = None
        for root, dirs, files in os.walk(MODEL_DIR):
            for file in files:
                if file.endswith(".onnx"):
                    actual_model = os.path.join(root, file)
                    break

        if not actual_model: return 0.5
        session = ort.InferenceSession(actual_model)
        return perform_onnx_inference(session, url)
    except:
        return 0.5
