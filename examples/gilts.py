import datetime as dt

from pyopenfigi import OpenFigi, Query

# Retrieve all UK gilts maturing in 2024 with a coupon smaller than 1%
query = Query(
    query="UKT",
    coupon=[0, 1],
    exch_code="LONDON",
    security_type="UK GILT STOCK",
    maturity=[dt.date(2024, 1, 1), dt.date(2024, 12, 31)]
)
results = OpenFigi().filter(query)
