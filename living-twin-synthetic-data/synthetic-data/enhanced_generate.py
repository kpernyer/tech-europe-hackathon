#!/usr/bin/env python3
"""
Enhanced Synthetic Data Generator
Integrates industrial companies data with synthetic organization and delegation scenarios
"""

import json
import random
import yaml
import click
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

# Import existing classes
from generate import Person, Organization, DelegationScenario, SyntheticDataGenerator

class EnhancedSyntheticDataGenerator(SyntheticDataGenerator):
    """Enhanced generator that integrates real industrial company data"""

    def __init__(self, config_path: str):
        super().__init__(config_path)
        self.industrial_companies = []
        self.load_industrial_companies()

    def load_industrial_companies(self):
        """Load industrial companies data"""
        try:
            industrial_config = self.config.get('industrial_integration', {})
            if not industrial_config.get('use_industrial_data', False):
                return

            data_path = industrial_config.get('industrial_data_path', 'industrial_data/industrial_companies.json')
            full_path = Path(data_path)

            if not full_path.exists():
                # Try relative path
                full_path = Path(__file__).parent / data_path

            if full_path.exists():
                with open(full_path, 'r', encoding='utf-8') as f:
                    self.industrial_companies = json.load(f)
                print(f"📊 Loaded {len(self.industrial_companies)} industrial companies")
            else:
                print(f"⚠️  Industrial companies data not found at {data_path}")

        except Exception as e:
            print(f"❌ Error loading industrial companies: {e}")
            self.industrial_companies = []

    def generate_organizations(self, count: Optional[int] = None) -> List[Organization]:
        """Generate organizations with industrial company integration"""
        count = count or self.config['generation']['organizations']['count']

        organizations = []
        industrial_config = self.config.get('industrial_integration', {})
        integration_weight = industrial_config.get('integration_weight', 0.4)

        # Determine how many organizations should be based on industrial companies
        industrial_based_count = int(count * integration_weight) if self.industrial_companies else 0
        synthetic_count = count - industrial_based_count

        print(f"🏭 Generating {industrial_based_count} industrial-based organizations")
        print(f"🧬 Generating {synthetic_count} synthetic organizations")

        # Generate industrial company based organizations
        for i in range(industrial_based_count):
            if i < len(self.industrial_companies):
                industrial_company = self.industrial_companies[i]
                org = self._create_organization_from_industrial_data(
                    org_id=f"ind_org_{i:03d}",
                    industrial_data=industrial_company
                )
                organizations.append(org)
                self.generated_orgs.append(org)

        # Generate remaining synthetic organizations
        for i in range(synthetic_count):
            org = self._generate_single_organization(f"syn_org_{i:03d}")
            organizations.append(org)
            self.generated_orgs.append(org)

        return organizations

    def _create_organization_from_industrial_data(self, org_id: str, industrial_data: Dict) -> Organization:
        """Create organization based on real industrial company data"""

        # Map industrial company to organization
        company_name = industrial_data.get('name', 'Unknown Company')
        industry = self._map_industrial_industry(industrial_data.get('industry', 'manufacturing'))
        region = industrial_data.get('headquarters', 'Unknown Location')
        size = industrial_data.get('employees', random.randint(1000, 10000))

        # Generate people for the organization
        num_people = random.randint(
            self.config['generation']['people']['per_organization']['min'],
            self.config['generation']['people']['per_organization']['max']
        )
        people = self._generate_people_hierarchy(org_id, num_people)

        # Extract meaningful data from industrial company
        revenue_numeric = industrial_data.get('revenue_numeric', 0)
        revenue_range = self._convert_revenue_to_range(revenue_numeric)

        # Create organization with industrial company characteristics
        org = Organization(
            id=org_id,
            name=company_name,
            industry=industry,
            size=size,
            revenue_range=revenue_range,
            profitable=revenue_numeric > 0.5,  # Assume profitable if revenue > $500M
            years_in_business=2024 - industrial_data.get('founded', 1990),
            headquarters=region,
            regions=self._extract_regions_from_locations(industrial_data.get('locations', [region])),
            structure_type=self._determine_structure_from_size(size),
            delegation_culture=self._determine_delegation_culture_from_industry(industry, size),
            decision_speed=self._infer_decision_speed(industry, size),
            innovation_index=industrial_data.get('innovation_index', random.random()),
            digital_maturity=industrial_data.get('digital_maturity', random.random()),
            people=people,
            departments=self._generate_departments_for_industry(industry),
            products=industrial_data.get('products', self._generate_products(industry)),
            services=industrial_data.get('services', self._generate_services(industry)),
            values=self._generate_industrial_values(industry),
            strategic_priorities=self._generate_industrial_priorities(industry, size)
        )

        return org

    def _map_industrial_industry(self, industrial_industry: str) -> str:
        """Map industrial company industry to synthetic data industry categories"""

        industry_mapping = {
            'Automotive': 'manufacturing',
            'Aerospace & Defense': 'manufacturing',
            'Machinery': 'manufacturing',
            'Electronics': 'technology',
            'Chemicals': 'manufacturing',
            'Pharmaceuticals': 'healthcare',
            'Oil & Gas': 'energy',
            'Renewable Energy': 'energy',
            'Utilities': 'energy',
            'Mining': 'manufacturing',
            'Construction': 'construction',
            'Semiconductors': 'technology',
            'Software': 'technology',
            'Robotics': 'technology',
            'Transportation': 'logistics',
            'Logistics': 'logistics',
            'Telecommunications': 'telecommunications'
        }

        return industry_mapping.get(industrial_industry, 'manufacturing')

    def _convert_revenue_to_range(self, revenue_numeric: Optional[float]) -> str:
        """Convert numeric revenue to range string"""

        if not revenue_numeric:
            return "$100M-$1B"

        if revenue_numeric < 0.1:
            return "$10M-$100M"
        elif revenue_numeric < 1:
            return "$100M-$1B"
        elif revenue_numeric < 5:
            return "$1B-$5B"
        elif revenue_numeric < 10:
            return "$5B-$10B"
        elif revenue_numeric < 50:
            return "$10B-$50B"
        elif revenue_numeric < 100:
            return "$50B-$100B"
        else:
            return "$100B+"

    def _extract_regions_from_locations(self, locations: List[str]) -> List[str]:
        """Extract regions from location list"""

        if not locations:
            return ['North America']

        regions = set()
        for location in locations:
            # Simple region mapping based on location
            location_lower = location.lower()
            if any(country in location_lower for country in ['usa', 'canada', 'mexico', 'america']):
                regions.add('North America')
            elif any(country in location_lower for country in ['uk', 'germany', 'france', 'italy', 'spain', 'europe']):
                regions.add('Europe')
            elif any(country in location_lower for country in ['china', 'japan', 'korea', 'singapore', 'asia', 'india']):
                regions.add('Asia Pacific')
            elif any(country in location_lower for country in ['brazil', 'argentina', 'latin', 'south america']):
                regions.add('Latin America')
            elif any(country in location_lower for country in ['saudi', 'uae', 'africa', 'middle east']):
                regions.add('Middle East & Africa')

        return list(regions) if regions else ['North America']

    def _determine_structure_from_size(self, size: int) -> str:
        """Determine organizational structure based on company size"""

        if size < 500:
            return 'flat'
        elif size < 2000:
            return random.choice(['hierarchical', 'matrix'])
        elif size < 10000:
            return random.choice(['hierarchical', 'matrix', 'divisional'])
        else:
            return 'hierarchical'

    def _determine_delegation_culture_from_industry(self, industry: str, size: int) -> str:
        """Determine delegation culture based on industry and size"""

        # Industry-specific patterns
        industry_cultures = {
            'technology': ['collaborative', 'distributed', 'agile'],
            'manufacturing': ['hierarchical', 'matrix', 'process-driven'],
            'healthcare': ['hierarchical', 'collaborative', 'regulatory'],
            'finance': ['hierarchical', 'matrix', 'risk-conscious'],
            'energy': ['hierarchical', 'safety-focused', 'regulatory'],
            'construction': ['project-based', 'hierarchical', 'collaborative']
        }

        cultures = industry_cultures.get(industry, ['hierarchical', 'collaborative'])

        # Size adjustment
        if size < 1000:
            cultures.extend(['flat', 'distributed'])
        elif size > 10000:
            cultures.extend(['formal', 'structured'])

        return random.choice(cultures)

    def _infer_decision_speed(self, industry: str, size: int) -> str:
        """Infer decision speed based on industry and size"""

        # Fast-moving industries
        if industry in ['technology', 'telecommunications']:
            return random.choice(['fast', 'agile', 'rapid'])

        # Regulated industries
        elif industry in ['healthcare', 'finance', 'energy']:
            return random.choice(['deliberate', 'systematic', 'cautious'])

        # Manufacturing and construction
        elif industry in ['manufacturing', 'construction']:
            return random.choice(['moderate', 'systematic', 'planned'])

        # Size factor
        if size > 50000:
            return random.choice(['deliberate', 'systematic'])
        elif size < 1000:
            return random.choice(['fast', 'agile'])

        return 'moderate'

    def _generate_departments_for_industry(self, industry: str) -> List[str]:
        """Generate departments specific to industry"""

        base_departments = ['Executive', 'Finance', 'HR', 'Operations', 'Legal']

        industry_departments = {
            'technology': ['Engineering', 'Product', 'DevOps', 'Data Science', 'AI/ML', 'Cybersecurity'],
            'manufacturing': ['Production', 'Quality Control', 'Supply Chain', 'R&D', 'Safety', 'Maintenance'],
            'healthcare': ['Clinical', 'Research', 'Regulatory Affairs', 'Quality Assurance', 'Medical Affairs'],
            'finance': ['Trading', 'Risk Management', 'Compliance', 'Investment Banking', 'Asset Management'],
            'energy': ['Exploration', 'Production', 'Refining', 'Environmental', 'Safety', 'Trading'],
            'construction': ['Project Management', 'Engineering', 'Safety', 'Procurement', 'Quality Control'],
            'telecommunications': ['Network Operations', 'Customer Service', 'Technology', 'Regulatory'],
            'logistics': ['Transportation', 'Warehousing', 'Supply Chain', 'Fleet Management', 'Customer Service']
        }

        specific_departments = industry_departments.get(industry, ['Sales', 'Marketing', 'Customer Service'])
        return base_departments + specific_departments

    def _generate_industrial_values(self, industry: str) -> List[str]:
        """Generate values relevant to industrial companies"""

        base_values = ['Integrity', 'Excellence', 'Innovation', 'Collaboration']

        industry_values = {
            'manufacturing': ['Quality', 'Continuous Improvement', 'Efficiency', 'Craftsmanship'],
            'technology': ['Innovation', 'Agility', 'Data-Driven', 'User-Centric'],
            'healthcare': ['Patient Safety', 'Scientific Rigor', 'Compassion', 'Access'],
            'energy': ['Safety', 'Environmental Responsibility', 'Reliability', 'Sustainability'],
            'construction': ['Safety', 'Quality', 'Timeliness', 'Partnership'],
            'finance': ['Trust', 'Transparency', 'Risk Management', 'Client Focus']
        }

        specific_values = industry_values.get(industry, ['Customer Focus', 'Accountability'])
        all_values = base_values + specific_values

        return random.sample(all_values, k=random.randint(4, 6))

    def _generate_industrial_priorities(self, industry: str, size: int) -> List[str]:
        """Generate strategic priorities for industrial companies"""

        base_priorities = ['Operational Excellence', 'Digital Transformation', 'Talent Development']

        industry_priorities = {
            'manufacturing': ['Industry 4.0', 'Supply Chain Resilience', 'Sustainability', 'Automation'],
            'technology': ['AI Innovation', 'Platform Scaling', 'Developer Experience', 'Market Expansion'],
            'healthcare': ['Patient Outcomes', 'Regulatory Compliance', 'Digital Health', 'Cost Management'],
            'energy': ['Energy Transition', 'Carbon Neutrality', 'Grid Modernization', 'Renewable Integration'],
            'construction': ['BIM Adoption', 'Sustainability', 'Safety Excellence', 'Digitalization'],
            'finance': ['Digital Banking', 'Risk Management', 'Regulatory Compliance', 'Customer Experience']
        }

        size_priorities = {
            'large': ['Global Expansion', 'M&A Strategy', 'ESG Leadership', 'Innovation Ecosystems'],
            'medium': ['Market Leadership', 'Technology Adoption', 'Operational Scaling', 'Partnership Strategy'],
            'small': ['Growth Acceleration', 'Market Penetration', 'Capability Building', 'Technology Investment']
        }

        size_category = 'large' if size > 10000 else 'medium' if size > 2000 else 'small'

        specific_priorities = industry_priorities.get(industry, ['Market Growth', 'Customer Satisfaction'])
        size_specific = size_priorities.get(size_category, [])

        all_priorities = base_priorities + specific_priorities + size_specific
        return random.sample(all_priorities, k=random.randint(3, 5))

    def generate_enhanced_scenarios(self, organization: Organization) -> List[DelegationScenario]:
        """Generate enhanced scenarios with more complexity"""

        num_scenarios = self.config['generation']['scenarios']['per_organization']
        scenarios = []

        # Use expanded scenario types
        scenario_types = self.config['generation']['scenarios']['types']

        for i in range(num_scenarios):
            scenario_type = random.choice(scenario_types)
            scenario = self._generate_enhanced_scenario(organization, scenario_type, i)
            scenarios.append(scenario)

        return scenarios

    def _generate_enhanced_scenario(self, org: Organization, scenario_type: str, index: int) -> DelegationScenario:
        """Generate enhanced delegation scenario with more realistic complexity"""

        # Select originator based on scenario type
        if scenario_type in ['strategic_planning', 'merger_acquisition', 'international_expansion']:
            # CEO-level scenarios
            executives = [p for p in org.people if p.level <= 1]
        elif scenario_type in ['digital_transformation', 'innovation_initiative', 'technology_adoption']:
            # CTO/VP-level scenarios
            executives = [p for p in org.people if p.level <= 2 and ('CTO' in p.role or 'technology' in p.role.lower() or 'innovation' in p.role.lower())]
        else:
            # VP-level scenarios
            executives = [p for p in org.people if p.level <= 2]

        originator = random.choice(executives) if executives else org.people[0]

        # Enhanced delegation chain
        chain_length = random.randint(
            self.config['generation']['scenarios']['delegation_chains']['min_length'],
            self.config['generation']['scenarios']['delegation_chains']['max_length']
        )

        delegation_chain = self._build_enhanced_delegation_chain(org, originator, chain_length, scenario_type)

        # Enhanced scenario details
        scenario = DelegationScenario(
            id=f"{org.id}_scenario_{scenario_type}_{index:03d}",
            organization_id=org.id,
            type=scenario_type,
            title=self._generate_enhanced_scenario_title(scenario_type, org),
            description=self._generate_enhanced_scenario_description(scenario_type, org),
            urgency=random.choice(self.config['generation']['scenarios']['urgency_levels']),
            scope=random.choice(self.config['generation']['scenarios']['scopes']),
            originator=originator.id,
            delegation_chain=delegation_chain,
            expected_outcomes=self._generate_enhanced_expected_outcomes(scenario_type, org),
            success_metrics=self._generate_enhanced_success_metrics(scenario_type, org),
            risks=self._generate_enhanced_risks(scenario_type, org),
            timeline=self._generate_realistic_timeline(scenario_type)
        )

        return scenario

    def _build_enhanced_delegation_chain(self, org: Organization, originator: Person,
                                       length: int, scenario_type: str) -> List[Dict]:
        """Build enhanced delegation chain with more realistic interactions"""

        chain = []
        current_person = originator
        people_in_chain = [originator.id]

        for step in range(length):
            # Enhanced candidate selection based on scenario type
            candidates = self._find_delegation_candidates(org, current_person, scenario_type, people_in_chain)

            if not candidates:
                break

            next_person = random.choice(candidates)

            # Enhanced response type determination
            response_type = self._determine_enhanced_response_type(
                current_person, next_person, scenario_type, step
            )

            # Enhanced delegation step
            delegation_step = {
                'step': step + 1,
                'from': current_person.id,
                'from_name': current_person.name,
                'from_role': current_person.role,
                'from_level': current_person.level,
                'to': next_person.id,
                'to_name': next_person.name,
                'to_role': next_person.role,
                'to_level': next_person.level,
                'response_type': response_type,
                'message': self._generate_enhanced_delegation_message(
                    current_person, next_person, scenario_type, response_type, step
                ),
                'questions': self._generate_enhanced_questions(response_type, scenario_type),
                'proposed_actions': self._generate_enhanced_proposed_actions(scenario_type, response_type),
                'timeline': self._generate_step_timeline(response_type),
                'resources_needed': self._generate_resources_needed(scenario_type, response_type),
                'stakeholders': self._identify_stakeholders(scenario_type, org),
                'risk_factors': self._identify_step_risks(scenario_type, response_type)
            }

            chain.append(delegation_step)
            people_in_chain.append(next_person.id)

            # Continue chain logic
            if response_type in ['accept', 'delegate_further', 'collaborate']:
                current_person = next_person
            elif response_type in ['escalate']:
                # Find higher-level person
                higher_level_people = [p for p in org.people if p.level < current_person.level]
                if higher_level_people:
                    current_person = random.choice(higher_level_people)
                else:
                    break
            else:
                break

        return chain

    def _find_delegation_candidates(self, org: Organization, current_person: Person,
                                  scenario_type: str, people_in_chain: List[str]) -> List[Person]:
        """Find appropriate delegation candidates based on scenario and context"""

        candidates = []

        # Scenario-specific delegation patterns
        if scenario_type in ['technology_adoption', 'digital_transformation']:
            # Look for technical people
            tech_keywords = ['CTO', 'technology', 'engineering', 'digital', 'IT', 'data']
            candidates = [p for p in org.people
                         if any(keyword.lower() in p.role.lower() for keyword in tech_keywords)
                         and p.id not in people_in_chain]

        elif scenario_type in ['cost_optimization', 'resource_allocation']:
            # Look for finance/operations people
            finance_keywords = ['CFO', 'finance', 'controller', 'operations', 'procurement']
            candidates = [p for p in org.people
                         if any(keyword.lower() in p.role.lower() for keyword in finance_keywords)
                         and p.id not in people_in_chain]

        elif scenario_type in ['market_expansion', 'competitive_response']:
            # Look for sales/marketing people
            sales_keywords = ['sales', 'marketing', 'business development', 'growth', 'customer']
            candidates = [p for p in org.people
                         if any(keyword.lower() in p.role.lower() for keyword in sales_keywords)
                         and p.id not in people_in_chain]

        # Fallback to standard delegation patterns
        if not candidates:
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

        return candidates

    def _determine_enhanced_response_type(self, from_person: Person, to_person: Person,
                                        scenario_type: str, step: int) -> str:
        """Enhanced response type determination with more factors"""

        distribution = self.config['generation']['scenarios']['delegation_chains']['response_distribution'].copy()

        # Personality adjustments
        if 'analytical' in to_person.personality_traits:
            distribution['clarify'] += 0.15
            distribution['accept'] -= 0.1
            distribution['push_back'] += 0.05

        if 'decisive' in to_person.personality_traits:
            distribution['accept'] += 0.2
            distribution['clarify'] -= 0.15

        if 'collaborative' in to_person.personality_traits:
            distribution['collaborate'] += 0.1
            distribution['delegate_further'] += 0.05

        # Scenario type adjustments
        if scenario_type in ['crisis_management', 'emergency_response']:
            distribution['accept'] += 0.15
            distribution['clarify'] -= 0.1

        elif scenario_type in ['strategic_planning', 'merger_acquisition']:
            distribution['clarify'] += 0.1
            distribution['push_back'] += 0.05

        # Step-based adjustments (later in chain = more acceptance)
        if step > 3:
            distribution['accept'] += 0.1
            distribution['push_back'] -= 0.05

        # Level difference adjustments
        level_diff = from_person.level - to_person.level
        if level_diff > 2:  # Big hierarchy jump
            distribution['clarify'] += 0.1
            distribution['push_back'] += 0.05

        # Normalize distribution
        total = sum(distribution.values())
        for key in distribution:
            distribution[key] /= total

        # Random selection
        types = list(distribution.keys())
        weights = list(distribution.values())

        return random.choices(types, weights=weights)[0]

    def _generate_enhanced_delegation_message(self, from_person: Person, to_person: Person,
                                            scenario_type: str, response_type: str, step: int) -> str:
        """Generate more contextual and realistic delegation messages"""

        # Context-aware message templates
        context = {
            'from_name': from_person.name,
            'to_name': to_person.name,
            'scenario': scenario_type.replace('_', ' ').title(),
            'step': step + 1
        }

        templates = {
            'accept': [
                f"I understand the importance of {context['scenario']}. I'll take ownership and ensure we deliver.",
                f"This aligns perfectly with our {to_person.department} priorities. Count on us to execute.",
                f"I have the right team and resources to tackle {context['scenario']}. We'll make it happen.",
                f"Given my experience with similar initiatives, I'm confident we can deliver strong results."
            ],
            'clarify': [
                f"Before we proceed with {context['scenario']}, I need clarity on a few critical aspects.",
                f"I want to ensure we're aligned on expectations for {context['scenario']}. Can we discuss the details?",
                f"To deliver the best outcome for {context['scenario']}, I need to understand the constraints and requirements better.",
                f"Let me make sure I fully understand the scope and success criteria before committing my team."
            ],
            'push_back': [
                f"I have concerns about the feasibility of {context['scenario']} given our current priorities and resources.",
                f"While I understand the importance of {context['scenario']}, we need to consider the trade-offs with existing commitments.",
                f"The timeline for {context['scenario']} seems aggressive considering our capacity. Can we explore alternatives?",
                f"I believe there might be more effective approaches to achieve the goals of {context['scenario']}."
            ],
            'delegate_further': [
                f"For {context['scenario']}, I believe my team lead who specializes in this area would be the best choice.",
                f"I'm connecting you with our subject matter expert who has extensive experience with {context['scenario']}.",
                f"Given the technical nature of {context['scenario']}, I recommend involving our specialist team directly.",
                f"I'll loop in the right people who have the specific expertise needed for {context['scenario']}."
            ],
            'collaborate': [
                f"For {context['scenario']}, I think we should form a cross-functional team to ensure comprehensive coverage.",
                f"This initiative would benefit from collaboration between our teams. Let's set up a joint working group.",
                f"I propose we combine our expertise with other departments to maximize the impact of {context['scenario']}.",
                f"Let's create a collaborative approach that leverages multiple perspectives for {context['scenario']}."
            ],
            'escalate': [
                f"Given the strategic importance of {context['scenario']}, I believe we need executive involvement.",
                f"The scope and implications of {context['scenario']} require decisions above my level.",
                f"I recommend elevating {context['scenario']} to ensure we have the necessary authority and resources.",
                f"This initiative touches on areas that need senior leadership alignment and support."
            ]
        }

        messages = templates.get(response_type, [f"I'll review {context['scenario']} and respond with next steps."])
        return random.choice(messages)

    def save_enhanced_outputs(self, output_dir: str, organizations: List[Organization],
                            scenarios: Dict[str, List[DelegationScenario]]):
        """Save enhanced outputs with additional analytics"""

        super().save_outputs(output_dir, organizations, scenarios)

        output_path = Path(output_dir)

        # Generate enhanced analytics
        analytics = self._generate_enhanced_analytics(organizations, scenarios)
        analytics_file = output_path / 'enhanced_analytics.json'
        with open(analytics_file, 'w') as f:
            json.dump(analytics, f, indent=2)

        # Generate industrial company mapping
        if self.industrial_companies:
            mapping = self._generate_industrial_mapping(organizations)
            mapping_file = output_path / 'industrial_company_mapping.json'
            with open(mapping_file, 'w') as f:
                json.dump(mapping, f, indent=2)

        print(f"📊 Enhanced analytics saved to {analytics_file}")
        if self.industrial_companies:
            print(f"🏭 Industrial mapping saved to {mapping_file}")

    def _generate_enhanced_analytics(self, organizations: List[Organization],
                                   scenarios: Dict[str, List[DelegationScenario]]) -> Dict[str, Any]:
        """Generate enhanced analytics with industrial insights"""

        analytics = {
            'generation_metadata': {
                'timestamp': datetime.now().isoformat(),
                'organizations_count': len(organizations),
                'total_people': sum(len(org.people) for org in organizations),
                'total_scenarios': sum(len(s) for s in scenarios.values()),
                'industrial_companies_used': len([org for org in organizations if org.id.startswith('ind_')])
            },
            'industry_analysis': {},
            'regional_analysis': {},
            'delegation_patterns': {},
            'complexity_metrics': {}
        }

        # Industry analysis
        industry_counts = {}
        for org in organizations:
            industry_counts[org.industry] = industry_counts.get(org.industry, 0) + 1

        analytics['industry_analysis'] = {
            'distribution': industry_counts,
            'diversity_score': len(industry_counts) / len(organizations) if organizations else 0
        }

        # Regional analysis
        region_data = {}
        for org in organizations:
            for region in org.regions:
                if region not in region_data:
                    region_data[region] = {'companies': 0, 'total_employees': 0, 'revenue_estimate': 0}
                region_data[region]['companies'] += 1
                region_data[region]['total_employees'] += len(org.people)

        analytics['regional_analysis'] = region_data

        # Delegation pattern analysis
        response_patterns = {}
        chain_lengths = []
        for org_scenarios in scenarios.values():
            for scenario in org_scenarios:
                chain_lengths.append(len(scenario.delegation_chain))
                for step in scenario.delegation_chain:
                    response_type = step.get('response_type', 'unknown')
                    response_patterns[response_type] = response_patterns.get(response_type, 0) + 1

        analytics['delegation_patterns'] = {
            'response_distribution': response_patterns,
            'average_chain_length': sum(chain_lengths) / len(chain_lengths) if chain_lengths else 0,
            'max_chain_length': max(chain_lengths) if chain_lengths else 0,
            'min_chain_length': min(chain_lengths) if chain_lengths else 0
        }

        return analytics

    def _generate_industrial_mapping(self, organizations: List[Organization]) -> Dict[str, Any]:
        """Generate mapping between industrial companies and synthetic organizations"""

        mapping = {
            'industrial_based_organizations': [],
            'synthetic_organizations': [],
            'mapping_statistics': {}
        }

        for org in organizations:
            if org.id.startswith('ind_'):
                mapping['industrial_based_organizations'].append({
                    'org_id': org.id,
                    'name': org.name,
                    'industry': org.industry,
                    'size': org.size,
                    'revenue_range': org.revenue_range
                })
            else:
                mapping['synthetic_organizations'].append({
                    'org_id': org.id,
                    'name': org.name,
                    'industry': org.industry,
                    'size': org.size,
                    'revenue_range': org.revenue_range
                })

        mapping['mapping_statistics'] = {
            'industrial_based_count': len(mapping['industrial_based_organizations']),
            'synthetic_count': len(mapping['synthetic_organizations']),
            'total_organizations': len(organizations),
            'industrial_integration_rate': len(mapping['industrial_based_organizations']) / len(organizations)
        }

        return mapping

