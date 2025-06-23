"""
Complete pipeline orchestrator - ties everything together
"""
import asyncio
import json
from pathlib import Path
from typing import List, Dict, Optional

from src.services.clip_detection.detector import EnhancedClipDetector
from src.services.broll_matching.matcher import BRollMatcher
from src.services.video_processing.processor import VideoProcessor, ProcessingSpec

class ViralContentPipeline:
    def __init__(self):
        self.clip_detector = EnhancedClipDetector()
        self.broll_matcher = BRollMatcher()
        self.video_processor = VideoProcessor()

    async def process_audio_file(self, audio_path: str, podcaster: str = "unknown", 
                               target_platforms: List[str] = ["tiktok"]) -> Dict:
        """Complete pipeline: audio → clips → B-roll → videos"""
        
        print(f"🚀 Starting viral content pipeline for: {audio_path}")
        results = {
            "success": False,
            "audio_path": audio_path,
            "podcaster": podcaster,
            "clips_detected": 0,
            "videos_created": 0,
            "output_files": []
        }
        
        try:
            # Step 1: Detect viral clips
            print("\n🎯 Step 1: Detecting viral clips...")
            clips = self.clip_detector.detect_clips(audio_path)
            results["clips_detected"] = len(clips)
            
            if not clips:
                print("⚠️  No viral clips detected")
                return results
            
            print(f"✅ Found {len(clips)} potential viral clips")
            
            # Step 2: Process each clip
            for i, clip in enumerate(clips[:3]):  # Process top 3 clips
                print(f"\n🎬 Step 2.{i+1}: Processing clip {i+1}")
                
                # Find B-roll footage
                print("  🎞️  Finding B-roll footage...")
                broll_footage = await self.broll_matcher.find_broll_for_keywords(clip.topic_keywords)
                
                if not broll_footage:
                    print("  ⚠️  No B-roll footage found, skipping clip")
                    continue
                
                # Convert footage to dict format
                broll_data = [
                    {
                        'id': footage.id,
                        'download_url': footage.download_url,
                        'title': footage.title,
                        'duration': footage.duration
                    }
                    for footage in broll_footage[:3]
                ]
                
                # Process for each platform
                for platform in target_platforms:
                    print(f"  📱 Creating {platform} video...")
                    
                    spec = ProcessingSpec(
                        clip_id=f"clip_{i+1}_{platform}",
                        start_time=clip.start_time,
                        end_time=clip.end_time,
                        transcript=clip.transcript,
                        broll_footage=broll_data,
                        target_platform=platform
                    )
                    
                    video_path = await self.video_processor.process_clip(spec, audio_path)
                    
                    if video_path:
                        results["output_files"].append({
                            "clip_number": i + 1,
                            "platform": platform,
                            "video_path": video_path,
                            "confidence_score": clip.confidence_score,
                            "transcript": clip.transcript[:100] + "...",
                            "keywords": clip.topic_keywords
                        })
                        results["videos_created"] += 1
                        print(f"  ✅ {platform} video created!")
                    else:
                        print(f"  ❌ {platform} video failed")
            
            results["success"] = results["videos_created"] > 0
            
            # Export summary
            summary_path = Path("data/processed") / f"pipeline_results_{Path(audio_path).stem}.json"
            summary_path.parent.mkdir(exist_ok=True)
            
            with open(summary_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"\n🎉 Pipeline complete! Created {results['videos_created']} videos")
            print(f"📄 Results saved to: {summary_path}")
            
            return results
            
        except Exception as e:
            print(f"❌ Pipeline error: {e}")
            results["error"] = str(e)
            return results
        
        finally:
            # Cleanup
            self.video_processor.cleanup_temp_files()

# Test function
async def test_pipeline():
    pipeline = ViralContentPipeline()
    print("🧪 Testing complete pipeline...")
    print("✅ Pipeline initialized successfully!")
    print("\n💡 To test with real audio:")
    print("   pipeline = ViralContentPipeline()")
    print("   results = await pipeline.process_audio_file('your_audio.wav')")

if __name__ == "__main__":
    asyncio.run(test_pipeline())
