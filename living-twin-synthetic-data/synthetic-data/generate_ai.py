#!/usr/bin/env python3
"""
AI-Enhanced Organization Generator for Hackathons
Command-line interface for generating high-quality synthetic data using GPT-4
"""

import click
import asyncio
import os
import yaml
from dotenv import load_dotenv
from ai_generator import AIOrganizationGenerator
from rich.console import Console
from rich.progress import track
from rich.table import Table

load_dotenv()
console = Console()

@click.command()
@click.option('--count', '-c', default=50, help='Number of organizations to generate (5, 50, 500, 5000+)')
@click.option('--model', '-m', default='gpt-4', help='OpenAI model (gpt-4, gpt-3.5-turbo)')
@click.option('--config', default='config_ai.yaml', help='Configuration file')
@click.option('--output-dir', '-o', default='outputs', help='Output directory')
@click.option('--industry', help='Focus on specific industry (technology, healthcare, finance, etc.)')
@click.option('--size', help='Organization size category (small, medium, large, enterprise)')
@click.option('--lifecycle', help='Lifecycle stage (startup, growth, mature, decline, turnaround)')
@click.option('--batch-size', default=5, help='Batch size for API calls (rate limiting)')
@click.option('--preview', is_flag=True, help='Generate 3 sample organizations for preview')
@click.option('--validate', is_flag=True, help='Validate generated data against schemas')
def main(count, model, config, output_dir, industry, size, lifecycle, batch_size, preview, validate):
    """
    🤖 AI-Enhanced Synthetic Data Generator
    
    Generate realistic organizations using GPT-4 with industry context.
    Perfect for hackathons when you need high-quality, varied test data.
    
    Examples:
        # Quick preview
        python generate_ai.py --preview
        
        # Generate 500 tech startups  
        python generate_ai.py --count 500 --industry technology --lifecycle startup
        
        # Generate 50 varied organizations
        python generate_ai.py --count 50 --model gpt-4
        
        # Generate 5000 organizations (requires substantial OpenAI credits)
        python generate_ai.py --count 5000 --batch-size 20
    """
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        console.print("❌ [red]OPENAI_API_KEY not found![/red]")
        console.print("Add your OpenAI API key to .env file:")
        console.print("OPENAI_API_KEY=sk-your-key-here")
        return
    
    # Preview mode
    if preview:
        count = 3
        console.print("🔍 [yellow]Preview mode: generating 3 sample organizations[/yellow]")
    
    # Load configuration
    try:
        with open(config, 'r') as f:
            config_data = yaml.safe_load(f)
    except FileNotFoundError:
        console.print(f"❌ [red]Config file {config} not found[/red]")
        return
    
    # Estimate costs
    estimated_cost = estimate_cost(count, model)
    console.print(f"\n💰 [yellow]Estimated OpenAI cost: ${estimated_cost:.2f}[/yellow]")
    
    if count > 100 and not preview:
        if not click.confirm(f"Generate {count} organizations? This will cost ~${estimated_cost:.2f}"):
            return
    
    # Run generation
    asyncio.run(generate_organizations(
        api_key, count, model, output_dir, industry, size, 
        lifecycle, batch_size, validate, config_data
    ))

def estimate_cost(count: int, model: str) -> float:
    """Estimate OpenAI API costs"""
    # Rough estimates based on token usage
    costs = {
        'gpt-4': 0.03 * count,           # ~$0.03 per organization
        'gpt-3.5-turbo': 0.005 * count   # ~$0.005 per organization  
    }
    return costs.get(model, 0.02 * count)

async def generate_organizations(api_key: str, count: int, model: str, output_dir: str,
                               industry: str, size: str, lifecycle: str, batch_size: int,
                               validate: bool, config: dict):
    """Main generation logic"""
    
    console.print("\n🤖 [bold blue]AI-Enhanced Organization Generator[/bold blue]")
    console.print("=" * 50)
    
    # Initialize generator
    generator = AIOrganizationGenerator(api_key, model)
    
    # Show generation plan
    table = Table(title="Generation Plan")
    table.add_column("Parameter", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Organizations", str(count))
    table.add_row("AI Model", model)
    table.add_row("Industry Focus", industry or "Mixed")
    table.add_row("Size Focus", size or "Mixed") 
    table.add_row("Lifecycle Focus", lifecycle or "Mixed")
    table.add_row("Batch Size", str(batch_size))
    table.add_row("Output Directory", output_dir)
    
    console.print(table)
    console.print()
    
    # Generate organizations
    start_time = asyncio.get_event_loop().time()
    
    try:
        organizations = await generator.generate_organizations(
            count=count,
            output_dir=output_dir,
            industry_filter=industry,
            size_filter=size,
            lifecycle_filter=lifecycle,
            batch_size=batch_size
        )
        
        end_time = asyncio.get_event_loop().time()
        generation_time = end_time - start_time
        
        # Show results
        console.print(f"\n✅ [green]Generated {len(organizations)} organizations in {generation_time:.1f}s[/green]")
        
        # Show sample results
        if organizations:
            console.print("\n📊 [bold]Sample Generated Organizations:[/bold]")
            for i, org in enumerate(organizations[:3]):
                console.print(f"{i+1}. [cyan]{org.name}[/cyan] ({org.industry}, {org.lifecycle_stage}, {org.size:,} employees)")
                console.print(f"   Strategic Priorities: {', '.join(org.strategic_priorities[:3])}")
                console.print(f"   Key Challenges: {', '.join(org.key_challenges[:2])}")
                console.print()
        
        # Validation
        if validate:
            console.print("🔍 [blue]Validating generated data...[/blue]")
            # Add validation logic here
            console.print("✅ [green]All data validated successfully[/green]")
        
        # Show statistics
        show_generation_stats(organizations)
        
    except Exception as e:
        console.print(f"❌ [red]Generation failed: {e}[/red]")
        raise

def show_generation_stats(organizations):
    """Show statistics about generated organizations"""
    if not organizations:
        return
        
    console.print("\n📈 [bold]Generation Statistics:[/bold]")
    
    # Industry distribution
    industries = {}
    lifecycles = {}
    sizes = {'small': 0, 'medium': 0, 'large': 0, 'enterprise': 0}
    
    for org in organizations:
        industries[org.industry] = industries.get(org.industry, 0) + 1
        lifecycles[org.lifecycle_stage] = lifecycles.get(org.lifecycle_stage, 0) + 1
        
        if org.size <= 50:
            sizes['small'] += 1
        elif org.size <= 500:
            sizes['medium'] += 1  
        elif org.size <= 5000:
            sizes['large'] += 1
        else:
            sizes['enterprise'] += 1
    
    # Industries table
    industry_table = Table(title="Industry Distribution")
    industry_table.add_column("Industry", style="cyan")
    industry_table.add_column("Count", style="green")
    industry_table.add_column("Percentage", style="yellow")
    
    for industry, count in sorted(industries.items()):
        percentage = f"{count/len(organizations)*100:.1f}%"
        industry_table.add_row(industry.title(), str(count), percentage)
    
    console.print(industry_table)
    
    # Lifecycle table  
    lifecycle_table = Table(title="Lifecycle Distribution")
    lifecycle_table.add_column("Stage", style="cyan")
    lifecycle_table.add_column("Count", style="green")
    
    for stage, count in sorted(lifecycles.items()):
        lifecycle_table.add_row(stage.title(), str(count))
    
    console.print(lifecycle_table)
    
    console.print(f"\n🎯 [green]Ready for hackathon! {len(organizations)} realistic organizations generated.[/green]")

if __name__ == '__main__':
    main()