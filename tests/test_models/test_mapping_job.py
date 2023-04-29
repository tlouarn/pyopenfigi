import datetime as dt

import pytest
from pydantic.error_wrappers import ValidationError

from pyopenfigi.models import MappingJob


@pytest.mark.parametrize("id_type", ["BASE_TICKER", "ID_EXCH_SYMBOL"])
def test_id_type_requires_security_type_2(id_type):
    """
    When the id_type is "BASE_TICKER" or "ID_EXCH_SYMBOL",
    the MappingJob must also contain a security_type_2 field.
    """
    id_value = "IBM"
    security_type_2 = "Common Stock"

    mapping_job = MappingJob(id_type=id_type, id_value=id_value, security_type_2=security_type_2)
    assert isinstance(mapping_job, MappingJob)

    with pytest.raises(ValidationError):
        mapping_job = MappingJob(id_type=id_type, id_value=id_value)


@pytest.mark.parametrize("security_type_2", ["Option", "Warrant"])
def test_security_type_2_requires_expiration(security_type_2):
    """
    When the security_type_2 is "Option" or "Warrant",
    the MappingJob must also contain an expiration field.
    """
    id_type = "TICKER"
    id_value = "IBM"
    expiration = [dt.date(2024, 1, 1), dt.date(2024, 6, 30)]

    mapping_job = MappingJob(
        id_type=id_type,
        id_value=id_value,
        security_type_2=security_type_2,
        expiration=expiration,
    )
    assert isinstance(mapping_job, MappingJob)

    with pytest.raises(ValidationError):
        mapping_job = MappingJob(id_type=id_type, id_value=id_value, security_type_2=security_type_2)


def test_security_type_2_requires_maturity():
    """
    When the security_type_2 is "Pool",
    the MappingJob must also contain a maturity field.
    """
    id_type = "TICKER"
    id_value = "IBM"
    security_type_2 = "Pool"
    maturity = [None, dt.date(2023, 12, 31)]

    mapping_job = MappingJob(
        id_type=id_type,
        id_value=id_value,
        security_type_2=security_type_2,
        maturity=maturity,
    )
    assert isinstance(mapping_job, MappingJob)

    with pytest.raises(ValidationError):
        mapping_job = MappingJob(id_type=id_type, id_value=id_value, security_type_2=security_type_2)
