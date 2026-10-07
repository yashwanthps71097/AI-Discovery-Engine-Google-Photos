from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# -----------------------------------------------------------------------------
# 1. Extraction Dimension Enums
# -----------------------------------------------------------------------------

class RetrievalScenario(str, Enum):
    OLD_FAMILY = "Old family photo"
    CHILDHOOD = "Childhood photo"
    TRAVEL = "Travel / vacation photo"
    SPECIFIC_PERSON = "Photo with specific person"
    EVENT_MILESTONE = "Event / milestone"
    FOOD_DINING = "Food / dining"
    SCREENSHOT = "Screenshot (receipts, chats, info)"
    DOCUMENT_ID = "Document / physical paper"
    NATURE_SCENERY = "Nature / scenery"
    OTHER = "Other"

class FailurePoint(str, Enum):
    RECALL_DEFICIT = "Cannot recall enough information"
    QUERY_TRANSLATION_GAP = "Cannot express memory as search query"
    DIRECTIONAL_PARALYSIS = "Does not know what to search"
    SEMANTIC_MISMATCH = "Search interpretation does not match intent"
    TOO_MANY_RESULTS = "Too many results / no relevance sorting"
    IRRELEVANT_RESULTS = "Results are completely not relevant"
    RECOGNITION_DIFFICULTY = "Relevant photo difficult to recognize"
    REFINEMENT_IMPASSE = "Cannot refine a failed search"
    COGNITIVE_FATIGUE = "Search requires too much manual effort"
    OTHER = "Other"

class UserOutcome(str, Enum):
    SUCCESSFUL = "Successfully retrieved"
    RETRIEVED_HIGH_EFFORT = "Retrieved after multiple attempts"
    RETRIEVED_MANUAL_BROWSE = "Retrieved through manual browsing"
    RETRIEVED_ANOTHER_METHOD = "Retrieved using another method"
    ABANDONED = "Could not retrieve (abandoned)"
    UNKNOWN = "Outcome unknown"

# -----------------------------------------------------------------------------
# 2. Epistemic Separation Evidence Unit (Layer 1 & Layer 2)
# -----------------------------------------------------------------------------

class ExtractedEvidenceRecord(BaseModel):
    """
    Core structured output schema for the 7-Dimensional LLM Extraction Engine.
    Strictly separates Layer 1 (User Evidence) from Layer 2 (AI Interpretation).
    """
    # Layer 1: Raw Grounding & Audit Provenance
    source_channel: str = Field(..., description="Platform origin: Reddit, PlayStore, AppStore, etc.")
    source_url: str = Field(..., description="Canonical public URL")
    post_date: Optional[str] = Field(None, description="ISO-8601 publication date")
    verbatim_quote: str = Field(..., description="Exact user statement/excerpt describing the search experience")

    # Layer 2: 7 Structured Discovery Dimensions
    scenario_type: RetrievalScenario = Field(..., description="Type of photo or artifact sought")
    scenario_custom_description: Optional[str] = Field(None, description="Granular scenario details if 'Other' or emergent")
    
    remembered_clues: List[str] = Field(
        default_factory=list,
        description="People, relationships, activities, setting, objects, visual appearance, approx time, emotion"
    )
    forgotten_metadata: List[str] = Field(
        default_factory=list,
        description="Exact date, exact GPS location, person's name, album name, filename, search keywords"
    )
    search_behaviors: List[str] = Field(
        default_factory=list,
        description="Search actions: face tag, place search, timeline scroll, repeated queries, external apps"
    )
    failure_point: FailurePoint = Field(..., description="Specific stage where the retrieval journey broke")
    workarounds: List[str] = Field(
        default_factory=list,
        description="Compensatory actions: external chat backup, asking relatives, brute-force scrolling"
    )
    user_outcome: UserOutcome = Field(..., description="Final resolution outcome")

    # Epistemic Audit Guardrail
    ai_confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence in classification without hallucinating")
    ai_interpretation_notes: str = Field(
        ...,
        description="Explicit chain of reasoning explaining the classification based strictly on user quote"
    )

# -----------------------------------------------------------------------------
# 3. Problem Cluster Schema (Layer 2 -> Layer 3 Bridge)
# -----------------------------------------------------------------------------

class EvidenceReference(BaseModel):
    source: str
    url: str
    date: Optional[str] = None
    quote: str
    failure_point: str

class ProblemClusterSchema(BaseModel):
    cluster_id: str
    problem_name: str
    description: str
    frequency: int
    frequency_percentage: float
    severity_indicators: str
    retrieval_impact: str
    common_user_behavior: List[str]
    common_workaround: List[str]
    sources_present: List[str]
    representative_evidence: List[EvidenceReference]
    potential_opportunity_area: str

# -----------------------------------------------------------------------------
# 4. Opportunity Area Schema (Layer 3)
# -----------------------------------------------------------------------------

class OpportunityAreaSchema(BaseModel):
    id: str
    title: str
    description: str
    backing_cluster_id: str
    evidence_volume: int
    severity_level: str
    validation_hypothesis: str
    primary_research_questions: List[str]

# -----------------------------------------------------------------------------
# 5. Executive Synthesis Dossier (8 Core Questions)
# -----------------------------------------------------------------------------

class ExecutiveDossierResponse(BaseModel):
    hardest_photos_to_retrieve: str
    natural_memory_cues: str
    common_missing_information: str
    search_behavior_under_incomplete_memory: str
    primary_failure_points: str
    workaround_ecosystem: str
    cross_source_consistent_problems: str
    priority_opportunity_areas_for_validation: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)

# -----------------------------------------------------------------------------
# 6. API Response Wrappers
# -----------------------------------------------------------------------------

class HealthCheckResponse(BaseModel):
    status: str
    app_name: str
    environment: str
    groq_api_configured: bool
    database_connected: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SourceOverviewStats(BaseModel):
    total_conversations_analyzed: int
    platforms_covered: int
    date_range_start: Optional[str]
    date_range_end: Optional[str]
    platform_distribution: Dict[str, int]
    earliest_post_date: Optional[str]
    latest_post_date: Optional[str]
