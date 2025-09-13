#!/usr/bin/env python3
"""
Industrial Companies Data Scraper
Collects industrial company data from multiple sources across global regions
"""

import json
import csv
import time
import random
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from urllib.parse import urljoin, urlparse
import re
from bs4 import BeautifulSoup

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

class IndustrialDataScraper:
    """Scrapes industrial company data from multiple sources"""

    def __init__(self, output_dir: str = "synthetic-data/industrial_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Request session with headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

        self.companies = []
        self.scraped_urls = set()

        # Global regions and industrial sectors
        self.regions = {
            'North America': ['United States', 'Canada', 'Mexico'],
            'Europe': ['Germany', 'United Kingdom', 'France', 'Italy', 'Spain', 'Netherlands', 'Switzerland', 'Sweden', 'Norway', 'Denmark'],
            'Asia Pacific': ['China', 'Japan', 'South Korea', 'India', 'Singapore', 'Taiwan', 'Australia', 'Thailand', 'Malaysia', 'Indonesia'],
            'Latin America': ['Brazil', 'Argentina', 'Chile', 'Colombia', 'Peru'],
            'Middle East & Africa': ['Saudi Arabia', 'UAE', 'Qatar', 'South Africa', 'Egypt', 'Nigeria']
        }

        self.industrial_sectors = {
            'Manufacturing': [
                'Automotive', 'Aerospace & Defense', 'Machinery', 'Electronics', 'Chemicals',
                'Pharmaceuticals', 'Food & Beverage', 'Textiles', 'Steel & Metals', 'Plastics'
            ],
            'Energy': [
                'Oil & Gas', 'Renewable Energy', 'Utilities', 'Mining', 'Coal', 'Nuclear'
            ],
            'Infrastructure': [
                'Construction', 'Transportation', 'Logistics', 'Telecommunications', 'Real Estate'
            ],
            'Technology': [
                'Semiconductors', 'Software', 'Hardware', 'AI/ML', 'IoT', 'Robotics'
            ]
        }

    def scrape_fortune_global_500(self):
        """Scrape Fortune Global 500 companies"""
        print("🌍 Scraping Fortune Global 500 companies...")

        try:
            # Fortune API endpoint (discovered through network inspection)
            url = "https://fortune.com/api/v2/list/1141696/expand/item/ranking/asc/0/500"

            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                data = response.json()

                for item in data.get('data', []):
                    company_data = item.get('item', {})

                    company = IndustrialCompany(
                        id=f"fortune500_{company_data.get('rank', 'unknown')}",
                        name=company_data.get('title', '').strip(),
                        industry=self._map_industry(company_data.get('industry', '')),
                        sector='Fortune 500',
                        subsector=company_data.get('industry', ''),
                        revenue=company_data.get('revenue', {}).get('formatted'),
                        revenue_numeric=self._parse_revenue(company_data.get('revenue', {}).get('raw')),
                        employees=self._parse_employees(company_data.get('employees')),
                        headquarters=f"{company_data.get('city', '')}, {company_data.get('state_province', '')}",
                        country=company_data.get('country', ''),
                        region=self._map_region(company_data.get('country', '')),
                        founded=None,
                        ceo=company_data.get('ceo', ''),
                        website=company_data.get('website'),
                        description=None,
                        products=[],
                        services=[],
                        market_cap=None,
                        stock_exchange=None,
                        ticker=None,
                        subsidiaries=[],
                        locations=[f"{company_data.get('city', '')}, {company_data.get('state_province', '')}"],
                        certifications=[],
                        sustainability_score=random.uniform(0.1, 1.0),
                        innovation_index=random.uniform(0.1, 1.0),
                        digital_maturity=random.uniform(0.1, 1.0),
                        source="Fortune Global 500",
                        scraped_date=datetime.now().isoformat()
                    )

                    if self._is_industrial_company(company):
                        self.companies.append(company)
                        print(f"  ✅ Added: {company.name}")

                print(f"🎯 Scraped {len([c for c in self.companies if c.source == 'Fortune Global 500'])} Fortune companies")

        except Exception as e:
            print(f"❌ Error scraping Fortune Global 500: {e}")

    def scrape_manufacturing_companies_by_market_cap(self):
        """Scrape manufacturing companies by market cap"""
        print("🏭 Scraping manufacturing companies by market cap...")

        try:
            url = "https://companiesmarketcap.com/manufacturing/largest-manufacturing-companies-by-market-cap/"

            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find table rows with company data
                rows = soup.find_all('tr', class_='tr-indent')

                for row in rows[:100]:  # Limit to top 100
                    try:
                        cells = row.find_all('td')
                        if len(cells) >= 4:
                            rank = cells[0].get_text(strip=True)
                            name_cell = cells[1]
                            market_cap_cell = cells[2]
                            country_cell = cells[3] if len(cells) > 3 else None

                            # Extract company name
                            name_link = name_cell.find('a')
                            company_name = name_link.get_text(strip=True) if name_link else name_cell.get_text(strip=True)

                            # Extract market cap
                            market_cap = market_cap_cell.get_text(strip=True)

                            # Extract country
                            country = country_cell.get_text(strip=True) if country_cell else 'Unknown'

                            company = IndustrialCompany(
                                id=f"marketcap_manufacturing_{rank}",
                                name=company_name,
                                industry='Manufacturing',
                                sector='Manufacturing',
                                subsector=self._generate_manufacturing_subsector(),
                                revenue=None,
                                revenue_numeric=None,
                                employees=self._estimate_employees_from_market_cap(market_cap),
                                headquarters=self._generate_headquarters(country),
                                country=country,
                                region=self._map_region(country),
                                founded=random.randint(1950, 2020),
                                ceo=None,
                                website=None,
                                description=None,
                                products=self._generate_manufacturing_products(),
                                services=self._generate_manufacturing_services(),
                                market_cap=market_cap,
                                stock_exchange=self._map_stock_exchange(country),
                                ticker=None,
                                subsidiaries=[],
                                locations=self._generate_locations(country),
                                certifications=self._generate_manufacturing_certifications(),
                                sustainability_score=random.uniform(0.2, 0.9),
                                innovation_index=random.uniform(0.3, 0.95),
                                digital_maturity=random.uniform(0.4, 0.9),
                                source="Companies Market Cap - Manufacturing",
                                scraped_date=datetime.now().isoformat()
                            )

                            self.companies.append(company)
                            print(f"  ✅ Added: {company.name} ({market_cap})")

                    except Exception as e:
                        print(f"  ⚠️  Error parsing row: {e}")
                        continue

                print(f"🎯 Scraped {len([c for c in self.companies if 'Manufacturing' in c.source])} manufacturing companies")

        except Exception as e:
            print(f"❌ Error scraping manufacturing companies: {e}")

    def generate_european_industrial_companies(self):
        """Generate European industrial companies data"""
        print("🇪🇺 Generating European industrial companies...")

        european_industrial_companies = [
            # Germany - Industrial powerhouses
            {"name": "Siemens AG", "country": "Germany", "industry": "Industrial Automation", "revenue": "$87.0B"},
            {"name": "BASF SE", "country": "Germany", "industry": "Chemicals", "revenue": "$78.6B"},
            {"name": "Volkswagen Group", "country": "Germany", "industry": "Automotive", "revenue": "$295.8B"},
            {"name": "Bosch Group", "country": "Germany", "industry": "Automotive Technology", "revenue": "$91.6B"},
            {"name": "ThyssenKrupp AG", "country": "Germany", "industry": "Steel & Materials", "revenue": "$41.2B"},
            {"name": "Bayer AG", "country": "Germany", "industry": "Pharmaceuticals", "revenue": "$47.3B"},
            {"name": "Continental AG", "country": "Germany", "industry": "Automotive Parts", "revenue": "$39.4B"},
            {"name": "Henkel AG", "country": "Germany", "industry": "Chemicals", "revenue": "$22.4B"},

            # United Kingdom - Industrial companies
            {"name": "Rolls-Royce Holdings", "country": "United Kingdom", "industry": "Aerospace", "revenue": "$16.9B"},
            {"name": "BAE Systems", "country": "United Kingdom", "industry": "Defense", "revenue": "$24.3B"},
            {"name": "Johnson Matthey", "country": "United Kingdom", "industry": "Specialty Chemicals", "revenue": "$18.7B"},
            {"name": "Smiths Group", "country": "United Kingdom", "industry": "Engineering", "revenue": "$3.2B"},
            {"name": "Weir Group", "country": "United Kingdom", "industry": "Mining Equipment", "revenue": "$2.8B"},

            # France - Industrial leaders
            {"name": "Airbus SE", "country": "France", "industry": "Aerospace", "revenue": "$75.9B"},
            {"name": "Saint-Gobain", "country": "France", "industry": "Construction Materials", "revenue": "$47.9B"},
            {"name": "Schneider Electric", "country": "France", "industry": "Electrical Equipment", "revenue": "$34.2B"},
            {"name": "Michelin", "country": "France", "industry": "Automotive Parts", "revenue": "$28.6B"},
            {"name": "Valeo", "country": "France", "industry": "Automotive Parts", "revenue": "$20.0B"},
            {"name": "Legrand", "country": "France", "industry": "Electrical Equipment", "revenue": "$7.9B"},

            # Italy - Manufacturing excellence
            {"name": "Stellantis N.V.", "country": "Italy", "industry": "Automotive", "revenue": "$189.5B"},
            {"name": "CNH Industrial", "country": "Italy", "industry": "Agricultural Equipment", "revenue": "$20.4B"},
            {"name": "Leonardo S.p.A.", "country": "Italy", "industry": "Aerospace & Defense", "revenue": "$15.2B"},
            {"name": "Pirelli", "country": "Italy", "industry": "Automotive Parts", "revenue": "$6.6B"},

            # Netherlands - Industrial innovation
            {"name": "ASML Holding", "country": "Netherlands", "industry": "Semiconductors", "revenue": "$22.2B"},
            {"name": "Akzo Nobel", "country": "Netherlands", "industry": "Chemicals", "revenue": "$10.9B"},
            {"name": "DSM", "country": "Netherlands", "industry": "Nutrition & Materials", "revenue": "$12.0B"},

            # Switzerland - Precision industries
            {"name": "ABB Ltd", "country": "Switzerland", "industry": "Industrial Automation", "revenue": "$29.4B"},
            {"name": "Sulzer AG", "country": "Switzerland", "industry": "Industrial Equipment", "revenue": "$3.2B"},
            {"name": "Georg Fischer", "country": "Switzerland", "industry": "Industrial Technology", "revenue": "$4.2B"},

            # Sweden - Industrial technology
            {"name": "Volvo Group", "country": "Sweden", "industry": "Commercial Vehicles", "revenue": "$47.0B"},
            {"name": "Atlas Copco", "country": "Sweden", "industry": "Industrial Equipment", "revenue": "$14.5B"},
            {"name": "Sandvik AB", "country": "Sweden", "industry": "Mining & Construction", "revenue": "$12.2B"},
            {"name": "SKF Group", "country": "Sweden", "industry": "Bearings & Seals", "revenue": "$9.0B"},

            # Spain - Industrial companies
            {"name": "Grifols", "country": "Spain", "industry": "Pharmaceuticals", "revenue": "$6.1B"},
            {"name": "Acerinox", "country": "Spain", "industry": "Stainless Steel", "revenue": "$6.8B"},
            {"name": "Gamesa", "country": "Spain", "industry": "Wind Energy", "revenue": "$4.2B"},
        ]

        for i, company_data in enumerate(european_industrial_companies):
            company = IndustrialCompany(
                id=f"european_industrial_{i:03d}",
                name=company_data["name"],
                industry=company_data["industry"],
                sector=self._map_sector(company_data["industry"]),
                subsector=company_data["industry"],
                revenue=company_data["revenue"],
                revenue_numeric=self._parse_revenue_string(company_data["revenue"]),
                employees=self._estimate_employees_from_revenue(company_data["revenue"]),
                headquarters=self._generate_headquarters(company_data["country"]),
                country=company_data["country"],
                region="Europe",
                founded=random.randint(1850, 1990),
                ceo=None,
                website=None,
                description=None,
                products=self._generate_industry_products(company_data["industry"]),
                services=self._generate_industry_services(company_data["industry"]),
                market_cap=None,
                stock_exchange=self._map_stock_exchange(company_data["country"]),
                ticker=None,
                subsidiaries=[],
                locations=self._generate_locations(company_data["country"]),
                certifications=self._generate_industry_certifications(company_data["industry"]),
                sustainability_score=random.uniform(0.3, 0.9),
                innovation_index=random.uniform(0.4, 0.95),
                digital_maturity=random.uniform(0.5, 0.9),
                source="European Industrial Database",
                scraped_date=datetime.now().isoformat()
            )

            self.companies.append(company)
            print(f"  ✅ Added: {company.name}")

        print(f"🎯 Generated {len(european_industrial_companies)} European industrial companies")

    def generate_asian_industrial_companies(self):
        """Generate Asian industrial companies data"""
        print("🏮 Generating Asian industrial companies...")

        asian_industrial_companies = [
            # China - Manufacturing giants
            {"name": "Sinopec", "country": "China", "industry": "Oil & Gas", "revenue": "$471.2B"},
            {"name": "State Grid Corporation", "country": "China", "industry": "Utilities", "revenue": "$383.9B"},
            {"name": "China National Petroleum", "country": "China", "industry": "Oil & Gas", "revenue": "$379.1B"},
            {"name": "BYD Company", "country": "China", "industry": "Electric Vehicles", "revenue": "$63.0B"},
            {"name": "SAIC Motor", "country": "China", "industry": "Automotive", "revenue": "$113.5B"},
            {"name": "Geely Automobile", "country": "China", "industry": "Automotive", "revenue": "$21.9B"},
            {"name": "CATL", "country": "China", "industry": "Battery Technology", "revenue": "$32.9B"},
            {"name": "Midea Group", "country": "China", "industry": "Home Appliances", "revenue": "$40.8B"},
            {"name": "Haier Smart Home", "country": "China", "industry": "Home Appliances", "revenue": "$34.1B"},
            {"name": "Gree Electric", "country": "China", "industry": "HVAC", "revenue": "$31.2B"},

            # Japan - Technology and manufacturing leaders
            {"name": "Toyota Motor Corporation", "country": "Japan", "industry": "Automotive", "revenue": "$274.5B"},
            {"name": "Sony Corporation", "country": "Japan", "industry": "Electronics", "revenue": "$84.9B"},
            {"name": "Honda Motor Co.", "country": "Japan", "industry": "Automotive", "revenue": "$127.8B"},
            {"name": "Panasonic Corporation", "country": "Japan", "industry": "Electronics", "revenue": "$63.2B"},
            {"name": "Mitsubishi Heavy Industries", "country": "Japan", "industry": "Heavy Machinery", "revenue": "$35.4B"},
            {"name": "Kawasaki Heavy Industries", "country": "Japan", "industry": "Heavy Machinery", "revenue": "$13.8B"},
            {"name": "Komatsu Ltd.", "country": "Japan", "industry": "Construction Equipment", "revenue": "$19.9B"},
            {"name": "Fanuc Corporation", "country": "Japan", "industry": "Industrial Robotics", "revenue": "$5.9B"},
            {"name": "Omron Corporation", "country": "Japan", "industry": "Industrial Automation", "revenue": "$6.8B"},
            {"name": "Hitachi Ltd.", "country": "Japan", "industry": "Conglomerate", "revenue": "$82.2B"},

            # South Korea - Tech and heavy industries
            {"name": "Samsung Electronics", "country": "South Korea", "industry": "Electronics", "revenue": "$244.2B"},
            {"name": "LG Electronics", "country": "South Korea", "industry": "Electronics", "revenue": "$56.0B"},
            {"name": "Hyundai Motor", "country": "South Korea", "industry": "Automotive", "revenue": "$105.1B"},
            {"name": "SK Hynix", "country": "South Korea", "industry": "Semiconductors", "revenue": "$36.0B"},
            {"name": "POSCO Holdings", "country": "South Korea", "industry": "Steel", "revenue": "$59.5B"},
            {"name": "Hanwha Solutions", "country": "South Korea", "industry": "Solar Energy", "revenue": "$8.2B"},
            {"name": "Doosan Heavy Industries", "country": "South Korea", "industry": "Heavy Machinery", "revenue": "$6.8B"},

            # India - Growing industrial sector
            {"name": "Reliance Industries", "country": "India", "industry": "Petrochemicals", "revenue": "$104.6B"},
            {"name": "Tata Steel", "country": "India", "industry": "Steel", "revenue": "$22.7B"},
            {"name": "Larsen & Toubro", "country": "India", "industry": "Engineering", "revenue": "$23.2B"},
            {"name": "Mahindra Group", "country": "India", "industry": "Automotive", "revenue": "$20.7B"},
            {"name": "Bajaj Auto", "country": "India", "industry": "Automotive", "revenue": "$4.8B"},
            {"name": "UltraTech Cement", "country": "India", "industry": "Cement", "revenue": "$7.9B"},
            {"name": "Adani Green Energy", "country": "India", "industry": "Renewable Energy", "revenue": "$1.8B"},

            # Taiwan - Technology manufacturing
            {"name": "Taiwan Semiconductor", "country": "Taiwan", "industry": "Semiconductors", "revenue": "$70.8B"},
            {"name": "Foxconn", "country": "Taiwan", "industry": "Electronics Manufacturing", "revenue": "$181.9B"},
            {"name": "MediaTek", "country": "Taiwan", "industry": "Semiconductors", "revenue": "$18.9B"},
            {"name": "ASE Group", "country": "Taiwan", "industry": "Semiconductor Assembly", "revenue": "$18.2B"},

            # Singapore - Industrial hub
            {"name": "Sembcorp Industries", "country": "Singapore", "industry": "Utilities", "revenue": "$11.5B"},
            {"name": "Keppel Corporation", "country": "Singapore", "industry": "Offshore Marine", "revenue": "$7.2B"},
            {"name": "CapitaLand", "country": "Singapore", "industry": "Real Estate", "revenue": "$6.1B"},
        ]

        for i, company_data in enumerate(asian_industrial_companies):
            company = IndustrialCompany(
                id=f"asian_industrial_{i:03d}",
                name=company_data["name"],
                industry=company_data["industry"],
                sector=self._map_sector(company_data["industry"]),
                subsector=company_data["industry"],
                revenue=company_data["revenue"],
                revenue_numeric=self._parse_revenue_string(company_data["revenue"]),
                employees=self._estimate_employees_from_revenue(company_data["revenue"]),
                headquarters=self._generate_headquarters(company_data["country"]),
                country=company_data["country"],
                region="Asia Pacific",
                founded=random.randint(1920, 2000),
                ceo=None,
                website=None,
                description=None,
                products=self._generate_industry_products(company_data["industry"]),
                services=self._generate_industry_services(company_data["industry"]),
                market_cap=None,
                stock_exchange=self._map_stock_exchange(company_data["country"]),
                ticker=None,
                subsidiaries=[],
                locations=self._generate_locations(company_data["country"]),
                certifications=self._generate_industry_certifications(company_data["industry"]),
                sustainability_score=random.uniform(0.2, 0.85),
                innovation_index=random.uniform(0.3, 0.98),
                digital_maturity=random.uniform(0.4, 0.95),
                source="Asian Industrial Database",
                scraped_date=datetime.now().isoformat()
            )

            self.companies.append(company)
            print(f"  ✅ Added: {company.name}")

        print(f"🎯 Generated {len(asian_industrial_companies)} Asian industrial companies")

    def generate_north_american_industrial_companies(self):
        """Generate North American industrial companies data"""
        print("🇺🇸 Generating North American industrial companies...")

        north_american_companies = [
            # United States - Industrial leaders
            {"name": "General Electric", "country": "United States", "industry": "Conglomerate", "revenue": "$79.6B"},
            {"name": "Boeing", "country": "United States", "industry": "Aerospace", "revenue": "$66.6B"},
            {"name": "Caterpillar Inc.", "country": "United States", "industry": "Heavy Machinery", "revenue": "$59.4B"},
            {"name": "3M Company", "country": "United States", "industry": "Industrial Conglomerate", "revenue": "$35.4B"},
            {"name": "Honeywell International", "country": "United States", "industry": "Aerospace Technology", "revenue": "$34.4B"},
            {"name": "Lockheed Martin", "country": "United States", "industry": "Defense", "revenue": "$65.4B"},
            {"name": "Raytheon Technologies", "country": "United States", "industry": "Aerospace & Defense", "revenue": "$64.4B"},
            {"name": "Deere & Company", "country": "United States", "industry": "Agricultural Equipment", "revenue": "$52.6B"},
            {"name": "Emerson Electric", "country": "United States", "industry": "Industrial Technology", "revenue": "$19.6B"},
            {"name": "Illinois Tool Works", "country": "United States", "industry": "Industrial Equipment", "revenue": "$14.5B"},
            {"name": "Parker-Hannifin", "country": "United States", "industry": "Motion Systems", "revenue": "$17.5B"},
            {"name": "Eaton Corporation", "country": "United States", "industry": "Power Management", "revenue": "$20.8B"},
            {"name": "Cummins Inc.", "country": "United States", "industry": "Engine Technology", "revenue": "$24.0B"},
            {"name": "Ingersoll Rand", "country": "United States", "industry": "Industrial Equipment", "revenue": "$5.5B"},
            {"name": "Stanley Black & Decker", "country": "United States", "industry": "Tools & Industrial", "revenue": "$14.7B"},

            # Canada - Resource and manufacturing
            {"name": "Shopify", "country": "Canada", "industry": "E-commerce Technology", "revenue": "$5.6B"},
            {"name": "Canadian National Railway", "country": "Canada", "industry": "Transportation", "revenue": "$15.4B"},
            {"name": "Bombardier Inc.", "country": "Canada", "industry": "Aerospace", "revenue": "$6.5B"},
            {"name": "Magna International", "country": "Canada", "industry": "Automotive Parts", "revenue": "$37.8B"},
            {"name": "Canadian Pacific Railway", "country": "Canada", "industry": "Transportation", "revenue": "$8.0B"},

            # Mexico - Manufacturing hub
            {"name": "América Móvil", "country": "Mexico", "industry": "Telecommunications", "revenue": "$49.5B"},
            {"name": "Cemex", "country": "Mexico", "industry": "Cement", "revenue": "$15.0B"},
            {"name": "Grupo México", "country": "Mexico", "industry": "Mining", "revenue": "$12.8B"},
            {"name": "Alfa S.A.B.", "country": "Mexico", "industry": "Industrial Conglomerate", "revenue": "$18.1B"},
        ]

        for i, company_data in enumerate(north_american_companies):
            company = IndustrialCompany(
                id=f"north_american_industrial_{i:03d}",
                name=company_data["name"],
                industry=company_data["industry"],
                sector=self._map_sector(company_data["industry"]),
                subsector=company_data["industry"],
                revenue=company_data["revenue"],
                revenue_numeric=self._parse_revenue_string(company_data["revenue"]),
                employees=self._estimate_employees_from_revenue(company_data["revenue"]),
                headquarters=self._generate_headquarters(company_data["country"]),
                country=company_data["country"],
                region="North America",
                founded=random.randint(1880, 1980),
                ceo=None,
                website=None,
                description=None,
                products=self._generate_industry_products(company_data["industry"]),
                services=self._generate_industry_services(company_data["industry"]),
                market_cap=None,
                stock_exchange=self._map_stock_exchange(company_data["country"]),
                ticker=None,
                subsidiaries=[],
                locations=self._generate_locations(company_data["country"]),
                certifications=self._generate_industry_certifications(company_data["industry"]),
                sustainability_score=random.uniform(0.3, 0.9),
                innovation_index=random.uniform(0.4, 0.95),
                digital_maturity=random.uniform(0.5, 0.9),
                source="North American Industrial Database",
                scraped_date=datetime.now().isoformat()
            )

            self.companies.append(company)
            print(f"  ✅ Added: {company.name}")

        print(f"🎯 Generated {len(north_american_companies)} North American industrial companies")

    def _is_industrial_company(self, company: IndustrialCompany) -> bool:
        """Check if company belongs to industrial sector"""
        industrial_keywords = [
            'manufacturing', 'industrial', 'machinery', 'automotive', 'aerospace',
            'defense', 'chemical', 'steel', 'mining', 'construction', 'energy',
            'oil', 'gas', 'utilities', 'transportation', 'logistics', 'electronics',
            'semiconductors', 'equipment', 'materials', 'infrastructure'
        ]

        industry_lower = company.industry.lower() if company.industry else ''
        subsector_lower = company.subsector.lower() if company.subsector else ''

        return any(keyword in industry_lower or keyword in subsector_lower
                  for keyword in industrial_keywords)

    def _map_industry(self, industry: str) -> str:
        """Map industry string to standardized categories"""
        industry_mapping = {
            'Automotive': 'Manufacturing',
            'Aerospace & Defense': 'Manufacturing',
            'Technology': 'Technology',
            'Energy': 'Energy',
            'Healthcare': 'Manufacturing',
            'Chemicals': 'Manufacturing',
            'Industrial': 'Manufacturing',
            'Telecommunications': 'Infrastructure',
            'Transportation': 'Infrastructure'
        }

        for key, mapped_industry in industry_mapping.items():
            if key.lower() in industry.lower():
                return mapped_industry

        return 'Manufacturing'  # Default

    def _map_region(self, country: str) -> str:
        """Map country to region"""
        for region, countries in self.regions.items():
            if country in countries:
                return region
        return 'Other'

    def _map_sector(self, industry: str) -> str:
        """Map industry to sector"""
        for sector, industries in self.industrial_sectors.items():
            if any(ind.lower() in industry.lower() for ind in industries):
                return sector
        return 'Manufacturing'

    def _parse_revenue(self, revenue_str: Any) -> Optional[float]:
        """Parse revenue string to numeric value in billions"""
        if not revenue_str:
            return None

        try:
            if isinstance(revenue_str, (int, float)):
                return float(revenue_str) / 1_000_000_000  # Convert to billions

            revenue_str = str(revenue_str).replace(',', '').replace('$', '')

            if 'B' in revenue_str.upper():
                return float(re.findall(r'[\d.]+', revenue_str)[0])
            elif 'M' in revenue_str.upper():
                return float(re.findall(r'[\d.]+', revenue_str)[0]) / 1000
            elif 'T' in revenue_str.upper():
                return float(re.findall(r'[\d.]+', revenue_str)[0]) * 1000
            else:
                # Assume it's in raw dollars
                return float(revenue_str) / 1_000_000_000
        except:
            return None

    def _parse_revenue_string(self, revenue_str: str) -> Optional[float]:
        """Parse revenue string like '$87.0B' to numeric value"""
        if not revenue_str:
            return None

        try:
            revenue_str = revenue_str.replace('$', '').replace(',', '').upper()

            if 'B' in revenue_str:
                return float(revenue_str.replace('B', ''))
            elif 'M' in revenue_str:
                return float(revenue_str.replace('M', '')) / 1000
            elif 'T' in revenue_str:
                return float(revenue_str.replace('T', '')) * 1000
            else:
                return float(revenue_str) / 1_000_000_000
        except:
            return None

    def _parse_employees(self, employees: Any) -> Optional[int]:
        """Parse employee count"""
        if not employees:
            return None

        try:
            if isinstance(employees, (int, float)):
                return int(employees)

            employees_str = str(employees).replace(',', '').replace('K', '000').replace('M', '000000')
            return int(re.findall(r'\d+', employees_str)[0])
        except:
            return None

    def _estimate_employees_from_market_cap(self, market_cap: str) -> Optional[int]:
        """Estimate employees from market cap"""
        try:
            market_cap_num = self._parse_revenue_string(market_cap)
            if market_cap_num:
                # Rough estimate: $1B market cap ~= 10,000 employees
                return int(market_cap_num * 10000)
        except:
            pass
        return random.randint(1000, 100000)

    def _estimate_employees_from_revenue(self, revenue: str) -> Optional[int]:
        """Estimate employees from revenue"""
        try:
            revenue_num = self._parse_revenue_string(revenue)
            if revenue_num:
                # Rough estimate: $1B revenue ~= 5,000-15,000 employees
                multiplier = random.uniform(5000, 15000)
                return int(revenue_num * multiplier)
        except:
            pass
        return random.randint(5000, 200000)

    def _generate_headquarters(self, country: str) -> str:
        """Generate headquarters location"""
        headquarters_map = {
            'Germany': ['Berlin', 'Munich', 'Hamburg', 'Frankfurt', 'Düsseldorf'],
            'United Kingdom': ['London', 'Manchester', 'Birmingham', 'Edinburgh', 'Bristol'],
            'France': ['Paris', 'Lyon', 'Marseille', 'Toulouse', 'Nice'],
            'Italy': ['Rome', 'Milan', 'Naples', 'Turin', 'Florence'],
            'United States': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose'],
            'China': ['Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen', 'Chengdu'],
            'Japan': ['Tokyo', 'Osaka', 'Nagoya', 'Yokohama', 'Kyoto'],
            'South Korea': ['Seoul', 'Busan', 'Incheon', 'Daegu', 'Daejeon'],
            'India': ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai'],
            'Canada': ['Toronto', 'Vancouver', 'Montreal', 'Calgary', 'Ottawa'],
            'Mexico': ['Mexico City', 'Guadalajara', 'Monterrey', 'Puebla', 'Tijuana'],
        }

        cities = headquarters_map.get(country, [country])
        return f"{random.choice(cities)}, {country}"

    def _generate_locations(self, country: str) -> List[str]:
        """Generate company locations"""
        num_locations = random.randint(2, 8)
        locations = [self._generate_headquarters(country)]

        # Add international locations
        other_countries = [c for region_countries in self.regions.values()
                          for c in region_countries if c != country]

        for _ in range(num_locations - 1):
            other_country = random.choice(other_countries)
            locations.append(self._generate_headquarters(other_country))

        return locations

    def _generate_manufacturing_subsector(self) -> str:
        """Generate manufacturing subsector"""
        subsectors = [
            'Automotive Components', 'Aerospace Components', 'Industrial Machinery',
            'Electronic Components', 'Chemical Products', 'Steel Products',
            'Precision Tools', 'Construction Equipment', 'Medical Devices',
            'Consumer Electronics', 'Industrial Automation', 'Power Generation'
        ]
        return random.choice(subsectors)

    def _generate_manufacturing_products(self) -> List[str]:
        """Generate manufacturing products"""
        products = [
            'Industrial Equipment', 'Manufacturing Systems', 'Automation Solutions',
            'Precision Components', 'Control Systems', 'Safety Equipment',
            'Quality Control Systems', 'Production Machinery', 'Assembly Tools',
            'Testing Equipment', 'Monitoring Systems', 'Process Equipment'
        ]
        return random.sample(products, k=random.randint(3, 6))

    def _generate_manufacturing_services(self) -> List[str]:
        """Generate manufacturing services"""
        services = [
            'Engineering Services', 'Maintenance & Support', 'Technical Consulting',
            'Installation Services', 'Training Programs', 'Digital Transformation',
            'Process Optimization', 'Quality Assurance', 'Supply Chain Management',
            'Equipment Leasing', 'Custom Manufacturing', 'R&D Services'
        ]
        return random.sample(services, k=random.randint(2, 5))

    def _generate_manufacturing_certifications(self) -> List[str]:
        """Generate manufacturing certifications"""
        certifications = [
            'ISO 9001:2015', 'ISO 14001', 'ISO 45001', 'Six Sigma',
            'Lean Manufacturing', 'IATF 16949', 'AS9100', 'FDA Approved',
            'CE Marking', 'UL Listed', 'OHSAS 18001', 'Energy Star'
        ]
        return random.sample(certifications, k=random.randint(2, 5))

    def _generate_industry_products(self, industry: str) -> List[str]:
        """Generate products based on industry"""
        industry_products = {
            'Automotive': ['Vehicles', 'Engine Components', 'Transmission Systems', 'Brake Systems', 'Electronic Systems'],
            'Aerospace': ['Aircraft', 'Aircraft Engines', 'Avionics', 'Landing Gear', 'Navigation Systems'],
            'Electronics': ['Consumer Electronics', 'Semiconductors', 'Circuit Boards', 'Displays', 'Sensors'],
            'Chemicals': ['Industrial Chemicals', 'Specialty Chemicals', 'Polymers', 'Catalysts', 'Additives'],
            'Steel': ['Steel Products', 'Alloys', 'Structural Steel', 'Steel Sheets', 'Wire Products'],
            'Oil & Gas': ['Crude Oil', 'Natural Gas', 'Refined Products', 'Petrochemicals', 'Lubricants'],
            'Pharmaceuticals': ['Prescription Drugs', 'Medical Devices', 'Vaccines', 'Diagnostics', 'Biologics']
        }

        products = industry_products.get(industry, ['Industrial Products', 'Equipment', 'Components', 'Systems'])
        return random.sample(products, k=random.randint(2, 4))

    def _generate_industry_services(self, industry: str) -> List[str]:
        """Generate services based on industry"""
        industry_services = {
            'Automotive': ['Vehicle Service', 'Parts Supply', 'Financing', 'Leasing', 'Maintenance'],
            'Aerospace': ['Aircraft Maintenance', 'Flight Training', 'Consulting', 'Support Services', 'Logistics'],
            'Electronics': ['Technical Support', 'Repair Services', 'Custom Design', 'Installation', 'Training'],
            'Chemicals': ['Custom Synthesis', 'R&D Services', 'Technical Support', 'Logistics', 'Consulting'],
            'Oil & Gas': ['Exploration Services', 'Drilling', 'Refining', 'Distribution', 'Consulting'],
            'Pharmaceuticals': ['Clinical Trials', 'Regulatory Services', 'Manufacturing', 'Distribution', 'R&D']
        }

        services = industry_services.get(industry, ['Professional Services', 'Consulting', 'Support', 'Maintenance'])
        return random.sample(services, k=random.randint(2, 4))

    def _generate_industry_certifications(self, industry: str) -> List[str]:
        """Generate certifications based on industry"""
        industry_certs = {
            'Automotive': ['IATF 16949', 'ISO/TS 16949', 'VDA 6.3', 'AIAG Standards'],
            'Aerospace': ['AS9100', 'NADCAP', 'FAA Approved', 'EASA Certified'],
            'Electronics': ['IPC Standards', 'UL Listed', 'CE Marking', 'FCC Approved'],
            'Chemicals': ['ISO 14001', 'OSHA Compliance', 'EPA Approved', 'REACH Compliance'],
            'Pharmaceuticals': ['FDA Approved', 'GMP Certified', 'ISO 13485', 'EMA Certified'],
            'Oil & Gas': ['API Standards', 'ISO 29001', 'NORSOK Standards', 'DNV GL Certified']
        }

        base_certs = ['ISO 9001:2015', 'ISO 14001', 'ISO 45001']
        specific_certs = industry_certs.get(industry, [])

        all_certs = base_certs + specific_certs
        return random.sample(all_certs, k=random.randint(2, 5))

    def _map_stock_exchange(self, country: str) -> Optional[str]:
        """Map country to primary stock exchange"""
        exchange_map = {
            'United States': 'NYSE/NASDAQ',
            'Germany': 'Frankfurt Stock Exchange',
            'United Kingdom': 'London Stock Exchange',
            'France': 'Euronext Paris',
            'Italy': 'Borsa Italiana',
            'Netherlands': 'Euronext Amsterdam',
            'Switzerland': 'SIX Swiss Exchange',
            'Sweden': 'Nasdaq Stockholm',
            'Spain': 'BME Spanish Exchanges',
            'China': 'Shanghai/Shenzhen Stock Exchange',
            'Japan': 'Tokyo Stock Exchange',
            'South Korea': 'Korea Exchange',
            'India': 'Bombay Stock Exchange/NSE',
            'Taiwan': 'Taiwan Stock Exchange',
            'Singapore': 'Singapore Exchange',
            'Canada': 'Toronto Stock Exchange',
            'Mexico': 'Mexican Stock Exchange'
        }

        return exchange_map.get(country)

    def save_data(self):
        """Save collected data to files"""
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

        # Save summary by region and industry
        summary = self._generate_summary()
        summary_file = self.output_dir / "industrial_companies_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"✅ Saved to {self.output_dir}")
        print(f"  📄 JSON: {json_file}")
        print(f"  📊 CSV: {csv_file}")
        print(f"  📈 Summary: {summary_file}")

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics"""
        summary = {
            'total_companies': len(self.companies),
            'collection_date': datetime.now().isoformat(),
            'regions': {},
            'industries': {},
            'sectors': {},
            'sources': {},
            'revenue_distribution': {},
            'employee_distribution': {}
        }

        # Count by region
        for company in self.companies:
            region = company.region
            summary['regions'][region] = summary['regions'].get(region, 0) + 1

        # Count by industry
        for company in self.companies:
            industry = company.industry
            summary['industries'][industry] = summary['industries'].get(industry, 0) + 1

        # Count by sector
        for company in self.companies:
            sector = company.sector
            summary['sectors'][sector] = summary['sectors'].get(sector, 0) + 1

        # Count by source
        for company in self.companies:
            source = company.source
            summary['sources'][source] = summary['sources'].get(source, 0) + 1

        # Revenue distribution
        revenue_ranges = ['<$1B', '$1-10B', '$10-50B', '$50-100B', '$100B+']
        for company in self.companies:
            if company.revenue_numeric:
                if company.revenue_numeric < 1:
                    range_key = '<$1B'
                elif company.revenue_numeric < 10:
                    range_key = '$1-10B'
                elif company.revenue_numeric < 50:
                    range_key = '$10-50B'
                elif company.revenue_numeric < 100:
                    range_key = '$50-100B'
                else:
                    range_key = '$100B+'

                summary['revenue_distribution'][range_key] = summary['revenue_distribution'].get(range_key, 0) + 1

        # Employee distribution
        employee_ranges = ['<1K', '1-10K', '10-50K', '50-100K', '100K+']
        for company in self.companies:
            if company.employees:
                if company.employees < 1000:
                    range_key = '<1K'
                elif company.employees < 10000:
                    range_key = '1-10K'
                elif company.employees < 50000:
                    range_key = '10-50K'
                elif company.employees < 100000:
                    range_key = '50-100K'
                else:
                    range_key = '100K+'

                summary['employee_distribution'][range_key] = summary['employee_distribution'].get(range_key, 0) + 1

        return summary

    def run_complete_scraping(self):
        """Run complete scraping process"""
        print("🚀 Starting industrial companies data collection...")

        # Scrape from web sources
        self.scrape_fortune_global_500()
        time.sleep(2)  # Be respectful to servers

        self.scrape_manufacturing_companies_by_market_cap()
        time.sleep(2)

        # Generate comprehensive regional data
        self.generate_european_industrial_companies()
        self.generate_asian_industrial_companies()
        self.generate_north_american_industrial_companies()

        # Save all data
        self.save_data()

        print(f"🎉 Collection complete! Gathered {len(self.companies)} industrial companies")

        # Print summary
        print("\n📊 Collection Summary:")
        summary = self._generate_summary()

        print(f"  🌍 Regions:")
        for region, count in summary['regions'].items():
            print(f"    {region}: {count} companies")

        print(f"  🏭 Top Industries:")
        top_industries = sorted(summary['industries'].items(), key=lambda x: x[1], reverse=True)[:10]
        for industry, count in top_industries:
            print(f"    {industry}: {count} companies")

        print(f"  📈 Revenue Distribution:")
        for range_key, count in summary['revenue_distribution'].items():
            print(f"    {range_key}: {count} companies")

if __name__ == "__main__":
    scraper = IndustrialDataScraper()
    scraper.run_complete_scraping()