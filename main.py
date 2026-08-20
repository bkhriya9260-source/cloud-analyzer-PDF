from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from database import init_db
from auth import router as auth_router
from subscriptions import router as sub_router

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs"
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database Schema
init_db()

# Register Core Routers
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(sub_router, prefix=settings.API_V1_PREFIX)

@app.get("/")
def root():
    return {
        "message": "E-Commerce Intelligence Core Engine Online",
        "documentation": "/docs",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "architecture": "FastAPI Async Core Engine"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)