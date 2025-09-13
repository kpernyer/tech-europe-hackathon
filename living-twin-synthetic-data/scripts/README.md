# Scripts Directory

This directory contains utility scripts for generating synthetic organizational data for the Living Twin platform.

## Data Generation Scripts

### Core Generation
- **`generate_structured_data.py`** - Generate basic structured organizational data
- **`quick_structured_data.py`** - Fast generation of minimal organizational datasets
- **`unified_persona_pipeline.py`** - Create unified personas combining text, voice, and metadata

### Strategic Documents
- **`generate_strategic_documents.py`** - Generate realistic strategic business documents
- **`enhanced_strategic_generator.py`** - Advanced strategic document generation with GPT integration
- **`scrape_real_strategic_docs.py`** - Web scraping tools for gathering real strategic document examples

## Testing Scripts
- **`test_enhanced_doc.py`** - Test the enhanced document generation functionality
- **`test_unified_personas.py`** - Test unified persona pipeline

## Usage

Most scripts can be run directly with Python:

```bash
# Generate basic structured data
python scripts/generate_structured_data.py

# Generate strategic documents
python scripts/generate_strategic_documents.py

# Run unified persona pipeline
python scripts/unified_persona_pipeline.py --help
```

## Dependencies

All scripts use the dependencies defined in `pyproject.toml`. Make sure to install them first:

```bash
pip install uv
uv sync
```

Then run scripts with:
```bash
uv run python scripts/script_name.py
```