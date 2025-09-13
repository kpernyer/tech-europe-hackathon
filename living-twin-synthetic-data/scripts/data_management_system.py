#!/usr/bin/env python3
"""
Production Data Management System
Handles data archival, ID management, and generation tracking to prevent conflicts
and ensure reproducible data generation across multiple runs.
"""

import json
import shutil
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Any
from datetime import datetime
import uuid

class DataManagementSystem:
    """Production data management with ID tracking and archival."""
    
    def __init__(self):
        self.base_path = Path("/Users/kenper/src/aprio-one/tech-europe-hackathon/living-twin-synthetic-data")
        self.generated_path = self.base_path / "generated"
        self.production_path = self.base_path / "production_data"
        self.archives_path = self.base_path / "archives"
        self.id_registry_path = self.base_path / "id_registry"
        
        # Create directory structure
        self.production_path.mkdir(exist_ok=True)
        self.archives_path.mkdir(exist_ok=True)
        self.id_registry_path.mkdir(exist_ok=True)
        
        # ID management files
        self.org_id_registry = self.id_registry_path / "organization_ids.json"
        self.persona_id_registry = self.id_registry_path / "persona_ids.json"
        self.message_id_registry = self.id_registry_path / "message_ids.json"
        self.voice_id_registry = self.id_registry_path / "voice_ids.json"
        self.avatar_id_registry = self.id_registry_path / "avatar_ids.json"
        self.generation_log = self.id_registry_path / "generation_history.json"

    def initialize_id_registries(self):
        """Initialize ID tracking registries if they don't exist."""
        
        registries = {
            self.org_id_registry: {
                "next_id": 0,
                "used_ids": [],
                "reserved_ranges": {},
                "generation_batches": {}
            },
            self.persona_id_registry: {
                "next_id": 0,
                "used_ids": [],
                "persona_mappings": {},
                "generation_batches": {}
            },
            self.message_id_registry: {
                "used_message_ids": [],
                "generation_sessions": {}
            },
            self.voice_id_registry: {
                "elevenlabs_mappings": {},
                "used_voice_ids": [],
                "generation_batches": {}
            },
            self.avatar_id_registry: {
                "beyond_presence_mappings": {},
                "used_avatar_ids": [],
                "generation_batches": {}
            },
            self.generation_log: {
                "generations": [],
                "current_version": "2.0",
                "schema_versions": {"1.0": "basic", "2.0": "intent_based"}
            }
        }
        
        for registry_file, default_content in registries.items():
            if not registry_file.exists():
                with open(registry_file, 'w') as f:
                    json.dump(default_content, f, indent=2)
                print(f"✓ Initialized {registry_file.name}")

    def scan_existing_ids(self):
        """Scan existing generated data to populate ID registries."""
        
        print("📊 Scanning existing data for ID registration...")
        
        # Scan organizations
        org_ids = self._scan_organization_ids()
        self._register_organization_ids(org_ids)
        
        # Scan personas
        persona_ids = self._scan_persona_ids()
        self._register_persona_ids(persona_ids)
        
        # Scan messages
        message_ids = self._scan_message_ids()
        self._register_message_ids(message_ids)
        
        # Scan voice/avatar mappings
        voice_mappings, avatar_mappings = self._scan_multimodal_ids()
        self._register_multimodal_ids(voice_mappings, avatar_mappings)
        
        print(f"   ✓ Registered {len(org_ids)} organization IDs")
        print(f"   ✓ Registered {len(persona_ids)} persona IDs") 
        print(f"   ✓ Registered {len(message_ids)} message IDs")
        print(f"   ✓ Registered {len(voice_mappings)} voice mappings")
        print(f"   ✓ Registered {len(avatar_mappings)} avatar mappings")

    def _scan_organization_ids(self) -> List[str]:
        """Scan for existing organization IDs."""
        org_ids = []
        orgs_path = self.generated_path / "structured" / "organizations"
        
        if orgs_path.exists():
            for org_dir in orgs_path.iterdir():
                if org_dir.is_dir() and org_dir.name.startswith('org_'):
                    org_ids.append(org_dir.name)
        
        return sorted(org_ids)

    def _scan_persona_ids(self) -> List[str]:
        """Scan for existing persona IDs."""
        persona_ids = []
        
        # From unified registry
        registry_file = self.generated_path / "personas" / "demo-unified-personas" / "unified_persona_registry.json"
        if registry_file.exists():
            with open(registry_file, 'r') as f:
                registry_data = json.load(f)
                persona_ids.extend(registry_data.get("personas", {}).keys())
        
        # From individual profiles
        individual_path = self.generated_path / "personas" / "individual_profiles"
        if individual_path.exists():
            for persona_dir in individual_path.iterdir():
                if persona_dir.is_dir() and persona_dir.name.startswith('persona_'):
                    if persona_dir.name not in persona_ids:
                        persona_ids.append(persona_dir.name)
        
        return sorted(persona_ids)

    def _scan_message_ids(self) -> List[str]:
        """Scan for existing message IDs in communication flows."""
        message_ids = []
        
        # Scan organization flows
        orgs_path = self.generated_path / "structured" / "organizations"
        if orgs_path.exists():
            for org_dir in orgs_path.iterdir():
                flows_dir = org_dir / "flows"
                if flows_dir.exists():
                    for flow_file in flows_dir.glob("*.json"):
                        try:
                            with open(flow_file, 'r') as f:
                                flow_data = json.load(f)
                                
                            # Extract message IDs from different flow types
                            if "message_id" in flow_data:
                                message_ids.append(flow_data["message_id"])
                            
                            if "flow_steps" in flow_data:
                                for step in flow_data["flow_steps"]:
                                    if "message_id" in step:
                                        message_ids.append(step["message_id"])
                        except:
                            continue
        
        return list(set(message_ids))  # Remove duplicates

    def _scan_multimodal_ids(self) -> tuple:
        """Scan for voice and avatar ID mappings."""
        voice_mappings = {}
        avatar_mappings = {}
        
        # From persona registry
        registry_file = self.generated_path / "personas" / "demo-unified-personas" / "unified_persona_registry.json"
        if registry_file.exists():
            with open(registry_file, 'r') as f:
                registry_data = json.load(f)
                
                for persona_id, persona_data in registry_data.get("personas", {}).items():
                    system_ids = persona_data.get("system_ids", {})
                    
                    if "elevenlabs_voice_id" in system_ids:
                        voice_mappings[persona_id] = system_ids["elevenlabs_voice_id"]
                    
                    if "beyond_presence_avatar_id" in system_ids:
                        avatar_mappings[persona_id] = system_ids["beyond_presence_avatar_id"]
        
        return voice_mappings, avatar_mappings

    def _register_organization_ids(self, org_ids: List[str]):
        """Register organization IDs in the registry."""
        with open(self.org_id_registry, 'r') as f:
            registry = json.load(f)
        
        # Extract numeric IDs and find next available
        numeric_ids = []
        for org_id in org_ids:
            try:
                num_id = int(org_id.replace('org_', ''))
                numeric_ids.append(num_id)
            except ValueError:
                continue
        
        registry["used_ids"] = org_ids
        registry["next_id"] = max(numeric_ids) + 1 if numeric_ids else 0
        registry["generation_batches"]["current_scan"] = {
            "timestamp": datetime.now().isoformat(),
            "count": len(org_ids),
            "ids": org_ids
        }
        
        with open(self.org_id_registry, 'w') as f:
            json.dump(registry, f, indent=2)

    def _register_persona_ids(self, persona_ids: List[str]):
        """Register persona IDs in the registry."""
        with open(self.persona_id_registry, 'r') as f:
            registry = json.load(f)
        
        registry["used_ids"] = persona_ids
        registry["persona_mappings"] = {pid: {"status": "active", "generation": "current"} for pid in persona_ids}
        registry["generation_batches"]["current_scan"] = {
            "timestamp": datetime.now().isoformat(),
            "count": len(persona_ids),
            "ids": persona_ids
        }
        
        with open(self.persona_id_registry, 'w') as f:
            json.dump(registry, f, indent=2)

    def _register_message_ids(self, message_ids: List[str]):
        """Register message IDs in the registry."""
        with open(self.message_id_registry, 'r') as f:
            registry = json.load(f)
        
        registry["used_message_ids"] = message_ids
        registry["generation_sessions"]["current_scan"] = {
            "timestamp": datetime.now().isoformat(),
            "count": len(message_ids),
            "session_id": f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
        with open(self.message_id_registry, 'w') as f:
            json.dump(registry, f, indent=2)

    def _register_multimodal_ids(self, voice_mappings: Dict, avatar_mappings: Dict):
        """Register voice and avatar ID mappings."""
        # Voice IDs
        with open(self.voice_id_registry, 'r') as f:
            voice_registry = json.load(f)
        
        voice_registry["elevenlabs_mappings"] = voice_mappings
        voice_registry["used_voice_ids"] = list(voice_mappings.values())
        
        with open(self.voice_id_registry, 'w') as f:
            json.dump(voice_registry, f, indent=2)
        
        # Avatar IDs
        with open(self.avatar_id_registry, 'r') as f:
            avatar_registry = json.load(f)
        
        avatar_registry["beyond_presence_mappings"] = avatar_mappings
        avatar_registry["used_avatar_ids"] = list(avatar_mappings.values())
        
        with open(self.avatar_id_registry, 'w') as f:
            json.dump(avatar_registry, f, indent=2)

    def create_production_deployment(self):
        """Create production-ready deployment of all generated data."""
        
        print("🚀 Creating Production Deployment...")
        
        # Create deployment metadata
        deployment_id = f"deployment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        deployment_path = self.production_path / deployment_id
        deployment_path.mkdir(exist_ok=True)
        
        # Copy all generated data to production
        if self.generated_path.exists():
            shutil.copytree(
                self.generated_path,
                deployment_path / "data",
                ignore=shutil.ignore_patterns('*.pyc', '__pycache__', '.DS_Store')
            )
        
        # Copy ID registries
        shutil.copytree(self.id_registry_path, deployment_path / "id_registries")
        
        # Copy scripts for reproducibility
        scripts_dest = deployment_path / "scripts"
        scripts_dest.mkdir(exist_ok=True)
        
        for script_file in (self.base_path / "scripts").glob("*.py"):
            shutil.copy2(script_file, scripts_dest)
        
        # Create deployment manifest
        deployment_manifest = self._create_deployment_manifest(deployment_id, deployment_path)
        
        manifest_file = deployment_path / "DEPLOYMENT_MANIFEST.json"
        with open(manifest_file, 'w') as f:
            json.dump(deployment_manifest, f, indent=2)
        
        # Create deployment README
        self._create_deployment_readme(deployment_path, deployment_manifest)
        
        # Create symlink to latest deployment
        latest_link = self.production_path / "latest"
        if latest_link.exists():
            latest_link.unlink()
        latest_link.symlink_to(deployment_id)
        
        print(f"   ✓ Created deployment: {deployment_id}")
        print(f"   ✓ Data path: {deployment_path}")
        print(f"   ✓ Latest symlink updated")
        
        return deployment_path, deployment_manifest

    def _create_deployment_manifest(self, deployment_id: str, deployment_path: Path) -> Dict:
        """Create comprehensive deployment manifest."""
        
        # Calculate data statistics
        stats = self._calculate_data_statistics(deployment_path / "data")
        
        # Create checksums for data integrity
        checksums = self._create_data_checksums(deployment_path / "data")
        
        manifest = {
            "deployment_info": {
                "deployment_id": deployment_id,
                "created_at": datetime.now().isoformat(),
                "system_version": "2.0",
                "schema_version": "intent_based_v2",
                "generator_commit": self._get_git_commit_hash()
            },
            "data_statistics": stats,
            "data_integrity": {
                "checksums": checksums,
                "verification_method": "sha256"
            },
            "id_ranges": self._get_id_ranges(),
            "generation_config": {
                "reproducible": True,
                "random_seed_managed": True,
                "id_conflict_prevention": True
            },
            "system_requirements": {
                "python_version": "3.8+",
                "required_packages": ["json", "pathlib", "datetime", "uuid", "hashlib"],
                "optional_integrations": ["elevenlabs", "beyond_presence"]
            },
            "usage_instructions": {
                "regeneration": "Run scripts/regenerate_from_manifest.py",
                "id_reservation": "Use scripts/reserve_id_ranges.py for new generations",
                "data_merging": "Use scripts/merge_datasets.py for combining deployments"
            }
        }
        
        return manifest

    def _calculate_data_statistics(self, data_path: Path) -> Dict:
        """Calculate comprehensive data statistics."""
        
        stats = {
            "organizations": {"count": 0, "with_flows": 0, "with_enhanced_flows": 0},
            "personas": {"count": 0, "individual_profiles": 0},
            "communication_flows": {"basic": 0, "enhanced": 0, "intent_based": 0},
            "voice_integration": {"mappings": 0, "samples": 0},
            "avatar_integration": {"mappings": 0, "behavior_profiles": 0},
            "total_files": 0,
            "total_size_mb": 0
        }
        
        if not data_path.exists():
            return stats
        
        # Count organizations
        orgs_path = data_path / "structured" / "organizations"
        if orgs_path.exists():
            org_dirs = [d for d in orgs_path.iterdir() if d.is_dir() and d.name.startswith('org_')]
            stats["organizations"]["count"] = len(org_dirs)
            
            for org_dir in org_dirs:
                flows_dir = org_dir / "flows"
                if flows_dir.exists():
                    stats["organizations"]["with_flows"] += 1
                    
                    flow_files = list(flows_dir.glob("*.json"))
                    enhanced_files = [f for f in flow_files if "enhanced" in f.name]
                    intent_files = [f for f in flow_files if "intent" in f.name]
                    
                    if enhanced_files:
                        stats["organizations"]["with_enhanced_flows"] += 1
                        stats["communication_flows"]["enhanced"] += len(enhanced_files)
                    
                    if intent_files:
                        stats["communication_flows"]["intent_based"] += len(intent_files)
                    
                    basic_files = [f for f in flow_files if "enhanced" not in f.name and "intent" not in f.name]
                    stats["communication_flows"]["basic"] += len(basic_files)
        
        # Count personas
        personas_path = data_path / "personas"
        if personas_path.exists():
            registry_file = personas_path / "demo-unified-personas" / "unified_persona_registry.json"
            if registry_file.exists():
                with open(registry_file, 'r') as f:
                    registry_data = json.load(f)
                    stats["personas"]["count"] = registry_data["generation_info"]["total_personas"]
            
            individual_path = personas_path / "individual_profiles"
            if individual_path.exists():
                individual_dirs = [d for d in individual_path.iterdir() if d.is_dir()]
                stats["personas"]["individual_profiles"] = len(individual_dirs)
        
        # Calculate total size and file count
        total_size = 0
        total_files = 0
        
        for file_path in data_path.rglob("*"):
            if file_path.is_file():
                total_files += 1
                total_size += file_path.stat().st_size
        
        stats["total_files"] = total_files
        stats["total_size_mb"] = round(total_size / (1024 * 1024), 2)
        
        return stats

    def _create_data_checksums(self, data_path: Path) -> Dict[str, str]:
        """Create checksums for data integrity verification."""
        
        checksums = {}
        
        if not data_path.exists():
            return checksums
        
        # Create checksums for key data files
        key_files = [
            "structured/organizations/*/org_*.json",
            "personas/*/unified_persona_registry.json",
            "*/individual_profiles/*/persona_*_profile.json"
        ]
        
        for pattern in key_files:
            for file_path in data_path.glob(pattern):
                if file_path.is_file():
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()
                        relative_path = str(file_path.relative_to(data_path))
                        checksums[relative_path] = file_hash
        
        return checksums

    def _get_id_ranges(self) -> Dict:
        """Get current ID ranges from registries."""
        
        ranges = {}
        
        # Organization IDs
        if self.org_id_registry.exists():
            with open(self.org_id_registry, 'r') as f:
                org_registry = json.load(f)
                ranges["organizations"] = {
                    "next_available": org_registry.get("next_id", 0),
                    "reserved_ranges": org_registry.get("reserved_ranges", {}),
                    "total_used": len(org_registry.get("used_ids", []))
                }
        
        # Persona IDs
        if self.persona_id_registry.exists():
            with open(self.persona_id_registry, 'r') as f:
                persona_registry = json.load(f)
                ranges["personas"] = {
                    "total_used": len(persona_registry.get("used_ids", [])),
                    "active_mappings": len(persona_registry.get("persona_mappings", {}))
                }
        
        return ranges

    def _get_git_commit_hash(self) -> str:
        """Get current git commit hash if available."""
        try:
            import subprocess
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                  capture_output=True, text=True, cwd=self.base_path)
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except:
            return "unknown"

    def _create_deployment_readme(self, deployment_path: Path, manifest: Dict):
        """Create deployment README with usage instructions."""
        
        readme_content = f"""# Living Twin Data Deployment - {manifest['deployment_info']['deployment_id']}

## Deployment Information
- **Created**: {manifest['deployment_info']['created_at'][:19]} UTC
- **System Version**: {manifest['deployment_info']['system_version']}
- **Schema**: {manifest['deployment_info']['schema_version']}
- **Generator Commit**: {manifest['deployment_info']['generator_commit']}

## Data Statistics
- **Organizations**: {manifest['data_statistics']['organizations']['count']} total
  - With Flows: {manifest['data_statistics']['organizations']['with_flows']}
  - With Enhanced Flows: {manifest['data_statistics']['organizations']['with_enhanced_flows']}
- **Personas**: {manifest['data_statistics']['personas']['count']} unified, {manifest['data_statistics']['personas']['individual_profiles']} individual profiles
- **Communication Flows**: 
  - Basic: {manifest['data_statistics']['communication_flows']['basic']}
  - Enhanced: {manifest['data_statistics']['communication_flows']['enhanced']}
  - Intent-Based: {manifest['data_statistics']['communication_flows']['intent_based']}
- **Total Size**: {manifest['data_statistics']['total_size_mb']} MB ({manifest['data_statistics']['total_files']} files)

## ID Ranges (Prevent Conflicts)
- **Organizations**: Next available ID: {manifest['id_ranges']['organizations']['next_available']}
- **Personas**: {manifest['id_ranges']['personas']['total_used']} IDs used

## Directory Structure
```
{manifest['deployment_info']['deployment_id']}/
├── data/                          # All generated data
│   ├── structured/organizations/  # Organization profiles and flows
│   ├── personas/                 # Persona profiles and registries
│   ├── voice_integration/        # Voice specifications
│   └── avatar_integration/       # Avatar behavior mappings
├── id_registries/               # ID tracking and conflict prevention
├── scripts/                     # Generation scripts for reproducibility
├── DEPLOYMENT_MANIFEST.json     # This deployment's metadata
└── README.md                    # This file
```

## Usage Instructions

### Regenerate This Dataset
```bash
# Use the preserved scripts and ID registries
python scripts/regenerate_from_manifest.py DEPLOYMENT_MANIFEST.json
```

### Generate New Data (Conflict-Free)
```bash
# Reserve new ID ranges to prevent conflicts
python scripts/reserve_id_ranges.py --orgs 100 --personas 10

# Generate with reserved IDs
python scripts/generate_with_reserved_ids.py
```

### Merge with Other Datasets
```bash
# Safely merge multiple deployments
python scripts/merge_datasets.py deployment_A deployment_B --output merged_dataset
```

### Verify Data Integrity
```bash
# Verify checksums match
python scripts/verify_deployment.py DEPLOYMENT_MANIFEST.json
```

## Data Integrity
- **Verification Method**: SHA256 checksums
- **Checksums**: {len(manifest['data_integrity']['checksums'])} files tracked
- **ID Conflict Prevention**: ✅ Enabled
- **Reproducible Generation**: ✅ Enabled

## Integration Ready
- **ElevenLabs Voice**: {manifest['data_statistics']['voice_integration']['mappings']} persona mappings ready
- **Beyond Presence Avatar**: {manifest['data_statistics']['avatar_integration']['mappings']} behavior profiles ready
- **Intent-Based Communication**: {manifest['data_statistics']['communication_flows']['intent_based']} examples implemented

---
*This deployment contains production-ready Living Twin synthetic data with sophisticated intent-based communication modeling.*
"""
        
        readme_file = deployment_path / "README.md"
        with open(readme_file, 'w') as f:
            f.write(readme_content)

    def create_archive_backup(self, deployment_path: Path):
        """Create compressed archive backup of deployment."""
        
        print("📦 Creating Archive Backup...")
        
        deployment_id = deployment_path.name
        archive_file = self.archives_path / f"{deployment_id}.tar.gz"
        
        # Create compressed archive
        import tarfile
        with tarfile.open(archive_file, "w:gz") as tar:
            tar.add(deployment_path, arcname=deployment_id)
        
        # Calculate archive size
        archive_size_mb = round(archive_file.stat().st_size / (1024 * 1024), 2)
        
        print(f"   ✓ Archive created: {archive_file}")
        print(f"   ✓ Archive size: {archive_size_mb} MB")
        
        return archive_file

    def run_production_deployment(self):
        """Run complete production deployment process."""
        
        print("🏭 Starting Production Data Deployment Process...")
        print("=" * 70)
        
        # 1. Initialize ID management
        print("1️⃣ Initializing ID Management System...")
        self.initialize_id_registries()
        
        # 2. Scan and register existing IDs
        print("\n2️⃣ Scanning and Registering Existing Data...")
        self.scan_existing_ids()
        
        # 3. Create production deployment
        print("\n3️⃣ Creating Production Deployment...")
        deployment_path, manifest = self.create_production_deployment()
        
        # 4. Create archive backup
        print("\n4️⃣ Creating Archive Backup...")
        archive_file = self.create_archive_backup(deployment_path)
        
        # 5. Update generation log
        print("\n5️⃣ Updating Generation History...")
        self._update_generation_log(deployment_path.name, manifest)
        
        print("\n" + "=" * 70)
        print("✅ Production Deployment Complete!")
        print(f"\n📁 Production Data: {self.production_path / 'latest'}")
        print(f"📦 Archive Backup: {archive_file}")
        print(f"🆔 ID Registries: {self.id_registry_path}")
        print(f"\n🚀 Ready for:")
        print("   • ElevenLabs voice generation")
        print("   • Beyond Presence avatar integration") 
        print("   • Conflict-free dataset expansion")
        print("   • Production system integration")

    def _update_generation_log(self, deployment_id: str, manifest: Dict):
        """Update the generation history log."""
        
        with open(self.generation_log, 'r') as f:
            log = json.load(f)
        
        generation_entry = {
            "deployment_id": deployment_id,
            "timestamp": datetime.now().isoformat(),
            "system_version": manifest["deployment_info"]["system_version"],
            "data_statistics": manifest["data_statistics"],
            "id_ranges": manifest["id_ranges"],
            "generator_commit": manifest["deployment_info"]["generator_commit"]
        }
        
        log["generations"].append(generation_entry)
        
        with open(self.generation_log, 'w') as f:
            json.dump(log, f, indent=2)
        
        print(f"   ✓ Added generation entry: {deployment_id}")


def main():
    """Main execution function."""
    dms = DataManagementSystem()
    dms.run_production_deployment()

if __name__ == "__main__":
    main()