@click.command()
@click.option('--output-dir', default='synthetic-data/enhanced_outputs', help='Output directory')
@click.option('--config', default='synthetic-data/enhanced_config.yaml', help='Enhanced configuration file')
@click.option('--count', type=int, help='Number of organizations to generate')
def main(output_dir: str, config: str, count: Optional[int]):
    """Generate enhanced synthetic organizational data with industrial company integration"""

    print("🏢 Generating enhanced synthetic organizations with industrial data...")

    generator = EnhancedSyntheticDataGenerator(config)

    # Generate organizations
    organizations = generator.generate_organizations(count)

    # Generate enhanced scenarios for each organization
    all_scenarios = {}
    for org in organizations:
        scenarios = generator.generate_enhanced_scenarios(org)
        all_scenarios[org.id] = scenarios

    # Save enhanced outputs
    generator.save_enhanced_outputs(output_dir, organizations, all_scenarios)

    print(f"✅ Enhanced generation complete!")
    print(f"📊 Generated {len(organizations)} organizations with {sum(len(org.people) for org in organizations)} people")
    print(f"📋 Generated {sum(len(s) for s in all_scenarios.values())} enhanced delegation scenarios")
    print(f"🏭 Industrial companies integrated: {len([org for org in organizations if org.id.startswith('ind_')])}")

if __name__ == '__main__':
    main()