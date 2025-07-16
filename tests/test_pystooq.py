"""
pystooq pytests
"""


from datetime import date

from pystooq.load import get_stooq_ticker
from pystooq.stooq_data_fetcher import StooqDataFetcher


def test_fetcher():
    tickers = ["VOO", "GLD"]
    stooq_tickers = [ get_stooq_ticker(_t) for _t in tickers ]
    fetcher = StooqDataFetcher()
    dfs = fetcher.get_data(
        tickers=stooq_tickers,
        start=date.fromisoformat("2022-01-01"),
        end=date.fromisoformat("2022-01-31"),
    )

    for key, df in dfs.items():
        print(key)
        print(df)
        assert len(df.index) == 20

