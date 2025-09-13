#!/usr/bin/env python3
"""
Structured Data Generator
Creates organized data directory with markdown reports and JSON data files
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
import click
from rich.console import Console
from rich.progress import track

console = Console()

class StructuredDataGenerator:
    """Generates structured data organization with markdown reports"""
    
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        
    def load_organization_data(self) -> List[Dict]:
        """Load all organization data"""
        org_dir = self.input_dir / "organizations"
        organizations = []
        
        if not org_dir.exists():
            console.print(f"❌ Organizations directory not found: {org_dir}")
            return []
        
        for org_file in org_dir.glob("*.json"):
            try:
                with open(org_file, 'r') as f:
                    org_data = json.load(f)
                    organizations.append(org_data)
            except Exception as e:
                console.print(f"⚠️ Error loading {org_file}: {e}")
        
        console.print(f"📊 Loaded {len(organizations)} organizations")
        return organizations
    
    def load_people_for_org(self, org_id: str) -> List[Dict]:
        """Load people data for specific organization"""
        people_file = self.input_dir / "people" / f"people_{org_id}.json"
        
        if not people_file.exists():
            return []
        
        try:
            with open(people_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            console.print(f"⚠️ Error loading people for {org_id}: {e}")
            return []
    
    def load_scenarios_for_org(self, org_id: str) -> List[Dict]:
        """Load delegation scenarios for specific organization"""
        scenarios = []
        scenario_dir = self.input_dir / "scenarios"
        
        if not scenario_dir.exists():
            return []
        
        # Find all scenario files for this organization
        for scenario_file in scenario_dir.glob(f"scenario_{org_id}_*.json"):
            try:
                with open(scenario_file, 'r') as f:
                    scenario_data = json.load(f)
                    scenarios.append(scenario_data)
            except Exception as e:
                console.print(f"⚠️ Error loading scenario {scenario_file}: {e}")
        
        return scenarios
    
    def generate_organization_markdown(self, org: Dict, people: List[Dict], scenarios: List[Dict]) -> str:
        """Generate comprehensive markdown report for organization"""
        
        org_id = org.get("id", "unknown")
        org_name = org.get("name", "Unknown Organization")
        
        # Calculate stats
        total_people = len(people)
        total_scenarios = len(scenarios)
        departments = org.get("departments", [])
        
        # Safe formatting helpers
        size_val = org.get('size', 0)
        size_str = f"{size_val:,} employees" if isinstance(size_val, (int, float)) else str(size_val)
        profitable_str = '✅ Yes' if org.get('profitable', False) else '❌ No'
        
        # People by level
        level_counts = {}
        for person in people:
            level = person.get("level", "unknown")
            level_counts[level] = level_counts.get(level, 0) + 1
        
        # Scenario types
        scenario_types = {}
        for scenario in scenarios:
            stype = scenario.get("type", "unknown")
            scenario_types[stype] = scenario_types.get(stype, 0) + 1
        
        markdown = f"""# {org_name}
*Organization ID: `{org_id}`*

## 🏢 Company Overview

**Industry**: {org.get('industry', 'Unknown').title()}  
**Size**: {size_str}  
**Revenue**: {org.get('revenue_range', 'Unknown')}  
**Profitable**: {profitable_str}  
**Years in Business**: {org.get('years_in_business', 'Unknown')} years  
**Headquarters**: {org.get('headquarters', 'Unknown')}  

### Geographic Presence
{', '.join(org.get('regions', ['Unknown']))}

## 🏗️ Organizational Structure

**Structure Type**: {org.get('structure_type', 'Unknown').title()}  
**Delegation Culture**: {org.get('delegation_culture', 'Unknown').title()}  
**Decision Speed**: {org.get('decision_speed', 'Unknown').title()}  

### Maturity Metrics
- **Innovation Index**: {org.get('innovation_index', 0):.2f}
- **Digital Maturity**: {org.get('digital_maturity', 0):.2f}

## 🎯 Strategic Information

### Core Values
{self._format_list(org.get('values', []))}

### Strategic Priorities  
{self._format_list(org.get('strategic_priorities', []))}

### Products & Services
**Products**: {', '.join(org.get('products', ['None listed']))}  
**Services**: {', '.join(org.get('services', ['None listed']))}

## 👥 People Overview

**Total Employees**: {total_people:,}

### Hierarchy Distribution
{self._format_level_distribution(level_counts)}

### Departments
{self._format_list(departments)}

## 📋 Delegation Scenarios

**Total Scenarios**: {total_scenarios}

### Scenario Types
{self._format_scenario_types(scenario_types)}

### Recent Scenarios
{self._format_recent_scenarios(scenarios[:5])}

## 📊 Key Statistics

| Metric | Value |
|--------|-------|
| Employee Count | {total_people:,} |
| Delegation Scenarios | {total_scenarios} |
| Departments | {len(departments)} |
| Management Levels | {len(level_counts)} |
| Decision Culture | {org.get('delegation_culture', 'Unknown').title()} |
| Industry | {org.get('industry', 'Unknown').title()} |

