#!/usr/bin/env python3
"""
Enhanced ElevenLabs Voice Generation with Detailed Personas
Creates unique voices based on demographics, personality, and regional characteristics
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from dataclasses import asdict
import random
from pathlib import Path
import click
from rich.console import Console
from rich.progress import track
from dotenv import load_dotenv

# Import our persona system
import sys
sys.path.append('../shared')
from persona_system import UnifiedPersona, Ethnicity, Accent, SpeechPattern, PersonaGenerator

load_dotenv()
console = Console()

class ElevenLabsEnhancedGenerator:
    """Enhanced ElevenLabs integration with detailed persona mapping"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        self.persona_generator = PersonaGenerator()
        
        # Pre-defined voice mappings for different persona types
        self.voice_mappings = self._setup_voice_mappings()
        
    def _setup_voice_mappings(self) -> Dict:
        """Map demographic/personality combinations to ElevenLabs voices"""
        return {
            # Male voices with different characteristics
            "male_american_confident": {
                "voice_id": "pNInz6obpgDQGcFmaJgB",  # Adam - confident American
                "name": "Adam",
                "characteristics": ["confident", "professional", "clear"]
            },
            "male_american_analytical": {
                "voice_id": "VR6AewLTigWG4xSOukaG",  # Arnold - deeper, thoughtful
                "name": "Arnold", 
                "characteristics": ["analytical", "measured", "authoritative"]
            },
            "male_british_formal": {
                "voice_id": "rM7mXuQTk96B8Y5Hk3DK",  # Brian - British accent
                "name": "Brian",
                "characteristics": ["formal", "articulate", "british"]
            },
            
            # Female voices with different characteristics  
            "female_american_warm": {
                "voice_id": "XB0fDUnXU5powFXDhCwa",  # Charlotte - warm, friendly
                "name": "Charlotte",
                "characteristics": ["warm", "approachable", "professional"]
            },
            "female_american_energetic": {
                "voice_id": "IKne3meq5aSn9XLyUdCD",  # Freya - energetic, youthful
                "name": "Freya",
                "characteristics": ["energetic", "enthusiastic", "dynamic"]
            },
            "female_british_sophisticated": {
                "voice_id": "XrExE9yKIg1WjnnlVkGX",  # Matilda - British, sophisticated
                "name": "Matilda", 
                "characteristics": ["sophisticated", "articulate", "british"]
            },
            
            # Diverse accent voices
            "male_indian_accent": {
                "voice_id": "pqHfZKP75CvOlQylNhV4",  # Custom or closest match
                "name": "Raj",
                "characteristics": ["indian_accent", "professional", "technical"]
            },
            "female_hispanic_accent": {
                "voice_id": "ThT5KcBeYPX3keUQqHPh",  # Custom or closest match
                "name": "Sofia",
                "characteristics": ["hispanic_accent", "warm", "collaborative"]
            }
        }
    
    def select_voice_for_persona(self, persona: UnifiedPersona) -> Dict[str, Any]:
        """Intelligently select ElevenLabs voice based on persona characteristics"""
        
        # Build selection criteria
        gender = persona.demographics.gender
        accent = persona.demographics.accent.value
        personality = persona.personality_traits
        
        # Score each voice option
        best_voice = None
        best_score = 0
        
        for voice_key, voice_data in self.voice_mappings.items():
            score = 0
            
            # Gender match (high weight)
            if gender in voice_key:
                score += 10
            
            # Accent match (high weight)
            if any(acc in voice_key for acc in [accent, accent.split('_')[0]]):
                score += 8
            elif "american" in voice_key and accent.startswith("american"):
                score += 6
            elif "british" in voice_key and accent == "british":
                score += 8
            
            # Personality match (medium weight)
            personality_matches = [
                trait for trait in personality 
                if any(char in voice_data["characteristics"] for char in [trait, trait.lower()])
            ]
            score += len(personality_matches) * 3
            
            # Speech pattern match (medium weight)
            speech_pattern = persona.voice.speech_pattern.value
            if "confident" in speech_pattern and "confident" in voice_data["characteristics"]:
                score += 4
            elif "analytical" in speech_pattern and "analytical" in voice_data["characteristics"]:
                score += 4
            elif "warm" in speech_pattern and "warm" in voice_data["characteristics"]:
                score += 4
            
            if score > best_score:
                best_score = score
                best_voice = voice_data
        
        # Fallback to default if no good match
        if not best_voice:
            best_voice = self.voice_mappings["male_american_confident" if gender == "male" else "female_american_warm"]
        
        return best_voice
    
    async def create_custom_voice_settings(self, persona: UnifiedPersona, base_voice: Dict) -> Dict:
        """Create custom voice settings based on persona characteristics"""
        
        # Base settings
        settings = {
            "stability": 0.75,
            "similarity_boost": 0.75, 
            "style": 0.0,
            "use_speaker_boost": True
        }
        
        # Adjust based on personality
        if "energetic" in persona.personality_traits:
            settings["stability"] = 0.6  # Less stable = more dynamic
            settings["style"] = 0.3      # More stylistic variation
        elif "analytical" in persona.personality_traits:
            settings["stability"] = 0.9  # Very stable = consistent
            settings["style"] = 0.1      # Minimal stylistic variation
        
        # Adjust based on speech pattern
        if persona.voice.speech_pattern == SpeechPattern.FAST_ENERGETIC:
            settings["style"] = 0.4
        elif persona.voice.speech_pattern == SpeechPattern.SLOW_ANALYTICAL:
            settings["stability"] = 0.95
        
        # Adjust based on role level
        if persona.level <= 2:  # Senior roles
            settings["stability"] = 0.85  # More authoritative consistency
        
        return settings
    
    async def generate_voice_persona_description(self, persona: UnifiedPersona) -> str:
        """Generate description for voice persona creation"""
        
        demo = persona.demographics
        voice = persona.voice
        
        description = f"""
        Professional voice persona for {persona.name}, {persona.role}.
        
        Demographics: {demo.gender.title()}, {demo.age_range} years old, {demo.ethnicity.value} ethnicity.
        Originally from {demo.region_origin}, currently based in {demo.current_location}.
        Accent: {demo.accent.value.replace('_', ' ').title()}
        
        Personality: {', '.join(persona.personality_traits).title()}
        Communication Style: {persona.communication_style.title()}
        
        Voice Characteristics:
        - Speech Pattern: {voice.speech_pattern.value.replace('_', ' ').title()}
        - Pace: {voice.pace.title()} speaking speed
        - Tone: {voice.tone.title()} and {voice.formality.replace('_', ' ')}
        - Pitch: {voice.pitch.title()} pitch range
        - Clarity: {voice.clarity.replace('_', ' ').title()}
        
        This voice should convey {persona.role} authority while maintaining {persona.communication_style} communication.
        Suitable for business meetings, presentations, and professional conversations.
        """
        
        return description.strip()
    
    async def create_elevenlabs_voice(self, persona: UnifiedPersona, 
                                    audio_samples: List[str] = None) -> Optional[str]:
        """Create custom voice in ElevenLabs for this persona (if audio samples provided)"""
        
        if not audio_samples:
            console.print(f"⏭️ No audio samples for {persona.name}, using pre-mapped voice")
            return None
        
        url = f"{self.base_url}/voices/add"
        
        description = await self.generate_voice_persona_description(persona)
        
        # Prepare the request
        data = {
            "name": f"{persona.name}_{persona.persona_id}",
            "description": description,
            "labels": json.dumps({
                "accent": persona.demographics.accent.value,
                "gender": persona.demographics.gender,
                "age": persona.demographics.age_range,
                "role": persona.role,
                "personality": ",".join(persona.personality_traits)
            })
        }
        
        headers = {
            "xi-api-key": self.api_key
        }
        
        # Add audio files (you'd implement file handling here)
        files = {}
        for i, sample_path in enumerate(audio_samples[:25]):  # Max 25 samples
            files[f"files[{i}]"] = open(sample_path, "rb")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        voice_id = result.get("voice_id")
                        console.print(f"✅ Created custom voice for {persona.name}: {voice_id}")
                        return voice_id
                    else:
                        error = await response.text()
                        console.print(f"❌ Failed to create voice for {persona.name}: {error}")
                        return None
        except Exception as e:
            console.print(f"❌ Error creating voice for {persona.name}: {e}")
            return None
        finally:
            # Close file handles
            for file_handle in files.values():
                file_handle.close()
    
    async def generate_speech(self, persona: UnifiedPersona, text: str, 
                            output_path: str, mock: bool = False) -> bool:
        """Generate speech for a specific persona"""
        
        if mock:
            # Create mock audio file
            mock_content = f"[MOCK AUDIO for {persona.name}: {text[:50]}...]"
            with open(output_path, 'w') as f:
                f.write(mock_content)
            return True
        
        # Select appropriate voice
        voice_data = self.select_voice_for_persona(persona)
        voice_id = persona.elevenlabs_voice_id or voice_data["voice_id"]
        
        # Get custom voice settings
        voice_settings = await self.create_custom_voice_settings(persona, voice_data)
        
        # Generate speech
        url = f"{self.base_url}/text-to-speech/{voice_id}"
        
        payload = {
            "text": text,
            "model_id": persona.voice.elevenlabs_model,
            "voice_settings": voice_settings
        }
        
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        audio_content = await response.read()
                        with open(output_path, 'wb') as f:
                            f.write(audio_content)
                        return True
                    else:
                        error = await response.text()
                        console.print(f"❌ Failed to generate speech for {persona.name}: {error}")
                        return False
        except Exception as e:
            console.print(f"❌ Error generating speech for {persona.name}: {e}")
            return False
    
    async def create_persona_voice_mapping(self, personas: List[UnifiedPersona], 
                                         output_dir: str, mock: bool = False) -> Dict:
        """Create voice mappings for all personas"""
        
        console.print(f"🎙️ Creating voice personas for {len(personas)} people...")
        
        voice_mapping = {
            "generation_info": {
                "total_personas": len(personas),
                "elevenlabs_model": "eleven_multilingual_v2",
                "mock_mode": mock
            },
            "personas": {}
        }
        
        for persona in track(personas, description="Creating voice personas..."):
            
            # Select best voice for this persona
            voice_data = self.select_voice_for_persona(persona)
            
            # Get custom settings
            settings = await self.create_custom_voice_settings(persona, voice_data)
            
            # Store mapping
            voice_mapping["personas"][persona.persona_id] = {
                "name": persona.name,
                "role": persona.role,
                "organization_id": persona.organization_id,
                "demographics": {
                    "gender": persona.demographics.gender,
                    "ethnicity": persona.demographics.ethnicity.value,
                    "accent": persona.demographics.accent.value,
                    "age_range": persona.demographics.age_range,
                    "region_origin": persona.demographics.region_origin
                },
                "voice_characteristics": {
                    "speech_pattern": persona.voice.speech_pattern.value,
                    "pace": persona.voice.pace,
                    "tone": persona.voice.tone,
                    "pitch": persona.voice.pitch,
                    "formality": persona.voice.formality
                },
                "elevenlabs_config": {
                    "voice_id": voice_data["voice_id"],
                    "voice_name": voice_data["name"],
                    "model": persona.voice.elevenlabs_model,
                    "settings": settings,
                    "characteristics": voice_data["characteristics"]
                },
                "beyond_presence_ready": True  # Flag for avatar generation
            }
        
        # Save mapping
        mapping_file = Path(output_dir) / "enhanced_voice_mapping.json"
        with open(mapping_file, 'w') as f:
            json.dump(voice_mapping, f, indent=2)
        
        console.print(f"✅ Created enhanced voice mapping for {len(personas)} personas")
        console.print(f"💾 Saved to {mapping_file}")
        
        return voice_mapping

