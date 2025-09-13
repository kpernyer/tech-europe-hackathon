#!/usr/bin/env python3
"""
Enhanced Data Structure Generator
Creates delegation flows, relationships, and industry-specific behaviors
for Living Twin synthetic organizations.
"""

import json
import os
import random
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, timedelta

class DelegationFlowGenerator:
    """Generates realistic organizational communication flows."""
    
    def __init__(self):
        self.scenarios = {
            "board_revenue_request": {
                "trigger": "Board requests Q4 revenue projection",
                "urgency": "high",
                "expected_completion": "3-5 days"
            },
            "product_launch_crisis": {
                "trigger": "Critical bug found in production system",
                "urgency": "critical", 
                "expected_completion": "24 hours"
            },
            "strategic_pivot": {
                "trigger": "Market shift requires new strategic direction",
                "urgency": "medium",
                "expected_completion": "2-3 weeks"
            },
            "talent_acquisition": {
                "trigger": "Key competitor poaching senior engineers",
                "urgency": "high",
                "expected_completion": "1-2 weeks"
            },
            "compliance_audit": {
                "trigger": "Regulatory compliance audit scheduled",
                "urgency": "medium",
                "expected_completion": "1 month"
            }
        }
        
        self.roles_hierarchy = {
            "CEO": {"level": 1, "typical_response_time": "30 minutes", "delegation_style": "strategic"},
            "COO": {"level": 2, "typical_response_time": "1 hour", "delegation_style": "operational"},
            "CTO": {"level": 2, "typical_response_time": "45 minutes", "delegation_style": "technical"},
            "CFO": {"level": 2, "typical_response_time": "2 hours", "delegation_style": "analytical"},
            "VP Engineering": {"level": 3, "typical_response_time": "2 hours", "delegation_style": "collaborative"},
            "VP Sales": {"level": 3, "typical_response_time": "1 hour", "delegation_style": "results_driven"},
            "VP Marketing": {"level": 3, "typical_response_time": "3 hours", "delegation_style": "creative"},
            "Engineering Manager": {"level": 4, "typical_response_time": "4 hours", "delegation_style": "hands_on"},
            "Sales Manager": {"level": 4, "typical_response_time": "2 hours", "delegation_style": "coaching"}
        }
    
    def generate_delegation_flow(self, org_data: Dict, scenario_key: str) -> Dict:
        """Generate a complete delegation flow for a scenario."""
        scenario = self.scenarios[scenario_key]
        
        # Select participants based on organization structure and scenario
        participants = self._select_participants(org_data, scenario_key)
        
        # Generate communication chain
        flow_steps = self._generate_flow_steps(participants, scenario, org_data)
        
        return {
            "scenario_id": f"{org_data['id']}_{scenario_key}",
            "organization_id": org_data['id'],
            "scenario_type": scenario_key,
            "trigger": scenario["trigger"],
            "urgency_level": scenario["urgency"],
            "expected_completion": scenario["expected_completion"],
            "participants": participants,
            "generated_at": datetime.now().isoformat(),
            "flow_steps": flow_steps,
            "industry_context": self._get_industry_context(org_data["industry"], scenario_key)
        }
    
    def _select_participants(self, org_data: Dict, scenario_key: str) -> List[str]:
        """Select relevant participants based on scenario type."""
        base_roles = ["CEO"]
        
        scenario_role_mapping = {
            "board_revenue_request": ["CEO", "CFO", "VP Sales", "Sales Manager"],
            "product_launch_crisis": ["CEO", "CTO", "VP Engineering", "Engineering Manager"],
            "strategic_pivot": ["CEO", "COO", "VP Marketing", "VP Sales"],
            "talent_acquisition": ["CEO", "VP Engineering", "Engineering Manager"],
            "compliance_audit": ["CEO", "CFO", "COO"]
        }
        
        return scenario_role_mapping.get(scenario_key, base_roles)
    
    def _generate_flow_steps(self, participants: List[str], scenario: Dict, org_data: Dict) -> List[Dict]:
        """Generate realistic communication flow between participants."""
        steps = []
        
        # Industry-specific communication styles
        communication_style = self._get_communication_style(org_data["industry"])
        
        for i in range(len(participants) - 1):
            from_role = participants[i]
            to_role = participants[i + 1]
            
            step = {
                "step_number": i + 1,
                "from_role": from_role,
                "to_role": to_role,
                "message": self._generate_message(from_role, to_role, scenario, org_data),
                "interpretation": self._generate_interpretation(to_role, scenario, org_data),
                "response_time": self.roles_hierarchy[to_role]["typical_response_time"],
                "delegation_style": self.roles_hierarchy[to_role]["delegation_style"],
                "communication_medium": communication_style["preferred_medium"],
                "emotional_tone": self._get_emotional_tone(scenario["urgency"]),
                "expected_actions": self._generate_expected_actions(to_role, scenario),
                "potential_escalations": self._generate_escalations(from_role, to_role, scenario)
            }
            steps.append(step)
        
        # Add response flow back up the chain
        if len(participants) > 2:
            for i in range(len(participants) - 2, 0, -1):
                from_role = participants[i]
                to_role = participants[i - 1]
                
                response_step = {
                    "step_number": len(steps) + 1,
                    "from_role": from_role,
                    "to_role": to_role,
                    "message": self._generate_response_message(from_role, to_role, scenario),
                    "interpretation": "Status update and recommendations",
                    "response_time": self.roles_hierarchy[to_role]["typical_response_time"],
                    "communication_medium": communication_style["follow_up_medium"],
                    "message_type": "response"
                }
                steps.append(response_step)
        
        return steps
    
    def _generate_message(self, from_role: str, to_role: str, scenario: Dict, org_data: Dict) -> str:
        """Generate realistic message based on roles and scenario."""
        messages = {
            ("CEO", "CFO"): f"Board needs {scenario['trigger'].lower()}. Please coordinate with teams.",
            ("CEO", "CTO"): f"We have a situation: {scenario['trigger']}. Need your assessment ASAP.",
            ("CFO", "VP Sales"): "Need detailed pipeline analysis and revenue projections for board presentation.",
            ("CTO", "VP Engineering"): "Critical issue needs immediate technical assessment and resolution plan.",
            ("VP Engineering", "Engineering Manager"): "Urgent technical investigation required. All hands on deck."
        }
        
        key = (from_role, to_role)
        return messages.get(key, f"{from_role} to {to_role}: {scenario['trigger']}")
    
    def _generate_interpretation(self, role: str, scenario: Dict, org_data: Dict) -> str:
        """Generate how each role interprets the message based on their perspective."""
        interpretations = {
            "CFO": "Financial implications need immediate analysis",
            "CTO": "Technical risk assessment and mitigation required",
            "VP Engineering": "Resource allocation and team coordination needed",
            "VP Sales": "Revenue impact analysis and client communication required",
            "Engineering Manager": "Hands-on technical investigation and team leadership needed"
        }
        
        return interpretations.get(role, "Action required based on role responsibilities")
    
    def _generate_expected_actions(self, role: str, scenario: Dict) -> List[str]:
        """Generate expected actions for each role."""
        actions = {
            "CFO": ["Analyze financial data", "Prepare board presentation", "Coordinate with accounting"],
            "CTO": ["Technical assessment", "Risk analysis", "Resource planning"],
            "VP Engineering": ["Team coordination", "Technical planning", "Status reporting"],
            "VP Sales": ["Pipeline analysis", "Client communication", "Revenue forecasting"]
        }
        
        return actions.get(role, ["Assess situation", "Take appropriate action", "Report back"])
    
    def _generate_escalations(self, from_role: str, to_role: str, scenario: Dict) -> List[str]:
        """Generate potential escalation scenarios."""
        return [
            "If no response within expected timeframe",
            "If additional resources needed",
            "If external stakeholders must be involved"
        ]
    
    def _generate_response_message(self, from_role: str, to_role: str, scenario: Dict) -> str:
        """Generate response messages flowing back up the hierarchy."""
        return f"Update from {from_role}: Analysis complete, recommendations attached."
    
    def _get_communication_style(self, industry: str) -> Dict:
        """Get industry-specific communication preferences."""
        styles = {
            "technology": {"preferred_medium": "slack", "follow_up_medium": "video_call"},
            "consulting": {"preferred_medium": "email", "follow_up_medium": "meeting"},
            "retail": {"preferred_medium": "phone", "follow_up_medium": "email"},
            "manufacturing": {"preferred_medium": "meeting", "follow_up_medium": "email"}
        }
        
        return styles.get(industry, {"preferred_medium": "email", "follow_up_medium": "meeting"})
    
    def _get_emotional_tone(self, urgency: str) -> str:
        """Get appropriate emotional tone based on urgency."""
        tones = {
            "critical": "urgent_concerned",
            "high": "serious_focused",
            "medium": "professional_measured",
            "low": "collaborative_relaxed"
        }
        
        return tones.get(urgency, "professional_measured")
    
    def _get_industry_context(self, industry: str, scenario_key: str) -> Dict:
        """Add industry-specific context to scenarios."""
        contexts = {
            "technology": {
                "board_revenue_request": "Focus on ARR, churn rates, and product metrics",
                "product_launch_crisis": "Emphasis on system reliability and user experience"
            },
            "consulting": {
                "board_revenue_request": "Focus on billable hours and client satisfaction",
                "talent_acquisition": "Emphasis on expertise and client relationship impact"
            },
            "retail": {
                "board_revenue_request": "Focus on seasonal trends and inventory turnover",
                "strategic_pivot": "Emphasis on customer behavior and market trends"
            }
        }
        
        return contexts.get(industry, {}).get(scenario_key, "Standard industry practices apply")

