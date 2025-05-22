import logging
from typing import List, Dict

def setup_logging(level: int = logging.INFO) -> None:
    """
    Configure logging with a standard format.
    """
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')

def deduplicate_results(results: List[Dict]) -> List[Dict]:
    """
    Deduplicate results by pmcid.

    Args:
        results (List[Dict]): List of article metadata.

    Returns:
        List[Dict]: Deduplicated list.
    """
    seen_pmcids = set()
    deduplicated = []
    for result in results:
        if result["pmcid"] not in seen_pmcids:
            seen_pmcids.add(result["pmcid"])
            deduplicated.append(result)
    return deduplicated