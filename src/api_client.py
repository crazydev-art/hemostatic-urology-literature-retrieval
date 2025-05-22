"""
API client module for Biomedical Literature Retrieval.

Handles low-level interactions with NCBI E-utilities API.
"""
import requests
import urllib.parse
import logging
import os
from typing import Optional, Dict, List
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()
logger = logging.getLogger(__name__)

class EntrezClient:
    """Client for NCBI E-utilities API with rate limiting."""
    def __init__(self, base_url: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/", max_url_length: int = 2000, api_key: Optional[str] = None) -> None:
        self.base_url = base_url
        self.max_url_length = max_url_length
        self.api_key = api_key or os.getenv("NCBI_API_KEY")
        self.session = requests.Session()
        self.rate_limit = 10 if self.api_key else 3

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _make_request(self, endpoint: str, params: Dict, method: str = "GET") -> Optional[requests.Response]:
        url = f"{self.base_url}{endpoint}"
        if method == "GET":
            encoded_url = f"{url}?{urllib.parse.urlencode(params, safe='%')}"
            if len(encoded_url) > self.max_url_length:
                raise ValueError(f"URL exceeds {self.max_url_length} bytes")
        try:
            response = self.session.request(method, url, params=params if method == "GET" else None, data=params if method == "POST" else None)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f"Request failed: %s", e)
            raise

    def search(self, db: str, term: str, use_history: bool = True, retmode: str = "json", retmax: int = 1000, api_key: Optional[str] = None) -> Optional[Dict]:
        params = {
            "db": db,
            "term": term,
            "usehistory": "y" if use_history else "n",
            "retmode": retmode,
            "retmax": retmax,
        }
        if api_key or self.api_key:
            params["api_key"] = api_key or self.api_key
        response = self._make_request("esearch.fcgi", params)
        if response:
            logger.info(f"ESearch successful for term: %s", term[:50])
            return response.json() if retmode == "json" else None
        return None

    def fetch_summary(self, db: str, webenv: str, total_results: int, querykey: str, retmode: str = "json", retmax: int = 1000, api_key: Optional[str] = None) -> List[Dict]:
        all_results = []
        total_iterations = (total_results + retmax - 1) // retmax
        for retstart in tqdm(range(0, total_results, retmax), total=total_iterations, desc="Fetching summaries"):
            params = {
                "db": db,
                "WebEnv": webenv,
                "query_key": querykey,
                "retmode": retmode,
                "retmax": min(retmax, total_results - retstart),
                "retstart": retstart,
            }
            if api_key or self.api_key:
                params["api_key"] = api_key or self.api_key
            try:
                response = self._make_request("esummary.fcgi", params)
                if response and retmode == "json":
                    summary_data = response.json()
                    result_set = summary_data.get("result", {})
                    for uid in result_set.get("uids", []):
                        if uid in result_set:
                            all_results.append(result_set[uid])
                    logger.info(f"Fetched %d records at retstart=%d", len(result_set.get('uids', [])), retstart)
                else:
                    logger.warning("Summary fetch failed at retstart=%d, continuing...", retstart)
                    continue
            except Exception as e:
                logger.warning("Summary fetch failed at retstart=%d: %s, continuing...", retstart, e)
                continue
        if len(all_results) < total_results:
            logger.warning("Partial results: fetched %d of %d records", len(all_results), total_results)
        return all_results