import os
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import google.generativeai as genai

app = FastAPI(title="Cloud Web Deep Analyzer")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
else:
    model = None

class AnalysisRequest(BaseModel):
    url: str

@app.get("/")
def home():
    return {"status": "online", "message": "Cloud Analyzer API Ready!"}

@app.post("/analyze")
async def analyze_url(payload: AnalysisRequest):
    if not model:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY Missing!")

    url = payload.url
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = await context.new_page()
            await page.goto(url, wait_until="networkidle", timeout=60000)
            content = await page.content()
            await browser.close()

        soup = BeautifulSoup(content, "html.parser")
        for element in soup(["script", "style", "nav", "footer", "iframe", "noscript"]):
            element.extract()

        clean_text = soup.get_text(separator=" ", strip=True)[:10000]

        prompt = f"""
Aapko is website ke extracted text ka deep analysis karna hai.
1. Purpose & Overview
2. Key Products/Services
3. Pricing Structure & Offers
4. Target Audience
5. Key Strengths & Weaknesses

Content:
{clean_text}
"""
        response = model.generate_content(prompt)
        return {"status": "success", "url": url, "deep_analysis": response.text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))