## 🔧 Technical Data

- **Organization ID**: `{org_id}`
- **Data Files**: 
  - Organization: `{org_id}.json`
  - People: `people_{org_id}.json`
  - Scenarios: `scenario_{org_id}_*.json`

---
*Generated by Living Twin Synthetic Data System*
"""
        return markdown
    
    def _format_list(self, items: List[str]) -> str:
        """Format list as markdown bullet points"""
        if not items:
            return "- None listed"
        return '\n'.join([f"- {item}" for item in items])
    
    def _format_level_distribution(self, level_counts: Dict) -> str:
        """Format hierarchy level distribution"""
        if not level_counts:
            return "- No data available"
        
        level_names = {
            1: "Executive (Level 1)",
            2: "Senior Management (Level 2)", 
            3: "Middle Management (Level 3)",
            4: "Team Leads (Level 4)",
            5: "Individual Contributors (Level 5)"
        }
        
        result = []
        for level in sorted(level_counts.keys()):
            name = level_names.get(level, f"Level {level}")
            count = level_counts[level]
            result.append(f"- {name}: {count} people")
        
        return '\n'.join(result)
    
    def _format_scenario_types(self, scenario_types: Dict) -> str:
        """Format scenario type distribution"""
        if not scenario_types:
            return "- No scenarios available"
        
        result = []
        for stype, count in scenario_types.items():
            result.append(f"- {stype.replace('_', ' ').title()}: {count}")
        
        return '\n'.join(result)
    
    def _format_recent_scenarios(self, scenarios: List[Dict]) -> str:
        """Format recent scenarios list"""
        if not scenarios:
            return "- No scenarios available"
        
        result = []
        for scenario in scenarios:
            title = scenario.get('title', 'Untitled Scenario')
            stype = scenario.get('type', 'unknown').replace('_', ' ').title()
            scenario_id = scenario.get('id', 'unknown')
            result.append(f"- **{title}** ({stype}) - `{scenario_id}`")
        
        return '\n'.join(result)
    
    def create_organization_data_files(self, org: Dict, people: List[Dict], scenarios: List[Dict]):
        """Create JSON data files for organization"""
        
        org_id = org.get("id", "unknown")
        org_dir = self.output_dir / "organizations" / org_id
        
        # Create organization directory
        org_dir.mkdir(parents=True, exist_ok=True)
        
        # Save organization data
        with open(org_dir / f"{org_id}.json", 'w') as f:
            json.dump(org, f, indent=2)
        
        # Save people data
        if people:
            with open(org_dir / f"people_{org_id}.json", 'w') as f:
                json.dump(people, f, indent=2)
        
        # Save scenarios data
        if scenarios:
            with open(org_dir / f"scenarios_{org_id}.json", 'w') as f:
                json.dump(scenarios, f, indent=2)
    
    def create_delegation_summaries(self, all_scenarios: List[Dict]):
        """Create delegation pattern summaries"""
        
        delegation_dir = self.output_dir / "delegations"
        delegation_dir.mkdir(parents=True, exist_ok=True)
        
        # Group scenarios by type
        scenarios_by_type = {}
        for scenario in all_scenarios:
            stype = scenario.get('type', 'unknown')
            if stype not in scenarios_by_type:
                scenarios_by_type[stype] = []
            scenarios_by_type[stype].append(scenario)
        
        # Create summary for each type
        for stype, scenarios in scenarios_by_type.items():
            
            markdown = f"""# {stype.replace('_', ' ').title()} Scenarios

## Overview
Total scenarios of this type: {len(scenarios)}

## Patterns Observed

{self._analyze_delegation_patterns(scenarios)}

## Example Scenarios

{self._format_example_scenarios(scenarios[:10])}

---
*Generated by Living Twin Synthetic Data System*
"""
            
            with open(delegation_dir / f"{stype}_summary.md", 'w') as f:
                f.write(markdown)
    
    def _analyze_delegation_patterns(self, scenarios: List[Dict]) -> str:
        """Analyze delegation patterns in scenarios"""
        
        if not scenarios:
            return "- No scenarios available for analysis"
        
        # Analyze chain lengths
        chain_lengths = []
        response_types = {}
        
        for scenario in scenarios:
            chain = scenario.get('delegation_chain', [])
            chain_lengths.append(len(chain))
            
            for step in chain:
                response_type = step.get('response_type', 'unknown')
                response_types[response_type] = response_types.get(response_type, 0) + 1
        
        avg_length = sum(chain_lengths) / len(chain_lengths) if chain_lengths else 0
        
        patterns = [
            f"- Average delegation chain length: {avg_length:.1f} steps",
            f"- Shortest chain: {min(chain_lengths)} steps" if chain_lengths else "- No chain data",
            f"- Longest chain: {max(chain_lengths)} steps" if chain_lengths else "- No chain data",
            "",
            "**Response Type Distribution:**"
        ]
        
        for response_type, count in sorted(response_types.items()):
            patterns.append(f"- {response_type.replace('_', ' ').title()}: {count}")
        
        return '\n'.join(patterns)
    
    def _format_example_scenarios(self, scenarios: List[Dict]) -> str:
        """Format example scenarios"""
        
        if not scenarios:
            return "- No example scenarios available"
        
        examples = []
        for i, scenario in enumerate(scenarios, 1):
            title = scenario.get('title', 'Untitled')
            org_id = scenario.get('organization_id', 'unknown')
            chain_length = len(scenario.get('delegation_chain', []))
            
            examples.append(f"""### Example {i}: {title}
