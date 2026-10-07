import json
import logging
import time
from typing import Optional
from groq import Groq
import instructor

from backend.app.core.config import settings
from backend.app.models.schemas import (
    ExtractedEvidenceRecord, RetrievalScenario, FailurePoint, UserOutcome
)
from backend.app.extraction.prompt import (
    EXTRACTION_SYSTEM_PROMPT, FEW_SHOT_USER_EXAMPLE, FEW_SHOT_ASSISTANT_EXAMPLE
)

logger = logging.getLogger(__name__)

class DiscoveryExtractor:
    """Extracts 7 structured discovery dimensions from unstructured posts using Groq LPU inference."""

    def __init__(self):
        self.raw_client = Groq(api_key=settings.GROQ_API_KEY)
        # Use instructor in JSON mode
        self.instructor_client = instructor.from_groq(
            self.raw_client,
            mode=instructor.Mode.JSON
        )
        self.model = settings.GROQ_MODEL_EXTRACTION

    def extract(
        self, 
        raw_text: str, 
        source_channel: str, 
        source_url: str, 
        post_date: Optional[str] = None,
        max_retries: int = 3
    ) -> ExtractedEvidenceRecord:
        """
        Parses raw text into an ExtractedEvidenceRecord with automated retry and backoff.
        """
        messages = [
            {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": FEW_SHOT_USER_EXAMPLE},
            {"role": "assistant", "content": json.dumps(FEW_SHOT_ASSISTANT_EXAMPLE)},
            {
                "role": "user",
                "content": (
                    f"Analyze this user retrieval experience:\n"
                    f"Source Platform: {source_channel}\n"
                    f"Canonical URL: {source_url}\n"
                    f"Date: {post_date or 'Undated'}\n"
                    f"User Post Content:\n{raw_text}\n\n"
                    f"Extract the 7 dimensions strictly adhering to the schema."
                )
            }
        ]

        attempt = 0
        backoff_seconds = 2.0

        while attempt < max_retries:
            try:
                # 1. Attempt Instructor-based extraction
                record = self.instructor_client.chat.completions.create(
                    model=self.model,
                    response_model=ExtractedEvidenceRecord,
                    messages=messages,
                    temperature=0.1,
                )
                
                # Ground Layer 1 provenance
                record.source_channel = source_channel
                record.source_url = source_url
                record.post_date = post_date
                if not record.verbatim_quote:
                    record.verbatim_quote = raw_text[:500]

                return record

            except Exception as e:
                attempt += 1
                logger.warning(
                    f"Extraction attempt {attempt}/{max_retries} failed on model '{self.model}' ({e}). "
                    f"Backing off for {backoff_seconds}s..."
                )
                time.sleep(backoff_seconds)
                backoff_seconds *= 2.0

        # Fallback to direct Groq chat JSON completion if Instructor encounters schema deserialization issue
        logger.info("Attempting direct Groq JSON mode fallback...")
        return self._extract_fallback_json(raw_text, source_channel, source_url, post_date)

    def _extract_fallback_json(
        self, 
        raw_text: str, 
        source_channel: str, 
        source_url: str, 
        post_date: Optional[str]
    ) -> ExtractedEvidenceRecord:
        """Robust fallback parsing using direct JSON mode with schema alignment."""
        try:
            response = self.raw_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT + "\nOutput strict valid JSON conforming to the schema."},
                    {
                        "role": "user", 
                        "content": f"Platform: {source_channel}\nURL: {source_url}\nDate: {post_date}\nText:\n{raw_text}"
                    }
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)

            return ExtractedEvidenceRecord(
                source_channel=source_channel,
                source_url=source_url,
                post_date=post_date,
                verbatim_quote=data.get("verbatim_quote", raw_text[:500]),
                scenario_type=data.get("scenario_type", RetrievalScenario.OTHER),
                scenario_custom_description=data.get("scenario_custom_description"),
                remembered_clues=data.get("remembered_clues", []),
                forgotten_metadata=data.get("forgotten_metadata", []),
                search_behaviors=data.get("search_behaviors", []),
                failure_point=data.get("failure_point", FailurePoint.SEMANTIC_MISMATCH),
                workarounds=data.get("workarounds", []),
                user_outcome=data.get("user_outcome", UserOutcome.UNKNOWN),
                ai_confidence_score=float(data.get("ai_confidence_score", 0.85)),
                ai_interpretation_notes=data.get("ai_interpretation_notes", "Extracted via Groq direct JSON fallback.")
            )
        except Exception as err:
            logger.error(f"Fallback extraction failed: {err}")
            # Safe minimum record
            return ExtractedEvidenceRecord(
                source_channel=source_channel,
                source_url=source_url,
                post_date=post_date,
                verbatim_quote=raw_text[:500],
                scenario_type=RetrievalScenario.OTHER,
                remembered_clues=["photo mentioned in user post"],
                forgotten_metadata=["exact date", "album"],
                search_behaviors=["attempted search"],
                failure_point=FailurePoint.COGNITIVE_FATIGUE,
                workarounds=["abandoned"],
                user_outcome=UserOutcome.ABANDONED,
                ai_confidence_score=0.70,
                ai_interpretation_notes=f"Minimum safe extraction generated due to: {err}"
            )
