#!/usr/bin/env python3
"""
Animation Data Generator
Creates VR/AR scene data and spatial configurations for Beyond Presence integration
"""

import json
import click
import math
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class SpatialPosition:
    """3D position and orientation"""
    x: float
    y: float
    z: float
    rotation_y: float = 0.0

@dataclass
class AvatarConfig:
    """Avatar appearance and behavior configuration"""
    person_id: str
    name: str
    role: str
    appearance_style: str
    age_range: str
    body_language: str
    gesture_frequency: str
    animation_set: str

@dataclass
class EnvironmentConfig:
    """VR/AR environment settings"""
    type: str
    name: str
    lighting: str
    ambience: str
    acoustics: Dict[str, float]
    props: List[str]
    capacity: int

@dataclass
class AnimationSequence:
    """Timed animation sequence"""
    time: float
    character: str
    animation: str
    duration: float
    target: Optional[str] = None
    emotion: str = "neutral"

@dataclass
class CameraMovement:
    """Camera position and movement"""
    time: float
    type: str
    position: SpatialPosition
    target: Optional[str] = None
    duration: float = 3.0

@dataclass
class VRScene:
    """Complete VR/AR scene configuration"""
    id: str
    name: str
    organization_name: str
    scenario_type: str
    environment: EnvironmentConfig
    avatars: List[AvatarConfig]
    positions: List[Dict[str, SpatialPosition]]
    animations: List[AnimationSequence]
    camera_movements: List[CameraMovement]
    spatial_audio: Dict[str, Any]
    interaction_points: List[Dict[str, Any]]
    metadata: Dict[str, Any]

