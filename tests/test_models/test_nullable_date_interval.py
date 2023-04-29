import datetime as dt

import pytest
from pydantic import BaseModel, ValidationError

from pyopenfigi.models import NullableDateInterval


class TestModel(BaseModel):
    expiration: NullableDateInterval


@pytest.mark.parametrize(
    "expiration",
    [
        [dt.date(2023, 1, 1)],
        [dt.date(2023, 1, 1), dt.date(2023, 1, 2), dt.date(2023, 1, 3)],
        [None, None],
        [dt.date(2020, 1, 1), dt.date(2023, 1, 1)],
    ],
)
def test_invalid_inputs_should_raise_exception(expiration):
    """
    Test that an invalid combination of inputs raises a ValidationError exception.
    """
    with pytest.raises(ValidationError):
        test_model = TestModel(expiration=expiration)


@pytest.mark.parametrize(
    "expiration",
    [
        [dt.date(2023, 1, 1), dt.date(2023, 12, 31)],
        [None, dt.date(2023, 12, 31)],
        [dt.date(2023, 1, 1), None],
    ],
)
def test_valid_inputs_should_instantiate(expiration):
    """
    Test that a valid combination of inputs instantiates the list.
    """
    test_model = TestModel(expiration=expiration)

    assert isinstance(test_model.expiration, list)
    assert test_model.expiration == expiration


@pytest.mark.parametrize(
    "expiration,result",
    [
        ([dt.date(2023, 1, 1), dt.date(2023, 12, 31)], '{"expiration": ["2023-01-01", "2023-12-31"]}'),
        ([None, dt.date(2023, 12, 31)], '{"expiration": [null, "2023-12-31"]}'),
        ([dt.date(2023, 1, 1), None], '{"expiration": ["2023-01-01", null]}'),
    ],
)
def test_dates_should_be_correctly_serialized(expiration, result):
    """
    Test that the NullableDateInterval objects are correctly serialized into YYYY-MM-DD format.
    """
    test_json = TestModel(expiration=expiration).json()

    assert test_json == result
