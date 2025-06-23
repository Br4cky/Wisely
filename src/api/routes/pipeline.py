"""
Complete pipeline API endpoint
"""
import sys
sys.path.insert(0, 'src')

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import List
import os
import uuid
import asyncio
from pathlib import Path

from src.services.orchestration.pipeline import ViralContentPipeline

router = APIRouter(prefix="/pipeline", tags=["pipeline"])

@router.post("/process")
async def process_complete_pipeline(
    file: UploadFile = File(...),
    podcaster: str = Form("unknown"),
    platforms: str = Form("tiktok,instagram")
):
    """Process complete viral content pipeline"""
    
    try:
        # Save uploaded file
        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix
        upload_path = Path("data/uploads")
        upload_path.mkdir(exist_ok=True)
        
        file_path = upload_path / f"{file_id}{file_extension}"
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process platforms
        platform_list = [p.strip() for p in platforms.split(',')]
        
        # Run complete pipeline
        pipeline = ViralContentPipeline()
        results = await pipeline.process_audio_file(
            str(file_path), 
            podcaster, 
            platform_list
        )
        
        return {
            "success": results["success"],
            "file_id": file_id,
            "original_filename": file.filename,
            "clips_detected": results["clips_detected"],
            "videos_created": results["videos_created"],
            "output_files": results["output_files"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")

@router.get("/health")
async def pipeline_health():
    return {"status": "healthy", "service": "pipeline"}
