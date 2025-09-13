#!/usr/bin/env python3
"""
Beyond Presence Avatar Integration
Creates avatar personas that match voice and demographic characteristics
"""

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
import os

# Import our persona system
import sys
sys.path.append('../shared')
from persona_system import UnifiedPersona, Ethnicity, Accent, PersonaGenerator

load_dotenv()
console = Console()

class BeyondPresenceAvatarGenerator:
    """Integration with Beyond Presence for avatar creation"""
    
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key
        self.base_url = base_url or "https://api.beyondpresence.com/v1"  # Replace with actual BP API
        
        # Avatar style mappings based on persona characteristics
        self.avatar_styles = self._setup_avatar_styles()
        
    def _setup_avatar_styles(self) -> Dict:
        """Define avatar appearance styles based on demographics and role"""
        return {
            "executive_male_caucasian": {
                "base_model": "professional_male_01",
                "styling": {
                    "hair": {"style": "executive_short", "color": "brown"},
                    "clothing": {"style": "business_suit", "color": "navy"},
                    "accessories": ["watch", "tie"],
                    "build": "professional"
                }
            },
            "executive_female_caucasian": {
                "base_model": "professional_female_01", 
                "styling": {
                    "hair": {"style": "professional_medium", "color": "blonde"},
                    "clothing": {"style": "business_suit", "color": "charcoal"},
                    "accessories": ["watch", "earrings"],
                    "build": "professional"
                }
            },
            "manager_male_asian_south": {
                "base_model": "professional_male_02",
                "styling": {
                    "hair": {"style": "professional_short", "color": "black"},
                    "skin_tone": "medium",
                    "clothing": {"style": "business_casual", "color": "blue"},
                    "accessories": ["watch"],
                    "build": "slim"
                }
            },
            "manager_female_hispanic": {
                "base_model": "professional_female_02",
                "styling": {
                    "hair": {"style": "shoulder_length", "color": "dark_brown"},
                    "skin_tone": "olive",
                    "clothing": {"style": "professional_blouse", "color": "burgundy"},
                    "accessories": ["earrings", "bracelet"],
                    "build": "medium"
                }
            },
            "staff_male_african_american": {
                "base_model": "casual_male_01",
                "styling": {
                    "hair": {"style": "short_fade", "color": "black"},
                    "skin_tone": "dark",
                    "clothing": {"style": "button_down", "color": "light_blue"},
                    "accessories": [],
                    "build": "athletic"
                }
            },
            "staff_female_asian_east": {
                "base_model": "casual_female_01",
                "styling": {
                    "hair": {"style": "long_straight", "color": "black"},
                    "skin_tone": "light",
                    "clothing": {"style": "cardigan", "color": "cream"},
                    "accessories": ["glasses"],
                    "build": "petite"
                }
            }
        }
    
    def select_avatar_style(self, persona: UnifiedPersona) -> Dict[str, Any]:
        """Select appropriate avatar style based on persona characteristics"""
        
        # Build style key based on role level, gender, and ethnicity
        role_category = "executive" if persona.level <= 2 else "manager" if persona.level <= 3 else "staff"
        gender = persona.demographics.gender
        ethnicity = persona.demographics.ethnicity.value
        
        # Try exact match first
        style_key = f"{role_category}_{gender}_{ethnicity}"
        if style_key in self.avatar_styles:
            return self.avatar_styles[style_key]
        
        # Try broader match
        broader_key = f"{role_category}_{gender}_caucasian"
        if broader_key in self.avatar_styles:
            style = self.avatar_styles[broader_key].copy()
            # Adjust for ethnicity
            style = self._adjust_style_for_ethnicity(style, persona.demographics.ethnicity)
            return style
        
        # Fallback to most generic
        fallback_key = f"staff_{gender}_caucasian"
        if fallback_key in self.avatar_styles:
            return self._adjust_style_for_ethnicity(self.avatar_styles[fallback_key], persona.demographics.ethnicity)
        
        # Ultimate fallback
        return self.avatar_styles["staff_male_caucasian"]
    
    def _adjust_style_for_ethnicity(self, base_style: Dict, ethnicity: Ethnicity) -> Dict:
        """Adjust avatar styling for specific ethnicity"""
        style = base_style.copy()
        
        if ethnicity == Ethnicity.AFRICAN_AMERICAN:
            style["styling"]["skin_tone"] = "dark"
            if "hair" in style["styling"]:
                style["styling"]["hair"]["color"] = "black"
        elif ethnicity == Ethnicity.HISPANIC:
            style["styling"]["skin_tone"] = "olive"
            if "hair" in style["styling"]:
                style["styling"]["hair"]["color"] = "dark_brown"
        elif ethnicity == Ethnicity.ASIAN_SOUTH:
            style["styling"]["skin_tone"] = "medium"
            if "hair" in style["styling"]:
                style["styling"]["hair"]["color"] = "black"
        elif ethnicity == Ethnicity.ASIAN_EAST:
            style["styling"]["skin_tone"] = "light"
            if "hair" in style["styling"]:
                style["styling"]["hair"]["color"] = "black"
        elif ethnicity == Ethnicity.MIDDLE_EASTERN:
            style["styling"]["skin_tone"] = "olive"
            if "hair" in style["styling"]:
                style["styling"]["hair"]["color"] = "dark_brown"
        
        return style
    
    def generate_avatar_behavior_profile(self, persona: UnifiedPersona) -> Dict[str, Any]:
        """Generate behavioral characteristics for the avatar"""
        
        return {
            "personality_expression": {
                "confidence_level": self._map_confidence(persona.personality_traits),
                "energy_level": self._map_energy(persona.personality_traits),
                "approachability": self._map_approachability(persona.personality_traits),
                "formality": persona.voice.formality
            },
            "communication_behaviors": {
                "gesture_frequency": persona.avatar.gesture_frequency,
                "eye_contact_style": persona.avatar.eye_contact_style,
                "posture": persona.avatar.posture,
                "body_language": persona.avatar.body_language
            },
            "meeting_behaviors": {
                "speaking_turn_preference": self._speaking_preference(persona),
                "interruption_tolerance": self._interruption_tolerance(persona),
                "agreement_expression": self._agreement_style(persona),
                "disagreement_expression": self._disagreement_style(persona)
            },
            "cultural_adaptations": {
                "accent_influence_on_gestures": self._gesture_cultural_mapping(persona.demographics.accent),
                "cultural_communication_style": self._cultural_communication(persona.demographics.ethnicity),
                "personal_space_preference": self._personal_space(persona.demographics.ethnicity)
            }
        }
    
    def create_beyond_presence_avatar_request(self, persona: UnifiedPersona) -> Dict[str, Any]:
        """Create avatar creation request for Beyond Presence API"""
        
        style = self.select_avatar_style(persona)
        behavior = self.generate_avatar_behavior_profile(persona)
        
        # Beyond Presence API request format (adjust based on actual API)
        avatar_request = {
            "persona_id": persona.persona_id,
            "name": persona.name,
            "role": persona.role,
            "organization_id": persona.organization_id,
            
            "appearance": {
                "base_model": style["base_model"],
                "styling": style["styling"],
                "demographic_traits": {
                    "ethnicity": persona.demographics.ethnicity.value,
                    "gender": persona.demographics.gender,
                    "age_range": persona.demographics.age_range
                }
            },
            
            "voice_integration": {
                "elevenlabs_voice_id": persona.elevenlabs_voice_id,
                "speech_characteristics": {
                    "accent": persona.demographics.accent.value,
                    "pace": persona.voice.pace,
                    "tone": persona.voice.tone,
                    "pitch": persona.voice.pitch
                }
            },
            
            "behavior_profile": behavior,
            
            "metadata": {
                "creation_source": "living_twin_synthetic_data",
                "personality_traits": persona.personality_traits,
                "communication_style": persona.communication_style,
                "decision_making_style": persona.decision_making_style
            }
        }
        
        return avatar_request
    
    async def create_avatar(self, persona: UnifiedPersona, mock: bool = False) -> Optional[str]:
        """Create avatar in Beyond Presence platform"""
        
        if mock:
            # Return mock avatar ID for development
            mock_avatar_id = f"bp_avatar_{persona.persona_id}_{random.randint(1000, 9999)}"
            console.print(f"🎭 [MOCK] Created avatar for {persona.name}: {mock_avatar_id}")
            return mock_avatar_id
        
        avatar_request = self.create_beyond_presence_avatar_request(persona)
        
        url = f"{self.base_url}/avatars"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=avatar_request, headers=headers) as response:
                    if response.status == 201:
                        result = await response.json()
                        avatar_id = result.get("avatar_id")
                        console.print(f"✅ Created avatar for {persona.name}: {avatar_id}")
                        return avatar_id
                    else:
                        error = await response.text()
                        console.print(f"❌ Failed to create avatar for {persona.name}: {error}")
                        return None
        except Exception as e:
            console.print(f"❌ Error creating avatar for {persona.name}: {e}")
            return None
    
    async def create_avatar_batch(self, personas: List[UnifiedPersona], 
                                output_dir: str, mock: bool = False) -> Dict:
        """Create avatars for multiple personas"""
        
        console.print(f"🎭 Creating Beyond Presence avatars for {len(personas)} personas...")
        
        avatar_mapping = {
            "generation_info": {
                "total_avatars": len(personas),
                "beyond_presence_api": self.base_url,
                "mock_mode": mock
            },
            "avatars": {}
        }
        
        # Process personas in batches to respect rate limits
        batch_size = 5
        for i in range(0, len(personas), batch_size):
            batch = personas[i:i + batch_size]
            
            console.print(f"🔄 Processing avatar batch {i//batch_size + 1}")
            
            batch_tasks = []
            for persona in batch:
                task = self.create_avatar(persona, mock)
                batch_tasks.append(task)
            
            # Wait for batch to complete
            avatar_ids = await asyncio.gather(*batch_tasks)
            
            # Store results
            for persona, avatar_id in zip(batch, avatar_ids):
                avatar_mapping["avatars"][persona.persona_id] = {
                    "name": persona.name,
                    "role": persona.role,
                    "organization_id": persona.organization_id,
                    "avatar_id": avatar_id,
                    "appearance_config": self.select_avatar_style(persona),
                    "behavior_profile": self.generate_avatar_behavior_profile(persona),
                    "voice_persona_link": persona.persona_id,  # Links to voice mapping
                    "creation_status": "success" if avatar_id else "failed"
                }
            
            # Small delay between batches
            if i + batch_size < len(personas):
                await asyncio.sleep(2)
        
        # Save mapping
        mapping_file = Path(output_dir) / "beyond_presence_avatars.json"
        with open(mapping_file, 'w') as f:
            json.dump(avatar_mapping, f, indent=2)
        
        successful_avatars = sum(1 for avatar in avatar_mapping["avatars"].values() 
                               if avatar["creation_status"] == "success")
        
        console.print(f"✅ Created {successful_avatars}/{len(personas)} avatars successfully")
        console.print(f"💾 Avatar mapping saved to {mapping_file}")
        
        return avatar_mapping
    
    # Helper methods for behavior mapping
    def _map_confidence(self, traits: List[str]) -> str:
        if "confident" in traits or "decisive" in traits:
            return "high"
        elif "hesitant" in traits or "careful" in traits:
            return "low"
        return "medium"
    
    def _map_energy(self, traits: List[str]) -> str:
        if "energetic" in traits or "dynamic" in traits:
            return "high"
        elif "calm" in traits or "steady" in traits:
            return "low"
        return "medium"
    
    def _map_approachability(self, traits: List[str]) -> str:
        if "warm" in traits or "collaborative" in traits:
            return "high"
        elif "formal" in traits or "reserved" in traits:
            return "low"
        return "medium"
    
    def _speaking_preference(self, persona: UnifiedPersona) -> str:
        if persona.level <= 2:  # Senior roles
            return "early"
        elif "confident" in persona.personality_traits:
            return "active"
        return "moderate"
    
    def _interruption_tolerance(self, persona: UnifiedPersona) -> str:
        if "collaborative" in persona.personality_traits:
            return "high"
        elif "formal" in persona.personality_traits:
            return "low"
        return "medium"
    
    def _agreement_style(self, persona: UnifiedPersona) -> str:
        if persona.demographics.ethnicity == Ethnicity.ASIAN_EAST:
            return "subtle_nodding"
        elif "energetic" in persona.personality_traits:
            return "enthusiastic"
        return "professional_acknowledgment"
    
    def _disagreement_style(self, persona: UnifiedPersona) -> str:
        if "diplomatic" in persona.personality_traits:
            return "diplomatic_questioning"
        elif "direct" in persona.personality_traits:
            return "direct_but_respectful"
        return "collaborative_exploration"
    
    def _gesture_cultural_mapping(self, accent: Accent) -> str:
        cultural_gesture_map = {
            Accent.AMERICAN_NEW_YORK: "expressive_hands",
            Accent.ITALIAN: "very_expressive", 
            Accent.SPANISH: "animated",
            Accent.BRITISH: "restrained",
            Accent.JAPANESE: "minimal_formal",
            Accent.GERMAN: "precise_controlled"
        }
        return cultural_gesture_map.get(accent, "moderate")
    
    def _cultural_communication(self, ethnicity: Ethnicity) -> str:
        cultural_map = {
            Ethnicity.ASIAN_EAST: "high_context_respectful",
            Ethnicity.ASIAN_SOUTH: "expressive_technical",
            Ethnicity.HISPANIC: "warm_expressive",
            Ethnicity.MIDDLE_EASTERN: "formal_respectful"
        }
        return cultural_map.get(ethnicity, "direct_professional")
    
    def _personal_space(self, ethnicity: Ethnicity) -> str:
        space_map = {
            Ethnicity.ASIAN_EAST: "formal_distance",
            Ethnicity.HISPANIC: "closer_comfortable",
            Ethnicity.MIDDLE_EASTERN: "respectful_distance"
        }
        return space_map.get(ethnicity, "professional_standard")

