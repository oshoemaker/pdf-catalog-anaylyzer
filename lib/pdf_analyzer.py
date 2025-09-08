from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import fitz  # PyMuPDF
from tqdm import tqdm


class PDFAnalyzer:
    """Comprehensive PDF analysis and data extraction helper.

    This class encapsulates PDF loading, text extraction, basic structure analysis,
    and page image generation to support downstream vision/AI extraction.
    """

    def __init__(
        self,
        pdf_path: str | Path,
        temp_dir: Optional[str | Path] = None,
        extracted_data_dir: Optional[str | Path] = None,
    ) -> None:
        self.pdf_path: Path = Path(pdf_path)
        self.temp_dir: Path = Path(temp_dir) if temp_dir else self.pdf_path.parent / "temp"
        self.extracted_data_dir: Path = (
            Path(extracted_data_dir) if extracted_data_dir else self.pdf_path.parent / "extracted_data"
        )

        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.extracted_data_dir.mkdir(parents=True, exist_ok=True)

        self.pdf_doc: Optional[fitz.Document] = None
        self.pages_data: List[Dict[str, Any]] = []
        self.extracted_text: str = ""

    def load_pdf(self) -> bool:
        """Load the PDF file into memory."""
        try:
            self.pdf_doc = fitz.open(str(self.pdf_path))
            return True
        except Exception:
            self.pdf_doc = None
            return False

    def extract_basic_info(self) -> Optional[Dict[str, Any]]:
        """Extract basic PDF metadata and structure."""
        if not self.pdf_doc:
            return None

        metadata = self.pdf_doc.metadata
        info: Dict[str, Any] = {
            "filename": self.pdf_path.name,
            "page_count": len(self.pdf_doc),
            "title": metadata.get("title", "N/A"),
            "author": metadata.get("author", "N/A"),
            "subject": metadata.get("subject", "N/A"),
            "creator": metadata.get("creator", "N/A"),
            "producer": metadata.get("producer", "N/A"),
        }
        return info

    def extract_text_by_page(self) -> List[Dict[str, Any]]:
        """Extract text from each page with position information."""
        if not self.pdf_doc:
            return []

        pages_text: List[Dict[str, Any]] = []
        for page_num in tqdm(range(len(self.pdf_doc)), desc="Extracting text"):
            page = self.pdf_doc[page_num]
            text_dict = page.get_text("dict")
            page_data = {
                "page_number": page_num + 1,
                "raw_text": page.get_text(),
                "text_blocks": text_dict.get("blocks", []),
                "page_size": tuple(page.rect),
            }
            pages_text.append(page_data)

        self.pages_data = pages_text
        self.extracted_text = "\n\n".join(p["raw_text"] for p in pages_text)
        return pages_text

    def iter_pages(self, render_image: bool = True, high_quality: bool = False) -> Any:
        """Yield per-page dicts with text and optionally render a page image.

        Set render_image=False to avoid creating images unless explicitly requested
        via render_page_image().
        """
        if not self.pdf_doc:
            return
        total_pages = len(self.pdf_doc)
        for page_num in range(total_pages):
            page = self.pdf_doc[page_num]
            text_dict = page.get_text("dict")
            page_data = {
                "page_number": page_num + 1,
                "raw_text": page.get_text(),
                "text_blocks": text_dict.get("blocks", []),
                "page_size": tuple(page.rect),
            }

            if render_image:
                mat = fitz.Matrix(2.0, 2.0) if high_quality else fitz.Matrix(1.5, 1.5)
                pix = page.get_pixmap(matrix=mat)
                temp_img_path = self.temp_dir / f"page_{page_num + 1}.png"
                pix.save(str(temp_img_path))
                pix = None
                page_data["temp_image_path"] = str(temp_img_path)

            yield page_data

    def render_page_image(self, page_number: int, high_quality: bool = False) -> Path:
        """Render and save a single page image and return its path."""
        if not self.pdf_doc:
            raise RuntimeError("PDF not loaded")
        if page_number < 1 or page_number > len(self.pdf_doc):
            raise ValueError("Invalid page number")
        page = self.pdf_doc[page_number - 1]
        mat = fitz.Matrix(2.0, 2.0) if high_quality else fitz.Matrix(1.5, 1.5)
        pix = page.get_pixmap(matrix=mat)
        temp_img_path = self.temp_dir / f"page_{page_number}.png"
        pix.save(str(temp_img_path))
        pix = None
        return temp_img_path

    def detect_tables_and_images(self, high_quality: bool = False, max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        """Detect tables and images, and create per-page images.

        Note: If max_pages is None, all pages will be processed.
        """
        if not self.pdf_doc:
            return []

        elements: List[Dict[str, Any]] = []
        total_pages = len(self.pdf_doc)
        pages_to_process = min(max_pages, total_pages) if (max_pages and max_pages < total_pages) else total_pages

        for page_num in tqdm(range(pages_to_process), desc="Processing pages"):
            page = self.pdf_doc[page_num]
            image_list = page.get_images()

            if high_quality:
                mat = fitz.Matrix(2.0, 2.0)
            else:
                mat = fitz.Matrix(1.5, 1.5)

            pix = page.get_pixmap(matrix=mat)
            temp_img_path = self.temp_dir / f"page_{page_num + 1}.png"
            pix.save(str(temp_img_path))
            pix = None  # free memory

            text_length = len(page.get_text().strip())
            has_substantial_text = text_length > 50

            page_elements = {
                "page_number": page_num + 1,
                "embedded_images": len(image_list),
                "image_details": image_list,
                "temp_image_path": str(temp_img_path),
                "text_length": text_length,
                "has_substantial_text": has_substantial_text,
                "extraction_strategy": "text" if has_substantial_text else "vision",
            }
            elements.append(page_elements)

        return elements

    def get_extraction_strategy(self) -> List[Dict[str, Any]]:
        """Analyze PDF and recommend an extraction strategy for each page."""
        if not self.pages_data:
            return []

        strategies: List[Dict[str, Any]] = []
        for page_data in self.pages_data:
            page_num = page_data["page_number"]
            text_length = len(page_data["raw_text"].strip())

            if text_length > 100:
                strategy = {
                    "page": page_num,
                    "method": "text",
                    "reason": f"Substantial text content ({text_length} chars)",
                    "confidence": "high",
                }
            elif text_length > 20:
                strategy = {
                    "page": page_num,
                    "method": "hybrid",
                    "reason": f"Some text content ({text_length} chars), may benefit from vision",
                    "confidence": "medium",
                }
            else:
                strategy = {
                    "page": page_num,
                    "method": "vision",
                    "reason": f"Minimal text content ({text_length} chars), likely image-based",
                    "confidence": "high",
                }
            strategies.append(strategy)

        return strategies

    def detect_product_data_pages(self) -> List[Dict[str, Any]]:
        """Detect which pages contain product data vs introductory content."""
        if not self.pages_data:
            return []

        product_pages: List[Dict[str, Any]] = []
        for page_data in self.pages_data:
            page_num = page_data["page_number"]
            text = page_data["raw_text"].lower()

            product_indicators = [
                "model",
                "years",
                "specification",
                "part",
                "inner",
                "outer",
                "side",
                "left",
                "right",
                "front",
                "rear",
                "fitment",
                "86-",
                "87-",
                "88-",
                "89-",
                "toyota",
                "honda",
                "ford",
                "chevrolet",
                "nissan",
                "acura",
                "lexus",
                "mazda",
                "subaru",
                "volkswagen",
            ]

            intro_indicators = [
                "table of contents",
                "introduction",
                "warning",
                "copyright",
                "how to use",
                "installation",
                "technical information",
                "about this catalog",
                "index",
                "notes",
            ]

            product_score = sum(1 for indicator in product_indicators if indicator in text)
            intro_score = sum(1 for indicator in intro_indicators if indicator in text)
            has_tabular_data = self._detect_tabular_structure(text)
            has_part_numbers = len(
                [line for line in text.split("\n") if "86-" in line or "87-" in line]
            ) > 2

            if has_tabular_data and has_part_numbers:
                confidence = "high"
                is_product_page = True
            elif product_score > intro_score and product_score >= 3:
                confidence = "medium"
                is_product_page = True
            elif intro_score > product_score:
                confidence = "high"
                is_product_page = False
            else:
                confidence = "low"
                is_product_page = len(text.strip()) > 500

            page_analysis = {
                "page": page_num,
                "is_product_page": is_product_page,
                "confidence": confidence,
                "product_score": product_score,
                "intro_score": intro_score,
                "has_tabular_data": has_tabular_data,
                "has_part_numbers": has_part_numbers,
                "text_length": len(text),
            }
            product_pages.append(page_analysis)

        return product_pages

    def _detect_tabular_structure(self, text: str) -> bool:
        """Detect if text contains tabular data structure."""
        lines = text.split("\n")
        tabular_indicators = 0
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if "..." in line and len(line.split("...")) > 1:
                tabular_indicators += 1

            numbers = len([word for word in line.split() if word.replace("-", "").isdigit()])
            if numbers >= 3:
                tabular_indicators += 1

            if "86-" in line or "87-" in line:
                tabular_indicators += 1

        return tabular_indicators >= 5

    def save_extracted_data(self, output_path: Optional[str | Path] = None) -> Path:
        """Save extracted data to a JSON file and return the output path."""
        if output_path is None:
            output_path = self.extracted_data_dir / f"{self.pdf_path.stem}_extracted.json"

        data = {
            "pdf_info": self.extract_basic_info(),
            "pages_data": self.pages_data,
            "full_text": self.extracted_text,
        }

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        return output_path



