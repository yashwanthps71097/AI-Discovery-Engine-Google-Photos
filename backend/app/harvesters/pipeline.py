import logging
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.database import SessionLocal
from backend.app.models.orm_models import DataSource, RawPost
from backend.app.harvesters.playstore import GooglePlayStoreHarvester
from backend.app.harvesters.appstore import AppleAppStoreHarvester
from backend.app.harvesters.reddit import RedditHarvester
from backend.app.harvesters.google_community import GoogleCommunityHarvester
from backend.app.harvesters.preprocessor import DataPreprocessor
from backend.app.harvesters.relevance_gate import RelevanceGate

logger = logging.getLogger(__name__)

class IngestionPipeline:
    """Orchestrates multi-channel harvesting, deduplication, PII masking, and relevance gating."""

    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
        self.relevance_gate = RelevanceGate()
        self.harvesters = [
            GooglePlayStoreHarvester(),
            AppleAppStoreHarvester(),
            RedditHarvester(),
            GoogleCommunityHarvester()
        ]

    def _get_or_create_source(self, channel_name: str, base_url: str) -> DataSource:
        """Finds or registers the data source in the database."""
        source = self.db.query(DataSource).filter_by(channel_name=channel_name).first()
        if not source:
            source = DataSource(
                channel_name=channel_name,
                base_url=base_url,
                is_active=True,
                last_scraped_at=datetime.utcnow()
            )
            self.db.add(source)
            self.db.commit()
            self.db.refresh(source)
        else:
            source.last_scraped_at = datetime.utcnow()
            self.db.commit()
        return source

    def run_harvest(self, limit_per_channel: int = 15) -> Dict[str, Any]:
        """
        Executes end-to-end ingestion pipeline across all configured channels.
        """
        stats = {
            "total_fetched": 0,
            "duplicates_skipped": 0,
            "relevant_stored": 0,
            "rejected_noise": 0,
            "by_channel": {}
        }

        for harvester in self.harvesters:
            channel_name = harvester.channel_name
            channel_stats = {"fetched": 0, "stored": 0, "duplicates": 0, "rejected": 0}
            logger.info(f"Starting harvest for channel: {channel_name}...")

            source_record = self._get_or_create_source(
                channel_name=channel_name,
                base_url=f"https://discovery.googlephotos/{channel_name.lower().replace(' ', '_')}"
            )

            try:
                raw_posts = harvester.fetch_posts(limit=limit_per_channel)
                channel_stats["fetched"] = len(raw_posts)
                stats["total_fetched"] += len(raw_posts)

                for item in raw_posts:
                    # 1. Preprocess & Mask PII
                    sanitized_text, sanitized_author, dedup_hash = DataPreprocessor.process_raw_post(
                        raw_text=item.raw_text,
                        source_channel=item.source_channel,
                        author=item.post_author or "Anonymous User",
                        post_date=item.post_created_at
                    )

                    # 2. Check Deduplication
                    existing = self.db.query(RawPost).filter_by(deduplication_hash=dedup_hash).first()
                    if existing:
                        channel_stats["duplicates"] += 1
                        stats["duplicates_skipped"] += 1
                        continue

                    # 3. Relevance Gate
                    is_relevant, score, reasoning = self.relevance_gate.evaluate(sanitized_text)

                    status = "PENDING_EXTRACTION" if is_relevant else "REJECTED_NOISE"

                    # 4. Persist to Database
                    post_record = RawPost(
                        source_id=source_record.id,
                        source_channel=channel_name,
                        raw_text=sanitized_text,
                        canonical_url=item.canonical_url,
                        post_author=sanitized_author,
                        post_created_at=item.post_created_at,
                        deduplication_hash=dedup_hash,
                        relevance_score=score,
                        processing_status=status
                    )
                    self.db.add(post_record)
                    self.db.commit()

                    if is_relevant:
                        channel_stats["stored"] += 1
                        stats["relevant_stored"] += 1
                    else:
                        channel_stats["rejected"] += 1
                        stats["rejected_noise"] += 1

            except Exception as e:
                logger.error(f"Error harvesting from {channel_name}: {e}")
                self.db.rollback()

            stats["by_channel"][channel_name] = channel_stats

        logger.info(f"Harvest complete. Stored {stats['relevant_stored']} relevant posts for LLM extraction.")
        return stats

    def close(self):
        """Closes the DB session."""
        if self.db:
            self.db.close()
