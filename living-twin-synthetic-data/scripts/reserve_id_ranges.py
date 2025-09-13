#!/usr/bin/env python3
"""
ID Range Reservation System
Reserves ID ranges for future data generation to prevent conflicts when merging datasets.
"""

import json
import argparse
from pathlib import Path
from datetime import datetime

def reserve_id_ranges(base_path: Path, org_count: int, persona_count: int, reservation_name: str):
    """Reserve ID ranges for future generation."""
    
    id_registry_path = base_path / "id_registry"
    org_registry_file = id_registry_path / "organization_ids.json"
    persona_registry_file = id_registry_path / "persona_ids.json"
    
    print(f"🎯 Reserving ID Ranges for '{reservation_name}'...")
    
    # Reserve organization IDs
    if org_registry_file.exists():
        with open(org_registry_file, 'r') as f:
            org_registry = json.load(f)
        
        start_org_id = org_registry["next_id"]
        end_org_id = start_org_id + org_count - 1
        
        # Update registry
        org_registry["next_id"] = end_org_id + 1
        org_registry["reserved_ranges"][reservation_name] = {
            "start": start_org_id,
            "end": end_org_id,
            "count": org_count,
            "reserved_at": datetime.now().isoformat(),
            "status": "reserved"
        }
        
        with open(org_registry_file, 'w') as f:
            json.dump(org_registry, f, indent=2)
        
        print(f"   ✓ Organization IDs: {start_org_id} - {end_org_id} ({org_count} IDs)")
    
    # Reserve persona IDs (simpler approach - just track count)
    if persona_registry_file.exists():
        with open(persona_registry_file, 'r') as f:
            persona_registry = json.load(f)
        
        current_count = len(persona_registry.get("used_ids", []))
        
        if "reserved_ranges" not in persona_registry:
            persona_registry["reserved_ranges"] = {}
        
        persona_registry["reserved_ranges"][reservation_name] = {
            "count": persona_count,
            "reserved_at": datetime.now().isoformat(),
            "status": "reserved"
        }
        
        with open(persona_registry_file, 'w') as f:
            json.dump(persona_registry, f, indent=2)
        
        print(f"   ✓ Persona slots: {persona_count} reserved")
    
    print(f"✅ ID ranges reserved for '{reservation_name}'")
    print(f"   Use these ranges in your next generation run to avoid conflicts")

def main():
    parser = argparse.ArgumentParser(description="Reserve ID ranges for future data generation")
    parser.add_argument("--orgs", type=int, default=100, help="Number of organization IDs to reserve")
    parser.add_argument("--personas", type=int, default=10, help="Number of persona slots to reserve")
    parser.add_argument("--name", type=str, default=f"batch_{datetime.now().strftime('%Y%m%d_%H%M')}", 
                       help="Name for this reservation")
    
    args = parser.parse_args()
    
    base_path = Path(__file__).parent.parent
    reserve_id_ranges(base_path, args.orgs, args.personas, args.name)

if __name__ == "__main__":
    main()