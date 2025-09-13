# Organizational AI Fine-Tuning Experiment

> **Hackathon Demo**: Watch AI learn your organization's DNA through document fine-tuning

## 🎯 The Demo Story

1. **Upload strategic documents** (vision, values, policies)
2. **Generate training examples** from organizational content  
3. **Fine-tune the AI model** on company-specific data
4. **Compare responses**: Generic AI vs Organizational AI

## 🚀 Quick Start

```bash
# Start the demo
make demo

# Visit http://localhost:3000 for the frontend
# API docs at http://localhost:8000/docs
```

## 📊 What You'll See

### Before Fine-tuning
**Question**: "How should we approach our next strategic initiative?"
**Generic Response**: "Consider market analysis, stakeholder input, and ROI calculations..."

### After Fine-tuning  
**Question**: "How should we approach our next strategic initiative?"
**Org-Specific Response**: "Based on our commitment to sustainable innovation and our Q3 objectives to expand in Nordic markets, we should leverage our core values of customer-centricity and operational excellence..."

## 🏗️ Architecture

- **Backend**: FastAPI with fine-tuning pipeline
- **Frontend**: React interface for document upload and model comparison
- **Training**: LoRA fine-tuning on organizational documents
- **Storage**: File-based demo data (no external dependencies)

## 📈 Model Comparison

| Model | Size | Deployment | Training Time | Response Quality |
|-------|------|------------|---------------|-----------------|
| Base GPT | 13GB | Local | N/A | Generic |
| Fine-tuned | 13GB + 200MB LoRA | Local | ~10 minutes | Organization-specific |
| ChatGPT-4 | ~1.7TB | Cloud API | N/A | Generic |

## 🎭 Demo Script

See [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) for complete hackathon presentation guide.
