// -----------------------------------------------------------------------------
// Core Extraction Dimension Types
// -----------------------------------------------------------------------------

export type RetrievalScenario =
  | "Old family photo"
  | "Childhood photo"
  | "Travel / vacation photo"
  | "Photo with specific person"
  | "Event / milestone"
  | "Food / dining"
  | "Screenshot (receipts, chats, info)"
  | "Document / physical paper"
  | "Nature / scenery"
  | "Other";

export type FailurePoint =
  | "Cannot recall enough information"
  | "Cannot express memory as search query"
  | "Does not know what to search"
  | "Search interpretation does not match intent"
  | "Too many results / no relevance sorting"
  | "Results are completely not relevant"
  | "Relevant photo difficult to recognize"
  | "Cannot refine a failed search"
  | "Search requires too much manual effort"
  | "Other";

export type UserOutcome =
  | "Successfully retrieved"
  | "Retrieved after multiple attempts"
  | "Retrieved through manual browsing"
  | "Retrieved using another method"
  | "Could not retrieve (abandoned)"
  | "Outcome unknown";

// -----------------------------------------------------------------------------
// Epistemic Evidence Record (Layer 1 + Layer 2)
// -----------------------------------------------------------------------------

export interface ExtractedEvidenceRecord {
  id: string;
  source_channel: string;
  source_url: string;
  post_date?: string;
  verbatim_quote: string;

  scenario_type: RetrievalScenario;
  scenario_custom_description?: string;
  remembered_clues: string[];
  forgotten_metadata: string[];
  search_behaviors: string[];
  failure_point: FailurePoint;
  workarounds: string[];
  user_outcome: UserOutcome;

  ai_confidence_score: number;
  ai_interpretation_notes: string;
  created_at: string;
}

// -----------------------------------------------------------------------------
// Problem Cluster & Opportunity Area Types
// -----------------------------------------------------------------------------

export interface EvidenceReference {
  source: string;
  url: string;
  date?: string;
  quote: string;
  failure_point: string;
}

export interface ProblemCluster {
  cluster_id: string;
  problem_name: string;
  description: string;
  frequency: number;
  frequency_percentage: number;
  severity_indicators: string;
  retrieval_impact: string;
  common_user_behavior: string[];
  common_workaround: string[];
  sources_present: string[];
  representative_evidence: EvidenceReference[];
  potential_opportunity_area: string;
}

export interface OpportunityArea {
  id: string;
  title: string;
  description: string;
  backing_cluster_id: string;
  evidence_volume: number;
  severity_level: "High" | "Medium" | "Low";
  validation_hypothesis: string;
  primary_research_questions: string[];
}

export interface ExecutiveDossier {
  hardest_photos_to_retrieve: string;
  natural_memory_cues: string;
  common_missing_information: string;
  search_behavior_under_incomplete_memory: string;
  primary_failure_points: string;
  workaround_ecosystem: string;
  cross_source_consistent_problems: string;
  priority_opportunity_areas_for_validation: string;
  generated_at: string;
}
