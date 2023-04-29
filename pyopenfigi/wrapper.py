import time
from typing import Optional

import requests
from pydantic import parse_obj_as

from pyopenfigi.exceptions import FilterQueryError, HTTPError, TooManyMappingJobs
from pyopenfigi.models import (
    BulkMappingJob,
    FigiResult,
    Key,
    MappingJob,
    MappingJobResult,
    Query,
)


class OpenFigi:
    BASE_URL = "https://api.openfigi.com"
    VERSION = 3
    MAX_MAPPING_REQUESTS_NO_KEY = 25
    MAX_MAPPING_JOBS_NO_KEY = 10
    MAX_SEARCH_REQUESTS_NO_KEY = 5
    MAX_MAPPING_REQUESTS_KEY = 250
    MAX_MAPPING_JOBS_KEY = 100
    MAX_SEARCH_REQUESTS_KEY = 20

    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Providing an API key allows for improved rate limitations.

        :param api_key: Optional API key.
        """
        self.api_key = api_key

    @property
    def max_mapping_requests(self) -> int:
        """
        The maximum number of mapping requests per minute depends on whether an API key was provided or not.

        :return: the maximum number of mapping requests per minute
        """
        return self.MAX_MAPPING_REQUESTS_KEY if self.api_key else self.MAX_MAPPING_REQUESTS_NO_KEY

    @property
    def max_mapping_jobs(self) -> int:
        """
        The maximum number of mapping jobs per request depends on whether an API key was provided or not.

        :return: the maximum number of mapping jobs per request
        """
        return self.MAX_MAPPING_JOBS_KEY if self.api_key else self.MAX_MAPPING_JOBS_NO_KEY

    @property
    def max_search_requests(self) -> int:
        """
        The maximum number of search/filter requests per minute depends on whether an API key was provided or not.

        :return: the maximum number of search/filter requests per minute
        """
        return self.MAX_SEARCH_REQUESTS_KEY if self.api_key else self.MAX_SEARCH_REQUESTS_NO_KEY

    @property
    def headers(self) -> dict[str, str]:
        """
        Build the HTTP headers for all endpoints depending on whether an API key was provided or not.

        :return: a dictionary of HTTP headers
        """
        content_type = {"Content-Type": "application/json"}
        authorization = {"X-OPENFIGI-APIKEY": self.api_key} if self.api_key else {}
        return content_type | authorization

    def map(self, mapping_jobs: list[MappingJob]) -> list[MappingJobResult]:
        """
        Map third party identifiers to FIGIs.

        The number of mapping jobs is limited (the rate limit depends on whether an API key was provided or not).

        A MappingJobResult can be either:
            - a MappingJobResultFigiList in case results were found for the given MappingJob request
            - a MappingJobResultFigiNotFound in case nothing was found
            - a MappingJobResultError in case the MappingJob was invalid (should not happen with Pydantic validation)

        The MappingJobResult at index i contains the results for the MappingJob at index i in the request.

        :param mapping_jobs: a list of MappingJob objects
        :return: a list of MappingJobResult objects
        """
        if len(mapping_jobs) > self.max_mapping_jobs:
            raise TooManyMappingJobs(
                f"The maximum number of MappingJobs "
                f"{'with' if self.api_key else 'without'} API key "
                f"is {self.max_mapping_jobs} per request"
            )

        url = f"{self.BASE_URL}/v3/mapping"
        headers = self.headers
        data = BulkMappingJob.parse_obj(mapping_jobs).json(exclude_none=True, by_alias=True)
        result = self._request(method="POST", url=url, data=data, headers=headers).json()

        return parse_obj_as(list[MappingJobResult], result)

    def get_id_types(self) -> list[str]:
        """
        Get the list of possible values for `id_type`.
        :return: the list of possible values for `id_type`
        """
        return self._get_values("idType")

    def get_exch_codes(self) -> list[str]:
        """
        Get the list of possible values for `exch_code`.
        :return: the list of possible values for `exch_code`
        """
        return self._get_values("exchCode")

    def get_mic_codes(self) -> list[str]:
        """
        Get the list of possible values for `mic_code`.
        :return: the list of possible values for `mic_code`
        """
        return self._get_values("micCode")

    def get_currencies(self) -> list[str]:
        """
        Get the list of possible values for `currency`.
        :return: the list of possible values for `currency`
        """
        return self._get_values("currency")

    def get_market_sec_des(self) -> list[str]:
        """
        Get the list of possible values for `market_sec_des`.
        :return: the list of possible values for `market_sec_des`
        """
        return self._get_values("marketSecDes")

    def get_security_types(self) -> list[str]:
        """
        Get the list of possible values for `security_type`.
        :return: the list of possible values for `security_type`
        """
        return self._get_values("securityType")

    def get_security_types_2(self) -> list[str]:
        """
        Get the list of possible values for `security_type_2`.
        :return: the list of possible values for `security_type_2`
        """
        return self._get_values("securityType2")

    def get_state_codes(self) -> list[str]:
        """
        Get the list of possible values for `state_code`.
        :return: the list of possible values for `state_code`
        """
        return self._get_values("stateCode")

    def _get_values(self, key: Key) -> list[str]:
        """
        Generic private method to get the current list of values
        for the enum-like properties on Mapping Jobs.
        :return: the list of possible values for the requested field
        """
        url = f"{self.BASE_URL}/v3/mapping/values/{key}"
        headers = self.headers
        result = self._request(method="GET", url=url, headers=headers).json()

        return result["values"]

    def filter(self, query: Query) -> list[FigiResult]:
        """
        Search for FIGIs using keywords and other filters.
        The results are listed alphabetically by FIGI and include the total number of results.

        :param query: Query object
        :return: a list of FigiResult objects
        """

        # Requests rate limitation for Search/Filter API
        # We add half a second extra
        delay = 60 / self.max_search_requests + 0.5

        url = f"{self.BASE_URL}/v3/filter"
        headers = self.headers
        data = query.json(exclude_none=True, by_alias=True)
        result = self._request(method="POST", url=url, data=data, headers=headers).json()

        # It's unlikely that an error occurs given the validation made with Pydantic
        # But in case there's an error, it would raise an Exception
        if "error" in result:
            raise FilterQueryError(result["error"])

        mapping_job_results = result["data"]
        while "next" in result:
            time.sleep(delay)
            query.start = result["next"]
            data = query.json(exclude_none=True, by_alias=True)
            result = self._request(method="POST", url=url, data=data, headers=headers).json()
            mapping_job_results += result["data"]

        return parse_obj_as(list[FigiResult], mapping_job_results)

    def get_total_number_of_matches(self, query: Query) -> int:
        """
        Return the total number of matches for a given query.
        The function only makes one call to the `filter` endpoint and returns the `total` field
        from the response.

        :param query: Query object
        :return: the total number of matches as a positive integer
        """

        url = f"{self.BASE_URL}/v3/filter"
        headers = self.headers

        data = query.json(exclude_none=True, by_alias=True)
        result = self._request(method="POST", url=url, data=data, headers=headers).json()

        return result["total"]

    @staticmethod
    def _request(method: str, url: str, headers: dict[str, str], data: Optional[str] = None) -> requests.Response:
        """
        Generic method for remote calls which raises a custom exception in case of HTTP error.
        """
        response = requests.request(method=method, url=url, headers=headers, data=data)

        if response.status_code != 200:
            raise HTTPError(response.status_code, response.text)

        return response
