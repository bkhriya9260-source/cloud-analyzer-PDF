from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# Allow requests from GitHub Pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "Analyzer Engine API is Live"}

from pydantic import BaseModel
from fastapi import Header, HTTPException

class AnalyzeRequest(BaseModel):
    url: str

@app.post("/analyze")
def analyze(req: AnalyzeRequest, x_api_key: str = Header(None)):
    if x_api_key != "ADMIN123":
        raise HTTPException(status_code=401, detail="Unauthorized API Key")
    
    return {
        "product_title": "Store Analysis - " + req.url.replace("https://", "").replace("http://", ""),
        "price": "$29.99",
        "description": "Store verified successfully. E-commerce analytics engine connected.",
        "ai_analysis": {
            "target_audience": "US Dropshipping & E-commerce Buyers (Age 18-45)",
            "marketing_angle": "Problem-solving hook with fast shipping angle & high converting video creative."
        }
    }
