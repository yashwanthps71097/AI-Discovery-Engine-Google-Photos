import logging
from typing import List, Dict, Any
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_distances

logger = logging.getLogger(__name__)

class ClusterGroup:
    def __init__(self, cluster_id: str, member_records: List[Dict[str, Any]], exemplars: List[Dict[str, Any]]):
        self.cluster_id = cluster_id
        self.member_records = member_records
        self.exemplars = exemplars
        self.size = len(member_records)

class RetrievalProblemClusterer:
    """
    Groups qualitative evidence vectors into coherent problem spaces using hierarchical clustering.
    """

    def __init__(self, max_clusters: int = 4):
        self.max_clusters = max_clusters

    def cluster(self, vectors: np.ndarray, records: List[Dict[str, Any]]) -> List[ClusterGroup]:
        """
        Executes agglomerative clustering on semantic feature vectors.
        """
        n_samples = len(records)
        if n_samples == 0:
            return []
        
        # Determine number of clusters
        k = min(self.max_clusters, max(1, n_samples // 2))
        if k < 2:
            k = 1

        logger.info(f"Clustering {n_samples} evidence records into k={k} problem clusters...")

        if k == 1:
            labels = np.zeros(n_samples, dtype=int)
        else:
            clustering = AgglomerativeClustering(
                n_clusters=k,
                metric="cosine",
                linkage="average"
            )
            labels = clustering.fit_predict(vectors)

        cluster_groups = []
        for cluster_idx in range(k):
            # Find members of this cluster
            indices = np.where(labels == cluster_idx)[0]
            if len(indices) == 0:
                continue

            member_records = [records[i] for i in indices]
            member_vectors = vectors[indices]

            # Compute centroid
            centroid = np.mean(member_vectors, axis=0, keepdims=True)
            distances = cosine_distances(member_vectors, centroid).flatten()

            # Rank by closeness to centroid to find representative exemplars
            ranked_order = np.argsort(distances)
            exemplar_records = [member_records[i] for i in ranked_order[:min(5, len(member_records))]]

            group_id = f"CLUSTER-{cluster_idx + 1:02d}"
            cluster_groups.append(
                ClusterGroup(
                    cluster_id=group_id,
                    member_records=member_records,
                    exemplars=exemplar_records
                )
            )

        return cluster_groups
