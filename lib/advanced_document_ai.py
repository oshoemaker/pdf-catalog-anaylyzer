from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional


# Optional dependencies flags
try:
    import easyocr  # type: ignore
    EASYOCR_AVAILABLE = True
except Exception:
    EASYOCR_AVAILABLE = False

try:
    from paddleocr import PaddleOCR  # type: ignore
    PADDLEOCR_AVAILABLE = True
except Exception:
    PADDLEOCR_AVAILABLE = False

try:
    from transformers import TrOCRProcessor, VisionEncoderDecoderModel  # type: ignore
    TROCR_AVAILABLE = True
except Exception:
    TROCR_AVAILABLE = False

try:
    import boto3  # type: ignore
    AWS_AVAILABLE = True
except Exception:
    AWS_AVAILABLE = False

try:
    from google.cloud import vision  # type: ignore
    GCP_VISION_AVAILABLE = True
except Exception:
    GCP_VISION_AVAILABLE = False


class AdvancedDocumentAI:
    """State-of-the-art Document AI helper combining multiple OCR and cloud engines."""

    def __init__(
        self,
        enable_trocr: bool = False,
        enable_paddleocr: bool = True,
        enable_easyocr: bool = True,
        torch_threads: Optional[int] = 1,
    ) -> None:
        self.enable_trocr = enable_trocr
        self.enable_paddleocr = enable_paddleocr
        self.enable_easyocr = enable_easyocr
        self.torch_threads = torch_threads

        self.ocr_engines: Dict[str, Any] = {}
        self.cloud_services: Dict[str, Any] = {}
        self._initialize_engines()

    def _initialize_engines(self) -> None:
        # Optionally limit torch threads to reduce resource contention
        if self.torch_threads is not None:
            try:
                import torch  # type: ignore
                torch.set_num_threads(int(self.torch_threads))
            except Exception:
                pass

        if EASYOCR_AVAILABLE and self.enable_easyocr:
            try:
                self.ocr_engines["easyocr"] = easyocr.Reader(["en"])  # type: ignore
            except Exception:
                pass

        if PADDLEOCR_AVAILABLE and self.enable_paddleocr:
            try:
                self.ocr_engines["paddleocr"] = PaddleOCR(use_textline_orientation=True, lang="en")  # type: ignore
            except Exception:
                pass

        if TROCR_AVAILABLE and self.enable_trocr:
            try:
                # Suppress HuggingFace transformers weight init warnings
                try:
                    from transformers.utils import logging as hf_logging  # type: ignore
                    hf_logging.set_verbosity_error()
                except Exception:
                    pass

                # Prefer fast image processor when available for speed
                try:
                    self.ocr_engines["trocr_processor"] = TrOCRProcessor.from_pretrained(
                        "microsoft/trocr-base-printed", use_fast=True  # type: ignore[arg-type]
                    )
                except TypeError:
                    # Older transformers versions may not accept use_fast; fall back
                    self.ocr_engines["trocr_processor"] = TrOCRProcessor.from_pretrained(
                        "microsoft/trocr-base-printed"
                    )
                self.ocr_engines["trocr_model"] = VisionEncoderDecoderModel.from_pretrained(
                    "microsoft/trocr-base-printed"
                )  # type: ignore
            except Exception:
                pass

        if AWS_AVAILABLE:
            try:
                import boto3  # local import in case global failed
                self.cloud_services["textract"] = boto3.client("textract")
            except Exception:
                pass

        if GCP_VISION_AVAILABLE:
            try:
                from google.cloud import vision as gv  # type: ignore
                self.cloud_services["gcp_vision"] = gv.ImageAnnotatorClient()
            except Exception:
                pass

    # --------- OCR engines ---------
    def extract_with_advanced_ocr(self, image_path: str, method: str = "auto") -> Optional[str]:
        if method == "auto":
            if "paddleocr" in self.ocr_engines:
                method = "paddleocr"
            elif "easyocr" in self.ocr_engines:
                method = "easyocr"
            elif "trocr_processor" in self.ocr_engines:
                method = "trocr"
            else:
                return None

        try:
            if method == "paddleocr" and "paddleocr" in self.ocr_engines:
                result = self.ocr_engines["paddleocr"].ocr(image_path)
                extracted_text = []
                for line in result[0] if result and result[0] else []:
                    text, confidence = line[1]
                    if confidence > 0.5:
                        extracted_text.append(text)
                return "\n".join(extracted_text)

            if method == "easyocr" and "easyocr" in self.ocr_engines:
                result = self.ocr_engines["easyocr"].readtext(image_path)
                extracted_text = []
                for (_bbox, text, confidence) in result:
                    if confidence > 0.5:
                        extracted_text.append(text)
                return "\n".join(extracted_text)

            if method == "trocr" and "trocr_processor" in self.ocr_engines:
                from PIL import Image
                image = Image.open(image_path).convert("RGB")
                processor = self.ocr_engines["trocr_processor"]
                model = self.ocr_engines["trocr_model"]
                pixel_values = processor(image, return_tensors="pt", padding=True).pixel_values
                generated_ids = model.generate(pixel_values)
                generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
                return generated_text

        except Exception:
            return None

        return None

    # --------- Cloud services ---------
    def extract_with_cloud_services(self, image_path: str, service: str = "auto") -> Optional[Any]:
        if service == "auto":
            if "textract" in self.cloud_services:
                service = "textract"
            elif "gcp_vision" in self.cloud_services:
                service = "gcp_vision"
            else:
                return None

        try:
            if service == "textract" and "textract" in self.cloud_services:
                with open(image_path, "rb") as image_file:
                    response = self.cloud_services["textract"].analyze_document(
                        Document={"Bytes": image_file.read()},
                        FeatureTypes=["TABLES", "FORMS"],
                    )
                tables = []
                for block in response.get("Blocks", []):
                    if block.get("BlockType") == "TABLE":
                        tables.append(self._process_textract_table(block, response.get("Blocks", [])))
                return {"text": self._extract_textract_text(response.get("Blocks", [])), "tables": tables}

            if service == "gcp_vision" and "gcp_vision" in self.cloud_services:
                with open(image_path, "rb") as image_file:
                    content = image_file.read()
                image = vision.Image(content=content)  # type: ignore
                response = self.cloud_services["gcp_vision"].document_text_detection(image=image)
                if response.text_annotations:
                    return response.text_annotations[0].description
                return None

        except Exception:
            return None

        return None

    def _extract_textract_text(self, blocks: Any) -> str:
        text_blocks = []
        for block in blocks or []:
            if block.get("BlockType") == "LINE":
                text_blocks.append(block.get("Text", ""))
        return "\n".join(text_blocks)

    def _process_textract_table(self, table_block: Dict[str, Any], all_blocks: Any) -> Dict[str, Any]:
        return {"id": table_block.get("Id"), "confidence": table_block.get("Confidence", 0), "rows": []}

    # --------- Multimodal orchestration ---------
    def multi_engine_extraction(self, image_path: str) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        for method in ["paddleocr", "easyocr", "trocr"]:
            if method in self.ocr_engines or (method == "trocr" and "trocr_processor" in self.ocr_engines):
                result = self.extract_with_advanced_ocr(image_path, method)
                if result:
                    results[method] = result

        for service in ["textract", "gcp_vision"]:
            if service in self.cloud_services:
                result = self.extract_with_cloud_services(image_path, service)
                if result:
                    results[service] = result

        return results

    def get_best_extraction(self, multi_results: Dict[str, Any]) -> Optional[Any]:
        if not multi_results:
            return None
        best_result = None
        best_score = 0
        for _engine, result in multi_results.items():
            if isinstance(result, dict):
                score = len(result.get("text", "")) + len(result.get("tables", [])) * 100
            else:
                score = len(str(result))
            if score > best_score:
                best_score = score
                best_result = result
        return best_result

    def extract_with_layoutlm_style(self, image_path: str, text: Optional[str] = None) -> Dict[str, Any]:
        ocr_results = self.multi_engine_extraction(image_path)
        best_ocr_text = None
        if ocr_results:
            best_result = self.get_best_extraction(ocr_results)
            if isinstance(best_result, dict):
                best_ocr_text = best_result.get("text", "")
            else:
                best_ocr_text = str(best_result) if best_result else ""

        combined_text = text or ""
        if best_ocr_text and best_ocr_text not in combined_text:
            combined_text += f"\n\n{best_ocr_text}"

        return {
            "combined_text": combined_text,
            "ocr_results": ocr_results,
            "image_path": image_path,
            "extraction_method": "layoutlm_style_multimodal",
        }


