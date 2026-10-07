import logging
from datetime import datetime
from typing import List
from google_play_scraper import reviews, Sort
from backend.app.harvesters.base import BaseHarvester, RawHarvestedPost

logger = logging.getLogger(__name__)

class GooglePlayStoreHarvester(BaseHarvester):
    """Harvester for Google Play Store reviews of Google Photos."""

    PACKAGE_NAME = "com.google.android.apps.photos"
    RETRIEVAL_KEYWORDS = [
        "search", "find", "missing", "scroll", "album", 
        "years ago", "lost", "face", "retrieval", "timeline", "photos"
    ]

    def __init__(self):
        super().__init__(channel_name="Google Play Store")

    def fetch_posts(self, limit: int = 50) -> List[RawHarvestedPost]:
        harvested = []
        try:
            # Fetch newest reviews first
            result, _ = reviews(
                self.PACKAGE_NAME,
                lang="en",
                country="us",
                sort=Sort.NEWEST,
                count=min(limit * 2, 200)
            )

            for rev in result:
                content = rev.get("content", "").strip()
                if not content or len(content) < 15:
                    continue

                # Filter for retrieval relevance keywords
                content_lower = content.lower()
                if any(kw in content_lower for kw in self.RETRIEVAL_KEYWORDS):
                    review_id = rev.get("reviewId", "unknown")
                    canonical_url = f"https://play.google.com/store/apps/details?id={self.PACKAGE_NAME}&reviewId={review_id}"
                    
                    harvested.append(
                        RawHarvestedPost(
                            source_channel=self.channel_name,
                            raw_text=content,
                            canonical_url=canonical_url,
                            post_author=rev.get("userName", "Play Store User"),
                            post_created_at=rev.get("at", datetime.utcnow()),
                            external_id=review_id
                        )
                    )

                if len(harvested) >= limit:
                    break

        except Exception as e:
            logger.error(f"Error harvesting Google Play Store reviews: {e}")

        logger.info(f"PlayStore Harvester yielded {len(harvested)} retrieval candidate reviews.")
        return harvested
