import json
import logging
from typing import Tuple
from groq import Groq
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

RELEVANCE_SYSTEM_PROMPT = """
You are a high-speed discovery filter for a Google Photos research engine.
Your task is to determine whether a user review or forum post describes an ACTUAL PHOTO RETRIEVAL EXPERIENCE, search difficulty, memory recall problem, or photo organization friction.

Classify:
- RELEVANT (Score >= 0.70):
  * User describes trying to find, locate, or retrieve a specific photo, document, album, or person.
  * User describes search failing, wrong results, too many results, scrolling endlessly, missing dates/locations.
  * User describes face recognition / person tagging retrieval problems.
- IRRELEVANT (Score < 0.70):
  * Generic reviews ("Good app", "I love photos").
  * App crashes, payment/subscription billing bugs, update download errors unrelated to search/retrieval.
  * Cloud storage pricing complaints without retrieval context.

You MUST respond strictly with valid JSON format:
{
  "is_relevant": true/false,
  "relevance_score": 0.0 to 1.0,
  "reasoning": "brief explanation in 1 sentence"
}
"""

class RelevanceGate:
    """Evaluates raw user text to filter out noise using Groq's high-speed LPU inference."""

    POSITIVE_KEYWORDS = [
        "search", "find", "retrieve", "found", "looking for", "missing",
        "scroll", "timeline", "album", "years ago", "lost", "face", "tag",
        "query", "filter", "remember", "date", "exif", "recognize", "photo", "pictures"
    ]
    NEGATIVE_KEYWORDS = [
        "subscription", "charged my card", "refund", "credit card", 
        "billing", "payment", "login loop", "password reset"
    ]

    def __init__(self):
        self.client = None
        if settings.GROQ_API_KEY:
            try:
                self.client = Groq(api_key=settings.GROQ_API_KEY)
            except Exception as e:
                logger.warning(f"Could not initialize Groq client for RelevanceGate: {e}")

    def heuristic_score(self, text: str) -> Tuple[bool, float, str]:
        """Fast keyword-density heuristic fallback."""
        lower = text.lower()
        pos_hits = sum(1 for kw in self.POSITIVE_KEYWORDS if kw in lower)
        neg_hits = sum(1 for kw in self.NEGATIVE_KEYWORDS if kw in lower)

        if neg_hits > pos_hits:
            score = max(0.1, 0.5 - (neg_hits * 0.15))
            return False, round(score, 2), "Heuristic: Irrelevant billing/crash keywords dominant."

        score = min(0.95, 0.4 + (pos_hits * 0.15))
        is_rel = score >= settings.MIN_RELEVANCE_SCORE
        return is_rel, round(score, 2), f"Heuristic: Matched {pos_hits} retrieval intent keywords."

    def evaluate(self, text: str) -> Tuple[bool, float, str]:
        """
        Evaluates relevance of a post.
        Returns: (is_relevant, relevance_score, reasoning)
        """
        if not text or len(text.strip()) < 15:
            return False, 0.0, "Text too short to evaluate."

        # If Groq is available, use fast LPU filter model
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model=settings.GROQ_MODEL_FAST_FILTER,
                    messages=[
                        {"role": "system", "content": RELEVANCE_SYSTEM_PROMPT},
                        {"role": "user", "content": f"User post to evaluate:\n{text[:1000]}"}
                    ],
                    temperature=0.0,
                    response_format={"type": "json_object"}
                )
                raw_json = response.choices[0].message.content
                data = json.loads(raw_json)

                score = float(data.get("relevance_score", 0.0))
                is_relevant = bool(data.get("is_relevant", score >= settings.MIN_RELEVANCE_SCORE))
                reasoning = data.get("reasoning", "Evaluated by Groq LPU relevance filter.")
                return is_relevant, score, reasoning
            except Exception as e:
                logger.warning(f"Groq relevance evaluation error ({e}). Using heuristic fallback.")

        # Fallback heuristic
        return self.heuristic_score(text)
