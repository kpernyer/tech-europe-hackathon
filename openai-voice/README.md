# OpenAI Voice Demo - Organizational Twin CEO Assistant

## 🎯 Project Overview

This demo showcases an **Organizational Twin CEO Assistant** - an AI voice agent that understands your company's context, maintains conversation state, and provides intelligent analysis of CEO interactions. Unlike generic voice assistants, this system has deep organizational knowledge and can conduct realistic business conversations with sentiment analysis and interpretation.

### 🧠 Key Capabilities
- **Organizational Context**: Deep knowledge of company structure, culture, and current priorities
- **Intelligent Backlog Management**: Presents daily priorities and tracks conversation progress
- **Sentiment Analysis**: Detects stress, urgency, tempo, and emotional state during conversations
- **Conversation Intelligence**: Remembers context, handles interruptions, maintains topic awareness
- **Predictable Demo**: Same organizational context, different user responses for consistent testing

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   CEO (Voice)   │◄──►│  Voice Frontend  │◄──►│  Analysis Backend   │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────────┐
                       │ OpenAI Realtime  │    │ Conversation State  │
                       │   (WebRTC)       │    │  & Sentiment API    │
                       └──────────────────┘    └─────────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────────┐
                       │Organizational    │    │  Analytics &        │
                       │Context Data      │    │  Interpretation     │
                       └──────────────────┘    └─────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Docker & Docker Compose
- OpenAI API key with Realtime API access

### 1. Setup Environment
```bash
# Create environment file with your OpenAI API key
make setup-env

# Edit .env file with your actual OpenAI API key
# You need an OpenAI API key with Realtime API access
```

### 2. Full Demo (Recommended)
```bash
# Install, build, and start everything
make demo

# This will:
# - Install dependencies
# - Build Docker containers  
# - Start API server on http://localhost:8787
# - Start web interface on http://localhost:5173
```

### 3. Test the System
```bash
# Run system tests (API endpoints, context loading)
make test

# Run conversation interpretation demo (simulated CEO briefing)
make demo-conversation
```

### 4. Access the Demo
- **Web Interface**: http://localhost:5173 (main demo UI)
- **API Server**: http://localhost:8787 (backend endpoints)

### 5. Monitor & Debug
```bash
# View live logs from both services
make logs

# Check health status
make health

# Stop everything
make stop
```

## 🎭 Demo Flow

1. Start with `make demo`
2. Open http://localhost:5173 
3. Click "Connect to Organizational Twin"
4. The AI will automatically begin: *"Good morning! I have today's 5 priority items for your review..."*
5. You can interrupt anytime to ask questions
6. Watch the real-time analytics panel for sentiment and engagement tracking

## 🛠️ Available Make Commands

Run `make help` to see all options:
- `make demo` - Start the full system
- `make test` - Run API tests  
- `make demo-conversation` - Simulate CEO briefing conversation
- `make health` - Check if services are running
- `make logs` - View service logs
- `make stop` - Stop all services
- `make clean` - Clean up containers and data

## 📊 Demo Scenario

### The Organizational Twin
- **Company**: WellnessRoberts Care (Healthcare, 2623 employees)
- **Role**: Intelligent organizational assistant for CEO
- **Personality**: Professional, analytical, healthcare-focused
- **Context**: Complete company knowledge, strategic priorities, current challenges

### Conversation Flow
1. **Assistant initiates**: "Good morning! Here are today's 5 priority items..."
2. **CEO can interrupt**: At any point during the presentation
3. **State management**: Assistant remembers where conversation was, what was covered
4. **Sentiment tracking**: Analyzes CEO's stress, urgency, decision-making patterns
5. **Analytics output**: Real-time interpretation of conversation dynamics

## 🏢 Organizational Context

The system loads complete organizational context from:
- **Company Profile**: Industry, size, culture, strategic priorities
- **Current Backlog**: 5 daily priority items requiring CEO attention
- **Communication Patterns**: How information flows through the organization
- **Sentiment Baselines**: Expected communication styles and stress indicators

## 📈 Analytics & Intelligence

