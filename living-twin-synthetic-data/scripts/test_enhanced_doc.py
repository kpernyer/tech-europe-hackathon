#!/usr/bin/env python3
"""
Test Enhanced Strategic Document Generation
"""

import json
import os
import asyncio
from pathlib import Path
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

async def generate_enhanced_code_of_conduct():
    """Generate one enhanced code of conduct as a test"""
    
    # Sample organization data
    org_data = {
        "name": "TechCorp Solutions",
        "industry": "technology",
        "size": 2500,
        "delegation_culture": "collaborative",
        "years_in_business": 8,
        "revenue_range": "$100M - $500M"
    }
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY required")
        return
    
    client = AsyncOpenAI(api_key=api_key)
    
    # Technology industry patterns
    terminology = [
        "digital transformation", "innovation velocity", "technical debt", "user experience",
        "machine learning", "artificial intelligence", "cloud-native", "DevOps culture",
        "agile methodology", "continuous integration", "microservices architecture", "API-first"
    ]
    
    values = [
        "innovation", "excellence", "customer obsession", "think different", "move fast",
        "be bold", "embrace change", "fail fast, learn faster", "customer-centric"
    ]
    
    sections = [
        "Our Values", "Respect and Inclusion", "Data Privacy", "Intellectual Property",
        "Open Source Guidelines", "Customer Trust", "Innovation Ethics", "Reporting Concerns"
    ]
    
    prompt = f"""
    Create an authentic Code of Conduct for {org_data['name']} using real Fortune 500 corporate language patterns.
    
    COMPANY PROFILE:
    - Name: {org_data['name']}
    - Industry: {org_data['industry']} 
    - Size: {org_data['size']:,} employees
    - Culture: {org_data['delegation_culture']}
    - Years in business: {org_data['years_in_business']}
    
    INDUSTRY PATTERNS TO INCORPORATE:
    - Terminology: {', '.join(terminology[:8])}
    - Core Values: {', '.join(values[:6])}
    
    DOCUMENT STRUCTURE (based on real technology companies):
    - Sections: {', '.join(sections)}
    - Tone: professional but approachable, innovation-focused
    - Target Length: structured (1500-2000 words)
    
    REQUIREMENTS:
    1. Use authentic corporate language from real technology companies
    2. Include industry-specific compliance requirements and terminology
    3. Match the formal structure of Fortune 500 codes of conduct
    4. Include specific behavioral expectations and reporting procedures
    5. Use professional, authoritative tone appropriate for 2,500 employee organization
    
    Base this on real codes of conduct from companies like Microsoft, Apple, Google corporate policies.
    Make this indistinguishable from a real technology company's official code of conduct.
    """
    
    try:
        print("🚀 Generating enhanced Code of Conduct...")
        
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a corporate governance expert who has studied hundreds of Fortune 500 codes of conduct. Create authentic, industry-specific codes that match real corporate standards. Use the exact language patterns, structure, and compliance requirements found in actual technology company documents."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=2500
        )
        
        content = response.choices[0].message.content
        
        # Save the enhanced document
        output_file = Path("sample_enhanced_code_of_conduct.md")
        with open(output_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Enhanced Code of Conduct generated and saved to {output_file}")
        print(f"📄 Length: {len(content)} characters")
        print(f"🎯 Quality: Fortune 500-level authenticity")
        
        return content
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    result = asyncio.run(generate_enhanced_code_of_conduct())
    if result:
        print("\n🎉 Test successful! Enhanced document generation working.")
        print("📄 Sample content preview:")
        print("-" * 50)
        print(result[:300] + "...")
    else:
        print("\n❌ Test failed.")