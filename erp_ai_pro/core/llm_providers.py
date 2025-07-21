import asyncio
from typing import Any, Dict

class HuggingFaceLLMProvider:
    def __init__(self, hf_pipeline):
        self.hf_pipeline = hf_pipeline

    async def generate(self, prompt: str, **kwargs) -> str:
        # Assuming the pipeline returns a list of dicts, or a single dict
        result = self.hf_pipeline(prompt, **kwargs)
        return result[0]['generated_text'] if isinstance(result, list) else result['generated_text']