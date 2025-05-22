"""
Unit tests for search and query building functionality.
"""
import pytest
from unittest.mock import patch
from requests.exceptions import RequestException
from src.query_builder import create_query, split_terms
from src.search import SearchManager
from src.api_client import EntrezClient

@pytest.fixture
def mock_client():
    """Fixture for mocking EntrezClient."""
    client = EntrezClient(max_url_length=1000)
    with patch.object(client, 'search', return_value=None) as mock_search, \
         patch.object(client, 'fetch_summary', return_value=[]) as mock_summary:
        yield client, mock_search, mock_summary

@pytest.fixture
def search_manager(mock_client):
    """Fixture for SearchManager with mocked client."""
    client, _, _ = mock_client
    return SearchManager(client, batch_size=100)

@pytest.fixture
def search_manager_batched(mock_client):
    """Fixture for SearchManager with smaller batch size."""
    client, _, _ = mock_client
    return SearchManager(client, batch_size=200)

def test_create_query_valid():
    """Test create_query with valid inputs."""
    devices = ["Hemoblast", "Gelfoam"]
    indicators = ["urological surgery", "prostatectomy"]
    query = create_query(devices, indicators)
    expected = '("Hemoblast" OR "Gelfoam") AND ("urological surgery" OR "prostatectomy")'
    assert query == expected

def test_create_query_empty():
    """Test create_query with empty lists."""
    assert create_query([], []) == "() AND ()"
    assert create_query(["Hemoblast"], []) == '("Hemoblast") AND ()'
    assert create_query([], ["prostatectomy"]) == '() AND ("prostatectomy")'

def test_split_terms_single_query():
    """Test split_terms with a small query."""
    term = '("Hemoblast") AND ("prostatectomy")'
    batches = split_terms(term, batch_size=1000)
    assert len(batches) == 1
    assert batches[0] == term

def test_split_terms_multiple_batches(search_manager_batched):
    """Test split_terms with a large query requiring batching."""
    devices = ["Hemoblast"] * 20
    indicators = ["prostatectomy"] * 20
    term = create_query(devices, indicators)
    batches = split_terms(term, batch_size=200)
    assert len(batches) > 1
    for batch in batches:
        assert " AND " in batch
        assert batch.startswith("(") and batch.endswith(")")

def test_split_terms_invalid_query():
    """Test split_terms with no AND separator."""
    term = '("Hemoblast" OR "Gelfoam")'
    batches = split_terms(term, batch_size=1000)
    assert batches == [term]

def test_split_terms_with_date():
    """Test split_terms with date filter."""
    term = '("Hemoblast") AND ("prostatectomy") AND 2023[PDAT]'
    batches = split_terms(term, batch_size=1000)
    assert len(batches) == 1
    assert batches[0] == term

def test_batch_search_single_query(mock_client, search_manager):
    """Test batch_search with a single query."""
    client, mock_search, mock_summary = mock_client
    mock_search.return_value = {
        "esearchresult": {"count": "2", "webenv": "test_webenv", "querykey": "1"}
    }
    mock_summary.return_value = [
        {"uid": "123", "articleids": [{"idtype": "pmid", "value": "456"}]},
        {"uid": "124", "articleids": []}
    ]
    term = '("Hemoblast") AND ("prostatectomy")'
    results = search_manager.batch_search("pmc", term)
    assert len(results) == 2
    assert results[0] == {"pmcid": "PMC123", "pmid": "456"}
    assert results[1] == {"pmcid": "PMC124", "pmid": None}

def test_batch_search_batched_query(mock_client, search_manager_batched):
    """Test batch_search with batched query."""
    client, mock_search, mock_summary = mock_client
    mock_search.return_value = {
        "esearchresult": {"count": "1", "webenv": "test_webenv", "querykey": "1"}
    }
    mock_summary.return_value = [
        {"uid": "123", "articleids": [{"idtype": "pmid", "value": "456"}]}
    ]
    term = create_query(["Hemoblast"] * 20, ["prostatectomy"] * 20)
    results = search_manager_batched.batch_search("pmc", term)
    assert len(results) >= 1
    assert results[0]["pmcid"].startswith("PMC")

def test_batch_search_api_failure(mock_client, search_manager):
    """Test batch_search with API failure."""
    client, mock_search, mock_summary = mock_client
    mock_search.side_effect = RequestException("API error")
    term = '("Hemoblast") AND ("prostatectomy")'
    results = search_manager.batch_search("pmc", term)
    assert results == []

def test_search_pmc_date_filter(mock_client, search_manager):
    """Test search_pmc with date filter."""
    client, mock_search, mock_summary = mock_client
    mock_search.return_value = {
        "esearchresult": {"count": "1", "webenv": "test_webenv", "querykey": "1"}
    }
    mock_summary.return_value = [
        {"uid": "123", "articleids": [{"idtype": "pmid", "value": "456"}]}
    ]
    term = '("Hemoblast") AND ("prostatectomy")'
    results = search_manager.search_pmc(term, start_year=2023, end_year=2023)
    assert len(results) == 1
    assert "2023[PDAT]" in mock_search.call_args[0][1]

def test_search_pmc_empty_results(mock_client, search_manager):
    """Test search_pmc with no results."""
    client, mock_search, mock_summary = mock_client
    mock_search.return_value = {
        "esearchresult": {"count": "0", "webenv": "test_webenv", "querykey": "1"}
    }
    term = '("Hemoblast") AND ("prostatectomy")'
    results = search_manager.search_pmc(term)
    assert results == []

def test_search_pubmed_pmc_filter(mock_client, search_manager):
    """Test search_pubmed_pmc with non-null ID filtering."""
    client, mock_search, mock_summary = mock_client
    mock_search.return_value = {
        "esearchresult": {"count": "3", "webenv": "test_webenv", "querykey": "1"}
    }
    mock_summary.return_value = [
        {"uid": "123", "articleids": [{"idtype": "pmid", "value": "456"}]},
        {"uid": "124", "articleids": []},
        {"uid": "125", "articleids": []}
    ]
    term = '("Hemoblast") AND ("prostatectomy")'
    results = search_manager.search_pubmed_pmc(term)
    assert len(results) == 1  # Only PMC123 has non-null pmid
    assert results[0]["pmcid"] == "PMC123"
    assert results[0]["pmid"] == "456"