def enhance_organization_data(org_path: Path):
    """Enhance a single organization with delegation flows and relationships."""
    
    # Read existing organization data
    org_json_file = org_path / f"{org_path.name}.json"
    if not org_json_file.exists():
        print(f"Skipping {org_path.name} - no JSON file found")
        return
    
    with open(org_json_file, 'r') as f:
        org_data = json.load(f)
    
    print(f"Enhancing {org_data['name']} ({org_data['id']})...")
    
    # Create flows directory
    flows_dir = org_path / "flows"
    flows_dir.mkdir(exist_ok=True)
    
    # Generate delegation flows
    generator = DelegationFlowGenerator()
    
    # Select 3-5 relevant scenarios for each organization
    scenarios = list(generator.scenarios.keys())
    selected_scenarios = random.sample(scenarios, min(3, len(scenarios)))
    
    for scenario_key in selected_scenarios:
        flow_data = generator.generate_delegation_flow(org_data, scenario_key)
        
        # Save flow to JSON file
        flow_file = flows_dir / f"{scenario_key}.json"
        with open(flow_file, 'w') as f:
            json.dump(flow_data, f, indent=2)
        
        # Create readable Markdown version
        md_file = flows_dir / f"{scenario_key}.md"
        generate_flow_markdown(flow_data, md_file)
    
    # Enhance the main README if it exists (rename from report)
    report_file = org_path / f"{org_path.name}_report.md"
    readme_file = org_path / "README.md"
    
    if report_file.exists() and not readme_file.exists():
        # Rename and enhance existing report
        enhanced_content = enhance_readme_content(org_data, flows_dir)
        with open(readme_file, 'w') as f:
            f.write(enhanced_content)
        print(f"  ✓ Enhanced README.md created")
    
    print(f"  ✓ Generated {len(selected_scenarios)} delegation flows")

