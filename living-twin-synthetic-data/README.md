# Living Twin Synthetic Data Generation

A comprehensive synthetic data generation system for the Living Twin organizational intelligence platform. This repository contains three interconnected subprojects that build upon each other to create rich, multimodal training data.

## 🏗️ Architecture

```
synthetic-data/     → Base: Organizations, people, scenarios
    ↓
voice-generation/   → Adds: Voice personas, audio files
    ↓
animation-data/     → Adds: 3D positions, gestures, scenes
```

## 📁 Project Structure

```
living-twin-synthetic-data/
├── synthetic-data/          # Core data generation
│   ├── organizations/       # Organization profiles
│   ├── people/             # Person personas
│   ├── scenarios/          # Delegation & strategic scenarios
│   └── outputs/            # Generated JSON data
│
├── voice-generation/        # ElevenLabs voice synthesis
│   ├── voice-mapping/      # Person → Voice mappings
│   ├── audio-scripts/      # Text to be voiced
│   └── audio-outputs/      # Generated MP3 files
│
├── animation-data/          # VR/AR scene generation
│   ├── spatial-configs/    # 3D environments
│   ├── avatar-models/      # Character configurations
│   └── scene-outputs/      # Complete VR/AR scenes
│
├── shared/                  # Shared utilities
│   ├── schemas/            # Data schemas
│   ├── validators/         # Data validators
│   └── utils/              # Common utilities
│
└── Makefile                # Build orchestration
```

## 🚀 Quick Start

```bash
# Install dependencies
make install

# Generate synthetic organizations
make synthetic-data

# Add voice generation (requires ElevenLabs API key)
make voice-generation

# Add animation data
make animation-data

# Run complete pipeline
make all

# Clean all generated data
make clean
```

## 🔧 Configuration

Create a `.env` file with your API keys:

```bash
OPENAI_API_KEY=your_key_here
ELEVENLABS_API_KEY=your_key_here
AWS_REGION=us-east-1
AWS_BEDROCK_ENABLED=true
```

## 📊 Data Dimensions

### Organizations
- Size (50-10000 employees)
- Industry (tech, finance, healthcare, etc.)
- Geographic regions
- Profitability status
- Years in business
- Organizational structure (flat, hierarchical, matrix)
- Delegation culture (top-down, consensus, distributed)

### People
- Roles & hierarchy
- Personality traits
- Communication styles
- Decision-making patterns
- Years of experience
- Risk tolerance
- Cultural backgrounds

### Scenarios
- Strategic decisions
- Delegation chains
- Crisis responses
- Innovation challenges
- Performance reviews
- Resource allocation
- Market responses

## 🎯 Make Targets

- `make synthetic-data` - Generate base synthetic data
- `make voice-generation` - Generate voice personas and audio
- `make animation-data` - Generate VR/AR scene data
- `make validate` - Validate all generated data
- `make stats` - Show statistics about generated data
- `make clean` - Remove all generated files
- `make all` - Run complete pipeline

## 📈 Dependency Tracking

The Makefile automatically:
- Detects changes in source data
- Regenerates dependent outputs
- Maintains consistency across subprojects
- Validates data at each stage

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.