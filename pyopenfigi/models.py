import datetime as dt
from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field
from pydantic.class_validators import validator

Key = Literal[
    "idType",
    "exchCode",
    "micCode",
    "currency",
    "marketSecDes",
    "securityType",
    "securityType2",
    "stateCode",
]


class IdType(Enum):
    ID_ISIN = "ID_ISIN"
    ID_BB_UNIQUE = "ID_BB_UNIQUE"
    ID_SEDOL = "ID_SEDOL"
    ID_COMMON = "ID_COMMON"
    ID_WERTPAPIER = "ID_WERTPAPIER"
    ID_CUSIP = "ID_CUSIP"
    ID_BB = "ID_BB"
    ID_ITALY = "ID_ITALY"
    ID_EXCH_SYMBOL = "ID_EXCH_SYMBOL"
    ID_FULL_EXCHANGE_SYMBOL = "ID_FULL_EXCHANGE_SYMBOL"
    COMPOSITE_ID_BB_GLOBAL = "COMPOSITE_ID_BB_GLOBAL"
    ID_BB_GLOBAL_SHARE_CLASS_LEVEL = "ID_BB_GLOBAL_SHARE_CLASS_LEVEL"
    ID_BB_SEC_NUM_DES = "ID_BB_SEC_NUM_DES"
    ID_BB_GLOBAL = "ID_BB_GLOBAL"
    TICKER = "TICKER"
    ID_CUSIP_8_CHR = "ID_CUSIP_8_CHR"
    OCC_SYMBOL = "OCC_SYMBOL"
    UNIQUE_ID_FUT_OPT = "UNIQUE_ID_FUT_OPT"
    OPRA_SYMBOL = "OPRA_SYMBOL"
    TRADING_SYSTEM_IDENTIFIER = "TRADING_SYSTEM_IDENTIFIER"
    ID_CINS = "ID_CINS"
    ID_SHORT_CODE = "ID_SHORT_CODE"
    BASE_TICKER = "BASE_TICKER"
    VENDOR_INDEX_CODE = "VENDOR_INDEX_CODE"


class NullableNumberInterval(list):
    """
    NullableNumberInterval implementation using Pydantic.

    Rules:
    Value should be an Array interval of the form [a, b] where a, b are Numbers or null.
    At least one entry must be a Number. When both are Numbers, it is required that a <= b.
    Also, [a, null] is equivalent to the interval [a, ∞) and [null, b] is equivalent to (-∞, b].
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: Any) -> list[int | float | None]:
        if not isinstance(v, list):
            raise TypeError("List required")

        if len(v) != 2:
            raise TypeError("The list must contain two elements")

        if not isinstance(v[0], int | float | None) or not isinstance(v[1], int | float | None):
            raise TypeError("Elements must be of type int, float or None")

        if v[0] is None and v[1] is None:
            raise TypeError("At least one element must be a number")

        if v[0] is not None and v[1] is not None and v[0] > v[1]:
            raise TypeError("Numbers must be sorted in ascending order")

        return v

    def __repr__(self):
        return super().__repr__()


class NullableDateInterval(list):
    """
    NullableDateInterval implementation using Pydantic.

    Rules:
    Value should be an Array interval of the form [a, b] where a, b are date Strings or null.
    Date strings must be of the form YYYY-MM-DD. At least one entry must be a date String.
    When both are date Strings, it is required that a and b are no more than one year apart.
    Also, [a, null] is equivalent to the interval [a, a + (1 year)] and [null, b] is equivalent to [b - (1 year), b].
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: Any) -> list[str | None]:
        if not isinstance(v, list):
            raise TypeError("List required")

        if len(v) != 2:
            raise TypeError("The list must contain two elements")

        if not isinstance(v[0], dt.date | None) or not isinstance(v[1], dt.date | None):
            raise TypeError("Elements must be of type date or None")

        if v[0] is None and v[1] is None:
            raise TypeError("At least one element must be a date")

        if v[0] is not None and v[1] is not None and v[0] + dt.timedelta(days=365) < v[1]:
            raise TypeError("Dates must not be more than a year apart")

        return v

    def __repr__(self):
        return super().__repr__()


class Model(BaseModel):
    """
    Pydantic BaseModel configured for OpenFIGI models.
    """

    class Config:
        allow_population_by_field_name = True


