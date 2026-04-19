from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
from src.features import normalize_url, WHITELIST, BLACKLIST, perform_ai_inference, extract_all_features, update_whitelist, update_ai_training_set
from src.ai_model import get_ai_prediction
import joblib
import onnxruntime as ort

app = FastAPI(title="AI Sentinel Pro | Security Engine")

# Security: CORS Policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Models once at startup
MODELS = {}

@app.on_event("startup")
def load_models():
    # 1. Ensure AI Assets are localized (Downloads if missing)
    from src.ai_model import download_ai_assets
    download_ai_assets()

    # 2. Load Local RandomForest Expert Logic
    rf_path = 'models/phishing_model.pkl'
    if os.path.exists(rf_path):
        MODELS['rf'] = joblib.load(rf_path)

    hf_dir = 'models/hf_pretrained'
    if os.path.exists(hf_dir):
        for root, _, files in os.walk(hf_dir):
            for f in files:
                if f.endswith(".onnx"):
                    MODELS['onnx'] = ort.InferenceSession(os.path.join(root, f))
                    break

class URLRequest(BaseModel):
    url: str

class FeedbackRequest(BaseModel):
    url: str
    label: int

# --- ROUTES ---

@app.get("/")
async def root():
    # Automatically load /about when root is visited
    return RedirectResponse(url="/about")

@app.get("/about")
async def read_about():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"status": "API Online", "message": "About Page (index.html) not found"}

@app.get("/app")
async def read_app():
    # In a SPA, /app can also serve index.html, and the frontend handles the 'app' state
    # We will serve index.html and let Alpine.js handle the internal routing
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"status": "API Online", "message": "App Page (index.html) not found"}

@app.get("/document")
async def read_docs():
    if os.path.exists("docs.html"):
        return FileResponse("docs.html")
    return {"status": "API Online", "message": "Documentation Page not found"}

@app.post("/analyze")
async def analyze_url(req: URLRequest):
    url = req.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    clean_url = "https://" + url if not url.startswith("http") else url
    norm_url = normalize_url(clean_url)

    # 1. Whitelist Check
    if norm_url in WHITELIST:
        return {"type": "safe", "reason": "Whitelisted Domain", "risk": 0, "evidence": {}, "infra": 0, "url": clean_url}

    # 2. Known Threat Check (Blacklist)
    if norm_url in BLACKLIST:
        return {
            "type": "analysis",
            "url": clean_url,
            "risk": 100.0,
            "evidence": {"has_password": 1, "brand_spoofing": 1, "urgent_keywords": 1, "ext_forms": 1},
            "infra": 100,
            "reason": "Known Phishing Vector (Database Match)"
        }

    # 3. Deep Forensic Scan
    inf = perform_ai_inference(clean_url)
    feats = extract_all_features(clean_url, behavior_data=inf['evidence'], infra_score=inf['infra_score']/100.0)

    # 3. Model Inference
    ml_p = MODELS['rf'].predict_proba([feats])[0][1] if 'rf' in MODELS else 0.5
    hf_p = get_ai_prediction(clean_url)

    final_risk = min((ml_p * 35) + (hf_p * 35) + (inf['total_risk'] * 0.3), 100.0)

    return {
        "type": "analysis",
        "url": clean_url,
        "risk": round(final_risk, 2),
        "evidence": inf['evidence'],
        "infra": inf['infra_score']
    }

@app.post("/feedback")
async def log_feedback(req: FeedbackRequest):
    if req.label == 0:
        res = update_whitelist(req.url)
    else:
        res = update_ai_training_set(req.url, label=1)
    return {"status": res}

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
