from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import os
import uuid
from pathlib import Path
import asyncio
import subprocess

# from ..domain.services import get_rag_service  # Will implement this later
from ..ports.llm import IChatLLM
# from ..di import get_chat_llm  # Will implement proper DI later

router = APIRouter(prefix="/experiments/fine-tuning", tags=["fine-tuning-experiment"])

# Data models
class OrganizationCreate(BaseModel):
    name: str
    industry: str

class TrainingExample(BaseModel):
    instruction: str
    input: str
    output: str
    source_doc: str

class StartTrainingRequest(BaseModel):
    organization_id: str
    tenantId: str

class CompareModelsRequest(BaseModel):
    query: str
    organizations: List[str]
    tenantId: str

# Storage paths
EXPERIMENT_BASE = Path("experiments/fine-tuning")
TENANT_DATA_DIR = EXPERIMENT_BASE / "tenant_data"
MODELS_DIR = EXPERIMENT_BASE / "models"
TRAINING_DATA_DIR = EXPERIMENT_BASE / "training_data"

# Ensure directories exist
for dir_path in [TENANT_DATA_DIR, MODELS_DIR, TRAINING_DATA_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# In-memory storage for demo (in production, use proper database)
organizations_store = {}
documents_store = {}
training_data_store = {}

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    organization_id: str = Form(...),
    tenantId: str = Form(...)
):
    """Upload a document for a specific organization"""
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Validate file type
    allowed_extensions = {'.pdf', '.docx', '.doc', '.txt', '.md'}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file_ext} not supported. Allowed: {allowed_extensions}"
        )
    
    # Create organization directory
    org_dir = TENANT_DATA_DIR / organization_id
    org_dir.mkdir(exist_ok=True)
    
    # Generate unique document ID and save file
    doc_id = str(uuid.uuid4())
    file_path = org_dir / f"{doc_id}_{file.filename}"
    
    # Save file
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Store document metadata
    if organization_id not in documents_store:
        documents_store[organization_id] = []
    
    doc_metadata = {
        "id": doc_id,
        "filename": file.filename,
        "title": title,
        "file_path": str(file_path),
        "size": len(content),
        "processed": False
    }
    documents_store[organization_id].append(doc_metadata)
    
    return {
        "document_id": doc_id,
        "message": f"Document uploaded for organization {organization_id}",
        "file_type": file_ext,
        "size": len(content)
    }

@router.post("/generate-training-data")
async def generate_training_data(request: dict):
    """Generate training examples from uploaded documents"""
    
    organization_id = request["organization_id"]
    tenant_id = request["tenantId"]
    
    if organization_id not in documents_store:
        raise HTTPException(status_code=404, detail="No documents found for organization")
    
    documents = documents_store[organization_id]
    if not documents:
        raise HTTPException(status_code=400, detail="No documents uploaded for this organization")
    
    training_examples = []
    
    # Process each document to generate training examples
    for doc in documents:
        try:
            # Read document content
            with open(doc["file_path"], "r", encoding="utf-8") as f:
                content = f.read()
            
            # Generate training examples based on document type and content
            examples = await _generate_examples_from_content(
                content, 
                doc["title"], 
                organization_id
            )
            training_examples.extend(examples)
            
            # Mark document as processed
            doc["processed"] = True
            
        except Exception as e:
            print(f"Error processing document {doc['filename']}: {e}")
            continue
    
    # Store training data
    training_data_store[organization_id] = training_examples
    
    # Save training data to file
    training_file = TRAINING_DATA_DIR / f"{organization_id}_training.jsonl"
    with open(training_file, "w") as f:
        for example in training_examples:
            f.write(json.dumps({
                "instruction": example["instruction"],
                "input": example["input"],
                "output": example["output"]
            }) + "\n")
    
    return {
        "examples": training_examples[:5],  # Return first 5 for preview
        "total_count": len(training_examples),
        "training_file": str(training_file)
    }

@router.post("/start-training")
async def start_training(request: StartTrainingRequest):
    """Start LoRA fine-tuning for an organization"""
    
    organization_id = request.organization_id
    
    if organization_id not in training_data_store:
        raise HTTPException(status_code=400, detail="No training data generated for this organization")
    
    training_file = TRAINING_DATA_DIR / f"{organization_id}_training.jsonl"
    if not training_file.exists():
        raise HTTPException(status_code=400, detail="Training data file not found")
    
    # Create model output directory
    model_output_dir = MODELS_DIR / f"dna-{organization_id}"
    model_output_dir.mkdir(exist_ok=True)
    
    # Start fine-tuning process (async)
    asyncio.create_task(_run_fine_tuning(organization_id, str(training_file), str(model_output_dir)))
    
    return {
        "message": f"Fine-tuning started for organization {organization_id}",
        "model_output_dir": str(model_output_dir),
        "status": "training_started"
    }

