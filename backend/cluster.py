import sys
import argparse
import logging
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.database import init_db
from backend.app.clustering.service import ClusteringService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="AI Discovery Engine Semantic Problem Clustering CLI")
    args = parser.parse_args()

    logger.info("Initializing database...")
    init_db()

    logger.info("Starting Semantic Problem Clustering & LLM Synthesis...")
    service = ClusteringService()
    try:
        results = service.run_clustering()
        print("\n" + "=" * 70)
        print("CLUSTERING & SYNTHESIS SUMMARY")
        print("=" * 70)
        print(f"Total Evidence Records Clustered: {results['total_evidence_clustered']}")
        print(f"Problem Clusters Synthesized:     {results['clusters_created']}")
        print("-" * 70)
        print("Synthesized Problem Clusters:")
        for c in results.get("clusters", []):
            name_clean = c['name'].encode('ascii', 'ignore').decode('ascii')
            sources_clean = ', '.join(c['sources']).encode('ascii', 'ignore').decode('ascii')
            print(f"  [{c['cluster_id']}] {name_clean}")
            print(f"      Frequency: {c['frequency']} items ({c['percentage']}%) | Sources: {sources_clean}")
        print("=" * 70 + "\n")
    finally:
        service.close()

if __name__ == "__main__":
    main()
