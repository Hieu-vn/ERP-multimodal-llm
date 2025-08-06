# -*- coding: utf-8 -*-
"""
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

from erp_ai_pro.core.config import SystemConfig

logger = structlog.get_logger()


class MultimodalProcessor:
    """Handles multimodal content processing."""

    def __init__(self, config: SystemConfig):
        self.config = config
        self.setup_models()

    def setup_models(self):
        """Initialize multimodal models."""
        try:
            # BLIP for image captioning
            self.blip_processor = BlipProcessor.from_pretrained(self.config.vision_model_name)
            self.blip_model = BlipForConditionalGeneration.from_pretrained(self.config.vision_model_name)

            # CLIP for image understanding
            self.clip_processor = CLIPProcessor.from_pretrained(self.config.clip_model_name)
            self.clip_model = CLIPModel.from_pretrained(self.config.clip_model_name)

            # OCR engines
            self.easyocr_reader = easyocr.Reader(['en', 'vi'])

            logger.info("Multimodal models initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize multimodal models: {e}")
            raise

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
        # Charts tend to have more unique colors than documents
        return len(np.unique(np_image.reshape(-1, np_image.shape[2]), axis=0)) > 200

class MultimodalAgent:
    """
    The specialized agent for handling multimodal queries.
    It uses the MultimodalProcessor to understand image content and synthesizes it with the user's question.
    """

    def __init__(self, config: SystemConfig):
        self.processor = MultimodalProcessor(config)
        logger.info("MultimodalAgent initialized.")

    async def execute(self, image_path: str, question: str) -> Dict[str, Any]:
        """
        Processes the image, synthesizes the findings with the user's question,
        and provides a comprehensive answer.
        """
        logger.info(f"MultimodalAgent executing for image: {image_path}")
        
        image_data = await self.processor.process_image(image_path)

        if "error" in image_data:
            return {"answer": f"Sorry, I couldn't process the image. Error: {image_data['error']}"}

        # Synthesize the information into a more useful response
        summary = self._create_summary(image_data, question)

        return {
            "status": "success",
            "image_analysis": image_data,
            "answer": summary
        }

    def _create_summary(self, image_data: Dict[str, Any], question: str) -> str:
        """Creates a detailed summary combining image analysis and the user's question."""
        
        image_type = image_data.get('image_type', 'unknown')
        caption = image_data.get('caption', 'No caption generated.')
        ocr_text = image_data.get('ocr_text', '').strip()

        summary = f"I have analyzed the uploaded {image_type}. Here's what I found:\n\n"
        summary += f"**Image Caption:**\n> {caption}\n\n"

        if ocr_text:
            summary += f"**Text from Image (OCR):**\n> {ocr_text}\n\n"
        else:
            summary += "**Text from Image (OCR):**\n> No text was detected in the image.\n\n"

        summary += f"**Regarding your question: '{question}'**\n"

        # Basic synthesis logic
        if "total" in question.lower() and "revenue" in question.lower() and ocr_text:
            # Try to find numbers in the OCR text
            numbers = [float(s) for s in ocr_text.split() if s.replace('.', '', 1).isdigit()]
            if numbers:
                summary += f"Based on the text in the image, the total revenue might be related to the sum of the numbers found: {sum(numbers):,.2f}."
            else:
                summary += "I couldn't find specific numbers in the image to calculate the total revenue."
        elif ocr_text:
            summary += "The text I extracted from the image may contain the answer to your question. Please review the extracted text above."
        else:
            summary += "I was unable to extract any text from the image to directly answer your question."
            
        return summary
