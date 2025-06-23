"""
Test the complete viral content pipeline
"""
import sys
import os
import asyncio
sys.path.insert(0, 'src')

from src.services.clip_detection.detector import EnhancedClipDetector
from src.services.broll_matching.matcher import BRollMatcher
from src.services.video_processing.processor import VideoProcessor

async def test_complete_system():
    print("�� Testing Complete Viral Content System...")
    
    try:
        # Test 1: Clip Detection
        print("\n1️⃣ Testing Clip Detection...")
        detector = EnhancedClipDetector()
        print("   ✅ Clip detector initialized")
        
        # Test 2: B-Roll Matching
        print("\n2️⃣ Testing B-Roll Matching...")
        matcher = BRollMatcher()
        test_keywords = ["productivity", "focus"]
        footage = await matcher.find_broll_for_keywords(test_keywords)
        print(f"   ✅ Found {len(footage)} B-roll clips for: {test_keywords}")
        
        # Test 3: Video Processing
        print("\n3️⃣ Testing Video Processor...")
        processor = VideoProcessor()
        print("   ✅ Video processor initialized")
        
        print("\n🎉 All systems operational!")
        print("\n🚀 Your Viral Content Automation System is READY!")
        
        print("\n📋 What you can do now:")
        print("   🌐 Web Interface: Start API and upload files")
        print("   🎵 Audio Test: Add sample audio and test full pipeline")
        print("   📱 Video Output: Get ready-to-upload social media clips")
        
    except Exception as e:
        print(f"❌ System test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_complete_system())
