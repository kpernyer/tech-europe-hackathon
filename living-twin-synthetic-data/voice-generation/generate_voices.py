#!/usr/bin/env python3
"""
Voice Generation Pipeline
Generates voice personas and audio files from synthetic data using ElevenLabs
"""

import json
import os
import click
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests
from dataclasses import dataclass
import hashlib

@dataclass
class VoicePersona:
    """Voice characteristics for a person"""
    person_id: str
    person_name: str
    role: str
    voice_id: str
    voice_name: str
    characteristics: Dict[str, Any]
    accent: Optional[str] = None

class VoiceGenerator:
    """Generates voice personas and audio files"""
    
    def __init__(self, elevenlabs_api_key: Optional[str] = None):
        self.api_key = elevenlabs_api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": elevenlabs_api_key
        } if elevenlabs_api_key else None
        
        # Available ElevenLabs voices (as of 2024)
        self.available_voices = {
            # Executive voices - authoritative
            "Rachel": {"gender": "female", "age": "adult", "accent": "american", "tone": "professional"},
            "Antoni": {"gender": "male", "age": "adult", "accent": "american", "tone": "warm"},
            "Adam": {"gender": "male", "age": "adult", "accent": "american", "tone": "deep"},
            "Nicole": {"gender": "female", "age": "adult", "accent": "american", "tone": "friendly"},
            
            # Technical voices - clear and analytical
            "Josh": {"gender": "male", "age": "young", "accent": "american", "tone": "casual"},
            "Arnold": {"gender": "male", "age": "mature", "accent": "american", "tone": "authoritative"},
            "Charlotte": {"gender": "female", "age": "adult", "accent": "british", "tone": "professional"},
            "Bella": {"gender": "female", "age": "young", "accent": "american", "tone": "energetic"},
            
            # Sales/Marketing voices - engaging
            "Drew": {"gender": "male", "age": "young", "accent": "american", "tone": "enthusiastic"},
            "Grace": {"gender": "female", "age": "adult", "accent": "american", "tone": "confident"},
            "Michael": {"gender": "male", "age": "adult", "accent": "american", "tone": "friendly"},
            "Jessica": {"gender": "female", "age": "adult", "accent": "american", "tone": "warm"},
            
            # International voices
            "Giovanni": {"gender": "male", "age": "adult", "accent": "italian", "tone": "expressive"},
            "Liam": {"gender": "male", "age": "young", "accent": "american", "tone": "casual"},
            "Mimi": {"gender": "female", "age": "young", "accent": "swedish", "tone": "cheerful"},
            "Freya": {"gender": "female", "age": "adult", "accent": "american", "tone": "clear"}
        }
    
    def load_synthetic_data(self, input_dir: str) -> Dict[str, Any]:
        """Load synthetic data from the generation phase"""
        
        input_path = Path(input_dir)
        
        data = {
            'organizations': [],
            'people': {},
            'scenarios': []
        }
        
        # Load organizations
        org_dir = input_path / 'organizations'
        if org_dir.exists():
            for org_file in org_dir.glob('*.json'):
                with open(org_file, 'r') as f:
                    org_data = json.load(f)
                    data['organizations'].append(org_data)
        
        # Load people
        people_dir = input_path / 'people'
        if people_dir.exists():
            for people_file in people_dir.glob('*.json'):
                with open(people_file, 'r') as f:
                    people_data = json.load(f)
                    # Extract org_id from filename
                    org_id = people_file.stem.replace('people_', '')
                    data['people'][org_id] = people_data
        
        # Load scenarios
        scenario_dir = input_path / 'scenarios'
        if scenario_dir.exists():
            for scenario_file in scenario_dir.glob('*.json'):
                with open(scenario_file, 'r') as f:
                    scenario_data = json.load(f)
                    data['scenarios'].append(scenario_data)
        
        print(f"📊 Loaded {len(data['organizations'])} organizations with {sum(len(p) for p in data['people'].values())} people")
        
        return data
    
    def create_voice_personas(self, data: Dict[str, Any]) -> Dict[str, VoicePersona]:
        """Create voice personas for all people"""
        
        personas = {}
        
        for org_id, people_list in data['people'].items():
            org = next((o for o in data['organizations'] if o['id'] == org_id), None)
            if not org:
                continue
                
            print(f"🎙️ Creating voice personas for {org['name']}...")
            
            for person in people_list:
                persona = self._create_persona_for_person(person, org)
                personas[person['id']] = persona
        
        return personas
    
    def _create_persona_for_person(self, person: Dict, org: Dict) -> VoicePersona:
        """Create voice persona for a single person"""
        
        # Select voice based on characteristics
        voice_name = self._select_voice_for_person(person, org)
        
        # Generate voice characteristics
        characteristics = self._generate_voice_characteristics(person)
        
        # Determine accent based on organization location
        accent = self._determine_accent(org.get('headquarters', 'Unknown'))
        
        persona = VoicePersona(
            person_id=person['id'],
            person_name=person['name'],
            role=person['role'],
            voice_id=voice_name.lower(),
            voice_name=voice_name,
            characteristics=characteristics,
            accent=accent
        )
        
        return persona
    
    def _select_voice_for_person(self, person: Dict, org: Dict) -> str:
        """Select appropriate voice based on person characteristics"""
        
        # Filter voices by gender
        gender = person.get('gender', 'male')
        gender_voices = {
            name: info for name, info in self.available_voices.items()
            if info['gender'] == gender
        }
        
        if not gender_voices:
            gender_voices = self.available_voices
        
        # Further filter by role type
        role = person.get('role', '').lower()
        level = person.get('level', 5)
        age = person.get('age', 30)
        
        # Scoring system for voice selection
        voice_scores = {}
        
        for voice_name, voice_info in gender_voices.items():
            score = 0
            
            # Age matching
            voice_age = voice_info.get('age', 'adult')
            if voice_age == 'young' and age < 35:
                score += 2
            elif voice_age == 'adult' and 35 <= age < 50:
                score += 2
            elif voice_age == 'mature' and age >= 50:
                score += 2
            
            # Role matching
            if level <= 2:  # Executive level
                if voice_info.get('tone') in ['professional', 'authoritative']:
                    score += 3
            elif 'engineering' in role or 'technical' in role:
                if voice_info.get('tone') in ['clear', 'analytical']:
                    score += 3
            elif 'sales' in role or 'marketing' in role:
                if voice_info.get('tone') in ['enthusiastic', 'engaging', 'confident']:
                    score += 3
            
            # Personality matching
            personality = person.get('personality_traits', [])
            if 'decisive' in personality and voice_info.get('tone') == 'authoritative':
                score += 2
            if 'collaborative' in personality and voice_info.get('tone') == 'friendly':
                score += 2
            if 'analytical' in personality and voice_info.get('tone') == 'clear':
                score += 2
            
            voice_scores[voice_name] = score
        
        # Select voice with highest score, with some randomness for diversity
        sorted_voices = sorted(voice_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Use person's name hash for consistent selection
        name_hash = int(hashlib.md5(person['name'].encode()).hexdigest(), 16)
        
        # Pick from top 3 voices for some variety
        top_voices = sorted_voices[:3]
        selected_voice = top_voices[name_hash % len(top_voices)][0]
        
        return selected_voice
    
    def _generate_voice_characteristics(self, person: Dict) -> Dict[str, Any]:
        """Generate ElevenLabs voice characteristics"""
        
        # Base characteristics
        characteristics = {
            "stability": 0.5,  # Voice consistency
            "similarity_boost": 0.75,  # Voice clarity
            "style": 0.5,  # Speaking style strength
            "use_speaker_boost": True
        }
        
        # Adjust based on personality
        personality = person.get('personality_traits', [])
        communication_style = person.get('communication_style', 'collaborative')
        
        if 'analytical' in personality:
            characteristics['stability'] = 0.8  # More consistent
            characteristics['style'] = 0.3  # Less expressive
        elif 'creative' in personality or 'visionary' in personality:
            characteristics['stability'] = 0.3  # More varied
            characteristics['style'] = 0.8  # More expressive
        
        if communication_style == 'direct':
            characteristics['similarity_boost'] = 0.9  # Very clear
        elif communication_style == 'diplomatic':
            characteristics['similarity_boost'] = 0.6  # Softer
            characteristics['style'] = 0.6  # More nuanced
        
        # Adjust for role level
        level = person.get('level', 5)
        if level <= 2:  # Executive
            characteristics['stability'] = min(0.9, characteristics['stability'] + 0.2)
            characteristics['style'] = max(0.6, characteristics['style'])
        
        return characteristics
    
    def _determine_accent(self, headquarters: str) -> str:
        """Determine accent based on headquarters location"""
        
        accent_map = {
            'silicon valley': 'american-west',
            'san francisco': 'american-west',
            'new york': 'american-northeast',
            'boston': 'american-northeast',
            'london': 'british',
            'berlin': 'european',
            'singapore': 'singaporean',
            'tokyo': 'japanese-english',
            'sydney': 'australian',
            'toronto': 'canadian'
        }
        
        hq_lower = headquarters.lower()
        for location, accent in accent_map.items():
            if location in hq_lower:
                return accent
        
        return 'american-neutral'
    
    def generate_audio_scripts(self, data: Dict[str, Any], personas: Dict[str, VoicePersona]) -> Dict[str, List[Dict]]:
        """Generate text scripts for audio generation"""
        
        scripts = {}
        
        # Generate scripts from delegation scenarios
        for scenario in data['scenarios']:
            org_id = scenario['organization_id']
            
            scenario_scripts = []
            
            # Introduction by originator
            originator_id = scenario['originator']
            if originator_id in personas:
                script = {
                    'id': f"{scenario['id']}_intro",
                    'person_id': originator_id,
                    'persona': personas[originator_id],
                    'type': 'introduction',
                    'text': self._generate_intro_script(scenario),
                    'context': 'strategic_directive'
                }
                scenario_scripts.append(script)
            
            # Delegation chain responses
            for i, step in enumerate(scenario['delegation_chain']):
                to_person_id = step['to']
                
                if to_person_id in personas:
                    script = {
                        'id': f"{scenario['id']}_response_{i}",
                        'person_id': to_person_id,
                        'persona': personas[to_person_id],
                        'type': 'response',
                        'text': self._enhance_message_for_voice(step['message'], step['response_type']),
                        'context': step['response_type'],
                        'questions': step.get('questions', [])
                    }
                    scenario_scripts.append(script)
            
            scripts[scenario['id']] = scenario_scripts
        
        return scripts
    
    def _generate_intro_script(self, scenario: Dict) -> str:
        """Generate introduction script for scenario originator"""
        
        templates = [
            f"Team, I need your attention on an urgent matter. {scenario['description']} We need to move quickly on this {scenario['type'].replace('_', ' ')} initiative.",
            
            f"I'm calling this meeting to address a critical {scenario['type'].replace('_', ' ')} situation. {scenario['description']} Let's discuss our approach.",
            
            f"We have a {scenario['urgency']} priority item that requires immediate action. {scenario['description']} I need each of your teams to contribute to this effort."
        ]
        
        # Select based on urgency and type
        if scenario['urgency'] == 'critical':
            return templates[2]
        elif scenario['type'] in ['crisis_management', 'competitive_response']:
            return templates[1]
        else:
            return templates[0]
    
    def _enhance_message_for_voice(self, message: str, response_type: str) -> str:
        """Enhance message text for more natural speech"""
        
        # Add natural speech patterns based on response type
        enhancements = {
            'accept': {
                'prefix': ['Absolutely.', 'Of course.', 'I understand.'],
                'connector': [' I\'ll ', ' We\'ll ', ' My team will '],
                'suffix': [' right away.', ' immediately.', ' as our top priority.']
            },
            'clarify': {
                'prefix': ['Well,', 'Let me think about this.', 'I have a few questions.'],
                'connector': [' Can we discuss ', ' I need to understand ', ' Could you clarify '],
                'suffix': [' before we proceed?', ' to ensure we\'re aligned?', '?']
            },
            'push_back': {
                'prefix': ['I appreciate the urgency, but', 'I understand the importance, however', 'This is significant, though'],
                'connector': [' I\'m concerned about ', ' We need to consider ', ' I see potential issues with '],
                'suffix': ['. Can we explore alternatives?', '. Should we reassess?', '.']
            },
            'suggest_alternative': {
                'prefix': ['I have a different perspective.', 'Let me propose an alternative.', 'What if we considered'],
                'connector': [' Instead of this approach, ', ' Rather than ', ' My recommendation is '],
                'suffix': [' This might be more effective.', ' This could work better.', ' What do you think?']
            },
            'delegate_further': {
                'prefix': ['I think this would be better handled by', 'Let me connect you with', 'This falls under'],
                'connector': [' my team lead ', ' the specialist who ', ' someone who '],
                'suffix': [' They\'ll take point on this.', ' They have the expertise.', ' They can handle this efficiently.']
            }
        }
        
        if response_type in enhancements:
            enhancement = enhancements[response_type]
            import random
            
            # Sometimes enhance, sometimes keep original
            if random.random() < 0.7:  # 70% chance to enhance
                prefix = random.choice(enhancement['prefix'])
                return f"{prefix} {message}"
        
        return message
    
    def generate_audio_files(self, scripts: Dict[str, List[Dict]], output_dir: str, mock: bool = False) -> Dict[str, Dict]:
        """Generate audio files from scripts"""
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        audio_files = {}
        
        for scenario_id, scenario_scripts in scripts.items():
            scenario_audio = {}
            
            print(f"🎙️ Generating audio for scenario {scenario_id}...")
            
            for script in scenario_scripts:
                if mock:
                    # Mock generation - create placeholder files
                    audio_file = output_path / f"{script['id']}.mp3"
                    
                    # Create empty file as placeholder
                    audio_file.touch()
                    
                    scenario_audio[script['id']] = {
                        'file': str(audio_file),
                        'duration': len(script['text']) / 150 * 60,  # Estimate
                        'persona': script['persona'].person_name,
                        'voice': script['persona'].voice_name,
                        'generated': 'mock'
                    }
                    
                else:
                    # Real ElevenLabs generation
                    audio_data = self._generate_audio_with_elevenlabs(script)
                    
                    if audio_data:
                        audio_file = output_path / f"{script['id']}.mp3"
                        
                        with open(audio_file, 'wb') as f:
                            f.write(audio_data)
                        
                        scenario_audio[script['id']] = {
                            'file': str(audio_file),
                            'persona': script['persona'].person_name,
                            'voice': script['persona'].voice_name,
                            'generated': 'elevenlabs'
                        }
                        
                        print(f"  ✅ Generated audio for {script['persona'].person_name}")
            
            audio_files[scenario_id] = scenario_audio
        
        return audio_files
    
    def _generate_audio_with_elevenlabs(self, script: Dict) -> Optional[bytes]:
        """Generate audio using ElevenLabs API"""
        
        if not self.api_key or not self.headers:
            print("⚠️ No ElevenLabs API key provided")
            return None
        
        persona = script['persona']
        
        url = f"{self.base_url}/text-to-speech/{persona.voice_id}"
        
        data = {
            "text": script['text'],
            "model_id": "eleven_monolingual_v1",
            "voice_settings": persona.characteristics
        }
        
        try:
            response = requests.post(url, json=data, headers=self.headers)
            
            if response.status_code == 200:
                return response.content
            else:
                print(f"❌ ElevenLabs API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error calling ElevenLabs API: {e}")
            return None
    
    def save_voice_mapping(self, personas: Dict[str, VoicePersona], 
                          scripts: Dict[str, List[Dict]], 
                          audio_files: Dict[str, Dict], 
                          output_dir: str):
        """Save voice mapping data"""
        
        output_path = Path(output_dir)
        
        # Voice persona mapping
        persona_mapping = {
            person_id: {
                'person_name': persona.person_name,
                'role': persona.role,
                'voice_id': persona.voice_id,
                'voice_name': persona.voice_name,
                'characteristics': persona.characteristics,
                'accent': persona.accent
            }
            for person_id, persona in personas.items()
        }
        
        mapping_file = output_path.parent / 'voice-mapping' / 'persona_mapping.json'
        mapping_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(mapping_file, 'w') as f:
            json.dump(persona_mapping, f, indent=2)
        
        # Audio file catalog
        audio_catalog = {
            'generation_date': '2024-01-01T00:00:00',  # Would be datetime.now()
            'total_files': sum(len(scenario) for scenario in audio_files.values()),
            'scenarios': audio_files
        }
        
        catalog_file = output_path / 'audio_catalog.json'
        
        with open(catalog_file, 'w') as f:
            json.dump(audio_catalog, f, indent=2)
        
        # Script archive
        scripts_file = output_path.parent / 'audio-scripts' / 'generated_scripts.json'
        scripts_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert personas to serializable format
        serializable_scripts = {}
        for scenario_id, scenario_scripts in scripts.items():
            serializable_scripts[scenario_id] = []
            for script in scenario_scripts:
                serializable_script = script.copy()
                # Convert persona to dict
                serializable_script['persona'] = {
                    'person_id': script['persona'].person_id,
                    'person_name': script['persona'].person_name,
                    'voice_name': script['persona'].voice_name
                }
                serializable_scripts[scenario_id].append(serializable_script)
        
        with open(scripts_file, 'w') as f:
            json.dump(serializable_scripts, f, indent=2)
        
        print(f"💾 Saved voice mapping data to {output_path.parent}")

@click.command()
@click.option('--input-dir', required=True, help='Input directory with synthetic data')
@click.option('--output-dir', required=True, help='Output directory for audio files')
@click.option('--mock', is_flag=True, help='Generate mock audio files instead of real ones')
def main(input_dir: str, output_dir: str, mock: bool):
    """Generate voice personas and audio files"""
    
    print("🎙️ Voice Generation Pipeline")
    print("=" * 40)
    
    # Get ElevenLabs API key from environment
    elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
    
    if not elevenlabs_key and not mock:
        print("⚠️ No ELEVENLABS_API_KEY found, switching to mock generation")
        mock = True
    
    # Initialize voice generator
    generator = VoiceGenerator(elevenlabs_key)
    
    # Load synthetic data
    data = generator.load_synthetic_data(input_dir)
    
    if not data['people']:
        print("❌ No people data found. Run synthetic data generation first.")
        return
    
    # Create voice personas
    personas = generator.create_voice_personas(data)
    print(f"✅ Created {len(personas)} voice personas")
    
    # Generate audio scripts
    scripts = generator.generate_audio_scripts(data, personas)
    total_scripts = sum(len(s) for s in scripts.values())
    print(f"✅ Generated {total_scripts} audio scripts")
    
    # Generate audio files
    audio_files = generator.generate_audio_files(scripts, output_dir, mock)
    
    # Save mapping data
    generator.save_voice_mapping(personas, scripts, audio_files, output_dir)
    
    total_files = sum(len(scenario) for scenario in audio_files.values())
    print(f"✅ Generated {total_files} audio files")
    
    if mock:
        print("ℹ️ Mock generation completed. Audio files are placeholders.")
    else:
        print("✅ ElevenLabs audio generation completed!")

if __name__ == '__main__':
    main()