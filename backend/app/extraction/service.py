import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.app.core.database import SessionLocal
from backend.app.models.orm_models import RawPost, ExtractedEvidence
from backend.app.extraction.extractor import DiscoveryExtractor

logger = logging.getLogger(__name__)

class ExtractionService:
    """Service orchestrating extraction of raw posts into structured evidence records."""

    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
        self.extractor = DiscoveryExtractor()

    def process_pending_posts(self, batch_size: int = 10) -> Dict[str, Any]:
        """
        Pulls PENDING_EXTRACTION raw posts, extracts 7 dimensions using Groq,
        and saves them into the extracted_evidence table.
        """
        pending_posts = (
            self.db.query(RawPost)
            .filter_by(processing_status="PENDING_EXTRACTION")
            .limit(batch_size)
            .all()
        )

        results = {
            "total_pending_found": len(pending_posts),
            "successfully_processed": 0,
            "failed_count": 0,
            "evidence_ids": []
        }

        if not pending_posts:
            logger.info("No pending posts found for extraction.")
            return results

        logger.info(f"Processing batch of {len(pending_posts)} pending posts...")

        for post in pending_posts:
            try:
                date_str = post.post_created_at.strftime("%Y-%m-%d") if post.post_created_at else None

                # 1. Extract 7 discovery dimensions via Groq LPU
                record = self.extractor.extract(
                    raw_text=post.raw_text,
                    source_channel=post.source_channel,
                    source_url=post.canonical_url,
                    post_date=date_str
                )

                # 2. Persist to extracted_evidence table
                evidence = ExtractedEvidence(
                    raw_post_id=post.id,
                    scenario_type=record.scenario_type.value if hasattr(record.scenario_type, "value") else str(record.scenario_type),
                    scenario_custom_description=record.scenario_custom_description,
                    remembered_clues=record.remembered_clues,
                    forgotten_metadata=record.forgotten_metadata,
                    search_behaviors=record.search_behaviors,
                    failure_point=record.failure_point.value if hasattr(record.failure_point, "value") else str(record.failure_point),
                    workarounds=record.workarounds,
                    user_outcome=record.user_outcome.value if hasattr(record.user_outcome, "value") else str(record.user_outcome),
                    verbatim_quote=record.verbatim_quote,
                    canonical_url=record.source_url,
                    source_channel=record.source_channel,
                    post_date=record.post_date,
                    ai_confidence_score=record.ai_confidence_score,
                    ai_interpretation_notes=record.ai_interpretation_notes
                )
                self.db.add(evidence)

                # 3. Mark post as processed
                post.processing_status = "PROCESSED"
                self.db.commit()
                self.db.refresh(evidence)

                results["successfully_processed"] += 1
                results["evidence_ids"].append(evidence.id)
                logger.info(f"Successfully extracted post {post.id} -> Scenario: {evidence.scenario_type}")

            except Exception as e:
                logger.error(f"Failed to process post {post.id}: {e}")
                self.db.rollback()
                post.processing_status = "EXTRACTION_FAILED"
                self.db.commit()
                results["failed_count"] += 1

        logger.info(
            f"Extraction batch complete. Success: {results['successfully_processed']}, "
            f"Failed: {results['failed_count']}"
        )
        return results

    def close(self):
        """Closes the DB session."""
        if self.db:
            self.db.close()
