from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .pdf_analyzer import PDFAnalyzer
from .ai_extraction import AIDataExtractor
from .advanced_document_ai import AdvancedDocumentAI


def process_document(
    pdf_path: str | Path,
    temp_dir: Optional[str | Path] = None,
    extracted_data_dir: Optional[str | Path] = None,
    catalog_type: str = "automotive",
    use_openai: bool = True,
    use_gemini: bool = False,
    use_advanced_ai: bool = True,
    high_quality_images: bool = False,
    max_pages: Optional[int] = None,
    extraction_prompt: Optional[str] = None,
    minimize_memory: bool = False,
) -> Dict[str, Any]:
    """End-to-end processing of an entire PDF in a memory-safe sequential loop.

    Always iterates over all pages (or up to max_pages if provided) and returns
    a dictionary containing extracted items and basic info.
    """
    analyzer = PDFAnalyzer(pdf_path, temp_dir=temp_dir, extracted_data_dir=extracted_data_dir)
    if not analyzer.load_pdf():
        return {"success": False, "error": "Failed to load PDF"}

    pdf_info = analyzer.extract_basic_info() or {}

    # Extract text and basic per-page structures
    pages_data = analyzer.extract_text_by_page()

    # Ensure per-page images exist for vision unless minimizing memory
    if not minimize_memory:
        analyzer.detect_tables_and_images(high_quality=high_quality_images, max_pages=max_pages)

    # Simple heuristic to identify likely product pages
    product_pages_analysis = analyzer.detect_product_data_pages()

    # Hybrid AI extraction across pages
    extractor = AIDataExtractor(use_openai=use_openai, use_gemini=use_gemini)
    extracted_items = extractor.extract_hybrid_data(
        pages_data=pages_data,
        temp_dir=str(analyzer.temp_dir),
        product_pages_analysis=product_pages_analysis,
        catalog_type=catalog_type,
        use_advanced_ai=use_advanced_ai and not minimize_memory,
        extraction_prompt=extraction_prompt,
    )

    return {
        "success": True,
        "pdf_info": pdf_info,
        "items": extracted_items,
        "pages": len(pages_data),
    }


def process_document_streaming(
    pdf_path: str | Path,
    temp_dir: Optional[str | Path] = None,
    extracted_data_dir: Optional[str | Path] = None,
    extraction_prompt: Optional[str] = None,
    catalog_type: str = "automotive",
    use_openai: bool = True,
    use_gemini: bool = False,
    use_advanced_ai: bool = True,
    high_quality_images: bool = False,
    minimize_memory: bool = False,
    verbose: bool = True,
) -> Dict[str, Any]:
    """Memory-safe, page-by-page streaming processing.

    Generates and processes one page at a time, releasing intermediate objects promptly.
    """
    analyzer = PDFAnalyzer(pdf_path, temp_dir=temp_dir, extracted_data_dir=extracted_data_dir)
    if not analyzer.load_pdf():
        return {"success": False, "error": "Failed to load PDF"}

    pdf_info = analyzer.extract_basic_info() or {}
    total_pages = pdf_info.get("page_count", 0)
    extractor = AIDataExtractor(use_openai=use_openai, use_gemini=use_gemini)

    # Create a single shared AdvancedDocumentAI instance to reuse across pages
    shared_advanced_ai: Optional[AdvancedDocumentAI] = None
    if use_advanced_ai and not minimize_memory:
        try:
            shared_advanced_ai = AdvancedDocumentAI(
                enable_trocr=False,
                enable_paddleocr=True,
                enable_easyocr=False,
                torch_threads=1,
            )
        except Exception:
            shared_advanced_ai = None

    if verbose:
        mode_desc = "low-memory" if minimize_memory else "standard"
        llms = []
        if use_openai:
            llms.append("OpenAI")
        if use_gemini:
            llms.append("Gemini")
        print(
            f"Streaming {total_pages} pages in {mode_desc} mode using {', '.join(llms) if llms else 'no LLMs'}...",
            flush=True,
        )

    all_items: List[Dict[str, Any]] = []
    processed_pages = 0
    for page_data in analyzer.iter_pages(render_image=not minimize_memory):
        processed_pages += 1
        # Lightweight product-page heuristic on the fly
        text = page_data.get("raw_text", "").lower()
        is_candidate = (
            ("86-" in text or "87-" in text) or (len(text) > 100 and any(k in text for k in ["model", "years", "part"]))
        )

        if verbose:
            page_num = page_data.get("page_number", processed_pages)
            print(
                f"Page {page_num}/{total_pages}: candidate={bool(is_candidate)} text_len={len(text)}",
                flush=True,
            )

        selected_pages = [page_data] if is_candidate else [page_data]  # still process all pages

        # If minimizing memory and image not rendered, render only for candidate pages
        if minimize_memory and is_candidate and not page_data.get("temp_image_path"):
            try:
                temp_image_path = analyzer.render_page_image(page_number=page_data["page_number"], high_quality=False)
                page_data["temp_image_path"] = str(temp_image_path)
                if verbose:
                    print(
                        f"  Rendered image for page {page_data['page_number']} -> {temp_image_path.name}",
                        flush=True,
                    )
            except Exception:
                pass
        items = extractor.extract_hybrid_data(
            pages_data=selected_pages,
            temp_dir=str(analyzer.temp_dir),
            product_pages_analysis=None,
            catalog_type=catalog_type,
            use_advanced_ai=use_advanced_ai and not minimize_memory,
            extraction_prompt=extraction_prompt,
            shared_advanced_ai=shared_advanced_ai,
        )
        if items:
            all_items.extend(items)
        if verbose:
            print(
                f"  Extracted {len(items) if items else 0} items this page | Total so far: {len(all_items)}",
                flush=True,
            )

        # Drop large references explicitly
        del selected_pages
        del items

    return {"success": True, "pdf_info": pdf_info, "items": all_items, "pages": pdf_info.get("page_count", 0)}


