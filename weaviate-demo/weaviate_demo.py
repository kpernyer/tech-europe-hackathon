#!/usr/bin/env python3
"""
Weaviate Demo: Comprehensive demonstration of Weaviate's capabilities
for semantic search, vectorization strategies, and performance analysis.
"""

import asyncio
import time
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

import weaviate
from weaviate.classes.config import Configure, Property, DataType, VectorDistances
from weaviate.classes.query import Filter, MetadataQuery
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import typer

console = Console()
app = typer.Typer(help="Weaviate Demo - Semantic Search Capabilities")

@dataclass
class DemoResult:
    query: str
    results: List[Dict]
    execution_time: float
    model_used: str
    strategy: str

class WeaviateDemo:
    """
    Comprehensive Weaviate demonstration class showcasing:
    - Multiple vectorization strategies
    - Semantic search capabilities  
    - Performance comparisons
    - Real-world business scenarios
    """
    
    def __init__(self, weaviate_url: str = "http://localhost:8080"):
        self.weaviate_url = weaviate_url
        self.client = None
        self.demo_results = []
        
    def connect(self):
        """Connect to Weaviate instance"""
        try:
            # Use HTTP client for local connection with startup checks disabled
            self.client = weaviate.connect_to_local(
                host="localhost",
                port=8080,
                skip_init_checks=True
            )
            console.print("✅ Connected to Weaviate", style="green")
            return True
        except Exception as e:
            console.print(f"❌ Failed to connect to Weaviate: {e}", style="red")
            return False
    
    def create_demo_schemas(self, filter_collections=None):
        """Create different schemas for testing various vectorization strategies"""
        
        schemas = [
            {
                "name": "BusinessDoc_OpenAI",
                "description": "Business documents with OpenAI embeddings",
                "vectorizer": Configure.Vectorizer.text2vec_openai(model="text-embedding-3-large"),
                "properties": [
                    Property(name="title", data_type=DataType.TEXT),
                    Property(name="content", data_type=DataType.TEXT),
                    Property(name="category", data_type=DataType.TEXT),
                    Property(name="domain", data_type=DataType.TEXT),
                ]
            },
            {
                "name": "BusinessDoc_HuggingFace",
                "description": "Business documents with HuggingFace embeddings",
                "vectorizer": Configure.Vectorizer.text2vec_huggingface(
                    model="sentence-transformers/all-MiniLM-L6-v2"
                ),
                "properties": [
                    Property(name="title", data_type=DataType.TEXT),
                    Property(name="content", data_type=DataType.TEXT),
                    Property(name="category", data_type=DataType.TEXT),
                    Property(name="domain", data_type=DataType.TEXT),
                ]
            },
            {
                "name": "CodeDoc_OpenAI",
                "description": "Programming and code documentation with OpenAI's best embedding model",
                "vectorizer": Configure.Vectorizer.text2vec_openai(model="text-embedding-3-large"),
                "properties": [
                    Property(name="title", data_type=DataType.TEXT),
                    Property(name="content", data_type=DataType.TEXT),
                    Property(name="language", data_type=DataType.TEXT),
                    Property(name="framework", data_type=DataType.TEXT),
                    Property(name="complexity", data_type=DataType.TEXT),
                ]
            }
        ]
        
        created_schemas = []
        for schema in schemas:
            # Filter collections if specified
            if filter_collections and schema["name"] not in filter_collections:
                continue
                
            try:
                # Delete existing collection if it exists
                if self.client.collections.exists(schema["name"]):
                    self.client.collections.delete(schema["name"])
                    console.print(f"🗑️  Deleted existing collection: {schema['name']}")
                
                # Create new collection
                collection = self.client.collections.create(
                    name=schema["name"],
                    description=schema["description"],
                    properties=schema["properties"],
                    vectorizer_config=schema["vectorizer"],
                    vector_index_config=Configure.VectorIndex.hnsw(
                        distance_metric=VectorDistances.COSINE,
                        dynamic_ef_factor=8,
                        dynamic_ef_max=500,
                        ef_construction=128,
                        max_connections=32,
                        vector_cache_max_objects=100000
                    )
                )
                
                created_schemas.append(schema["name"])
                console.print(f"✅ Created collection: {schema['name']}", style="green")
                
            except Exception as e:
                console.print(f"❌ Failed to create {schema['name']}: {e}", style="red")
        
        return created_schemas
    
    def get_sample_business_data(self) -> List[Dict]:
        """Generate comprehensive sample business data for testing"""
        return [
            {
                "title": "Customer Retention Strategies for SaaS Companies",
                "content": """
                Customer retention is crucial for SaaS businesses, directly impacting lifetime value and growth.
                Key strategies include onboarding optimization, proactive customer success, feature adoption tracking,
                and churn prediction analytics. Companies should focus on user engagement metrics, provide
                excellent customer support, and continuously gather feedback for product improvements.
                Successful retention programs can increase revenue by 25-95% while reducing acquisition costs.
                """,
                "category": "Business Strategy",
                "domain": "SaaS",
                "metadata": {"author": "Strategy Team", "date": "2024-01-15", "priority": "high"}
            },
            {
                "title": "Digital Marketing ROI Analysis Framework",
                "content": """
                Measuring digital marketing ROI requires comprehensive tracking across channels and touchpoints.
                Attribution models should account for multi-touch customer journeys, considering first-touch,
                last-touch, and linear attribution. Key metrics include customer acquisition cost (CAC),
                lifetime value (LTV), conversion rates, and channel-specific performance indicators.
                Advanced analytics can reveal optimization opportunities and budget allocation strategies.
                """,
                "category": "Marketing Analytics", 
                "domain": "Digital Marketing",
                "metadata": {"author": "Marketing Team", "date": "2024-02-01", "priority": "medium"}
            },
            {
                "title": "AI Implementation Best Practices for Enterprises",
                "content": """
                Enterprise AI implementation requires strategic planning, stakeholder alignment, and phased rollouts.
                Success factors include data quality assessment, infrastructure readiness, talent acquisition,
                and change management. Organizations should start with pilot projects, establish governance frameworks,
                and focus on measurable business outcomes. Common pitfalls include insufficient data preparation,
                lack of executive sponsorship, and unrealistic timeline expectations.
                """,
                "category": "Technology Strategy",
                "domain": "Artificial Intelligence", 
                "metadata": {"author": "Tech Team", "date": "2024-02-15", "priority": "high"}
            },
            {
                "title": "Financial Planning and Analysis Automation",
                "content": """
                FP&A automation transforms financial planning through predictive modeling and real-time reporting.
                Modern solutions integrate ERP systems, provide scenario modeling capabilities, and enable
                collaborative budgeting processes. Benefits include reduced cycle times, improved accuracy,
                and enhanced strategic insights. Implementation requires data standardization, process redesign,
                and comprehensive user training for maximum adoption and ROI.
                """,
                "category": "Financial Operations",
                "domain": "Finance",
                "metadata": {"author": "Finance Team", "date": "2024-01-30", "priority": "medium"}
            },
            {
                "title": "Supply Chain Resilience in Global Markets",
                "content": """
                Building supply chain resilience requires diversification, visibility, and adaptive strategies.
                Companies should implement multi-supplier networks, invest in real-time monitoring systems,
                and develop contingency plans for disruptions. Risk management approaches include geographic
                diversification, inventory optimization, and strategic partnerships. Technology solutions
                like IoT sensors and AI-powered analytics enhance supply chain transparency and responsiveness.
                """,
                "category": "Operations Management",
                "domain": "Supply Chain",
                "metadata": {"author": "Operations Team", "date": "2024-02-10", "priority": "high"}
            },
            {
                "title": "Employee Engagement and Remote Work Productivity",
                "content": """
                Remote work success depends on engagement strategies, communication tools, and performance management.
                Key factors include regular check-ins, goal alignment, virtual team building, and flexible work arrangements.
                Technology infrastructure should support collaboration, with emphasis on security and accessibility.
                Measuring productivity requires outcome-based metrics rather than time tracking, focusing on
                deliverables and impact rather than hours worked.
                """,
                "category": "Human Resources",
                "domain": "Workplace Management",
                "metadata": {"author": "HR Team", "date": "2024-01-20", "priority": "medium"}
            },
            {
                "title": "Cybersecurity Risk Assessment Methodology",
                "content": """
                Comprehensive cybersecurity risk assessment involves threat identification, vulnerability analysis,
                and impact evaluation. Organizations should conduct regular penetration testing, implement
                continuous monitoring, and maintain incident response plans. Risk mitigation strategies include
                employee training, access controls, encryption, and security awareness programs.
                Compliance frameworks like ISO 27001 and NIST provide structured approaches to security management.
                """,
                "category": "Information Security",
                "domain": "Cybersecurity",
                "metadata": {"author": "Security Team", "date": "2024-02-05", "priority": "high"}
            },
            {
                "title": "Sustainable Business Practices and ESG Reporting",
                "content": """
                ESG (Environmental, Social, Governance) initiatives drive sustainable business growth and stakeholder value.
                Implementation requires materiality assessments, goal setting, and transparent reporting mechanisms.
                Environmental efforts focus on carbon reduction, waste management, and resource efficiency.
                Social initiatives emphasize diversity, community impact, and employee wellbeing.
                Governance improvements include ethical practices, board diversity, and stakeholder engagement.
                """,
                "category": "Corporate Responsibility",
                "domain": "Sustainability",
                "metadata": {"author": "CSR Team", "date": "2024-01-25", "priority": "medium"}
            }
        ]
    
    def get_sample_programming_data(self) -> List[Dict]:
        """Generate comprehensive sample programming data optimized for OpenAI embeddings"""
        return [
            {
                "title": "Advanced Python Async Programming Patterns",
                "content": """
                Modern Python async programming leverages asyncio, async/await syntax, and concurrent.futures
                for high-performance I/O bound applications. Key patterns include async context managers,
                async generators, and proper exception handling in async functions. Best practices involve
                using asyncio.gather() for concurrent operations, implementing proper cancellation with
                asyncio.CancelledError, and avoiding blocking operations in async functions.
                Advanced patterns include async iterators, async comprehensions, and custom event loops.
                """,
                "language": "Python",
                "framework": "asyncio",
                "complexity": "Advanced",
                "metadata": {"author": "Python Team", "date": "2024-01-15", "tags": ["async", "concurrency", "performance"]}
            },
            {
                "title": "React Server Components and Next.js 14 Architecture",
                "content": """
                React Server Components revolutionize full-stack development by enabling server-side rendering
                with component-level granularity. Next.js 14 implements this through the App Router, allowing
                seamless mixing of server and client components. Key concepts include streaming, suspense
                boundaries, and progressive enhancement. Server components can directly access databases,
                while client components handle interactivity. This architecture reduces bundle size and
                improves performance through selective hydration and server-side data fetching.
                """,
                "language": "JavaScript",
                "framework": "React/Next.js",
                "complexity": "Advanced",
                "metadata": {"author": "Frontend Team", "date": "2024-02-01", "tags": ["react", "ssr", "performance"]}
            },
            {
                "title": "Rust Memory Safety and Zero-Cost Abstractions",
                "content": """
                Rust's ownership system provides memory safety without garbage collection through compile-time
                checks. The borrow checker ensures no data races, dangling pointers, or memory leaks.
                Zero-cost abstractions mean high-level constructs compile to efficient machine code.
                Key concepts include ownership, borrowing, lifetimes, and trait bounds. Advanced patterns
                include smart pointers (Box, Rc, Arc), interior mutability with RefCell, and unsafe code
                for system programming. Rust excels in systems programming, web assembly, and performance-critical applications.
                """,
                "language": "Rust",
                "framework": "Standard Library",
                "complexity": "Expert",
                "metadata": {"author": "Systems Team", "date": "2024-02-15", "tags": ["memory-safety", "performance", "systems"]}
            },
            {
                "title": "Machine Learning Pipeline with PyTorch and HuggingFace",
                "content": """
                Modern ML pipelines integrate PyTorch for model development with HuggingFace Transformers
                for pre-trained models. Key components include data preprocessing with torchvision,
                model training with custom loss functions, and deployment with TorchScript or ONNX.
                Advanced techniques include gradient accumulation, mixed precision training, and
                distributed training with PyTorch DDP. HuggingFace provides tokenizers, model hubs,
                and evaluation metrics. Best practices include proper data splitting, hyperparameter
                tuning, and model versioning with MLflow or Weights & Biases.
                """,
                "language": "Python",
                "framework": "PyTorch/HuggingFace",
                "complexity": "Advanced",
                "metadata": {"author": "ML Team", "date": "2024-01-30", "tags": ["ml", "nlp", "transformers"]}
            },
            {
                "title": "Kubernetes Operator Development with Go",
                "content": """
                Kubernetes operators extend the API using custom resources and controllers written in Go.
                The operator pattern automates application lifecycle management through declarative APIs.
                Key components include Custom Resource Definitions (CRDs), controllers with informers,
                and reconciliation loops. Development involves using controller-runtime, kubebuilder,
                or operator-sdk for scaffolding. Advanced patterns include finalizers, owner references,
                and admission webhooks. Operators enable GitOps workflows and infrastructure as code
                for complex distributed systems.
                """,
                "language": "Go",
                "framework": "Kubernetes",
                "complexity": "Expert",
                "metadata": {"author": "DevOps Team", "date": "2024-02-10", "tags": ["kubernetes", "operators", "automation"]}
            },
            {
                "title": "GraphQL Schema Design and Federation",
                "content": """
                GraphQL federation enables distributed schema composition across microservices.
                Schema stitching combines multiple GraphQL APIs into a unified endpoint.
                Key concepts include type extensions, field resolvers, and data loaders for
                efficient data fetching. Advanced patterns include schema federation with
                Apollo Federation, custom directives, and subscription handling.
                Best practices include proper error handling, query complexity analysis,
                and caching strategies. GraphQL provides type safety, introspection,
                and real-time subscriptions for modern API development.
                """,
                "language": "JavaScript",
                "framework": "GraphQL",
                "complexity": "Advanced",
                "metadata": {"author": "API Team", "date": "2024-01-20", "tags": ["graphql", "api", "microservices"]}
            },
            {
                "title": "WebAssembly Performance Optimization",
                "content": """
                WebAssembly (WASM) enables near-native performance in web browsers through
                a binary instruction format. Optimization techniques include minimizing
                memory allocations, using SIMD instructions, and proper module instantiation.
                Key concepts include linear memory, tables, and the JavaScript API.
                Advanced patterns include multi-threading with SharedArrayBuffer,
                streaming compilation, and integration with Web Workers.
                WASM excels in computational tasks, game engines, and performance-critical
                web applications. Tools like Emscripten and wasm-pack simplify development.
                """,
                "language": "WebAssembly",
                "framework": "WASM",
                "complexity": "Expert",
                "metadata": {"author": "Performance Team", "date": "2024-02-05", "tags": ["wasm", "performance", "web"]}
            },
            {
                "title": "Distributed Systems with Event Sourcing and CQRS",
                "content": """
                Event sourcing stores state changes as a sequence of events, enabling
                temporal queries and audit trails. CQRS (Command Query Responsibility Segregation)
                separates read and write models for scalability. Key patterns include
                event stores, projections, and saga orchestration. Advanced concepts
                include eventual consistency, conflict resolution, and event replay.
                Implementation involves message queues (Kafka, RabbitMQ), event stores
                (EventStore, Apache Pulsar), and projection engines. This architecture
                supports complex business workflows and provides strong audit capabilities.
                """,
                "language": "Multiple",
                "framework": "Event-Driven Architecture",
                "complexity": "Expert",
                "metadata": {"author": "Architecture Team", "date": "2024-01-25", "tags": ["events", "cqrs", "distributed"]}
            }
        ]
    
    def load_data_to_collections(self, collections: List[str]):
        """Load sample data to all collections for comparison"""
        
        for collection_name in collections:
            try:
                collection = self.client.collections.get(collection_name)
                
                # Choose appropriate data based on collection type
                if "CodeDoc" in collection_name:
                    sample_data = self.get_sample_programming_data()
                    console.print(f"📚 Loading programming data to {collection_name}...")
                else:
                    sample_data = self.get_sample_business_data()
                    console.print(f"📊 Loading business data to {collection_name}...")
                
                # Batch insert data
                with console.status(f"Loading data to {collection_name}..."):
                    uuids = collection.data.insert_many(sample_data)
                
                console.print(f"✅ Loaded {len(uuids)} documents to {collection_name}", style="green")
                
            except Exception as e:
                console.print(f"❌ Failed to load data to {collection_name}: {e}", style="red")
    
    def semantic_search_demo(self, collection_name: str, queries: List[str]) -> List[DemoResult]:
        """Demonstrate semantic search capabilities"""
        results = []
        collection = self.client.collections.get(collection_name)
        
        for query in queries:
            try:
                start_time = time.time()
                
                response = collection.query.near_text(
                    query=query,
                    limit=5,
                    return_metadata=MetadataQuery(distance=True, certainty=True)
                )
                
                execution_time = time.time() - start_time
                
                search_results = []
                for obj in response.objects:
                    search_results.append({
                        'id': str(obj.uuid),
                        'title': obj.properties.get('title', ''),
                        'category': obj.properties.get('category', ''),
                        'domain': obj.properties.get('domain', ''),
                        'certainty': obj.metadata.certainty if obj.metadata else 0.0,
                        'distance': obj.metadata.distance if obj.metadata else 1.0
                    })
                
                results.append(DemoResult(
                    query=query,
                    results=search_results,
                    execution_time=execution_time,
                    model_used=collection_name.split('_')[1],
                    strategy="semantic_search"
                ))
                
            except Exception as e:
                console.print(f"❌ Search failed for '{query}': {e}", style="red")
        
        return results
    
    def hybrid_search_demo(self, collection_name: str, queries: List[str]) -> List[DemoResult]:
        """Demonstrate hybrid search (vector + keyword)"""
        results = []
        collection = self.client.collections.get(collection_name)
        
        for query in queries:
            try:
                start_time = time.time()
                
                # Hybrid search with alpha=0.7 (70% vector, 30% keyword)
                response = collection.query.hybrid(
                    query=query,
                    alpha=0.7,
                    limit=5,
                    return_metadata=MetadataQuery(score=True, explain_score=True)
                )
                
                execution_time = time.time() - start_time
                
                search_results = []
                for obj in response.objects:
                    search_results.append({
                        'id': str(obj.uuid),
                        'title': obj.properties.get('title', ''),
                        'category': obj.properties.get('category', ''),
                        'domain': obj.properties.get('domain', ''),
                        'score': obj.metadata.score if obj.metadata else 0.0,
                        'explanation': obj.metadata.explain_score if obj.metadata else None
                    })
                
                results.append(DemoResult(
                    query=query,
                    results=search_results,
                    execution_time=execution_time,
                    model_used=collection_name.split('_')[1],
                    strategy="hybrid_search"
                ))
                
            except Exception as e:
                console.print(f"❌ Hybrid search failed for '{query}': {e}", style="red")
        
        return results
    
    def performance_comparison(self, collections: List[str], test_queries: List[str]):
        """Compare performance across different vectorization strategies"""
        
        console.print("\n🔥 Performance Comparison Across Vectorization Strategies", style="bold cyan")
        
        all_results = {}
        
        for collection_name in collections:
            console.print(f"\n📊 Testing {collection_name}...")
            
            # Test semantic search
            semantic_results = self.semantic_search_demo(collection_name, test_queries)
            
            # Test hybrid search  
            hybrid_results = self.hybrid_search_demo(collection_name, test_queries)
            
            all_results[collection_name] = {
                'semantic': semantic_results,
                'hybrid': hybrid_results
            }
        
        # Display performance comparison table
        self.display_performance_table(all_results, test_queries)
        
        return all_results
    
    def display_performance_table(self, results: Dict, queries: List[str]):
        """Display performance comparison in a rich table"""
        
        table = Table(title="Weaviate Performance Comparison")
        table.add_column("Model", style="cyan")
        table.add_column("Strategy", style="magenta")
        table.add_column("Query", style="green")
        table.add_column("Avg Time (ms)", justify="right")
        table.add_column("Results Found", justify="right")
        table.add_column("Avg Certainty", justify="right")
        
        for collection_name, strategies in results.items():
            model = collection_name.split('_')[1]
            
            for strategy_name, strategy_results in strategies.items():
                if not strategy_results:
                    continue
                    
                avg_time = sum(r.execution_time for r in strategy_results) / len(strategy_results) * 1000
                total_results = sum(len(r.results) for r in strategy_results)
                
                # Calculate average certainty/score
                all_scores = []
                for r in strategy_results:
                    for result in r.results:
                        score = result.get('certainty', result.get('score', 0))
                        if score:
                            all_scores.append(score)
                
                avg_certainty = sum(all_scores) / len(all_scores) if all_scores else 0
                
                table.add_row(
                    model,
                    strategy_name,
                    f"{len(queries)} queries",
                    f"{avg_time:.1f}",
                    str(total_results),
                    f"{avg_certainty:.3f}"
                )
        
        console.print(table)
    
    def detailed_query_analysis(self, results: Dict, query_index: int = 0):
        """Analyze results for a specific query in detail"""
        
        if not results:
            return
        
        # Get the first query from results
        first_collection = list(results.keys())[0]
        first_strategy = list(results[first_collection].keys())[0]
        
        if query_index >= len(results[first_collection][first_strategy]):
            return
            
        query = results[first_collection][first_strategy][query_index].query
        
        console.print(f"\n🔍 Detailed Analysis for Query: '{query}'", style="bold yellow")
        
        for collection_name, strategies in results.items():
            model = collection_name.split('_')[1]
            console.print(f"\n📋 {model} Model Results:", style="bold blue")
            
            for strategy_name, strategy_results in strategies.items():
                if query_index < len(strategy_results):
                    result = strategy_results[query_index]
                    
                    console.print(f"\n  🎯 {strategy_name.upper()}:")
                    console.print(f"    ⏱️  Execution time: {result.execution_time*1000:.1f}ms")
                    console.print(f"    📊 Results found: {len(result.results)}")
                    
                    if result.results:
                        console.print("    📝 Top results:")
                        for i, res in enumerate(result.results[:3], 1):
                            score = res.get('certainty', res.get('score', 0))
                            console.print(f"      {i}. {res['title'][:60]}... (score: {score:.3f})")
    
    def close(self):
        """Close Weaviate connection"""
        if self.client:
            self.client.close()
            console.print("👋 Disconnected from Weaviate", style="yellow")

