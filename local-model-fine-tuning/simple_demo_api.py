#!/usr/bin/env python3
"""
Simple Demo API for Local Model Fine-tuning Demo
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime
import random

app = FastAPI(title="Local Model Fine-tuning Demo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "healthy", "service": "local-model-fine-tuning"}

@app.get("/api/models")
def get_models():
    return {
        "available_models": [
            {"name": "llama2:7b-chat", "size": "7B", "status": "ready", "type": "chat"},
            {"name": "llama2:13b-chat", "size": "13B", "status": "downloading", "type": "chat"},
            {"name": "mistral:7b-instruct", "size": "7B", "status": "ready", "type": "instruct"},
            {"name": "codellama:7b", "size": "7B", "status": "ready", "type": "code"}
        ]
    }

@app.post("/api/training/start")
def start_training(request: dict = None):
    if not request:
        request = {}
    return {
        "status": "training_started",
        "job_id": f"demo_job_{random.randint(1000, 9999)}",
        "model": request.get("model_name", "llama2:7b-chat"),
        "epochs": request.get("epochs", 3),
        "started_at": datetime.now().isoformat(),
        "estimated_duration_minutes": 45
    }

@app.get("/api/training/status")
def get_training_status():
    return {
        "status": "running",
        "progress": round(random.uniform(0.3, 0.9), 2),
        "epoch": random.randint(1, 3),
        "loss": round(random.uniform(0.2, 0.8), 3),
        "eta_minutes": random.randint(5, 30),
        "metrics": {
            "learning_rate": 0.0001,
            "batch_size": 32,
            "accuracy": round(random.uniform(0.7, 0.95), 3)
        }
    }

@app.get("/api/datasets")
def get_datasets():
    return {
        "datasets": [
            {"name": "customer_support", "size": 1500, "type": "conversational"},
            {"name": "technical_docs", "size": 3200, "type": "instruction"},
            {"name": "code_completion", "size": 890, "type": "code"}
        ]
    }

@app.get("/api/wellnessroberts/documents")
def get_wellnessroberts_documents():
    return {
        "organization": "WellnessRoberts Care",
        "description": "Major healthcare organization in Tokyo with 2,623 employees",
        "documents": [
            {
                "id": "org_profile",
                "name": "📋 Organization Profile",
                "description": "Complete organizational structure, departments, strategic priorities",
                "size": "2.1 KB",
                "type": "organizational",
                "content_preview": "WellnessRoberts Care - Healthcare Organization Profile (2,623 employees, Tokyo-based, $500M-$2B revenue range)"
            },
            {
                "id": "daily_priorities",
                "name": "🎯 CEO Daily Priorities",
                "description": "Executive briefing with 5 strategic priorities including $4.2M PatientCare Suite investment decision",
                "size": "8.7 KB",
                "type": "executive",
                "content_preview": "Q4 Budget Approval Review ($4.2M PatientCare Suite), Japan Health Data Protection Act compliance, Senior Physician retention..."
            },
            {
                "id": "industry_context",
                "name": "🏥 Healthcare Industry Analysis",
                "description": "Tokyo healthcare market analysis, competitive landscape, regulatory requirements",
                "size": "12.3 KB",
                "type": "market_analysis",
                "content_preview": "Japan's healthcare sector regulatory transformation, HDPA compliance, digital maturity gaps, competitive analysis..."
            }
        ]
    }

@app.post("/api/wellnessroberts/upload")
def upload_wellnessroberts_document(request: dict):
    document_id = request.get("document_id")

    # Simulate processing the specific document
    doc_info = {
        "org_profile": {
            "training_examples": 45,
            "topics": ["organizational_structure", "departments", "strategic_priorities", "employee_counts"],
            "use_cases": ["HR queries", "organizational charts", "department info"]
        },
        "daily_priorities": {
            "training_examples": 127,
            "topics": ["budget_decisions", "regulatory_compliance", "physician_retention", "strategic_partnerships"],
            "use_cases": ["executive decision support", "budget analysis", "strategic planning"]
        },
        "industry_context": {
            "training_examples": 89,
            "topics": ["healthcare_regulations", "market_analysis", "competitive_landscape", "digital_transformation"],
            "use_cases": ["market questions", "regulatory compliance", "competitive analysis"]
        }
    }

    selected_doc = doc_info.get(document_id, {"training_examples": 50, "topics": ["general"], "use_cases": ["general queries"]})

    return {
        "status": "uploaded",
        "document_id": document_id,
        "processed": True,
        "training_examples_generated": selected_doc["training_examples"],
        "topics_identified": selected_doc["topics"],
        "use_cases": selected_doc["use_cases"],
        "ready_for_training": True
    }

@app.get("/api/training/history")
def get_training_history():
    return {
        "recent_jobs": [
            {
                "job_id": "job_8847",
                "model": "llama2:7b-chat",
                "status": "completed",
                "accuracy": 0.89,
                "completed_at": "2025-09-13T10:30:00Z"
            },
            {
                "job_id": "job_8848",
                "model": "mistral:7b-instruct",
                "status": "failed",
                "error": "Out of memory",
                "failed_at": "2025-09-13T12:15:00Z"
            }
        ]
    }

if __name__ == "__main__":
    print("🤖 Starting Local Model Fine-tuning Demo API on port 8005...")
    uvicorn.run(app, host="0.0.0.0", port=8005, log_level="info")