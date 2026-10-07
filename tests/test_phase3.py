import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.database import init_db, SessionLocal
from backend.app.models.orm_models import ProblemCluster, ClusterEvidenceJunction, OpportunityArea, ExtractedEvidence
from backend.app.clustering.embedder import SemanticFeatureVectorizer
from backend.app.clustering.clusterer import RetrievalProblemClusterer
from backend.app.clustering.synthesizer import ClusterSynthesizer
from backend.app.clustering.service import ClusteringService

def test_semantic_vectorizer_and_clustering():
    """Verify semantic feature vectorization and clustering."""
    records = [
        {
            "id": "1",
            "scenario_type": "Nature / scenery",
            "failure_point": "Search interpretation does not match intent",
            "user_outcome": "Retrieved through manual browsing",
            "remembered_clues": ["dog", "lake tahoe", "sunset", "blue bandana"],
            "forgotten_metadata": ["exact year"],
            "workarounds": ["scrolled timeline manually"],
            "verbatim_quote": "Searched dog lake bandana but got random dog pictures in grass."
        },
        {
            "id": "2",
            "scenario_type": "Childhood photo",
            "failure_point": "Search interpretation does not match intent",
            "user_outcome": "Outcome unknown",
            "remembered_clues": ["grandmother", "kitchen", "apple pie", "flour"],
            "forgotten_metadata": ["album name", "date"],
            "workarounds": ["gave up"],
            "verbatim_quote": "Searching grandma kitchen gave 0 results because she was never tagged."
        },
        {
            "id": "3",
            "scenario_type": "Document / physical paper",
            "failure_point": "Results are completely not relevant",
            "user_outcome": "Retrieved using another method",
            "remembered_clues": ["car insurance policy", "roadside registration card"],
            "forgotten_metadata": ["filename", "date"],
            "workarounds": ["called spouse to text copy"],
            "verbatim_quote": "Searched insurance card policy and got 200 random receipts and flight passes."
        }
    ]

    vectorizer = SemanticFeatureVectorizer()
    vectors = vectorizer.fit_transform(records)
    assert vectors.shape[0] == 3
    assert vectors.shape[1] > 0
    print(f"[OK] SemanticFeatureVectorizer produced shape: {vectors.shape}")

    clusterer = RetrievalProblemClusterer(max_clusters=2)
    groups = clusterer.cluster(vectors, records)
    assert len(groups) > 0
    assert len(groups[0].exemplars) > 0
    print(f"[OK] RetrievalProblemClusterer formed {len(groups)} cluster groups.")

def test_cluster_synthesizer_with_groq():
    """Verify Groq synthesizes a cohesive ProblemCluster schema."""
    synthesizer = ClusterSynthesizer()

    sample_members = [
        {
            "source_channel": "Reddit",
            "canonical_url": "https://reddit.com/r/googlephotos/1",
            "post_date": "2024-03-12",
            "verbatim_quote": "Searched dog lake bandana, got dog in grass. Search interpretation does not match intent.",
            "failure_point": "Search interpretation does not match intent",
            "scenario_type": "Nature / scenery"
        },
        {
            "source_channel": "Google Help Community",
            "canonical_url": "https://support.google.com/photos/thread/2",
            "post_date": "2024-05-14",
            "verbatim_quote": "Typed graduation day outside in rain holding umbrella, got zero results.",
            "failure_point": "Search interpretation does not match intent",
            "scenario_type": "Event / milestone"
        }
    ]

    synth_result = synthesizer.synthesize(
        cluster_id="CLUSTER-01",
        member_records=sample_members,
        exemplars=sample_members,
        total_dataset_size=10
    )

    assert "problem_name" in synth_result
    assert "description" in synth_result
    assert "severity_indicators" in synth_result
    assert "retrieval_impact" in synth_result
    assert "potential_opportunity_area" in synth_result
    assert len(synth_result["sources_present"]) >= 1
    assert len(synth_result["representative_evidence"]) == 2

    desc_preview = synth_result['description'][:90].encode('ascii', 'ignore').decode('ascii')
    opp_preview = synth_result['potential_opportunity_area'][:90].encode('ascii', 'ignore').decode('ascii')
    print(f"[OK] ClusterSynthesizer produced: '{synth_result['problem_name']}'")
    print(f"     Description: {desc_preview}...")
    print(f"     Opportunity: {opp_preview}...")

def test_end_to_end_clustering_service():
    """Verify full ClusteringService execution against database."""
    init_db()
    db = SessionLocal()
    service = ClusteringService(db=db)

    evidence_count = db.query(ExtractedEvidence).count()
    print(f"[INFO] Database has {evidence_count} extracted evidence records.")

    if evidence_count > 0:
        results = service.run_clustering()
        assert results["clusters_created"] > 0

        # Verify database entities created
        cluster_count = db.query(ProblemCluster).count()
        junction_count = db.query(ClusterEvidenceJunction).count()
        opp_count = db.query(OpportunityArea).count()

        assert cluster_count == results["clusters_created"]
        assert junction_count == evidence_count
        assert opp_count == cluster_count

        print(f"[OK] Database verified: {cluster_count} Clusters, {junction_count} Junctions, {opp_count} Opportunity Areas.")
    else:
        print("[SKIP] No evidence in database to cluster.")

    service.close()

if __name__ == "__main__":
    test_semantic_vectorizer_and_clustering()
    test_cluster_synthesizer_with_groq()
    test_end_to_end_clustering_service()
    print("\n=== ALL PHASE 3 VERIFICATION CHECKS PASSED SUCCESSFULLY! ===")
