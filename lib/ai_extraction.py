from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import google.generativeai as genai
import openai

from .advanced_document_ai import AdvancedDocumentAI


class AIDataExtractor:
    """AI-powered data extraction and validation with optional vision capabilities."""

    def __init__(self, use_openai: bool = True, use_gemini: bool = False) -> None:
        self.openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        self.google_api_key: Optional[str] = os.getenv("GOOGLE_API_KEY")

        self.use_openai: bool = bool(use_openai and self.openai_api_key)
        self.use_gemini: bool = bool(use_gemini and self.google_api_key)

        self._openai_client: Optional[openai.OpenAI] = None
        self._gemini_model = None
        self._gemini_vision_model = None

        if self.use_openai:
            self._openai_client = openai.OpenAI(api_key=self.openai_api_key)

        if self.use_gemini:
            genai.configure(api_key=self.google_api_key)
            # Use Gemini 2.5 Pro for superior contextual understanding
            self._gemini_model = genai.GenerativeModel("gemini-2.5-pro")
            self._gemini_vision_model = genai.GenerativeModel("gemini-2.5-pro")

    # ---------- Core text extraction ----------
    def extract_structured_data(
        self,
        text: str,
        extraction_prompt: Optional[str] = None,
        catalog_type: str = "general",
    ) -> Optional[str]:
        """Extract structured data from plain text using the selected AI service.

        Returns the raw AI response string (which may contain JSON). Use
        validate_extracted_data() to parse into Python data structures.
        """
        if not extraction_prompt:
            # Require explicit prompt from caller for clarity
            return None

        if self.use_openai:
            return self._extract_with_openai(text, extraction_prompt)
        if self.use_gemini:
            return self._extract_with_gemini(text, extraction_prompt)
        return None

    def _extract_with_openai(self, text: str, prompt: str) -> Optional[str]:
        try:
            if not self._openai_client:
                return None
            response = self._openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert at extracting structured data from catalog documents."},
                    {"role": "user", "content": f"{prompt}\n\nText to analyze:\n{text[:8000]}"},
                ],
                temperature=0.1,
            )
            return response.choices[0].message.content
        except Exception:
            return None

    def _extract_with_gemini(self, text: str, prompt: str) -> Optional[str]:
        try:
            if not self._gemini_model:
                return None
            full_prompt = f"{prompt}\n\nText to analyze:\n{text[:8000]}"
            response = self._gemini_model.generate_content(full_prompt)
            return response.text
        except Exception:
            return None

    # ---------- Validation ----------
    def validate_extracted_data(self, extracted_text: str) -> Optional[Any]:
        """Attempt to parse a JSON array/object from an AI response string."""
        try:
            cleaned = extracted_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned.replace("```json", "").replace("```", "").strip()
            elif cleaned.startswith("```"):
                lines = cleaned.split("\n")
                if lines and lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                cleaned = "\n".join(lines).strip()

            import re  # local import to keep module lightweight on import

            match = re.search(r"(\[.*?\])", cleaned, re.DOTALL)
            if match:
                return json.loads(match.group(1))

            match = re.search(r"(\{.*?\})", cleaned, re.DOTALL)
            if match:
                return json.loads(match.group(1))

            return json.loads(cleaned)
        except Exception:
            return None

    # ---------- Vision extraction ----------
    def extract_from_image(self, image_path: str, extraction_prompt: Optional[str] = None) -> Optional[str]:
        if not extraction_prompt:
            return None

        if self.use_openai:
            return self._extract_image_with_openai(image_path, extraction_prompt)
        if self.use_gemini:
            return self._extract_image_with_gemini(image_path, extraction_prompt)
        return None

    def _extract_image_with_openai(self, image_path: str, prompt: str) -> Optional[str]:
        try:
            if not self._openai_client:
                return None
            import base64

            with open(image_path, "rb") as f:
                base64_image = base64.b64encode(f.read()).decode("utf-8")

            response = self._openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}},
                        ],
                    }
                ],
                temperature=0.1,
                max_tokens=2000,
            )
            return response.choices[0].message.content
        except Exception:
            return None

    def _extract_image_with_gemini(self, image_path: str, prompt: str) -> Optional[str]:
        try:
            from PIL import Image

            image = Image.open(image_path)
            if not self._gemini_vision_model:
                return None
            response = self._gemini_vision_model.generate_content([prompt, image])
            return response.text
        except Exception:
            return None

    # ---------- Hybrid (text + vision) ----------
    def extract_hybrid_data(
        self,
        pages_data: List[Dict[str, Any]],
        temp_dir: str | Path,
        product_pages_analysis: Optional[List[Dict[str, Any]]] = None,
        catalog_type: str = "automotive",
        use_advanced_ai: bool = True,
        extraction_prompt: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Run hybrid extraction across provided pages_data sequentially (memory-safe)."""
        all_items: List[Dict[str, Any]] = []

        advanced_ai: Optional[AdvancedDocumentAI] = None
        if use_advanced_ai:
            try:
                # Disable TrOCR by default to avoid kernel crashes; can be enabled later
                advanced_ai = AdvancedDocumentAI(enable_trocr=False, enable_paddleocr=True, enable_easyocr=True)
            except Exception:
                advanced_ai = None

        if product_pages_analysis:
            product_page_nums = {p["page"] for p in product_pages_analysis if p.get("is_product_page")}
            pages_to_process = [p for p in pages_data if p.get("page_number") in product_page_nums]
        else:
            pages_to_process = pages_data

        temp_dir = Path(temp_dir)
        for page_data in pages_to_process:
            page_num = page_data["page_number"]
            raw_text = page_data.get("raw_text", "")
            temp_img_path = temp_dir / f"page_{page_num}.png"

            extracted_items: List[Dict[str, Any]] = []

            if advanced_ai and temp_img_path.exists():
                try:
                    multimodal_result = advanced_ai.extract_with_layoutlm_style(str(temp_img_path), raw_text)
                    enhanced_text = multimodal_result.get("combined_text", raw_text) or raw_text
                    text_result = self.extract_structured_data(
                        enhanced_text,
                        extraction_prompt=extraction_prompt,
                        catalog_type=catalog_type,
                    )
                    if text_result:
                        text_data = self.validate_extracted_data(text_result)
                        if isinstance(text_data, list) and text_data:
                            extracted_items.extend(text_data)
                except Exception:
                    pass

            if not extracted_items and len(raw_text.strip()) > 100:
                text_result = self.extract_structured_data(
                    raw_text,
                    extraction_prompt=extraction_prompt,
                    catalog_type=catalog_type,
                )
                if text_result:
                    text_data = self.validate_extracted_data(text_result)
                    if isinstance(text_data, list) and text_data:
                        extracted_items.extend(text_data)

            if not extracted_items and temp_img_path.exists():
                vision_result = self.extract_from_image(str(temp_img_path), extraction_prompt=extraction_prompt)
                if vision_result:
                    vision_data = self.validate_extracted_data(vision_result)
                    if isinstance(vision_data, list) and vision_data:
                        extracted_items.extend(vision_data)

            if extracted_items:
                all_items.extend(extracted_items)

        return all_items


