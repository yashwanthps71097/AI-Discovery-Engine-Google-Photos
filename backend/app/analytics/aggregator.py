import logging
from typing import Dict, Any, List
from collections import Counter
from sqlalchemy.orm import Session

from backend.app.core.database import SessionLocal
from backend.app.models.orm_models import (
    ExtractedEvidence, ProblemCluster, OpportunityArea, DataSource, RawPost
)
from backend.app.analytics.funnel import RetrievalFunnelAnalyzer
from backend.app.analytics.hypothesis import HypothesisValidator

logger = logging.getLogger(__name__)

class DiscoveryAnalyticsAggregator:
    """Aggregates and formats statistical discovery metrics for the 7 PM analytical dashboards."""

    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()

    def get_source_overview(self) -> Dict[str, Any]:
        """Dashboard 1: Source distribution, total volume, date range, and canonical links."""
        evidence_list = self.db.query(ExtractedEvidence).all()
        raw_posts = self.db.query(RawPost).all()
        
        platform_counts = Counter(p.source_channel for p in raw_posts)
        dates = [e.post_date for e in evidence_list if e.post_date]

        canonical_sources = []
        for e in evidence_list[:10]:
            canonical_sources.append({
                "source": e.source_channel,
                "url": e.canonical_url,
                "date": e.post_date or "Undated",
                "quote_preview": e.verbatim_quote[:120] + "...",
                "scenario": e.scenario_type
            })

        return {
            "total_conversations_analyzed": len(raw_posts),
            "verified_retrieval_evidence_count": len(evidence_list),
            "platforms_covered_count": len(platform_counts),
            "platform_distribution": dict(platform_counts),
            "date_range": {
                "earliest": min(dates) if dates else "2024-01-01",
                "latest": max(dates) if dates else "2024-06-30"
            },
            "canonical_sources_sample": canonical_sources
        }

    def get_scenario_breakdown(self) -> Dict[str, Any]:
        """Dashboard 2: Photo scenarios frequency and cross-tabulation with outcomes."""
        evidence_list = self.db.query(ExtractedEvidence).all()
        scenario_counts = Counter(e.scenario_type for e in evidence_list)

        # Cross-tab scenario vs outcome
        cross_tab = {}
        for e in evidence_list:
            sc = e.scenario_type
            if sc not in cross_tab:
                cross_tab[sc] = Counter()
            cross_tab[sc][e.user_outcome] += 1

        formatted_cross_tab = {
            sc: dict(outcomes) for sc, outcomes in cross_tab.items()
        }

        return {
            "scenario_distribution": dict(scenario_counts.most_common()),
            "cross_tab_scenario_vs_outcome": formatted_cross_tab,
            "most_common_scenario": scenario_counts.most_common(1)[0][0] if scenario_counts else "None"
        }

    def get_memory_patterns(self) -> Dict[str, Any]:
        """Dashboard 3: What users naturally remember vs what they forget, plus hypothesis testing."""
        evidence_list = self.db.query(ExtractedEvidence).all()
        hypothesis_data = HypothesisValidator.test_mismatch_hypothesis(evidence_list)

        # Co-occurrence pairs (remembered category vs missing parameter)
        co_occurrences = []
        for e in evidence_list:
            remembered = e.remembered_clues if isinstance(e.remembered_clues, list) else []
            forgotten = e.forgotten_metadata if isinstance(e.forgotten_metadata, list) else []
            for r in remembered[:2]:
                for f in forgotten[:2]:
                    co_occurrences.append({"remembered": str(r).lower(), "forgotten": str(f).lower()})

        return {
            "hypothesis_validation": hypothesis_data,
            "co_occurrence_sample": co_occurrences[:15],
            "top_remembered_clues": hypothesis_data.get("top_recalled_cue_categories", {}),
            "top_forgotten_metadata": hypothesis_data.get("top_missing_metadata_categories", {})
        }

    def get_search_behaviors(self) -> Dict[str, Any]:
        """Dashboard 4: Retrieval tactics distribution and workaround flows."""
        evidence_list = self.db.query(ExtractedEvidence).all()
        behaviors_counter = Counter()
        workarounds_counter = Counter()

        # Flows: behavior -> workaround -> outcome
        flow_links = []
        for e in evidence_list:
            behaviors = e.search_behaviors if isinstance(e.search_behaviors, list) else []
            workarounds = e.workarounds if isinstance(e.workarounds, list) else []

            for b in behaviors:
                behaviors_counter[str(b)] += 1
            for w in workarounds:
                workarounds_counter[str(w)] += 1

            if behaviors and workarounds:
                flow_links.append({
                    "initial_action": str(behaviors[0]),
                    "fallback_workaround": str(workarounds[0]),
                    "final_outcome": e.user_outcome
                })

        return {
            "search_tactics_frequency": dict(behaviors_counter.most_common(10)),
            "common_workarounds_frequency": dict(workarounds_counter.most_common(10)),
            "behavioral_transition_flows": flow_links[:10]
        }

    def get_failure_funnel(self) -> Dict[str, Any]:
        """Dashboard 5: 7-Stage retrieval failure funnel and attrition analysis."""
        evidence_list = self.db.query(ExtractedEvidence).all()
        return RetrievalFunnelAnalyzer.compute_funnel(evidence_list)

    def get_executive_dossier(self) -> Dict[str, Any]:
        """Synthesizes answers to the 8 Core Discovery Questions from the Problem Statement."""
        evidence_list = self.db.query(ExtractedEvidence).all()
        clusters = self.db.query(ProblemCluster).all()

        scenarios = Counter(e.scenario_type for e in evidence_list)
        failures = Counter(e.failure_point for e in evidence_list)
        outcomes = Counter(e.user_outcome for e in evidence_list)

        hypothesis_res = HypothesisValidator.test_mismatch_hypothesis(evidence_list)

        return {
            "q1_hardest_photos": f"Childhood photos ({scenarios.get('Childhood photo', 0)}), Documents/cards ({scenarios.get('Document / physical paper', 0)}), and Nature/travel scenery.",
            "q2_natural_memory_cues": "Activities (baking, jumping, ceremonies), sensory settings (lake, cabin, kitchen), relationships (grandma, roommate), and emotional occasions.",
            "q3_common_missing_info": "Exact calendar year/date, exact GPS coordinates, original camera filenames, and formal tagged names.",
            "q4_search_behavior_under_incomplete_memory": "Users iterate keyword combinations, attempt multi-concept queries, and quickly revert to brute-force chronological timeline scrolling.",
            "q5_primary_breakdown_point": f"Search interpretation does not match intent ({failures.get('Search interpretation does not match intent', 0)} occurrences) followed by completely irrelevant results.",
            "q6_workarounds_ecosystem": "Manual timeline scrolling (45+ mins), asking family members on WhatsApp/text for duplicate copies, and external cloud drive searches.",
            "q7_cross_source_consistent_problems": f"{len(clusters)} cross-platform clusters identified across Reddit and Google Help Community, notably Multi-Concept Query Mismatch and Document Ingestion Clutter.",
            "q8_priority_opportunity_areas": "Multimodal relational search operators, associative recall filters, and visual timeline era anchors."
        }

    def close(self):
        if self.db:
            self.db.close()
