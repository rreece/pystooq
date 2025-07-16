"""
Loads and cleans stooq data
"""


import numpy as np
import os
import pandas as pd


DIR_OF_THIS_FILE = os.path.dirname(os.path.abspath(__file__))


def get_stooq_ticker(ticker):
    ticker_map = {
        "BTC": "BTC.V",
        "ETH": "ETH.V",
    }
    stooq_ticker = ticker_map.get(ticker)
    if stooq_ticker is None:
        region_code = "US"
        stooq_ticker = "%s.%s" % (ticker, region_code)
    return stooq_ticker


def get_ticker_filename(ticker):
    stooq_ticker = get_stooq_ticker(ticker)
    csv_path = os.path.join(
        DIR_OF_THIS_FILE, "daily/%s.csv" % (stooq_ticker)
    )
    return csv_path


def get_ticker_df(ticker, date_range=None):
    csv_path = get_ticker_filename(ticker)
    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"], yearfirst=True)
    df = df.set_index("date")
    # NOTE: The next two lines extend the date index to include possibly missing
    # dates like weekends, and then the replace line uses the previous value to
    # fill the current.
#    df = df.reindex(df_dummy.index)
#    df.replace(inplace=True)
    if date_range:
        start_date, end_date = date_range
        df = df[pd.to_datetime(start_date):pd.to_datetime(end_date)]
    return df


def get_tickers_closes_df(tickers, date_range=None):
    dfs = [get_ticker_df(_t, date_range=date_range) for _t in tickers]
    dfs = [_df["close"] for _df in dfs]
    for _df, _ticker in zip(dfs, tickers):
        _df.rename(_ticker, inplace=True)
    df = pd.concat(dfs, axis=1, join="inner")
    return df

