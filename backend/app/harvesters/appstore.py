import logging
from datetime import datetime
from typing import List
import requests
from backend.app.harvesters.base import BaseHarvester, RawHarvestedPost

logger = logging.getLogger(__name__)

class AppleAppStoreHarvester(BaseHarvester):
    """Harvester for Apple App Store customer reviews of Google Photos."""

    APP_ID = "962194608" # Google Photos iOS App ID
    RETRIEVAL_KEYWORDS = [
        "search", "find", "missing", "scroll", "album", 
        "years ago", "lost", "face", "retrieval", "timeline", "photos"
    ]

    def __init__(self):
        super().__init__(channel_name="Apple App Store")

    def fetch_posts(self, limit: int = 50) -> List[RawHarvestedPost]:
        harvested = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
        }

        # Query multiple pages if needed
        for page in range(1, 4):
            if len(harvested) >= limit:
                break

            url = f"https://itunes.apple.com/us/rss/customerreviews/page={page}/id={self.APP_ID}/sortBy=mostRecent/json"
            try:
                resp = requests.get(url, headers=headers, timeout=10)
                if resp.status_code != 200:
                    continue

                data = resp.json()
                entries = data.get("feed", {}).get("entry", [])
                
                # If single entry, make it a list
                if isinstance(entries, dict):
                    entries = [entries]

                for item in entries:
                    content = item.get("content", {}).get("label", "").strip()
                    title = item.get("title", {}).get("label", "").strip()
                    combined_text = f"{title}. {content}" if title else content

                    if len(combined_text) < 15:
                        continue

                    # Filter for retrieval-related friction
                    combined_lower = combined_text.lower()
                    if any(kw in combined_lower for kw in self.RETRIEVAL_KEYWORDS):
                        review_id = item.get("id", {}).get("label", str(datetime.utcnow().timestamp()))
                        author = item.get("author", {}).get("name", {}).get("label", "iOS User")
                        canonical_url = f"https://apps.apple.com/us/app/google-photos/id{self.APP_ID}?reviewId={review_id}"

                        harvested.append(
                            RawHarvestedPost(
                                source_channel=self.channel_name,
                                raw_text=combined_text,
                                canonical_url=canonical_url,
                                post_author=author,
                                post_created_at=datetime.utcnow(),
                                external_id=review_id
                            )
                        )

                    if len(harvested) >= limit:
                        break

            except Exception as e:
                logger.error(f"Error fetching Apple App Store reviews page {page}: {e}")

        logger.info(f"App Store Harvester yielded {len(harvested)} retrieval candidate reviews.")
        return harvested
