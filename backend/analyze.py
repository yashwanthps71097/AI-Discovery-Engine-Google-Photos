import sys
import argparse
import logging
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.database import init_db
from backend.app.analytics.aggregator import DiscoveryAnalyticsAggregator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="AI Discovery Engine Statistical Analytics & Funnel CLI")
    args = parser.parse_args()

    init_db()
    aggregator = DiscoveryAnalyticsAggregator()

    try:
        overview = aggregator.get_source_overview()
        funnel = aggregator.get_failure_funnel()
        memory = aggregator.get_memory_patterns()
        hyp = memory["hypothesis_validation"]
        dossier = aggregator.get_executive_dossier()

        print("\n" + "=" * 75)
        print("GOOGLE PHOTOS RETRIEVAL DISCOVERY: ANALYTICAL REPORT")
        print("=" * 75)
        print(f"Total Conversations Analyzed: {overview['total_conversations_analyzed']}")
        print(f"Verified Evidence Units:      {overview['verified_retrieval_evidence_count']}")
        print(f"Platforms Represented:        {', '.join(overview['platform_distribution'].keys())}")
        print(f"Date Range:                   {overview['date_range']['earliest']} to {overview['date_range']['latest']}")

        print("\n" + "-" * 75)
        print("1. CENTRAL RESEARCH HYPOTHESIS VALIDATION")
        print("-" * 75)
        print(f"Hypothesis:        {hyp['hypothesis_title']}")
        print(f"Status:            [{hyp['status']}] (Confidence: {hyp['confidence_level']})")
        print(f"Episodic Reliance: {hyp['empirical_findings']['users_relying_on_episodic_memory_pct']}% of users recalled rich contextual cues")
        print(f"Metadata Deficit:  {hyp['empirical_findings']['users_lacking_exact_metadata_pct']}% of users lacked exact indexing parameters")
        print(f"Mismatch Ratio:    {hyp['empirical_findings']['episodic_to_metadata_ratio']} episodic cues per missing metadata point")
        print(f"PM Conclusion:     {hyp['pm_takeaway']}")

        print("\n" + "-" * 75)
        print("2. 7-STAGE RETRIEVAL FAILURE FUNNEL")
        print("-" * 75)
        for stage in funnel["stages"]:
            bar = "#" * int(stage["retention_rate_pct"] / 5)
            print(f"  Stage {stage['stage_num']}: {stage['stage_name']:<22} | Retention: {stage['retention_rate_pct']:>5.1f}% | Dropouts: {stage['users_dropping_out']:>2} ({stage['dropout_rate_pct']}%) [{bar:<20}]")
        print(f"Primary Failure Bottleneck: Stage {funnel['primary_bottleneck_stage']}")
        print(f"Search Abandonment Rate:    {funnel['outcomes_summary']['abandonment_rate_pct']}%")

        print("\n" + "-" * 75)
        print("3. EXECUTIVE DISCOVERY DOSSIER (8 CORE QUESTIONS)")
        print("-" * 75)
        print(f"1. Hardest Photos to Retrieve: {dossier['q1_hardest_photos']}")
        print(f"2. Natural Memory Cues:        {dossier['q2_natural_memory_cues']}")
        print(f"3. Missing Information:        {dossier['q3_common_missing_info']}")
        print(f"4. Incomplete Memory Search:   {dossier['q4_search_behavior_under_incomplete_memory']}")
        print(f"5. Primary Breakdown Point:    {dossier['q5_primary_breakdown_point']}")
        print(f"6. Dominant Workarounds:       {dossier['q6_workarounds_ecosystem']}")
        print(f"7. Cross-Source Consistency:   {dossier['q7_cross_source_consistent_problems']}")
        print(f"8. Priority Opportunity Areas: {dossier['q8_priority_opportunity_areas']}")
        print("=" * 75 + "\n")

    finally:
        aggregator.close()

if __name__ == "__main__":
    main()
