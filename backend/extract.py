import sys
import argparse
import logging
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.database import init_db
from backend.app.extraction.service import ExtractionService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="AI Discovery Engine 7D LLM Extraction CLI")
    parser.add_argument("--batch-size", type=int, default=10, help="Number of pending posts to extract")
    args = parser.parse_args()

    logger.info("Initializing database...")
    init_db()

    logger.info(f"Starting 7-Dimensional LLM Extraction Engine (Batch size: {args.batch_size})...")
    service = ExtractionService()
    try:
        results = service.process_pending_posts(batch_size=args.batch_size)
        print("\n" + "=" * 60)
        print("EXTRACTION SUMMARY")
        print("=" * 60)
        print(f"Pending Posts Found:     {results['total_pending_found']}")
        print(f"Successfully Extracted:  {results['successfully_processed']}")
        print(f"Extraction Failures:     {results['failed_count']}")
        print(f"Evidence Records Created:{len(results['evidence_ids'])}")
        print("=" * 60 + "\n")
    finally:
        service.close()

if __name__ == "__main__":
    main()
