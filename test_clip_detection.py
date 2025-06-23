"""
Test script for clip detection
"""
import sys
import os
sys.path.insert(0, 'src')

from src.services.clip_detection.detector import EnhancedClipDetector

def test_with_sample():
    print("🧪 Testing Enhanced Clip Detector...")
    
    # Initialize detector
    try:
        detector = EnhancedClipDetector()
        print("✅ Detector initialized successfully!")
        
        # Test with a sample audio file (you'll need to provide one)
        audio_path = "tests/fixtures/sample_audio.wav"
        
        if not os.path.exists(audio_path):
            print("⚠️  No sample audio file found.")
            print("   Please add a short podcast audio file (.wav or .mp3) to:")
            print(f"   {audio_path}")
            print("\n💡 For testing, you can:")
            print("   1. Download a short podcast clip")
            print("   2. Convert it to .wav format")
            print("   3. Place it in tests/fixtures/")
            return
            
        # Run clip detection
        print(f"🔍 Analyzing audio: {audio_path}")
        clips = detector.detect_clips(audio_path)
        
        print(f"\n🎯 Results:")
        print(f"   Found {len(clips)} potential clips")
        
        for i, clip in enumerate(clips):
            print(f"\n   Clip {i+1}:")
            print(f"   ⏱️  Time: {clip.start_time:.1f}s - {clip.end_time:.1f}s")
            print(f"   📊 Confidence: {clip.confidence_score:.3f}")
            print(f"   🏷️  Keywords: {', '.join(clip.topic_keywords)}")
            print(f"   📝 Text: {clip.transcript[:100]}...")
            
        # Export results
        if clips:
            detector.export_clips_metadata(clips, "test_clips_output.json")
            print("\n✅ Test completed successfully!")
        else:
            print("\n⚠️  No clips detected. This might be normal for very short audio files.")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\n🔧 This might be due to:")
        print("   1. Missing OpenAI API key in .env file")
        print("   2. Audio file format issues")
        print("   3. Missing dependencies")

if __name__ == "__main__":
    test_with_sample()
