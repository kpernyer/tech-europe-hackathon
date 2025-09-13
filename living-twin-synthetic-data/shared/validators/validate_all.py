#!/usr/bin/env python3
"""
Data Validator
Validates all generated synthetic data against schemas
"""

import json
import click
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import jsonschema
from jsonschema import validate, ValidationError
from rich.console import Console
from rich.table import Table
from rich.progress import track

console = Console()

class DataValidator:
    """Validates synthetic data against JSON schemas"""
    
    def __init__(self, schema_dir: str):
        self.schema_dir = Path(schema_dir)
        self.schemas = self._load_schemas()
        
    def _load_schemas(self) -> Dict[str, Dict]:
        """Load all JSON schemas"""
        
        schemas = {}
        
        if not self.schema_dir.exists():
            console.print(f"[yellow]⚠️ Schema directory not found: {self.schema_dir}[/yellow]")
            return schemas
        
        for schema_file in self.schema_dir.glob('*.json'):
            try:
                with open(schema_file, 'r') as f:
                    schema = json.load(f)
                    schemas[schema_file.stem] = schema
                    console.print(f"[green]✅ Loaded schema: {schema_file.name}[/green]")
            except Exception as e:
                console.print(f"[red]❌ Failed to load schema {schema_file.name}: {e}[/red]")
        
        return schemas
    
    def validate_organizations(self, org_dir: str) -> Tuple[int, int, List[str]]:
        """Validate organization files"""
        
        org_path = Path(org_dir)
        if not org_path.exists():
            return 0, 0, [f"Organizations directory not found: {org_dir}"]
        
        org_files = list(org_path.glob('*.json'))
        if not org_files:
            return 0, 0, ["No organization files found"]
        
        valid_count = 0
        total_count = len(org_files)
        errors = []
        
        schema = self.schemas.get('organization')
        if not schema:
            return 0, total_count, ["Organization schema not found"]
        
        console.print(f"\n[blue]🏢 Validating {total_count} organization files...[/blue]")
        
        for org_file in track(org_files, description="Validating organizations..."):
            try:
                with open(org_file, 'r') as f:
                    org_data = json.load(f)
                
                validate(instance=org_data, schema=schema)
                valid_count += 1
                
            except ValidationError as e:
                errors.append(f"{org_file.name}: {e.message}")
            except Exception as e:
                errors.append(f"{org_file.name}: {str(e)}")
        
        return valid_count, total_count, errors
    
    def validate_people(self, people_dir: str) -> Tuple[int, int, List[str]]:
        """Validate people files"""
        
        people_path = Path(people_dir)
        if not people_path.exists():
            return 0, 0, [f"People directory not found: {people_dir}"]
        
        people_files = list(people_path.glob('*.json'))
        if not people_files:
            return 0, 0, ["No people files found"]
        
        valid_count = 0
        total_count = 0
        errors = []
        
        console.print(f"\n[blue]👥 Validating people files...[/blue]")
        
        for people_file in track(people_files, description="Validating people..."):
            try:
                with open(people_file, 'r') as f:
                    people_data = json.load(f)
                
                if not isinstance(people_data, list):
                    errors.append(f"{people_file.name}: Expected array of people")
                    continue
                
                file_people_count = len(people_data)
                total_count += file_people_count
                
                # Validate each person
                for i, person in enumerate(people_data):
                    try:
                        self._validate_person(person)
                        valid_count += 1
                    except ValidationError as e:
                        errors.append(f"{people_file.name}[{i}]: {e}")
                    except Exception as e:
                        errors.append(f"{people_file.name}[{i}]: {str(e)}")
                        
            except Exception as e:
                errors.append(f"{people_file.name}: {str(e)}")
        
        return valid_count, total_count, errors
    
    def _validate_person(self, person: Dict):
        """Validate individual person data"""
        
        required_fields = ['id', 'name', 'role', 'level', 'email']
        
        for field in required_fields:
            if field not in person:
                raise ValidationError(f"Missing required field: {field}")
        
        # Validate specific fields
        if not isinstance(person['level'], int) or person['level'] < 1 or person['level'] > 5:
            raise ValidationError("Level must be integer between 1 and 5")
        
        if '@' not in person['email']:
            raise ValidationError("Invalid email format")
        
        if not person['name'].strip():
            raise ValidationError("Name cannot be empty")
    
    def validate_scenarios(self, scenario_dir: str) -> Tuple[int, int, List[str]]:
        """Validate scenario files"""
        
        scenario_path = Path(scenario_dir)
        if not scenario_path.exists():
            return 0, 0, [f"Scenarios directory not found: {scenario_dir}"]
        
        scenario_files = list(scenario_path.glob('*.json'))
        if not scenario_files:
            return 0, 0, ["No scenario files found"]
        
        valid_count = 0
        total_count = len(scenario_files)
        errors = []
        
        console.print(f"\n[blue]📋 Validating {total_count} scenario files...[/blue]")
        
        for scenario_file in track(scenario_files, description="Validating scenarios..."):
            try:
                with open(scenario_file, 'r') as f:
                    scenario_data = json.load(f)
                
                self._validate_scenario(scenario_data)
                valid_count += 1
                
            except ValidationError as e:
                errors.append(f"{scenario_file.name}: {e}")
            except Exception as e:
                errors.append(f"{scenario_file.name}: {str(e)}")
        
        return valid_count, total_count, errors
    
    def _validate_scenario(self, scenario: Dict):
        """Validate individual scenario data"""
        
        required_fields = ['id', 'organization_id', 'type', 'title', 'originator', 'delegation_chain']
        
        for field in required_fields:
            if field not in scenario:
                raise ValidationError(f"Missing required field: {field}")
        
        # Validate delegation chain
        if not isinstance(scenario['delegation_chain'], list):
            raise ValidationError("delegation_chain must be an array")
        
        for i, step in enumerate(scenario['delegation_chain']):
            if not isinstance(step, dict):
                raise ValidationError(f"delegation_chain[{i}] must be an object")
            
            required_step_fields = ['from', 'to', 'response_type', 'message']
            for field in required_step_fields:
                if field not in step:
                    raise ValidationError(f"delegation_chain[{i}] missing field: {field}")
    
    def validate_voice_data(self, voice_dir: str) -> Tuple[int, int, List[str]]:
        """Validate voice generation data"""
        
        voice_path = Path(voice_dir)
        if not voice_path.exists():
            return 0, 0, [f"Voice directory not found: {voice_dir}"]
        
        errors = []
        valid_count = 0
        total_count = 0
        
        console.print(f"\n[blue]🎙️ Validating voice data...[/blue]")
        
        # Check for voice mapping
        mapping_file = voice_path.parent / 'voice-mapping' / 'persona_mapping.json'
        if mapping_file.exists():
            try:
                with open(mapping_file, 'r') as f:
                    mapping_data = json.load(f)
                
                if isinstance(mapping_data, dict):
                    valid_count += len(mapping_data)
                    total_count += len(mapping_data)
                else:
                    errors.append("persona_mapping.json: Expected object")
                    
            except Exception as e:
                errors.append(f"persona_mapping.json: {str(e)}")
        else:
            errors.append("persona_mapping.json not found")
        
        # Check for audio catalog
        catalog_file = voice_path / 'audio_catalog.json'
        if catalog_file.exists():
            try:
                with open(catalog_file, 'r') as f:
                    catalog_data = json.load(f)
                
                scenarios = catalog_data.get('scenarios', {})
                for scenario_id, scenario_audio in scenarios.items():
                    total_count += len(scenario_audio)
                    
                    for audio_id, audio_info in scenario_audio.items():
                        if 'file' in audio_info and 'persona' in audio_info:
                            # Check if audio file exists (for real generation)
                            audio_file = Path(audio_info['file'])
                            if audio_file.exists() or audio_info.get('generated') == 'mock':
                                valid_count += 1
                            else:
                                errors.append(f"Audio file not found: {audio_file}")
                        else:
                            errors.append(f"Invalid audio info: {audio_id}")
                            
            except Exception as e:
                errors.append(f"audio_catalog.json: {str(e)}")
        else:
            errors.append("audio_catalog.json not found")
        
        return valid_count, total_count, errors
    
    def validate_animation_data(self, animation_dir: str) -> Tuple[int, int, List[str]]:
        """Validate animation/VR scene data"""
        
        animation_path = Path(animation_dir)
        if not animation_path.exists():
            return 0, 0, [f"Animation directory not found: {animation_dir}"]
        
        scene_files = list(animation_path.glob('*.json'))
        # Remove catalog file from validation
        scene_files = [f for f in scene_files if f.name != 'scene_catalog.json']
        
        if not scene_files:
            return 0, 0, ["No scene files found"]
        
        valid_count = 0
        total_count = len(scene_files)
        errors = []
        
        console.print(f"\n[blue]🎬 Validating {total_count} VR scene files...[/blue]")
        
        for scene_file in track(scene_files, description="Validating VR scenes..."):
            try:
                with open(scene_file, 'r') as f:
                    scene_data = json.load(f)
                
                self._validate_vr_scene(scene_data)
                valid_count += 1
                
            except ValidationError as e:
                errors.append(f"{scene_file.name}: {e}")
            except Exception as e:
                errors.append(f"{scene_file.name}: {str(e)}")
        
        return valid_count, total_count, errors
    
    def _validate_vr_scene(self, scene: Dict):
        """Validate VR scene data"""
        
        required_fields = ['id', 'name', 'organization_name', 'environment', 'avatars', 'positions']
        
        for field in required_fields:
            if field not in scene:
                raise ValidationError(f"Missing required field: {field}")
        
        # Validate environment
        if not isinstance(scene['environment'], dict):
            raise ValidationError("environment must be an object")
        
        env_required = ['type', 'name', 'lighting', 'acoustics']
        for field in env_required:
            if field not in scene['environment']:
                raise ValidationError(f"environment missing field: {field}")
        
        # Validate avatars
        if not isinstance(scene['avatars'], list):
            raise ValidationError("avatars must be an array")
        
        for i, avatar in enumerate(scene['avatars']):
            if not isinstance(avatar, dict):
                raise ValidationError(f"avatars[{i}] must be an object")
            
            avatar_required = ['person_id', 'name', 'role', 'appearance_style']
            for field in avatar_required:
                if field not in avatar:
                    raise ValidationError(f"avatars[{i}] missing field: {field}")
        
        # Validate positions
        if not isinstance(scene['positions'], list):
            raise ValidationError("positions must be an array")
    
    def generate_report(self, results: Dict[str, Tuple[int, int, List[str]]]) -> str:
        """Generate validation report"""
        
        table = Table(title="Data Validation Report")
        table.add_column("Data Type", style="cyan")
        table.add_column("Valid", style="green")
        table.add_column("Total", style="blue")
        table.add_column("Success Rate", style="yellow")
        table.add_column("Errors", style="red")
        
        total_valid = 0
        total_items = 0
        
        for data_type, (valid, total, errors) in results.items():
            success_rate = f"{(valid/total)*100:.1f}%" if total > 0 else "N/A"
            error_count = len(errors)
            
            table.add_row(
                data_type.title(),
                str(valid),
                str(total),
                success_rate,
                str(error_count) if error_count > 0 else "0"
            )
            
            total_valid += valid
            total_items += total
        
        # Add summary row
        overall_rate = f"{(total_valid/total_items)*100:.1f}%" if total_items > 0 else "0%"
        table.add_row(
            "[bold]TOTAL[/bold]",
            f"[bold]{total_valid}[/bold]",
            f"[bold]{total_items}[/bold]",
            f"[bold]{overall_rate}[/bold]",
            ""
        )
        
        console.print(table)
        
        # Show error details
        for data_type, (_, _, errors) in results.items():
            if errors:
                console.print(f"\n[red]❌ {data_type.title()} Errors:[/red]")
                for error in errors[:10]:  # Show first 10 errors
                    console.print(f"  • {error}")
                
                if len(errors) > 10:
                    console.print(f"  ... and {len(errors) - 10} more errors")
        
        return f"Validation complete: {total_valid}/{total_items} items valid ({overall_rate})"

