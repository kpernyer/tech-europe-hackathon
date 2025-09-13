#!/usr/bin/env python3
"""
Unified Persona Pipeline
Orchestrates creation of consistent personas across text, voice, and avatar systems
Each person gets ONE unique ID used everywhere: persona_org001_p0001
"""

import json
import asyncio
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import click
from rich.console import Console
from rich.progress import track, Progress, TaskID
from rich.table import Table
from dotenv import load_dotenv

# Import all our persona systems
import sys
sys.path.append('shared')
sys.path.append('voice-generation')  
sys.path.append('animation-data')

from persona_system import PersonaGenerator, UnifiedPersona
# For now, create mock versions since the enhanced generators need refactoring

load_dotenv()
console = Console()

class UnifiedPersonaPipeline:
    """Orchestrates complete persona creation across all systems"""
    
    def __init__(self, openai_key: str = None, elevenlabs_key: str = None, 
                 beyond_presence_key: str = None):
        self.openai_key = openai_key
        self.elevenlabs_key = elevenlabs_key  
        self.beyond_presence_key = beyond_presence_key
        
        # Initialize generators
        self.persona_generator = PersonaGenerator()
        self.voice_generator = ElevenLabsEnhancedGenerator(elevenlabs_key) if elevenlabs_key else None
        self.avatar_generator = BeyondPresenceAvatarGenerator(beyond_presence_key) if beyond_presence_key else None
        
    def load_organization_data(self, synthetic_data_dir: str) -> List[Dict]:
        """Load organization data from synthetic data generation"""
        
        orgs = []
        org_dir = Path(synthetic_data_dir) / "organizations"
        
        if not org_dir.exists():
            console.print(f"❌ Organizations directory not found: {org_dir}")
            return []
        
        for org_file in org_dir.glob("*.json"):
            try:
                with open(org_file, 'r') as f:
                    org_data = json.load(f)
                    orgs.append(org_data)
            except Exception as e:
                console.print(f"⚠️ Error loading {org_file}: {e}")
        
        console.print(f"📊 Loaded {len(orgs)} organizations")
        return orgs
    
    def load_people_data(self, synthetic_data_dir: str, org_id: str) -> List[Dict]:
        """Load people data for a specific organization"""
        
        people_dir = Path(synthetic_data_dir) / "people" 
        people_file = people_dir / f"people_{org_id}.json"
        
        if not people_file.exists():
            console.print(f"⚠️ People file not found: {people_file}")
            return []
        
        try:
            with open(people_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            console.print(f"❌ Error loading people for {org_id}: {e}")
            return []
    
    def create_personas_for_organization(self, org_data: Dict, 
                                       people_data: List[Dict]) -> List[UnifiedPersona]:
        """Create unified personas for all people in an organization"""
        
        personas = []
        org_id = org_data["id"]
        
        for i, person in enumerate(people_data):
            try:
                # Extract person data
                name = person["name"]
                role = person["role"] 
                level = person["level"]
                personality = person.get("personality_traits", ["professional"])
                
                # Get regional bias from organization
                region_bias = org_data.get("headquarters", "United States")
                
                # Create unified persona with consistent ID
                persona = self.persona_generator.create_unified_persona(
                    org_id=org_id,
                    person_index=i,
                    name=name,
                    role=role,
                    level=level,
                    personality=personality,
                    region_bias=region_bias
                )
                
                personas.append(persona)
                
            except Exception as e:
                console.print(f"⚠️ Error creating persona for {person.get('name', 'unknown')}: {e}")
        
        return personas
    
    async def generate_voices_for_personas(self, personas: List[UnifiedPersona], 
                                         output_dir: str, mock: bool = False) -> Dict:
        """Generate ElevenLabs voices for all personas"""
        
        if not self.voice_generator:
            console.print("⚠️ ElevenLabs generator not initialized (missing API key)")
            return {}
        
        console.print(f"🎙️ Generating voices for {len(personas)} personas...")
        
        voice_mapping = await self.voice_generator.create_persona_voice_mapping(
            personas, output_dir, mock
        )
        
        # Update personas with voice IDs
        for persona in personas:
            voice_data = voice_mapping["personas"].get(persona.persona_id, {})
            elevenlabs_config = voice_data.get("elevenlabs_config", {})
            persona.elevenlabs_voice_id = elevenlabs_config.get("voice_id")
        
        return voice_mapping
    
    async def generate_avatars_for_personas(self, personas: List[UnifiedPersona],
                                          output_dir: str, mock: bool = False) -> Dict:
        """Generate Beyond Presence avatars for all personas"""
        
        if not self.avatar_generator:
            console.print("⚠️ Beyond Presence generator not initialized (missing API key)")
            return {}
        
        console.print(f"🎭 Generating avatars for {len(personas)} personas...")
        
        avatar_mapping = await self.avatar_generator.create_avatar_batch(
            personas, output_dir, mock
        )
        
        # Update personas with avatar IDs
        for persona in personas:
            avatar_data = avatar_mapping["avatars"].get(persona.persona_id, {})
            persona.beyond_presence_avatar_id = avatar_data.get("avatar_id")
        
        return avatar_mapping
    
    def save_unified_personas(self, personas: List[UnifiedPersona], output_dir: str):
        """Save all personas with unified IDs and cross-references"""
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Create unified persona registry
        registry = {
            "generation_info": {
                "total_personas": len(personas),
                "systems_integrated": ["text", "voice", "avatar"],
                "id_format": "persona_orgXXX_pXXXX"
            },
            "personas": {}
        }
        
        # Save individual persona files and build registry
        for persona in personas:
            # Save individual persona file
            persona_file = Path(output_dir) / f"{persona.persona_id}.json"
            with open(persona_file, 'w') as f:
                json.dump(asdict(persona), f, indent=2)
            
            # Add to registry
            registry["personas"][persona.persona_id] = {
                "name": persona.name,
                "role": persona.role,
                "organization_id": persona.organization_id,
                "level": persona.level,
                "demographics": {
                    "gender": persona.demographics.gender,
                    "ethnicity": persona.demographics.ethnicity.value,
                    "accent": persona.demographics.accent.value,
                    "age_range": persona.demographics.age_range
                },
                "system_ids": {
                    "elevenlabs_voice_id": persona.elevenlabs_voice_id,
                    "beyond_presence_avatar_id": persona.beyond_presence_avatar_id,
                    "persona_file": f"{persona.persona_id}.json"
                },
                "personality_summary": {
                    "traits": persona.personality_traits,
                    "communication_style": persona.communication_style,
                    "decision_style": persona.decision_making_style
                }
            }
        
        # Save registry
        registry_file = Path(output_dir) / "unified_persona_registry.json"
        with open(registry_file, 'w') as f:
            json.dump(registry, f, indent=2)
        
        console.print(f"💾 Saved {len(personas)} unified personas")
        console.print(f"📋 Registry saved to {registry_file}")
        
        return registry
    
    async def run_complete_pipeline(self, synthetic_data_dir: str, output_dir: str,
                                  mock_voice: bool = False, mock_avatar: bool = False,
                                  org_limit: int = None) -> Dict:
        """Run the complete unified persona pipeline"""
        
        console.print("\n🚀 [bold blue]Unified Persona Pipeline[/bold blue]")
        console.print("=" * 50)
        
        # Show configuration
        config_table = Table(title="Pipeline Configuration")
        config_table.add_column("System", style="cyan")
        config_table.add_column("Status", style="green")
        config_table.add_column("Mode", style="yellow")
        
        config_table.add_row("Text Generation", "✅ Ready", "Synthetic Data")
        config_table.add_row("Voice Generation", 
                           "✅ Ready" if self.elevenlabs_key else "⚠️ Mock Only",
                           "Mock" if mock_voice else "ElevenLabs API")
        config_table.add_row("Avatar Generation", 
                           "✅ Ready" if self.beyond_presence_key else "⚠️ Mock Only", 
                           "Mock" if mock_avatar else "Beyond Presence API")
        
        console.print(config_table)
        console.print()
        
        # Step 1: Load organization data
        orgs = self.load_organization_data(synthetic_data_dir)
        if not orgs:
            console.print("❌ No organization data found")
            return {}
        
        if org_limit:
            orgs = orgs[:org_limit]
            console.print(f"🔸 Limited to {len(orgs)} organizations for testing")
        
        # Step 2: Process each organization
        all_personas = []
        total_people = 0
        
        with Progress() as progress:
            org_task = progress.add_task("Processing organizations...", total=len(orgs))
            
            for org in orgs:
                org_id = org["id"]
                org_name = org.get("name", org_id)
                
                # Load people for this org
                people = self.load_people_data(synthetic_data_dir, org_id)
                if not people:
                    console.print(f"⚠️ No people found for {org_name}")
                    progress.advance(org_task)
                    continue
                
                total_people += len(people)
                console.print(f"👥 Processing {len(people)} people from {org_name}")
                
                # Create personas
                org_personas = self.create_personas_for_organization(org, people)
                all_personas.extend(org_personas)
                
                progress.advance(org_task)
        
        console.print(f"✅ Created {len(all_personas)} unified personas from {len(orgs)} organizations")
        
        # Step 3: Generate voices
        voice_mapping = {}
        if all_personas:
            voice_mapping = await self.generate_voices_for_personas(
                all_personas, output_dir, mock_voice or not self.elevenlabs_key
            )
        
        # Step 4: Generate avatars  
        avatar_mapping = {}
        if all_personas:
            avatar_mapping = await self.generate_avatars_for_personas(
                all_personas, output_dir, mock_avatar or not self.beyond_presence_key
            )
        
        # Step 5: Save unified registry
        registry = self.save_unified_personas(all_personas, output_dir)
        
        # Step 6: Generate summary report
        self.generate_summary_report(registry, voice_mapping, avatar_mapping, output_dir)
        
        return {
            "registry": registry,
            "voice_mapping": voice_mapping, 
            "avatar_mapping": avatar_mapping,
            "total_personas": len(all_personas)
        }
    
    def generate_summary_report(self, registry: Dict, voice_mapping: Dict, 
                              avatar_mapping: Dict, output_dir: str):
        """Generate summary report of pipeline execution"""
        
        console.print("\n📊 [bold]Pipeline Summary Report[/bold]")
        
        # Persona statistics
        personas = registry["personas"]
        
        # Demographics breakdown
        ethnicities = {}
        genders = {}
        roles = {}
        
        for persona_id, persona_data in personas.items():
            demo = persona_data["demographics"]
            ethnicities[demo["ethnicity"]] = ethnicities.get(demo["ethnicity"], 0) + 1
            genders[demo["gender"]] = genders.get(demo["gender"], 0) + 1
            roles[persona_data["role"]] = roles.get(persona_data["role"], 0) + 1
        
        # Show demographics table
        demo_table = Table(title="Persona Demographics")
        demo_table.add_column("Category", style="cyan")
        demo_table.add_column("Breakdown", style="green")
        
        demo_table.add_row("Gender", ", ".join([f"{k}: {v}" for k, v in genders.items()]))
        demo_table.add_row("Ethnicities", ", ".join([f"{k}: {v}" for k, v in list(ethnicities.items())[:5]]))
        demo_table.add_row("Total Roles", str(len(roles)))
        
        console.print(demo_table)
        
        # System integration status
        voice_success = len([p for p in personas.values() if p["system_ids"]["elevenlabs_voice_id"]])
        avatar_success = len([p for p in personas.values() if p["system_ids"]["beyond_presence_avatar_id"]])
        
        integration_table = Table(title="System Integration Status")
        integration_table.add_column("System", style="cyan")
        integration_table.add_column("Success Rate", style="green")
        integration_table.add_column("Ready for Use", style="yellow")
        
        integration_table.add_row("Voice Generation", f"{voice_success}/{len(personas)}", 
                                "✅" if voice_success > 0 else "❌")
        integration_table.add_row("Avatar Generation", f"{avatar_success}/{len(personas)}",
                                "✅" if avatar_success > 0 else "❌")
        
        console.print(integration_table)
        
        console.print(f"\n🎯 [green]Pipeline Complete![/green]")
        console.print(f"📁 All data saved to: {output_dir}")
        console.print(f"🔑 Unique persona IDs: {len(personas)}")
        console.print(f"🎙️ Voice personas ready: {voice_success}")
        console.print(f"🎭 Avatar personas ready: {avatar_success}")

@click.command()
@click.option('--synthetic-data-dir', required=True, help='Directory with synthetic organization data')
@click.option('--output-dir', required=True, help='Output directory for unified personas')
@click.option('--mock-voice', is_flag=True, help='Use mock voice generation')
@click.option('--mock-avatar', is_flag=True, help='Use mock avatar generation')
@click.option('--org-limit', type=int, help='Limit number of organizations for testing')
@click.option('--openai-key', help='OpenAI API key')
@click.option('--elevenlabs-key', help='ElevenLabs API key')
@click.option('--beyond-presence-key', help='Beyond Presence API key')
def main(synthetic_data_dir, output_dir, mock_voice, mock_avatar, org_limit,
         openai_key, elevenlabs_key, beyond_presence_key):
    """
    🚀 Unified Persona Pipeline
    
    Creates consistent personas with unique IDs across text, voice, and avatar systems.
    
    Each person gets ONE ID: persona_org001_p0001 used everywhere.
    
    Examples:
        # Quick test with 2 orgs, mock everything
        python unified_persona_pipeline.py --synthetic-data-dir synthetic-data/outputs --output-dir unified-personas --org-limit 2 --mock-voice --mock-avatar
        
        # Full pipeline with real APIs  
        python unified_persona_pipeline.py --synthetic-data-dir synthetic-data/outputs --output-dir unified-personas
    """
    
    # Get API keys from environment if not provided
    openai_key = openai_key or os.getenv('OPENAI_API_KEY')
    elevenlabs_key = elevenlabs_key or os.getenv('ELEVENLABS_API_KEY') 
    beyond_presence_key = beyond_presence_key or os.getenv('BEYOND_PRESENCE_API_KEY')
    
    # Initialize pipeline
    pipeline = UnifiedPersonaPipeline(openai_key, elevenlabs_key, beyond_presence_key)
    
    # Run pipeline
    result = asyncio.run(pipeline.run_complete_pipeline(
        synthetic_data_dir, output_dir, mock_voice, mock_avatar, org_limit
    ))
    
    if result and result.get("total_personas", 0) > 0:
        console.print(f"\n✅ [green]Success! Generated {result['total_personas']} unified personas[/green]")
    else:
        console.print("\n❌ [red]Pipeline failed or generated no personas[/red]")

if __name__ == "__main__":
    main()