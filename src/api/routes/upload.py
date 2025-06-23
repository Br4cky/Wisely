"""
Upload endpoints for viral content automation
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import List
import os
import sys
import uuid
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from services.clip_detection.detector import EnhancedClipDetector

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("/analyze")
async def analyze_audio(
    file: UploadFile = File(...),
    podcaster: str = Form("unknown")
):
    """Upload and analyze an audio file for viral clips"""
    
    # Validate file type
    if not file.filename.lower().endswith(('.wav', '.mp3', '.m4a', '.mp4')):
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Please upload an audio file (.wav, .mp3, .m4a, .mp4)"
        )
    
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
        
        # Initialize detector and analyze
        detector = EnhancedClipDetector()
        clips = detector.detect_clips(str(file_path))
        
        # Prepare response
        results = []
        for i, clip in enumerate(clips):
            results.append({
                "clip_id": f"{file_id}_clip_{i+1}",
                "start_time": clip.start_time,
                "end_time": clip.end_time,
                "duration": clip.end_time - clip.start_time,
                "confidence_score": clip.confidence_score,
                "transcript": clip.transcript,
                "keywords": clip.topic_keywords,
                "viral_indicators": clip.viral_indicators
            })
        
        return {
            "success": True,
            "file_id": file_id,
            "original_filename": file.filename,
            "podcaster": podcaster,
            "clips_found": len(clips),
            "clips": results
        }
        
    except Exception as e:
        # Clean up file if error
        if 'file_path' in locals() and file_path.exists():
            file_path.unlink()
            
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/health")
async def upload_health():
    """Health check for upload service"""
    return {"status": "healthy", "service": "upload"}