@click.command()
@click.option('--synthetic-dir', help='Synthetic data directory')
@click.option('--voice-dir', help='Voice generation directory')
@click.option('--animation-dir', help='Animation data directory')
@click.option('--schema-dir', default='shared/schemas', help='Schema directory')
def main(synthetic_dir: Optional[str], voice_dir: Optional[str], 
         animation_dir: Optional[str], schema_dir: str):
    """Validate all generated data"""
    
    console.print("[bold blue]🔍 Data Validation Suite[/bold blue]")
    console.print("=" * 50)
    
    validator = DataValidator(schema_dir)
    
    if not validator.schemas:
        console.print("[red]❌ No schemas loaded. Cannot validate data.[/red]")
        return
    
    results = {}
    
    # Validate synthetic data
    if synthetic_dir:
        synthetic_path = Path(synthetic_dir)
        
        if (synthetic_path / 'organizations').exists():
            org_result = validator.validate_organizations(synthetic_path / 'organizations')
            results['organizations'] = org_result
        
        if (synthetic_path / 'people').exists():
            people_result = validator.validate_people(synthetic_path / 'people')
            results['people'] = people_result
        
        if (synthetic_path / 'scenarios').exists():
            scenario_result = validator.validate_scenarios(synthetic_path / 'scenarios')
            results['scenarios'] = scenario_result
    
    # Validate voice data
    if voice_dir:
        voice_result = validator.validate_voice_data(voice_dir)
        results['voice_data'] = voice_result
    
    # Validate animation data
    if animation_dir:
        animation_result = validator.validate_animation_data(animation_dir)
        results['vr_scenes'] = animation_result
    
    if not results:
        console.print("[yellow]⚠️ No data directories specified or found.[/yellow]")
        console.print("Use --synthetic-dir, --voice-dir, and/or --animation-dir")
        return
    
    # Generate and display report
    summary = validator.generate_report(results)
    
    console.print(f"\n[bold green]✅ {summary}[/bold green]")

if __name__ == '__main__':
    main()