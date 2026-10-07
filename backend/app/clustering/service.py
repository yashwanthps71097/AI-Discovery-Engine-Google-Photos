import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from backend.app.core.database import SessionLocal
from backend.app.models.orm_models import (
    ExtractedEvidence, ProblemCluster, ClusterEvidenceJunction, OpportunityArea
)
from backend.app.clustering.embedder import SemanticFeatureVectorizer
from backend.app.clustering.clusterer import RetrievalProblemClusterer
from backend.app.clustering.synthesizer import ClusterSynthesizer

logger = logging.getLogger(__name__)

class ClusteringService:
    """Service orchestrating semantic embedding, unsupervised clustering, and LLM cluster synthesis."""

    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
        self.vectorizer = SemanticFeatureVectorizer()
        self.clusterer = RetrievalProblemClusterer(max_clusters=4)
        self.synthesizer = ClusterSynthesizer()

    def run_clustering(self) -> Dict[str, Any]:
        """
        Pulls all extracted evidence records, performs semantic clustering,
        synthesizes problem spaces with Groq, and persists them.
        """
        evidence_records = self.db.query(ExtractedEvidence).all()
        total_records = len(evidence_records)

        if total_records == 0:
            logger.warning("No extracted evidence records found to cluster.")
            return {"total_clustered": 0, "clusters_created": 0}

        logger.info(f"Loaded {total_records} evidence records for semantic clustering.")

        # Convert to dictionary representation for vectorizer
        dict_records = []
        for ev in evidence_records:
            dict_records.append({
                "id": ev.id,
                "scenario_type": ev.scenario_type,
                "failure_point": ev.failure_point,
                "user_outcome": ev.user_outcome,
                "remembered_clues": ev.remembered_clues,
                "forgotten_metadata": ev.forgotten_metadata,
                "workarounds": ev.workarounds,
                "verbatim_quote": ev.verbatim_quote,
                "canonical_url": ev.canonical_url,
                "source_channel": ev.source_channel,
                "post_date": ev.post_date
            })

        # 1. Generate semantic feature vectors
        vectors = self.vectorizer.fit_transform(dict_records)

        # 2. Cluster into problem groups
        cluster_groups = self.clusterer.cluster(vectors, dict_records)

        # 3. Clean prior clusters & junctions to allow re-clustering runs
        self.db.query(ClusterEvidenceJunction).delete()
        self.db.query(OpportunityArea).delete()
        self.db.query(ProblemCluster).delete()
        self.db.commit()

        created_clusters = []

        # 4. Synthesize and persist each cluster
        for group in cluster_groups:
            synth_data = self.synthesizer.synthesize(
                cluster_id=group.cluster_id,
                member_records=group.member_records,
                exemplars=group.exemplars,
                total_dataset_size=total_records
            )

            # Insert ProblemCluster
            cluster_orm = ProblemCluster(
                cluster_id=synth_data["cluster_id"],
                problem_name=synth_data["problem_name"],
                description=synth_data["description"],
                frequency=synth_data["frequency"],
                frequency_percentage=synth_data["frequency_percentage"],
                severity_indicators=synth_data["severity_indicators"],
                retrieval_impact=synth_data["retrieval_impact"],
                common_user_behavior=synth_data["common_user_behavior"],
                common_workaround=synth_data["common_workaround"],
                sources_present=synth_data["sources_present"],
                potential_opportunity_area=synth_data["potential_opportunity_area"]
            )
            self.db.add(cluster_orm)
            self.db.commit()
            self.db.refresh(cluster_orm)

            # Insert junctions linking evidence to cluster
            for member in group.member_records:
                junction = ClusterEvidenceJunction(
                    cluster_id=cluster_orm.id,
                    evidence_id=member["id"],
                    distance_to_centroid=0.1
                )
                self.db.add(junction)

            # Insert associated OpportunityArea
            opp_area = OpportunityArea(
                cluster_id=cluster_orm.id,
                title=f"Opportunity: {synth_data['problem_name']}",
                description=synth_data["potential_opportunity_area"],
                evidence_volume=synth_data["frequency"],
                severity_level="High" if "high" in synth_data["severity_indicators"].lower() else "Medium",
                validation_hypothesis=(
                    f"If users are given associative recall cues for {synth_data['problem_name'].lower()}, "
                    f"the drop-off rate will decrease and manual timeline scroll fatigue will be mitigated."
                ),
                primary_research_questions=[
                    f"How do users naturally describe memories related to {synth_data['problem_name']}?",
                    "What visual or relational anchors do users recall first when exact dates are forgotten?",
                    "Under what conditions do users abandon search in favor of external messaging apps?"
                ]
            )
            self.db.add(opp_area)
            self.db.commit()

            created_clusters.append({
                "cluster_id": cluster_orm.cluster_id,
                "name": cluster_orm.problem_name,
                "frequency": cluster_orm.frequency,
                "percentage": cluster_orm.frequency_percentage,
                "sources": cluster_orm.sources_present
            })

            logger.info(f"Synthesized Cluster {cluster_orm.cluster_id}: {cluster_orm.problem_name} ({cluster_orm.frequency} items)")

        return {
            "total_evidence_clustered": total_records,
            "clusters_created": len(created_clusters),
            "clusters": created_clusters
        }

    def close(self):
        if self.db:
            self.db.close()
