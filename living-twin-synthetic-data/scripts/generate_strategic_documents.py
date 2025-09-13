#!/usr/bin/env python3
"""
Strategic Documents Generator
Creates authentic Code of Conduct, Products & Terminology, Strategic DNA, and Strategic Market documents
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

class StrategicDocumentGenerator:
    """Generates realistic strategic documents for organizations"""
    
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "gpt-4"
        
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
                    # Extract wait time from error message or use exponential backoff
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
    
    async def generate_code_of_conduct(self, org: Dict) -> str:
        """Generate Code of Conduct - varies dramatically by industry and culture"""
        
        industry = org.get('industry', 'unknown')
        # Handle different size data formats
        size_data = org.get('size', 100)
        if isinstance(size_data, dict):
            size = size_data.get('employees', 100)
        elif isinstance(size_data, str):
            # Extract number from strings like "10000 employees"
            import re
            numbers = re.findall(r'\d+', size_data)
            size = int(numbers[0]) if numbers else 100
        else:
            size = size_data
        structure = org.get('structure_type', 'hierarchical')
        culture = org.get('delegation_culture', 'collaborative')
        years = org.get('years_in_business', 5)
        
        # Determine document length and formality based on characteristics
        if industry in ['finance', 'healthcare'] or size > 1000:
            doc_style = "comprehensive_formal"
        elif industry in ['technology', 'consulting'] and size > 100:
            doc_style = "structured_professional"
        elif years < 5 or culture in ['collaborative', 'distributed']:
            doc_style = "casual_values_based"
        else:
            doc_style = "moderate_practical"
        
        prompt = f"""
        Create a Code of Conduct for {org.get('name', 'Company')} based on these characteristics:
        
        Industry: {industry}
        Size: {size} employees
        Structure: {structure}
        Culture: {culture}
        Years in business: {years}
        Document style: {doc_style}
        
        STYLE GUIDELINES:
        - comprehensive_formal: Long, detailed, covers compliance, ethics, reporting procedures, consequences
        - structured_professional: Organized sections, clear policies, professional tone
        - casual_values_based: Short, value-driven, "be good" philosophy, conversational
        - moderate_practical: Practical guidelines, not too formal, covers key areas
        
        Include industry-appropriate elements:
        - Finance: Compliance, conflicts of interest, confidentiality
        - Healthcare: Patient privacy, safety, professional standards
        - Technology: IP protection, data privacy, open source guidelines
        - Startups: Innovation, collaboration, rapid iteration
        
        Make it authentic to this specific organization type and culture.
        """
        
        try:
            messages = [
                {"role": "system", "content": "You are an expert in corporate governance and organizational culture. Create authentic, industry-appropriate codes of conduct."},
                {"role": "user", "content": prompt}
            ]
            
            return await self.make_api_call_with_retry(messages, max_tokens=2000, temperature=0.7)
            
        except Exception as e:
            console.print(f"⚠️ Error generating Code of Conduct: {e}")
            return self._fallback_code_of_conduct(org, doc_style)
    
    async def generate_products_terminology(self, org: Dict) -> str:
        """Generate Products and Terminology guide with industry-authentic language"""
        
        industry = org.get('industry', 'unknown')
        name = org.get('name', 'Company')
        
        prompt = f"""
        Create a Products and Terminology guide for {name}, a {industry} company.
        
        Include:
        1. PRODUCTS/SERVICES CATALOG
           - Specific products they make/sell with realistic names
           - Service offerings with proper industry terminology
           - Product lines or categories
        
        2. INDUSTRY TERMINOLOGY
           - Technical terms employees would use daily
           - Industry-specific acronyms and jargon
           - Process and methodology names
           - Tools and systems common in this industry
        
        3. INTERNAL LANGUAGE
           - How the company talks about customers/clients
           - Department names and roles
           - Meeting types and processes
           - Success metrics and KPIs
        
        Make this authentic to {industry}:
        - Healthcare: EHR, clinical trials, patient outcomes, HIPAA, FDA approval
        - Technology: APIs, microservices, CI/CD, technical debt, user stories
        - Finance: AUM, basis points, risk assessment, regulatory capital
        - Manufacturing: lean manufacturing, quality control, supply chain
        - Consulting: deliverables, engagement, SOW, utilization rates
        
        Write as if an employee handbook section that helps new hires understand how people actually talk.
        """
        
        try:
            messages = [
                {"role": "system", "content": "You are an industry expert who creates authentic professional terminology guides. Use real industry language that domain experts would recognize."},
                {"role": "user", "content": prompt}
            ]
            
            return await self.make_api_call_with_retry(messages, max_tokens=1500, temperature=0.6)
            
        except Exception as e:
            console.print(f"⚠️ Error generating Products & Terminology: {e}")
            return self._fallback_products_terminology(org)
    
    async def generate_strategic_dna(self, org: Dict) -> str:
        """Generate Strategic DNA - core identity and ambition"""
        
        industry = org.get('industry', 'unknown')
        name = org.get('name', 'Company')
        # Handle different size data formats
        size_data = org.get('size', 100)
        if isinstance(size_data, dict):
            size = size_data.get('employees', 100)
        elif isinstance(size_data, str):
            # Extract number from strings like "10000 employees"
            import re
            numbers = re.findall(r'\d+', size_data)
            size = int(numbers[0]) if numbers else 100
        else:
            size = size_data
        culture = org.get('delegation_culture', 'collaborative')
        decision_speed = org.get('decision_speed', 'moderate')
        innovation = org.get('innovation_index', 0.5)
        values = org.get('values', [])
        
        prompt = f"""
        Create a Strategic DNA document for {name} that captures their core identity and ambition.
        
        Company Profile:
        - Industry: {industry}
        - Size: {size} employees
        - Culture: {culture}
        - Decision making: {decision_speed}
        - Innovation focus: {innovation:.2f}/1.0
        - Stated values: {', '.join(values) if values else 'None specified'}
        
        STRATEGIC DNA ELEMENTS:
        
        1. CORE IDENTITY
           - Who we are at our fundamental core
           - What defines us even if everything changes
           - Our unchanging character and principles
        
        2. AMBITION & ASPIRATION
           - What we're building toward (not just revenue goals)
           - The impact we want to have
           - How we want to be remembered
        
        3. DECISION-MAKING PHILOSOPHY
           - How we approach hard choices
           - What guides us when there's no clear answer
           - Risk tolerance and opportunity bias
        
        4. CULTURAL BACKBONE
           - How we treat people (employees, customers, partners)
           - What behaviors we reward vs discourage
           - The personality of the organization
        
        5. ENDURING BELIEFS
           - What we believe about our industry/market
           - Principles that won't change with trends
           - Our fundamental assumptions about success
        
        Write this as an internal document that defines "what we are even if trends shift dramatically."
        Make it specific to this {industry} company with this culture and ambition level.
        """
        
        try:
            messages = [
                {"role": "system", "content": "You are a strategic planning expert who creates authentic organizational identity documents. Focus on timeless identity rather than tactical plans."},
                {"role": "user", "content": prompt}
            ]
            
            return await self.make_api_call_with_retry(messages, max_tokens=1800, temperature=0.7)
            
        except Exception as e:
            console.print(f"⚠️ Error generating Strategic DNA: {e}")
            return self._fallback_strategic_dna(org)
    
    async def generate_strategic_market(self, org: Dict) -> str:
        """Generate Strategic Market document - future preferred state with KPIs"""
        
        industry = org.get('industry', 'unknown')
        name = org.get('name', 'Company')
        # Handle different size data formats
        size_data = org.get('size', 100)
        if isinstance(size_data, dict):
            size = size_data.get('employees', 100)
        elif isinstance(size_data, str):
            # Extract number from strings like "10000 employees"
            import re
            numbers = re.findall(r'\d+', size_data)
            size = int(numbers[0]) if numbers else 100
        else:
            size = size_data
        revenue = org.get('revenue_range', 'Unknown')
        years = org.get('years_in_business', 5)
        innovation = org.get('innovation_index', 0.5)
        digital_maturity = org.get('digital_maturity', 0.5)
        
        # Determine company stage for realistic goals
        if years < 5:
            stage = "startup_growth"
        elif years < 15 and size < 500:
            stage = "scale_up"
        elif size > 1000 or years > 15:
            stage = "established_expansion"
        else:
            stage = "mature_optimization"
        
        prompt = f"""
        Create a Strategic Market document for {name} describing their future preferred state.
        
        Current State:
        - Industry: {industry}
        - Size: {size} employees
        - Revenue: {revenue}
        - Stage: {stage}
        - Innovation level: {innovation:.2f}/1.0
        - Digital maturity: {digital_maturity:.2f}/1.0
        
        STRATEGIC MARKET ELEMENTS:
        
        1. FUTURE PREFERRED STATE (3-5 years)
           - What the company will look like when successful
           - Market position we're building toward
           - Scale and scope of operations
        
        2. KEY STRATEGIC GOALS
           - 3-5 major objectives that define success
           - Specific, measurable outcomes
           - Time-bound achievements
        
        3. CRITICAL KPIs & METRICS
           - Primary metrics we track religiously
           - Leading indicators of success
           - Financial and operational measures
           - Industry-specific performance indicators
        
        4. COARSE-GRAINED ACTIVITIES
           - Major initiatives and programs
           - Core operational focuses
           - Investment priorities
           - Capability building areas
        
        5. MARKET STRATEGY
           - How we compete and win
           - Target markets and customers
           - Competitive differentiation
           - Growth drivers and expansion plans
        
        Make this realistic for a {stage} {industry} company.
        Include industry-appropriate KPIs:
        - Healthcare: Patient outcomes, safety metrics, regulatory compliance
        - Technology: User growth, technical performance, innovation velocity
        - Finance: AUM, risk metrics, regulatory capital, client satisfaction
        - Manufacturing: Operational efficiency, quality metrics, supply chain
        """
        
        try:
            messages = [
                {"role": "system", "content": "You are a strategic planning expert who creates realistic market strategy documents with authentic KPIs and measurable goals."},
                {"role": "user", "content": prompt}
            ]
            
            return await self.make_api_call_with_retry(messages, max_tokens=2000, temperature=0.6)
            
        except Exception as e:
            console.print(f"⚠️ Error generating Strategic Market: {e}")
            return self._fallback_strategic_market(org, stage)
    
    # Fallback methods for when API calls fail
    def _fallback_code_of_conduct(self, org: Dict, style: str) -> str:
        if style == "casual_values_based":
            return f"""# {org.get('name', 'Company')} Code of Conduct
            
