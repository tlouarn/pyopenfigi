import pytest
from pydantic import BaseModel, ValidationError

from pyopenfigi.models import NullableNumberInterval


class TestModel(BaseModel):
    strike: NullableNumberInterval


@pytest.mark.parametrize("strike", [[0], [0, 1, 2], [None, None], [1, 0]])
def test_invalid_inputs_should_raise_exception(strike):
    """
    Test that an invalid combination of inputs raises a ValidationError exception.
    """
    with pytest.raises(ValidationError):
        test_model = TestModel(strike=strike)


@pytest.mark.parametrize("strike", [[0, 1], [None, 1], [0, None]])
def test_valid_inputs_should_instantiate(strike):
    """
    Test that a valid combination of inputs instantiates the list.
    """
    test_model = TestModel(strike=strike)

    assert isinstance(test_model.strike, list)
    assert test_model.strike == strike
