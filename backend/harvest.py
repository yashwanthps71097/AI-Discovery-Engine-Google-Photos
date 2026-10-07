import sys
import argparse
import logging
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.database import init_db
from backend.app.harvesters.pipeline import IngestionPipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="AI Discovery Engine Multi-Source Harvester CLI")
    parser.add_argument("--limit", type=int, default=15, help="Number of records to fetch per channel")
    args = parser.parse_args()

    logger.info("Initializing database...")
    init_db()

    logger.info(f"Starting Ingestion Pipeline (Limit per channel: {args.limit})...")
    pipeline = IngestionPipeline()
    try:
        stats = pipeline.run_harvest(limit_per_channel=args.limit)
        print("\n" + "=" * 60)
        print("HARVESTING SUMMARY")
        print("=" * 60)
        print(f"Total Fetched:        {stats['total_fetched']}")
        print(f"Relevant Stored:      {stats['relevant_stored']} (Flagged PENDING_EXTRACTION)")
        print(f"Duplicates Skipped:   {stats['duplicates_skipped']}")
        print(f"Noise Rejected:       {stats['rejected_noise']}")
        print("-" * 60)
        print("Channel Breakdown:")
        for ch, data in stats["by_channel"].items():
            print(f"  - {ch:<24}: Fetched={data['fetched']}, Stored={data['stored']}, Duplicates={data['duplicates']}")
        print("=" * 60 + "\n")
    finally:
        pipeline.close()

if __name__ == "__main__":
    main()
