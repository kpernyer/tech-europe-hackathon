#!/usr/bin/env python3
"""
Standalone Industrial Data Generation Script
Generates comprehensive industrial company data and integrates with synthetic organizations
"""

import json
from pathlib import Path
from industrial_company_generator import IndustrialCompanyGenerator

def main():
    """Run complete industrial data generation pipeline"""

    print("🚀 Starting Industrial Data Generation Pipeline...")
    print("=" * 60)

    # Step 1: Generate Industrial Companies Data
    print("\n📊 Step 1: Generating Industrial Companies Dataset")
    generator = IndustrialCompanyGenerator()

    # Generate different sized datasets
    datasets = {
        'small': 200,
        'medium': 500,
        'large': 1000
    }

    print(f"Available dataset sizes: {list(datasets.keys())}")

    # Generate medium dataset (500 companies)
    companies = generator.generate_all_industrial_companies(total_companies=500)

    # Print comprehensive summary
    generator.print_summary()

    # Save all data
    print(f"\n💾 Step 2: Saving Generated Data")
    files = generator.save_data()

    print(f"\n✅ Files Generated:")
    for file_type, file_path in files.items():
        print(f"  📄 {file_type.replace('_', ' ').title()}: {file_path}")

    # Step 3: Generate Sample Analysis
    print(f"\n📈 Step 3: Generating Sample Analysis")

    # Analyze by region
    regional_analysis = analyze_by_region(companies)
    print(f"\n🌍 Regional Distribution:")
    for region, data in regional_analysis.items():
        print(f"  {region}: {data['count']} companies, ${data['total_revenue']:.1f}B total revenue")

    # Analyze by industry
    industry_analysis = analyze_by_industry(companies)
    print(f"\n🏭 Top Industries by Company Count:")
    sorted_industries = sorted(industry_analysis.items(), key=lambda x: x[1]['count'], reverse=True)[:10]
    for industry, data in sorted_industries:
        print(f"  {industry}: {data['count']} companies, avg revenue ${data['avg_revenue']:.1f}B")

    # Step 4: Generate Integration Examples
    print(f"\n🔗 Step 4: Creating Integration Examples")
    create_integration_examples(companies)

    print(f"\n🎉 Industrial Data Generation Complete!")
    print(f"📊 Generated {len(companies)} companies across {len(regional_analysis)} regions")
    print(f"🌍 Coverage: {len(industry_analysis)} different industries")

    total_revenue = sum(c.revenue_numeric for c in companies if c.revenue_numeric)
    total_employees = sum(c.employees for c in companies if c.employees)

    print(f"💰 Total Revenue: ${total_revenue:,.1f}B")
    print(f"👥 Total Employees: {total_employees:,}")

    return files

def analyze_by_region(companies):
    """Analyze companies by region"""
    regional_data = {}

    for company in companies:
        region = company.region
        if region not in regional_data:
            regional_data[region] = {
                'count': 0,
                'total_revenue': 0,
                'companies': []
            }

        regional_data[region]['count'] += 1
        regional_data[region]['total_revenue'] += company.revenue_numeric or 0
        regional_data[region]['companies'].append({
            'name': company.name,
            'industry': company.industry,
            'revenue': company.revenue_numeric
        })

    return regional_data

def analyze_by_industry(companies):
    """Analyze companies by industry"""
    industry_data = {}

    for company in companies:
        industry = company.industry
        if industry not in industry_data:
            industry_data[industry] = {
                'count': 0,
                'total_revenue': 0,
                'revenues': []
            }

        industry_data[industry]['count'] += 1
        if company.revenue_numeric:
            industry_data[industry]['total_revenue'] += company.revenue_numeric
            industry_data[industry]['revenues'].append(company.revenue_numeric)

    # Calculate averages
    for industry, data in industry_data.items():
        if data['revenues']:
            data['avg_revenue'] = sum(data['revenues']) / len(data['revenues'])
        else:
            data['avg_revenue'] = 0

    return industry_data

