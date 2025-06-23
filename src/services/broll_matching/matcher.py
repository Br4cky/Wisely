"""
B-Roll matching service - finds relevant stock footage
"""
import asyncio
import aiohttp
import json
import os
from typing import List, Dict, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class FootageClip:
    id: str
    url: str
    download_url: str
    title: str
    duration: float
    resolution: str
    source: str
    tags: List[str]
    relevance_score: float

class BRollMatcher:
    def __init__(self):
        self.pexels_api_key = os.getenv('PEXELS_API_KEY')
        self.pixabay_api_key = os.getenv('PIXABAY_API_KEY')
        
        if not self.pexels_api_key:
            print("⚠️  Pexels API key not found")

    async def search_pexels(self, query: str, per_page: int = 10) -> List[FootageClip]:
        """Search Pexels for video footage"""
        if not self.pexels_api_key:
            return []
            
        url = "https://api.pexels.com/videos/search"
        headers = {"Authorization": self.pexels_api_key}
        params = {
            "query": query,
            "per_page": per_page,
            "orientation": "all"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_pexels_response(data.get('videos', []))
        except Exception as e:
            print(f"Pexels API error for '{query}': {e}")
        
        return []

    def _parse_pexels_response(self, videos: List[Dict]) -> List[FootageClip]:
        """Parse Pexels API response"""
        clips = []
        for video in videos:
            try:
                video_files = video.get('video_files', [])
                if not video_files:
                    continue
                    
                best_file = max(video_files, key=lambda x: x.get('width', 0))
                
                clip = FootageClip(
                    id=f"pexels_{video['id']}",
                    url=video.get('url', ''),
                    download_url=best_file.get('link', ''),
                    title=f"Pexels Video {video['id']}",
                    duration=video.get('duration', 10.0),
                    resolution=f"{best_file.get('width')}x{best_file.get('height')}",
                    source='pexels',
                    tags=[],  # Pexels doesn't provide tags
                    relevance_score=0.5  # Default score
                )
                clips.append(clip)
            except Exception as e:
                print(f"Error parsing Pexels video: {e}")
                
        return clips

    async def find_broll_for_keywords(self, keywords: List[str]) -> List[FootageClip]:
        """Find B-roll footage for given keywords"""
        print(f"🎬 Searching for B-roll: {keywords}")
        
        all_footage = []
        
        # Search for each keyword
        for keyword in keywords[:3]:  # Limit to avoid API limits
            footage = await self.search_pexels(keyword)
            all_footage.extend(footage)
        
        # Remove duplicates and sort by relevance
        unique_footage = {clip.id: clip for clip in all_footage}
        sorted_footage = sorted(unique_footage.values(), key=lambda x: x.relevance_score, reverse=True)
        
        print(f"✅ Found {len(sorted_footage)} B-roll clips")
        return sorted_footage[:10]  # Return top 10

# Test function
async def test_broll_matcher():
    matcher = BRollMatcher()
    keywords = ["neuroscience", "brain", "meditation"]
    footage = await matcher.find_broll_for_keywords(keywords)
    
    print(f"Found {len(footage)} clips:")
    for clip in footage[:3]:
        print(f"  - {clip.title} ({clip.source}) - {clip.resolution}")

if __name__ == "__main__":
    asyncio.run(test_broll_matcher())
