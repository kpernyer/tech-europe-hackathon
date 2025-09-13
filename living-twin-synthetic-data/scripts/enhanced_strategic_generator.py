#!/usr/bin/env python3
"""
Enhanced Strategic Documents Generator
Uses real company patterns and authentic corporate language to create superior synthetic documents
"""

import json
import os
import asyncio
import random
from pathlib import Path
from typing import Dict, List, Any
import click
from rich.console import Console
from rich.progress import track
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
console = Console()

class EnhancedStrategicGenerator:
    """Enhanced generator using real corporate language patterns"""
    
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "gpt-4"
        
        # Real corporate language patterns from major companies
        self.industry_patterns = {
            "technology": {
                "terminology": [
                    "digital transformation", "innovation velocity", "technical debt", "user experience",
                    "machine learning", "artificial intelligence", "cloud-native", "DevOps culture",
                    "agile methodology", "continuous integration", "microservices architecture", "API-first",
                    "data-driven decisions", "scalability", "security by design", "open source"
                ],
                "values_language": [
                    "innovation", "excellence", "customer obsession", "think different", "move fast",
                    "be bold", "embrace change", "fail fast, learn faster", "customer-centric",
                    "data-driven", "transparent", "collaborative", "inclusive", "diverse"
                ],
                "code_style": "structured_professional_tech"
            },
            "healthcare": {
                "terminology": [
                    "patient outcomes", "clinical excellence", "regulatory compliance", "HIPAA",
                    "FDA approval", "clinical trials", "evidence-based medicine", "quality metrics",
                    "patient safety", "healthcare delivery", "population health", "precision medicine",
                    "electronic health records", "interoperability", "care coordination", "value-based care"
                ],
                "values_language": [
                    "compassion", "integrity", "excellence", "innovation", "respect", "accountability",
                    "patient first", "do no harm", "continuous improvement", "scientific rigor",
                    "ethical standards", "professional excellence", "collaborative care"
                ],
                "code_style": "comprehensive_formal_healthcare"
            },
            "finance": {
                "terminology": [
                    "assets under management", "regulatory capital", "risk management", "compliance",
                    "fiduciary responsibility", "ESG investing", "digital banking", "fintech",
                    "cryptocurrency", "blockchain", "robo-advisory", "wealth management",
                    "investment banking", "capital markets", "liquidity", "credit risk", "operational risk"
                ],
                "values_language": [
                    "integrity", "trust", "excellence", "client focus", "risk management",
                    "regulatory compliance", "fiduciary duty", "transparency", "accountability",
                    "long-term thinking", "sustainable investing", "ethical conduct"
                ],
                "code_style": "comprehensive_formal_finance"
            },
            "consulting": {
                "terminology": [
                    "client engagement", "thought leadership", "best practices", "change management",
                    "digital transformation", "strategy execution", "operational excellence",
                    "organizational design", "talent management", "performance improvement",
                    "stakeholder management", "project delivery", "knowledge management"
                ],
                "values_language": [
                    "client success", "excellence", "collaboration", "innovation", "integrity",
                    "diverse perspectives", "continuous learning", "thought leadership",
                    "results-driven", "partnership", "professional excellence"
                ],
                "code_style": "structured_professional_consulting"
            },
            "manufacturing": {
                "terminology": [
                    "lean manufacturing", "six sigma", "total quality management", "supply chain",
                    "operational excellence", "continuous improvement", "safety first",
                    "environmental sustainability", "automation", "Industry 4.0", "IoT",
                    "predictive maintenance", "quality control", "regulatory compliance"
                ],
                "values_language": [
                    "safety", "quality", "efficiency", "sustainability", "innovation",
                    "continuous improvement", "teamwork", "accountability", "customer focus",
                    "operational excellence", "environmental stewardship"
                ],
                "code_style": "structured_professional_manufacturing"
            }
        }
        
        # Real code of conduct patterns from Fortune 500 companies
        self.code_patterns = {
            "comprehensive_formal_healthcare": {
                "sections": [
                    "Our Commitment to Patients", "Clinical Excellence", "Regulatory Compliance",
                    "Patient Privacy and Confidentiality", "Research Ethics", "Conflicts of Interest",
                    "Professional Standards", "Reporting Violations", "Disciplinary Actions"
                ],
                "tone": "formal, compliance-focused, patient-centric",
                "length": "comprehensive (2000-3000 words)"
            },
            "comprehensive_formal_finance": {
                "sections": [
                    "Fiduciary Responsibility", "Regulatory Compliance", "Conflicts of Interest",
                    "Market Conduct", "Anti-Money Laundering", "Data Protection", "Trading Ethics",
                    "Client Confidentiality", "Reporting Requirements", "Enforcement"
                ],
                "tone": "formal, regulatory-focused, risk-aware",
                "length": "comprehensive (2500-3500 words)"
            },
            "structured_professional_tech": {
                "sections": [
                    "Our Values", "Respect and Inclusion", "Data Privacy", "Intellectual Property",
                    "Open Source Guidelines", "Customer Trust", "Innovation Ethics", "Reporting Concerns"
                ],
                "tone": "professional but approachable, innovation-focused",
                "length": "structured (1500-2000 words)"
            },
            "structured_professional_consulting": {
                "sections": [
                    "Client First", "Professional Excellence", "Confidentiality", "Conflicts of Interest",
                    "Team Collaboration", "Continuous Learning", "Diversity and Inclusion", "Reporting"
                ],
                "tone": "professional, client-focused, collaborative",
                "length": "structured (1200-1800 words)"
            }
        }
        
    async def make_api_call_with_retry(self, messages: List[Dict], max_tokens: int = 2000, temperature: float = 0.7, max_retries: int = 5) -> str:
        """Make OpenAI API call with exponential backoff retry logic"""
        for attempt in range(max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
                
            except Exception as e:
                if "rate_limit_exceeded" in str(e) and attempt < max_retries - 1:
                    wait_time = min(2 ** attempt + random.uniform(0, 1), 60)
                    console.print(f"⏳ Rate limit hit, waiting {wait_time:.1f}s (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise e

    def load_organization(self, org_path: Path) -> Dict:
        """Load organization data from JSON file"""
        json_file = org_path / f"{org_path.name}.json"
        
        if not json_file.exists():
            return {}
        
        try:
            with open(json_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            console.print(f"⚠️ Error loading {json_file}: {e}")
            return {}

    def get_size_value(self, org: Dict) -> int:
        """Extract employee count from various size formats"""
        size_data = org.get('size', 100)
        if isinstance(size_data, dict):
            return size_data.get('employees', 100)
        elif isinstance(size_data, str):
            import re
            numbers = re.findall(r'\d+', size_data)
            return int(numbers[0]) if numbers else 100
        else:
            return size_data

    async def generate_enhanced_code_of_conduct(self, org: Dict) -> str:
        """Generate enhanced code of conduct using real corporate patterns"""
        
        industry = org.get('industry', 'unknown')
        name = org.get('name', 'Company')
        size = self.get_size_value(org)
        culture = org.get('delegation_culture', 'collaborative')
        years = org.get('years_in_business', 5)
        
        # Get industry-specific patterns
        patterns = self.industry_patterns.get(industry, self.industry_patterns.get('technology'))
        code_style = patterns['code_style']
        terminology = patterns['terminology']
        values = patterns['values_language']
        
        # Get code structure patterns
        structure = self.code_patterns.get(code_style, self.code_patterns['structured_professional_tech'])
        
        prompt = f"""
        Create an authentic Code of Conduct for {name} using real Fortune 500 corporate language patterns.
        
        COMPANY PROFILE:
        - Name: {name}
        - Industry: {industry} 
        - Size: {size:,} employees
        - Culture: {culture}
        - Years in business: {years}
        
        INDUSTRY PATTERNS TO INCORPORATE:
        - Terminology: {', '.join(terminology[:10])}
        - Core Values: {', '.join(values[:8])}
        
        DOCUMENT STRUCTURE (based on real {industry} companies):
        - Sections: {', '.join(structure['sections'])}
        - Tone: {structure['tone']}
        - Target Length: {structure['length']}
        
        REQUIREMENTS:
        1. Use authentic corporate language from real {industry} companies
        2. Include industry-specific compliance requirements and terminology
        3. Match the formal structure of Fortune 500 codes of conduct
        4. Include specific behavioral expectations and reporting procedures
        5. Use professional, authoritative tone appropriate for {size:,} employee organization
        
        Base this on real codes of conduct from companies like:
        - Technology: Microsoft, Apple, Google corporate policies
        - Healthcare: Johnson & Johnson, Pfizer compliance frameworks
        - Finance: JPMorgan Chase, Goldman Sachs ethical standards
        - Manufacturing: GE, 3M operational guidelines
        - Consulting: Accenture, Deloitte professional standards
        
        Make this indistinguishable from a real {industry} company's official code of conduct.
        """
        
        try:
            messages = [
                {"role": "system", "content": f"You are a corporate governance expert who has studied hundreds of Fortune 500 codes of conduct. Create authentic, industry-specific codes that match real corporate standards. Use the exact language patterns, structure, and compliance requirements found in actual {industry} company documents."},
                {"role": "user", "content": prompt}
            ]
            
            return await self.make_api_call_with_retry(messages, max_tokens=2500, temperature=0.6)
            
        except Exception as e:
            console.print(f"⚠️ Error generating Enhanced Code of Conduct: {e}")
            return f"# {name} Code of Conduct\n\nError generating enhanced document. Please try again."

    async def generate_enhanced_products_terminology(self, org: Dict) -> str:
        """Generate enhanced products and terminology guide"""
        
        industry = org.get('industry', 'unknown')
        name = org.get('name', 'Company')
        
        # Get industry-specific patterns
        patterns = self.industry_patterns.get(industry, self.industry_patterns.get('technology'))
        terminology = patterns['terminology']
        
        prompt = f"""
        Create an authentic Products and Terminology guide for {name}, mirroring real {industry} company documentation.
        
        Use authentic terminology from leading {industry} companies:
        {', '.join(terminology)}
        
        STRUCTURE (based on real corporate handbooks):
        
        1. PRODUCTS & SERVICES PORTFOLIO
           - Core offerings with real industry naming conventions
           - Service lines using authentic {industry} categorization
           - Product lifecycle terminology
        
        2. INDUSTRY TERMINOLOGY GLOSSARY
           - Technical terms employees actually use daily
           - Regulatory and compliance terminology
           - Process and methodology definitions
           - Tools and platforms common in {industry}
        
        3. INTERNAL LANGUAGE & CULTURE
           - How we refer to clients/customers/patients/users
           - Department naming conventions 
           - Meeting types and operational processes
           - Performance metrics and KPIs used in {industry}
        
        4. EXTERNAL COMMUNICATION STANDARDS
           - Brand language guidelines
           - Client-facing terminology
           - Industry positioning language
        
        Model this after real terminology guides from:
        - Technology: Google, Microsoft, Amazon internal documentation
        - Healthcare: Mayo Clinic, Cleveland Clinic operational guides
        - Finance: Goldman Sachs, JPMorgan terminology standards
        - Consulting: McKinsey, BCG knowledge frameworks
        
        Make this read like authentic internal corporate documentation that new employees would receive.
        """
        
        try:
            messages = [
                {"role": "system", "content": f"You are a corporate communications expert who has analyzed internal documentation from hundreds of {industry} companies. Create authentic terminology guides that match real corporate standards and use genuine industry language."},
                {"role": "user", "content": prompt}
            ]
            
            return await self.make_api_call_with_retry(messages, max_tokens=1800, temperature=0.5)
            
        except Exception as e:
            console.print(f"⚠️ Error generating Enhanced Products & Terminology: {e}")
            return f"# {name} Products and Terminology\n\nError generating enhanced document."

    async def generate_enhanced_strategic_dna(self, org: Dict) -> str:
        """Generate enhanced strategic DNA using real corporate identity patterns"""
        
        industry = org.get('industry', 'unknown')
        name = org.get('name', 'Company')
        size = self.get_size_value(org)
        culture = org.get('delegation_culture', 'collaborative')
        innovation = org.get('innovation_index', 0.5)
        values = org.get('values', [])
        
        # Get industry-specific patterns
        patterns = self.industry_patterns.get(industry, self.industry_patterns.get('technology'))
        core_values = patterns['values_language']
        
        prompt = f"""
        Create an authentic Strategic DNA document for {name} using the language and structure of real Fortune 500 corporate identity documents.
        
        COMPANY CONTEXT:
        - Industry: {industry}
        - Size: {size:,} employees  
        - Culture: {culture}
        - Innovation Focus: {innovation:.1f}/1.0
        - Stated Values: {', '.join(values) if values else 'Define based on industry'}
        
        AUTHENTIC {industry.upper()} VALUES LANGUAGE:
        {', '.join(core_values)}
        
        STRUCTURE (mirroring real corporate DNA documents):
        
        ## WHO WE ARE (Core Identity)
        - Fundamental essence that never changes
        - Industry positioning and unique character
        - Cultural DNA and organizational personality
        
        ## OUR AMBITION (Future Vision)
        - Aspirational impact beyond financial metrics  
        - Legacy we want to create in {industry}
        - How we want to transform our space
        
        ## HOW WE DECIDE (Decision Philosophy)
        - Core principles guiding difficult choices
        - Risk tolerance and opportunity approach
        - Stakeholder prioritization framework
        
        ## OUR CULTURE (Behavioral DNA)
        - How we treat employees, customers, partners
        - Behaviors we reward vs discourage  
        - The personality of the organization
        
        ## ENDURING BELIEFS (Timeless Principles)
        - Fundamental beliefs about {industry} and markets
        - Principles that survive trend changes
        - Success philosophy and core assumptions
        
        Model after real strategic identity documents from:
        - Apple: "Think Different" philosophy and design principles
        - Johnson & Johnson: "Our Credo" and patient-first mission
        - Goldman Sachs: Partnership principles and client focus
        - 3M: Innovation culture and scientific approach
        
        Use the authentic language, depth, and philosophical approach of real corporate identity documents. This should feel like an internal document that defines organizational soul.
        """
        
        try:
            messages = [
                {"role": "system", "content": f"You are a strategic planning expert who has analyzed the strategic identity documents of Fortune 500 companies. Create authentic corporate DNA documents that capture the philosophical depth and authentic language of real organizational identity statements. Focus on timeless principles over tactical elements."},
                {"role": "user", "content": prompt}
            ]
            
            return await self.make_api_call_with_retry(messages, max_tokens=2000, temperature=0.7)
            
        except Exception as e:
            console.print(f"⚠️ Error generating Enhanced Strategic DNA: {e}")
            return f"# {name} Strategic DNA\n\nError generating enhanced document."

    async def generate_enhanced_strategic_market(self, org: Dict) -> str:
        """Generate enhanced strategic market document with real corporate KPI patterns"""
        
        industry = org.get('industry', 'unknown')
        name = org.get('name', 'Company')
        size = self.get_size_value(org)
        revenue = org.get('revenue_range', 'Unknown')
        years = org.get('years_in_business', 5)
        innovation = org.get('innovation_index', 0.5)
        
        # Determine company stage for realistic goals
        if years < 5:
            stage = "high_growth_startup"
        elif years < 15 and size < 500:
            stage = "scaling_company"
        elif size > 1000 or years > 15:
            stage = "established_enterprise"
        else:
            stage = "mature_optimization"
        
        # Get industry-specific KPIs and metrics
        industry_kpis = {
            "technology": [
                "Monthly Active Users (MAU)", "Customer Acquisition Cost (CAC)", "Annual Recurring Revenue (ARR)",
                "Net Revenue Retention", "Product-Market Fit Score", "Time to Market", "Developer Productivity",
                "System Uptime (99.9%+)", "API Response Time", "Security Incident Response Time"
            ],
            "healthcare": [
                "Patient Satisfaction (HCAHPS)", "Clinical Quality Metrics", "Readmission Rates",
                "Length of Stay", "Medication Error Rate", "Infection Rates", "Mortality Index",
                "Regulatory Compliance Score", "Staff-to-Patient Ratios", "Cost Per Quality Adjusted Life Year"
            ],
            "finance": [
                "Assets Under Management (AUM)", "Return on Equity (ROE)", "Net Interest Margin",
                "Credit Loss Ratio", "Efficiency Ratio", "Regulatory Capital Ratio", "Client Satisfaction",
                "Risk-Weighted Assets", "Liquidity Coverage Ratio", "Trading Revenue"
            ],
            "consulting": [
                "Utilization Rate", "Revenue Per Consultant", "Client Satisfaction Score",
                "Project Margin", "Repeat Business Rate", "Proposal Win Rate", "Talent Retention",
                "Knowledge Asset Utilization", "Thought Leadership Impact", "Digital Capability Score"
            ],
            "manufacturing": [
                "Overall Equipment Effectiveness (OEE)", "First Pass Yield", "Defect Rate",
                "On-Time Delivery", "Inventory Turnover", "Safety Incident Rate", "Cost Per Unit",
                "Supplier Quality Rating", "Energy Efficiency", "Waste Reduction Percentage"
            ]
        }
        
        kpis = industry_kpis.get(industry, industry_kpis['technology'])
        
        prompt = f"""
        Create an authentic Strategic Market document for {name} using real Fortune 500 strategic planning frameworks and KPI structures.
        
        COMPANY PROFILE:
        - Industry: {industry}
        - Size: {size:,} employees
        - Revenue: {revenue}
        - Stage: {stage}
        - Innovation Level: {innovation:.1f}/1.0
        
        AUTHENTIC {industry.upper()} KPIs TO INCLUDE:
        {', '.join(kpis[:8])}
        
        STRUCTURE (based on real corporate strategic plans):
        
        ## FUTURE PREFERRED STATE (3-5 Year Vision)
        - Specific market position and competitive advantage
        - Scale of operations and market presence
        - Quantified success metrics and benchmarks
        
        ## STRATEGIC IMPERATIVES (Core Objectives)
        - 3-5 mission-critical priorities that define success
        - Measurable outcomes with specific targets
        - Time-bound milestones and checkpoints
        
        ## KEY PERFORMANCE INDICATORS (KPIs)
        - Primary metrics tracked at board level
        - Leading indicators that predict success
        - Industry-standard benchmarks and targets
        - Operational metrics that drive results
        
        ## STRATEGIC INITIATIVES (Major Programs)  
        - Large-scale programs and investments
        - Capability building priorities
        - Market expansion and product development
        - Digital transformation and innovation projects
        
        ## MARKET STRATEGY & COMPETITIVE POSITIONING
        - How we compete and differentiate
        - Target markets and customer segments
        - Growth drivers and expansion strategy
        - Competitive moats and sustainable advantages
        
        Use authentic strategic planning language from real {industry} companies:
        - Include specific, measurable targets (not vague goals)
        - Use industry-standard KPIs and benchmarks
        - Reference real competitive dynamics
        - Include genuine operational metrics
        
        Model after strategic planning documents from:
        - Technology: Amazon's long-term planning, Microsoft's cloud strategy
        - Healthcare: Mayo Clinic's strategic plan, Kaiser Permanente objectives  
        - Finance: JPMorgan's strategic priorities, Goldman Sachs market strategy
        - Manufacturing: GE's industrial strategy, 3M's innovation roadmap
        
        Make this indistinguishable from a real {stage} {industry} company's strategic plan.
        """
        
        try:
            messages = [
                {"role": "system", "content": f"You are a strategic planning expert who has analyzed Fortune 500 strategic plans across industries. Create authentic strategic market documents that use real corporate planning frameworks, genuine KPIs, and specific measurable targets that match actual {industry} company strategic plans."},
                {"role": "user", "content": prompt}
            ]
            
            return await self.make_api_call_with_retry(messages, max_tokens=2200, temperature=0.6)
            
        except Exception as e:
            console.print(f"⚠️ Error generating Enhanced Strategic Market: {e}")
            return f"# {name} Strategic Market\n\nError generating enhanced document."

    async def process_organization_enhanced(self, org_path: Path) -> bool:
        """Process organization with enhanced authentic documents"""
        
        org_data = self.load_organization(org_path)
        if not org_data:
            return False
        
        org_name = org_data.get('name', org_path.name)
        console.print(f"🚀 Generating ENHANCED documents for {org_name} ({org_data.get('industry', 'unknown')})")
        
        try:
            # Generate all four enhanced documents concurrently
            tasks = [
                self.generate_enhanced_code_of_conduct(org_data),
                self.generate_enhanced_products_terminology(org_data), 
                self.generate_enhanced_strategic_dna(org_data),
                self.generate_enhanced_strategic_market(org_data)
            ]
            
            results = await asyncio.gather(*tasks)
            code_of_conduct, products_terminology, strategic_dna, strategic_market = results
            
            # Save enhanced documents with "enhanced" prefix
            doc_files = [
                (org_path / f"{org_path.name}_enhanced_code_of_conduct.md", code_of_conduct),
                (org_path / f"{org_path.name}_enhanced_products_terminology.md", products_terminology),
                (org_path / f"{org_path.name}_enhanced_strategic_dna.md", strategic_dna),
                (org_path / f"{org_path.name}_enhanced_strategic_market.md", strategic_market)
            ]
            
            for file_path, content in doc_files:
                with open(file_path, 'w') as f:
                    f.write(content)
            
            console.print(f"✅ Enhanced documents created for {org_name}")
            return True
            
        except Exception as e:
            console.print(f"❌ Error processing {org_name}: {e}")
            return False

    async def generate_enhanced_documents(self, organizations_dir: str, max_orgs: int = 10) -> Dict[str, int]:
        """Generate enhanced strategic documents for selected organizations"""
        
        org_dir = Path(organizations_dir)
        if not org_dir.exists():
            console.print(f"❌ Organizations directory not found: {org_dir}")
            return {"success": 0, "failed": 0}
        
        # Get organizations with different industries for variety
        org_folders = [d for d in org_dir.iterdir() if d.is_dir()]
        
        # Select diverse set of organizations
        selected_orgs = []
        industries_seen = set()
        
        for org_folder in org_folders:
            if len(selected_orgs) >= max_orgs:
                break
                
            org_data = self.load_organization(org_folder)
            if org_data:
                industry = org_data.get('industry', 'unknown')
                # Prioritize different industries for variety
                if industry not in industries_seen or len(selected_orgs) < 5:
                    selected_orgs.append(org_folder)
                    industries_seen.add(industry)
        
        console.print(f"🎯 Selected {len(selected_orgs)} organizations across industries: {', '.join(industries_seen)}")
        
        results = {"success": 0, "failed": 0}
        
        # Process organizations one by one to avoid rate limits
        for org_folder in track(selected_orgs, description="Generating enhanced documents..."):
            success = await self.process_organization_enhanced(org_folder)
            if success:
                results["success"] += 1
            else:
                results["failed"] += 1
            
            # Delay between organizations to be respectful of rate limits
            await asyncio.sleep(5)
        
        return results

@click.command()
@click.option('--organizations-dir', default='/Users/kenper/src/aprio-one/tech-europe-hackathon/living-twin-synthetic-data/generated/structured/organizations', 
              help='Directory with organization folders')
@click.option('--max-orgs', default=10, help='Maximum organizations to enhance')
def main(organizations_dir, max_orgs):
    """Generate enhanced strategic documents using real corporate patterns"""
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        console.print("❌ OPENAI_API_KEY required")
        return
    
    console.print("🚀 [bold blue]Enhanced Strategic Documents Generator[/bold blue]")
    console.print("=" * 60)
    console.print("Creating authentic strategic documents using real Fortune 500 patterns")
    console.print("🏢 Industries: Technology, Healthcare, Finance, Manufacturing, Consulting")
    console.print("📋 Documents: Enhanced Code of Conduct, Products & Terminology, Strategic DNA, Strategic Market")
    console.print("✨ Quality: Indistinguishable from real corporate documents")
    console.print()
    
    generator = EnhancedStrategicGenerator(api_key)
    
    results = asyncio.run(generator.generate_enhanced_documents(organizations_dir, max_orgs))
    
    console.print(f"\n🎉 [green]Enhanced Generation Complete![/green]")
    console.print(f"✅ Success: {results['success']} organizations")
    console.print(f"❌ Failed: {results['failed']} organizations") 
    console.print(f"📊 Total enhanced documents created: {results['success'] * 4}")
    console.print(f"💎 Quality: Fortune 500-level authenticity")

if __name__ == "__main__":
    main()