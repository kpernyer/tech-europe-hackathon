#!/usr/bin/env python3
"""
Qwen 2.5 3B LoRA Fine-tuning Demo
Optimized for organizational AI training with efficient resource usage
"""

import os
import json
import torch
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

import transformers
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType, PeftModel
from datasets import Dataset

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class QwenLoRAConfig:
    """Configuration for Qwen 2.5 3B LoRA training"""

    # Model settings
    model_name: str = "qwen2.5:3b"
    base_model_path: str = "Qwen/Qwen2.5-3B-Instruct"

    # LoRA settings optimized for 3B model
    lora_r: int = 16  # Rank - good balance for 3B model
    lora_alpha: int = 32  # Scaling parameter
    lora_dropout: float = 0.05
    lora_target_modules: List[str] = field(default_factory=lambda: [
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ])

    # Training settings optimized for efficiency
    num_train_epochs: int = 3
    per_device_train_batch_size: int = 1  # Small for 3B model
    gradient_accumulation_steps: int = 4
    learning_rate: float = 2e-4
    warmup_steps: int = 50
    max_length: int = 512  # Reasonable for organizational content

    # Quantization for memory efficiency (disabled for Apple Silicon)
    use_4bit: bool = False
    bnb_4bit_quant_type: str = "nf4"
    bnb_4bit_compute_dtype: str = "float16"

    # Output settings
    output_dir: str = "./models/qwen-3b-org-lora"
    logging_steps: int = 10
    save_steps: int = 100

    # Data settings
    max_samples: int = 500  # Reasonable for demo

