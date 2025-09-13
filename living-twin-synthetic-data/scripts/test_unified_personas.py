#!/usr/bin/env python3
"""
Test Unified Persona System - Quick Demo
Shows the unified ID system with consistent personas across all systems
"""

import json
import os
from pathlib import Path
from typing import List
from rich.console import Console
from rich.table import Table
import random

# Import persona system
import sys
sys.path.append('shared')
from persona_system import PersonaGenerator, UnifiedPersona

console = Console()

def create_sample_personas() -> List[UnifiedPersona]:
    """Create sample personas to demonstrate the system"""
    
    generator = PersonaGenerator()
    
    sample_people = [
        {"name": "Rajesh Patel", "role": "VP Engineering", "level": 2, "traits": ["analytical", "collaborative", "calm"]},
        {"name": "Sarah Johnson", "role": "Marketing Director", "level": 3, "traits": ["energetic", "creative", "persuasive"]},
        {"name": "Miguel Rodriguez", "role": "Sales Manager", "level": 3, "traits": ["confident", "outgoing", "decisive"]},
        {"name": "Li Wei Chen", "role": "Data Scientist", "level": 4, "traits": ["analytical", "detail-oriented", "innovative"]},
        {"name": "Aisha Okonkwo", "role": "Product Manager", "level": 3, "traits": ["strategic", "collaborative", "user-focused"]},
        {"name": "David Thompson", "role": "CEO", "level": 1, "traits": ["visionary", "decisive", "charismatic"]},
        {"name": "Isabella Garcia", "role": "HR Director", "level": 3, "traits": ["empathetic", "diplomatic", "organized"]}
    ]
    
    personas = []
    for i, person in enumerate(sample_people):
        persona = generator.create_unified_persona(
            org_id="org_001",
            person_index=i,
            name=person["name"],
            role=person["role"],
            level=person["level"],
            personality=person["traits"],
            region_bias="United States"
        )
        
        # Simulate API integrations with mock IDs
        persona.elevenlabs_voice_id = f"elevenlabs_voice_{random.randint(1000, 9999)}"
        persona.beyond_presence_avatar_id = f"bp_avatar_{random.randint(1000, 9999)}"
        
        personas.append(persona)
    
    return personas

def demonstrate_unified_ids(personas):
    """Show the unified ID system in action"""
    
    console.print("\n🚀 [bold blue]Unified Persona ID System Demo[/bold blue]")
    console.print("=" * 60)
    
    # Show ID consistency table
    id_table = Table(title="Consistent Persona IDs Across All Systems")
    id_table.add_column("Name", style="cyan")
    id_table.add_column("Unified ID", style="green")
    id_table.add_column("ElevenLabs Voice ID", style="yellow")
    id_table.add_column("Beyond Presence Avatar ID", style="magenta")
    
    for persona in personas:
        id_table.add_row(
            persona.name,
            persona.persona_id,
            persona.elevenlabs_voice_id or "Not set",
            persona.beyond_presence_avatar_id or "Not set"
        )
    
    console.print(id_table)

def demonstrate_voice_characteristics(personas):
    """Show how demographics and personality affect voice generation"""
    
    console.print("\n🎙️ [bold blue]Voice Persona Characteristics[/bold blue]")
    console.print("=" * 60)
    
    voice_table = Table(title="Voice Characteristics Based on Demographics & Personality")
    voice_table.add_column("Name", style="cyan")
    voice_table.add_column("Ethnicity", style="green")
    voice_table.add_column("Accent", style="yellow")
    voice_table.add_column("Speech Pattern", style="magenta")
    voice_table.add_column("Pace", style="red")
    voice_table.add_column("Tone", style="blue")
    
    for persona in personas:
        voice_table.add_row(
            persona.name,
            persona.demographics.ethnicity.value.replace("_", " ").title(),
            persona.demographics.accent.value.replace("_", " ").title(),
            persona.voice.speech_pattern.value.replace("_", " ").title(),
            persona.voice.pace.title(),
            persona.voice.tone.title()
        )
    
    console.print(voice_table)