### Real-time Analysis
- **Sentiment Detection**: Stress, urgency, confidence levels
- **Tempo Analysis**: Speaking pace, interruption patterns
- **Topic Tracking**: What's been discussed, what's pending
- **Decision Indicators**: When CEO is ready to make decisions vs. needs more info

### Conversation Intelligence
- **Context Maintenance**: Remembers full conversation history
- **Interruption Handling**: Graceful topic switching and resumption
- **Priority Rebalancing**: Adapts agenda based on CEO's immediate concerns
- **Follow-up Suggestions**: Intelligent next steps based on conversation

## 🎛️ Available Commands

### Development
```bash
make install          # Install dependencies
make dev              # Start development servers
make build            # Build Docker images
make demo             # Start full containerized demo
make stop             # Stop all services
```

### Testing & Analysis
```bash
make logs             # View system logs
make health           # Check service health
make clean            # Clean containers and data
```

## 🔧 Configuration

### Environment Variables
```bash
# Required
OPENAI_API_KEY=sk-...                    # OpenAI API key with Realtime access

# Optional
PORT=8787                                # Server port
NODE_ENV=development                     # Environment mode
ORGANIZATION_ID=org_000                  # Which company context to load
CONVERSATION_LOGGING=true               # Enable conversation analytics
```

### Organizational Context
The system loads organizational data from `context/` directory:
- `context/organization.json` - Company profile and culture
- `context/backlog.json` - Current priorities and agenda items
- `context/conversation_flows.json` - Communication patterns
- `context/personas.json` - Key personnel and roles

## 📋 API Endpoints

### Voice & Tokens
- `POST /api/ephemeral-token` - Generate OpenAI ephemeral tokens
- `GET /healthz` - Service health check

### Analytics & Context
- `POST /api/conversation/start` - Initialize new conversation session
- `POST /api/conversation/update` - Update conversation state and sentiment
- `GET /api/organization/context` - Load organizational context
- `GET /api/analytics/summary` - Get conversation analytics summary

## 🧪 Demo Usage

### Starting a Session
1. Click "Connect to Voice Agent"
2. Allow microphone permissions
3. Wait for "Good morning! Here are today's 5 priority items..."
4. Listen or interrupt at any time

### Testing Interruptions
- Interrupt during item #2: "Wait, tell me more about that budget issue"
- Assistant will pause, address your concern, then ask "Shall we continue with the remaining items?"
- Test different interruption points to see state management

### Analyzing Results
- Check the "Conversation Analytics" panel for real-time sentiment
- View "Topic Progress" to see what's been covered
- Monitor "CEO Stress Indicators" for urgency/pressure detection

## 🔍 Technical Details

### Voice Processing
- **Transport**: WebRTC with ephemeral tokens for security
- **Model**: GPT-4o Realtime Preview with organizational instructions
- **Audio**: Real-time bidirectional voice communication

### Context Management
- **State Persistence**: Full conversation history and progress tracking
- **Dynamic Instructions**: Real-time system prompt updates based on context
- **Interruption Recovery**: Sophisticated resume-from-interruption logic

### Analytics Pipeline
- **Sentiment Analysis**: OpenAI + custom sentiment detection
- **Temporal Analysis**: Speaking patterns, pause detection, urgency indicators
- **Topic Modeling**: What's discussed, decision points, follow-up needs

## 🐛 Troubleshooting

### Connection Issues
- Ensure OpenAI API key has Realtime API access
- Check browser microphone permissions for localhost
- Try Chrome without extensions (some block WebRTC)

### Context Loading
- Verify `context/organization.json` exists and is valid
- Check server logs for context loading errors
- Ensure all required organizational data fields are present

### Audio Quality
- Use headphones to prevent echo/feedback
- Ensure stable internet connection for WebRTC
- Check microphone quality and permissions

## 🚀 Future Enhancements

- **Multi-language Support**: International organizational contexts
- **Advanced Analytics**: Deeper conversation intelligence and insights  
- **Integration APIs**: Connect with calendar, email, CRM systems
- **Mobile Support**: Native mobile app with same capabilities
- **Multi-user Sessions**: Support for team meetings and collaboration

---

**This demo represents the future of organizational AI - intelligent assistants that understand your business context and provide meaningful analysis of executive interactions.**

*Built for Hackathon Tech Europe 2025 by Kenneth Pernyer*