class QwenOrganizationalTrainer:
    """Trainer for Qwen 2.5 3B with organizational fine-tuning"""

    def __init__(self, config: QwenLoRAConfig):
        self.config = config
        self.device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")

        # Create output directories
        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)
        Path("./training_data").mkdir(exist_ok=True)

    def setup_model_and_tokenizer(self) -> Tuple[AutoModelForCausalLM, AutoTokenizer]:
        """Setup Qwen model with quantization and LoRA"""

        logger.info("Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            self.config.base_model_path,
            trust_remote_code=True,
            padding_side="right"
        )

        # Add pad token if not present
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        logger.info("Loading model without quantization for Apple Silicon...")
        model = AutoModelForCausalLM.from_pretrained(
            self.config.base_model_path,
            device_map="auto",
            trust_remote_code=True,
            torch_dtype=torch.float16,
        )

        logger.info("Setting up LoRA configuration...")
        lora_config = LoraConfig(
            r=self.config.lora_r,
            lora_alpha=self.config.lora_alpha,
            target_modules=self.config.lora_target_modules,
            lora_dropout=self.config.lora_dropout,
            bias="none",
            task_type=TaskType.CAUSAL_LM,
        )

        logger.info("Applying LoRA to model...")
        model = get_peft_model(model, lora_config)
        model.print_trainable_parameters()

        return model, tokenizer

    def create_organizational_dataset(self) -> List[Dict[str, str]]:
        """Create sample organizational training data"""

        organizational_examples = [
            {
                "instruction": "What is our company's approach to digital transformation?",
                "input": "",
                "output": "Our digital transformation strategy focuses on customer-centric innovation, leveraging cloud-first architecture and data-driven decision making. We prioritize agile methodologies and cross-functional collaboration to deliver scalable solutions that enhance operational efficiency while maintaining our commitment to excellence and sustainable growth."
            },
            {
                "instruction": "How should we handle a potential merger opportunity?",
                "input": "A competitor has approached us about a potential merger.",
                "output": "We should conduct thorough due diligence focusing on strategic fit, cultural alignment, and synergy potential. Our evaluation framework includes financial analysis, market positioning assessment, and integration complexity review. We'll engage our board early and ensure transparency with stakeholders while maintaining confidentiality throughout the process."
            },
            {
                "instruction": "What are our core values in practice?",
                "input": "",
                "output": "Our core values manifest through customer obsession, operational excellence, and team empowerment. We demonstrate integrity in every decision, embrace innovation as a growth driver, and maintain accountability at all levels. These values guide our hiring, promotion, and strategic decisions, ensuring consistent culture across all business units."
            },
            {
                "instruction": "How do we approach risk management?",
                "input": "We're considering expanding into a new market segment.",
                "output": "Our risk management framework balances opportunity assessment with prudent controls. We conduct comprehensive market analysis, pilot programs, and scenario planning. Key considerations include regulatory compliance, competitive landscape, resource allocation, and potential impact on existing operations. We maintain clear escalation procedures and regular risk review cycles."
            },
            {
                "instruction": "What is our talent development philosophy?",
                "input": "",
                "output": "We believe in developing talent through challenging assignments, mentorship programs, and continuous learning opportunities. Our approach includes 360-degree feedback, cross-functional rotations, and leadership development tracks. We invest in both technical skills and leadership capabilities, fostering a culture of growth mindset and knowledge sharing."
            },
            {
                "instruction": "How do we prioritize strategic initiatives?",
                "input": "We have multiple competing priorities for the next quarter.",
                "output": "Our prioritization framework evaluates initiatives based on strategic alignment, resource requirements, expected ROI, and implementation timeline. We use a scoring matrix considering customer impact, competitive advantage, and organizational capability. Regular reviews ensure agility in responding to market changes while maintaining focus on long-term objectives."
            },
            {
                "instruction": "What is our crisis management protocol?",
                "input": "We're facing a potential PR crisis.",
                "output": "Immediate activation of our crisis response team with clear communication channels and decision authority. Priority one is ensuring stakeholder safety and business continuity. We follow established communication protocols with transparent, timely updates to customers, employees, and partners. Post-crisis analysis includes lessons learned and process improvements."
            },
            {
                "instruction": "How do we foster innovation?",
                "input": "",
                "output": "Innovation thrives through dedicated time allocation, cross-team collaboration, and failure tolerance. We support experimentation with allocated resources, encourage diverse perspectives, and maintain open innovation channels. Regular innovation sessions, external partnerships, and customer feedback loops drive continuous improvement and breakthrough thinking."
            }
        ]

        # Extend with variations and additional examples
        extended_examples = []
        for example in organizational_examples:
            # Add original
            extended_examples.append(example)

            # Add variations for different organizational contexts
            if "digital transformation" in example["instruction"]:
                extended_examples.append({
                    "instruction": "Describe our technology modernization strategy.",
                    "input": "",
                    "output": example["output"].replace("digital transformation", "technology modernization")
                })

        logger.info(f"Created {len(extended_examples)} training examples")
        return extended_examples[:self.config.max_samples]

    def format_training_data(self, examples: List[Dict[str, str]], tokenizer: AutoTokenizer) -> Dataset:
        """Format data for Qwen training with proper formatting"""

        def format_example(example):
            if example["input"]:
                prompt = f"### Instruction:\n{example['instruction']}\n\n### Input:\n{example['input']}\n\n### Response:\n{example['output']}"
            else:
                prompt = f"### Instruction:\n{example['instruction']}\n\n### Response:\n{example['output']}"
            return prompt

        formatted_texts = [format_example(ex) for ex in examples]

        def tokenize_function(examples):
            return tokenizer(
                examples["text"],
                truncation=True,
                padding=False,
                max_length=self.config.max_length,
                return_tensors=None,
            )

        dataset = Dataset.from_dict({"text": formatted_texts})
        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=dataset.column_names
        )

        return tokenized_dataset

    def train(self):
        """Main training function"""

        logger.info("Starting Qwen 2.5 3B LoRA training...")

        # Setup model and tokenizer
        model, tokenizer = self.setup_model_and_tokenizer()

        # Create dataset
        examples = self.create_organizational_dataset()
        train_dataset = self.format_training_data(examples, tokenizer)

        # Training arguments optimized for Apple Silicon - avoid bitsandbytes
        training_args = TrainingArguments(
            output_dir=self.config.output_dir,
            num_train_epochs=self.config.num_train_epochs,
            per_device_train_batch_size=self.config.per_device_train_batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            optim="adamw_torch",  # Use standard PyTorch optimizer for Apple Silicon
            save_steps=self.config.save_steps,
            logging_steps=self.config.logging_steps,
            learning_rate=self.config.learning_rate,
            weight_decay=0.001,
            fp16=False,  # Disable FP16 on Apple Silicon
            bf16=False,  # Disable BF16 on Apple Silicon
            max_grad_norm=0.3,
            max_steps=-1,
            warmup_steps=self.config.warmup_steps,
            group_by_length=False,  # Disable grouping for simplicity
            lr_scheduler_type="constant",
            report_to=None,  # Disable wandb for simplicity
            save_safetensors=True,
            dataloader_drop_last=False,  # Keep all data
            dataloader_pin_memory=False,  # Disable pin memory for Apple Silicon
            push_to_hub=False,
            load_best_model_at_end=False,
            eval_strategy="no",  # No evaluation for simplicity
            save_total_limit=1,  # Keep only latest checkpoint
            remove_unused_columns=False,  # Keep all columns for LoRA
        )

        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False,
        )

        # Initialize trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            tokenizer=tokenizer,
            data_collator=data_collator,
        )

        # Start training
        logger.info("Starting training...")
        trainer.train()

        # Save the model
        logger.info("Saving model...")
        trainer.save_model()
        tokenizer.save_pretrained(self.config.output_dir)

        # Save training config
        config_path = Path(self.config.output_dir) / "training_config.json"
        with open(config_path, 'w') as f:
            json.dump({
                "model_name": self.config.model_name,
                "lora_r": self.config.lora_r,
                "lora_alpha": self.config.lora_alpha,
                "training_time": datetime.now().isoformat(),
                "num_examples": len(examples),
                "device": self.device
            }, f, indent=2)

        logger.info(f"Training completed! Model saved to {self.config.output_dir}")
        return trainer

    def test_model(self, test_prompts: List[str]) -> None:
        """Test the trained model with sample prompts"""

        logger.info("Loading trained model for testing...")

        # Load base model and tokenizer
        tokenizer = AutoTokenizer.from_pretrained(self.config.output_dir)

        base_model = AutoModelForCausalLM.from_pretrained(
            self.config.base_model_path,
            device_map="auto",
            trust_remote_code=True,
            torch_dtype=torch.float16,
        )

        # Load LoRA weights
        model = PeftModel.from_pretrained(base_model, self.config.output_dir)
        model.eval()

        logger.info("Testing model with sample prompts...")
        for prompt in test_prompts:
            formatted_prompt = f"### Instruction:\n{prompt}\n\n### Response:\n"

            inputs = tokenizer(formatted_prompt, return_tensors="pt").to(model.device)

            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=150,
                    do_sample=True,
                    temperature=0.7,
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                )

            response = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)

            print(f"\n{'='*50}")
            print(f"Prompt: {prompt}")
            print(f"Response: {response}")
            print(f"{'='*50}")

def main():
    """Main execution function"""

    # Initialize configuration
    config = QwenLoRAConfig()

    # Initialize trainer
    trainer = QwenOrganizationalTrainer(config)

    try:
        # Train the model
        trainer.train()

        # Test with sample prompts
        test_prompts = [
            "What is our approach to strategic planning?",
            "How do we handle competitive threats?",
            "What are our priorities for Q4?"
        ]

        trainer.test_model(test_prompts)

    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise

if __name__ == "__main__":
    main()