def generate_flow_markdown(flow_data: Dict, output_file: Path):
    """Generate human-readable Markdown for delegation flow."""
    
    content = f"""# {flow_data['scenario_type'].title().replace('_', ' ')} - Delegation Flow

## Scenario Overview
- **Organization**: {flow_data['organization_id']}
- **Trigger**: {flow_data['trigger']}
- **Urgency**: {flow_data['urgency_level']}
- **Expected Completion**: {flow_data['expected_completion']}
- **Generated**: {flow_data['generated_at'][:10]}

## Participants
{', '.join(flow_data['participants'])}

## Communication Flow

"""
    
    for step in flow_data['flow_steps']:
        content += f"""### Step {step['step_number']}: {step['from_role']} → {step['to_role']}

**Message**: {step['message']}

**Interpretation**: {step['interpretation']}

**Response Time**: {step['response_time']}
**Medium**: {step.get('communication_medium', 'email')}
**Tone**: {step.get('emotional_tone', 'professional')}

**Expected Actions**:
{chr(10).join([f"- {action}" for action in step.get('expected_actions', [])])}

---

"""
    
    content += f"""## Industry Context
{flow_data.get('industry_context', 'Standard business practices apply')}

## Notes
This delegation flow represents typical organizational communication patterns and may vary based on specific circumstances, company culture, and individual leadership styles.

*Generated by Living Twin Synthetic Data System*
"""
    
    with open(output_file, 'w') as f:
        f.write(content)