Be good. Work hard. Have fun. Treat everyone with respect.

That's it. We trust you to do the right thing."""
        else:
            return f"""# {org.get('name', 'Company')} Code of Conduct

## Professional Standards
All employees are expected to maintain the highest standards of professional conduct.

## Respect and Integrity
We treat colleagues, customers, and partners with respect and act with integrity in all business dealings.

## Compliance
Employees must comply with all applicable laws and company policies."""
    
    def _fallback_products_terminology(self, org: Dict) -> str:
        return f"""# {org.get('name', 'Company')} Products and Terminology

## Our Products
- Primary offerings in {org.get('industry', 'business')}
- Industry-standard solutions
- Customer-focused services

## Key Terms
Common terminology used in our {org.get('industry', 'business')} operations."""
    
    def _fallback_strategic_dna(self, org: Dict) -> str:
        return f"""# {org.get('name', 'Company')} Strategic DNA

## Who We Are
We are a {org.get('industry', 'business')} company focused on excellence and innovation.

## Our Ambition
To be the leading provider in our market while maintaining our core values.

## Decision Philosophy
We make decisions based on data, customer needs, and long-term value creation."""
    
    def _fallback_strategic_market(self, org: Dict, stage: str) -> str:
        return f"""# {org.get('name', 'Company')} Strategic Market

## Future Vision
Become a market leader in {org.get('industry', 'our industry')} over the next 5 years.

## Key Goals
- Increase market share
- Expand customer base
- Improve operational efficiency

## Critical KPIs
- Revenue growth
- Customer satisfaction
- Market share
- Operational metrics"""
    
    async def process_organization(self, org_path: Path) -> bool:
        """Process a single organization and generate all strategic documents"""
        
        org_data = self.load_organization(org_path)
        if not org_data:
            return False
        
        org_name = org_data.get('name', org_path.name)
        console.print(f"📝 Generating strategic documents for {org_name}")
        
        try:
            # Generate all four documents concurrently
            tasks = [
                self.generate_code_of_conduct(org_data),
                self.generate_products_terminology(org_data),
                self.generate_strategic_dna(org_data),
                self.generate_strategic_market(org_data)
            ]
            
            results = await asyncio.gather(*tasks)
            code_of_conduct, products_terminology, strategic_dna, strategic_market = results
            
            # Save documents
            doc_files = [
                (org_path / f"{org_path.name}_code_of_conduct.md", code_of_conduct),
                (org_path / f"{org_path.name}_products_terminology.md", products_terminology),
                (org_path / f"{org_path.name}_strategic_dna.md", strategic_dna),
                (org_path / f"{org_path.name}_strategic_market.md", strategic_market)
            ]
            
            for file_path, content in doc_files:
                with open(file_path, 'w') as f:
                    f.write(content)
            
            return True
            
        except Exception as e:
            console.print(f"❌ Error processing {org_name}: {e}")
            return False
    
    async def generate_all_documents(self, organizations_dir: str) -> Dict[str, int]:
        """Generate strategic documents for all organizations"""
        
        org_dir = Path(organizations_dir)
        if not org_dir.exists():
            console.print(f"❌ Organizations directory not found: {org_dir}")
            return {"success": 0, "failed": 0}
        
        org_folders = [d for d in org_dir.iterdir() if d.is_dir()]
        console.print(f"🏢 Found {len(org_folders)} organizations")
        
        results = {"success": 0, "failed": 0}
        
        # Process in smaller batches to respect rate limits
        batch_size = 2  # Reduced from 5 to handle rate limits better
        for i in range(0, len(org_folders), batch_size):
            batch = org_folders[i:i + batch_size]
            console.print(f"🔄 Processing batch {i//batch_size + 1}/{(len(org_folders) + batch_size - 1)//batch_size}")
            
            batch_tasks = []
            for org_folder in batch:
                task = self.process_organization(org_folder)
                batch_tasks.append(task)
            
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, Exception):
                    results["failed"] += 1
                    console.print(f"❌ Batch error: {result}")
                elif result:
                    results["success"] += 1
                else:
                    results["failed"] += 1
            
            # Longer delay between batches to respect rate limits
            if i + batch_size < len(org_folders):
                console.print("⏳ Waiting between batches...")
                await asyncio.sleep(10)  # Increased from 2s to 10s
        
        return results

@click.command()
@click.option('--organizations-dir', default='generated/structured/organizations', 
              help='Directory with organization folders')
@click.option('--batch-size', default=5, help='Organizations per batch (rate limiting)')
def main(organizations_dir, batch_size):
    """Generate strategic documents for all organizations"""
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        console.print("❌ OPENAI_API_KEY required")
        return
    
    console.print("📋 [bold blue]Strategic Documents Generator[/bold blue]")
    console.print("=" * 50)
    console.print("Generating 4 documents per organization:")
    console.print("• Code of Conduct (varies by industry/culture)")
    console.print("• Products & Terminology (industry-authentic)")
    console.print("• Strategic DNA (identity & ambition)")
    console.print("• Strategic Market (KPIs & future state)")
    console.print()
    
    generator = StrategicDocumentGenerator(api_key)
    
    results = asyncio.run(generator.generate_all_documents(organizations_dir))
    
    console.print(f"\n🎉 [green]Generation Complete![/green]")
    console.print(f"✅ Success: {results['success']} organizations")
    console.print(f"❌ Failed: {results['failed']} organizations")
    console.print(f"📊 Total documents created: {results['success'] * 4}")

if __name__ == "__main__":
    main()