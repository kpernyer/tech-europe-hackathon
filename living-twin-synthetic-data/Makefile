# Living Twin Synthetic Data Generation Pipeline
# Automatically tracks dependencies and regenerates when source changes

.PHONY: all clean install synthetic-data synthetic-data-ai voice-generation animation-data unified-personas validate stats help

# Configuration
PYTHON := python3
VENV := .venv
UV := uv
PYTHON_VENV := $(UV) run python

# Directories
SYNTHETIC_DIR := synthetic-data
VOICE_DIR := voice-generation
ANIMATION_DIR := animation-data
SHARED_DIR := shared

# Output directories
ORG_OUTPUT := $(SYNTHETIC_DIR)/outputs/organizations
SCENARIO_OUTPUT := $(SYNTHETIC_DIR)/outputs/scenarios
VOICE_OUTPUT := $(VOICE_DIR)/audio-outputs
ANIMATION_OUTPUT := $(ANIMATION_DIR)/scene-outputs

# Timestamp files for dependency tracking
SYNTHETIC_TIMESTAMP := $(SYNTHETIC_DIR)/.generated
VOICE_TIMESTAMP := $(VOICE_DIR)/.generated
ANIMATION_TIMESTAMP := $(ANIMATION_DIR)/.generated

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Default target
all: install synthetic-data voice-generation animation-data validate stats
	@echo "$(GREEN)✅ Complete pipeline executed successfully!$(NC)"

# Help target
help:
	@echo "$(BLUE)Living Twin Synthetic Data Generation$(NC)"
	@echo "======================================="
	@echo ""
	@echo "$(YELLOW)Available targets:$(NC)"
	@echo "  make install           - Install dependencies"
	@echo "  make synthetic-data    - Generate organizations and scenarios (Faker)"
	@echo "  make synthetic-data-ai - Generate organizations with GPT-4 (premium)"
	@echo "  make voice-generation  - Generate voice personas and audio"
	@echo "  make animation-data    - Generate VR/AR animation data"
	@echo "  make unified-personas  - Create unified personas (text + voice + avatar)"
	@echo "  make validate          - Validate all generated data"
	@echo "  make stats            - Show statistics"
	@echo "  make clean            - Remove all generated data"
	@echo "  make all              - Run complete pipeline"
	@echo ""
	@echo "$(YELLOW)Development targets:$(NC)"
	@echo "  make test             - Run tests"
	@echo "  make lint             - Run linters"
	@echo "  make watch            - Watch for changes and regenerate"

# Install dependencies
install: pyproject.toml
	@echo "$(BLUE)📦 Installing dependencies with uv...$(NC)"
	$(UV) sync
	@echo "$(GREEN)✅ Dependencies installed$(NC)"

pyproject.toml:
	@echo "$(BLUE)📝 Initializing uv project...$(NC)"
	$(UV) init --no-readme --no-workspace
	$(UV) add openai boto3 pydantic faker jsonschema click rich requests python-dotenv pyyaml

# Synthetic data generation
synthetic-data: install $(SYNTHETIC_TIMESTAMP)

$(SYNTHETIC_TIMESTAMP): $(SYNTHETIC_DIR)/generate.py $(SYNTHETIC_DIR)/config.yaml
	@echo "$(BLUE)🏢 Generating synthetic organizations and scenarios...$(NC)"
	@mkdir -p $(ORG_OUTPUT) $(SCENARIO_OUTPUT)
	$(PYTHON_VENV) $(SYNTHETIC_DIR)/generate.py \
		--output-dir $(SYNTHETIC_DIR)/outputs \
		--config $(SYNTHETIC_DIR)/config.yaml
	@touch $(SYNTHETIC_TIMESTAMP)
	@echo "$(GREEN)✅ Synthetic data generated$(NC)"

# AI-enhanced synthetic data generation (premium)
synthetic-data-ai: install
	@echo "$(BLUE)🤖 Generating AI-enhanced organizations with GPT-4...$(NC)"
	@if [ -z "$${OPENAI_API_KEY}" ]; then \
		echo "$(RED)❌ OPENAI_API_KEY required for AI generation$(NC)"; \
		echo "$(YELLOW)Add your OpenAI key to .env file$(NC)"; \
		exit 1; \
	fi
	@mkdir -p $(ORG_OUTPUT) $(SCENARIO_OUTPUT)
	$(PYTHON_VENV) $(SYNTHETIC_DIR)/generate_ai.py \
		--count $${SYNTHETIC_DATA_COUNT:-50} \
		--output-dir $(SYNTHETIC_DIR)/outputs \
		--config $(SYNTHETIC_DIR)/config_ai.yaml
	@touch $(SYNTHETIC_TIMESTAMP)
	@echo "$(GREEN)✅ AI-enhanced synthetic data generated$(NC)"

