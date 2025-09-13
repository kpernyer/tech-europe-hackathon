#!/usr/bin/env python3
"""
Dataset Merging System
Safely merges multiple Living Twin datasets while preventing ID conflicts.
"""

import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set

def merge_datasets(base_path: Path, deployment_paths: List[Path], output_name: str):
    """Merge multiple datasets into a single unified dataset."""
    
    print(f"🔄 Merging {len(deployment_paths)} datasets into '{output_name}'...")
    
    # Create output directory
    output_path = base_path / "production_data" / output_name
    output_path.mkdir(exist_ok=True)
    
    # Initialize merge tracking
    merge_manifest = {
        "merge_info": {
            "merge_id": output_name,
            "created_at": datetime.now().isoformat(),
            "source_deployments": [p.name for p in deployment_paths],
            "merge_strategy": "id_conflict_resolution"
        },
        "merged_statistics": {
            "organizations": {"total": 0, "conflicts_resolved": 0},
            "personas": {"total": 0, "conflicts_resolved": 0},
            "communication_flows": {"total": 0},
            "total_files": 0
        },
        "id_mappings": {
            "organization_remappings": {},
            "persona_remappings": {},
            "message_remappings": {}
        }
    }
    
    # Track used IDs to prevent conflicts
    used_org_ids = set()
    used_persona_ids = set()
    used_message_ids = set()
    
    # Create merged data structure
    merged_data_path = output_path / "data"
    merged_data_path.mkdir(exist_ok=True)
    
    org_counter = 0
    persona_counter = 0
    
    for i, deployment_path in enumerate(deployment_paths):
        print(f"\n   Processing deployment {i+1}/{len(deployment_paths)}: {deployment_path.name}")
        
        data_path = deployment_path / "data"
        if not data_path.exists():
            print(f"   ⚠️  No data directory found in {deployment_path.name}, skipping...")
            continue
        
        # Merge organizations
        orgs_merged, org_counter = merge_organizations(
            data_path, merged_data_path, used_org_ids, org_counter, merge_manifest
        )
        
        # Merge personas  
        personas_merged, persona_counter = merge_personas(
            data_path, merged_data_path, used_persona_ids, persona_counter, merge_manifest
        )
        
        # Merge other data (voice, avatar, etc.)
        merge_auxiliary_data(data_path, merged_data_path)
        
        print(f"   ✓ Merged {orgs_merged} organizations, {personas_merged} personas")
    
    # Create merged registries
    create_merged_registries(output_path, merge_manifest)
    
    # Save merge manifest
    manifest_file = output_path / "MERGE_MANIFEST.json"
    with open(manifest_file, 'w') as f:
        json.dump(merge_manifest, f, indent=2)
    
    # Create merge README
    create_merge_readme(output_path, merge_manifest)
    
    print(f"\n✅ Dataset merge complete!")
    print(f"   📁 Merged dataset: {output_path}")
    print(f"   📊 Total organizations: {merge_manifest['merged_statistics']['organizations']['total']}")
    print(f"   👥 Total personas: {merge_manifest['merged_statistics']['personas']['total']}")
    print(f"   🔧 ID conflicts resolved: {merge_manifest['merged_statistics']['organizations']['conflicts_resolved']}")

def merge_organizations(data_path: Path, merged_path: Path, used_ids: Set, 
                       counter: int, manifest: Dict) -> tuple:
    """Merge organization data with conflict resolution."""
    
    orgs_source = data_path / "structured" / "organizations"
    orgs_dest = merged_path / "structured" / "organizations"
    orgs_dest.mkdir(parents=True, exist_ok=True)
    
    merged_count = 0
    conflicts_resolved = 0
    
    if orgs_source.exists():
        for org_dir in orgs_source.iterdir():
            if not (org_dir.is_dir() and org_dir.name.startswith('org_')):
                continue
            
            original_id = org_dir.name
            
            # Check for ID conflict
            if original_id in used_ids:
                # Resolve conflict by assigning new ID
                new_id = f"org_{counter:03d}"
                while new_id in used_ids:
                    counter += 1
                    new_id = f"org_{counter:03d}"
                
                conflicts_resolved += 1
                manifest["id_mappings"]["organization_remappings"][original_id] = new_id
                final_id = new_id
            else:
                final_id = original_id
            
            # Copy organization with potentially new ID
            dest_dir = orgs_dest / final_id
            shutil.copytree(org_dir, dest_dir)
            
            # Update JSON file with new ID if changed
            if final_id != original_id:
                update_organization_json_id(dest_dir, final_id)
            
            used_ids.add(final_id)
            merged_count += 1
            counter += 1
    
    manifest["merged_statistics"]["organizations"]["total"] += merged_count
    manifest["merged_statistics"]["organizations"]["conflicts_resolved"] += conflicts_resolved
    
    return merged_count, counter