@click.command()
@click.option('--personas-file', required=True, help='JSON file with persona data')
@click.option('--output-dir', required=True, help='Output directory')
@click.option('--mock', is_flag=True, help='Use mock mode for development')
@click.option('--api-key', help='Beyond Presence API key')
@click.option('--api-url', help='Beyond Presence API URL')
def main(personas_file, output_dir, mock, api_key, api_url):
    """Create Beyond Presence avatars from persona data"""
    
    # Load personas
    try:
        with open(personas_file, 'r') as f:
            personas_data = json.load(f)
    except FileNotFoundError:
        console.print(f"❌ Personas file not found: {personas_file}")
        return
    
    # Convert to persona objects (you'd implement proper deserialization)
    # For demo, create sample personas
    persona_gen = PersonaGenerator()
    sample_personas = [
        persona_gen.create_unified_persona("org_001", 1, "Rajesh Patel", "VP Engineering", 2, 
                                         ["analytical", "collaborative"]),
        persona_gen.create_unified_persona("org_001", 2, "Sarah Johnson", "Marketing Director", 3,
                                         ["energetic", "creative"]),
        persona_gen.create_unified_persona("org_001", 3, "Miguel Rodriguez", "Sales Manager", 3,
                                         ["confident", "persuasive"])
    ]
    
    # Initialize generator
    generator = BeyondPresenceAvatarGenerator(api_key, api_url)
    
    # Run avatar creation
    asyncio.run(create_avatars(generator, sample_personas, output_dir, mock))

async def create_avatars(generator, personas, output_dir, mock):
    """Main avatar creation logic"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Create avatars
    avatar_mapping = await generator.create_avatar_batch(personas, output_dir, mock)
    
    console.print(f"\n🎭 Beyond Presence avatar creation complete!")
    console.print(f"📊 Processed {len(personas)} personas")
    
    success_count = sum(1 for avatar in avatar_mapping["avatars"].values() 
                       if avatar["creation_status"] == "success")
    console.print(f"✅ Successfully created {success_count} avatars")

if __name__ == "__main__":
    main()