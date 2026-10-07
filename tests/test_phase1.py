import sys
from pathlib import Path
from datetime import datetime

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.database import init_db, SessionLocal
from backend.app.models.orm_models import RawPost, DataSource
from backend.app.harvesters.preprocessor import DataPreprocessor
from backend.app.harvesters.relevance_gate import RelevanceGate
from backend.app.harvesters.playstore import GooglePlayStoreHarvester
from backend.app.harvesters.reddit import RedditHarvester
from backend.app.harvesters.google_community import GoogleCommunityHarvester
from backend.app.harvesters.pipeline import IngestionPipeline

def test_data_preprocessor_pii_and_hash():
    """Verify that PII is masked and deduplication hash is deterministic."""
    dirty_text = (
        "<p>Contact me at <b>alice.smith@gmail.com</b> or call +1-555-123-4567. "
        "My server IP is 192.168.1.100. I cannot find my childhood photos.</p>"
    )
    sanitized, author, dedup_hash = DataPreprocessor.process_raw_post(
        raw_text=dirty_text,
        source_channel="PlayStore",
        author="alice.smith@gmail.com",
        post_date=datetime(2024, 1, 15)
    )

    # Assertions
    assert "alice.smith@gmail.com" not in sanitized
    assert "[EMAIL_REDACTED]" in sanitized
    assert "+1-555-123-4567" not in sanitized
    assert "[PHONE_REDACTED]" in sanitized
    assert "192.168.1.100" not in sanitized
    assert "[IP_REDACTED]" in sanitized
    assert "<p>" not in sanitized
    assert "<b>" not in sanitized
    assert "[EMAIL_REDACTED]" in author

    # Verify deterministic hash
    hash2 = DataPreprocessor.compute_deduplication_hash(sanitized, "PlayStore", datetime(2024, 1, 15))
    assert dedup_hash == hash2
    print("[OK] DataPreprocessor PII sanitization and deduplication verified.")

def test_individual_harvesters():
    """Verify channel harvesters yield valid RawHarvestedPost payloads."""
    # Play Store
    play_harvester = GooglePlayStoreHarvester()
    play_posts = play_harvester.fetch_posts(limit=5)
    assert isinstance(play_posts, list)
    print(f"[OK] Play Store Harvester yielded {len(play_posts)} posts.")

    # Reddit
    reddit_harvester = RedditHarvester()
    reddit_posts = reddit_harvester.fetch_posts(limit=5)
    assert len(reddit_posts) > 0
    assert reddit_posts[0].source_channel == "Reddit"
    assert "reddit.com" in reddit_posts[0].canonical_url
    print(f"[OK] Reddit Harvester yielded {len(reddit_posts)} posts.")

    # Google Community
    comm_harvester = GoogleCommunityHarvester()
    comm_posts = comm_harvester.fetch_posts(limit=5)
    assert len(comm_posts) > 0
    assert "support.google.com" in comm_posts[0].canonical_url
    print(f"[OK] Community Harvester yielded {len(comm_posts)} posts.")

def test_relevance_gate_with_groq():
    """Verify Groq LPU relevance filter accurately distinguishes retrieval friction from noise."""
    gate = RelevanceGate()

    # Relevant retrieval complaint
    rel_text = "I spent hours looking for a photo of my mom in a blue dress at the beach. Google Photos search showed me pictures of blue sky and oceans, but not my mom."
    is_rel, score, reason = gate.evaluate(rel_text)
    assert is_rel is True
    assert score >= 0.70
    print(f"[OK] Relevance Gate recognized retrieval friction: score={score}, reasoning='{reason}'")

    # Irrelevant noise (billing complaint)
    noise_text = "Google charged my credit card $9.99 for storage renewal without warning. Please refund immediately!"
    is_noise, score_noise, reason_noise = gate.evaluate(noise_text)
    assert is_noise is False
    assert score_noise < 0.70
    print(f"[OK] Relevance Gate recognized noise: score={score_noise}, reasoning='{reason_noise}'")

def test_end_to_end_ingestion_pipeline():
    """Verify end-to-end ingestion, deduplication, and database persistence."""
    init_db()
    db = SessionLocal()
    pipeline = IngestionPipeline(db=db)

    # Initial harvest run
    stats = pipeline.run_harvest(limit_per_channel=5)
    assert stats["total_fetched"] > 0
    assert stats["relevant_stored"] > 0 or stats["duplicates_skipped"] > 0
    print(f"[OK] Ingestion Pipeline Run: Stored={stats['relevant_stored']}, Duplicates={stats['duplicates_skipped']}.")

    # Check database records
    count_stored = db.query(RawPost).filter_by(processing_status="PENDING_EXTRACTION").count()
    assert count_stored >= stats["relevant_stored"]

    # Verify zero PII in stored posts
    for post in db.query(RawPost).limit(10).all():
        assert "@" not in post.post_author or "[EMAIL_REDACTED]" in post.post_author

    # Second run to test deduplication avoidance
    stats_dup = pipeline.run_harvest(limit_per_channel=5)
    assert stats_dup["duplicates_skipped"] > 0
    print(f"[OK] Ingestion Pipeline Run 2 (Deduplication Check): Skipped {stats_dup['duplicates_skipped']} duplicates.")

    pipeline.close()

if __name__ == "__main__":
    test_data_preprocessor_pii_and_hash()
    test_individual_harvesters()
    test_relevance_gate_with_groq()
    test_end_to_end_ingestion_pipeline()
    print("\n=== ALL PHASE 1 VERIFICATION CHECKS PASSED SUCCESSFULLY! ===")
