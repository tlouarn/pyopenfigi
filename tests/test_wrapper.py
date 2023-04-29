import pytest

from pyopenfigi import MappingJob, OpenFigi, Query
from pyopenfigi.exceptions import TooManyMappingJobs, HTTPError
from pyopenfigi.models import (
    FigiResult,
    MappingJobResult,
    MappingJobResultFigiList,
    MappingJobResultFigiNotFound,
)


@pytest.fixture(scope="module")
def vcr_config():
    return {"filter_headers": ["authorization"], "record_mode": "none"}


def test_headers():
    """
    Test that the HTTP headers include the API key when the latter is provided.
    """
    api_key = "XXXXXXXXXX"
    headers_without_key = {"Content-Type": "application/json"}
    headers_with_key = headers_without_key | {"X-OPENFIGI-APIKEY": api_key}

    assert OpenFigi().headers == headers_without_key
    assert OpenFigi(api_key=api_key).headers == headers_with_key


@pytest.mark.vcr
def test_map_one_job():
    """
    Test a mapping request for an existing ticker (e.g. IBM US).
    """
    mapping_job = MappingJob(id_type="TICKER", id_value="IBM", exchange_code="US")
    mapping_jobs = [mapping_job]
    results = OpenFigi().map(mapping_jobs)

    assert results
    assert all([isinstance(x, MappingJobResultFigiList) for x in results])


@pytest.mark.vcr
def test_map_two_jobs():
    """
    Test a mapping request for two existing tickers (e.g. IBM US and XRX US).
    """
    mapping_job_ibm = MappingJob(id_type="TICKER", id_value="IBM", exchange_code="US")
    mapping_job_xerox = MappingJob(id_type="TICKER", id_value="XRX", exchange_code="US")
    mapping_jobs = [mapping_job_ibm, mapping_job_xerox]
    results = OpenFigi().map(mapping_jobs)

    assert results
    assert all([isinstance(x, MappingJobResultFigiList) for x in results])


@pytest.mark.vcr
def test_map_two_jobs_one_of_which_is_in_error():
    """
    Test a mapping request for two tickers, one of them being unknown.
    """
    mapping_job_ibm = MappingJob(id_type="TICKER", id_value="IBM", exchange_code="US")
    mapping_job_error = MappingJob(id_type="TICKER", id_value="UNKNOWN_TICKER", exchange_code="US")
    mapping_jobs = [mapping_job_ibm, mapping_job_error]
    results = OpenFigi().map(mapping_jobs)

    assert results
    assert all([isinstance(x, MappingJobResult) for x in results])
    assert isinstance(results[0], MappingJobResultFigiList)
    assert isinstance(results[1], MappingJobResultFigiNotFound)


def test_map_too_many_jobs_in_one_request():
    """
    Test that an exception is raised if too many MappingJob are provided in one request.
    """
    mapping_jobs = [MappingJob(id_type="TICKER", id_value="IBM", exchange_code="US")] * 11

    with pytest.raises(TooManyMappingJobs):
        results = OpenFigi().map(mapping_jobs)


@pytest.mark.vcr
def test_too_many_mapping_requests():
    """
    Test that an exception is raised if too many MappingJob requests are sent.
    """
    mapping_jobs = [MappingJob(id_type="TICKER", id_value="IBM", exchange_code="US")]

    with pytest.raises(HTTPError):
        for i in range(50):
            results = OpenFigi().map(mapping_jobs)


@pytest.mark.vcr
def test_filter_single_api_call():
    """
    Test a search request for a little known security (i.e. only requires one remote call).
    """
    query = Query(query="SJIM")
    results = OpenFigi().filter(query)

    assert results
    assert all(isinstance(x, FigiResult) for x in results)


@pytest.mark.vcr
def test_filter_instrument_not_found():
    """
    Test that a search for something that does not exist returns an empty list.
    """
    query = Query(query="UNKNOWN_TICKER")
    results = OpenFigi().filter(query)

    assert isinstance(results, list)
    assert len(results) == 0


# @pytest.mark.vcr
# def test_filter_multi_api_call():
#     """
#     Test that a search for a query with over 100 results (and therefore necessiting several calls
#     taking into acccount the rate limitations) works fine.
#
#     Careful: this test can take up to 20min to run if the query returns the maximum of 15,000 results
#     and no API key was provided.
#     """
#     query = Query(query="CTA")
#     results = OpenFigi().filter(query)
#
#     assert results
#     assert all(isinstance(x, FigiResult) for x in results)


@pytest.mark.vcr
def test_get_total_number_of_matches():
    """
    Test that the total number of matches for a given query is returned.
    """

    # Test for a query that has matches
    query = Query(query="IBM")
    matches = OpenFigi().get_total_number_of_matches(query)

    assert isinstance(matches, int)

    # Test for a query that has no matches
    query = Query(query="UNKNOWN_TICKER")
    matches = OpenFigi().get_total_number_of_matches(query)

    assert matches == 0


@pytest.mark.vcr
def test_get_id_types():
    id_types = OpenFigi().get_id_types()

    assert isinstance(id_types, list)
    assert all(isinstance(x, str) for x in id_types)
    assert "TICKER" in id_types


@pytest.mark.vcr
def test_get_exchange_codes():
    exchange_codes = OpenFigi().get_exch_codes()

    assert isinstance(exchange_codes, list)
    assert all(isinstance(x, str) for x in exchange_codes)
    assert "US" in exchange_codes


@pytest.mark.vcr
def test_get_mic_codes():
    mic_codes = OpenFigi().get_mic_codes()

    assert isinstance(mic_codes, list)
    assert all(isinstance(x, str) for x in mic_codes)
    assert "BATS" in mic_codes


@pytest.mark.vcr
def test_get_currencies():
    currencies = OpenFigi().get_currencies()

    assert isinstance(currencies, list)
    assert all(isinstance(x, str) for x in currencies)
    assert "USD" in currencies


@pytest.mark.vcr
def test_get_market_security_descriptions():
    market_security_descriptions = OpenFigi().get_market_sec_des()

    assert isinstance(market_security_descriptions, list)
    assert all(isinstance(x, str) for x in market_security_descriptions)
    assert "Equity" in market_security_descriptions


@pytest.mark.vcr
def test_get_security_types():
    security_types = OpenFigi().get_security_types()

    assert isinstance(security_types, list)
    assert all(isinstance(x, str) for x in security_types)
    assert "Equity Index" in security_types


@pytest.mark.vcr
def test_get_security_types_2():
    security_types_2 = OpenFigi().get_security_types_2()

    assert isinstance(security_types_2, list)
    assert all(isinstance(x, str) for x in security_types_2)
    assert "Common Stock" in security_types_2


@pytest.mark.vcr
def test_get_state_codes():
    state_codes = OpenFigi().get_state_codes()

    assert isinstance(state_codes, list)
    assert all(isinstance(x, str) for x in state_codes)
    assert "AB" in state_codes
