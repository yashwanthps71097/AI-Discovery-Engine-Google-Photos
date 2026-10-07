import logging
from typing import List, Dict, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

logger = logging.getLogger(__name__)

class SemanticFeatureVectorizer:
    """
    Transforms structured qualitative evidence into dense semantic feature representations.
    Combines Scenario, Failure Point, Remembered Cues, and Forgotten Parameters.
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            max_features=256,
            sublinear_tf=True
        )

    @staticmethod
    def build_composite_text(record: Dict[str, Any]) -> str:
        """
        Creates a dense textual representation highlighting the memory gap and failure point.
        """
        scenario = record.get("scenario_type", "Unknown Scenario")
        failure = record.get("failure_point", "Unknown Failure")
        outcome = record.get("user_outcome", "Unknown Outcome")
        
        remembered = record.get("remembered_clues", [])
        remembered_str = ", ".join(remembered) if isinstance(remembered, list) else str(remembered)
        
        forgotten = record.get("forgotten_metadata", [])
        forgotten_str = ", ".join(forgotten) if isinstance(forgotten, list) else str(forgotten)
        
        workarounds = record.get("workarounds", [])
        workaround_str = ", ".join(workarounds) if isinstance(workarounds, list) else str(workarounds)
        
        quote = record.get("verbatim_quote", "")

        return (
            f"Scenario: {scenario}. "
            f"Failure Point: {failure}. "
            f"User Outcome: {outcome}. "
            f"Naturally Remembered: {remembered_str}. "
            f"Lacked Metadata: {forgotten_str}. "
            f"Workaround Deployed: {workaround_str}. "
            f"Evidence Quote: {quote}"
        )

    def fit_transform(self, records: List[Dict[str, Any]]) -> np.ndarray:
        """Vectorizes a list of evidence records into normalized feature vectors."""
        texts = [self.build_composite_text(r) for r in records]
        tfidf_matrix = self.vectorizer.fit_transform(texts)
        dense_vectors = tfidf_matrix.toarray()
        return normalize(dense_vectors)
