from pathlib import Path
from typing import Optional
import json

from app.utils.logger import log


class LocalAIEngine:

    def __init__(
        self,
        model_name: str = "Qwen/Qwen3-0.6B"
    ):

        self.model_name = model_name

        self.tokenizer = None
        self.model = None

        self.loaded = False

    def load(self):

        if self.loaded:
            return

        log(
            f"Loading local model: {self.model_name}"
        )

        from transformers import (
            AutoTokenizer,
            AutoModelForCausalLM,
        )

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name
        )

        self.loaded = True

        log(
            "Local AI model loaded successfully"
        )

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 512,
        temperature: float = 0.2,
    ) -> str:

        self.load()

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt"
        )

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=temperature > 0,
        )

        generated = outputs[0]

        result = self.tokenizer.decode(
            generated,
            skip_special_tokens=True
        )

        return result

    def ask(
        self,
        instruction: str
    ) -> str:

        prompt = f"""
You are BANKAI, a local AI coding agent.

You help developers understand,
design, implement, test and debug software.

Follow these rules:

1. Understand the task.
2. Inspect the available context.
3. Produce a structured plan.
4. Never invent files or project state.
5. Prefer safe, minimal changes.
6. Explain technical decisions clearly.

USER TASK:

{instruction}

Return a concise engineering response.
"""

        return self.generate(prompt)