@router.post("/compare")
async def compare_models(request: CompareModelsRequest):
    """Compare responses from different models"""
    
    query = request.query
    organizations = request.organizations
    
    results = {}
    
    # Get RAG-only baseline (mock for now)
    rag_hits = [{"text": f"Mock RAG result for: {query}", "source": "demo"}]
    results["rag_only"] = f"RAG Response: Based on our documents, {query}"
    
    # Get fine-tuned model responses
    for org_id in organizations:
        model_path = MODELS_DIR / f"dna-{org_id}"
        if model_path.exists():
            # In a real implementation, you'd load the fine-tuned model here
            # For now, we'll simulate with enhanced prompts
            enhanced_response = await _get_fine_tuned_response(query, org_id, rag_hits)
            results[f"fine_tuned_{org_id}"] = enhanced_response
        else:
            results[f"fine_tuned_{org_id}"] = "Model not ready yet"
    
    return results

@router.get("/status/{organization_id}")
async def get_organization_status(organization_id: str):
    """Get training status for an organization"""
    
    model_path = MODELS_DIR / f"dna-{organization_id}"
    
    if model_path.exists():
        # Check if training is complete
        if (model_path / "adapter_model.bin").exists():
            status = "ready"
        else:
            status = "training"
    else:
        status = "not_started"
    
    return {
        "organization_id": organization_id,
        "status": status,
        "documents_count": len(documents_store.get(organization_id, [])),
        "training_examples": len(training_data_store.get(organization_id, [])),
        "model_path": str(model_path) if model_path.exists() else None
    }

# Helper functions
async def _generate_examples_from_content(content: str, title: str, org_id: str) -> List[Dict[str, str]]:
    """Generate training examples from document content"""
    
    examples = []
    
    # Split content into chunks for processing
    chunks = _split_content(content, max_length=1000)
    
    # Generate different types of training examples
    for i, chunk in enumerate(chunks[:10]):  # Limit to first 10 chunks
        
        # Strategic analysis examples
        examples.append({
            "instruction": "Analyze this content from our organizational perspective and provide strategic insights.",
            "input": f"Content: {chunk}",
            "output": f"Based on our organizational values and strategic direction, this content suggests: {_create_strategic_analysis(chunk, org_id)}",
            "source_doc": title
        })
        
        # Value alignment examples
        examples.append({
            "instruction": "How does this align with our core organizational values?",
            "input": f"Topic: {chunk[:200]}...",
            "output": f"This aligns with our values by: {_create_value_alignment(chunk, org_id)}",
            "source_doc": title
        })
        
        # Communication style examples
        examples.append({
            "instruction": "Rewrite this in our organizational communication style.",
            "input": f"Original: {chunk[:300]}...",
            "output": f"In our style: {_adapt_communication_style(chunk, org_id)}",
            "source_doc": title
        })
    
    return examples

def _split_content(content: str, max_length: int = 1000) -> List[str]:
    """Split content into manageable chunks"""
    words = content.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) > max_length and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
        else:
            current_chunk.append(word)
            current_length += len(word) + 1  # +1 for space
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

def _create_strategic_analysis(content: str, org_id: str) -> str:
    """Create strategic analysis based on organization"""
    # Simplified example - in practice, this would use the organization's specific context
    return f"This represents a key strategic opportunity for {org_id} to leverage our core competencies and market position."

def _create_value_alignment(content: str, org_id: str) -> str:
    """Create value alignment explanation"""
    return f"Demonstrating {org_id}'s commitment to excellence, innovation, and customer-centricity."

def _adapt_communication_style(content: str, org_id: str) -> str:
    """Adapt content to organization's communication style"""
    # Simplified - would use actual organizational voice
    return f"[{org_id} style] " + content[:200] + "..."

async def _run_fine_tuning(org_id: str, training_file: str, output_dir: str):
    """Run the actual fine-tuning process (mock implementation)"""
    
    # In a real implementation, this would:
    # 1. Load base model (Mistral-7B)
    # 2. Apply LoRA adapters
    # 3. Train on the generated data
    # 4. Save the fine-tuned model
    
    # For now, just simulate the training process
    await asyncio.sleep(10)  # Simulate training time
    
    # Create mock model files
    model_dir = Path(output_dir)
    model_dir.mkdir(exist_ok=True)
    
    # Create placeholder files to indicate training completion
    (model_dir / "adapter_model.bin").touch()
    (model_dir / "adapter_config.json").write_text('{"base_model": "mistral-7b"}')
    
    print(f"Fine-tuning completed for organization {org_id}")

async def _get_fine_tuned_response(query: str, org_id: str, rag_hits: List[Dict[str, Any]]) -> str:
    """Get response from fine-tuned model (mock implementation)"""
    
    # In a real implementation, this would load and use the fine-tuned model
    # For now, simulate organizational-specific responses
    
    context = "\n".join([f"[{i+1}] {hit.get('text', '')}" for i, hit in enumerate(rag_hits)])
    
    org_styles = {
        "org1": "As a technology-forward organization, we believe that",
        "org2": "From our manufacturing excellence perspective, we focus on"
    }
    
    style_prefix = org_styles.get(org_id, "In our organizational context,")
    
    return f"{style_prefix} {query}\n\nBased on our strategic documents:\n{context}\n\nOur approach emphasizes operational excellence and sustainable growth aligned with our core values."