# Voice generation (depends on synthetic data)
voice-generation: synthetic-data $(VOICE_TIMESTAMP)

$(VOICE_TIMESTAMP): $(SYNTHETIC_TIMESTAMP) $(VOICE_DIR)/generate_voices.py
	@echo "$(BLUE)🎙️ Generating voice personas and audio files...$(NC)"
	@mkdir -p $(VOICE_OUTPUT)
	@if [ -z "$${ELEVENLABS_API_KEY}" ]; then \
		echo "$(YELLOW)⚠️  Warning: ELEVENLABS_API_KEY not set, using mock generation$(NC)"; \
		$(PYTHON_VENV) $(VOICE_DIR)/generate_voices.py \
			--input-dir $(SYNTHETIC_DIR)/outputs \
			--output-dir $(VOICE_OUTPUT) \
			--mock; \
	else \
		$(PYTHON_VENV) $(VOICE_DIR)/generate_voices.py \
			--input-dir $(SYNTHETIC_DIR)/outputs \
			--output-dir $(VOICE_OUTPUT); \
	fi
	@touch $(VOICE_TIMESTAMP)
	@echo "$(GREEN)✅ Voice generation complete$(NC)"

# Animation data (depends on voice generation)
animation-data: voice-generation $(ANIMATION_TIMESTAMP)

$(ANIMATION_TIMESTAMP): $(VOICE_TIMESTAMP) $(ANIMATION_DIR)/generate_animations.py
	@echo "$(BLUE)🎬 Generating animation and VR/AR scene data...$(NC)"
	@mkdir -p $(ANIMATION_OUTPUT)
	$(PYTHON_VENV) $(ANIMATION_DIR)/generate_animations.py \
		--synthetic-dir $(SYNTHETIC_DIR)/outputs \
		--voice-dir $(VOICE_OUTPUT) \
		--output-dir $(ANIMATION_OUTPUT)
	@touch $(ANIMATION_TIMESTAMP)
	@echo "$(GREEN)✅ Animation data generated$(NC)"

# Unified persona generation (text + voice + avatar with consistent IDs)
unified-personas: synthetic-data
	@echo "$(BLUE)🚀 Generating unified personas with consistent IDs...$(NC)"
	@mkdir -p unified-personas
	@if [ -z "$${ELEVENLABS_API_KEY}" ] && [ -z "$${BEYOND_PRESENCE_API_KEY}" ]; then \
		echo "$(YELLOW)⚠️  Running in full mock mode (no API keys)$(NC)"; \
		$(PYTHON_VENV) unified_persona_pipeline.py \
			--synthetic-data-dir $(SYNTHETIC_DIR)/outputs \
			--output-dir unified-personas \
			--mock-voice --mock-avatar \
			--org-limit $${ORG_LIMIT:-3}; \
	elif [ -z "$${ELEVENLABS_API_KEY}" ]; then \
		echo "$(YELLOW)⚠️  Voice generation in mock mode (missing ELEVENLABS_API_KEY)$(NC)"; \
		$(PYTHON_VENV) unified_persona_pipeline.py \
			--synthetic-data-dir $(SYNTHETIC_DIR)/outputs \
			--output-dir unified-personas \
			--mock-voice; \
	elif [ -z "$${BEYOND_PRESENCE_API_KEY}" ]; then \
		echo "$(YELLOW)⚠️  Avatar generation in mock mode (missing BEYOND_PRESENCE_API_KEY)$(NC)"; \
		$(PYTHON_VENV) unified_persona_pipeline.py \
			--synthetic-data-dir $(SYNTHETIC_DIR)/outputs \
			--output-dir unified-personas \
			--mock-avatar; \
	else \
		echo "$(GREEN)🔑 Full API mode enabled$(NC)"; \
		$(PYTHON_VENV) unified_persona_pipeline.py \
			--synthetic-data-dir $(SYNTHETIC_DIR)/outputs \
			--output-dir unified-personas; \
	fi
	@echo "$(GREEN)✅ Unified personas generated$(NC)"

# Validate all generated data
validate: $(SHARED_DIR)/validators/validate_all.py
	@echo "$(BLUE)🔍 Validating all generated data...$(NC)"
	@if [ -f $(SYNTHETIC_TIMESTAMP) ]; then \
		$(PYTHON_VENV) $(SHARED_DIR)/validators/validate_all.py \
			--synthetic-dir $(SYNTHETIC_DIR)/outputs \
			--voice-dir $(VOICE_OUTPUT) \
			--animation-dir $(ANIMATION_OUTPUT); \
		echo "$(GREEN)✅ All data validated successfully$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  No data to validate. Run 'make synthetic-data' first.$(NC)"; \
	fi

