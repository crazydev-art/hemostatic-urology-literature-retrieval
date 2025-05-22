"""
Search module for Biomedical Literature Retrieval.

Implements search functionality using NCBI E-utilities API with batching and parallel processing.
"""
import logging
import urllib.parse
from typing import List, Optional, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.exceptions import RequestException
from tqdm import tqdm
from src.api_client import EntrezClient
from src.query_builder import split_terms

logger = logging.getLogger(__name__)

class SearchManager:
    """Manages search operations with batching and parallel processing."""
    def __init__(self, client: EntrezClient, batch_size: int = 1000):
        """
        Initialize SearchManager.

        Args:
            client (EntrezClient): API client for NCBI E-utilities.
            batch_size (int): Max characters per query batch.
        """
        self.client = client
        self.batch_size = batch_size

    def _format_article(self, article_data: Dict) -> Dict:
        """Format article metadata into pmcid and pmid dictionary."""
        uid = article_data["uid"]
        pmid = None
        for article_id in article_data.get("articleids", []):
            if article_id["idtype"] == "pmid" and article_id["value"] != "0":
                pmid = article_id["value"]
        formatted_pmcid = f"PMC{uid}" if not uid.startswith("PMC") else uid
        return {"pmcid": formatted_pmcid, "pmid": pmid}

    def _process_single_query(self, db: str, term: str, api_key: Optional[str] = None) -> List[Dict]:
        """Process a single query without batching."""
        try:
            search_result = self.client.search(db, term, api_key=api_key)
            if not search_result:
                logger.warning("Single query search failed: %s", term[:50])
                return []
            total_results = int(search_result["esearchresult"]["count"])
            webenv = search_result["esearchresult"]["webenv"]
            querykey = search_result["esearchresult"]["querykey"]
            summary_data = self.client.fetch_summary(db, webenv, total_results, querykey, api_key=api_key)
            if not summary_data:
                return []
            seen_pmcids = set()
            results = []
            for article_data in summary_data:
                article = self._format_article(article_data)
                if article["pmcid"] not in seen_pmcids:
                    seen_pmcids.add(article["pmcid"])
                    results.append(article)
            return results
        except RequestException as e:
            logger.warning("Single query failed: %s", e)
            return []

    def _process_batch(self, batch: str, db: str, api_key: Optional[str] = None, retries: int = 1) -> List[Dict]:
        """Process a single batch with retries."""
        for attempt in range(retries + 1):
            try:
                search_result = self.client.search(db, batch, api_key=api_key)
                if not search_result:
                    logger.warning("Batch search failed (attempt %d): %s", attempt + 1, batch[:50])
                    continue
                total_results = int(search_result["esearchresult"]["count"])
                webenv = search_result["esearchresult"]["webenv"]
                querykey = search_result["esearchresult"]["querykey"]
                summary_data = self.client.fetch_summary(db, webenv, total_results, querykey, api_key=api_key)
                if not summary_data:
                    continue
                return [
                    self._format_article(article_data)
                    for article_data in summary_data
                ]
            except RequestException as e:
                logger.warning("Batch %s failed (attempt %d): %s", batch[:50], attempt + 1, e)
        return []

    def _check_url_length(self, db: str, term: str) -> str:
        """Check if query URL exceeds max length."""
        return (
            f"{self.client.base_url}esearch.fcgi?db={db}&usehistory=y"
            f"&retmode=json&term={urllib.parse.quote(term, safe='%')}"
        )

    def batch_search(self, db: str, term: str, api_key: Optional[str] = None) -> List[Dict]:
        """
        Search database with batching and parallel processing.

        Args:
            db (str): Database (e.g., "pmc").
            term (str): Search query string.
            api_key (Optional[str]): NCBI API key.

        Returns:
            List[Dict]: List of article metadata with pmcid and pmid.
        """
        query_url = self._check_url_length(db, term)
        if len(query_url) <= self.client.max_url_length:
            return self._process_single_query(db, term, api_key=api_key)

        batches = split_terms(term, self.batch_size, self.client.base_url, api_key)
        if not batches:
            logger.error("No valid batches created")
            return []

        results = []
        seen_pmcids = set()
        try:
            with ThreadPoolExecutor(max_workers=2) as executor:
                future_to_batch = {
                    executor.submit(self._process_batch, batch, db, api_key): batch
                    for batch in batches
                }
                for future in tqdm(as_completed(future_to_batch), total=len(batches), desc="Processing batches"):
                    batch = future_to_batch[future]
                    batch_results = future.result()
                    for result in batch_results:
                        if result["pmcid"] not in seen_pmcids:
                            seen_pmcids.add(result["pmcid"])
                            results.append(result)
        except RequestException as e:
            logger.warning("Parallel processing failed: %s, switching to sequential", e)
            for batch in tqdm(batches, desc="Processing batches sequentially"):
                batch_results = self._process_batch(batch, db, api_key)
                for result in batch_results:
                    if result["pmcid"] not in seen_pmcids:
                        seen_pmcids.add(result["pmcid"])
                        results.append(result)

        logger.info("Total unique results: %d", len(results))
        return results

    def search_pmc(self, query: str, start_year: Optional[int] = None, end_year: Optional[int] = None, api_key: Optional[str] = None) -> List[Dict]:
        """
        Search PMC database with batching.

        Args:
            query (str): Search query string.
            start_year (Optional[int]): Start year for date filter.
            end_year (Optional[int]): End year for date filter.
            api_key (Optional[str]): NCBI API key.

        Returns:
            List[Dict]: List of article metadata.
        """
        if start_year or end_year:
            date_query = f"{start_year}[PDAT]" if start_year else ""
            date_query += ":" if start_year and end_year else ""
            date_query += f"{end_year}[PDAT]" if end_year else ""
            query = f"({query}) AND {date_query}"
        results = self.batch_search("pmc", query, api_key=api_key)
        logger.info("Found %d results in PMC", len(results))
        return results

    def search_pubmed_pmc(self, query: str, start_year: Optional[int] = None, end_year: Optional[int] = None, api_key: Optional[str] = None) -> List[Dict]:
        """
        Search PMC (PubMed not implemented).

        Args:
            query (str): Search query string.
            start_year (Optional[int]): Start year for date filter.
            end_year (Optional[int]): End year for date filter.
            api_key (Optional[str]): NCBI API key.

        Returns:
            List[Dict]: List of article metadata with non-null IDs.
        """
        results = self.search_pmc(query, start_year, end_year, api_key=api_key)
        return [info for info in results if info["pmcid"] and info["pmid"]]