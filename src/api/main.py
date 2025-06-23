import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import route modules
from src.api.routes.upload import router as upload_router

app = FastAPI(
    title="Viral Content Automation API",
    description="AI-powered viral content creation system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload_router)

@app.get("/")
async def root():
    return {
        "message": "🎬 Viral Content Automation API",
        "status": "online",
        "version": "1.0.0",
        "features": [
            "AI Clip Detection",
            "B-Roll Matching", 
            "Video Processing Ready"
        ],
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2024-01-01"}
