# -*- coding: utf-8 -"""
Multimodal Agent for ERP AI Pro
Handles all image-based processing and analysis.
"""

import logging
from typing import Dict, Any

import numpy as np
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration, CLIPProcessor, CLIPModel
import easyocr
import structlog

# This import will be updated later when config is centralized.
from erp_ai_pro.core.config import SystemConfig

logger = structlog.get_logger()


class MultimodalProcessor:
    """Handles multimodal content processing."""

    def __init__(self, config: EnhancedRAGConfig):
        self.config = config
        self.setup_models()

    def setup_models(self):
        """Initialize multimodal models."""
        # BLIP for image captioning
        self.blip_processor = BlipProcessor.from_pretrained(self.config.vision_model_name)
        self.blip_model = BlipForConditionalGeneration.from_pretrained(self.config.vision_model_name)

        # CLIP for image understanding
        self.clip_processor = CLIPProcessor.from_pretrained(self.config.clip_model_name)
        self.clip_model = CLIPModel.from_pretrained(self.config.clip_model_name)

        # OCR engines
        self.easyocr_reader = easyocr.Reader(['en', 'vi'])

        logger.info("Multimodal models initialized successfully")

    async def process_image(self, image_path: str) -> Dict[str, Any]:
        """Process image and extract information."""
        try:
            # Load image
            image = Image.open(image_path).convert('RGB')

            # Generate caption
            inputs = self.blip_processor(image, return_tensors="pt")
            out = self.blip_model.generate(**inputs, max_length=100)
            caption = self.blip_processor.decode(out[0], skip_special_tokens=True)

            # Extract text using OCR
            ocr_text = self.easyocr_reader.readtext(np.array(image), detail=0)

            # Get image embeddings
            clip_inputs = self.clip_processor(images=image, return_tensors="pt")
            image_features = self.clip_model.get_image_features(**clip_inputs)

            return {
                "caption": caption,
                "ocr_text": " ".join(ocr_text) if ocr_text else "",
                "image_embeddings": image_features.detach().numpy().tolist(),
                "image_type": "chart" if self._is_chart(image) else "document"
            }

        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return {"error": str(e)}

    def _is_chart(self, image: Image.Image) -> bool:
        """Detect if image is a chart/graph."""
        # Simple heuristic - can be improved with specialized models
        np_image = np.array(image)
        return len(np.unique(np_image)) > 100  # Charts typically have many colors


class MultimodalAgent:
    """
    The specialized agent for handling multimodal queries.
    It uses the MultimodalProcessor to understand image content.
    """

    def __init__(self, config: EnhancedRAGConfig):
        self.processor = MultimodalProcessor(config)
        logger.info("MultimodalAgent initialized.")

    async def execute(self, image_path: str, question: str) -> Dict[str, Any]:
        """
        The main execution method for this agent.
        It processes the image and prepares a response or context for another agent.
        """
        logger.info(f"MultimodalAgent executing for image: {image_path}")
        
        image_data = await self.processor.process_image(image_path)

        if "error" in image_data:
            return {"answer": f"Sorry, I couldn't process the image. Error: {image_data['error']}"}

        context_summary = (
            f"The user has uploaded an image. My analysis is as follows:\n"
            f"Image Type: {image_data.get('image_type')}\n"
            f"Generated Caption: {image_data.get('caption')}\n"
            f"Text extracted via OCR: {image_data.get('ocr_text')}"
        )

        return {
            "status": "success",
            "image_analysis": image_data,
            "context_for_next_agent": context_summary,
            "answer": f"I have analyzed the image. It appears to be a {image_data.get('image_type')} with the caption: '{image_data.get('caption')}'. Now, how can I help you with this in relation to your question: '{question}'?"
        }