def enhance_readme_content(org_data: Dict, flows_dir: Path) -> str:
    """Generate enhanced README content for organization."""
    
    flows = list(flows_dir.glob("*.json"))
    flow_names = [f.stem for f in flows]
    
    # Handle different size data structures
    size_info = org_data.get('size', 'Unknown')
    if isinstance(size_info, dict):
        size_display = f"{size_info.get('employees', 'Unknown')} employees"
    elif isinstance(size_info, int):
        size_display = f"{size_info} employees"
    else:
        size_display = str(size_info)

    content = f"""# {org_data['name']}

## Organization Profile
- **ID**: `{org_data['id']}`
- **Industry**: {org_data['industry'].title()}
- **Size**: {size_display}
- **Revenue**: {org_data.get('revenue_range', 'Not specified')}
- **Headquarters**: {org_data.get('headquarters', 'Not specified')}
- **Lifecycle Stage**: {org_data.get('lifecycle_stage', 'Not specified')}

## Organizational Culture
- **Structure**: {org_data.get('structure_type', 'Not specified')}
- **Delegation Culture**: {org_data.get('delegation_culture', 'Not specified')}
- **Decision Speed**: {org_data.get('decision_speed', 'Not specified')}
- **Leadership Style**: {org_data.get('leadership_style', 'Not specified')}
- **Communication Style**: {org_data.get('communication_style', 'Not specified')}

## Strategic Context
"""
    
    if org_data.get('strategic_priorities'):
        content += "\n### Strategic Priorities\n"
        for priority in org_data['strategic_priorities']:
            content += f"- {priority}\n"
    
    if org_data.get('competitive_advantages'):
        content += "\n### Competitive Advantages\n"
        for advantage in org_data['competitive_advantages']:
            content += f"- {advantage}\n"
    
    if org_data.get('key_challenges'):
        content += "\n### Key Challenges\n"
        for challenge in org_data['key_challenges']:
            content += f"- {challenge}\n"
    
    content += f"""
## Available Data Files

### Core Data
- `{org_data['id']}.json` - Complete organization profile (structured data)

### Documentation
- `README.md` - This human-readable overview
"""
    
    # List other existing files
    additional_files = [
        f"{org_data['id']}_strategic_dna.md",
        f"{org_data['id']}_code_of_conduct.md", 
        f"{org_data['id']}_products_terminology.md",
        f"{org_data['id']}_strategic_market.md"
    ]
    
    for file in additional_files:
        content += f"- `{file}` - Additional organization documentation\n"
    
    if flow_names:
        content += f"\n### Delegation Flows\n"
        for flow_name in sorted(flow_names):
            content += f"- `flows/{flow_name}.json` - Structured delegation flow data\n"
            content += f"- `flows/{flow_name}.md` - Human-readable delegation flow\n"
    
    content += f"""
## Usage Notes

This organization profile is part of the Living Twin synthetic data system for organizational AI modeling. The data includes:

1. **Static Profile**: Basic organizational information and culture
2. **Delegation Flows**: Realistic communication scenarios showing how information flows through the organization
3. **Industry Context**: Sector-specific behaviors and decision patterns

### Delegation Flow Scenarios
{f"Currently available: {', '.join([name.replace('_', ' ').title() for name in flow_names])}" if flow_names else "No delegation flows generated yet"}

---
*Enhanced by Living Twin Synthetic Data System on {datetime.now().strftime('%Y-%m-%d')}*
"""
    
    return content

def main():
    """Main enhancement process."""
    base_path = Path("/Users/kenper/src/aprio-one/tech-europe-hackathon/living-twin-synthetic-data")
    orgs_path = base_path / "generated" / "structured" / "organizations"
    
    if not orgs_path.exists():
        print(f"Organizations path not found: {orgs_path}")
        return
    
    org_dirs = [d for d in orgs_path.iterdir() if d.is_dir() and d.name.startswith('org_')]
    
    print(f"Found {len(org_dirs)} organizations to enhance...")
    
    # Process first few organizations as examples
    sample_orgs = sorted(org_dirs)[:5]  # Start with first 5 organizations
    
    for org_dir in sample_orgs:
        try:
            enhance_organization_data(org_dir)
        except Exception as e:
            print(f"Error enhancing {org_dir.name}: {e}")
            continue
    
    print(f"\n✅ Enhanced {len(sample_orgs)} organizations with delegation flows and improved documentation")
    print("Each organization now includes:")
    print("  - Enhanced README.md with complete profile")
    print("  - flows/ directory with delegation scenarios")
    print("  - JSON and Markdown versions of each flow")

if __name__ == "__main__":
    main()