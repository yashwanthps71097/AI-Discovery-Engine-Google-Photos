// Frontend API Client connecting to FastAPI backend with seamless offline fallback
import { 
  SUMMARY_METRICS, PLATFORM_DATA, TIMELINE_DATA, SCENARIO_DATA, 
  MEMORY_VS_SYSTEM_DATA, SEARCH_TACTICS_DATA, BEHAVIOR_FLOWS, 
  FUNNEL_DATA, PROBLEM_CLUSTERS, OPPORTUNITY_DATA, EXECUTIVE_DOSSIER 
} from '../data/mockDiscoveryData';

const BASE_URL = import.meta.env.VITE_API_BASE_URL !== undefined ? import.meta.env.VITE_API_BASE_URL : '';

async function safeFetch<T>(endpoint: string, fallback: T): Promise<{ data: T; isLive: boolean }> {
  try {
    const res = await fetch(`${BASE_URL}${endpoint}`, {
      headers: { 'Accept': 'application/json' },
    });
    if (!res.ok) {
      console.warn(`[Discovery API] ${endpoint} returned status ${res.status}. Using fallback.`);
      return { data: fallback, isLive: false };
    }
    const json = await res.json();
    return { data: json, isLive: true };
  } catch (err) {
    // Backend offline or network error
    return { data: fallback, isLive: false };
  }
}

export const api = {
  async getHealth() {
    return safeFetch('/health', { status: 'offline', groq_api_configured: false });
  },

  async getOverview() {
    return safeFetch('/api/v1/overview', {
      total_conversations_analyzed: 24592,
      platform_distribution: PLATFORM_DATA.reduce((acc, p) => ({ ...acc, [p.name]: p.count }), {}),
      date_range: { earliest: '2023-01-15', latest: '2026-08-20' },
      canonical_sources_sample: []
    });
  },

  async getScenarios() {
    return safeFetch('/api/v1/scenarios', {
      scenario_distribution: {},
      cross_tab_scenario_vs_outcome: {},
      high_friction_scenarios: []
    });
  },

  async getMemoryPatterns() {
    return safeFetch('/api/v1/memory-patterns', {
      total_evidence: 24592,
      remembered_clues_frequency: {},
      forgotten_metadata_deficits: {},
      hypothesis_validation: {
        status: 'CONFIRMED',
        claim: 'Episodic recall cues strongly correlate with search retrieval failure',
        chi_square_stat: 12.84,
        p_value: 0.0003,
        cramers_v: 0.48,
        episodic_failure_ratio: '2.3 : 1',
        interpretation: 'Statistically significant mismatch (p < 0.001) between natural human episodic recall and indexing requirements.'
      }
    });
  },

  async getSearchBehaviors() {
    return safeFetch('/api/v1/search-behaviors', {
      search_tactics_frequency: {},
      behavioral_transition_flows: BEHAVIOR_FLOWS
    });
  },

  async getFailureFunnel() {
    return safeFetch('/api/v1/failure-funnel', {
      total_cohort: 24592,
      stages: FUNNEL_DATA,
      primary_bottleneck_stage: {
        stage_number: 3,
        stage_name: 'Stage 3: Search Query Formulation & Syntax Gap',
        dropout_percentage: 27.2
      }
    });
  },

  async getClusters() {
    return safeFetch('/api/v1/clusters', PROBLEM_CLUSTERS);
  },

  async getOpportunities() {
    return safeFetch('/api/v1/opportunities', OPPORTUNITY_DATA);
  },

  async getExecutiveDossier() {
    return safeFetch('/api/v1/executive-dossier', EXECUTIVE_DOSSIER);
  },

  async getEvidence(skip = 0, limit = 50, platform?: string) {
    const query = new URLSearchParams({ skip: String(skip), limit: String(limit) });
    if (platform && platform !== 'All') query.append('platform', platform);
    return safeFetch(`/api/v1/evidence?${query.toString()}`, { total: 0, items: [] });
  },

  async askAssistant(question: string) {
    try {
      const res = await fetch(`${BASE_URL}/api/v1/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
      });
      if (res.ok) {
        const json = await res.json();
        return { data: json, isLive: true };
      }
    } catch (e) {
      console.warn('[Discovery API] /ask failed or offline:', e);
    }
    return { data: null, isLive: false };
  }
};

