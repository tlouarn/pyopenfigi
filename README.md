## pyopenfigi

![Python 3.10](https://img.shields.io/badge/python-3.10-blue)
![Black](https://img.shields.io/badge/code%20style-black-black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Python wrapper for the [OpenFIGI API](https://www.openfigi.com/api) v3.

## Table of contents

- [About OpenFIGI](#about-openfigi)
- [Installation](#installation)
- [API key](#api-key)
- [Mapping](#mapping)
- [Filtering](#filtering)
- [Troubleshooting](#troubleshooting)

## About OpenFIGI

- The **F**inancial **I**nstrument **G**lobal **I**dentifier (FIGI) is a universal system for identifying instruments
  globally and across all asset classes
- OpenFIGI is an application programming interface that provides automated access
  to mapping various symbols with their corresponding FIGI. It is available at https://www.openfigi.com/
- [pyopenfigi](https://github.com/tlouarn/pyopenfigi) is a
  thin Python wrapper to access OpenFIGI

The API contains 3 endpoints:

| endpoint | description                                          |
|----------|------------------------------------------------------|
| /mapping | Map third-party identifiers to FIGIs                 |
| /filter  | Filter for FIGIs using keywords and optional filters |
| /search  | Search for FIGIs using keywords and optional filters |

_Note: given that the */search* endpoint is strictly superseded by the */filter* endpoint, we
choose not to include it in the wrapper._

## Installation

**pyopenfigi** is published on [PyPI](https://pypi.org/project/pyopenfigi/). To install it, simply run:

```commandline
pip install pyopenfigi
```

## API key

The API can be used with or without API key.
Getting an API key is free and loosens the [rate limits](https://www.openfigi.com/api#rate-limit).

When instantiating the wrapper, the API key is optional:

```python
from pyopenfigi import OpenFigi

wrapper = OpenFigi()
wrapper = OpenFigi(api_key="XXXXXXXXXX")
```

## Mapping

The `map()` method takes a list of `MappingJob` as argument and returns a list of `MappingJobResult`. The
result of the request at index `i` in the list of mapping jobs is located at index `i` in the list of results.

```python
from pyopenfigi import OpenFigi, MappingJob

mapping_job = MappingJob(id_type="TICKER", id_value="IBM", exch_code="US")
mapping_jobs = [mapping_job]
results = OpenFigi().map(mapping_jobs)

>>> results
[
    MappingJobResultFigiList(
        data = [
            FigiResult(
                  figi='BBG000BLNNH6', 
                  security_type='Common Stock', 
                  market_sector='Equity', 
                  ticker='IBM', 
                  name='INTL BUSINESS MACHINES CORP', 
                  exch_code='US', 
                  share_class_figi='BBG001S5S399', 
                  composite_figi='BBG000BLNNH6', 
                  security_type2='Common Stock', 
                  security_description='IBM', 
                  metadata=None
            )
        ]
    )
]
```

A `MappingJobResult` can either be a `MappingJobResultFigiList`, a `MappingJobResultFigiNotFound` or a
`MappingJobResultError`.

The `MappingJob` object has 2 required properties which are `id_type` and `id_value`. The other properties are optional
but subject to specific rules in case they are provided. These rules are modeled and checked using **Pydantic**.

Below is the full list of properties for `MappingJob`:

| property                  | required | type | example                                  |
|---------------------------|----------|------|------------------------------------------|
| id_type                   | X        | str  | `"TICKER"`                               |
| id_value                  | X        | str  | `"IBM"`                                  |
| exch_code                 |          | str  | `"UN"`                                   |
| mic_code                  |          | str  | `"XNYS"`                                 |
| currency                  |          | str  | `"USD"`                                  |
| market_sec_des            |          | str  | `"Equity"`                               |
| security_type             |          | str  | `"Common Stock"`                         |
| security_type_2           |          | str  | `"Common Stock"`                         |
| include_unlisted_equities |          | bool |                                          |
| option_type               |          | str  | `"Call"`                                 | 
| strike                    |          | list | `[100, 200]`                             |
| contract_size             |          | list | `[0, 100]`                               |
| coupon                    |          | list | `[0, 2.5]`                               |
| expiration                |          | list | `[date(2023, 6, 1), date(2023, 12, 31)]` |
| maturity                  |          | list | `[date(2023, 6, 1), date(2023, 12, 31)]` |
| state_code                |          | str  | `"AZ"`                                   |

Some of the properties in the `MappingJob` are "enum-like". For each of these properties, it is possible to
retrieve the current list of accepted values via specific methods:

| property        | method                   | examples |
|-----------------|--------------------------|----------|
| id_type         | `get_id_types()`         |          |
| exch_code       | `get_exch_codes()`       |          |
| mic_code        | `get_mic_codes()`        |          |
| currency        | `get_currencies()`       |          |
| market_sec_des  | `get_market_sec_des()`   |          |
| security_type   | `get_security_types()`   |          |
| security_type_2 | `get_security_types_2()` |          |
| state_code      | `get_state_codes()`      |          |

For example, to retrieve the current values for `id_type`:

```python
from pyopenfigi import OpenFigi

id_types = OpenFigi().get_id_types()
```

## Filtering

The `filter()` method takes a `Query` object as argument and returns a list of `FigiResult`.

* The `Query` object is very similar to the `MappingJob` object 
* The only difference are that the `id_type` and `id_value` are replaced by a single `query` property
* All the "enum-like" properties are the same and the list of accepted values is the same
* The maximum number of results is limited to 15,000

| property                  | required | type | example                                  |
|---------------------------|----------|------|------------------------------------------|
| query                     | X        | str  | `"SJIM"`                                 |
| exch_code                 |          | str  | `"UN"`                                   |
| mic_code                  |          | str  | `"XNYS"`                                 |
| currency                  |          | str  | `"USD"`                                  |
| market_sec_des            |          | str  | `"Equity"`                               |
| security_type             |          | str  | `"Common Stock"`                         |
| security_type_2           |          | str  | `"Common Stock"`                         |
| include_unlisted_equities |          | bool |                                          |
| option_type               |          | str  | `"Call"`                                 | 
| strike                    |          | list | `[100, 200]`                             |
| contract_size             |          | list | `[0, 100]`                               |
| coupon                    |          | list | `[0, 2.5]`                               |
| expiration                |          | list | `[date(2023, 6, 1), date(2023, 12, 31)]` |
| maturity                  |          | list | `[date(2023, 6, 1), date(2023, 12, 31)]` |
| state_code                |          | str  | `"AZ"`                                   |

Example

```python
from pyopenfigi import OpenFigi, Query

query = Query(query="SJIM")
results = OpenFigi().filter(query)
```

In order to know the total number of matches for a given query before starting to request them, it is possible to use 
the `get_total_number_of_matches()` method:

```python
from pyopenfigi import OpenFigi, Query

query = Query(query="SJIM")
number_of_results = OpenFigi().get_total_number_of_matches(query)

>>> number_of_results
36
```


## Troubleshooting

Several kinds of errors can occur.

* `ValidationError`: the `MappingJob` and `Query` objects are modeled using **Pydantic** and therefore need to be
  properly instantiated. If an error occurs, a `pydantic.exceptions.ValidationError` will be raised.

* `HTTPError`: in case the status code of the HTTP response is not 200, an HTTPError exception will be raised. Note:
  in case a particular symbol is not found, the API will still respond with a status 200 and a `MappingNotFound`
  object. HTTP errors only occur if there is a real error like a malformed `MappingJob` request (which should not
  happen since all `MappingJob` objects are checked by **Pydantic** prior to being sent), a rate limitation or an
  internal server error.

Here is how to check for `ValidationError` in case the mapping jobs are instantiated programmatically:

```python3
from pydantic import ValidationError

from pyopenfigi import MappingJob

tickers = ["IBM", "XRX", "TSLA", None, "MSFT"]

mapping_jobs = []
for ticker in tickers:
    try:
        mapping_job = MappingJob(id_type="TICKER", id_value=ticker, exch_code="US")
        mapping_jobs.append(mapping_job)
    except ValidationError:
        print(f"Error when trying to build a MappingJob with {ticker=}")
        # Do something
        continue
```

And here is how to check for `HTTPError` in case exceptions need to be handled:

```python
from pyopenfigi import OpenFigi, MappingJob
from pyopenfigi.exceptions import HTTPError

mapping_jobs = [MappingJob(id_type="TICKER", id_value="IBM", exch_code="US")]

try:
    results = OpenFigi().map(mapping_jobs)
except HTTPError as e:
    print(f"{e}")
    # Do something
```
