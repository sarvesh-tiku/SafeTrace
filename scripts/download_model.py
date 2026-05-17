#!/usr/bin/env python3
"""Pre-download a HuggingFace model to a specified cache directory.

Usage:
    HF_HOME=/storage/scratch1/0/stiku6/hf_cache python scripts/download_model.py meta-llama/Llama-3.1-8B-Instruct
"""
import sys
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

model_id = sys.argv[1] if len(sys.argv) > 1 else "microsoft/Phi-3.5-mini-instruct"

print(f"Downloading tokenizer: {model_id}")
AutoTokenizer.from_pretrained(model_id, use_fast=False)

print(f"Downloading model: {model_id}")
AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16)

print("Done!")