@app.command()
def full_demo(
    weaviate_url: str = typer.Option("http://localhost:8080", help="Weaviate URL"),
    include_openai: bool = typer.Option(False, help="Include OpenAI embeddings (requires API key)"),
    query_analysis: bool = typer.Option(True, help="Include detailed query analysis")
):
    """Run the complete Weaviate demonstration"""
    
    console.print("🚀 Starting Weaviate Comprehensive Demo", style="bold green")
    
    demo = WeaviateDemo(weaviate_url)
    
    if not demo.connect():
        raise typer.Exit(1)
    
    try:
        # Create schemas (skip OpenAI if not requested)
        collections_to_create = ["BusinessDoc_Transformers", "BusinessDoc_HuggingFace"]
        if include_openai:
            collections_to_create.extend(["BusinessDoc_OpenAI", "CodeDoc_OpenAI"])
        
        console.print(f"\n🏗️  Creating {len(collections_to_create)} collections...")
        created_collections = demo.create_demo_schemas()
        
        # Filter to only include successfully created collections
        active_collections = [c for c in collections_to_create if c in created_collections]
        
        if not active_collections:
            console.print("❌ No collections were created successfully", style="red")
            raise typer.Exit(1)
        
        # Load sample data
        console.print(f"\n📊 Loading sample business data...")
        demo.load_data_to_collections(active_collections)
        
        # Test queries covering different domains
        test_queries = [
            "How to improve customer retention rates?",
            "AI implementation best practices for companies",
            "Digital marketing ROI measurement strategies", 
            "Supply chain risk management approaches",
            "Cybersecurity assessment methodologies"
        ]
        
        # Programming-focused queries for OpenAI's best models
        programming_queries = [
            "How to implement async programming patterns in Python?",
            "React Server Components and Next.js architecture best practices",
            "Rust memory safety and zero-cost abstractions",
            "Machine learning pipeline optimization with PyTorch",
            "Kubernetes operator development and deployment strategies",
            "GraphQL federation and schema design patterns",
            "WebAssembly performance optimization techniques",
            "Event sourcing and CQRS in distributed systems"
        ]
        
        console.print(f"\n🔍 Running performance comparison with {len(test_queries)} queries...")
        
        # Run comprehensive performance comparison
        all_results = demo.performance_comparison(active_collections, test_queries)
        
        # Special programming demo if OpenAI collections are available
        if include_openai and "CodeDoc_OpenAI" in active_collections:
            console.print(f"\n🚀 Running Programming-Focused Demo with OpenAI's Best Models", style="bold cyan")
            programming_results = demo.performance_comparison(["CodeDoc_OpenAI"], programming_queries)
            all_results.update(programming_results)
        
        # Detailed analysis for first query
        if query_analysis and all_results:
            demo.detailed_query_analysis(all_results, query_index=0)
        
        # Save results to file
        results_file = Path("weaviate_demo_results.json")
        with open(results_file, 'w') as f:
            # Convert results to JSON-serializable format
            json_results = {}
            for collection, strategies in all_results.items():
                json_results[collection] = {}
                for strategy, results in strategies.items():
                    json_results[collection][strategy] = [
                        {
                            'query': r.query,
                            'execution_time': r.execution_time,
                            'model_used': r.model_used,
                            'strategy': r.strategy,
                            'results_count': len(r.results),
                            'results': r.results
                        }
                        for r in results
                    ]
            
            json.dump(json_results, f, indent=2)
        
        console.print(f"\n💾 Results saved to: {results_file}", style="green")
        console.print("\n🎉 Demo completed successfully!", style="bold green")
        
    except Exception as e:
        console.print(f"❌ Demo failed: {e}", style="red")
        raise typer.Exit(1)
    
    finally:
        demo.close()

