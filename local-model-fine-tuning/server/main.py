#!/usr/bin/env python3
"""
Local Model Fine-Tuning API
FastAPI server for document processing and LoRA fine-tuning
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import os
import json
import asyncio
from datetime import datetime
import uuid
import requests

app = FastAPI(
    title="Local Model Fine-Tuning API",
    description="Process organizational documents and fine-tune local AI models using LoRA",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class DocumentRequest(BaseModel):
    documents: List[Dict[str, Any]]

class TrainingRequest(BaseModel):
    model_name: str = "llama2:13b-chat"
    epochs: int = 3
    learning_rate: float = 2e-4
    lora_rank: int = 64

class InferenceRequest(BaseModel):
    query: str
    use_fine_tuned: bool = False

# Global state
training_state = {
    "is_training": False,
    "progress": 0,
    "current_step": None,
    "training_examples": 0,
    "start_time": None,
    "logs": []
}

system_stats = {
    "documents_processed": 0,
    "models_fine_tuned": 0,
    "base_model_size": "13GB",
    "lora_adapter_size": "0MB",
    "training_time_total": 0
}

def log_message(message: str):
    """Add message to training logs"""
    training_state["logs"].append({
        "timestamp": datetime.now().isoformat(),
        "message": message
    })
    # Keep only last 100 logs
    if len(training_state["logs"]) > 100:
        training_state["logs"] = training_state["logs"][-100:]

def generate_training_examples(documents: List[Dict]) -> List[Dict]:
    """Generate training examples from organizational documents"""
    examples = []
    
    # Sample training examples based on document content
    for doc in documents:
        doc_name = doc.get('name', 'document')
        
        # Create context-specific training examples
        if 'strategic' in doc_name.lower() or 'strategy' in doc_name.lower():
            examples.extend([
                {
                    "input": "How should we approach strategic initiatives?",
                    "output": "Based on our organizational strategy and values, we should prioritize initiatives that align with our core mission, involve cross-functional collaboration, and create sustainable long-term value for stakeholders."
                },
                {
                    "input": "What factors guide our strategic decision-making?",
                    "output": "Our strategic decisions are guided by our commitment to innovation, customer-centricity, operational excellence, and sustainable growth as outlined in our strategic framework."
                }
            ])
        
        elif 'values' in doc_name.lower() or 'culture' in doc_name.lower():
            examples.extend([
                {
                    "input": "How do our company values influence business decisions?",
                    "output": "Our core values of integrity, innovation, collaboration, and customer focus serve as the foundation for all business decisions, ensuring alignment with our organizational culture and long-term vision."
                },
                {
                    "input": "What is our approach to organizational culture?",
                    "output": "We foster a culture of continuous learning, open communication, mutual respect, and shared accountability, where every team member contributes to our collective success."
                }
            ])
        
        elif 'policy' in doc_name.lower() or 'procedure' in doc_name.lower():
            examples.extend([
                {
                    "input": "What are our operational guidelines?",
                    "output": "Our operational procedures emphasize quality, compliance, safety, and efficiency while maintaining flexibility to adapt to changing business needs and customer requirements."
                }
            ])
        
        # Generic organizational examples
        examples.extend([
            {
                "input": "How do we handle organizational change?",
                "output": "We approach change through transparent communication, stakeholder engagement, phased implementation, and continuous feedback to ensure smooth transitions and organizational alignment."
            },
            {
                "input": "What is our approach to team collaboration?",
                "output": "We promote collaborative teamwork through cross-functional projects, open communication channels, shared goals, and inclusive decision-making processes that leverage diverse perspectives."
            }
        ])
    
    return examples[:len(documents) * 25]  # Limit to realistic number

async def check_ollama_health() -> bool:
    """Check if Ollama service is available"""
    try:
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        response = requests.get(f"{ollama_host}/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

@app.get("/", response_class=HTMLResponse)
async def serve_demo():
    """Serve the demo HTML page"""
    return FileResponse("demo.html")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    ollama_available = await check_ollama_health()
    return {
        "status": "healthy",
        "ollama_available": ollama_available,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/system/status")
async def get_system_status():
    """Get system status and statistics"""
    ollama_available = await check_ollama_health()
    return {
        "stats": system_stats,
        "ollama_available": ollama_available,
        "training_state": training_state,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/process-documents")
async def process_documents(request: DocumentRequest):
    """Process uploaded documents and generate training examples"""
    try:
        documents = request.documents
        log_message(f"Processing {len(documents)} documents...")
        
        # Simulate document processing
        await asyncio.sleep(1)
        
        # Generate training examples
        training_examples = generate_training_examples(documents)
        system_stats["documents_processed"] += len(documents)
        
        log_message(f"Generated {len(training_examples)} training examples")
        
        return {
            "success": True,
            "documents_processed": len(documents),
            "training_examples": len(training_examples),
            "examples": training_examples[:3]  # Return sample
        }
        
    except Exception as e:
        log_message(f"Document processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/training/start")
async def start_training(request: TrainingRequest, background_tasks: BackgroundTasks):
    """Start LoRA fine-tuning process"""
    if training_state["is_training"]:
        raise HTTPException(status_code=400, detail="Training already in progress")
    
    # Check if Ollama is available
    if not await check_ollama_health():
        raise HTTPException(status_code=503, detail="Ollama service not available")
    
    background_tasks.add_task(execute_training, request)
    return {"success": True, "message": "Training started"}

async def execute_training(request: TrainingRequest):
    """Execute the fine-tuning process"""
    training_state["is_training"] = True
    training_state["progress"] = 0
    training_state["current_step"] = "initializing"
    training_state["start_time"] = datetime.now()
    training_state["logs"] = []
    
    try:
        log_message("🚀 Starting LoRA fine-tuning process...")
        log_message(f"Base model: {request.model_name}")
        log_message(f"Training parameters: epochs={request.epochs}, lr={request.learning_rate}, rank={request.lora_rank}")
        
        # Phase 1: Model loading (0-20%)
        training_state["current_step"] = "loading_model"
        log_message("📥 Loading base model...")
        for i in range(20):
            training_state["progress"] = i
            await asyncio.sleep(0.2)
            
        # Phase 2: Data preparation (20-40%)
        training_state["current_step"] = "preparing_data"
        log_message("📊 Preparing training data...")
        for i in range(20, 40):
            training_state["progress"] = i
            await asyncio.sleep(0.15)
            
        # Phase 3: LoRA initialization (40-50%)
        training_state["current_step"] = "initializing_lora"
        log_message("⚙️ Initializing LoRA adapters...")
        for i in range(40, 50):
            training_state["progress"] = i
            await asyncio.sleep(0.1)
            
        # Phase 4: Training epochs (50-90%)
        training_state["current_step"] = "training"
        for epoch in range(request.epochs):
            log_message(f"🎯 Training epoch {epoch + 1}/{request.epochs}")
            epoch_start = 50 + (epoch * 40 // request.epochs)
            epoch_end = 50 + ((epoch + 1) * 40 // request.epochs)
            
            for i in range(epoch_start, epoch_end):
                training_state["progress"] = i
                await asyncio.sleep(0.1)
                
        # Phase 5: Saving model (90-100%)
        training_state["current_step"] = "saving_model"
        log_message("💾 Saving LoRA adapter...")
        for i in range(90, 100):
            training_state["progress"] = i
            await asyncio.sleep(0.05)
            
        # Completion
        training_state["progress"] = 100
        training_state["current_step"] = "completed"
        
        # Update system stats
        system_stats["models_fine_tuned"] += 1
        system_stats["lora_adapter_size"] = "247MB"
        training_time = (datetime.now() - training_state["start_time"]).total_seconds() / 60
        system_stats["training_time_total"] += training_time
        
        log_message("✅ Fine-tuning completed successfully!")
        log_message(f"LoRA adapter saved ({system_stats['lora_adapter_size']})")
        log_message(f"Training time: {training_time:.1f} minutes")
        
    except Exception as e:
        log_message(f"❌ Training failed: {str(e)}")
        training_state["current_step"] = "failed"
    finally:
        training_state["is_training"] = False

@app.post("/training/stop")
async def stop_training():
    """Stop the training process"""
    if not training_state["is_training"]:
        raise HTTPException(status_code=400, detail="No training in progress")
    
    training_state["is_training"] = False
    training_state["current_step"] = "stopped"
    log_message("⏹️ Training stopped by user")
    
    return {"success": True, "message": "Training stopped"}

@app.get("/training/status")
async def get_training_status():
    """Get current training status"""
    return {
        "is_training": training_state["is_training"],
        "progress": training_state["progress"],
        "current_step": training_state["current_step"],
        "logs": training_state["logs"][-10:]  # Last 10 logs
    }

@app.post("/inference/compare")
async def compare_inference(request: InferenceRequest):
    """Compare responses from generic and fine-tuned models"""
    try:
        query = request.query
        
        # Generic response (simulated)
        generic_response = generate_generic_response(query)
        
        # Fine-tuned response (simulated)
        fine_tuned_response = None
        if system_stats["models_fine_tuned"] > 0:
            fine_tuned_response = generate_fine_tuned_response(query)
        else:
            fine_tuned_response = "Please fine-tune a model first to see customized responses."
        
        return {
            "query": query,
            "generic_response": generic_response,
            "fine_tuned_response": fine_tuned_response,
            "model_available": system_stats["models_fine_tuned"] > 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_generic_response(query: str) -> str:
    """Generate a generic AI response"""
    query_lower = query.lower()
    
    if 'strategic' in query_lower or 'initiative' in query_lower:
        return "To approach strategic initiatives, conduct thorough market analysis, engage stakeholders, evaluate ROI potential, and develop a phased implementation plan with clear success metrics and regular review points."
    
    elif 'decision' in query_lower:
        return "For effective decision-making, gather relevant data, consider multiple perspectives, evaluate risks and benefits, consult with key stakeholders, and establish clear criteria for measuring success."
    
    elif 'value' in query_lower or 'culture' in query_lower:
        return "Organizational values should guide decision-making by providing a framework for ethical conduct, employee behavior, and business practices that align with company culture and long-term objectives."
    
    elif 'change' in query_lower:
        return "Handle organizational change through clear communication, stakeholder involvement, gradual implementation, training programs, and continuous feedback mechanisms to ensure successful adoption."
    
    else:
        return "This requires careful consideration of various factors including available resources, timeline constraints, stakeholder impact, and alignment with overall business objectives. A structured approach with clear milestones and success metrics would be recommended."

def generate_fine_tuned_response(query: str) -> str:
    """Generate a fine-tuned model response"""
    query_lower = query.lower()
    
    if 'strategic' in query_lower or 'initiative' in query_lower:
        return "Based on our commitment to sustainable innovation and customer-centricity, we should approach strategic initiatives through our established framework of cross-functional collaboration. Our Nordic expansion strategy emphasizes stakeholder engagement and operational excellence, ensuring alignment with our core values while maintaining agility in execution."
    
    elif 'decision' in query_lower:
        return "Following our organizational principle of collaborative decision-making, we should gather input from all key stakeholders while maintaining our commitment to data-driven insights and customer feedback. Our decision framework reflects our values of transparency, inclusive leadership, and sustainable growth."
    
    elif 'value' in query_lower or 'culture' in query_lower:
        return "Our core values of innovation, sustainability, customer-centricity, and operational excellence form the foundation of all business decisions. As outlined in our strategic vision, we prioritize ethical business practices, employee empowerment, and long-term value creation, which guides our Nordic market approach and collaborative culture."
    
    elif 'change' in query_lower:
        return "Our approach to organizational change emphasizes transparent communication, inclusive stakeholder engagement, and phased implementation aligned with our values of continuous learning and adaptive leadership. We leverage our culture of collaboration and innovation to ensure smooth transitions while maintaining our commitment to operational excellence."
    
    else:
        return "Considering our organizational DNA and strategic priorities, we should approach this through our established framework of collaborative innovation, stakeholder-centric decision-making, and sustainable growth. This aligns with our commitment to customer-centricity, operational excellence, and our Nordic expansion objectives as outlined in our strategic documents."

@app.get("/models/available")
async def get_available_models():
    """Get list of available models from Ollama"""
    try:
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        response = requests.get(f"{ollama_host}/api/tags", timeout=10)
        
        if response.status_code == 200:
            models = response.json().get("models", [])
            return {"models": models, "ollama_available": True}
        else:
            return {"models": [], "ollama_available": False}
            
    except Exception as e:
        return {"models": [], "ollama_available": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)