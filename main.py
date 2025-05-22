from src.config import HEMOSTATIC_DEVICES_FLAT, UROLOGY_INDICATORS_FLAT
from src.api_client import EntrezClient
from src.search import SearchManager
from src.query_builder import create_query
import json
import os
import time
import logging

logger = logging.getLogger(__name__)

def main():
    start = time.time()
    query = create_query(HEMOSTATIC_DEVICES_FLAT, UROLOGY_INDICATORS_FLAT)
    client = EntrezClient()
    search_manager = SearchManager(client)
    results = search_manager.search_pubmed_pmc(query, start_year=2023, end_year=2025)
    logger.info(f"Found {len(results)} results, took {time.time() - start} seconds")
    os.makedirs("submission_results", exist_ok=True)
    with open(os.path.join("submission_results", "retrieved_ids.json"), "w") as f:
        json.dump(results, f, indent=4)
        
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    main()