def create_integration_examples(companies):
    """Create integration examples for synthetic data"""

    output_dir = Path("synthetic-data/integration_examples")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Select diverse companies for integration examples
    examples = []

    # Select by region (top companies from each region)
    regions_represented = {}
    for company in companies:
        region = company.region
        if region not in regions_represented:
            regions_represented[region] = []

        if len(regions_represented[region]) < 3:  # Top 3 per region
            regions_represented[region].append(company)

    # Flatten and create integration examples
    for region, region_companies in regions_represented.items():
        for company in region_companies:
            example = {
                'organization_template': {
                    'name': company.name,
                    'industry': company.industry,
                    'size': company.employees,
                    'revenue_range': company.revenue,
                    'headquarters': company.headquarters,
                    'region': company.region,
                    'founded': company.founded,
                    'products': company.products,
                    'services': company.services,
                    'certifications': company.certifications,
                    'sustainability_score': company.sustainability_score,
                    'innovation_index': company.innovation_index,
                    'digital_maturity': company.digital_maturity
                },
                'suggested_scenarios': generate_industry_scenarios(company.industry),
                'delegation_characteristics': infer_delegation_patterns(company)
            }

            examples.append(example)

    # Save integration examples
    integration_file = output_dir / "industrial_integration_examples.json"
    with open(integration_file, 'w', encoding='utf-8') as f:
        json.dump(examples, f, indent=2, ensure_ascii=False)

    # Create summary
    summary = {
        'total_examples': len(examples),
        'regions_covered': list(regions_represented.keys()),
        'industries_covered': list(set(ex['organization_template']['industry'] for ex in examples)),
        'usage_guide': {
            'description': 'These examples show how industrial company data can be integrated into synthetic organization generation',
            'fields_mapping': {
                'name': 'Use real company name or generate similar',
                'industry': 'Map to synthetic data industry categories',
                'size': 'Use actual employee count',
                'revenue_range': 'Convert to revenue range buckets',
                'products_services': 'Use for realistic product/service generation',
                'certifications': 'Industry-specific compliance and standards'
            },
            'scenario_suggestions': 'Each example includes scenarios relevant to the industry',
            'delegation_patterns': 'Inferred delegation characteristics based on company size and industry'
        }
    }

    summary_file = output_dir / "integration_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"  📋 Created {len(examples)} integration examples")
    print(f"  📄 Saved to: {integration_file}")
    print(f"  📊 Summary: {summary_file}")

def generate_industry_scenarios(industry):
    """Generate relevant scenarios for industry"""

    base_scenarios = [
        'strategic_planning',
        'resource_allocation',
        'digital_transformation',
        'operational_excellence'
    ]

    industry_specific = {
        'Automotive': [
            'electric_vehicle_transition',
            'autonomous_driving_development',
            'supply_chain_disruption',
            'sustainability_initiative'
        ],
        'Aerospace & Defense': [
            'next_gen_aircraft_program',
            'defense_contract_execution',
            'space_program_development',
            'regulatory_compliance'
        ],
        'Oil & Gas': [
            'energy_transition',
            'carbon_neutrality_program',
            'drilling_optimization',
            'renewable_investment'
        ],
        'Semiconductors': [
            'chip_shortage_response',
            'fab_capacity_expansion',
            'ai_chip_development',
            'geopolitical_supply_chain'
        ],
        'Pharmaceuticals': [
            'drug_development_pipeline',
            'clinical_trial_management',
            'regulatory_approval',
            'manufacturing_scale_up'
        ]
    }

    specific = industry_specific.get(industry, [
        'market_expansion',
        'innovation_initiative',
        'cost_optimization',
        'competitive_response'
    ])

    return base_scenarios + specific

def infer_delegation_patterns(company):
    """Infer delegation patterns based on company characteristics"""

    patterns = {
        'delegation_culture': 'hierarchical',  # Default
        'decision_speed': 'moderate',
        'collaboration_level': 'medium',
        'innovation_orientation': 'balanced'
    }

    # Industry-based patterns
    if company.industry in ['Software', 'AI/ML', 'Semiconductors']:
        patterns['delegation_culture'] = 'collaborative'
        patterns['decision_speed'] = 'fast'
        patterns['innovation_orientation'] = 'high'

    elif company.industry in ['Oil & Gas', 'Pharmaceuticals', 'Aerospace & Defense']:
        patterns['delegation_culture'] = 'hierarchical'
        patterns['decision_speed'] = 'deliberate'
        patterns['collaboration_level'] = 'structured'

    elif company.industry in ['Manufacturing', 'Automotive']:
        patterns['delegation_culture'] = 'matrix'
        patterns['decision_speed'] = 'systematic'
        patterns['collaboration_level'] = 'high'

    # Size-based adjustments
    if company.employees and company.employees > 50000:
        patterns['delegation_culture'] = 'hierarchical'
        patterns['decision_speed'] = 'deliberate'
    elif company.employees and company.employees < 5000:
        patterns['delegation_culture'] = 'flat'
        patterns['decision_speed'] = 'fast'

    # Innovation and digital maturity influence
    if company.innovation_index and company.innovation_index > 0.8:
        patterns['innovation_orientation'] = 'high'
        patterns['collaboration_level'] = 'high'

    if company.digital_maturity and company.digital_maturity > 0.8:
        patterns['decision_speed'] = 'fast'
        patterns['collaboration_level'] = 'high'

    return patterns

if __name__ == "__main__":
    main()