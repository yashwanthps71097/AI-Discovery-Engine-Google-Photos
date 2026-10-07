import hashlib
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class RawHarvestedPost(BaseModel):
    """Normalized payload produced by any source channel harvester."""
    source_channel: str = Field(..., description="Platform identifier: PlayStore, AppStore, Reddit, Community, etc.")
    raw_text: str = Field(..., description="Original raw user text")
    canonical_url: str = Field(..., description="Direct link to post/review")
    post_author: Optional[str] = Field("Anonymous", description="User handle/author (will be sanitized)")
    post_created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    external_id: Optional[str] = Field(None, description="Native platform ID")

    def compute_hash(self) -> str:
        """Generates a deterministic SHA-256 hash for deduplication."""
        normalized = " ".join(self.raw_text.strip().lower().split())
        date_str = self.post_created_at.strftime("%Y-%m-%d") if self.post_created_at else "no_date"
        unique_string = f"{self.source_channel}:{date_str}:{normalized}"
        return hashlib.sha256(unique_string.encode("utf-8")).hexdigest()

class BaseHarvester(ABC):
    """Abstract base class for channel-specific data harvesters."""
    
    def __init__(self, channel_name: str):
        self.channel_name = channel_name

    @abstractmethod
    def fetch_posts(self, limit: int = 50) -> List[RawHarvestedPost]:
        """Fetches raw posts from the public source channel."""
        pass
