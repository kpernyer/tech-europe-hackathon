#!/usr/bin/env python3
"""
AI-Enhanced Synthetic Data Generator
Uses GPT-4 to generate realistic organizations with industry-specific context
"""

import json
import os
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import random
from openai import AsyncOpenAI
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import yaml

load_dotenv()

@dataclass
class AIOrganization:
    id: str
    name: str
    industry: str
    sub_industry: str
    size: int
    revenue_range: str
    profitable: bool
    years_in_business: int
    lifecycle_stage: str  # startup, growth, mature, decline, turnaround
    headquarters: str
    regions: List[str]
    structure_type: str
    delegation_culture: str
    decision_speed: str
    innovation_index: float
    digital_maturity: float
    risk_tolerance: str
    strategic_priorities: List[str]
    products: List[str]
    services: List[str]
    values: List[str]
    competitive_advantages: List[str]
    key_challenges: List[str]
    leadership_style: str
    communication_style: str
    performance_metrics: List[str]
    decision_making_process: str
    change_management_approach: str
    people: List[str]
    departments: List[str]

class AIOrganizationGenerator:
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.industry_contexts = {}
        
    async def scrape_industry_context(self, industry: str) -> Dict[str, Any]:
        """Scrape real industry information for context"""
        try:
            # Sample URLs for industry research (you'd expand this)
            industry_urls = {
                "technology": [
                    "https://www.mckinsey.com/industries/technology-media-and-telecommunications",
                    "https://www.gartner.com/en/information-technology"
                ],
                "healthcare": [
                    "https://www.mckinsey.com/industries/healthcare-systems-and-services",
                    "https://www.who.int/health-topics"
                ],
                "finance": [
                    "https://www.mckinsey.com/industries/financial-services",
                    "https://www.bis.org/list/bcbs/"
                ]
            }
            
            context = {
                "terminology": [],
                "challenges": [],
                "trends": [],
                "metrics": [],
                "products": []
            }
            
            # This would normally scrape real content
            # For demo purposes, using predefined industry context
            industry_data = {
                "technology": {
                    "terminology": ["API", "microservices", "cloud-native", "DevOps", "agile", "digital transformation"],
                    "challenges": ["tech debt", "scalability", "cybersecurity", "talent retention", "rapid innovation"],
                    "trends": ["AI/ML adoption", "edge computing", "quantum computing", "sustainable tech"],
                    "metrics": ["uptime", "deployment frequency", "MTTR", "customer satisfaction", "ARR"],
                    "products": ["SaaS platforms", "mobile apps", "enterprise software", "analytics tools"]
                },
                "healthcare": {
                    "terminology": ["patient outcomes", "clinical trials", "regulatory compliance", "EHR", "telemedicine"],
                    "challenges": ["regulatory compliance", "patient safety", "cost containment", "staff burnout"],
                    "trends": ["digital health", "personalized medicine", "value-based care", "AI diagnostics"],
                    "metrics": ["patient satisfaction", "readmission rates", "clinical quality", "cost per patient"],
                    "products": ["medical devices", "pharmaceuticals", "diagnostic tools", "health software"]
                },
                "finance": {
                    "terminology": ["risk management", "compliance", "capital adequacy", "liquidity", "Basel III"],
                    "challenges": ["regulatory change", "digital disruption", "cybersecurity", "market volatility"],
                    "trends": ["fintech integration", "open banking", "ESG investing", "blockchain"],
                    "metrics": ["ROA", "ROE", "capital ratio", "loan loss provision", "customer acquisition cost"],
                    "products": ["banking services", "investment products", "insurance", "payment solutions"]
                }
            }
            
            return industry_data.get(industry, context)
            
        except Exception as e:
            print(f"Error scraping context for {industry}: {e}")
            return {"terminology": [], "challenges": [], "trends": [], "metrics": [], "products": []}

    async def generate_organization_prompt(self, industry: str, size_category: str, lifecycle_stage: str) -> str:
        """Generate detailed prompt for organization creation"""
        context = await self.scrape_industry_context(industry)
        
        return f"""
        Create a realistic {industry} organization with the following characteristics:
        
        Size Category: {size_category}
        Lifecycle Stage: {lifecycle_stage}
        Industry Context: {context}
        
        Generate a comprehensive organization profile including:
        1. Company name that sounds realistic for this industry
        2. Specific sub-industry focus
        3. Realistic size (employees) for {size_category} category
        4. Revenue range appropriate for size and industry
        5. Geographic presence that makes business sense
        6. Leadership and decision-making style
        7. Strategic priorities aligned with {lifecycle_stage} stage
        8. Industry-specific products/services using proper terminology
        9. Competitive advantages realistic for this space
        10. Key challenges facing this type of organization
        11. Performance metrics commonly used in {industry}
        12. Decision-making processes typical for {size_category} organizations
        
        Use authentic industry terminology and realistic business challenges.
        Make the organization feel like a real company that could exist today.
        
        Return as JSON with all required fields populated with realistic data.
        """

    async def generate_single_organization(self, index: int, industry: str = None, 
                                         size_category: str = None, 
                                         lifecycle_stage: str = None) -> AIOrganization:
        """Generate a single AI-enhanced organization"""
        
        # Randomize parameters if not specified
        industries = ["technology", "healthcare", "finance", "manufacturing", "retail", "consulting", "education"]
        size_categories = ["small", "medium", "large", "enterprise"]
        lifecycle_stages = ["startup", "growth", "mature", "decline", "turnaround"]
        
        industry = industry or random.choice(industries)
        size_category = size_category or random.choice(size_categories)
        lifecycle_stage = lifecycle_stage or random.choice(lifecycle_stages)
        
        prompt = await self.generate_organization_prompt(industry, size_category, lifecycle_stage)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert business analyst who creates realistic organization profiles. Return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,  # Higher creativity for variety
                max_tokens=2000
            )
            
            # Parse the AI response and create organization
            ai_data = json.loads(response.choices[0].message.content)
            
            # Map AI response to our structure
            org = AIOrganization(
                id=f"org_{index:03d}",
                name=ai_data.get("name", f"Company {index}"),
                industry=industry,
                sub_industry=ai_data.get("sub_industry", industry),
                size=ai_data.get("size", self._default_size_for_category(size_category)),
                revenue_range=ai_data.get("revenue_range", "$1M-$10M"),
                profitable=ai_data.get("profitable", True),
                years_in_business=ai_data.get("years_in_business", 10),
                lifecycle_stage=lifecycle_stage,
                headquarters=ai_data.get("headquarters", "San Francisco"),
                regions=ai_data.get("regions", ["US"]),
                structure_type=ai_data.get("structure_type", "hierarchical"),
                delegation_culture=ai_data.get("delegation_culture", "collaborative"),
                decision_speed=ai_data.get("decision_speed", "moderate"),
                innovation_index=ai_data.get("innovation_index", random.uniform(0.3, 0.9)),
                digital_maturity=ai_data.get("digital_maturity", random.uniform(0.2, 0.8)),
                risk_tolerance=ai_data.get("risk_tolerance", "moderate"),
                strategic_priorities=ai_data.get("strategic_priorities", []),
                products=ai_data.get("products", []),
                services=ai_data.get("services", []),
                values=ai_data.get("values", []),
                competitive_advantages=ai_data.get("competitive_advantages", []),
                key_challenges=ai_data.get("key_challenges", []),
                leadership_style=ai_data.get("leadership_style", "collaborative"),
                communication_style=ai_data.get("communication_style", "transparent"),
                performance_metrics=ai_data.get("performance_metrics", []),
                decision_making_process=ai_data.get("decision_making_process", "consensus"),
                change_management_approach=ai_data.get("change_management_approach", "incremental"),
                people=[],  # Will be populated later
                departments=ai_data.get("departments", ["Executive", "Operations"])
            )
            
            return org
            
        except Exception as e:
            print(f"Error generating organization {index}: {e}")
            # Fallback to basic generation
            return self._generate_fallback_organization(index, industry, size_category, lifecycle_stage)
    
    def _default_size_for_category(self, category: str) -> int:
        sizes = {
            "small": random.randint(5, 50),
            "medium": random.randint(51, 500),  
            "large": random.randint(501, 5000),
            "enterprise": random.randint(5001, 50000)
        }
        return sizes.get(category, 100)
    
    def _generate_fallback_organization(self, index: int, industry: str, 
                                      size_category: str, lifecycle_stage: str) -> AIOrganization:
        """Fallback generation if AI fails"""
        return AIOrganization(
            id=f"org_{index:03d}",
            name=f"Fallback Company {index}",
            industry=industry,
            sub_industry=industry,
            size=self._default_size_for_category(size_category),
            revenue_range="$1M-$10M",
            profitable=True,
            years_in_business=random.randint(1, 50),
            lifecycle_stage=lifecycle_stage,
            headquarters="New York",
            regions=["US"],
            structure_type="hierarchical",
            delegation_culture="collaborative", 
            decision_speed="moderate",
            innovation_index=random.uniform(0.1, 0.9),
            digital_maturity=random.uniform(0.1, 0.9),
            risk_tolerance="moderate",
            strategic_priorities=["growth", "efficiency"],
            products=["Product A", "Product B"],
            services=["Service A", "Service B"],
            values=["integrity", "innovation", "teamwork"],
            competitive_advantages=["quality", "customer service"],
            key_challenges=["competition", "regulation"],
            leadership_style="collaborative",
            communication_style="transparent",
            performance_metrics=["revenue", "profit"],
            decision_making_process="consensus",
            change_management_approach="incremental",
            people=[],
            departments=["Executive", "Operations"]
        )

    async def generate_organizations(self, count: int, output_dir: str = "outputs",
                                   industry_filter: str = None, size_filter: str = None,
                                   lifecycle_filter: str = None, batch_size: int = 10):
        """Generate multiple AI-enhanced organizations"""
        print(f"🤖 Generating {count} AI-enhanced organizations...")
        
        os.makedirs(f"{output_dir}/organizations", exist_ok=True)
        
        organizations = []
        
        for i in range(0, count, batch_size):
            batch_end = min(i + batch_size, count)
            print(f"🔄 Processing batch {i//batch_size + 1}: organizations {i}-{batch_end-1}")
            
            batch_tasks = []
            for j in range(i, batch_end):
                task = self.generate_single_organization(
                    j, industry_filter, size_filter, lifecycle_filter
                )
                batch_tasks.append(task)
            
            # Process batch concurrently
            batch_orgs = await asyncio.gather(*batch_tasks)
            organizations.extend(batch_orgs)
            
            # Save each organization
            for org in batch_orgs:
                safe_name = org.name.replace(' ', '_').replace('/', '_')
                filename = f"{output_dir}/organizations/org_{org.id}_{safe_name}.json"
                with open(filename, 'w') as f:
                    json.dump(asdict(org), f, indent=2)
            
            # Small delay to respect rate limits
            await asyncio.sleep(1)
        
        print(f"✅ Generated {len(organizations)} AI-enhanced organizations")
        return organizations

async def main():
    """Test the AI generator"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return
    
    generator = AIOrganizationGenerator(api_key)
    
    # Generate a small test batch
    organizations = await generator.generate_organizations(5, "test_outputs")
    
    print(f"Generated {len(organizations)} organizations:")
    for org in organizations[:2]:  # Show first 2
        print(f"- {org.name} ({org.industry}, {org.lifecycle_stage}, {org.size} employees)")

if __name__ == "__main__":
    asyncio.run(main())