@click.command()
@click.option('--input-dir', required=True, help='Directory with persona JSON files')
@click.option('--output-dir', required=True, help='Output directory for voice files')
@click.option('--mock', is_flag=True, help='Generate mock audio files instead of real ones')
@click.option('--create-samples', is_flag=True, help='Generate sample audio for testing')
def main(input_dir, output_dir, mock, create_samples):
    """Enhanced voice generation with detailed personas"""
    
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key and not mock:
        console.print("❌ ELEVENLABS_API_KEY required for real voice generation")
        console.print("Use --mock flag for development without API key")
        return
    
    # Initialize generator
    generator = ElevenLabsEnhancedGenerator(api_key or "mock")
    
    # Load personas (you'd implement persona loading from your unified format)
    # For now, create sample personas
    persona_gen = PersonaGenerator()
    
    sample_personas = [
        persona_gen.create_unified_persona("org_001", 1, "Rajesh Patel", "VP Engineering", 2, 
                                         ["analytical", "collaborative"]),
        persona_gen.create_unified_persona("org_001", 2, "Sarah Johnson", "Marketing Director", 3,
                                         ["energetic", "creative"]),
        persona_gen.create_unified_persona("org_001", 3, "Miguel Rodriguez", "Sales Manager", 3,
                                         ["confident", "persuasive"])
    ]
    
    # Run generation
    asyncio.run(generate_enhanced_voices(generator, sample_personas, output_dir, mock, create_samples))

async def generate_enhanced_voices(generator, personas, output_dir, mock, create_samples):
    """Main generation logic"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Create voice mappings
    voice_mapping = await generator.create_persona_voice_mapping(personas, output_dir, mock)
    
    # Generate sample audio if requested
    if create_samples:
        console.print("🎙️ Generating sample audio files...")
        
        sample_text = "Hello, this is a test of the enhanced voice generation system. I'm speaking as my professional persona for business meetings and presentations."
        
        for persona in personas:
            output_file = Path(output_dir) / f"sample_{persona.persona_id}.mp3"
            success = await generator.generate_speech(persona, sample_text, str(output_file), mock)
            
            if success:
                console.print(f"✅ Generated sample for {persona.name}")
            else:
                console.print(f"❌ Failed to generate sample for {persona.name}")
    
    console.print(f"\n🎯 Enhanced voice generation complete!")
    console.print(f"📊 Generated {len(personas)} voice personas")
    console.print(f"💾 Voice mapping saved to {output_dir}/enhanced_voice_mapping.json")

if __name__ == "__main__":
    main()