@app.command()
def programming_demo(
    weaviate_url: str = typer.Option("http://localhost:8080", help="Weaviate URL")
):
    """Run programming-focused demo with OpenAI's best embedding models"""
    
    console.print("🚀 Starting Programming-Focused Weaviate Demo", style="bold green")
    console.print("Using OpenAI's text-embedding-3-large for optimal code understanding", style="cyan")
    
    demo = WeaviateDemo(weaviate_url)
    
    if not demo.connect():
        raise typer.Exit(1)
    
    try:
        # Create only programming-focused collections
        collections_to_create = ["CodeDoc_OpenAI"]
        
        console.print(f"\n🏗️  Creating programming-focused collection...")
        created_collections = demo.create_demo_schemas(filter_collections=collections_to_create)
        
        # Filter to only include successfully created collections
        active_collections = [c for c in collections_to_create if c in created_collections]
        
        if not active_collections:
            console.print("❌ No collections were created successfully", style="red")
            raise typer.Exit(1)
        
        # Load programming data
        console.print(f"\n📚 Loading programming documentation...")
        demo.load_data_to_collections(active_collections)
        
        # Programming-focused test queries
        programming_queries = [
            "How to implement async programming patterns in Python?",
            "React Server Components and Next.js architecture best practices",
            "Rust memory safety and zero-cost abstractions",
            "Machine learning pipeline optimization with PyTorch",
            "Kubernetes operator development and deployment strategies",
            "GraphQL federation and schema design patterns",
            "WebAssembly performance optimization techniques",
            "Event sourcing and CQRS in distributed systems"
        ]
        
        console.print(f"\n🔍 Running programming-focused search with {len(programming_queries)} queries...")
        
        # Run programming-focused performance comparison
        all_results = demo.performance_comparison(active_collections, programming_queries)
        
        # Detailed analysis for first programming query
        if all_results:
            demo.detailed_query_analysis(all_results, query_index=0)
        
        # Save results to file
        results_file = Path("programming_demo_results.json")
        with open(results_file, 'w') as f:
            # Convert results to JSON-serializable format
            json_results = {}
            for collection, strategies in all_results.items():
                json_results[collection] = {}
                for strategy, results in strategies.items():
                    json_results[collection][strategy] = [
                        {
                            'query': r.query,
                            'execution_time': r.execution_time,
                            'model_used': r.model_used,
                            'strategy': r.strategy,
                            'results_count': len(r.results),
                            'results': r.results
                        }
                        for r in results
                    ]
            
            json.dump(json_results, f, indent=2)
        
        console.print(f"\n💾 Programming demo results saved to: {results_file}", style="green")
        console.print("\n🎉 Programming demo completed successfully!", style="bold green")
        
    except Exception as e:
        console.print(f"❌ Programming demo failed: {e}", style="red")
        raise typer.Exit(1)
    
    finally:
        demo.close()

@app.command()
def quick_test(
    weaviate_url: str = typer.Option("http://localhost:8080", help="Weaviate URL")
):
    """Quick connectivity and basic functionality test"""
    
    console.print("⚡ Quick Weaviate Test", style="bold cyan")
    
    demo = WeaviateDemo(weaviate_url)
    
    if demo.connect():
        console.print("✅ Weaviate is running and accessible", style="green")
        
        # Quick health check
        try:
            is_ready = demo.client.is_ready()
            is_live = demo.client.is_live()
            
            console.print(f"🟢 Ready: {is_ready}")
            console.print(f"🔄 Live: {is_live}")
            
            if is_ready and is_live:
                console.print("🚀 Weaviate is fully operational!", style="bold green")
            else:
                console.print("⚠️  Weaviate may not be fully ready", style="yellow")
                
        except Exception as e:
            console.print(f"⚠️  Health check failed: {e}", style="yellow")
        
        demo.close()
    else:
        console.print("❌ Cannot connect to Weaviate", style="red")
        console.print("💡 Make sure Weaviate is running: docker-compose up weaviate", style="blue")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()