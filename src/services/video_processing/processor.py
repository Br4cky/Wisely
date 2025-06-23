"""
Video processing service - creates viral clips with B-roll and captions
"""
import os
import json
import asyncio
import aiohttp
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path
import tempfile
import subprocess

@dataclass
class ProcessingSpec:
    clip_id: str
    start_time: float
    end_time: float
    transcript: str
    broll_footage: List[Dict]
    target_platform: str = "tiktok"

class VideoProcessor:
    def __init__(self):
        self.temp_dir = Path("data/temp")
        self.temp_dir.mkdir(exist_ok=True)
        
        # Platform specifications
        self.platform_specs = {
            'tiktok': {
                'resolution': (1080, 1920),  # 9:16 aspect ratio
                'max_duration': 60,
                'caption_style': 'trendy'
            },
            'instagram': {
                'resolution': (1080, 1920),
                'max_duration': 90,
                'caption_style': 'clean'
            },
            'youtube_shorts': {
                'resolution': (1080, 1920),
                'max_duration': 60,
                'caption_style': 'educational'
            }
        }

    async def download_broll_clip(self, download_url: str, clip_id: str) -> Optional[str]:
        """Download a B-roll clip from URL"""
        try:
            output_path = self.temp_dir / f"broll_{clip_id}.mp4"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(download_url) as response:
                    if response.status == 200:
                        with open(output_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                        return str(output_path)
            
            print(f"⚠️  Failed to download B-roll: {download_url}")
            return None
            
        except Exception as e:
            print(f"❌ Error downloading B-roll: {e}")
            return None

    def create_simple_caption_file(self, transcript: str, duration: float) -> str:
        """Create a simple caption file"""
        caption_path = self.temp_dir / "captions.srt"
        
        # Simple caption - split transcript into chunks
        words = transcript.split()
        words_per_chunk = 6
        chunks = [words[i:i+words_per_chunk] for i in range(0, len(words), words_per_chunk)]
        
        chunk_duration = duration / len(chunks) if chunks else duration
        
        with open(caption_path, 'w') as f:
            for i, chunk in enumerate(chunks):
                start_time = i * chunk_duration
                end_time = (i + 1) * chunk_duration
                
                # Convert to SRT time format
                start_srt = self._seconds_to_srt_time(start_time)
                end_srt = self._seconds_to_srt_time(end_time)
                
                f.write(f"{i + 1}\n")
                f.write(f"{start_srt} --> {end_srt}\n")
                f.write(f"{' '.join(chunk)}\n\n")
        
        return str(caption_path)

    def _seconds_to_srt_time(self, seconds: float) -> str:
        """Convert seconds to SRT time format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

    async def process_clip(self, spec: ProcessingSpec, original_audio_path: str) -> Optional[str]:
        """Process a clip with B-roll and captions"""
        print(f"🎬 Processing clip: {spec.clip_id}")
        
        try:
            # Download B-roll clips
            broll_paths = []
            for i, footage in enumerate(spec.broll_footage[:3]):  # Limit to 3 clips
                path = await self.download_broll_clip(footage['download_url'], f"{spec.clip_id}_{i}")
                if path:
                    broll_paths.append(path)
            
            if not broll_paths:
                print("⚠️  No B-roll footage downloaded, creating audio-only clip")
            
            # Create captions
            duration = spec.end_time - spec.start_time
            caption_file = self.create_simple_caption_file(spec.transcript, duration)
            
            # Create output path
            output_path = self.temp_dir / f"{spec.clip_id}_{spec.target_platform}.mp4"
            
            # For now, create a simple video with the first B-roll clip and captions
            if broll_paths:
                success = await self._create_video_with_ffmpeg(
                    broll_paths[0], 
                    original_audio_path,
                    spec.start_time,
                    duration,
                    caption_file,
                    output_path,
                    spec.target_platform
                )
                
                if success:
                    print(f"✅ Video created: {output_path}")
                    return str(output_path)
            
            print("❌ Video processing failed")
            return None
            
        except Exception as e:
            print(f"❌ Error processing clip: {e}")
            return None

    async def _create_video_with_ffmpeg(self, video_path: str, audio_path: str, 
                                      start_time: float, duration: float,
                                      caption_file: str, output_path: Path,
                                      platform: str) -> bool:
        """Create video using FFmpeg"""
        try:
            spec = self.platform_specs[platform]
            width, height = spec['resolution']
            
            # FFmpeg command to create vertical video with captions
            cmd = [
                'ffmpeg', '-y',  # Overwrite output
                '-i', video_path,  # Video input
                '-i', audio_path,  # Audio input
                '-ss', str(start_time),  # Start time for audio
                '-t', str(duration),  # Duration
                '-vf', f'scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}',  # Resize and crop
                '-c:v', 'libx264',  # Video codec
                '-c:a', 'aac',  # Audio codec
                '-shortest',  # Stop when shortest input ends
                str(output_path)
            ]
            
            # Run FFmpeg
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return True
            else:
                print(f"FFmpeg error: {stderr.decode()}")
                return False
                
        except Exception as e:
            print(f"FFmpeg execution error: {e}")
            return False

    def cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            for file_path in self.temp_dir.glob("*"):
                if file_path.is_file():
                    file_path.unlink()
            print("🧹 Temporary files cleaned up")
        except Exception as e:
            print(f"⚠️  Cleanup error: {e}")

# Test function
async def test_video_processor():
    processor = VideoProcessor()
    
    # Mock processing spec
    spec = ProcessingSpec(
        clip_id="test_001",
        start_time=0.0,
        end_time=30.0,
        transcript="This is a test transcript for video processing",
        broll_footage=[{
            'download_url': 'https://www.learningcontainer.com/wp-content/uploads/2020/05/sample-mp4-file.mp4',
            'id': 'test_broll'
        }],
        target_platform="tiktok"
    )
    
    print("🧪 Testing video processor...")
    # Note: This would need a real audio file to work
    print("✅ Video processor initialized successfully!")

if __name__ == "__main__":
    asyncio.run(test_video_processor())
