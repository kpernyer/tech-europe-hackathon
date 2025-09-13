#!/usr/bin/env python3
"""
Unified Persona System
Creates consistent person identities across text, voice, and avatar generation
"""

import uuid
import hashlib
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from enum import Enum
import random

class Ethnicity(Enum):
    CAUCASIAN = "caucasian"
    AFRICAN_AMERICAN = "african_american"  
    HISPANIC = "hispanic"
    ASIAN_EAST = "asian_east"
    ASIAN_SOUTH = "asian_south"  # Indian subcontinent
    MIDDLE_EASTERN = "middle_eastern"
    NATIVE_AMERICAN = "native_american"
    MIXED = "mixed"

class Accent(Enum):
    AMERICAN_GENERAL = "american_general"
    AMERICAN_SOUTHERN = "american_southern"
    AMERICAN_NEW_YORK = "american_new_york"
    AMERICAN_CALIFORNIA = "american_california"
    BRITISH = "british"
    AUSTRALIAN = "australian"
    CANADIAN = "canadian"
    INDIAN = "indian"
    CHINESE = "chinese"
    GERMAN = "german"
    FRENCH = "french"
    SPANISH = "spanish"
    ITALIAN = "italian"
    RUSSIAN = "russian"
    JAPANESE = "japanese"
    KOREAN = "korean"

class SpeechPattern(Enum):
    FAST_ENERGETIC = "fast_energetic"
    MODERATE_STEADY = "moderate_steady"
    SLOW_ANALYTICAL = "slow_analytical"
    HESITANT_THOUGHTFUL = "hesitant_thoughtful"
    CONFIDENT_ASSERTIVE = "confident_assertive"
    WARM_CONVERSATIONAL = "warm_conversational"
    FORMAL_PRECISE = "formal_precise"
    CASUAL_RELAXED = "casual_relaxed"

@dataclass
class PersonaDemographics:
    ethnicity: Ethnicity
    accent: Accent
    age_range: str  # "25-35", "35-45", etc.
    gender: str     # "male", "female", "non-binary"
    region_origin: str  # Where they're from originally
    current_location: str  # Where they work now

@dataclass
class PersonaVoice:
    speech_pattern: SpeechPattern
    pace: str           # "fast", "moderate", "slow"
    pitch: str          # "high", "medium", "low"  
    tone: str           # "warm", "professional", "energetic", "calm"
    volume: str         # "loud", "medium", "soft"
    clarity: str        # "very_clear", "clear", "slightly_mumbled"
    formality: str      # "formal", "business_casual", "informal"
    
    # ElevenLabs specific
    elevenlabs_voice_id: Optional[str] = None
    elevenlabs_model: str = "eleven_multilingual_v2"
    voice_settings: Dict = None

@dataclass  
class PersonaAvatar:
    # Beyond Presence avatar characteristics
    avatar_id: Optional[str] = None
    appearance_style: str = "professional"  # professional, casual, creative
    body_language: str = "confident"        # confident, relaxed, energetic, reserved
    gesture_frequency: str = "moderate"     # high, moderate, low
    eye_contact_style: str = "direct"       # direct, moderate, occasional
    posture: str = "upright"               # upright, relaxed, forward_leaning
    
    # Physical characteristics for avatar generation
    hair_color: str = "brown"
    hair_style: str = "professional"
    eye_color: str = "brown"  
    clothing_style: str = "business_professional"
    accessories: List[str] = None

@dataclass
class UnifiedPersona:
    # Core Identity (consistent across all systems)
    persona_id: str                    # UNIQUE ID: "persona_org001_p0001" 
    organization_id: str               # Which org they belong to
    name: str                         # Full name
    role: str                         # Job title
    level: int                        # Hierarchy level (1=CEO, 5=junior)
    
    # Demographics & Background
    demographics: PersonaDemographics
    
    # Personality & Communication Style
    personality_traits: List[str]      # ["analytical", "collaborative", "decisive"]
    communication_style: str           # "direct", "diplomatic", "collaborative"
    decision_making_style: str         # "quick", "analytical", "consultative"
    stress_response: str               # "calm", "urgent", "detailed"
    
    # Voice Generation Data
    voice: PersonaVoice
    
    # Avatar Generation Data  
    avatar: PersonaAvatar
    
    # System Integration IDs
    elevenlabs_voice_id: Optional[str] = None
    beyond_presence_avatar_id: Optional[str] = None
    
    def __post_init__(self):
        """Initialize default values if not provided"""
        if self.avatar.accessories is None:
            self.avatar.accessories = []
        if self.voice.voice_settings is None:
            self.voice.voice_settings = {
                "stability": 0.75,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            }

