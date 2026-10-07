import logging
from typing import Dict, Any, List
from collections import Counter
from sqlalchemy.orm import Session

from backend.app.models.orm_models import ExtractedEvidence
from backend.app.models.schemas import FailurePoint

logger = logging.getLogger(__name__)

# The 7 canonical stages of photo retrieval
FUNNEL_STAGES = [
    {"stage_num": 1, "stage_name": "Memory Recall", "description": "User attempts to recall identifying attributes of the photo"},
    {"stage_num": 2, "stage_name": "Query Formulation", "description": "User attempts to translate episodic memory into search keywords"},
    {"stage_num": 3, "stage_name": "Search Execution", "description": "System processes query and interprets semantic intent"},
    {"stage_num": 4, "stage_name": "Results Display", "description": "System renders matching candidates with relevance ordering"},
    {"stage_num": 5, "stage_name": "Visual Recognition", "description": "User scans visual grid to identify the target image"},
    {"stage_num": 6, "stage_name": "Query Refinement", "description": "User refines search or filters when initial query fails"},
    {"stage_num": 7, "stage_name": "Final Retrieval", "description": "Successful retrieval of target photo or abandonment"}
]

# Mapping failure points to the funnel stage where the breakdown occurred
FAILURE_STAGE_MAPPING = {
    FailurePoint.RECALL_DEFICIT.value: 1, # Memory Recall
    FailurePoint.DIRECTIONAL_PARALYSIS.value: 2, # Query Formulation
    FailurePoint.QUERY_TRANSLATION_GAP.value: 2, # Query Formulation
    FailurePoint.SEMANTIC_MISMATCH.value: 3, # Search Execution / Intent Interpretation
    FailurePoint.TOO_MANY_RESULTS.value: 4, # Results Display / Clutter
    FailurePoint.IRRELEVANT_RESULTS.value: 4, # Results Display / Zero Recall
    FailurePoint.RECOGNITION_DIFFICULTY.value: 5, # Visual Recognition
    FailurePoint.REFINEMENT_IMPASSE.value: 6, # Query Refinement
    FailurePoint.COGNITIVE_FATIGUE.value: 6, # Query Refinement / Manual Burden
    FailurePoint.OTHER.value: 3
}

class RetrievalFunnelAnalyzer:
    """
    Models and calculates user drop-off across the 7-stage photo retrieval journey:
    Memory -> Query Formulation -> Search Execution -> Results Display -> Recognition -> Refinement -> Retrieval.
    """

    @classmethod
    def compute_funnel(cls, evidence_records: List[ExtractedEvidence]) -> Dict[str, Any]:
        total_journeys = len(evidence_records)
        if total_journeys == 0:
            return {"total_journeys": 0, "stages": [], "success_rate": 0.0, "abandonment_rate": 0.0}

        # Count dropouts at each stage
        dropout_counter = Counter()
        for ev in evidence_records:
            stage_num = FAILURE_STAGE_MAPPING.get(ev.failure_point, 3)
            dropout_counter[stage_num] += 1

        # Count outcome types
        outcomes = Counter(ev.user_outcome for ev in evidence_records)
        successful_retrievals = outcomes.get("Successfully retrieved", 0) + outcomes.get("Retrieved after multiple attempts", 0)
        manual_browsing = outcomes.get("Retrieved through manual browsing", 0)
        abandoned = outcomes.get("Could not retrieve (abandoned)", 0)
        external_workaround = outcomes.get("Retrieved using another method", 0)

        # Build progressive funnel stages
        stages_output = []
        current_active = total_journeys

        for stage in FUNNEL_STAGES:
            s_num = stage["stage_num"]
            dropouts_at_this_stage = dropout_counter[s_num]
            
            # Retention at stage
            retention_rate = round((current_active / total_journeys) * 100, 1)
            dropout_rate = round((dropouts_at_this_stage / total_journeys) * 100, 1)

            stages_output.append({
                "stage_num": s_num,
                "stage_name": stage["stage_name"],
                "description": stage["description"],
                "users_entering": current_active,
                "users_dropping_out": dropouts_at_this_stage,
                "dropout_rate_pct": dropout_rate,
                "retention_rate_pct": retention_rate
            })

            # Next stage has fewer users
            current_active = max(0, current_active - dropouts_at_this_stage)

        return {
            "total_journeys_analyzed": total_journeys,
            "stages": stages_output,
            "primary_bottleneck_stage": max(dropout_counter.items(), key=lambda x: x[1])[0] if dropout_counter else 3,
            "outcomes_summary": {
                "direct_success_count": successful_retrievals,
                "manual_browsing_fallback": manual_browsing,
                "external_workaround_fallback": external_workaround,
                "abandoned_count": abandoned,
                "abandonment_rate_pct": round((abandoned / total_journeys) * 100, 1)
            }
        }
