# 🚀 Hackathon {Tech: Europe} - Kenneth Pernyer

**September 13-14th 2025**
**Strategic AI Research - Strategy Alignment System**

## 🙏 Acknowledgments

**Huge thanks to [Tech Europe](https://techeurope.org) and all sponsors for organizing this fantastic hackathon event!**

**Technologies & Partners:**
- **OpenAI** - GPT-4o-mini models, Realtime API, and voice capabilities powering our AI demos
- **Weaviate** - Vector database and semantic search infrastructure for knowledge management
- **Lovable** - UI development assistance for creating beautiful interfaces
- **RunPod** - Attempted integration for GPU compute (couldn't include in final demos)

*This event has been an incredible opportunity to explore cutting-edge AI technologies and build meaningful solutions.*

---

## 🚀 Essential Commands

**Get started in 4 commands:**

```bash
make start              # Start all services
make stop               # Stop all services
make status             # Check all services status
make ports              # Show all port assignments
```

## 🔗 Port Management & Quick Start

### 📡 Centralized Port Configuration
All demos run on dedicated ports to avoid conflicts. Use the centralized port management system:

### 🌐 Demo URLs (Active Ports)
- **OpenAI Voice**: http://localhost:8001 (Web), http://localhost:8787 (API)
- **Weaviate Recall**: http://localhost:8002 (Web), http://localhost:8082 (Weaviate DB)
- **Hybrid Knowledge**: http://localhost:8003 (Web), http://localhost:8888 (API)
- **Living Twin**: http://localhost:8004 (Web), http://localhost:8889 (API), Redis: 6381
- **Local Model**: http://localhost:8005 (Web), http://localhost:8885 (API)

### 🏗️ Architecture Overview
- **Centralized Configuration**: All ports defined in root `Makefile` and `ports.yaml`
- **Docker Compose**: Each project uses lightweight containerized services
- **Environment Variables**: Port configuration passed to sub-projects
- **No Conflicts**: Dedicated port ranges prevent overlap issues

### ⚡ Quick Commands
```bash
cd /Users/kenper/src/aprio-one/tech-europe-hackathon

# Show all port allocations
make ports

# Start all demos simultaneously
make start

# Check which services are running
make status

# View logs from all services
make logs

# Stop everything
make stop
```

---

## 🎯 Research Objective

This repository contains **hackathon research across 5 critical areas** that will directly guide the development of **Aprio.One's Strategy Alignment solution**. Each project explores a different technological aspect to solving organizational alignment challenges. Learnings and patterns is feeding back into Aprio.One's core platform.

### 🔬 Research Areas

**The 5 research streams investigations today:**
1. **Knowledge Management & Semantic Search** → Strategy document retrieval and contextual search
2. **Voice AI & Conversational Interfaces** → Natural language strategy consultation. Speech-Speech model. 
3. **Synthetic Data & Privacy-Preserving AI** → Generate and use Safe training data for organizational AI
4. **Hybrid Knowledge Architecture** → Multi-modal data integration for comprehensive insights
5. **Custom AI Fine-tuning** → Organization-specific model that understands unique local contexts


## 📂 Demo Collection

### 🎙️ [OpenAI Voice Demo](./openai-voice/)
**Real-time Voice AI Agent with WebRTC/WebSocket Transport**

- **Core Stack**: OpenAI Realtime API, Node.js, TypeScript, Vite, WebRTC
- **Backend**: Express.js server with WebSocket handling
- **Frontend**: React 18 with TypeScript, real-time audio processing
- **Features**: Real-time voice conversations, ephemeral token management, audio streaming
- **Use Case**: Interactive voice assistants for customer service, support, and conversational AI
- **Demo URL**: `http://localhost:8001/`

### 🧠 [Weaviate Recall Knowledge](./weaviate-recall-knowledge/)
**Strategic Knowledge Management & Semantic Search**

- **Core Stack**: Weaviate 1.27.9, FastAPI, Python 3.11+, OpenAI GPT-4o-mini
- **Backend**: FastAPI with uv package management, asyncio for high performance
- **Vector DB**: Weaviate with text-embedding-3-small (1536 dims), GraphQL queries
- **Frontend**: Pure HTML/CSS/JS with real-time metrics and vector confidence scoring
- **Features**: Progressive document injection, semantic search, RAG pipeline, tiered responses
- **Use Case**: Enterprise knowledge management, strategic decision support
- **Demo URL**: `http://localhost:8002/`

### 🏢 [Local Model Fine-tuning](./local-model-fine-tuning/)
**Custom AI Model Training for Business Context**

- **Core Stack**: Python 3.11+, FastAPI, React 18, TypeScript, Docker, Ollama
- **Backend**: FastAPI with fine-tuning orchestration, dataset management
- **Frontend**: React with TypeScript, experiment tracking UI, progress visualization
- **ML Pipeline**: LoRA (Low-Rank Adaptation) fine-tuning, custom training workflows, validation metrics, model versioning
- **Local LLM**: Ollama for local model hosting and inference, privacy-preserving fine-tuning
- **Fine-tuning**: LoRA adapters for efficient parameter updates, organizational context adaptation
- **Features**: Domain-specific AI adaptation, business process optimization, experiment tracking, local model deployment
- **Use Case**: Tailored AI systems that understand organizational nuances without external API dependencies
- **Demo URL**: `http://localhost:8005/`

### 🔄 [Hybrid Knowledge System](./hybrid-knowledge-system/)
**Multi-Modal Knowledge Integration Platform**

- **Core Stack**: Python 3.11+, Neo4j 5.18, Weaviate, Redis, Docker Compose
- **Graph DB**: Neo4j with vector search, APOC plugins, Cypher queries
- **Vector DB**: Weaviate integration for semantic search capabilities  
- **Cache Layer**: Redis for performance optimization and session management
- **Features**: Cross-platform knowledge synthesis, hybrid search, unified query interface
- **Use Case**: Complex enterprise environments with diverse data sources
- **Demo URL**: `http://localhost:8003/`

### 🧬 [Living Twin Synthetic Data](./living-twin-synthetic-data/)
**Synthetic Data Generation for AI Training**

- **Core Stack**: Python 3.11+, OpenAI GPT-4o-mini, AsyncIO, Rich CLI, uv packaging
- **Data Generation**: AI-powered synthetic organizational data creation
- **Processing**: Pandas for data manipulation, structured JSON/CSV output
- **CLI Interface**: Rich-powered terminal UI with progress tracking
- **Features**: Realistic synthetic datasets, privacy compliance, scalable generation, validation
- **Use Case**: AI training without sensitive data exposure, compliance-friendly ML
- **Demo URL**: `http://localhost:8004/`

---

## 🎯 Demonstration Flow

**Recommended Demo Sequence:**
1. **Weaviate Recall Knowledge** - Show progressive knowledge enhancement
2. **OpenAI Voice Demo** - Interactive voice AI capabilities
3. **Hybrid Knowledge System** - Enterprise-scale architecture
4. **Synthetic Data & Fine-tuning** - Advanced AI customization

## 📦 Centralized Dependency Management

**Unified Library Versions** - All Python projects use identical versions of core libraries to ensure compatibility and avoid dependency conflicts.

### 🔍 Version Consistency
All projects reference `shared-versions.yml` for standardized dependency versions:

**Core Libraries (All Projects)**:
- **OpenAI**: `1.12.0` - Consistent AI model access
- **Pydantic**: `2.8.0` - Data validation and serialization
- **FastAPI**: `0.109.2` - Web framework standard
- **Weaviate Client**: `4.16.9` - Latest vector database client (eliminates deprecation warnings)

**Key Benefits**:
- ✅ **No version conflicts** between projects
- ✅ **Simplified dependency updates** - update once, apply everywhere
- ✅ **Consistent behavior** across all services
- ✅ **Reduced container build times** with shared base layers

### 📋 Projects Updated
1. **hybrid-knowledge-system** - All dependencies standardized
2. **weaviate-recall-knowledge** - Added FastAPI/web framework deps for consistency
3. **local-model-fine-tuning** - Updated pyproject.toml with unified versions
4. **living-twin-synthetic-data** - Enhanced with full development stack

## 🔧 Comprehensive Tech Stack

### 🐍 Backend & AI/ML
- **Python 3.11+** - Core backend language
- **FastAPI** - Modern async web framework with automatic API docs
- **uv** - Ultra-fast Python package manager and dependency resolver
- **Pydantic** - Data validation and serialization
- **AsyncIO** - Asynchronous programming for high-performance APIs
- **Uvicorn** - ASGI server for production deployment

### 🤖 AI & Machine Learning
- **OpenAI GPT-4o-mini** - Large language model for intelligent responses
- **OpenAI Realtime API** - Real-time voice conversation capabilities
- **OpenAI Embeddings** - text-embedding-3-small (1536 dimensions)
- **Ollama** - Local LLM hosting and inference for privacy-preserving AI
- **PyTorch** - Deep learning framework for model training, fine-tuning, and inference
- **LoRA (Low-Rank Adaptation)** - Efficient fine-tuning technique for parameter updates
- **Custom Fine-tuning** - Organization-specific model adaptation with LoRA adapters
- **LangChain** - AI application framework and RAG pipelines
- **Transformers** - Hugging Face model library and training frameworks
- **sentence-transformers** - Semantic similarity and embeddings

### 🗄️ Vector & Graph Databases  
- **Weaviate 1.25.0** - Primary vector database with OpenAI integration
- **Neo4j 5.18+** - Graph database with vector search capabilities
- **Redis 7.2** - In-memory cache and session storage
- **GraphQL** - Query language for semantic search operations

### 🌐 Frontend & UI
- **TypeScript** - Type-safe JavaScript development
- **React 18** - Modern frontend framework
- **Vite** - Fast build tool and development server
- **HTML/CSS/JS** - Pure web technologies for lightweight demos
- **WebRTC** - Real-time communication for voice features
- **WebSockets** - Real-time bidirectional communication

### 🐳 Infrastructure & DevOps
- **Docker** - Containerization for all services
- **Docker Compose** - Multi-container orchestration
- **GitHub Actions** - CI/CD workflows (planned)
- **GCP Cloud Run** - Serverless container deployment
- **Firebase Hosting** - Static site hosting and authentication
- **Nginx** - Reverse proxy and load balancing

### 📊 Data Processing & Analytics
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computing
- **Jupyter Notebooks** - Interactive data exploration
- **Matplotlib/Plotly** - Data visualization
- **Rich** - Beautiful terminal output and progress bars

### 🔧 Development Tools
- **Git** - Version control with conventional commits
- **GitHub CLI** - Repository management
- **VSCode** - Primary development environment
- **Black** - Python code formatting
- **ESLint** - TypeScript/JavaScript linting
- **Prettier** - Code formatting for web technologies

### 🔒 Security & Authentication
- **Environment Variables** - Secure configuration management
- **OAuth 2.0** - Authentication protocols
- **JWT Tokens** - Stateless authentication
- **CORS** - Cross-origin resource sharing
- **Rate Limiting** - API protection
- **Input Validation** - Pydantic schemas for security

### 📡 APIs & Communication
- **REST APIs** - Standard HTTP-based services
- **GraphQL** - Flexible query language for complex data
- **WebSockets** - Real-time bidirectional communication
- **Server-Sent Events** - Real-time server-to-client streaming
- **Webhooks** - Event-driven integrations

### 🧪 Testing & Quality Assurance
- **pytest** - Python testing framework
- **httpx** - Async HTTP client for API testing
- **Jest** - JavaScript testing framework
- **Coverage.py** - Code coverage analysis
- **mypy** - Static type checking for Python

### Key Architectural Patterns
- **RAG (Retrieval-Augmented Generation)** - Context-aware AI responses
- **Progressive Enhancement** - Knowledge quality improvement over time
- **Multi-modal Integration** - Text, voice, and structured data synthesis
- **Microservices Architecture** - Containerized, independently deployable services
- **Event-Driven Architecture** - Asynchronous communication patterns
- **Security-First Design** - Ephemeral tokens, data privacy, compliance

## 📊 Business Value for Aprio.One Strategy Alignment

### Strategic Knowledge Management → Aprio.One Integration
- **Faster strategy decisions** through instant access to organizational knowledge
- **Reduced alignment silos** with unified semantic search across strategy documents
- **Automated strategy compliance** checking against organizational values and goals

### Voice AI Integration → Strategy Consultation
- **Natural language strategy queries** for executives and teams
- **Accessible strategy guidance** for voice-first interactions
- **Scalable strategy support** without requiring strategy consultants

### Synthetic Data & Privacy → Organizational AI Training
- **Privacy-preserving strategy AI** without exposing sensitive organizational data
- **Rapid strategy dataset generation** for new organizational contexts
- **Compliance-ready synthetic strategy** alternatives for AI training

### Hybrid Architecture → Comprehensive Strategy Insights
- **Multi-modal strategy data integration** (documents, conversations, decisions)
- **Cross-organizational pattern recognition** for strategy optimization
- **Unified strategy intelligence** across all organizational touchpoints


## 👤 About

**Kenneth Pernyer**
*Founder, AI Solutions Architect & Full-Stack Developer*

**Contact**: Available during Hackathon {Tech: Europe}, LinkedIn