def demonstrate_avatar_characteristics(personas):
    """Show how personas translate to avatar behavior"""
    
    console.print("\n🎭 [bold blue]Avatar Behavior Characteristics[/bold blue]")
    console.print("=" * 60)
    
    avatar_table = Table(title="Avatar Behavior Based on Personality & Culture")
    avatar_table.add_column("Name", style="cyan")
    avatar_table.add_column("Body Language", style="green")
    avatar_table.add_column("Gesture Frequency", style="yellow")
    avatar_table.add_column("Eye Contact", style="magenta")
    avatar_table.add_column("Posture", style="red")
    
    for persona in personas:
        avatar_table.add_row(
            persona.name,
            persona.avatar.body_language.title(),
            persona.avatar.gesture_frequency.title(),
            persona.avatar.eye_contact_style.replace("_", " ").title(),
            persona.avatar.posture.replace("_", " ").title()
        )
    
    console.print(avatar_table)

def show_hackathon_workflow():
    """Show the exact workflow for hackathon use"""
    
    console.print("\n🏆 [bold blue]Your Hackathon Workflow[/bold blue]")
    console.print("=" * 60)
    
    workflow = [
        "1. Add API keys to .env file:",
        "   OPENAI_API_KEY=sk-your-key",
        "   ELEVENLABS_API_KEY=your-elevenlabs-key", 
        "   BEYOND_PRESENCE_API_KEY=your-bp-key",
        "",
        "2. Generate organizations with AI:",
        "   make synthetic-data-ai",
        "",
        "3. Create unified personas:",
        "   make unified-personas",
        "",
        "4. Each person gets ONE unique ID:",
        "   persona_org001_p0001 → Used in:",
        "   - Text generation (scenarios, roles)",
        "   - ElevenLabs voice creation", 
        "   - Beyond Presence avatar creation",
        "",
        "5. Result: Consistent personas across all systems!"
    ]
    
    for line in workflow:
        if line.startswith(("1.", "2.", "3.", "4.", "5.")):
            console.print(f"[bold yellow]{line}[/bold yellow]")
        elif "persona_org001_p0001" in line:
            console.print(f"[bold green]{line}[/bold green]")
        else:
            console.print(line)

def save_demo_output(personas):
    """Save demo data to show the structure"""
    
    output_dir = Path("demo-unified-personas")
    output_dir.mkdir(exist_ok=True)
    
    # Create registry
    registry = {
        "generation_info": {
            "total_personas": len(personas),
            "demo_mode": True,
            "systems_integrated": ["text", "voice", "avatar"]
        },
        "personas": {}
    }
    
    for persona in personas:
        # Save individual persona
        persona_file = output_dir / f"{persona.persona_id}.json"
        with open(persona_file, 'w') as f:
            json.dump(persona.__dict__, f, indent=2, default=str)
        
        # Add to registry
        registry["personas"][persona.persona_id] = {
            "name": persona.name,
            "role": persona.role,
            "demographics": {
                "ethnicity": persona.demographics.ethnicity.value,
                "accent": persona.demographics.accent.value,
                "gender": persona.demographics.gender
            },
            "system_ids": {
                "elevenlabs_voice_id": persona.elevenlabs_voice_id,
                "beyond_presence_avatar_id": persona.beyond_presence_avatar_id
            },
            "voice_characteristics": {
                "speech_pattern": persona.voice.speech_pattern.value,
                "pace": persona.voice.pace,
                "tone": persona.voice.tone
            },
            "avatar_characteristics": {
                "body_language": persona.avatar.body_language,
                "gesture_frequency": persona.avatar.gesture_frequency
            }
        }
    
    # Save registry
    with open(output_dir / "unified_persona_registry.json", 'w') as f:
        json.dump(registry, f, indent=2)
    
    console.print(f"\n💾 Demo data saved to {output_dir}/")
    console.print(f"📋 Registry: unified_persona_registry.json")
    console.print(f"👥 Individual personas: {len(personas)} JSON files")

def main():
    """Run the unified persona demo"""
    
    console.print("🎭 [bold blue]Living Twin Unified Persona System[/bold blue]")
    console.print("🚀 [bold green]Ready for your hackathon![/bold green]\n")
    
    # Create sample personas
    console.print("Creating sample personas...")
    personas = create_sample_personas()
    
    # Demonstrate the system
    demonstrate_unified_ids(personas)
    demonstrate_voice_characteristics(personas)  
    demonstrate_avatar_characteristics(personas)
    show_hackathon_workflow()
    
    # Save demo output
    save_demo_output(personas)
    
    console.print(f"\n🎯 [bold green]Demo Complete![/bold green]")
    console.print(f"✅ Created {len(personas)} unified personas")
    console.print(f"🔑 Each person has ONE unique ID used everywhere")
    console.print(f"🎙️ Voice personas: Ready for ElevenLabs")
    console.print(f"🎭 Avatar personas: Ready for Beyond Presence")

if __name__ == "__main__":
    main()