class PersonaGenerator:
    """Generates unified personas with consistent characteristics"""
    
    def __init__(self):
        self.ethnicity_demographics = self._setup_demographic_mappings()
        
    def _setup_demographic_mappings(self) -> Dict:
        """Map ethnicities to likely accents and regions"""
        return {
            Ethnicity.CAUCASIAN: {
                "accents": [Accent.AMERICAN_GENERAL, Accent.AMERICAN_SOUTHERN, Accent.AMERICAN_NEW_YORK, 
                           Accent.BRITISH, Accent.AUSTRALIAN, Accent.CANADIAN],
                "regions": ["United States", "United Kingdom", "Canada", "Australia", "Germany", "France"]
            },
            Ethnicity.AFRICAN_AMERICAN: {
                "accents": [Accent.AMERICAN_GENERAL, Accent.AMERICAN_SOUTHERN],
                "regions": ["United States", "United Kingdom", "Canada"]
            },
            Ethnicity.HISPANIC: {
                "accents": [Accent.AMERICAN_GENERAL, Accent.SPANISH],
                "regions": ["United States", "Mexico", "Spain", "Argentina", "Colombia"]
            },
            Ethnicity.ASIAN_SOUTH: {
                "accents": [Accent.INDIAN, Accent.AMERICAN_GENERAL, Accent.BRITISH],
                "regions": ["India", "Pakistan", "Bangladesh", "United States", "United Kingdom"]
            },
            Ethnicity.ASIAN_EAST: {
                "accents": [Accent.CHINESE, Accent.JAPANESE, Accent.KOREAN, Accent.AMERICAN_GENERAL],
                "regions": ["China", "Japan", "Korea", "Taiwan", "United States"]
            },
            Ethnicity.MIDDLE_EASTERN: {
                "accents": [Accent.AMERICAN_GENERAL, Accent.BRITISH],
                "regions": ["United States", "United Kingdom", "UAE", "Lebanon", "Iran"]
            }
        }
    
    def generate_persona_id(self, org_id: str, person_index: int) -> str:
        """Generate unique persona ID: persona_org001_p0001"""
        return f"persona_{org_id}_p{person_index:04d}"
    
    def generate_demographics(self, name: str, region_bias: str = None) -> PersonaDemographics:
        """Generate realistic demographics based on name and region"""
        
        # Simple ethnicity inference from name (you'd use a proper library in production)
        ethnicity = self._infer_ethnicity_from_name(name)
        
        # Get demographic data for this ethnicity
        demo_data = self.ethnicity_demographics.get(ethnicity, self.ethnicity_demographics[Ethnicity.CAUCASIAN])
        
        # Choose accent and region
        accent = random.choice(demo_data["accents"])
        region_origin = random.choice(demo_data["regions"])
        
        # Age range based on role level (you'd pass this in)
        age_ranges = ["25-35", "30-40", "35-45", "40-50", "45-55", "50-60"]
        age_range = random.choice(age_ranges)
        
        # Gender inference (very basic - you'd use a proper library)
        gender = self._infer_gender_from_name(name)
        
        return PersonaDemographics(
            ethnicity=ethnicity,
            accent=accent,
            age_range=age_range,
            gender=gender,
            region_origin=region_origin,
            current_location=region_bias or "United States"
        )
    
    def generate_voice_characteristics(self, demographics: PersonaDemographics, 
                                     personality: List[str], role_level: int) -> PersonaVoice:
        """Generate voice characteristics based on demographics and personality"""
        
        # Speech pattern based on personality
        speech_pattern = SpeechPattern.MODERATE_STEADY
        if "analytical" in personality:
            speech_pattern = SpeechPattern.SLOW_ANALYTICAL
        elif "energetic" in personality:
            speech_pattern = SpeechPattern.FAST_ENERGETIC
        elif "confident" in personality:
            speech_pattern = SpeechPattern.CONFIDENT_ASSERTIVE
        elif "collaborative" in personality:
            speech_pattern = SpeechPattern.WARM_CONVERSATIONAL
        
        # Pace based on demographics and personality
        pace = "moderate"
        if demographics.accent in [Accent.AMERICAN_NEW_YORK]:
            pace = "fast"
        elif demographics.accent in [Accent.AMERICAN_SOUTHERN]:
            pace = "slow"
        elif "energetic" in personality:
            pace = "fast"
        elif "analytical" in personality:
            pace = "slow"
        
        # Pitch based on demographics
        pitch = "medium"
        if demographics.gender == "female":
            pitch = random.choice(["medium", "high"])
        elif demographics.gender == "male":
            pitch = random.choice(["low", "medium"])
        
        # Tone based on role level and personality
        tone = "professional"
        if role_level <= 2:  # Senior roles
            tone = "confident"
        elif "warm" in personality:
            tone = "warm"
        elif "energetic" in personality:
            tone = "energetic"
        
        # Formality based on role level
        formality = "business_casual"
        if role_level == 1:  # CEO
            formality = "formal"
        elif role_level >= 4:  # Junior roles
            formality = "informal"
        
        return PersonaVoice(
            speech_pattern=speech_pattern,
            pace=pace,
            pitch=pitch,
            tone=tone,
            volume="medium",
            clarity="clear",
            formality=formality,
            elevenlabs_model="eleven_multilingual_v2"
        )
    
    def generate_avatar_characteristics(self, demographics: PersonaDemographics,
                                      personality: List[str], role_level: int) -> PersonaAvatar:
        """Generate avatar characteristics for Beyond Presence"""
        
        # Appearance style based on role level
        appearance_style = "professional"
        if role_level <= 2:
            appearance_style = "executive"
        elif "creative" in personality:
            appearance_style = "creative"
        
        # Body language based on personality
        body_language = "confident"
        if "energetic" in personality:
            body_language = "energetic"
        elif "collaborative" in personality:
            body_language = "approachable"
        elif "analytical" in personality:
            body_language = "reserved"
        
        # Gesture frequency based on demographics and personality
        gesture_frequency = "moderate"
        if demographics.ethnicity in [Ethnicity.HISPANIC, Ethnicity.MIDDLE_EASTERN]:
            gesture_frequency = "high"
        elif demographics.accent == Accent.AMERICAN_NEW_YORK:
            gesture_frequency = "high"
        elif "energetic" in personality:
            gesture_frequency = "high"
        elif "analytical" in personality:
            gesture_frequency = "low"
        
        # Clothing style based on role level
        clothing_style = "business_professional"
        if role_level == 1:
            clothing_style = "executive_formal"
        elif role_level >= 4:
            clothing_style = "business_casual"
        elif "creative" in personality:
            clothing_style = "smart_casual"
        
        return PersonaAvatar(
            appearance_style=appearance_style,
            body_language=body_language,
            gesture_frequency=gesture_frequency,
            eye_contact_style="direct" if "confident" in personality else "moderate",
            posture="upright" if role_level <= 3 else "relaxed",
            hair_color=self._hair_color_for_ethnicity(demographics.ethnicity),
            hair_style="professional",
            eye_color=self._eye_color_for_ethnicity(demographics.ethnicity),
            clothing_style=clothing_style,
            accessories=self._accessories_for_role(role_level)
        )
    
    def create_unified_persona(self, org_id: str, person_index: int, name: str, 
                             role: str, level: int, personality: List[str],
                             region_bias: str = None) -> UnifiedPersona:
        """Create a complete unified persona"""
        
        persona_id = self.generate_persona_id(org_id, person_index)
        demographics = self.generate_demographics(name, region_bias)
        voice = self.generate_voice_characteristics(demographics, personality, level)
        avatar = self.generate_avatar_characteristics(demographics, personality, level)
        
        return UnifiedPersona(
            persona_id=persona_id,
            organization_id=org_id,
            name=name,
            role=role,
            level=level,
            demographics=demographics,
            personality_traits=personality,
            communication_style=self._communication_style_from_personality(personality),
            decision_making_style=self._decision_style_from_personality(personality),
            stress_response=self._stress_response_from_personality(personality),
            voice=voice,
            avatar=avatar
        )
    
    # Helper methods
    def _infer_ethnicity_from_name(self, name: str) -> Ethnicity:
        """Basic ethnicity inference - you'd use a proper library in production"""
        name_lower = name.lower()
        
        # Very basic patterns - replace with proper name database
        if any(indicator in name_lower for indicator in ['raj', 'patel', 'singh', 'kumar', 'shah']):
            return Ethnicity.ASIAN_SOUTH
        elif any(indicator in name_lower for indicator in ['chen', 'wang', 'li', 'zhang', 'liu']):
            return Ethnicity.ASIAN_EAST
        elif any(indicator in name_lower for indicator in ['rodriguez', 'martinez', 'lopez', 'garcia']):
            return Ethnicity.HISPANIC
        elif any(indicator in name_lower for indicator in ['johnson', 'washington', 'williams', 'brown', 'jackson']):
            return Ethnicity.AFRICAN_AMERICAN
        else:
            return Ethnicity.CAUCASIAN
    
    def _infer_gender_from_name(self, name: str) -> str:
        """Basic gender inference - you'd use a proper library in production"""
        first_name = name.split()[0].lower()
        
        # Very basic patterns
        female_indicators = ['sarah', 'jennifer', 'mary', 'lisa', 'michelle', 'stephanie', 'rachel']
        male_indicators = ['john', 'michael', 'david', 'james', 'robert', 'william', 'richard']
        
        if first_name in female_indicators:
            return "female"
        elif first_name in male_indicators:
            return "male"
        else:
            return random.choice(["male", "female"])
    
    def _communication_style_from_personality(self, personality: List[str]) -> str:
        if "direct" in personality:
            return "direct"
        elif "diplomatic" in personality:
            return "diplomatic"
        else:
            return "collaborative"
    
    def _decision_style_from_personality(self, personality: List[str]) -> str:
        if "decisive" in personality:
            return "quick"
        elif "analytical" in personality:
            return "analytical"
        else:
            return "consultative"
    
    def _stress_response_from_personality(self, personality: List[str]) -> str:
        if "calm" in personality:
            return "calm"
        elif "urgent" in personality:
            return "urgent"
        else:
            return "detailed"
    
    def _hair_color_for_ethnicity(self, ethnicity: Ethnicity) -> str:
        color_map = {
            Ethnicity.CAUCASIAN: ["brown", "blonde", "black", "red"],
            Ethnicity.AFRICAN_AMERICAN: ["black", "brown"],
            Ethnicity.HISPANIC: ["black", "brown"],
            Ethnicity.ASIAN_EAST: ["black", "brown"],
            Ethnicity.ASIAN_SOUTH: ["black", "brown"],
            Ethnicity.MIDDLE_EASTERN: ["black", "brown"]
        }
        return random.choice(color_map.get(ethnicity, ["brown"]))
    
    def _eye_color_for_ethnicity(self, ethnicity: Ethnicity) -> str:
        color_map = {
            Ethnicity.CAUCASIAN: ["blue", "green", "brown", "hazel"],
            Ethnicity.AFRICAN_AMERICAN: ["brown", "hazel"],
            Ethnicity.HISPANIC: ["brown", "hazel"],
            Ethnicity.ASIAN_EAST: ["brown", "black"],
            Ethnicity.ASIAN_SOUTH: ["brown", "black"],
            Ethnicity.MIDDLE_EASTERN: ["brown", "green"]
        }
        return random.choice(color_map.get(ethnicity, ["brown"]))
    
    def _accessories_for_role(self, role_level: int) -> List[str]:
        if role_level == 1:  # CEO
            return ["watch", "cufflinks"]
        elif role_level <= 3:  # Senior
            return ["watch"]
        else:
            return []

# Example usage
if __name__ == "__main__":
    generator = PersonaGenerator()
    
    persona = generator.create_unified_persona(
        org_id="org_001",
        person_index=1,
        name="Rajesh Patel", 
        role="VP Engineering",
        level=2,
        personality=["analytical", "collaborative", "calm"],
        region_bias="United States"
    )
    
    print(f"Generated persona: {persona.persona_id}")
    print(f"Demographics: {persona.demographics.ethnicity.value}, {persona.demographics.accent.value}")
    print(f"Voice: {persona.voice.speech_pattern.value}, pace: {persona.voice.pace}")
    print(f"Avatar: {persona.avatar.body_language}, gestures: {persona.avatar.gesture_frequency}")