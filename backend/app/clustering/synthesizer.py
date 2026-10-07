import json
import logging
from typing import Dict, Any, List
from groq import Groq
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

CLUSTER_SYNTHESIS_PROMPT = """
You are a Lead Product Discovery Strategist analyzing Google Photos retrieval failure clusters.
You are given a group of real user complaints and search breakdowns that clustered together semantically.

Your task is to synthesize this cluster into an evidence-backed problem specification.

### Rules & Guardrails:
1. Strict Grounding: Every finding must be based on the provided user quotes. Do not invent arbitrary numbers or features.
2. Problem-Focused: Frame this as a DISCOVERY PROBLEM, NOT A SOLUTION. Do NOT propose final product solutions or UI wireframes.
3. Opportunity Hypothesis: State an opportunity area for PM investigation.

You must respond strictly with valid JSON conforming to:
{
  "problem_name": "Concise, descriptive problem title (e.g., Unanchored Entity & Natural Setting Failure)",
  "description": "2-3 sentences explaining the mechanics of how and why retrieval breaks for this group",
  "severity_indicators": "Objective description of user friction (e.g., High cognitive burden, 100% search abandonment, 45+ mins manual scroll)",
  "retrieval_impact": "Direct measurable impact on user retrieval outcomes",
  "common_user_behavior": ["List of observed search behaviors in this cluster"],
  "common_workaround": ["List of workarounds users adopted when search failed"],
  "potential_opportunity_area": "Product opportunity space for PMs to investigate through primary research"
}
"""

class ClusterSynthesizer:
    """Synthesizes raw clustered evidence into structured ProblemCluster definitions using Groq."""

    def __init__(self):
        self.client = None
        if settings.GROQ_API_KEY:
            try:
                self.client = Groq(api_key=settings.GROQ_API_KEY)
            except Exception as e:
                logger.warning(f"Could not initialize Groq client in ClusterSynthesizer: {e}")

    def synthesize(self, cluster_id: str, member_records: List[Dict[str, Any]], exemplars: List[Dict[str, Any]], total_dataset_size: int) -> Dict[str, Any]:
        """
        Synthesizes a cluster into a full ProblemCluster schema.
        """
        frequency = len(member_records)
        frequency_percentage = round((frequency / max(1, total_dataset_size)) * 100, 1)

        # Aggregate platforms present
        sources_present = list(set(r.get("source_channel", "Unknown") for r in member_records))

        # Format evidence items for prompt
        evidence_snippets = []
        representative_evidence = []
        for ex in exemplars:
            quote = ex.get("verbatim_quote", "")
            channel = ex.get("source_channel", "")
            url = ex.get("canonical_url", "")
            date = ex.get("post_date", "")
            fp = ex.get("failure_point", "")

            evidence_snippets.append(
                f"- [{channel}] (Failure: {fp}): \"{quote}\""
            )
            representative_evidence.append({
                "source": channel,
                "url": url,
                "date": date,
                "quote": quote,
                "failure_point": fp
            })

        evidence_text = "\n".join(evidence_snippets)

        # Attempt Groq LLM synthesis
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model=settings.GROQ_MODEL_SYNTHESIS,
                    messages=[
                        {"role": "system", "content": CLUSTER_SYNTHESIS_PROMPT},
                        {
                            "role": "user",
                            "content": (
                                f"Cluster ID: {cluster_id}\n"
                                f"Number of Member Records: {frequency}\n"
                                f"Sources Present: {', '.join(sources_present)}\n\n"
                                f"Representative User Evidence:\n{evidence_text}\n\n"
                                f"Synthesize this cluster into the requested JSON schema."
                            )
                        }
                    ],
                    temperature=0.2,
                    response_format={"type": "json_object"}
                )
                data = json.loads(response.choices[0].message.content)

                return {
                    "cluster_id": cluster_id,
                    "problem_name": data.get("problem_name", f"Retrieval Friction Space {cluster_id}"),
                    "description": data.get("description", "Cross-source photo retrieval breakdown."),
                    "frequency": frequency,
                    "frequency_percentage": frequency_percentage,
                    "severity_indicators": data.get("severity_indicators", "High: Repeated query failures leading to abandonment."),
                    "retrieval_impact": data.get("retrieval_impact", "Failed search results and manual timeline fallback."),
                    "common_user_behavior": data.get("common_user_behavior", ["keyword iteration", "timeline scrolling"]),
                    "common_workaround": data.get("common_workaround", ["manual scroll", "external chat"]),
                    "sources_present": sources_present,
                    "representative_evidence": representative_evidence,
                    "potential_opportunity_area": data.get("potential_opportunity_area", "Contextual and relational memory retrieval.")
                }
            except Exception as e:
                logger.error(f"Groq synthesis failed for {cluster_id} ({e}). Using deterministic synthesis.")

        # Fallback deterministic synthesis
        scenarios = list(set(r.get("scenario_type", "Photo") for r in member_records))
        failures = list(set(r.get("failure_point", "Search issue") for r in member_records))

        return {
            "cluster_id": cluster_id,
            "problem_name": f"{scenarios[0]} Retrieval & {failures[0]}",
            "description": f"Users attempting to locate {', '.join(scenarios[:2])} consistently experience {failures[0]}.",
            "frequency": frequency,
            "frequency_percentage": frequency_percentage,
            "severity_indicators": "High friction: Users express frustration over having to browse years of timeline manually.",
            "retrieval_impact": "Direct drop-off at search refinement stage.",
            "common_user_behavior": ["Keyword query rephrasing", "Brute-force timeline scroll"],
            "common_workaround": ["External messaging app search", "Asking family members"],
            "sources_present": sources_present,
            "representative_evidence": representative_evidence,
            "potential_opportunity_area": "Associative and episodic search operators."
        }
