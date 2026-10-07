import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.database import init_db, SessionLocal
from backend.app.models.orm_models import ExtractedEvidence
from backend.app.analytics.funnel import RetrievalFunnelAnalyzer
from backend.app.analytics.hypothesis import HypothesisValidator
from backend.app.analytics.aggregator import DiscoveryAnalyticsAggregator

def test_funnel_analyzer():
    """Verify 7-stage funnel dropout modeling."""
    init_db()
    db = SessionLocal()
    evidence_records = db.query(ExtractedEvidence).all()

    assert len(evidence_records) > 0, "Database must have evidence records for funnel test"

    funnel_result = RetrievalFunnelAnalyzer.compute_funnel(evidence_records)

    assert funnel_result["total_journeys_analyzed"] == len(evidence_records)
    assert len(funnel_result["stages"]) == 7
    assert funnel_result["primary_bottleneck_stage"] in [1, 2, 3, 4, 5, 6, 7]
    assert "abandonment_rate_pct" in funnel_result["outcomes_summary"]

    stage1 = funnel_result["stages"][0]
    assert stage1["stage_num"] == 1
    assert stage1["users_entering"] == len(evidence_records)

    print(f"[OK] RetrievalFunnelAnalyzer verified across {len(evidence_records)} user journeys.")
    print(f"     Primary Bottleneck Stage: Stage {funnel_result['primary_bottleneck_stage']}")
    print(f"     Abandonment Rate: {funnel_result['outcomes_summary']['abandonment_rate_pct']}%")
    db.close()

def test_hypothesis_validator():
    """Verify empirical validation of episodic memory vs indexing mismatch."""
    db = SessionLocal()
    evidence_records = db.query(ExtractedEvidence).all()

    hyp_result = HypothesisValidator.test_mismatch_hypothesis(evidence_records)

    assert hyp_result["status"] in ["CONFIRMED", "REFUTED", "INCONCLUSIVE"]
    assert "empirical_findings" in hyp_result
    findings = hyp_result["empirical_findings"]

    assert findings["mismatch_co_occurrence_pct"] > 0
    assert findings["avg_episodic_cues_per_user"] > 0
    assert hyp_result["is_confirmed"] is True

    print(f"[OK] HypothesisValidator confirmed hypothesis: Status=[{hyp_result['status']}]")
    print(f"     Mismatch Co-occurrence: {findings['mismatch_co_occurrence_pct']}%")
    print(f"     Episodic-to-Metadata Ratio: {findings['episodic_to_metadata_ratio']}")
    db.close()

def test_discovery_analytics_aggregator():
    """Verify aggregation engine prepares structured data for all dashboard views."""
    db = SessionLocal()
    aggregator = DiscoveryAnalyticsAggregator(db=db)

    # 1. Source Overview
    overview = aggregator.get_source_overview()
    assert overview["total_conversations_analyzed"] > 0
    assert overview["verified_retrieval_evidence_count"] > 0
    assert len(overview["canonical_sources_sample"]) > 0

    # 2. Scenario Breakdown
    scenarios = aggregator.get_scenario_breakdown()
    assert len(scenarios["scenario_distribution"]) > 0
    assert len(scenarios["cross_tab_scenario_vs_outcome"]) > 0

    # 3. Memory Patterns
    memory = aggregator.get_memory_patterns()
    assert "hypothesis_validation" in memory
    assert len(memory["top_remembered_clues"]) > 0

    # 4. Search Behaviors
    behaviors = aggregator.get_search_behaviors()
    assert len(behaviors["search_tactics_frequency"]) > 0

    # 5. Executive Dossier
    dossier = aggregator.get_executive_dossier()
    assert len(dossier["q1_hardest_photos"]) > 0
    assert len(dossier["q5_primary_breakdown_point"]) > 0
    assert len(dossier["q8_priority_opportunity_areas"]) > 0

    print("[OK] DiscoveryAnalyticsAggregator verified across all dashboard feeds.")
    aggregator.close()

if __name__ == "__main__":
    test_funnel_analyzer()
    test_hypothesis_validator()
    test_discovery_analytics_aggregator()
    print("\n=== ALL PHASE 4 VERIFICATION CHECKS PASSED SUCCESSFULLY! ===")
