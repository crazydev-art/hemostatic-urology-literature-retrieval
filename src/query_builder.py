"""
Query builder module for Biomedical Literature Retrieval.

Provides functions to create and split search queries for NCBI E-utilities API.
"""
import urllib.parse
import logging
from typing import List, Optional

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def create_query(devices: List[str], indicators: List[str]) -> str:
    """
    Create a search query combining devices and indicators.

    Args:
        devices (List[str]): List of device terms.
        indicators (List[str]): List of indicator terms.

    Returns:
        str: Combined search query.
    """
    device_query = " OR ".join([f'"{device}"' for device in devices])
    indicator_query = " OR ".join([f'"{indicator}"' for indicator in indicators])
    return f"({device_query}) AND ({indicator_query})"

def _build_batch(devices: List[str], indicators: List[str], date_part: str) -> str:
    """Build a batch query from device and indicator terms."""
    device_query = " OR ".join(devices)
    indicator_query = " OR ".join(indicators)
    batch_term = f"({device_query}) AND ({indicator_query})"
    if date_part:
        batch_term += f" AND {date_part}"
    return batch_term

def split_terms(term: str, batch_size: int = 1000, base_url: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/", api_key: Optional[str] = None) -> List[str]:
    """
    Split a query into batches based on character length.

    Args:
        term (str): Full query string.
        batch_size (int): Max characters per batch.
        base_url (str): API base URL.
        api_key (Optional[str]): NCBI API key.

    Returns:
        List[str]: List of sub-query strings.
    """
    parts = term.split(" AND ")
    if len(parts) < 2:
        return [term]

    device_part = parts[0].strip("()")
    indicator_part = parts[1].strip("()")
    date_part = parts[2] if len(parts) > 2 else ""

    device_terms = device_part.split(" OR ")
    indicator_terms = indicator_part.split(" OR ")

    batches = []
    current_devices = []
    current_indicators = []
    current_length = 0
    api_key_length = len(f"&api_key={api_key}") if api_key else 0

    for i in range(max(len(device_terms), len(indicator_terms))):
        added = False
        if i < len(device_terms):
            d_term = device_terms[i].strip("() ")
            d_length = len(urllib.parse.quote(d_term)) + 4
            if current_length + d_length < batch_size:
                current_devices.append(d_term)
                current_length += d_length
                added = True

        if i < len(indicator_terms):
            i_term = indicator_terms[i].strip("() ")
            i_length = len(urllib.parse.quote(i_term)) + 4
            if current_length + i_length < batch_size:
                current_indicators.append(i_term)
                current_length += i_length
                added = True

        if not added or (i == max(len(device_terms), len(indicator_terms)) - 1 and current_devices):
            if current_devices and current_indicators:
                batch_term = _build_batch(current_devices, current_indicators, date_part)
                batches.append(batch_term)
                current_devices = []
                current_indicators = []
                current_length = 0

    logger.info("Created %d batches", len(batches))
    return batches