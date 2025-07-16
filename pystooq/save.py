"""
Saves stooq data
"""


from datetime import date
import os
import pandas as pd
import shutil
import time

from pystooq.load import get_ticker_filename, get_stooq_ticker
from pystooq.stooq_data_fetcher import StooqDataFetcher


def save_tickers(tickers, date_range, use_cwd=False):
    for ticker in tickers:
        ## use cwd or standard stooq path
        if use_cwd:
            stooq_ticker = get_stooq_ticker(ticker)
            filename = "%s.csv" % stooq_ticker
        else:
            filename = get_ticker_filename(ticker)

        start, end = date_range

        ## check for existing data before downloading
        if os.path.isfile(filename):
            df1 = pd.read_csv(filename)
            print("Found existing %s with %i entries." % (filename, len(df1.index)))
            start_date = date.fromisoformat(start)
            end_date = date.fromisoformat(end)
            first_date_str = df1["date"].iloc[0]
            last_date_str = df1["date"].iloc[-1]
            first_date = date.fromisoformat(first_date_str)
            last_date = date.fromisoformat(last_date_str)
            del df1
            assert start_date <= end_date
            if (first_date <= start_date) and (end_date <= last_date):
                print("Requested date range (%s, %s) is within existing data (%s, %s)." % (start_date, end_date, first_date, last_date))
                continue
            else:
                print("Requested date range (%s, %s) is not within existing data (%s, %s)." % (start_date, end_date, first_date, last_date))

        ## fetch data from stooq
        dfs = __fetch_data([ticker], start, end)
        assert len(dfs) == 1
        stooq_ticker = get_stooq_ticker(ticker)
        df = dfs[stooq_ticker]

        ## check that data isn't empty
        assert len(df.index) > 0

        ## check for existing data and merge
        if os.path.isfile(filename):
            df = df.reset_index()
            df["date"] = pd.to_datetime(df["date"], yearfirst=True)
            df1 = pd.read_csv(filename)
            print("Merging with existing %s with %i entries." % (filename, len(df1.index)))
            df1["date"] = pd.to_datetime(df1["date"], yearfirst=True)
            df = pd.concat([df, df1], ignore_index=True)
            df = df.drop_duplicates(subset="date", keep="last")
            df = df.set_index("date")
            df = df.sort_index()
            shutil.copy(filename, filename + ".bak")

        ## save data
        print("Saving %s with %i entries." % (filename, len(df.index)))
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        df.to_csv(filename)

        ## slow down requests
        time.sleep(10)


def __fetch_data(tickers, start, end):
    print("Fetching data for %s" % (tickers))
    fetcher = StooqDataFetcher()
    stooq_tickers = [ get_stooq_ticker(_t) for _t in tickers ]
    dfs = fetcher.get_data(
        tickers=stooq_tickers,
        start=date.fromisoformat(start),
        end=date.fromisoformat(end),
    )
    return dfs


