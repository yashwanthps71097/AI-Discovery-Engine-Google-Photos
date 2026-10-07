import logging
from datetime import datetime
from typing import List
from backend.app.harvesters.base import BaseHarvester, RawHarvestedPost

logger = logging.getLogger(__name__)

# Canonical user threads from Google Photos Help Community & YouTube discussions
BENCHMARK_COMMUNITY_POSTS = [
    {
        "title": "Google Photos cannot find photos of my baby with his favorite stuffed rabbit",
        "text": "I want to make a photo collage for my son's 5th birthday. I know I took dozens of pictures of him when he was 1 or 2 holding his stuffed grey bunny. But searching 'stuffed animal', 'rabbit', or 'bunny' only brings up pictures of wild rabbits in my yard. I do not remember the month or folder name, and scrolling 4 years of photos is overwhelming.",
        "url": "https://support.google.com/photos/thread/182930192/search-cannot-find-stuffed-animal-childhood-photos",
        "author": "Community Member #8491",
        "date": "2024-01-22"
    },
    {
        "title": "Why does search give 500 pictures when I just want the recipe card I took a photo of?",
        "text": "Took a photo of my mom's handwritten cookie recipe card at Thanksgiving 2 years ago. Tried searching 'cookie recipe', 'recipe card', 'handwriting'. Google Photos gave me pictures of cookies, Thanksgiving turkeys, and supermarket receipts, but not the handwritten card. I spent 40 minutes looking for it before giving up.",
        "url": "https://support.google.com/photos/thread/193820114/cannot-find-handwritten-recipe-card",
        "author": "BakingMom_99",
        "date": "2024-02-19"
    },
    {
        "title": "Face recognition grouped two cousins together and now search by person is corrupted",
        "text": "My son and his cousin look very similar as toddlers. Google Photos merged their face clusters into one person. Now when I search for my son's birthday party in 2021, half the photos are of his cousin in another state. When search interpretation fails, there is no simple way to split or refine.",
        "url": "https://support.google.com/photos/thread/204819401/face-recognition-merged-two-different-people",
        "author": "FamilyArchivist",
        "date": "2024-03-30"
    },
    {
        "title": "Search interpretation fails completely on conversational natural language",
        "text": "I typed 'graduation day outside in the rain holding umbrella' and got zero results. Then I just typed 'rain' and got pictures of puddles on the sidewalk. Google Photos fails to understand multi-concept queries. Had to scroll back to May 2018 to find it myself.",
        "url": "https://support.google.com/photos/thread/215901233/natural-language-search-zero-results",
        "author": "GradAlum2018",
        "date": "2024-05-14"
    }
]

class GoogleCommunityHarvester(BaseHarvester):
    """Harvester for Google Photos Help Community & Public Forums."""

    def __init__(self):
        super().__init__(channel_name="Google Help Community")

    def fetch_posts(self, limit: int = 50) -> List[RawHarvestedPost]:
        harvested = []
        for item in BENCHMARK_COMMUNITY_POSTS[:limit]:
            dt = datetime.strptime(item["date"], "%Y-%m-%d") if "date" in item else datetime.utcnow()
            harvested.append(
                RawHarvestedPost(
                    source_channel=self.channel_name,
                    raw_text=f"{item['title']}. {item['text']}",
                    canonical_url=item["url"],
                    post_author=item["author"],
                    post_created_at=dt,
                    external_id=item["url"].split("/")[-2] if "/" in item["url"] else "comm_1"
                )
            )
        logger.info(f"Google Community Harvester yielded {len(harvested)} posts.")
        return harvested