# Show statistics
stats:
	@echo "$(BLUE)📊 Data Generation Statistics$(NC)"
	@echo "=============================="
	@if [ -f $(SYNTHETIC_TIMESTAMP) ]; then \
		echo "$(YELLOW)Synthetic Data:$(NC)"; \
		echo "  Organizations: $$(find $(ORG_OUTPUT) -name "*.json" 2>/dev/null | wc -l)"; \
		echo "  Scenarios: $$(find $(SCENARIO_OUTPUT) -name "*.json" 2>/dev/null | wc -l)"; \
		echo "  Total size: $$(du -sh $(SYNTHETIC_DIR)/outputs 2>/dev/null | cut -f1)"; \
	fi
	@if [ -f $(VOICE_TIMESTAMP) ]; then \
		echo "$(YELLOW)Voice Data:$(NC)"; \
		echo "  Audio files: $$(find $(VOICE_OUTPUT) -name "*.mp3" 2>/dev/null | wc -l)"; \
		echo "  Voice mappings: $$(find $(VOICE_DIR) -name "*mapping*.json" 2>/dev/null | wc -l)"; \
		echo "  Total size: $$(du -sh $(VOICE_OUTPUT) 2>/dev/null | cut -f1)"; \
	fi
	@if [ -f $(ANIMATION_TIMESTAMP) ]; then \
		echo "$(YELLOW)Animation Data:$(NC)"; \
		echo "  Scene files: $$(find $(ANIMATION_OUTPUT) -name "*.json" 2>/dev/null | wc -l)"; \
		echo "  Total size: $$(du -sh $(ANIMATION_OUTPUT) 2>/dev/null | cut -f1)"; \
	fi

# Clean all generated data
clean:
	@echo "$(RED)🧹 Cleaning all generated data...$(NC)"
	rm -rf $(SYNTHETIC_DIR)/outputs
	rm -rf $(VOICE_OUTPUT)
	rm -rf $(ANIMATION_OUTPUT)
	rm -f $(SYNTHETIC_TIMESTAMP) $(VOICE_TIMESTAMP) $(ANIMATION_TIMESTAMP)
	@echo "$(GREEN)✅ All generated data removed$(NC)"

# Clean everything including virtual environment
clean-all: clean
	@echo "$(RED)🧹 Removing virtual environment...$(NC)"
	rm -rf $(VENV)
	rm -f requirements.txt

# Test targets
test: install
	@echo "$(BLUE)🧪 Running tests...$(NC)"
	$(PYTHON_VENV) -m pytest tests/ -v

lint: install
	@echo "$(BLUE)🔍 Running linters...$(NC)"
	$(PYTHON_VENV) -m black --check .
	$(PYTHON_VENV) -m flake8 .
	$(PYTHON_VENV) -m mypy .

# Development: Watch for changes and regenerate
watch:
	@echo "$(BLUE)👁️  Watching for changes...$(NC)"
	@while true; do \
		$(MAKE) -q all || $(MAKE) all; \
		sleep 2; \
	done

# Check if source files have changed
check-synthetic-changes:
	@if [ ! -f $(SYNTHETIC_TIMESTAMP) ] || \
	   [ $(SYNTHETIC_DIR)/generate.py -nt $(SYNTHETIC_TIMESTAMP) ] || \
	   [ $(SYNTHETIC_DIR)/config.yaml -nt $(SYNTHETIC_TIMESTAMP) ]; then \
		echo "$(YELLOW)♻️  Synthetic data source changed, regenerating...$(NC)"; \
		rm -f $(SYNTHETIC_TIMESTAMP); \
	fi

check-voice-changes:
	@if [ ! -f $(VOICE_TIMESTAMP) ] || \
	   [ $(VOICE_DIR)/generate_voices.py -nt $(VOICE_TIMESTAMP) ] || \
	   [ $(SYNTHETIC_TIMESTAMP) -nt $(VOICE_TIMESTAMP) ]; then \
		echo "$(YELLOW)♻️  Voice generation source changed, regenerating...$(NC)"; \
		rm -f $(VOICE_TIMESTAMP); \
	fi

check-animation-changes:
	@if [ ! -f $(ANIMATION_TIMESTAMP) ] || \
	   [ $(ANIMATION_DIR)/generate_animations.py -nt $(ANIMATION_TIMESTAMP) ] || \
	   [ $(VOICE_TIMESTAMP) -nt $(ANIMATION_TIMESTAMP) ]; then \
		echo "$(YELLOW)♻️  Animation source changed, regenerating...$(NC)"; \
		rm -f $(ANIMATION_TIMESTAMP); \
	fi

# Include dependency checks in main targets
synthetic-data: check-synthetic-changes
voice-generation: check-voice-changes
animation-data: check-animation-changes