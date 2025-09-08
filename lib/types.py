from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ExtractionApproach(str, Enum):
    BASELINE_OCR = "baseline_ocr"
    HYBRID_GEMINI = "hybrid_gemini"
    HYBRID_OPENAI = "hybrid_openai"
    FULL_AI_INTEGRATION = "full_ai_integration"


@dataclass
class ExtractionMetrics:
    approach: ExtractionApproach
    success: bool
    processing_time: float
    memory_usage_mb: Optional[float] = None
    api_calls_made: int = 0
    tokens_used: int = 0
    estimated_cost_usd: float = 0.0
    items_extracted: int = 0
    fields_populated: int = 0
    total_possible_fields: int = 0
    completeness_score: float = 0.0
    errors_encountered: List[str] = field(default_factory=list)
    retry_attempts: int = 0
    consistency_hash: Optional[str] = None
    extracted_data: Optional[List[Dict[str, Any]]] = None
    raw_response: Optional[str] = None





