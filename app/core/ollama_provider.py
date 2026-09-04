import os

import requests


class OllamaProvider:
    """Connection layer between SOUL FORGE and Ollama."""

    def __init__(self, base_url=None, model=None):
        self.base_url = (
            base_url
            or os.getenv(
                "OLLAMA_BASE_URL",
                "http://127.0.0.1:11434",
            )
        ).rstrip("/")

        self.model = (
            model
            or os.getenv(
                "OLLAMA_MODEL",
                "qwen3:latest",
            )
        )

    def health(self):
        """Return True when Ollama is reachable."""

        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5,
            )

            return response.ok

        except requests.RequestException:
            return False

    def models(self):
        """Return available Ollama model names."""

        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=10,
            )

            response.raise_for_status()

            data = response.json()

            return [
                item.get("name")
                for item in data.get("models", [])
                if item.get("name")
            ]

        except (
            requests.RequestException,
            ValueError,
        ):
            return []

    def model_available(self):
        """Return True when the configured model exists."""

        return self.model in self.models()

    def generate(self, prompt, system=None):
        """Generate a response from the configured Ollama model."""

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        if system:
            payload["system"] = system

        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=300,
        )

        response.raise_for_status()

        data = response.json()

        return data.get("response", "")

    def status(self):
        """Return complete Ollama/model status."""

        reachable = self.health()

        if not reachable:
            return {
                "connected": False,
                "model": self.model,
                "model_available": False,
                "base_url": self.base_url,
            }

        available = self.model_available()

        return {
            "connected": True,
            "model": self.model,
            "model_available": available,
            "base_url": self.base_url,
        }
