"""Local HuggingFace transformers agent — GPU-ready, CPU-fallback.

Loads any instruction-tuned code model from HuggingFace and uses it
directly (no external server required). Supports:
  - Automatic GPU detection (CUDA/MPS)
  - 4-bit quantization via bitsandbytes (reduces VRAM by ~4x)
  - tensor_parallel via Accelerate device_map="auto"
  - Any OpenAI-chat-format instruction model

Default model: microsoft/Phi-3.5-mini-instruct
  - 3.8B params, ~7.6 GB FP16 — fits on V100-16GB; not on GT prohibited list
  - Swap MODEL_ID env var for other allowed models (Llama, Mistral, CodeLlama)
"""
from __future__ import annotations

import os
import re
from datetime import datetime
from typing import Any, Optional

from .schemas import PatchResult, TaskSpec
from .utils import get_diff, read_file

_SYSTEM_PROMPT = (
    "You are a precise software engineer. Fix the bug described in the issue. "
    "Return ONLY the complete corrected file — no explanation, no markdown fences."
)


def _strip_fences(text: str) -> str:
    """Remove leading/trailing markdown code fences if the model adds them."""
    text = text.strip()
    text = re.sub(r"^```[a-zA-Z]*\n", "", text)
    text = re.sub(r"\n```$", "", text)
    return text.strip()


class LocalTransformersAgent:
    """Repair agent backed by a local HuggingFace model.

    Parameters
    ----------
    model_id:
        HuggingFace model ID, e.g. ``'microsoft/Phi-3.5-mini-instruct'``.
        Defaults to ``SAFETRACE_LOCAL_MODEL`` env var or the 1.5B default.
    device_map:
        ``'auto'`` distributes across all GPUs; ``'cpu'`` forces CPU.
    load_in_4bit:
        Enable 4-bit quantization (requires ``bitsandbytes``). Reduces VRAM
        usage by ~4x with minimal quality loss. Recommended for 7B+ models.
    load_in_8bit:
        Enable 8-bit quantization. Less aggressive than 4-bit.
    max_new_tokens:
        Maximum tokens to generate per patch.
    temperature:
        Sampling temperature (0.0 = greedy).
    """

    def __init__(
        self,
        model_id: Optional[str] = None,
        device_map: str = "auto",
        load_in_4bit: bool = False,
        load_in_8bit: bool = False,
        max_new_tokens: int = 2048,
        temperature: float = 0.1,
    ) -> None:
        self.model_id = model_id or os.environ.get(
            "SAFETRACE_LOCAL_MODEL", "microsoft/Phi-3.5-mini-instruct"
        )
        self.model = self.model_id  # attribute name expected by run_eval.py
        self.device_map = device_map
        self.load_in_4bit = load_in_4bit
        self.load_in_8bit = load_in_8bit
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature

        self._pipeline: Any = None

    # ── model loading ─────────────────────────────────────────────────────────

    def _get_pipeline(self) -> Any:
        if self._pipeline is not None:
            return self._pipeline

        try:
            import torch
            from transformers import AutoTokenizer, pipeline
        except ImportError as exc:
            raise RuntimeError(
                "transformers/torch not installed. "
                "Run: pip install 'safetrace[gpu]'"
            ) from exc

        kwargs: dict[str, Any] = {
            "model": self.model_id,
            "task": "text-generation",
            "device_map": self.device_map,
            "trust_remote_code": True,
        }

        if self.load_in_4bit or self.load_in_8bit:
            try:
                from transformers import BitsAndBytesConfig
                bnb_cfg = BitsAndBytesConfig(
                    load_in_4bit=self.load_in_4bit,
                    load_in_8bit=self.load_in_8bit,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4",
                )
                kwargs["quantization_config"] = bnb_cfg
            except ImportError:
                print(
                    "[LocalAgent] bitsandbytes not installed — skipping quantization. "
                    "Run: pip install bitsandbytes"
                )

        self._pipeline = pipeline(**kwargs)
        return self._pipeline

    # ── agent interface ───────────────────────────────────────────────────────

    def retrieve_context(self, task: TaskSpec) -> str:
        parts: list[str] = []
        try:
            parts.append(f"=== issue.md ===\n{read_file(task.issue_path)}")
        except OSError:
            pass
        for fname in sorted(os.listdir(task.repo_path)):
            if fname.endswith(".py") and not fname.startswith("test_"):
                try:
                    parts.append(
                        f"=== {fname} ===\n"
                        + read_file(os.path.join(task.repo_path, fname))
                    )
                except OSError:
                    pass
        return "\n\n".join(parts)

    def generate_patch(
        self, task: TaskSpec, context: str, feedback: Optional[str] = None
    ) -> PatchResult:
        issue = read_file(task.issue_path)
        src_files = sorted(
            f for f in os.listdir(task.repo_path)
            if f.endswith(".py") and not f.startswith("test_")
        )
        target_file = src_files[0] if src_files else "main.py"
        original = read_file(os.path.join(task.repo_path, target_file))

        user_msg = (
            f"Issue:\n{issue}\n\n"
            f"File to fix ({target_file}):\n{original}"
        )
        if feedback:
            user_msg += f"\n\nYour previous attempt failed tests:\n{feedback}"

        messages = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ]

        pipe = self._get_pipeline()

        # apply_chat_template is preferred but not all pipelines expose it directly
        try:
            tokenizer = pipe.tokenizer
            formatted = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            out = pipe(
                formatted,
                max_new_tokens=self.max_new_tokens,
                temperature=self.temperature,
                do_sample=self.temperature > 0,
                return_full_text=False,
            )
            patch_content = out[0]["generated_text"]
        except Exception:
            # Fallback: pass messages directly if pipeline supports it
            out = pipe(
                messages,
                max_new_tokens=self.max_new_tokens,
                temperature=self.temperature,
                do_sample=self.temperature > 0,
            )
            patch_content = out[0]["generated_text"][-1]["content"]

        patch_content = _strip_fences(patch_content)
        diff = get_diff(original, patch_content, target_file)
        added = sum(
            1 for l in diff.splitlines()
            if l.startswith("+") and not l.startswith("+++")
        )
        removed = sum(
            1 for l in diff.splitlines()
            if l.startswith("-") and not l.startswith("---")
        )

        return PatchResult(
            patch_id=f"{task.task_id}_local_{datetime.utcnow().strftime('%H%M%S')}",
            files_changed=[target_file],
            lines_added=added,
            lines_removed=removed,
            diff=diff,
            applied_at=datetime.utcnow(),
        )

    def self_review(self, patch: PatchResult, task: TaskSpec) -> str:
        pipe = self._get_pipeline()
        messages = [
            {"role": "system", "content": "You are a security code reviewer. Be concise."},
            {"role": "user", "content": f"Review this patch for security issues:\n{patch.diff}"},
        ]
        try:
            tokenizer = pipe.tokenizer
            formatted = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            out = pipe(formatted, max_new_tokens=512, temperature=0.0, do_sample=False, return_full_text=False)
            return out[0]["generated_text"]
        except Exception:
            out = pipe(messages, max_new_tokens=512, temperature=0.0, do_sample=False)
            return out[0]["generated_text"][-1]["content"]

    # ── convenience ───────────────────────────────────────────────────────────

    def device_info(self) -> str:
        """Return a human-readable description of the active device."""
        try:
            import torch
            if self.device_map == "auto":
                if torch.cuda.is_available():
                    names = [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())]
                    return f"CUDA × {len(names)}: {', '.join(names)}"
                if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                    return "Apple MPS"
            return "CPU"
        except ImportError:
            return "CPU"