class AnimationDataGenerator:
    """Generates VR/AR animation data and spatial configurations"""
    
    def __init__(self):
        self.environments = self._define_environments()
        self.avatar_styles = self._define_avatar_styles()
        self.animation_sets = self._define_animation_sets()
        
    def _define_environments(self) -> Dict[str, EnvironmentConfig]:
        """Define available VR/AR environments"""
        
        return {
            "executive_boardroom": EnvironmentConfig(
                type="boardroom",
                name="Executive Boardroom",
                lighting="warm_professional",
                ambience="quiet_formal",
                acoustics={"reverb": 0.3, "absorption": 0.7, "echo": 0.1},
                props=["mahogany_table", "leather_chairs", "city_view", "presentation_screen"],
                capacity=12
            ),
            
            "modern_conference": EnvironmentConfig(
                type="conference",
                name="Modern Conference Room", 
                lighting="bright_neutral",
                ambience="collaborative",
                acoustics={"reverb": 0.2, "absorption": 0.8, "echo": 0.05},
                props=["glass_table", "ergonomic_chairs", "whiteboards", "video_screens"],
                capacity=8
            ),
            
            "open_office": EnvironmentConfig(
                type="open_office",
                name="Open Office Space",
                lighting="natural_bright",
                ambience="busy_creative",
                acoustics={"reverb": 0.5, "absorption": 0.4, "echo": 0.3},
                props=["standing_desks", "monitors", "plants", "coffee_station"],
                capacity=20
            ),
            
            "startup_lounge": EnvironmentConfig(
                type="casual",
                name="Startup Lounge",
                lighting="warm_casual", 
                ambience="innovative_energetic",
                acoustics={"reverb": 0.4, "absorption": 0.5, "echo": 0.2},
                props=["bean_bags", "ping_pong_table", "exposed_brick", "neon_signs"],
                capacity=15
            ),
            
            "virtual_space": EnvironmentConfig(
                type="virtual",
                name="Digital Meeting Space",
                lighting="ethereal_blue",
                ambience="futuristic",
                acoustics={"reverb": 0.1, "absorption": 0.9, "echo": 0.0},
                props=["floating_platforms", "holographic_displays", "particle_effects"],
                capacity=50
            )
        }
    
    def _define_avatar_styles(self) -> Dict[str, Dict]:
        """Define avatar appearance styles"""
        
        return {
            "executive": {
                "clothing": "business_formal",
                "posture": "confident_upright",
                "default_expression": "focused",
                "gesture_style": "measured"
            },
            "professional": {
                "clothing": "business_casual",
                "posture": "relaxed_professional",
                "default_expression": "attentive",
                "gesture_style": "natural"
            },
            "creative": {
                "clothing": "smart_casual",
                "posture": "relaxed_open",
                "default_expression": "curious",
                "gesture_style": "expressive"
            },
            "technical": {
                "clothing": "casual_neat",
                "posture": "slightly_forward",
                "default_expression": "analytical",
                "gesture_style": "minimal"
            }
        }
    
    def _define_animation_sets(self) -> Dict[str, List[str]]:
        """Define animation sets for different roles"""
        
        return {
            "executive": [
                "authoritative_speaking", "confident_listening", "decisive_gesture",
                "strategic_pointing", "leadership_stance", "executive_nod"
            ],
            "collaborative": [
                "open_discussion", "active_listening", "encouraging_gesture", 
                "inclusive_speaking", "team_oriented", "supportive_nod"
            ],
            "analytical": [
                "thoughtful_pause", "data_presentation", "careful_consideration",
                "precise_gesture", "focused_attention", "analytical_expression"
            ],
            "creative": [
                "enthusiastic_speaking", "expressive_gesture", "idea_sharing",
                "creative_thinking", "inspirational_pose", "innovative_expression"
            ]
        }
    
    def load_input_data(self, synthetic_dir: str, voice_dir: str) -> Dict[str, Any]:
        """Load synthetic and voice data"""
        
        data = {
            'organizations': [],
            'people': {},
            'scenarios': [],
            'voice_personas': {},
            'audio_files': {}
        }
        
        # Load synthetic data
        synthetic_path = Path(synthetic_dir)
        
        # Organizations
        org_dir = synthetic_path / 'organizations'
        if org_dir.exists():
            for org_file in org_dir.glob('*.json'):
                with open(org_file, 'r') as f:
                    data['organizations'].append(json.load(f))
        
        # People
        people_dir = synthetic_path / 'people'
        if people_dir.exists():
            for people_file in people_dir.glob('*.json'):
                with open(people_file, 'r') as f:
                    org_id = people_file.stem.replace('people_', '')
                    data['people'][org_id] = json.load(f)
        
        # Scenarios
        scenario_dir = synthetic_path / 'scenarios'
        if scenario_dir.exists():
            for scenario_file in scenario_dir.glob('*.json'):
                with open(scenario_file, 'r') as f:
                    data['scenarios'].append(json.load(f))
        
        # Voice data
        voice_path = Path(voice_dir)
        
        # Voice personas
        voice_mapping_file = voice_path.parent / 'voice-mapping' / 'persona_mapping.json'
        if voice_mapping_file.exists():
            with open(voice_mapping_file, 'r') as f:
                data['voice_personas'] = json.load(f)
        
        # Audio catalog
        audio_catalog_file = voice_path / 'audio_catalog.json'
        if audio_catalog_file.exists():
            with open(audio_catalog_file, 'r') as f:
                data['audio_files'] = json.load(f)
        
        print(f"📊 Loaded data for {len(data['organizations'])} organizations")
        
        return data
    
    def generate_vr_scenes(self, data: Dict[str, Any]) -> List[VRScene]:
        """Generate VR/AR scenes from scenarios"""
        
        scenes = []
        
        for scenario in data['scenarios']:
            scene = self._create_scene_for_scenario(scenario, data)
            if scene:
                scenes.append(scene)
        
        return scenes
    
    def _create_scene_for_scenario(self, scenario: Dict, data: Dict[str, Any]) -> Optional[VRScene]:
        """Create a VR scene for a specific scenario"""
        
        org_id = scenario['organization_id']
        
        # Find organization
        org = next((o for o in data['organizations'] if o['id'] == org_id), None)
        if not org:
            return None
        
        # Get people for this organization
        people = data['people'].get(org_id, [])
        if not people:
            return None
        
        # Select appropriate environment
        environment = self._select_environment_for_scenario(scenario, org)
        
        # Create avatars for people in delegation chain
        avatars = self._create_avatars_for_scenario(scenario, people, data['voice_personas'])
        
        # Generate spatial positions
        positions = self._generate_spatial_positions(avatars, environment)
        
        # Create animation sequences
        animations = self._create_animation_sequences(scenario, avatars, data['audio_files'])
        
        # Generate camera movements
        camera_movements = self._generate_camera_movements(scenario, avatars, positions)
        
        # Configure spatial audio
        spatial_audio = self._configure_spatial_audio(avatars, positions, environment)
        
        # Create interaction points
        interaction_points = self._create_interaction_points(scenario, avatars)
        
        scene = VRScene(
            id=f"scene_{scenario['id']}",
            name=f"{scenario['title']} - VR Experience",
            organization_name=org['name'],
            scenario_type=scenario['type'],
            environment=environment,
            avatars=avatars,
            positions=positions,
            animations=animations,
            camera_movements=camera_movements,
            spatial_audio=spatial_audio,
            interaction_points=interaction_points,
            metadata={
                'created': datetime.now().isoformat(),
                'scenario_id': scenario['id'],
                'organization_id': org_id,
                'estimated_duration': self._estimate_scene_duration(animations),
                'complexity': 'medium'
            }
        )
        
        return scene
    
    def _select_environment_for_scenario(self, scenario: Dict, org: Dict) -> EnvironmentConfig:
        """Select appropriate environment based on scenario and organization"""
        
        scenario_type = scenario['type']
        urgency = scenario.get('urgency', 'medium')
        org_size = org.get('size', 500)
        
        # Environment selection logic
        if scenario_type in ['crisis_management', 'strategic_planning'] and urgency in ['high', 'critical']:
            return self.environments['executive_boardroom']
        elif org_size < 200:
            return self.environments['startup_lounge']
        elif scenario_type in ['innovation_initiative', 'digital_transformation']:
            return self.environments['modern_conference']
        elif scenario.get('scope') == 'company-wide':
            return self.environments['virtual_space']
        else:
            return self.environments['modern_conference']
    
    def _create_avatars_for_scenario(self, scenario: Dict, people: List[Dict], 
                                   voice_personas: Dict[str, Dict]) -> List[AvatarConfig]:
        """Create avatar configurations for people in scenario"""
        
        avatars = []
        
        # Get people involved in delegation chain
        involved_people = set([scenario['originator']])
        
        for step in scenario['delegation_chain']:
            involved_people.add(step['from'])
            involved_people.add(step['to'])
        
        # Create avatars for involved people
        for person in people:
            if person['id'] in involved_people:
                avatar = self._create_avatar_for_person(person, voice_personas.get(person['id'], {}))
                avatars.append(avatar)
        
        return avatars
    
    def _create_avatar_for_person(self, person: Dict, voice_persona: Dict) -> AvatarConfig:
        """Create avatar configuration for a person"""
        
        # Determine avatar style based on role and personality
        level = person.get('level', 5)
        personality = person.get('personality_traits', [])
        role = person.get('role', '').lower()
        
        # Select avatar style
        if level <= 2:
            appearance_style = "executive"
        elif 'creative' in personality or 'visionary' in personality:
            appearance_style = "creative"
        elif 'analytical' in personality or 'technical' in role:
            appearance_style = "technical"
        else:
            appearance_style = "professional"
        
        # Determine gesture frequency
        gesture_frequency = "high" if 'expressive' in personality else \
                           "low" if 'reserved' in personality else "medium"
        
        # Select animation set
        if 'decisive' in personality or level <= 2:
            animation_set = "executive"
        elif 'collaborative' in personality:
            animation_set = "collaborative"
        elif 'analytical' in personality:
            animation_set = "analytical"
        elif 'creative' in personality:
            animation_set = "creative"
        else:
            animation_set = "collaborative"
        
        # Determine body language
        body_language = "confident" if level <= 2 else \
                       "analytical" if 'analytical' in personality else \
                       "expressive" if 'creative' in personality else "neutral"
        
        avatar = AvatarConfig(
            person_id=person['id'],
            name=person['name'],
            role=person['role'],
            appearance_style=appearance_style,
            age_range=self._determine_age_range(person.get('age', 35)),
            body_language=body_language,
            gesture_frequency=gesture_frequency,
            animation_set=animation_set
        )
        
        return avatar
    
    def _determine_age_range(self, age: int) -> str:
        """Determine age range for avatar appearance"""
        
        if age < 30:
            return "young_adult"
        elif age < 45:
            return "adult"
        elif age < 60:
            return "mature_adult"
        else:
            return "senior"
    
    def _generate_spatial_positions(self, avatars: List[AvatarConfig], 
                                   environment: EnvironmentConfig) -> List[Dict[str, SpatialPosition]]:
        """Generate spatial positions for avatars in the environment"""
        
        positions = []
        
        if environment.type == "boardroom":
            positions = self._generate_boardroom_positions(avatars)
        elif environment.type == "conference":
            positions = self._generate_conference_positions(avatars)
        elif environment.type == "open_office":
            positions = self._generate_open_office_positions(avatars)
        elif environment.type == "casual":
            positions = self._generate_casual_positions(avatars)
        elif environment.type == "virtual":
            positions = self._generate_virtual_positions(avatars)
        else:
            positions = self._generate_default_positions(avatars)
        
        return positions
    
    def _generate_boardroom_positions(self, avatars: List[AvatarConfig]) -> List[Dict[str, SpatialPosition]]:
        """Generate positions for boardroom setting"""
        
        positions = []
        
        # Rectangular table layout
        num_avatars = len(avatars)
        
        # CEO/Originator at head of table
        ceo_avatar = next((a for a in avatars if 'ceo' in a.role.lower() or a.person_id.endswith('_000')), avatars[0])
        
        positions.append({
            ceo_avatar.person_id: SpatialPosition(x=0, y=0, z=3, rotation_y=180)
        })
        
        # Others around table
        remaining_avatars = [a for a in avatars if a != ceo_avatar]
        
        for i, avatar in enumerate(remaining_avatars):
            if i < 5:  # Left side
                x = -2.5
                z = (i - 2) * 1.2
                rotation = 90
            else:  # Right side
                x = 2.5
                z = ((i - 5) - 2) * 1.2
                rotation = -90
            
            positions.append({
                avatar.person_id: SpatialPosition(x=x, y=0, z=z, rotation_y=rotation)
            })
        
        return positions
    
    def _generate_conference_positions(self, avatars: List[AvatarConfig]) -> List[Dict[str, SpatialPosition]]:
        """Generate positions for conference room setting"""
        
        positions = []
        
        # U-shape arrangement
        num_avatars = len(avatars)
        
        for i, avatar in enumerate(avatars):
            angle = (i / max(1, num_avatars - 1)) * 180  # Spread across 180 degrees
            radius = 2.5
            
            x = radius * math.cos(math.radians(angle - 90))
            z = radius * math.sin(math.radians(angle - 90)) + 1
            
            positions.append({
                avatar.person_id: SpatialPosition(x=x, y=0, z=z, rotation_y=angle - 90)
            })
        
        return positions
    
    def _generate_open_office_positions(self, avatars: List[AvatarConfig]) -> List[Dict[str, SpatialPosition]]:
        """Generate positions for open office setting"""
        
        positions = []
        
        # Cluster around workstations
        for i, avatar in enumerate(avatars):
            cluster = i // 4
            position_in_cluster = i % 4
            
            base_x = (cluster % 3) * 4 - 4
            base_z = (cluster // 3) * 4 - 2
            
            offset_x = (position_in_cluster % 2) * 1.5
            offset_z = (position_in_cluster // 2) * 1.5
            
            x = base_x + offset_x
            z = base_z + offset_z
            rotation = (position_in_cluster * 90) % 360
            
            positions.append({
                avatar.person_id: SpatialPosition(x=x, y=0, z=z, rotation_y=rotation)
            })
        
        return positions
    
    def _generate_casual_positions(self, avatars: List[AvatarConfig]) -> List[Dict[str, SpatialPosition]]:
        """Generate positions for casual/startup setting"""
        
        positions = []
        
        # Loose circle arrangement
        for i, avatar in enumerate(avatars):
            angle = (i / len(avatars)) * 360
            radius = 2.0 + (i % 3) * 0.5  # Varying radius for natural feel
            
            x = radius * math.cos(math.radians(angle))
            z = radius * math.sin(math.radians(angle))
            
            positions.append({
                avatar.person_id: SpatialPosition(x=x, y=0, z=z, rotation_y=angle + 180)
            })
        
        return positions
    
    def _generate_virtual_positions(self, avatars: List[AvatarConfig]) -> List[Dict[str, SpatialPosition]]:
        """Generate positions for virtual space"""
        
        positions = []
        
        # Multi-level floating arrangement
        for i, avatar in enumerate(avatars):
            level = i // 8
            position_on_level = i % 8
            
            angle = (position_on_level / 8) * 360
            radius = 3 + level * 1.5
            height = level * 0.8
            
            x = radius * math.cos(math.radians(angle))
            z = radius * math.sin(math.radians(angle))
            y = height
            
            positions.append({
                avatar.person_id: SpatialPosition(x=x, y=y, z=z, rotation_y=angle + 180)
            })
        
        return positions
    
    def _generate_default_positions(self, avatars: List[AvatarConfig]) -> List[Dict[str, SpatialPosition]]:
        """Generate default circular positions"""
        
        positions = []
        
        for i, avatar in enumerate(avatars):
            angle = (i / len(avatars)) * 360
            radius = 2.5
            
            x = radius * math.cos(math.radians(angle))
            z = radius * math.sin(math.radians(angle))
            
            positions.append({
                avatar.person_id: SpatialPosition(x=x, y=0, z=z, rotation_y=angle + 180)
            })
        
        return positions
    
    def _create_animation_sequences(self, scenario: Dict, avatars: List[AvatarConfig], 
                                  audio_files: Dict) -> List[AnimationSequence]:
        """Create timed animation sequences"""
        
        animations = []
        current_time = 0.0
        
        # Opening scene - all idle
        for avatar in avatars:
            animations.append(AnimationSequence(
                time=0.0,
                character=avatar.person_id,
                animation="idle_professional",
                duration=5.0
            ))
        
        current_time = 2.0
        
        # Originator introduction
        originator_id = scenario['originator']
        originator = next((a for a in avatars if a.person_id == originator_id), None)
        
        if originator:
            animations.append(AnimationSequence(
                time=current_time,
                character=originator_id,
                animation="authoritative_speaking",
                duration=15.0,
                emotion="focused"
            ))
            
            # Others listening
            for avatar in avatars:
                if avatar.person_id != originator_id:
                    animations.append(AnimationSequence(
                        time=current_time,
                        character=avatar.person_id,
                        animation="active_listening",
                        duration=15.0,
                        target=originator_id
                    ))
            
            current_time += 18.0
        
        # Delegation chain animations
        for step in scenario['delegation_chain']:
            from_person = step['from']
            to_person = step['to']
            response_type = step['response_type']
            
            # Response animation based on type
            animation_map = {
                'accept': 'confident_agreement',
                'clarify': 'thoughtful_questioning',
                'push_back': 'concerned_expression',
                'delegate_further': 'directive_gesture',
                'suggest_alternative': 'enthusiastic_proposal'
            }
            
            animation = animation_map.get(response_type, 'neutral_speaking')
            
            # Speaking animation
            animations.append(AnimationSequence(
                time=current_time,
                character=to_person,
                animation=animation,
                duration=12.0,
                emotion=self._get_emotion_for_response(response_type)
            ))
            
            # Others listening/reacting
            for avatar in avatars:
                if avatar.person_id not in [from_person, to_person]:
                    react_animation = 'attentive_listening' if response_type == 'accept' else \
                                    'concerned_listening' if response_type == 'push_back' else \
                                    'interested_listening'
                    
                    animations.append(AnimationSequence(
                        time=current_time + 2.0,
                        character=avatar.person_id,
                        animation=react_animation,
                        duration=10.0,
                        target=to_person
                    ))
            
            current_time += 15.0
        
        # Closing scene
        animations.append(AnimationSequence(
            time=current_time,
            character=originator_id,
            animation="wrap_up_gesture",
            duration=5.0
        ))
        
        return animations
    
    def _get_emotion_for_response(self, response_type: str) -> str:
        """Get emotion based on response type"""
        
        emotion_map = {
            'accept': 'confident',
            'clarify': 'curious',
            'push_back': 'concerned',
            'delegate_further': 'directive',
            'suggest_alternative': 'enthusiastic'
        }
        
        return emotion_map.get(response_type, 'neutral')
    
    def _generate_camera_movements(self, scenario: Dict, avatars: List[AvatarConfig], 
                                 positions: List[Dict[str, SpatialPosition]]) -> List[CameraMovement]:
        """Generate cinematic camera movements"""
        
        movements = []
        
        # Get position lookup
        position_lookup = {}
        for pos_dict in positions:
            position_lookup.update(pos_dict)
        
        # Opening wide shot
        movements.append(CameraMovement(
            time=0.0,
            type="wide_shot",
            position=SpatialPosition(x=0, y=4, z=-6, rotation_y=0),
            duration=5.0
        ))
        
        current_time = 5.0
        
        # Focus on originator
        originator_id = scenario['originator']
        if originator_id in position_lookup:
            orig_pos = position_lookup[originator_id]
            movements.append(CameraMovement(
                time=current_time,
                type="medium_shot",
                position=SpatialPosition(
                    x=orig_pos.x + 2,
                    y=1.7,
                    z=orig_pos.z - 2,
                    rotation_y=0
                ),
                target=originator_id,
                duration=15.0
            ))
            
            current_time += 15.0
        
        # Follow delegation chain
        for step in scenario['delegation_chain']:
            to_person = step['to']
            
            if to_person in position_lookup:
                person_pos = position_lookup[to_person]
                
                # Over-shoulder shot
                movements.append(CameraMovement(
                    time=current_time,
                    type="over_shoulder",
                    position=SpatialPosition(
                        x=person_pos.x - 1.5,
                        y=1.8,
                        z=person_pos.z + 1,
                        rotation_y=0
                    ),
                    target=to_person,
                    duration=8.0
                ))
                
                current_time += 8.0
                
                # Reaction shots
                movements.append(CameraMovement(
                    time=current_time,
                    type="group_reaction",
                    position=SpatialPosition(x=3, y=2, z=0, rotation_y=0),
                    duration=4.0
                ))
                
                current_time += 7.0
        
        # Final wide shot
        movements.append(CameraMovement(
            time=current_time,
            type="final_wide",
            position=SpatialPosition(x=-2, y=3, z=-4, rotation_y=0),
            duration=5.0
        ))
        
        return movements
    
    def _configure_spatial_audio(self, avatars: List[AvatarConfig], 
                               positions: List[Dict[str, SpatialPosition]], 
                               environment: EnvironmentConfig) -> Dict[str, Any]:
        """Configure spatial audio settings"""
        
        # Get position lookup
        position_lookup = {}
        for pos_dict in positions:
            position_lookup.update(pos_dict)
        
        audio_sources = []
        
        for avatar in avatars:
            if avatar.person_id in position_lookup:
                pos = position_lookup[avatar.person_id]
                audio_sources.append({
                    "source_id": avatar.person_id,
                    "position": {"x": pos.x, "y": pos.y, "z": pos.z},
                    "voice_characteristics": {
                        "distance_attenuation": True,
                        "directional": True,
                        "occlusion": True
                    }
                })
        
        return {
            "enabled": True,
            "room_acoustics": environment.acoustics,
            "audio_sources": audio_sources,
            "listener_position": {"x": 0, "y": 1.7, "z": -3},
            "ambient_sounds": self._get_ambient_sounds(environment)
        }
    
    def _get_ambient_sounds(self, environment: EnvironmentConfig) -> List[Dict]:
        """Get ambient sounds for environment"""
        
        ambient_map = {
            "boardroom": [{"sound": "air_conditioning", "volume": 0.1}],
            "conference": [{"sound": "subtle_ventilation", "volume": 0.05}],
            "open_office": [
                {"sound": "keyboard_typing", "volume": 0.3},
                {"sound": "office_ambience", "volume": 0.2}
            ],
            "casual": [
                {"sound": "coffee_machine", "volume": 0.15},
                {"sound": "casual_ambience", "volume": 0.2}
            ],
            "virtual": [{"sound": "digital_hum", "volume": 0.1}]
        }
        
        return ambient_map.get(environment.type, [])
    
    def _create_interaction_points(self, scenario: Dict, avatars: List[AvatarConfig]) -> List[Dict[str, Any]]:
        """Create user interaction opportunities"""
        
        interactions = []
        current_time = 20.0  # After introduction
        
        for i, step in enumerate(scenario['delegation_chain']):
            # Decision point after each delegation step
            interactions.append({
                "id": f"decision_{i}",
                "time": current_time,
                "type": "choice",
                "title": f"How would you respond as {step['to']}?",
                "description": f"You are {step['to']}. The {step['from']} has delegated this task to you.",
                "options": [
                    {"label": "Accept immediately", "outcome": "quick_accept"},
                    {"label": "Ask for clarification", "outcome": "seek_clarity"},
                    {"label": "Suggest alternative approach", "outcome": "alternative"},
                    {"label": "Express concerns", "outcome": "pushback"}
                ],
                "timeout": 30,
                "analytics_tracked": True
            })
            
            current_time += 15.0
        
        # Voice response opportunity
        interactions.append({
            "id": "voice_practice",
            "time": current_time,
            "type": "voice_recording",
            "title": "Practice Your Response",
            "description": "Record how you would handle this delegation in your own words",
            "max_duration": 60,
            "analysis": {
                "confidence_detection": True,
                "pace_analysis": True,
                "clarity_score": True
            }
        })
        
        return interactions
    
    def _estimate_scene_duration(self, animations: List[AnimationSequence]) -> float:
        """Estimate total scene duration"""
        
        if not animations:
            return 60.0  # Default 1 minute
        
        max_end_time = max(anim.time + anim.duration for anim in animations)
        return max_end_time + 5.0  # Add buffer
    
    def save_scene_data(self, scenes: List[VRScene], output_dir: str):
        """Save VR scene data to files"""
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save individual scene files
        for scene in scenes:
            scene_file = output_path / f"{scene.id}.json"
            
            # Convert dataclasses to dicts
            scene_dict = asdict(scene)
            
            with open(scene_file, 'w') as f:
                json.dump(scene_dict, f, indent=2)
        
        # Save scene catalog
        catalog = {
            "generation_date": datetime.now().isoformat(),
            "total_scenes": len(scenes),
            "scenes": [
                {
                    "id": scene.id,
                    "name": scene.name,
                    "organization": scene.organization_name,
                    "scenario_type": scene.scenario_type,
                    "environment": scene.environment.name,
                    "avatar_count": len(scene.avatars),
                    "estimated_duration": scene.metadata.get('estimated_duration', 0),
                    "file": f"{scene.id}.json"
                }
                for scene in scenes
            ]
        }
        
        catalog_file = output_path / 'scene_catalog.json'
        with open(catalog_file, 'w') as f:
            json.dump(catalog, f, indent=2)
        
        print(f"💾 Saved {len(scenes)} VR scenes to {output_dir}")

@click.command()
@click.option('--synthetic-dir', required=True, help='Synthetic data directory')
@click.option('--voice-dir', required=True, help='Voice generation directory')
@click.option('--output-dir', required=True, help='Animation output directory')
def main(synthetic_dir: str, voice_dir: str, output_dir: str):
    """Generate animation data and VR/AR scenes"""
    
    print("🎬 Animation Data Generator")
    print("=" * 40)
    
    generator = AnimationDataGenerator()
    
    # Load input data
    data = generator.load_input_data(synthetic_dir, voice_dir)
    
    if not data['scenarios']:
        print("❌ No scenarios found. Run synthetic data generation first.")
        return
    
    # Generate VR scenes
    scenes = generator.generate_vr_scenes(data)
    
    if not scenes:
        print("❌ No scenes generated.")
        return
    
    # Save scene data
    generator.save_scene_data(scenes, output_dir)
    
    print(f"✅ Generated {len(scenes)} VR/AR scenes")
    print(f"📊 Environments used: {len(set(scene.environment.name for scene in scenes))}")
    print(f"🎭 Total avatars: {sum(len(scene.avatars) for scene in scenes)}")

if __name__ == '__main__':
    main()