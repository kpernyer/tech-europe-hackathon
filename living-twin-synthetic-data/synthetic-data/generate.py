#!/usr/bin/env python3
"""
Synthetic Data Generator
Generates organizations, people, and delegation scenarios
"""

import json
import random
import yaml
import click
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from faker import Faker

fake = Faker()

@dataclass
class Person:
    """Person within an organization"""
    id: str
    name: str
    role: str
    department: str
    level: int
    email: str
    personality_traits: List[str]
    communication_style: str
    decision_style: str
    risk_tolerance: str
    years_in_role: int
    years_at_company: int
    reports_to: Optional[str]
    direct_reports: List[str]
    age: int
    gender: str
    cultural_background: str

@dataclass
class Organization:
    """Organization profile"""
    id: str
    name: str
    industry: str
    size: int
    revenue_range: str
    profitable: bool
    years_in_business: int
    headquarters: str
    regions: List[str]
    structure_type: str
    delegation_culture: str
    decision_speed: str
    innovation_index: float
    digital_maturity: float
    people: List[Person]
    departments: List[str]
    products: List[str]
    services: List[str]
    values: List[str]
    strategic_priorities: List[str]

@dataclass
class DelegationScenario:
    """Delegation scenario with chain of responses"""
    id: str
    organization_id: str
    type: str
    title: str
    description: str
    urgency: str
    scope: str
    originator: str
    delegation_chain: List[Dict]
    expected_outcomes: List[str]
    success_metrics: List[str]
    risks: List[str]
    timeline: str

