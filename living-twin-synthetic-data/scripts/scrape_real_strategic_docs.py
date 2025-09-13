#!/usr/bin/env python3
"""
Real Company Strategic Document Scraper
Scrapes authentic strategic documents from real companies to improve synthetic generation
"""

import asyncio
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
import click
from rich.console import Console
from rich.progress import track
import aiohttp
from bs4 import BeautifulSoup
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
console = Console()

@dataclass
class CompanyProfile:
    name: str
    industry: str
    size: str
    ticker: Optional[str] = None
    website: str = ""
    headquarters: str = ""

@dataclass
class StrategicDocument:
    company: str
    doc_type: str  # code_of_conduct, mission_vision, values, strategic_plan
    title: str
    content: str
    url: str
    industry: str
    company_size: str

class RealDocumentScraper:
    """Scrapes real strategic documents from public companies"""
    
    def __init__(self, openai_api_key: str):
        self.client = AsyncOpenAI(api_key=openai_api_key)
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Target companies across different industries
        self.target_companies = [
            # Technology
            CompanyProfile("Microsoft", "technology", "large", "MSFT", "https://www.microsoft.com"),
            CompanyProfile("Apple", "technology", "large", "AAPL", "https://www.apple.com"),
            CompanyProfile("Google", "technology", "large", "GOOGL", "https://www.google.com"),
            CompanyProfile("Amazon", "technology", "large", "AMZN", "https://www.amazon.com"),
            
            # Healthcare
            CompanyProfile("Johnson & Johnson", "healthcare", "large", "JNJ", "https://www.jnj.com"),
            CompanyProfile("Pfizer", "healthcare", "large", "PFE", "https://www.pfizer.com"),
            CompanyProfile("UnitedHealth", "healthcare", "large", "UNH", "https://www.unitedhealthgroup.com"),
            
            # Finance
            CompanyProfile("JPMorgan Chase", "finance", "large", "JPM", "https://www.jpmorganchase.com"),
            CompanyProfile("Bank of America", "finance", "large", "BAC", "https://www.bankofamerica.com"),
            CompanyProfile("Goldman Sachs", "finance", "large", "GS", "https://www.goldmansachs.com"),
            
            # Manufacturing
            CompanyProfile("General Electric", "manufacturing", "large", "GE", "https://www.ge.com"),
            CompanyProfile("3M", "manufacturing", "large", "MMM", "https://www.3m.com"),
            CompanyProfile("Boeing", "manufacturing", "large", "BA", "https://www.boeing.com"),
            
            # Consulting
            CompanyProfile("Accenture", "consulting", "large", "ACN", "https://www.accenture.com"),
            CompanyProfile("Deloitte", "consulting", "large", None, "https://www.deloitte.com"),
            CompanyProfile("McKinsey", "consulting", "large", None, "https://www.mckinsey.com"),
            
            # Retail
            CompanyProfile("Walmart", "retail", "large", "WMT", "https://www.walmart.com"),
            CompanyProfile("Target", "retail", "large", "TGT", "https://www.target.com"),
            CompanyProfile("Home Depot", "retail", "large", "HD", "https://www.homedepot.com"),
        ]
        
        # Common URL patterns for strategic documents
        self.doc_url_patterns = [
            "/about/code-of-conduct",
            "/about/ethics",
            "/governance/code-of-conduct",
            "/compliance/code-of-conduct",
            "/about/values",
            "/about/mission",
            "/about/purpose",
            "/investors/governance",
            "/sustainability",
            "/responsibility",
            "/careers/values",
            "/company/values",
            "/our-company/values",
            "/our-company/mission",
        ]

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def fetch_page(self, url: str) -> Optional[str]:
        """Fetch a web page with error handling"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    console.print(f"⚠️ HTTP {response.status} for {url}")
                    return None
        except Exception as e:
            console.print(f"❌ Error fetching {url}: {e}")
            return None

    async def find_strategic_document_urls(self, company: CompanyProfile) -> List[str]:
        """Find potential strategic document URLs for a company"""
        candidate_urls = []
        
        # Try common patterns
        for pattern in self.doc_url_patterns:
            url = urljoin(company.website, pattern)
            candidate_urls.append(url)
        
        # Also try to scrape the main site for relevant links
        main_page = await self.fetch_page(company.website)
        if main_page:
            soup = BeautifulSoup(main_page, 'html.parser')
            
            # Look for links containing strategic keywords
            strategic_keywords = [
                'code of conduct', 'ethics', 'values', 'mission', 'purpose',
                'governance', 'compliance', 'responsibility', 'culture'
            ]
            
            for link in soup.find_all('a', href=True):
                href = link.get('href', '').lower()
                text = link.get_text().lower()
                
                if any(keyword in href or keyword in text for keyword in strategic_keywords):
                    full_url = urljoin(company.website, link['href'])
                    if full_url not in candidate_urls:
                        candidate_urls.append(full_url)
        
        return candidate_urls[:10]  # Limit to avoid overwhelming

    async def extract_strategic_content(self, url: str, company: CompanyProfile) -> Optional[StrategicDocument]:
        """Extract strategic document content from a URL"""
        html = await self.fetch_page(url)
        if not html:
            return None
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Extract title
        title = ""
        if soup.title:
            title = soup.title.string.strip()
        
        # Extract main content
        content_selectors = [
            'main', 'article', '.content', '.main-content', 
            '#content', '#main', '.page-content', '.document-content'
        ]
        
        content = ""
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                content = elements[0].get_text(strip=True, separator='\n')
                break
        
        if not content:
            # Fallback to body content
            if soup.body:
                content = soup.body.get_text(strip=True, separator='\n')
        
        # Clean up content
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        
        if len(content) < 500:  # Too short, probably not a strategic document
            return None
        
        # Determine document type
        doc_type = self.classify_document_type(title, content, url)
        
        return StrategicDocument(
            company=company.name,
            doc_type=doc_type,
            title=title,
            content=content[:5000],  # Limit content length
            url=url,
            industry=company.industry,
            company_size=company.size
        )

    def classify_document_type(self, title: str, content: str, url: str) -> str:
        """Classify the type of strategic document"""
        title_lower = title.lower()
        content_lower = content.lower()
        url_lower = url.lower()
        
        if any(term in title_lower or term in url_lower for term in ['code of conduct', 'ethics', 'compliance']):
            return 'code_of_conduct'
        elif any(term in title_lower or term in url_lower for term in ['mission', 'vision', 'purpose']):
            return 'mission_vision'
        elif any(term in title_lower or term in url_lower for term in ['values', 'principles']):
            return 'values'
        elif any(term in content_lower[:1000] for term in ['strategic plan', 'strategy', 'objectives']):
            return 'strategic_plan'
        else:
            return 'general_strategic'

    async def analyze_document_patterns(self, documents: List[StrategicDocument]) -> Dict[str, Any]:
        """Use AI to analyze patterns in real strategic documents"""
        
        # Group documents by type and industry
        by_type = {}
        by_industry = {}
        
        for doc in documents:
            if doc.doc_type not in by_type:
                by_type[doc.doc_type] = []
            by_type[doc.doc_type].append(doc)
            
            if doc.industry not in by_industry:
                by_industry[doc.industry] = []
            by_industry[doc.industry].append(doc)
        
        console.print(f"📊 Analyzing {len(documents)} documents across {len(by_industry)} industries")
        
        analysis_prompt = f"""
        Analyze these real strategic documents from major corporations and extract key patterns:

        DOCUMENT SUMMARY:
        - Total documents: {len(documents)}
        - Industries: {list(by_industry.keys())}
        - Document types: {list(by_type.keys())}

        SAMPLE DOCUMENTS:
        {self._format_documents_for_analysis(documents[:10])}

        Please provide:
        1. LANGUAGE PATTERNS by industry (formal vs casual, technical terms, regulatory language)
        2. STRUCTURAL PATTERNS (common sections, organization, length)
        3. INDUSTRY-SPECIFIC TERMINOLOGY that should be included
        4. CULTURAL INDICATORS (values, principles, behavioral expectations)
        5. COMPLIANCE ELEMENTS (regulatory requirements, legal language)

        Format as structured analysis for improving synthetic document generation.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert in corporate communication and strategic document analysis. Provide detailed pattern analysis."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            return {
                "analysis": response.choices[0].message.content,
                "document_count": len(documents),
                "industries": list(by_industry.keys()),
                "doc_types": list(by_type.keys()),
                "by_industry": {k: len(v) for k, v in by_industry.items()},
                "by_type": {k: len(v) for k, v in by_type.items()}
            }
            
        except Exception as e:
            console.print(f"⚠️ Error analyzing documents: {e}")
            return {"error": str(e)}

    def _format_documents_for_analysis(self, documents: List[StrategicDocument]) -> str:
        """Format documents for AI analysis"""
        formatted = []
        for doc in documents:
            formatted.append(f"""
Company: {doc.company} ({doc.industry})
Type: {doc.doc_type}
Title: {doc.title}
Content Preview: {doc.content[:500]}...
URL: {doc.url}
---""")
        return "\n".join(formatted)

    async def scrape_company_documents(self, company: CompanyProfile) -> List[StrategicDocument]:
        """Scrape all strategic documents for a company"""
        console.print(f"🔍 Scraping documents for {company.name} ({company.industry})")
        
        urls = await self.find_strategic_document_urls(company)
        documents = []
        
        for url in urls:
            doc = await self.extract_strategic_content(url, company)
            if doc:
                documents.append(doc)
                console.print(f"✅ Found {doc.doc_type}: {doc.title[:50]}...")
        
        console.print(f"📄 Found {len(documents)} documents for {company.name}")
        return documents

    async def scrape_all_companies(self) -> List[StrategicDocument]:
        """Scrape documents from all target companies"""
        all_documents = []
        
        for company in track(self.target_companies, description="Scraping companies..."):
            documents = await self.scrape_company_documents(company)
            all_documents.extend(documents)
            
            # Small delay to be respectful
            await asyncio.sleep(2)
        
        return all_documents

    async def save_scraped_documents(self, documents: List[StrategicDocument], output_dir: Path):
        """Save scraped documents and analysis"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save individual documents
        docs_dir = output_dir / "scraped_documents"
        docs_dir.mkdir(exist_ok=True)
        
        for i, doc in enumerate(documents):
            filename = f"{doc.company.replace(' ', '_').lower()}_{doc.doc_type}_{i}.json"
            doc_data = {
                "company": doc.company,
                "industry": doc.industry,
                "company_size": doc.company_size,
                "doc_type": doc.doc_type,
                "title": doc.title,
                "content": doc.content,
                "url": doc.url,
                "scraped_at": "2025-09-13"
            }
            
            with open(docs_dir / filename, 'w') as f:
                json.dump(doc_data, f, indent=2)
        
        # Analyze patterns
        analysis = await self.analyze_document_patterns(documents)
        
        # Save analysis
        with open(output_dir / "real_document_analysis.json", 'w') as f:
            json.dump(analysis, f, indent=2)
        
        # Save summary
        summary = {
            "total_documents": len(documents),
            "companies_scraped": len(set(doc.company for doc in documents)),
            "industries": list(set(doc.industry for doc in documents)),
            "document_types": list(set(doc.doc_type for doc in documents)),
            "scraping_date": "2025-09-13",
            "documents_by_company": {
                company: len([d for d in documents if d.company == company])
                for company in set(doc.company for doc in documents)
            }
        }
        
        with open(output_dir / "scraping_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        console.print(f"💾 Saved {len(documents)} documents to {output_dir}")
        return analysis

@click.command()
@click.option('--output-dir', default='scraped_real_docs', help='Output directory for scraped documents')
@click.option('--max-companies', default=20, help='Maximum number of companies to scrape')
def main(output_dir, max_companies):
    """Scrape real strategic documents from major corporations"""
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        console.print("❌ OPENAI_API_KEY required")
        return
    
    console.print("🌐 [bold blue]Real Strategic Document Scraper[/bold blue]")
    console.print("=" * 60)
    console.print("Scraping authentic strategic documents from major corporations")
    console.print("Target industries: Technology, Healthcare, Finance, Manufacturing, Consulting, Retail")
    console.print()
    
    async def run_scraping():
        async with RealDocumentScraper(api_key) as scraper:
            # Limit companies if specified
            scraper.target_companies = scraper.target_companies[:max_companies]
            
            # Scrape documents
            documents = await scraper.scrape_all_companies()
            
            # Save and analyze
            output_path = Path(output_dir)
            analysis = await scraper.save_scraped_documents(documents, output_path)
            
            console.print(f"\n🎉 [green]Scraping Complete![/green]")
            console.print(f"📄 Total documents: {len(documents)}")
            console.print(f"🏢 Companies: {len(set(doc.company for doc in documents))}")
            console.print(f"🏭 Industries: {len(set(doc.industry for doc in documents))}")
            console.print(f"📊 Analysis saved to: {output_path}")
            
            return documents, analysis
    
    return asyncio.run(run_scraping())

if __name__ == "__main__":
    main()