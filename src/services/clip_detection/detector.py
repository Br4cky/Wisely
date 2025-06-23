"""
Enhanced clip detection service
"""
import os
import json
import re
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import numpy as np

# Check if we have the required packages
try:
    import whisper
    import librosa
    import torch
    import openai
    from textstat import flesch_reading_ease
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Missing dependency: {e}")
    DEPENDENCIES_AVAILABLE = False

@dataclass
class ClipCandidate:
    start_time: float
    end_time: float
    transcript: str
    confidence_score: float
    viral_indicators: Dict[str, float]
    topic_keywords: List[str]
    speaker_energy: float
    emotional_intensity: float

class EnhancedClipDetector:
    def __init__(self):
        """Initialize the enhanced clip detection system"""
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError("Missing required dependencies. Install with: pip install openai-whisper librosa torch openai textstat")
        
        # Load environment variables
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        # Initialize models
        print("🤖 Loading Whisper model...")
        self.whisper_model = whisper.load_model("base")  # Use base model for faster testing
        
        print("🔗 Connecting to OpenAI...")
        self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
        
        # Viral patterns from your original code
        self.viral_patterns = {
            'shocking_statements': [
                r'\b(shocking|unbelievable|incredible|mind-blowing|crazy|insane)\b',
                r'\b(never seen|first time|groundbreaking|revolutionary)\b',
                r'\b(secret|hidden|revealed|exposed|truth)\b'
            ],
            'controversial_topics': [
                r'\b(controversial|debate|disagree|argue|conflict)\b',
                r'\b(wrong|mistake|lie|fake|scam)\b',
                r'\b(banned|censored|forbidden|illegal)\b'
            ],
            'actionable_advice': [
                r'\b(should|must|need to|have to|tip|trick|hack)\b',
                r'\b(how to|steps|method|technique|strategy)\b',
                r'\b(avoid|prevent|fix|solve|improve)\b'
            ]
        }

    def detect_clips(self, audio_path: str, min_duration: float = 15.0, max_duration: float = 90.0) -> List[ClipCandidate]:
        """Main function to detect viral clip candidates"""
        print("🎙️ Transcribing audio...")
        
        try:
            # Transcribe audio
            result = self.whisper_model.transcribe(audio_path)
            
            # Simple clip detection for testing
            full_text = result['text']
            duration = len(full_text.split()) / 3  # Rough estimate: 3 words per second
            
            if duration < min_duration:
                print("⚠️  Audio too short for clip detection")
                return []
            
            # Create a simple test clip
            viral_scores = self.score_viral_potential(full_text)
            keywords = self.extract_topic_keywords(full_text)
            
            confidence = sum(viral_scores.values()) / len(viral_scores)
            
            clip = ClipCandidate(
                start_time=0.0,
                end_time=min(duration, max_duration),
                transcript=full_text[:200] + "..." if len(full_text) > 200 else full_text,
                confidence_score=confidence,
                viral_indicators=viral_scores,
                topic_keywords=keywords,
                speaker_energy=0.5,
                emotional_intensity=viral_scores.get('emotional_intensity', 0.0)
            )
            
            return [clip] if confidence > 0.3 else []
            
        except Exception as e:
            print(f"❌ Error during clip detection: {str(e)}")
            return []

    def score_viral_potential(self, text: str) -> Dict[str, float]:
        """Score the viral potential of a text segment"""
        scores = {
            'pattern_matches': 0.0,
            'emotional_intensity': 0.0,
            'length_score': 0.0,
            'readability': 0.0
        }
        
        text_lower = text.lower()
        
        # Pattern matching
        total_matches = 0
        for category, patterns in self.viral_patterns.items():
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower))
                total_matches += matches
        scores['pattern_matches'] = min(total_matches / 10.0, 1.0)
        
        # Emotional intensity
        emotional_indicators = text.count('!') + len(re.findall(r'[A-Z]{2,}', text))
        scores['emotional_intensity'] = min(emotional_indicators / 5.0, 1.0)
        
        # Length score
        word_count = len(text.split())
        if 20 <= word_count <= 100:
            scores['length_score'] = 1.0
        else:
            scores['length_score'] = 0.5
        
        # Readability
        try:
            flesch_score = flesch_reading_ease(text)
            scores['readability'] = min(flesch_score / 100.0, 1.0)
        except:
            scores['readability'] = 0.5
        
        return scores

    def extract_topic_keywords(self, text: str) -> List[str]:
        """Extract key topics for B-roll matching"""
        try:
            prompt = f"Extract 3-5 key visual topics from this text for B-roll footage. Return only keywords separated by commas:\n\n{text[:500]}"
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use cheaper model for testing
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.3
            )
            
            keywords = [k.strip() for k in response.choices[0].message.content.split(',')]
            return keywords[:5]
            
        except Exception as e:
            print(f"⚠️  Keyword extraction failed: {e}")
            return ['conversation', 'podcast', 'discussion']

    def export_clips_metadata(self, candidates: List[ClipCandidate], output_path: str):
        """Export clip metadata to JSON"""
        clips_data = []
        for i, candidate in enumerate(candidates):
            clips_data.append({
                'id': f'clip_{i+1}',
                'start_time': candidate.start_time,
                'end_time': candidate.end_time,
                'duration': candidate.end_time - candidate.start_time,
                'transcript': candidate.transcript,
                'confidence_score': candidate.confidence_score,
                'viral_indicators': candidate.viral_indicators,
                'topic_keywords': candidate.topic_keywords,
                'speaker_energy': candidate.speaker_energy,
                'emotional_intensity': candidate.emotional_intensity
            })
        
        with open(output_path, 'w') as f:
            json.dump(clips_data, f, indent=2)
        
        print(f"📄 Clip metadata exported to {output_path}")