- **Organization**: `{org_id}`
- **Delegation Steps**: {chain_length}
- **Scenario ID**: `{scenario.get('id', 'unknown')}`
""")
        
        return '\n'.join(examples)
    
    def generate_structured_data(self):
        """Generate complete structured data organization"""
        
        console.print("🏗️ [bold blue]Generating Structured Data Organization[/bold blue]")
        console.print("=" * 60)
        
        # Load all data
        organizations = self.load_organization_data()
        all_scenarios = []
        
        if not organizations:
            console.print("❌ No organization data found")
            return
        
        # Process each organization
        for org in track(organizations, description="Processing organizations..."):
            org_id = org.get("id", "unknown")
            org_name = org.get("name", "Unknown")
            
            # Load related data
            people = self.load_people_for_org(org_id)
            scenarios = self.load_scenarios_for_org(org_id)
            all_scenarios.extend(scenarios)
            
            # Generate markdown report
            markdown = self.generate_organization_markdown(org, people, scenarios)
            
            # Create organization directory and files
            org_dir = self.output_dir / "organizations" / org_id
            org_dir.mkdir(parents=True, exist_ok=True)
            
            # Save markdown report
            with open(org_dir / f"{org_id}_report.md", 'w') as f:
                f.write(markdown)
            
            # Save JSON data files
            self.create_organization_data_files(org, people, scenarios)
        
        # Create delegation summaries
        console.print("📋 Generating delegation pattern summaries...")
        self.create_delegation_summaries(all_scenarios)
        
        # Generate overview
        self.generate_overview_report(organizations, all_scenarios)
        
        console.print(f"✅ [green]Structured data generated successfully![/green]")
        console.print(f"📁 Output directory: {self.output_dir}")
        console.print(f"🏢 Organizations: {len(organizations)}")
        console.print(f"📋 Total scenarios: {len(all_scenarios)}")
    
    def generate_overview_report(self, organizations: List[Dict], scenarios: List[Dict]):
        """Generate overall summary report"""
        
        # Calculate statistics
        total_orgs = len(organizations)
        total_scenarios = len(scenarios)
        
        industries = {}
        sizes = []
        for org in organizations:
            industry = org.get('industry', 'unknown')
            industries[industry] = industries.get(industry, 0) + 1
            sizes.append(org.get('size', 0))
        
        avg_size = sum(sizes) / len(sizes) if sizes else 0
        
        overview = f"""# Living Twin Synthetic Data Overview

## 📊 Dataset Summary

- **Total Organizations**: {total_orgs:,}
- **Total Delegation Scenarios**: {total_scenarios:,}
- **Average Organization Size**: {avg_size:,.0f} employees

## 🏭 Industry Distribution

{self._format_industry_distribution(industries)}

## 📁 Data Structure

```
data/
├── organizations/
│   ├── org_001/
│   │   ├── org_001_report.md      # Comprehensive markdown report
│   │   ├── org_001.json           # Organization data
│   │   ├── people_org_001.json    # Employee data
│   │   └── scenarios_org_001.json # Delegation scenarios
│   └── org_002/
│       └── ...
└── delegations/
    ├── strategic_decision_summary.md
    ├── operational_issue_summary.md
    └── ...
```

## 🚀 Usage

Each organization has:
- **Markdown Report**: Human-readable comprehensive overview
- **JSON Data Files**: Machine-readable structured data
- **Delegation Scenarios**: Realistic business decision flows

Generated by Living Twin Synthetic Data System
"""
        
        with open(self.output_dir / "README.md", 'w') as f:
            f.write(overview)
    
    def _format_industry_distribution(self, industries: Dict) -> str:
        """Format industry distribution"""
        if not industries:
            return "- No industry data available"
        
        result = []
        for industry, count in sorted(industries.items(), key=lambda x: x[1], reverse=True):
            result.append(f"- {industry.title()}: {count} organizations")
        
        return '\n'.join(result)

@click.command()
@click.option('--input-dir', default='synthetic-data/outputs', help='Input directory with raw synthetic data')
@click.option('--output-dir', default='data', help='Output directory for structured data')
def main(input_dir, output_dir):
    """Generate structured data organization with markdown reports and JSON files"""
    
    generator = StructuredDataGenerator(input_dir, output_dir)
    generator.generate_structured_data()

if __name__ == "__main__":
    main()