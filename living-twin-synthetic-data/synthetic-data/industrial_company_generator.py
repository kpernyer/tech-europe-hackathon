#!/usr/bin/env python3
"""
Industrial Companies Data Generator
Generates comprehensive industrial company data across global regions
"""

import json
import csv
import random
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import re

@dataclass
class IndustrialCompany:
    """Industrial company profile"""
    id: str
    name: str
    industry: str
    sector: str
    subsector: str
    revenue: Optional[str]
    revenue_numeric: Optional[float]
    employees: Optional[int]
    headquarters: str
    country: str
    region: str
    founded: Optional[int]
    ceo: Optional[str]
    website: Optional[str]
    description: Optional[str]
    products: List[str]
    services: List[str]
    market_cap: Optional[str]
    stock_exchange: Optional[str]
    ticker: Optional[str]
    subsidiaries: List[str]
    locations: List[str]
    certifications: List[str]
    sustainability_score: Optional[float]
    innovation_index: Optional[float]
    digital_maturity: Optional[float]
    source: str
    scraped_date: str

class IndustrialCompanyGenerator:
    """Generates comprehensive industrial company data"""

    def __init__(self, output_dir: str = "synthetic-data/industrial_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.companies = []

        # Global regions and countries
        self.regions = {
            'North America': ['United States', 'Canada', 'Mexico'],
            'Europe': ['Germany', 'United Kingdom', 'France', 'Italy', 'Spain', 'Netherlands',
                      'Switzerland', 'Sweden', 'Norway', 'Denmark', 'Austria', 'Belgium', 'Poland'],
            'Asia Pacific': ['China', 'Japan', 'South Korea', 'India', 'Singapore', 'Taiwan',
                           'Australia', 'Thailand', 'Malaysia', 'Indonesia', 'Philippines', 'Vietnam'],
            'Latin America': ['Brazil', 'Argentina', 'Chile', 'Colombia', 'Peru', 'Venezuela', 'Ecuador'],
            'Middle East & Africa': ['Saudi Arabia', 'UAE', 'Qatar', 'South Africa', 'Egypt', 'Nigeria',
                                   'Turkey', 'Israel', 'Morocco']
        }

        # Industrial sectors and subsectors
        self.industrial_sectors = {
            'Manufacturing': {
                'Automotive': ['Vehicle Assembly', 'Auto Parts', 'Electric Vehicles', 'Autonomous Systems'],
                'Aerospace & Defense': ['Commercial Aircraft', 'Military Aircraft', 'Space Systems', 'Defense Equipment'],
                'Machinery': ['Industrial Machinery', 'Construction Equipment', 'Agricultural Equipment', 'Mining Equipment'],
                'Electronics': ['Consumer Electronics', 'Industrial Electronics', 'Telecommunications Equipment', 'Test Equipment'],
                'Chemicals': ['Basic Chemicals', 'Specialty Chemicals', 'Petrochemicals', 'Agricultural Chemicals'],
                'Pharmaceuticals': ['Prescription Drugs', 'Generic Drugs', 'Biotechnology', 'Medical Devices'],
                'Food & Beverage': ['Food Processing', 'Beverage Manufacturing', 'Packaging', 'Food Safety'],
                'Textiles': ['Apparel Manufacturing', 'Technical Textiles', 'Home Textiles', 'Industrial Fabrics'],
                'Metals': ['Steel Production', 'Aluminum', 'Copper', 'Precious Metals'],
                'Plastics': ['Polymer Production', 'Plastic Components', 'Packaging Materials', 'Composite Materials']
            },
            'Energy': {
                'Oil & Gas': ['Upstream Operations', 'Refining', 'Petrochemicals', 'Distribution'],
                'Renewable Energy': ['Solar Power', 'Wind Power', 'Hydroelectric', 'Geothermal'],
                'Utilities': ['Electric Power', 'Natural Gas Distribution', 'Water Treatment', 'Waste Management'],
                'Mining': ['Coal Mining', 'Metal Mining', 'Industrial Minerals', 'Rare Earth Elements'],
                'Nuclear': ['Nuclear Power Generation', 'Nuclear Technology', 'Nuclear Services', 'Waste Management']
            },
            'Infrastructure': {
                'Construction': ['Commercial Construction', 'Infrastructure Projects', 'Residential Construction', 'Industrial Construction'],
                'Transportation': ['Railway Systems', 'Aviation Infrastructure', 'Maritime Infrastructure', 'Urban Transport'],
                'Logistics': ['Supply Chain Management', 'Warehousing', 'Distribution', 'Third-Party Logistics'],
                'Telecommunications': ['Network Infrastructure', 'Wireless Technology', 'Fiber Optics', '5G Technology'],
                'Real Estate': ['Industrial Real Estate', 'Commercial Development', 'Infrastructure Investment', 'Property Management']
            },
            'Technology': {
                'Semiconductors': ['Chip Manufacturing', 'Semiconductor Equipment', 'Electronic Components', 'Memory Devices'],
                'Software': ['Enterprise Software', 'Industrial Software', 'ERP Systems', 'Manufacturing Execution'],
                'Hardware': ['Computer Hardware', 'Server Systems', 'Industrial Computers', 'Embedded Systems'],
                'AI/ML': ['Artificial Intelligence', 'Machine Learning Platforms', 'Computer Vision', 'Robotics AI'],
                'IoT': ['Industrial IoT', 'Smart Sensors', 'Connected Devices', 'Edge Computing'],
                'Robotics': ['Industrial Robots', 'Service Robots', 'Automation Systems', 'Robotic Components']
            }
        }

        # Company name components
        self.company_prefixes = {
            'Manufacturing': ['Advanced', 'Precision', 'Global', 'Industrial', 'Modern', 'Elite', 'Premier', 'Superior'],
            'Energy': ['Energy', 'Power', 'Green', 'Sustainable', 'Clean', 'Renewable', 'Eco', 'Future'],
            'Infrastructure': ['Build', 'Construct', 'Infrastructure', 'Development', 'Project', 'Engineering', 'Design'],
            'Technology': ['Tech', 'Digital', 'Cyber', 'Smart', 'Intelligent', 'Innovation', 'Next-Gen', 'AI']
        }

        self.company_suffixes = {
            'Manufacturing': ['Manufacturing', 'Industries', 'Corp', 'Systems', 'Solutions', 'Technologies', 'Group'],
            'Energy': ['Energy', 'Power', 'Resources', 'Solutions', 'Systems', 'Technologies', 'Group'],
            'Infrastructure': ['Construction', 'Engineering', 'Development', 'Projects', 'Solutions', 'Group'],
            'Technology': ['Technologies', 'Systems', 'Solutions', 'Labs', 'Innovations', 'Digital', 'AI']
        }

        # CEO names by region
        self.ceo_names = {
            'North America': ['James Smith', 'Robert Johnson', 'Patricia Williams', 'Jennifer Brown', 'Michael Davis', 'Linda Miller', 'William Wilson', 'Elizabeth Moore'],
            'Europe': ['Hans Müller', 'Marie Dubois', 'Giovanni Rossi', 'Ana García', 'Erik Andersson', 'Ingrid Hansen', 'Klaus Weber', 'Francesca Romano'],
            'Asia Pacific': ['Hiroshi Tanaka', 'Li Wei', 'Park Min-ho', 'Raj Patel', 'Chen Ming', 'Yamada Kenji', 'Kim Soo-jin', 'Singh Rajesh'],
            'Latin America': ['Carlos Silva', 'Maria González', 'João Santos', 'Ana López', 'Ricardo Morales', 'Luz Fernández', 'Diego Pérez', 'Isabella Ruiz'],
            'Middle East & Africa': ['Ahmed Al-Rashid', 'Fatima Hassan', 'Omar Ben Ali', 'Nour El-Din', 'Ibrahim Okafor', 'Amina Kone', 'Yusuf Mbeki', 'Sarah Al-Zahra']
        }

    def generate_all_industrial_companies(self, total_companies: int = 500):
        """Generate comprehensive industrial companies dataset"""
        print(f"🏭 Generating {total_companies} industrial companies across all regions...")

        companies_per_region = {
            'North America': int(total_companies * 0.25),
            'Europe': int(total_companies * 0.25),
            'Asia Pacific': int(total_companies * 0.30),
            'Latin America': int(total_companies * 0.10),
            'Middle East & Africa': int(total_companies * 0.10)
        }

        for region, count in companies_per_region.items():
            self._generate_regional_companies(region, count)

        print(f"✅ Generated {len(self.companies)} industrial companies")
        return self.companies

    def _generate_regional_companies(self, region: str, count: int):
        """Generate companies for a specific region"""
        print(f"  🌍 Generating {count} companies for {region}")

        countries = self.regions[region]

        for i in range(count):
            country = random.choice(countries)
            sector = random.choice(list(self.industrial_sectors.keys()))
            industry = random.choice(list(self.industrial_sectors[sector].keys()))
            subsector = random.choice(self.industrial_sectors[sector][industry])

            company = self._create_company(
                company_id=f"{region.lower().replace(' ', '_')}_{i:03d}",
                region=region,
                country=country,
                sector=sector,
                industry=industry,
                subsector=subsector
            )

            self.companies.append(company)

    def _create_company(self, company_id: str, region: str, country: str,
                       sector: str, industry: str, subsector: str) -> IndustrialCompany:
        """Create a single industrial company"""

        # Generate company name
        name = self._generate_company_name(sector, industry, country)

        # Generate revenue and employees
        revenue_numeric = self._generate_revenue()
        revenue_str = f"${revenue_numeric:.1f}B"
        employees = self._estimate_employees(revenue_numeric, industry)

        # Generate other attributes
        founded_year = random.randint(1890, 2020)
        ceo_name = random.choice(self.ceo_names.get(region, ['John Doe']))

        company = IndustrialCompany(
            id=company_id,
            name=name,
            industry=industry,
            sector=sector,
            subsector=subsector,
            revenue=revenue_str,
            revenue_numeric=revenue_numeric,
            employees=employees,
            headquarters=self._generate_headquarters(country),
            country=country,
            region=region,
            founded=founded_year,
            ceo=ceo_name,
            website=f"www.{name.lower().replace(' ', '').replace('.', '')}.com",
            description=self._generate_description(name, industry, subsector),
            products=self._generate_products(industry, subsector),
            services=self._generate_services(industry, subsector),
            market_cap=self._generate_market_cap(revenue_numeric),
            stock_exchange=self._get_stock_exchange(country),
            ticker=self._generate_ticker(name, country),
            subsidiaries=self._generate_subsidiaries(name, industry),
            locations=self._generate_locations(country, region, employees),
            certifications=self._generate_certifications(industry, subsector),
            sustainability_score=random.uniform(0.1, 0.95),
            innovation_index=random.uniform(0.2, 0.98),
            digital_maturity=random.uniform(0.3, 0.92),
            source="Industrial Company Database",
            scraped_date=datetime.now().isoformat()
        )

        return company

    def _generate_company_name(self, sector: str, industry: str, country: str) -> str:
        """Generate realistic company name"""

        prefixes = self.company_prefixes.get(sector, ['Global'])
        suffixes = self.company_suffixes.get(sector, ['Corp'])

        # Add some geographical names
        geographical_elements = {
            'United States': ['American', 'United', 'National', 'Continental'],
            'Germany': ['Deutsche', 'German', 'Euro', 'Continental'],
            'Japan': ['Japanese', 'Nippon', 'Tokyo', 'Pacific'],
            'China': ['China', 'Sino', 'Pacific', 'Eastern'],
            'United Kingdom': ['British', 'Anglo', 'Royal', 'Imperial'],
            'France': ['French', 'Euro', 'Continental', 'International'],
            'South Korea': ['Korean', 'Pacific', 'Eastern', 'Asia'],
            'India': ['Indian', 'Bharath', 'Asia', 'Continental']
        }

        # Randomly choose name pattern
        patterns = [
            f"{random.choice(prefixes)} {industry} {random.choice(suffixes)}",
            f"{random.choice(geographical_elements.get(country, ['Global']))} {random.choice(suffixes)}",
            f"{random.choice(prefixes)} {random.choice(suffixes)}",
            f"{industry} {random.choice(suffixes)}",
            f"{random.choice(['Alpha', 'Beta', 'Gamma', 'Delta', 'Omega'])} {random.choice(suffixes)}"
        ]

        name = random.choice(patterns)

        # Add occasional company type suffix
        if random.random() < 0.3:
            company_types = {
                'United States': ['Inc.', 'LLC', 'Corp.'],
                'Germany': ['GmbH', 'AG', 'SE'],
                'United Kingdom': ['Ltd.', 'PLC'],
                'France': ['SA', 'SAS'],
                'Japan': ['Co. Ltd.', 'Corp.'],
                'China': ['Co. Ltd.', 'Group'],
                'South Korea': ['Co. Ltd.', 'Corp.'],
                'India': ['Ltd.', 'Pvt. Ltd.']
            }

            company_type = random.choice(company_types.get(country, ['Corp.']))
            name += f" {company_type}"

        return name

    def _generate_revenue(self) -> float:
        """Generate revenue in billions USD"""
        # Distribution: many small companies, fewer giants
        if random.random() < 0.4:  # 40% small companies
            return random.uniform(0.1, 2.0)
        elif random.random() < 0.7:  # 30% medium companies
            return random.uniform(2.0, 20.0)
        elif random.random() < 0.9:  # 20% large companies
            return random.uniform(20.0, 100.0)
        else:  # 10% mega corporations
            return random.uniform(100.0, 500.0)

    def _estimate_employees(self, revenue: float, industry: str) -> int:
        """Estimate employees based on revenue and industry"""

        # Industry-specific revenue per employee (thousands USD)
        revenue_per_employee = {
            'Automotive': 300,
            'Aerospace & Defense': 400,
            'Machinery': 350,
            'Electronics': 450,
            'Chemicals': 500,
            'Pharmaceuticals': 600,
            'Oil & Gas': 800,
            'Renewable Energy': 400,
            'Utilities': 600,
            'Mining': 700,
            'Construction': 250,
            'Semiconductors': 800,
            'Software': 350,
            'Robotics': 400
        }

        base_revenue_per_employee = revenue_per_employee.get(industry, 400)
        # Add some variance
        actual_revenue_per_employee = base_revenue_per_employee * random.uniform(0.7, 1.3)

        employees = int((revenue * 1_000_000) / actual_revenue_per_employee)
        return max(100, employees)  # Minimum 100 employees

    def _generate_headquarters(self, country: str) -> str:
        """Generate headquarters location"""

        major_cities = {
            'United States': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose', 'Detroit', 'Seattle', 'Boston'],
            'Germany': ['Berlin', 'Munich', 'Hamburg', 'Frankfurt', 'Düsseldorf', 'Stuttgart', 'Cologne', 'Essen'],
            'United Kingdom': ['London', 'Manchester', 'Birmingham', 'Edinburgh', 'Bristol', 'Glasgow', 'Leeds'],
            'France': ['Paris', 'Lyon', 'Marseille', 'Toulouse', 'Nice', 'Strasbourg', 'Bordeaux'],
            'Italy': ['Rome', 'Milan', 'Naples', 'Turin', 'Florence', 'Bologna', 'Venice'],
            'Spain': ['Madrid', 'Barcelona', 'Valencia', 'Seville', 'Bilbao', 'Zaragoza'],
            'Netherlands': ['Amsterdam', 'Rotterdam', 'The Hague', 'Utrecht', 'Eindhoven'],
            'Switzerland': ['Zurich', 'Geneva', 'Basel', 'Bern', 'Lausanne'],
            'Sweden': ['Stockholm', 'Gothenburg', 'Malmö', 'Uppsala'],
            'Norway': ['Oslo', 'Bergen', 'Trondheim', 'Stavanger'],
            'Denmark': ['Copenhagen', 'Aarhus', 'Odense', 'Aalborg'],
            'China': ['Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen', 'Chengdu', 'Hangzhou', 'Nanjing', 'Tianjin', 'Wuhan', 'Xi\'an'],
            'Japan': ['Tokyo', 'Osaka', 'Nagoya', 'Yokohama', 'Kyoto', 'Kobe', 'Sapporo', 'Fukuoka'],
            'South Korea': ['Seoul', 'Busan', 'Incheon', 'Daegu', 'Daejeon', 'Ulsan'],
            'India': ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata', 'Pune', 'Ahmedabad'],
            'Taiwan': ['Taipei', 'Kaohsiung', 'Taichung', 'Tainan'],
            'Singapore': ['Singapore'],
            'Australia': ['Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide'],
            'Canada': ['Toronto', 'Vancouver', 'Montreal', 'Calgary', 'Ottawa', 'Edmonton'],
            'Mexico': ['Mexico City', 'Guadalajara', 'Monterrey', 'Puebla', 'Tijuana'],
            'Brazil': ['São Paulo', 'Rio de Janeiro', 'Salvador', 'Brasília', 'Fortaleza'],
            'Argentina': ['Buenos Aires', 'Córdoba', 'Rosario', 'Mendoza'],
            'Saudi Arabia': ['Riyadh', 'Jeddah', 'Mecca', 'Dammam'],
            'UAE': ['Dubai', 'Abu Dhabi', 'Sharjah'],
            'South Africa': ['Johannesburg', 'Cape Town', 'Durban', 'Pretoria']
        }

        cities = major_cities.get(country, [country])
        city = random.choice(cities)
        return f"{city}, {country}"

    def _generate_description(self, name: str, industry: str, subsector: str) -> str:
        """Generate company description"""

        templates = [
            f"{name} is a leading global provider of {subsector.lower()} solutions, serving customers across multiple industries with innovative products and services.",
            f"Founded as a pioneer in {industry.lower()}, {name} has evolved into a comprehensive {subsector.lower()} company with operations worldwide.",
            f"{name} specializes in {subsector.lower()} and related technologies, delivering cutting-edge solutions to industrial customers globally.",
            f"As a major player in the {industry.lower()} sector, {name} focuses on {subsector.lower()} with a commitment to innovation and sustainability.",
            f"{name} operates as a diversified {industry.lower()} company, with core expertise in {subsector.lower()} and a strong global presence."
        ]

        return random.choice(templates)

    def _generate_products(self, industry: str, subsector: str) -> List[str]:
        """Generate industry-specific products"""

        product_map = {
            'Automotive': ['Vehicles', 'Engine Systems', 'Transmission Components', 'Brake Systems', 'Electronic Control Units', 'Body Parts', 'Interior Systems'],
            'Aerospace & Defense': ['Aircraft', 'Aircraft Engines', 'Avionics Systems', 'Navigation Equipment', 'Defense Systems', 'Satellites', 'Radar Systems'],
            'Machinery': ['Industrial Machines', 'Manufacturing Equipment', 'Automation Systems', 'Precision Tools', 'Control Systems', 'Assembly Lines'],
            'Electronics': ['Consumer Electronics', 'Industrial Electronics', 'Semiconductors', 'Display Systems', 'Circuit Boards', 'Sensors'],
            'Chemicals': ['Industrial Chemicals', 'Specialty Chemicals', 'Polymers', 'Catalysts', 'Adhesives', 'Coatings'],
            'Pharmaceuticals': ['Prescription Drugs', 'Medical Devices', 'Diagnostic Equipment', 'Vaccines', 'Biologics', 'Generic Drugs'],
            'Oil & Gas': ['Crude Oil', 'Natural Gas', 'Refined Products', 'Petrochemicals', 'Lubricants', 'Pipeline Systems'],
            'Renewable Energy': ['Solar Panels', 'Wind Turbines', 'Energy Storage Systems', 'Power Inverters', 'Grid Systems'],
            'Construction': ['Construction Equipment', 'Building Materials', 'Prefab Structures', 'Safety Systems', 'Project Management Tools'],
            'Semiconductors': ['Microprocessors', 'Memory Chips', 'Sensors', 'Power Semiconductors', 'Analog Chips'],
            'Software': ['Enterprise Software', 'Manufacturing Execution Systems', 'ERP Solutions', 'Industrial IoT Platforms'],
            'Robotics': ['Industrial Robots', 'Automation Systems', 'Robot Controllers', 'Vision Systems', 'Safety Systems']
        }

        base_products = product_map.get(industry, ['Industrial Equipment', 'Systems', 'Components'])
        return random.sample(base_products, k=random.randint(3, min(6, len(base_products))))

    def _generate_services(self, industry: str, subsector: str) -> List[str]:
        """Generate industry-specific services"""

        service_map = {
            'Automotive': ['Vehicle Servicing', 'Parts Supply', 'Technical Support', 'Training Services', 'Financing Solutions'],
            'Aerospace & Defense': ['Maintenance Services', 'Technical Support', 'Training Programs', 'Consulting Services', 'Logistics Support'],
            'Machinery': ['Installation Services', 'Maintenance & Repair', 'Technical Training', 'Spare Parts', 'Consulting'],
            'Electronics': ['Technical Support', 'Repair Services', 'Custom Design', 'Installation Services', 'Training Programs'],
            'Chemicals': ['Technical Services', 'Custom Synthesis', 'Application Support', 'Logistics Services', 'R&D Services'],
            'Pharmaceuticals': ['Clinical Services', 'Regulatory Support', 'Manufacturing Services', 'Distribution', 'R&D Partnerships'],
            'Oil & Gas': ['Exploration Services', 'Drilling Services', 'Refining Services', 'Transportation', 'Technical Consulting'],
            'Renewable Energy': ['Installation Services', 'Maintenance Programs', 'Energy Consulting', 'Grid Integration', 'Financing Solutions'],
            'Construction': ['Project Management', 'Engineering Services', 'Construction Services', 'Maintenance', 'Consulting'],
            'Semiconductors': ['Design Services', 'Testing Services', 'Technical Support', 'Custom Manufacturing', 'R&D Services'],
            'Software': ['Implementation Services', 'Technical Support', 'Training Programs', 'Consulting Services', 'Cloud Services'],
            'Robotics': ['System Integration', 'Programming Services', 'Maintenance Support', 'Training Programs', 'Consulting']
        }

        base_services = service_map.get(industry, ['Professional Services', 'Technical Support', 'Consulting', 'Training'])
        return random.sample(base_services, k=random.randint(2, min(5, len(base_services))))

    def _generate_market_cap(self, revenue: float) -> str:
        """Generate market cap based on revenue"""
        # Typical market cap to revenue ratios by industry
        pe_ratios = {
            'Technology': random.uniform(3.0, 8.0),
            'Pharmaceuticals': random.uniform(4.0, 7.0),
            'Software': random.uniform(5.0, 12.0),
            'Manufacturing': random.uniform(1.5, 3.5),
            'Energy': random.uniform(1.0, 2.5),
            'Infrastructure': random.uniform(1.2, 2.8)
        }

        ratio = random.uniform(1.5, 4.0)  # Default ratio
        market_cap = revenue * ratio

        return f"${market_cap:.1f}B"

    def _get_stock_exchange(self, country: str) -> Optional[str]:
        """Get primary stock exchange for country"""

        exchanges = {
            'United States': 'NYSE/NASDAQ',
            'Canada': 'TSX',
            'Mexico': 'BMV',
            'Germany': 'Frankfurt Stock Exchange',
            'United Kingdom': 'London Stock Exchange',
            'France': 'Euronext Paris',
            'Italy': 'Borsa Italiana',
            'Spain': 'BME Spanish Exchanges',
            'Netherlands': 'Euronext Amsterdam',
            'Switzerland': 'SIX Swiss Exchange',
            'Sweden': 'Nasdaq Stockholm',
            'Norway': 'Oslo Stock Exchange',
            'Denmark': 'Nasdaq Copenhagen',
            'China': 'Shanghai/Shenzhen Stock Exchange',
            'Japan': 'Tokyo Stock Exchange',
            'South Korea': 'Korea Exchange',
            'India': 'BSE/NSE',
            'Taiwan': 'Taiwan Stock Exchange',
            'Singapore': 'Singapore Exchange',
            'Australia': 'ASX',
            'Brazil': 'B3',
            'Argentina': 'BCBA',
            'Saudi Arabia': 'Tadawul',
            'UAE': 'ADX/DFM',
            'South Africa': 'JSE'
        }

        return exchanges.get(country)

    def _generate_ticker(self, name: str, country: str) -> str:
        """Generate stock ticker symbol"""

        # Extract meaningful letters from company name
        words = name.replace(',', '').replace('.', '').split()

        # Take first letters or significant parts
        ticker_parts = []
        for word in words[:3]:  # Use first 3 words max
            if len(word) > 3:
                ticker_parts.append(word[:2].upper())
            else:
                ticker_parts.append(word[:1].upper())

        ticker = ''.join(ticker_parts)[:4]  # Max 4 characters

        # Add suffix based on country/exchange
        suffixes = {
            'Germany': '.DE',
            'United Kingdom': '.L',
            'France': '.PA',
            'Italy': '.MI',
            'Japan': '.T',
            'China': '.SS/.SZ',
            'South Korea': '.KS',
            'India': '.NS/.BO',
            'Australia': '.AX'
        }

        if country in suffixes:
            ticker += suffixes[country]

        return ticker

    def _generate_subsidiaries(self, parent_name: str, industry: str) -> List[str]:
        """Generate subsidiary companies"""

        num_subsidiaries = random.randint(0, 5)
        subsidiaries = []

        subsidiary_types = ['Technologies', 'Solutions', 'Services', 'International', 'Europe', 'Asia', 'Americas']

        for i in range(num_subsidiaries):
            # Use parent name with different suffix
            base_name = parent_name.split()[0]  # Take first word
            subsidiary_type = random.choice(subsidiary_types)
            subsidiary = f"{base_name} {subsidiary_type}"
            subsidiaries.append(subsidiary)

        return subsidiaries

    def _generate_locations(self, home_country: str, region: str, employees: int) -> List[str]:
        """Generate company locations worldwide"""

        locations = [self._generate_headquarters(home_country)]

        # Number of locations based on company size
        if employees < 1000:
            max_locations = 3
        elif employees < 10000:
            max_locations = 8
        elif employees < 50000:
            max_locations = 15
        else:
            max_locations = 25

        num_additional = random.randint(1, max_locations - 1)

        # Select countries from different regions
        all_countries = [country for region_countries in self.regions.values()
                        for country in region_countries if country != home_country]

        selected_countries = random.sample(all_countries, min(num_additional, len(all_countries)))

        for country in selected_countries:
            locations.append(self._generate_headquarters(country))

        return locations

    def _generate_certifications(self, industry: str, subsector: str) -> List[str]:
        """Generate industry-specific certifications"""

        base_certifications = ['ISO 9001:2015', 'ISO 14001:2015', 'ISO 45001:2018']

        industry_certifications = {
            'Automotive': ['IATF 16949:2016', 'VDA 6.3', 'AIAG Standards', 'FMVSS Compliance'],
            'Aerospace & Defense': ['AS9100D', 'NADCAP', 'FAA Certification', 'EASA Approval', 'DO-178C'],
            'Electronics': ['IPC Standards', 'UL Listed', 'CE Marking', 'FCC Approved', 'RoHS Compliant'],
            'Chemicals': ['REACH Compliance', 'GHS Standards', 'OSHA PSM', 'EPA Approved'],
            'Pharmaceuticals': ['FDA Approved', 'GMP Certified', 'ISO 13485', 'EMA Certified', 'WHO Prequalified'],
            'Oil & Gas': ['API Standards', 'ISO 29001', 'NORSOK Standards', 'ATEX Certified'],
            'Construction': ['OSHA Certified', 'LEED Certified', 'Building Code Compliance', 'Safety Certified'],
            'Semiconductors': ['SEMI Standards', 'JEDEC Standards', 'IPC-A-610', 'RBA Validated'],
            'Software': ['CMMI Level 5', 'ISO/IEC 27001', 'SOC 2 Compliant', 'GDPR Compliant'],
            'Robotics': ['CE Marking', 'UL 2089', 'ISO 10218', 'ANSI/RIA R15.06']
        }

        specific_certs = industry_certifications.get(industry, [])
        all_certs = base_certifications + specific_certs

        return random.sample(all_certs, k=random.randint(3, min(7, len(all_certs))))

    def save_data(self):
        """Save all generated data"""
        print(f"💾 Saving {len(self.companies)} companies...")

        # Save as JSON
        json_file = self.output_dir / "industrial_companies.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            companies_data = [asdict(company) for company in self.companies]
            json.dump(companies_data, f, indent=2, ensure_ascii=False)

        # Save as CSV
        csv_file = self.output_dir / "industrial_companies.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if self.companies:
                fieldnames = list(asdict(self.companies[0]).keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for company in self.companies:
                    row = asdict(company)
                    # Convert lists to strings for CSV
                    for key, value in row.items():
                        if isinstance(value, list):
                            row[key] = '; '.join(map(str, value))
                    writer.writerow(row)

        # Generate and save summary
        summary = self._generate_summary()
        summary_file = self.output_dir / "industrial_companies_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        # Generate analytics report
        analytics = self._generate_analytics()
        analytics_file = self.output_dir / "industrial_companies_analytics.json"
        with open(analytics_file, 'w', encoding='utf-8') as f:
            json.dump(analytics, f, indent=2, ensure_ascii=False)

        print(f"✅ Data saved to {self.output_dir}")
        print(f"  📄 JSON: {json_file.name}")
        print(f"  📊 CSV: {csv_file.name}")
        print(f"  📈 Summary: {summary_file.name}")
        print(f"  📉 Analytics: {analytics_file.name}")

        return {
            'json_file': str(json_file),
            'csv_file': str(csv_file),
            'summary_file': str(summary_file),
            'analytics_file': str(analytics_file)
        }

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate comprehensive summary statistics"""

        summary = {
            'dataset_info': {
                'total_companies': len(self.companies),
                'generation_date': datetime.now().isoformat(),
                'generator_version': '1.0.0'
            },
            'regional_distribution': {},
            'country_distribution': {},
            'sector_distribution': {},
            'industry_distribution': {},
            'revenue_analysis': {},
            'employee_analysis': {},
            'founding_year_analysis': {}
        }

        # Regional distribution
        for company in self.companies:
            region = company.region
            summary['regional_distribution'][region] = summary['regional_distribution'].get(region, 0) + 1

        # Country distribution
        for company in self.companies:
            country = company.country
            summary['country_distribution'][country] = summary['country_distribution'].get(country, 0) + 1

        # Sector distribution
        for company in self.companies:
            sector = company.sector
            summary['sector_distribution'][sector] = summary['sector_distribution'].get(sector, 0) + 1

        # Industry distribution
        for company in self.companies:
            industry = company.industry
            summary['industry_distribution'][industry] = summary['industry_distribution'].get(industry, 0) + 1

        # Revenue analysis
        revenues = [c.revenue_numeric for c in self.companies if c.revenue_numeric]
        if revenues:
            summary['revenue_analysis'] = {
                'total_revenue_billions': sum(revenues),
                'average_revenue_billions': sum(revenues) / len(revenues),
                'median_revenue_billions': sorted(revenues)[len(revenues)//2],
                'max_revenue_billions': max(revenues),
                'min_revenue_billions': min(revenues),
                'companies_over_10b': sum(1 for r in revenues if r > 10),
                'companies_over_100b': sum(1 for r in revenues if r > 100)
            }

        # Employee analysis
        employees = [c.employees for c in self.companies if c.employees]
        if employees:
            summary['employee_analysis'] = {
                'total_employees': sum(employees),
                'average_employees': sum(employees) / len(employees),
                'median_employees': sorted(employees)[len(employees)//2],
                'max_employees': max(employees),
                'min_employees': min(employees),
                'companies_over_10k': sum(1 for e in employees if e > 10000),
                'companies_over_100k': sum(1 for e in employees if e > 100000)
            }

        # Founding year analysis
        founding_years = [c.founded for c in self.companies if c.founded]
        if founding_years:
            summary['founding_year_analysis'] = {
                'oldest_company': min(founding_years),
                'newest_company': max(founding_years),
                'average_age': 2024 - (sum(founding_years) / len(founding_years)),
                'companies_founded_before_1950': sum(1 for y in founding_years if y < 1950),
                'companies_founded_after_2000': sum(1 for y in founding_years if y > 2000)
            }

        return summary

    def _generate_analytics(self) -> Dict[str, Any]:
        """Generate advanced analytics and insights"""

        analytics = {
            'market_insights': {},
            'innovation_metrics': {},
            'sustainability_metrics': {},
            'digital_transformation': {},
            'competitive_landscape': {},
            'growth_indicators': {}
        }

        # Innovation metrics
        innovation_scores = [c.innovation_index for c in self.companies if c.innovation_index]
        if innovation_scores:
            analytics['innovation_metrics'] = {
                'average_innovation_score': sum(innovation_scores) / len(innovation_scores),
                'innovation_leaders': sum(1 for s in innovation_scores if s > 0.8),
                'innovation_by_sector': {}
            }

            # Innovation by sector
            for company in self.companies:
                sector = company.sector
                if company.innovation_index:
                    if sector not in analytics['innovation_metrics']['innovation_by_sector']:
                        analytics['innovation_metrics']['innovation_by_sector'][sector] = []
                    analytics['innovation_metrics']['innovation_by_sector'][sector].append(company.innovation_index)

            # Calculate averages
            for sector, scores in analytics['innovation_metrics']['innovation_by_sector'].items():
                analytics['innovation_metrics']['innovation_by_sector'][sector] = {
                    'average_score': sum(scores) / len(scores),
                    'companies': len(scores)
                }

        # Sustainability metrics
        sustainability_scores = [c.sustainability_score for c in self.companies if c.sustainability_score]
        if sustainability_scores:
            analytics['sustainability_metrics'] = {
                'average_sustainability_score': sum(sustainability_scores) / len(sustainability_scores),
                'sustainability_leaders': sum(1 for s in sustainability_scores if s > 0.8),
                'sustainability_by_region': {}
            }

            # Sustainability by region
            for company in self.companies:
                region = company.region
                if company.sustainability_score:
                    if region not in analytics['sustainability_metrics']['sustainability_by_region']:
                        analytics['sustainability_metrics']['sustainability_by_region'][region] = []
                    analytics['sustainability_metrics']['sustainability_by_region'][region].append(company.sustainability_score)

            # Calculate averages
            for region, scores in analytics['sustainability_metrics']['sustainability_by_region'].items():
                analytics['sustainability_metrics']['sustainability_by_region'][region] = {
                    'average_score': sum(scores) / len(scores),
                    'companies': len(scores)
                }

        # Digital transformation metrics
        digital_scores = [c.digital_maturity for c in self.companies if c.digital_maturity]
        if digital_scores:
            analytics['digital_transformation'] = {
                'average_digital_maturity': sum(digital_scores) / len(digital_scores),
                'digital_leaders': sum(1 for s in digital_scores if s > 0.8),
                'digital_by_industry': {}
            }

        # Market concentration analysis
        revenue_by_industry = {}
        for company in self.companies:
            if company.revenue_numeric and company.industry:
                if company.industry not in revenue_by_industry:
                    revenue_by_industry[company.industry] = []
                revenue_by_industry[company.industry].append(company.revenue_numeric)

        analytics['competitive_landscape'] = {
            'industry_concentration': {},
            'largest_companies_by_revenue': []
        }

        # Top companies by revenue
        companies_by_revenue = sorted(self.companies, key=lambda x: x.revenue_numeric or 0, reverse=True)
        for i, company in enumerate(companies_by_revenue[:20]):
            analytics['competitive_landscape']['largest_companies_by_revenue'].append({
                'rank': i + 1,
                'name': company.name,
                'revenue_billions': company.revenue_numeric,
                'industry': company.industry,
                'country': company.country,
                'employees': company.employees
            })

        return analytics

    def print_summary(self):
        """Print a summary of generated data"""

        if not self.companies:
            print("No companies generated yet.")
            return

        print(f"\n🎉 Industrial Companies Dataset Generated!")
        print(f"📊 Total Companies: {len(self.companies)}")

        # Regional breakdown
        regions = {}
        for company in self.companies:
            regions[company.region] = regions.get(company.region, 0) + 1

        print(f"\n🌍 Regional Distribution:")
        for region, count in sorted(regions.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(self.companies)) * 100
            print(f"  {region}: {count} ({percentage:.1f}%)")

        # Industry breakdown
        industries = {}
        for company in self.companies:
            industries[company.industry] = industries.get(company.industry, 0) + 1

        print(f"\n🏭 Top Industries:")
        top_industries = sorted(industries.items(), key=lambda x: x[1], reverse=True)[:10]
        for industry, count in top_industries:
            print(f"  {industry}: {count} companies")

        # Revenue analysis
        revenues = [c.revenue_numeric for c in self.companies if c.revenue_numeric]
        if revenues:
            print(f"\n💰 Revenue Analysis:")
            print(f"  Total Revenue: ${sum(revenues):.1f}B")
            print(f"  Average Revenue: ${sum(revenues)/len(revenues):.1f}B")
            print(f"  Largest Company: ${max(revenues):.1f}B")
            print(f"  Companies >$10B: {sum(1 for r in revenues if r > 10)}")

if __name__ == "__main__":
    generator = IndustrialCompanyGenerator()

    # Generate companies
    generator.generate_all_industrial_companies(total_companies=500)

    # Print summary
    generator.print_summary()

    # Save data
    files = generator.save_data()

    print(f"\n✅ Generation complete! Files saved:")
    for file_type, file_path in files.items():
        print(f"  {file_type}: {file_path}")