class SyntheticDataGenerator:
    """Generates synthetic organizational data"""
    
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        self.fake = Faker()
        self.generated_orgs = []
        
    def generate_organizations(self, count: Optional[int] = None) -> List[Organization]:
        """Generate multiple organizations"""
        count = count or self.config['generation']['organizations']['count']
        
        organizations = []
        for i in range(count):
            org = self._generate_single_organization(f"org_{i:03d}")
            organizations.append(org)
            self.generated_orgs.append(org)
            
        return organizations
    
    def _generate_single_organization(self, org_id: str) -> Organization:
        """Generate a single organization with people"""
        
        # Select organization characteristics
        size_config = random.choices(
            self.config['generation']['organizations']['size_distribution'],
            weights=[s['weight'] for s in self.config['generation']['organizations']['size_distribution']]
        )[0]
        
        size = random.randint(size_config['range'][0], size_config['range'][1])
        industry = random.choice(self.config['generation']['organizations']['industries'])
        headquarters = random.choice(self.config['generation']['organizations']['regions'])
        
        # Generate company name
        company_name = self._generate_company_name(industry)
        
        # Generate people for the organization
        num_people = random.randint(
            self.config['generation']['people']['per_organization']['min'],
            self.config['generation']['people']['per_organization']['max']
        )
        people = self._generate_people_hierarchy(org_id, num_people)
        
        # Create organization
        org = Organization(
            id=org_id,
            name=company_name,
            industry=industry,
            size=size,
            revenue_range=self._estimate_revenue(size, industry),
            profitable=random.random() > 0.3,
            years_in_business=random.randint(1, 50),
            headquarters=headquarters,
            regions=self._select_regions(headquarters),
            structure_type=self._determine_structure(size),
            delegation_culture=self._determine_delegation_culture(size, industry),
            decision_speed=random.choice(['fast', 'moderate', 'deliberate']),
            innovation_index=random.random(),
            digital_maturity=random.random(),
            people=people,
            departments=self._generate_departments(industry),
            products=self._generate_products(industry),
            services=self._generate_services(industry),
            values=self._generate_values(),
            strategic_priorities=self._generate_strategic_priorities(industry)
        )
        
        return org
    
    def _generate_company_name(self, industry: str) -> str:
        """Generate realistic company name based on industry"""
        
        prefixes = {
            'technology': ['Tech', 'Digital', 'Cyber', 'Cloud', 'Data', 'AI'],
            'healthcare': ['Health', 'Med', 'Bio', 'Life', 'Care', 'Wellness'],
            'finance': ['Capital', 'Financial', 'Investment', 'Global', 'Trust'],
            'retail': ['Shop', 'Store', 'Market', 'Retail', 'Commerce'],
            'manufacturing': ['Industrial', 'Precision', 'Advanced', 'Global'],
            'consulting': ['Strategic', 'Advisory', 'Consulting', 'Partners'],
            'nonprofit': ['Foundation', 'Initiative', 'Alliance', 'Coalition'],
            'education': ['Academy', 'Institute', 'University', 'Learning']
        }
        
        suffixes = {
            'technology': ['Systems', 'Solutions', 'Labs', 'Technologies', 'AI', 'Cloud'],
            'healthcare': ['Health', 'Medical', 'Therapeutics', 'Sciences', 'Care'],
            'finance': ['Group', 'Holdings', 'Partners', 'Advisors', 'Management'],
            'retail': ['Co', 'Group', 'Direct', 'Plus', 'Hub'],
            'manufacturing': ['Corp', 'Industries', 'Manufacturing', 'Works'],
            'consulting': ['Group', 'Advisors', 'Consulting', 'Solutions'],
            'nonprofit': ['Foundation', 'Network', 'Alliance', 'Initiative'],
            'education': ['Academy', 'Institute', 'College', 'School']
        }
        
        prefix_list = prefixes.get(industry, ['Global'])
        suffix_list = suffixes.get(industry, ['Corp'])
        
        return f"{random.choice(prefix_list)}{self.fake.last_name()} {random.choice(suffix_list)}"
    
    def _generate_people_hierarchy(self, org_id: str, count: int) -> List[Person]:
        """Generate people with hierarchical structure"""
        
        people = []
        hierarchy_config = self.config['generation']['people']['hierarchy_levels']
        
        # Track reporting relationships
        level_people = {1: [], 2: [], 3: [], 4: [], 5: []}
        
        # Generate by level
        for level_config in hierarchy_config:
            level = level_config['level']
            
            if 'count' in level_config:
                num_at_level = level_config['count']
            else:
                num_at_level = random.randint(
                    level_config['count_range'][0],
                    level_config['count_range'][1]
                )
            
            for _ in range(num_at_level):
                if len(people) >= count:
                    break
                    
                person = self._generate_person(
                    org_id=org_id,
                    level=level,
                    title_options=level_config['titles']
                )
                
                # Set reporting relationship
                if level > 1 and level_people[level - 1]:
                    person.reports_to = random.choice(level_people[level - 1]).id
                
                people.append(person)
                level_people[level].append(person)
        
        # Set direct reports
        for person in people:
            if person.reports_to:
                manager = next((p for p in people if p.id == person.reports_to), None)
                if manager:
                    manager.direct_reports.append(person.id)
        
        return people
    
    def _generate_person(self, org_id: str, level: int, title_options: List[str]) -> Person:
        """Generate a single person"""
        
        # Determine gender for name generation
        gender = 'male' if random.random() < 0.5 else 'female'
        
        if gender == 'male':
            first_name = self.fake.first_name_male()
        else:
            first_name = self.fake.first_name_female()
        
        last_name = self.fake.last_name()
        
        # Select title and department
        title_prefix = random.choice(title_options)
        departments = ['Engineering', 'Sales', 'Marketing', 'Operations', 'Finance', 'HR', 'Product', 'Customer Success']
        department = random.choice(departments)
        
        if level <= 2:
            role = title_prefix
        else:
            role = f"{title_prefix} {department}"
        
        # Generate characteristics
        personality_traits = random.sample(
            self.config['generation']['people']['personality_traits'],
            k=random.randint(2, 4)
        )
        
        person = Person(
            id=f"{org_id}_person_{self.fake.uuid4()[:8]}",
            name=f"{first_name} {last_name}",
            role=role,
            department=department if level > 2 else 'Executive',
            level=level,
            email=f"{first_name.lower()}.{last_name.lower()}@company.com",
            personality_traits=personality_traits,
            communication_style=random.choice(self.config['generation']['people']['communication_styles']),
            decision_style=random.choice(self.config['generation']['people']['decision_styles']),
            risk_tolerance=random.choice(['low', 'medium', 'high']),
            years_in_role=random.randint(1, 10),
            years_at_company=random.randint(1, 15),
            reports_to=None,  # Set later
            direct_reports=[],  # Set later
            age=self._generate_age(level),
            gender=gender,
            cultural_background=random.choice(self.config['diversity']['cultural_backgrounds'])
        )
        
        return person
    
    def _generate_age(self, level: int) -> int:
        """Generate age based on hierarchy level"""
        base_ages = {1: 45, 2: 40, 3: 35, 4: 30, 5: 28}
        base = base_ages.get(level, 30)
        return base + random.randint(-5, 15)
    
    def _estimate_revenue(self, size: int, industry: str) -> str:
        """Estimate revenue range based on size and industry"""
        
        if size < 100:
            return "$1M-$10M"
        elif size < 500:
            return "$10M-$100M"
        elif size < 2000:
            return "$100M-$500M"
        elif size < 10000:
            return "$500M-$2B"
        else:
            return "$2B+"
    
    def _select_regions(self, headquarters: str) -> List[str]:
        """Select operational regions"""
        all_regions = self.config['generation']['organizations']['regions']
        num_regions = random.randint(1, min(4, len(all_regions)))
        regions = [headquarters]
        
        for _ in range(num_regions - 1):
            region = random.choice(all_regions)
            if region not in regions:
                regions.append(region)
        
        return regions
    
    def _determine_structure(self, size: int) -> str:
        """Determine organizational structure based on size"""
        if size < 200:
            return 'flat'
        elif size < 1000:
            return random.choice(['hierarchical', 'matrix'])
        else:
            return 'hierarchical'
    
    def _determine_delegation_culture(self, size: int, industry: str) -> str:
        """Determine delegation culture"""
        if size < 200:
            return random.choice(['collaborative', 'distributed'])
        elif industry in ['finance', 'healthcare']:
            return 'hierarchical'
        else:
            return random.choice(['hierarchical', 'matrix', 'collaborative'])
    
    def _generate_departments(self, industry: str) -> List[str]:
        """Generate relevant departments"""
        base_departments = ['Executive', 'Finance', 'HR', 'Operations']
        
        industry_specific = {
            'technology': ['Engineering', 'Product', 'DevOps', 'Data Science'],
            'healthcare': ['Clinical', 'Research', 'Compliance', 'Patient Care'],
            'finance': ['Trading', 'Risk', 'Compliance', 'Investment'],
            'retail': ['Merchandising', 'Supply Chain', 'Store Operations', 'E-commerce'],
            'manufacturing': ['Production', 'Quality', 'Supply Chain', 'R&D'],
            'consulting': ['Strategy', 'Implementation', 'Analytics', 'Client Services'],
            'nonprofit': ['Programs', 'Development', 'Advocacy', 'Community'],
            'education': ['Academic', 'Student Services', 'Research', 'Administration']
        }
        
        return base_departments + industry_specific.get(industry, ['Sales', 'Marketing'])
    
    def _generate_products(self, industry: str) -> List[str]:
        """Generate product names"""
        products_map = {
            'technology': ['CloudSync Pro', 'DataVault Enterprise', 'AI Assistant', 'SecureNet'],
            'healthcare': ['PatientCare Suite', 'HealthMonitor Pro', 'MedTrack System'],
            'finance': ['WealthManager', 'RiskAnalyzer', 'TradePro Platform'],
            'retail': ['ShopSmart App', 'Inventory Master', 'Customer360'],
            'manufacturing': ['PrecisionLine', 'QualityTrack', 'SupplyChain Pro']
        }
        
        return products_map.get(industry, ['Core Product', 'Premium Service'])
    
    def _generate_services(self, industry: str) -> List[str]:
        """Generate service offerings"""
        services_map = {
            'technology': ['Cloud Migration', 'Security Audit', 'Custom Development', '24/7 Support'],
            'healthcare': ['Patient Consultation', 'Health Screening', 'Emergency Care'],
            'finance': ['Wealth Management', 'Investment Advisory', 'Risk Assessment'],
            'consulting': ['Strategy Consulting', 'Digital Transformation', 'Change Management'],
            'education': ['Online Courses', 'Certification Programs', 'Research Services']
        }
        
        return services_map.get(industry, ['Professional Services', 'Customer Support'])
    
    def _generate_values(self) -> List[str]:
        """Generate company values"""
        all_values = [
            'Innovation', 'Integrity', 'Excellence', 'Collaboration',
            'Customer Focus', 'Accountability', 'Diversity', 'Sustainability',
            'Transparency', 'Agility', 'Quality', 'Respect'
        ]
        
        return random.sample(all_values, k=random.randint(3, 5))
    
    def _generate_strategic_priorities(self, industry: str) -> List[str]:
        """Generate strategic priorities"""
        base_priorities = [
            'Digital Transformation',
            'Customer Experience',
            'Operational Excellence',
            'Talent Development',
            'Market Expansion'
        ]
        
        industry_specific = {
            'technology': ['AI Innovation', 'Platform Scaling', 'Developer Experience'],
            'healthcare': ['Patient Outcomes', 'Cost Reduction', 'Regulatory Compliance'],
            'finance': ['Risk Management', 'Digital Banking', 'Regulatory Compliance'],
            'retail': ['Omnichannel Experience', 'Supply Chain Optimization', 'Personalization'],
            'manufacturing': ['Automation', 'Quality Improvement', 'Sustainability']
        }
        
        priorities = random.sample(base_priorities, k=2)
        if industry in industry_specific:
            priorities.extend(random.sample(industry_specific[industry], k=1))
        
        return priorities
    
    def generate_delegation_scenarios(self, organization: Organization) -> List[DelegationScenario]:
        """Generate delegation scenarios for an organization"""
        
        num_scenarios = self.config['generation']['scenarios']['per_organization']
        scenarios = []
        
        for i in range(num_scenarios):
            scenario_type = random.choice(self.config['generation']['scenarios']['types'])
            scenario = self._generate_single_scenario(organization, scenario_type, i)
            scenarios.append(scenario)
        
        return scenarios
    
    def _generate_single_scenario(self, org: Organization, scenario_type: str, index: int) -> DelegationScenario:
        """Generate a single delegation scenario"""
        
        # Select originator (usually CEO or VP)
        executives = [p for p in org.people if p.level <= 2]
        originator = random.choice(executives) if executives else org.people[0]
        
        # Build delegation chain
        chain_length = random.randint(
            self.config['generation']['scenarios']['delegation_chains']['min_length'],
            self.config['generation']['scenarios']['delegation_chains']['max_length']
        )
        
        delegation_chain = self._build_delegation_chain(org, originator, chain_length, scenario_type)
        
        scenario = DelegationScenario(
            id=f"{org.id}_scenario_{index:03d}",
            organization_id=org.id,
            type=scenario_type,
            title=self._generate_scenario_title(scenario_type),
            description=self._generate_scenario_description(scenario_type, org),
            urgency=random.choice(self.config['generation']['scenarios']['urgency_levels']),
            scope=random.choice(self.config['generation']['scenarios']['scopes']),
            originator=originator.id,
            delegation_chain=delegation_chain,
            expected_outcomes=self._generate_expected_outcomes(scenario_type),
            success_metrics=self._generate_success_metrics(scenario_type),
            risks=self._generate_risks(scenario_type),
            timeline=self._generate_timeline()
        )
        
        return scenario
    
    def _build_delegation_chain(self, org: Organization, originator: Person, 
                               length: int, scenario_type: str) -> List[Dict]:
        """Build a delegation chain"""
        
        chain = []
        current_person = originator
        people_in_chain = [originator.id]
        
        for step in range(length):
            # Find next person to delegate to
            candidates = []
            
            # Direct reports first
            if current_person.direct_reports:
                candidates = [p for p in org.people 
                            if p.id in current_person.direct_reports 
                            and p.id not in people_in_chain]
            
            # Same level peers
            if not candidates:
                candidates = [p for p in org.people 
                            if p.level == current_person.level 
                            and p.id != current_person.id
                            and p.id not in people_in_chain]
            
            # Next level down
            if not candidates:
                candidates = [p for p in org.people 
                            if p.level == current_person.level + 1
                            and p.id not in people_in_chain]
            
            if not candidates:
                break
            
            next_person = random.choice(candidates)
            
            # Determine response type
            response_type = self._determine_response_type(
                current_person, next_person, scenario_type
            )
            
            delegation_step = {
                'from': current_person.id,
                'from_name': current_person.name,
                'from_role': current_person.role,
                'to': next_person.id,
                'to_name': next_person.name,
                'to_role': next_person.role,
                'response_type': response_type,
                'message': self._generate_delegation_message(
                    current_person, next_person, scenario_type, response_type
                ),
                'questions': self._generate_questions(response_type),
                'proposed_actions': self._generate_proposed_actions(scenario_type, response_type),
                'timeline': f"{random.randint(1, 4)} days"
            }
            
            chain.append(delegation_step)
            people_in_chain.append(next_person.id)
            
            # Continue chain based on response type
            if response_type in ['accept', 'delegate_further']:
                current_person = next_person
            else:
                break
        
        return chain
    
    def _determine_response_type(self, from_person: Person, to_person: Person, 
                                scenario_type: str) -> str:
        """Determine how someone responds to delegation"""
        
        # Use configured distribution as base
        distribution = self.config['generation']['scenarios']['delegation_chains']['response_distribution']
        
        # Adjust based on personality
        if 'analytical' in to_person.personality_traits:
            distribution['clarify'] += 0.1
            distribution['accept'] -= 0.1
        
        if 'decisive' in to_person.personality_traits:
            distribution['accept'] += 0.1
            distribution['clarify'] -= 0.1
        
        # Random selection based on weights
        types = list(distribution.keys())
        weights = list(distribution.values())
        
        return random.choices(types, weights=weights)[0]
    
    def _generate_delegation_message(self, from_person: Person, to_person: Person,
                                    scenario_type: str, response_type: str) -> str:
        """Generate delegation message"""
        
        templates = {
            'accept': [
                "I'll take this on and ensure we meet the objectives.",
                "Understood. I'll mobilize my team to deliver on this.",
                "This aligns with our priorities. We'll make it happen."
            ],
            'clarify': [
                "I need more clarity on the specific deliverables and timeline.",
                "Can we discuss the resource implications before I commit?",
                "I'd like to understand how this fits with our current priorities."
            ],
            'push_back': [
                "I have concerns about the feasibility given our current commitments.",
                "This conflicts with our agreed Q3 priorities. Should we reconsider?",
                "The timeline seems aggressive. Can we explore alternatives?"
            ],
            'delegate_further': [
                "I'll loop in my team lead who has the expertise for this.",
                "This would be better handled by the specialist team.",
                "I'm assigning this to my direct report who owns this area."
            ],
            'suggest_alternative': [
                "I propose a different approach that could be more effective.",
                "Have we considered this alternative solution instead?",
                "Based on our experience, here's what I recommend instead."
            ]
        }
        
        return random.choice(templates.get(response_type, ["I'll review and respond."]))
    
    def _generate_questions(self, response_type: str) -> List[str]:
        """Generate questions based on response type"""
        
        if response_type == 'clarify':
            return random.sample([
                "What's the budget allocation for this?",
                "What's the expected timeline?",
                "Who are the key stakeholders?",
                "What are the success metrics?",
                "What resources are available?",
                "How does this align with our annual goals?"
            ], k=random.randint(1, 3))
        elif response_type == 'push_back':
            return random.sample([
                "How do we handle the conflict with existing priorities?",
                "What gets deprioritized to make room for this?",
                "Have we considered the risks fully?"
            ], k=random.randint(1, 2))
        else:
            return []
    
    def _generate_proposed_actions(self, scenario_type: str, response_type: str) -> List[str]:
        """Generate proposed actions"""
        
        if response_type in ['accept', 'delegate_further']:
            actions_map = {
                'strategic_planning': [
                    "Conduct stakeholder analysis",
                    "Draft strategic framework",
                    "Schedule planning sessions"
                ],
                'crisis_management': [
                    "Assemble crisis team",
                    "Assess immediate risks",
                    "Prepare communication plan"
                ],
                'resource_allocation': [
                    "Review current allocations",
                    "Identify optimization opportunities",
                    "Prepare reallocation proposal"
                ],
                'market_expansion': [
                    "Conduct market research",
                    "Analyze competitive landscape",
                    "Develop entry strategy"
                ]
            }
            
            return random.sample(
                actions_map.get(scenario_type, ["Analyze requirements", "Develop plan", "Execute"]),
                k=random.randint(2, 3)
            )
        
        return []
    
    def _generate_scenario_title(self, scenario_type: str) -> str:
        """Generate scenario title"""
        
        titles = {
            'strategic_planning': "Q3 Strategic Planning Initiative",
            'crisis_management': "Critical System Failure Response",
            'resource_allocation': "Budget Reallocation for Growth",
            'market_expansion': "European Market Entry Strategy",
            'digital_transformation': "Cloud Migration Program",
            'team_restructuring': "Engineering Team Reorganization",
            'product_launch': "AI Product Launch Preparation",
            'competitive_response': "Competitor Market Move Response",
            'cost_optimization': "20% Cost Reduction Initiative",
            'innovation_initiative': "Innovation Lab Establishment"
        }
        
        return titles.get(scenario_type, f"{scenario_type.replace('_', ' ').title()} Initiative")
    
    def _generate_scenario_description(self, scenario_type: str, org: Organization) -> str:
        """Generate detailed scenario description"""
        
        templates = {
            'strategic_planning': f"As {org.name} enters a critical growth phase, we need to align our strategic priorities for the next quarter. Market conditions are shifting and we must adapt our approach.",
            'crisis_management': f"A critical incident has occurred affecting our {random.choice(org.departments)} operations. Immediate action is required to minimize impact and restore normal operations.",
            'resource_allocation': f"With limited resources and multiple competing priorities, {org.name} must make tough decisions about where to invest for maximum impact.",
            'market_expansion': f"The opportunity to expand into new markets has emerged. {org.name} must evaluate and execute an entry strategy while managing risks."
        }
        
        return templates.get(scenario_type, f"A {scenario_type.replace('_', ' ')} scenario requiring strategic delegation and coordination across {org.name}.")
    
    def _generate_expected_outcomes(self, scenario_type: str) -> List[str]:
        """Generate expected outcomes"""
        
        outcomes_map = {
            'strategic_planning': [
                "Aligned strategic roadmap",
                "Clear priorities for next quarter",
                "Resource allocation plan"
            ],
            'crisis_management': [
                "Incident contained within 24 hours",
                "Communication to all stakeholders",
                "Prevention plan for future"
            ],
            'resource_allocation': [
                "Optimized budget distribution",
                "ROI improvement of 15%",
                "Clear project priorities"
            ]
        }
        
        return outcomes_map.get(scenario_type, ["Successful execution", "Stakeholder alignment", "Measurable results"])
    
    def _generate_success_metrics(self, scenario_type: str) -> List[str]:
        """Generate success metrics"""
        
        metrics_map = {
            'strategic_planning': ["Strategy adoption rate", "Milestone achievement", "Team alignment score"],
            'crisis_management': ["Time to resolution", "Impact minimization", "Stakeholder satisfaction"],
            'resource_allocation': ["ROI improvement", "Budget efficiency", "Project completion rate"],
            'market_expansion': ["Market penetration", "Revenue growth", "Customer acquisition"]
        }
        
        return metrics_map.get(scenario_type, ["Completion rate", "Quality score", "Timeline adherence"])
    
    def _generate_risks(self, scenario_type: str) -> List[str]:
        """Generate risks"""
        
        risks_map = {
            'strategic_planning': ["Misalignment between teams", "Market changes", "Resource constraints"],
            'crisis_management': ["Escalation potential", "Reputation damage", "Regulatory issues"],
            'resource_allocation': ["Project delays", "Team morale impact", "Quality compromise"],
            'market_expansion': ["Market rejection", "Regulatory barriers", "Competition response"]
        }
        
        return risks_map.get(scenario_type, ["Execution risk", "Timeline risk", "Budget overrun"])
    
    def _generate_timeline(self) -> str:
        """Generate timeline"""
        
        timelines = ["1 week", "2 weeks", "1 month", "Q3 2024", "6 months", "End of year"]
        return random.choice(timelines)
    
    def save_outputs(self, output_dir: str, organizations: List[Organization], 
                    scenarios: Dict[str, List[DelegationScenario]]):
        """Save generated data to files"""
        
        output_path = Path(output_dir)
        
        # Create output directories
        (output_path / 'organizations').mkdir(parents=True, exist_ok=True)
        (output_path / 'people').mkdir(parents=True, exist_ok=True)
        (output_path / 'scenarios').mkdir(parents=True, exist_ok=True)
        (output_path / 'delegation_chains').mkdir(parents=True, exist_ok=True)
        
        # Save organizations
        for org in organizations:
            # Save organization
            org_file = output_path / 'organizations' / f"org_{org.id}_{org.name.replace(' ', '_')}.json"
            org_data = asdict(org)
            org_data['people'] = [p.id for p in org.people]  # Just IDs in org file
            
            with open(org_file, 'w') as f:
                json.dump(org_data, f, indent=2)
            
            # Save people separately
            people_file = output_path / 'people' / f"people_{org.id}.json"
            people_data = [asdict(p) for p in org.people]
            
            with open(people_file, 'w') as f:
                json.dump(people_data, f, indent=2)
        
        # Save scenarios
        for org_id, org_scenarios in scenarios.items():
            for scenario in org_scenarios:
                scenario_file = output_path / 'scenarios' / f"scenario_{scenario.id}.json"
                
                with open(scenario_file, 'w') as f:
                    json.dump(asdict(scenario), f, indent=2)
        
        # Save summary
        summary = {
            'generation_date': datetime.now().isoformat(),
            'organizations_count': len(organizations),
            'total_people': sum(len(org.people) for org in organizations),
            'total_scenarios': sum(len(s) for s in scenarios.values()),
            'config_used': self.config
        }
        
        with open(output_path / 'generation_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"✅ Saved {len(organizations)} organizations to {output_dir}")

@click.command()
@click.option('--output-dir', default='synthetic-data/outputs', help='Output directory')
@click.option('--config', default='synthetic-data/config.yaml', help='Configuration file')
@click.option('--count', type=int, help='Number of organizations to generate')
def main(output_dir: str, config: str, count: Optional[int]):
    """Generate synthetic organizational data"""
    
    print("🏢 Generating synthetic organizations...")
    
    generator = SyntheticDataGenerator(config)
    
    # Generate organizations
    organizations = generator.generate_organizations(count)
    
    # Generate scenarios for each organization
    all_scenarios = {}
    for org in organizations:
        scenarios = generator.generate_delegation_scenarios(org)
        all_scenarios[org.id] = scenarios
    
    # Save outputs
    generator.save_outputs(output_dir, organizations, all_scenarios)
    
    print(f"✅ Generation complete!")
    print(f"📊 Generated {len(organizations)} organizations with {sum(len(org.people) for org in organizations)} people")
    print(f"📋 Generated {sum(len(s) for s in all_scenarios.values())} delegation scenarios")

if __name__ == '__main__':
    main()