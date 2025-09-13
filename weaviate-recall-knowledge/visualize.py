#!/usr/bin/env python3
"""
Weaviate Visualization - See what's in your database
"""

import requests
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree

console = Console()

def visualize_weaviate():
    """Show what's currently in Weaviate"""
    
    console.print("👁️  WEAVIATE VISUALIZATION", style="bold cyan")
    console.print("=" * 50)
    
    base_url = "http://localhost:8080"
    
    try:
        # 1. Get Meta Information
        console.print("\n🏷️  DATABASE INFO", style="bold yellow")
        response = requests.get(f"{base_url}/v1/meta")
        if response.status_code == 200:
            meta = response.json()
            
            info_table = Table(title="Weaviate Instance Info")
            info_table.add_column("Property", style="cyan")
            info_table.add_column("Value", style="green")
            
            info_table.add_row("Version", meta.get('version', 'unknown'))
            info_table.add_row("Hostname", meta.get('hostname', 'unknown'))
            
            modules = list(meta.get('modules', {}).keys())
            info_table.add_row("Modules", ', '.join(modules) if modules else 'none')
            
            console.print(info_table)
        
        # 2. Get Schema Information
        console.print(f"\n📋 SCHEMA STRUCTURE", style="bold yellow")
        response = requests.get(f"{base_url}/v1/schema")
        if response.status_code == 200:
            schema = response.json()
            classes = schema.get('classes', [])
            
            if classes:
                for cls in classes:
                    # Create a tree for each class
                    class_tree = Tree(f"🗂️  [bold green]{cls['class']}[/bold green]")
                    class_tree.add(f"📝 Description: {cls.get('description', 'No description')}")
                    
                    vectorizer = cls.get('vectorizer', 'none')
                    class_tree.add(f"🤖 Vectorizer: {vectorizer}")
                    
                    # Properties
                    props_node = class_tree.add("🏷️  Properties:")
                    for prop in cls.get('properties', []):
                        prop_info = f"{prop['name']} ({', '.join(prop.get('dataType', []))})"
                        if 'description' in prop:
                            prop_info += f" - {prop['description']}"
                        props_node.add(prop_info)
                    
                    console.print(class_tree)
            else:
                console.print("No classes found in schema")
        
        # 3. Get Object Counts
        console.print(f"\n📊 DATA STATISTICS", style="bold yellow")
        
        # Try to get counts for each class
        response = requests.get(f"{base_url}/v1/schema")
        if response.status_code == 200:
            schema = response.json()
            classes = schema.get('classes', [])
            
            count_table = Table(title="Document Counts by Class")
            count_table.add_column("Class", style="cyan")
            count_table.add_column("Count", justify="right", style="green")
            count_table.add_column("Status", style="yellow")
            
            for cls in classes:
                class_name = cls['class']
                
                # Try to get count via GraphQL
                count_query = {
                    "query": f"""
                    {{
                        Aggregate {{
                            {class_name} {{
                                meta {{
                                    count
                                }}
                            }}
                        }}
                    }}
                    """
                }
                
                try:
                    count_response = requests.post(f"{base_url}/v1/graphql", json=count_query)
                    if count_response.status_code == 200:
                        result = count_response.json()
                        count_data = result.get('data', {}).get('Aggregate', {}).get(class_name, [])
                        if count_data:
                            count = count_data[0].get('meta', {}).get('count', 0)
                            status = "✅ Ready" if count > 0 else "📭 Empty"
                        else:
                            count = 0
                            status = "📭 Empty"
                    else:
                        count = "?"
                        status = "❓ Error"
                except:
                    count = "?"
                    status = "❓ Error"
                
                count_table.add_row(class_name, str(count), status)
            
            console.print(count_table)
        
        # 4. Show sample data if available
        console.print(f"\n🔍 SAMPLE DATA", style="bold yellow")
        
        sample_query = {
            "query": """
            {
                Get {
                    BusinessDocument(limit: 3) {
                        title
                        category
                        content
                    }
                }
            }
            """
        }
        
        response = requests.post(f"{base_url}/v1/graphql", json=sample_query)
        if response.status_code == 200:
            result = response.json()
            docs = result.get('data', {}).get('Get', {}).get('BusinessDocument', [])
            
            if docs:
                console.print(f"📄 Sample BusinessDocument entries:")
                for i, doc in enumerate(docs, 1):
                    content_preview = doc.get('content', '')[:100] + "..." if len(doc.get('content', '')) > 100 else doc.get('content', '')
                    
                    doc_panel = Panel(
                        f"[bold]{doc.get('title', 'No title')}[/bold]\n"
                        f"Category: {doc.get('category', 'No category')}\n"
                        f"Content: {content_preview}",
                        title=f"Document {i}",
                        border_style="blue"
                    )
                    console.print(doc_panel)
            else:
                console.print("📭 No BusinessDocument entries found")
        
        # 5. Web Interface Links
        console.print(f"\n🌐 WEB INTERFACES", style="bold yellow")
        
        links_table = Table(title="Available Web Interfaces")
        links_table.add_column("Interface", style="cyan")
        links_table.add_column("URL", style="green")
        links_table.add_column("Purpose", style="yellow")
        
        links_table.add_row("Weaviate Console", "http://localhost:8080/v1/console", "Browse data visually")
        links_table.add_row("GraphQL Playground", "http://localhost:8080/v1/graphql", "Run queries interactively")
        links_table.add_row("REST API Explorer", "http://localhost:8080/v1/meta", "API documentation")
        
        console.print(links_table)
        
        console.print(f"\n💡 [bold green]Tip:[/bold green] Open http://localhost:8080/v1/console in your browser for a visual interface!")
        
        return True
        
    except requests.exceptions.ConnectionError:
        console.print("❌ Cannot connect to Weaviate", style="red")
        return False
    except Exception as e:
        console.print(f"❌ Visualization failed: {e}", style="red")
        return False

if __name__ == "__main__":
    visualize_weaviate()