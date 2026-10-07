import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.config import settings
from backend.app.core.database import init_db, SessionLocal, engine
from backend.app.models.orm_models import DataSource, RawPost, ExtractedEvidence
from backend.app.models.schemas import (
    ExtractedEvidenceRecord, RetrievalScenario, FailurePoint, UserOutcome
)
import pytest
from groq import Groq
import instructor

def test_settings_load():
    """Verify settings load successfully from .env"""
    assert settings.APP_NAME is not None
    assert settings.GROQ_API_KEY.startswith("gsk_"), "Groq API key must start with gsk_"
    assert settings.GROQ_MODEL_EXTRACTION in ["llama-3.3-70b-versatile", "openai/gpt-oss-120b"]
    print("[OK] Settings and Groq config successfully loaded.")

def test_database_init_and_crud():
    """Verify database initialization, schema creation, and basic ORM operations."""
    init_db()
    db = SessionLocal()
    try:
        # Create a test source
        source = DataSource(
            channel_name="Test Reddit",
            base_url="https://reddit.com/r/googlephotos"
        )
        db.add(source)
        db.commit()
        db.refresh(source)
        assert source.id is not None

        # Create a raw post
        raw_post = RawPost(
            source_id=source.id,
            source_channel="Test Reddit",
            raw_text="I remember taking a picture of my dog near a wooden cabin in 2019 but can't find it.",
            canonical_url="https://reddit.com/r/googlephotos/comments/test1",
            deduplication_hash="test_hash_12345",
            relevance_score=0.95
        )
        db.add(raw_post)
        db.commit()
        db.refresh(raw_post)
        assert raw_post.id is not None

        # Clean up
        db.delete(raw_post)
        db.delete(source)
        db.commit()
        print("[OK] Database tables initialized and ORM operations verified.")
    finally:
        db.close()

def test_pydantic_schema_validation():
    """Verify 7-dimensional extraction schema validation and epistemic separation."""
    sample_data = {
        "source_channel": "Reddit",
        "source_url": "https://reddit.com/r/googlephotos/comments/abc123",
        "post_date": "2024-02-15",
        "verbatim_quote": "I remember my dog jumped into the lake while wearing his red collar, but search just gave me grass.",
        "scenario_type": "Nature / scenery",
        "remembered_clues": ["dog", "lake", "red collar", "jumping"],
        "forgotten_metadata": ["exact date", "exact location"],
        "search_behaviors": ["searched dog lake", "scrolled timeline 2022"],
        "failure_point": "Semantic interpretation does not match intent",
        "workarounds": ["asked sister on WhatsApp for copy"],
        "user_outcome": "Could not retrieve (abandoned)",
        "ai_confidence_score": 0.95,
        "ai_interpretation_notes": "User explicitly noted lack of date and failure to match semantic query intent."
    }

    # Test valid validation with fallback / fuzzy enum
    record = ExtractedEvidenceRecord(
        source_channel=sample_data["source_channel"],
        source_url=sample_data["source_url"],
        post_date=sample_data["post_date"],
        verbatim_quote=sample_data["verbatim_quote"],
        scenario_type=RetrievalScenario.NATURE_SCENERY,
        remembered_clues=sample_data["remembered_clues"],
        forgotten_metadata=sample_data["forgotten_metadata"],
        search_behaviors=sample_data["search_behaviors"],
        failure_point=FailurePoint.SEMANTIC_MISMATCH,
        workarounds=sample_data["workarounds"],
        user_outcome=UserOutcome.ABANDONED,
        ai_confidence_score=0.95,
        ai_interpretation_notes=sample_data["ai_interpretation_notes"]
    )

    assert record.verbatim_quote == sample_data["verbatim_quote"]
    assert record.scenario_type == RetrievalScenario.NATURE_SCENERY
    assert record.failure_point == FailurePoint.SEMANTIC_MISMATCH
    print("[OK] Pydantic 7-dimension extraction schema validated.")

def test_groq_client_init():
    """Verify Groq API client with Instructor can be initialized."""
    raw_groq = Groq(api_key=settings.GROQ_API_KEY)
    client = instructor.from_groq(raw_groq, mode=instructor.Mode.JSON)
    assert client is not None
    print("[OK] Groq client + Instructor initialized.")

if __name__ == "__main__":
    test_settings_load()
    test_database_init_and_crud()
    test_pydantic_schema_validation()
    test_groq_client_init()
    print("\n=== ALL PHASE 0 VERIFICATION CHECKS PASSED SUCCESSFULLY! ===")