class MappingJob(Model):
    """
    MappingJob implementation using Pydantic and custom validators.
    """

    id_type: str = Field(alias="idType")
    id_value: str | int = Field(alias="idValue")
    exch_code: Optional[str] = Field(None, alias="exchCode")
    mic_code: Optional[str] = Field(None, alias="micCode")
    currency: Optional[str]
    market_sec_des: Optional[str] = Field(None, alias="marketSecDes")
    security_type: Optional[str] = Field(None, alias="securityType")
    security_type_2: Optional[str] = Field(None, alias="securityType2")
    include_unlisted_equities: Optional[bool] = Field(None, alias="includeUnlistedEquities")
    option_type: Optional[str] = Field(None, alias="optionType")
    strike: Optional[NullableNumberInterval]
    contract_size: Optional[NullableNumberInterval] = Field(None, alias="contractSize")
    coupon: Optional[NullableNumberInterval]
    expiration: Optional[NullableDateInterval]
    maturity: Optional[NullableDateInterval]
    state_code: Optional[str] = Field(None, alias="stateCode")

    class Config:
        json_encoders = {dt.date: lambda v: dt.date.strftime(v, "%Y-%m-%d")}

    @validator("security_type_2", always=True)
    def required_for_some_id_types(cls, v: str | None, values: dict) -> str | None:
        if values["id_type"] in ["BASE_TICKER", "ID_EXCH_SYMBOL"] and v is None:
            raise ValueError("Field security_type_2 is mandatory when id_type is 'BASE_TICKER' or 'ID_EXCH_SYMBOL'")
        return v

    @validator("expiration", always=True)
    def required_for_some_security_type_2(cls, v: list, values: dict) -> list:
        if "security_type_2" in values and values["security_type_2"] in ["Option", "Warrant"] and v is None:
            raise ValueError(f"Field expiration is mandatory when security_type_2 is 'Option' or 'Warrant'")
        return v

    @validator("maturity", always=True)
    def required_for_pool(cls, v: list | None, values: dict) -> list | None:
        if "security_type_2" in values and values["security_type_2"] == "Pool" and v is None:
            raise ValueError("Field maturity is mandatory when security_type_2 is 'Pool'")
        return v


class BulkMappingJob(Model):
    __root__: list[MappingJob]


class FigiResult(Model):
    figi: Optional[str]
    security_type: Optional[str] = Field(None, alias="securityType")
    market_sector: Optional[str] = Field(None, alias="marketSector")
    ticker: Optional[str]
    name: Optional[str]
    exch_code: Optional[str] = Field(None, alias="exchCode")
    share_class_figi: Optional[str] = Field(None, alias="shareClassFIGI")
    composite_figi: Optional[str] = Field(None, alias="compositeFIGI")
    security_type2: Optional[str] = Field(None, alias="securityType2")
    security_description: Optional[str] = Field(None, alias="securityDescription")
    metadata: Optional[str]


class MappingJobResultFigiList(Model):
    data: list[FigiResult]


class MappingJobResultFigiNotFound(Model):
    warning: str


class MappingJobResultError(Model):
    error: str


MappingJobResult = MappingJobResultFigiList | MappingJobResultFigiNotFound | MappingJobResultError


class Query(Model):
    """
    Search/Filter query object implementation using Pydantic.
    """

    query: str
    start: Optional[str]
    exch_code: Optional[str] = Field(None, alias="exchCode")
    mic_code: Optional[str] = Field(None, alias="micCode")
    currency: Optional[str]
    market_sec_des: Optional[str] = Field(None, alias="marketSecDes")
    security_type: Optional[str] = Field(None, alias="securityType")
    security_type_2: Optional[str] = Field(None, alias="securityType2")
    include_unlisted_equities: Optional[bool] = Field(None, alias="includeUnlistedEquities")
    option_type: Optional[str] = Field(None, alias="optionType")
    strike: Optional[NullableNumberInterval]
    contract_size: Optional[NullableNumberInterval] = Field(None, alias="contractSize")
    coupon: Optional[NullableNumberInterval]
    expiration: Optional[NullableDateInterval]
    maturity: Optional[NullableDateInterval]
    state_code: Optional[str] = Field(None, alias="stateCode")

    class Config:
        json_encoders = {dt.date: lambda v: dt.date.strftime(v, "%Y-%m-%d")}

    @validator("expiration", always=True)
    def required_for_some_security_type_2(cls, v: list, values: dict) -> list:
        if "security_type_2" in values and values["security_type_2"] in ["Option", "Warrant"] and v is None:
            raise ValueError(f"Field expiration is mandatory when security_type_2 is 'Option' or 'Warrant'")
        return v

    @validator("maturity", always=True)
    def required_for_pool(cls, v: list | None, values: dict) -> list | None:
        if "security_type_2" in values and values["security_type_2"] == "Pool" and v is None:
            raise ValueError("Field maturity is mandatory when security_type_2 is 'Pool'")
        return v