def merge_personas(data_path: Path, merged_path: Path, used_ids: Set,
                  counter: int, manifest: Dict) -> tuple:
    """Merge persona data with conflict resolution."""
    
    personas_source = data_path / "personas"
    personas_dest = merged_path / "personas"
    
    merged_count = 0
    
    if personas_source.exists():
        # Copy entire personas directory structure
        if not personas_dest.exists():
            shutil.copytree(personas_source, personas_dest)
            
            # Count personas from registry
            registry_file = personas_dest / "demo-unified-personas" / "unified_persona_registry.json"
            if registry_file.exists():
                with open(registry_file, 'r') as f:
                    registry_data = json.load(f)
                    merged_count = registry_data["generation_info"]["total_personas"]
        else:
            # Merge with existing personas (more complex logic needed)
            # For now, skip if personas already exist
            print("   ⚠️  Persona merging with existing personas not yet implemented")
    
    manifest["merged_statistics"]["personas"]["total"] += merged_count
    
    return merged_count, counter

def merge_auxiliary_data(data_path: Path, merged_path: Path):
    """Merge auxiliary data like voice and avatar configurations."""
    
    auxiliary_dirs = ["voice_integration", "avatar_integration", "integration_status"]
    
    for aux_dir in auxiliary_dirs:
        source_dir = data_path / aux_dir
        if source_dir.exists():
            dest_dir = merged_path / aux_dir
            if not dest_dir.exists():
                shutil.copytree(source_dir, dest_dir)

def update_organization_json_id(org_dir: Path, new_id: str):
    """Update organization JSON file with new ID."""
    
    # Find the organization JSON file
    json_files = list(org_dir.glob("org_*.json"))
    if not json_files:
        return
    
    json_file = json_files[0]
    
    # Update the ID in the JSON
    with open(json_file, 'r') as f:
        org_data = json.load(f)
    
    org_data["id"] = new_id
    
    with open(json_file, 'w') as f:
        json.dump(org_data, f, indent=2)
    
    # Rename file if needed
    new_json_name = f"{new_id}.json"
    if json_file.name != new_json_name:
        json_file.rename(org_dir / new_json_name)

def create_merged_registries(output_path: Path, manifest: Dict):
    """Create updated ID registries for the merged dataset."""
    
    registries_path = output_path / "id_registries"
    registries_path.mkdir(exist_ok=True)
    
    # Create organization registry
    org_registry = {
        "next_id": manifest["merged_statistics"]["organizations"]["total"],
        "used_ids": list(range(manifest["merged_statistics"]["organizations"]["total"])),
        "reserved_ranges": {},
        "generation_batches": {
            "merged_dataset": {
                "timestamp": datetime.now().isoformat(),
                "count": manifest["merged_statistics"]["organizations"]["total"],
                "source_deployments": manifest["merge_info"]["source_deployments"]
            }
        },
        "id_remappings": manifest["id_mappings"]["organization_remappings"]
    }
    
    with open(registries_path / "organization_ids.json", 'w') as f:
        json.dump(org_registry, f, indent=2)

def create_merge_readme(output_path: Path, manifest: Dict):
    """Create README for merged dataset."""
    
    readme_content = f"""# Merged Living Twin Dataset - {manifest['merge_info']['merge_id']}

## Merge Information
- **Created**: {manifest['merge_info']['created_at'][:19]} UTC
- **Source Deployments**: {len(manifest['merge_info']['source_deployments'])}
- **Merge Strategy**: {manifest['merge_info']['merge_strategy']}

## Source Deployments
{chr(10).join([f"- {deployment}" for deployment in manifest['merge_info']['source_deployments']])}

## Merged Statistics
- **Organizations**: {manifest['merged_statistics']['organizations']['total']} total
  - ID Conflicts Resolved: {manifest['merged_statistics']['organizations']['conflicts_resolved']}
- **Personas**: {manifest['merged_statistics']['personas']['total']} total
- **Total Files**: {manifest['merged_statistics']['total_files']}

## ID Conflict Resolution
{len(manifest['id_mappings']['organization_remappings'])} organization IDs were remapped to prevent conflicts:

{chr(10).join([f"- {old_id} → {new_id}" for old_id, new_id in list(manifest['id_mappings']['organization_remappings'].items())[:10]])}
{"..." if len(manifest['id_mappings']['organization_remappings']) > 10 else ""}

## Usage
This merged dataset can be used just like any single deployment:

```bash
# Generate additional data without conflicts
python scripts/reserve_id_ranges.py --orgs 50 --name new_batch

# Verify data integrity
python scripts/verify_deployment.py MERGE_MANIFEST.json
```

---
*Merged dataset created by Living Twin Data Management System*
"""
    
    readme_file = output_path / "README.md"
    with open(readme_file, 'w') as f:
        f.write(readme_content)

def main():
    parser = argparse.ArgumentParser(description="Merge multiple Living Twin datasets")
    parser.add_argument("deployments", nargs="+", help="Deployment directories to merge")
    parser.add_argument("--output", required=True, help="Output dataset name")
    
    args = parser.parse_args()
    
    base_path = Path(__file__).parent.parent
    deployment_paths = [base_path / "production_data" / dep for dep in args.deployments]
    
    # Verify all deployments exist
    for path in deployment_paths:
        if not path.exists():
            print(f"❌ Deployment not found: {path}")
            return
    
    merge_datasets(base_path, deployment_paths, args.output)

if __name__ == "__main__":
    main()