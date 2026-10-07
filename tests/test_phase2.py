import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.database import init_db, SessionLocal
from backend.app.models.orm_models import RawPost, ExtractedEvidence
from backend.app.extraction.extractor import DiscoveryExtractor
from backend.app.extraction.service import ExtractionService
from backend.app.models.schemas import ExtractedEvidenceRecord

def test_extractor_direct():
    """Verify DiscoveryExtractor extracts 7 dimensions with Groq LPU inference."""
    extractor = DiscoveryExtractor()

    sample_post = (
        "I was looking for my college graduation photo from 2018 where me and my roommates were holding "
        "champagne in the campus courtyard while it was raining. When I typed 'graduation champagne courtyard' "
        "into Google Photos, it gave me zero results. When I typed 'champagne' it gave me pictures of grocery store shelves. "
        "I couldn't remember the exact month, so I gave up searching and ended up scrolling the timeline manually."
    )

    record = extractor.extract(
        raw_text=sample_post,
        source_channel="Reddit",
        source_url="https://reddit.com/r/googlephotos/comments/test_grad",
        post_date="2024-03-01"
    )

    assert isinstance(record, ExtractedEvidenceRecord)
    assert record.source_channel == "Reddit"
    assert record.source_url == "https://reddit.com/r/googlephotos/comments/test_grad"
    assert len(record.remembered_clues) > 0
    assert len(record.forgotten_metadata) > 0
    assert len(record.search_behaviors) > 0
    assert record.failure_point is not None
    assert record.user_outcome is not None
    assert record.ai_confidence_score > 0.0
    assert len(record.ai_interpretation_notes) > 10

    print("[OK] DiscoveryExtractor 7D extraction verified.")
    print(f"     - Scenario: {record.scenario_type}")
    print(f"     - Remembered: {record.remembered_clues[:3]}")
    print(f"     - Forgotten: {record.forgotten_metadata}")
    print(f"     - Failure Point: {record.failure_point}")
    print(f"     - Workarounds: {record.workarounds}")
    print(f"     - Outcome: {record.user_outcome}")

def test_extraction_service_batch_processing():
    """Verify ExtractionService processes database records and transitions statuses."""
    init_db()
    db = SessionLocal()
    service = ExtractionService(db=db)

    # Check pending posts
    pending_count = db.query(RawPost).filter_by(processing_status="PENDING_EXTRACTION").count()
    print(f"[INFO] Pending posts in DB before extraction: {pending_count}")

    if pending_count > 0:
        # Run extraction on up to 3 posts
        results = service.process_pending_posts(batch_size=3)
        assert results["successfully_processed"] > 0
        print(f"[OK] ExtractionService processed {results['successfully_processed']} posts.")

        # Verify records created in extracted_evidence table
        for evidence_id in results["evidence_ids"]:
            ev = db.query(ExtractedEvidence).filter_by(id=evidence_id).first()
            assert ev is not None
            assert ev.verbatim_quote is not None
            assert ev.scenario_type is not None
            assert ev.failure_point is not None
            assert isinstance(ev.remembered_clues, list)
            assert isinstance(ev.forgotten_metadata, list)
            # Verify raw_post is updated to PROCESSED
            assert ev.raw_post.processing_status == "PROCESSED"
        print("[OK] Verified database persistence and status transition to PROCESSED.")
    else:
        print("[SKIP] No pending posts in database to process.")

    service.close()

if __name__ == "__main__":
    test_extractor_direct()
    test_extraction_service_batch_processing()
    print("\n=== ALL PHASE 2 VERIFICATION CHECKS PASSED SUCCESSFULLY! ===")
