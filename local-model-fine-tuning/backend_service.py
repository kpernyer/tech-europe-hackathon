#!/usr/bin/env python3
"""
Backend service for real LoRA training and inference
Integrates with the web demo to provide actual model training and inference
"""

import os
import json
import torch
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import tempfile
import shutil

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import threading
import time

# Import our existing trainer
from qwen_lora_trainer import QwenOrganizationalTrainer, QwenLoRAConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global state
training_status = {
    "status": "idle",  # idle, training, completed, error
    "progress": 0,
    "current_step": "",
    "start_time": None,
    "duration": 0,
    "model_size": "",
    "lora_size": "",
    "error_message": ""
}

active_model = None
active_tokenizer = None
current_trainer = None

@dataclass
class TrainingJob:
    id: str
    documents: List[str]
    status: str
    start_time: datetime
    progress: int
    model_path: Optional[str] = None
    metrics: Optional[Dict] = None

# Store active training jobs
training_jobs = {}

class DocumentProcessor:
    """Process uploaded documents into training format"""

    @staticmethod
    def extract_text_from_file(file_path: str) -> str:
        """Extract text from various file formats"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return ""

    @staticmethod
    def create_training_examples_from_documents(documents: List[str]) -> List[Dict[str, str]]:
        """Create training examples from document content"""
        examples = []

        for i, doc_content in enumerate(documents):
            # Split document into chunks and create Q&A pairs
            chunks = doc_content.split('\n\n')

            for j, chunk in enumerate(chunks):
                if len(chunk.strip()) > 50:  # Skip very short chunks
                    examples.append({
                        "instruction": f"What does document {i+1} say about this topic?",
                        "input": f"Excerpt: {chunk[:100]}...",
                        "output": chunk.strip()
                    })

                    # Also create a summarization example
                    examples.append({
                        "instruction": f"Summarize the key points from document {i+1}",
                        "input": "",
                        "output": f"Based on the document content: {chunk[:200]}... [This represents key insights from the uploaded organizational document]"
                    })

        # Limit to reasonable number of examples
        return examples[:20]  # Cap at 20 examples for demo

def train_model_background(documents: List[str], job_id: str):
    """Background training function"""
    global training_status, current_trainer

    try:
        training_status.update({
            "status": "training",
            "progress": 0,
            "current_step": "Initializing training",
            "start_time": time.time(),
            "error_message": ""
        })

        # Process documents into training examples
        training_status["current_step"] = "Processing documents"
        training_status["progress"] = 10

        training_examples = DocumentProcessor.create_training_examples_from_documents(documents)
        logger.info(f"Created {len(training_examples)} training examples from documents")

        # Setup trainer with custom config
        training_status["current_step"] = "Setting up model configuration"
        training_status["progress"] = 20

        config = QwenLoRAConfig()
        config.output_dir = f"./models/qwen-3b-custom-{job_id}"
        config.num_train_epochs = 2  # Shorter for demo
        config.max_samples = len(training_examples)

        trainer_obj = QwenOrganizationalTrainer(config)
        current_trainer = trainer_obj

        # Override the create_organizational_dataset method to use our documents
        def custom_dataset_method():
            return training_examples

        trainer_obj.create_organizational_dataset = custom_dataset_method

        training_status["current_step"] = "Loading model and tokenizer"
        training_status["progress"] = 30

        # Setup model and tokenizer
        model, tokenizer = trainer_obj.setup_model_and_tokenizer()

        training_status["current_step"] = "Preparing training data"
        training_status["progress"] = 40

        # Create dataset
        examples = trainer_obj.create_organizational_dataset()
        train_dataset = trainer_obj.format_training_data(examples, tokenizer)

        training_status["current_step"] = "Starting LoRA training"
        training_status["progress"] = 50

        # Training arguments optimized for quick demo
        from transformers import TrainingArguments, Trainer, DataCollatorForLanguageModeling

        training_args = TrainingArguments(
            output_dir=config.output_dir,
            num_train_epochs=config.num_train_epochs,
            per_device_train_batch_size=1,
            gradient_accumulation_steps=2,
            optim="adamw_torch",
            save_steps=50,
            logging_steps=5,
            learning_rate=2e-4,
            weight_decay=0.001,
            fp16=False,
            bf16=False,
            max_grad_norm=0.3,
            max_steps=-1,
            warmup_steps=20,
            lr_scheduler_type="constant",
            report_to=None,
            save_safetensors=True,
            push_to_hub=False,
            load_best_model_at_end=False,
            eval_strategy="no",
            save_total_limit=1,
            remove_unused_columns=False,
        )

        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False,
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            tokenizer=tokenizer,
            data_collator=data_collator,
        )

        training_status["current_step"] = "Training in progress"
        training_status["progress"] = 60

        # Start training
        trainer.train()

        training_status["current_step"] = "Saving model"
        training_status["progress"] = 90

        # Save the model
        trainer.save_model()
        tokenizer.save_pretrained(config.output_dir)

        # Calculate metrics
        end_time = time.time()
        duration = end_time - training_status["start_time"]

        # Get model sizes
        model_path = Path(config.output_dir)
        adapter_file = model_path / "adapter_model.safetensors"
        lora_size = f"{adapter_file.stat().st_size / (1024*1024):.1f}MB" if adapter_file.exists() else "Unknown"

        # Save training config
        config_path = Path(config.output_dir) / "training_config.json"
        with open(config_path, 'w') as f:
            json.dump({
                "model_name": config.model_name,
                "lora_r": config.lora_r,
                "lora_alpha": config.lora_alpha,
                "training_time": datetime.now().isoformat(),
                "num_examples": len(examples),
                "device": trainer_obj.device,
                "duration_seconds": duration,
                "lora_size": lora_size
            }, f, indent=2)

        training_status.update({
            "status": "completed",
            "progress": 100,
            "current_step": "Training completed successfully",
            "duration": duration,
            "model_size": "3GB",
            "lora_size": lora_size
        })

        logger.info(f"Training completed successfully! Duration: {duration:.1f}s, LoRA size: {lora_size}")

    except Exception as e:
        logger.error(f"Training failed: {e}")
        training_status.update({
            "status": "error",
            "error_message": str(e),
            "current_step": f"Error: {str(e)}"
        })

def load_trained_model(model_path: str):
    """Load the trained LoRA model for inference"""
    global active_model, active_tokenizer

    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        from peft import PeftModel

        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

        # Load base model
        base_model = AutoModelForCausalLM.from_pretrained(
            "Qwen/Qwen2.5-3B-Instruct",
            device_map="auto",
            trust_remote_code=True,
            torch_dtype=torch.float16,
        )

        # Load LoRA weights
        model = PeftModel.from_pretrained(base_model, model_path)
        model.eval()

        active_model = model
        active_tokenizer = tokenizer

        logger.info(f"Successfully loaded trained model from {model_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return False

def get_model_inference(prompt: str, use_trained: bool = True) -> str:
    """Get inference from the model"""
    global active_model, active_tokenizer

    try:
        if use_trained and active_model is not None and active_tokenizer is not None:
            # Use trained model
            formatted_prompt = f"### Instruction:\n{prompt}\n\n### Response:\n"

            inputs = active_tokenizer(formatted_prompt, return_tensors="pt").to(active_model.device)

            with torch.no_grad():
                outputs = active_model.generate(
                    **inputs,
                    max_new_tokens=150,
                    do_sample=True,
                    temperature=0.7,
                    pad_token_id=active_tokenizer.eos_token_id,
                    eos_token_id=active_tokenizer.eos_token_id,
                )

            response = active_tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
            return response.strip()
        else:
            # Fallback to simulated response
            return f"[Simulated response to: {prompt}] This demonstrates how the trained model would respond based on your uploaded documents."

    except Exception as e:
        logger.error(f"Inference failed: {e}")
        return f"Error during inference: {str(e)}"

# API Routes

@app.route('/')
def serve_demo():
    """Serve the demo HTML file"""
    return send_from_directory('.', 'demo.html')

@app.route('/api/status')
def get_status():
    """Get current training status"""
    return jsonify(training_status)

@app.route('/api/upload_documents', methods=['POST'])
def upload_documents():
    """Handle document upload and start training"""
    try:
        data = request.get_json()
        documents = data.get('documents', [])

        if len(documents) == 0:
            return jsonify({"error": "No documents provided"}), 400

        # Generate job ID
        job_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Start training in background
        training_thread = threading.Thread(
            target=train_model_background,
            args=(documents, job_id)
        )
        training_thread.daemon = True
        training_thread.start()

        return jsonify({
            "message": "Training started",
            "job_id": job_id,
            "status": "training"
        })

    except Exception as e:
        logger.error(f"Upload failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/inference', methods=['POST'])
def inference():
    """Handle inference requests"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        use_trained = data.get('use_trained', True)

        start_time = time.time()
        response = get_model_inference(prompt, use_trained)
        inference_time = (time.time() - start_time) * 1000  # Convert to ms

        return jsonify({
            "response": response,
            "inference_time_ms": f"{inference_time:.0f}ms",
            "model_used": "trained_qwen_lora" if use_trained and active_model else "simulated"
        })

    except Exception as e:
        logger.error(f"Inference failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/load_model', methods=['POST'])
def load_model():
    """Load a trained model for inference"""
    try:
        data = request.get_json()
        model_path = data.get('model_path', '')

        if not model_path:
            # Try to find the most recent model
            models_dir = Path("./models")
            if models_dir.exists():
                model_dirs = [d for d in models_dir.iterdir() if d.is_dir() and d.name.startswith("qwen-3b")]
                if model_dirs:
                    model_path = str(sorted(model_dirs, key=lambda x: x.stat().st_mtime)[-1])

        if model_path and Path(model_path).exists():
            success = load_trained_model(model_path)
            if success:
                return jsonify({"message": f"Model loaded successfully from {model_path}"})
            else:
                return jsonify({"error": "Failed to load model"}), 500
        else:
            return jsonify({"error": "Model path not found"}), 404

    except Exception as e:
        logger.error(f"Load model failed: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Try to load existing trained model on startup
    models_dir = Path("./models")
    if models_dir.exists():
        model_dirs = [d for d in models_dir.iterdir() if d.is_dir() and d.name.startswith("qwen-3b")]
        if model_dirs:
            latest_model = sorted(model_dirs, key=lambda x: x.stat().st_mtime)[-1]
            logger.info(f"Loading existing model: {latest_model}")
            load_trained_model(str(latest_model))

    logger.info("Starting backend service on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True, threaded=True)