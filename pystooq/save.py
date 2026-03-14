"""
Saves stooq data with incremental download optimization.

The save_tickers function intelligently downloads only the missing date ranges:
- If data already exists and covers the requested range: skip download entirely
- If data exists but is missing dates at the beginning: download earlier data only
- If data exists but is missing dates at the end: download newer data only
- If no data exists: download entire requested range

This significantly reduces download time and server load for daily updates.

Example:
    Existing data: 2023-12-15 to 2025-12-17
    Requested:     2024-01-01 to 2025-12-18
    Downloads:     2025-12-18 only (1 day instead of ~714 days)
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
        start_date = date.fromisoformat(start)
        end_date = date.fromisoformat(end)
        assert start_date <= end_date

        ## check for existing data and determine what needs to be downloaded
        ranges_to_download = []

        if os.path.isfile(filename):
            df_existing = pd.read_csv(filename)
            print("Found existing %s with %i entries." % (filename, len(df_existing.index)))

            first_date_str = df_existing["date"].iloc[0]
            last_date_str = df_existing["date"].iloc[-1]
            first_date = date.fromisoformat(first_date_str)
            last_date = date.fromisoformat(last_date_str)

            # Check if requested range is fully within existing data
            if (first_date <= start_date) and (end_date <= last_date):
                print("Requested date range (%s, %s) is within existing data (%s, %s). No download needed." % (start_date, end_date, first_date, last_date))
                del df_existing
                continue

            # Determine missing ranges
            # Case 1: Need data before existing data
            if start_date < first_date:
                # Download from start_date to day before first_date
                gap_end = first_date - pd.Timedelta(days=1)
                # Don't download beyond requested end_date
                if gap_end > end_date:
                    gap_end = end_date
                ranges_to_download.append((start_date, gap_end))
                print("Need to download earlier data: %s to %s" % (start_date, gap_end))

            # Case 2: Need data after existing data
            if end_date > last_date:
                # Download from day after last_date to end_date
                gap_start = last_date + pd.Timedelta(days=1)
                # Don't download before requested start_date
                if gap_start < start_date:
                    gap_start = start_date
                ranges_to_download.append((gap_start, end_date))
                print("Need to download newer data: %s to %s" % (gap_start, end_date))

            del df_existing
        else:
            # No existing file, download entire requested range
            print("No existing data found for %s" % ticker)
            ranges_to_download.append((start_date, end_date))

        # Download all missing ranges
        dfs_to_merge = []
        for download_start, download_end in ranges_to_download:
            print("Downloading %s data from %s to %s..." % (ticker, download_start, download_end))
            dfs = __fetch_data([ticker], download_start.isoformat(), download_end.isoformat())
            stooq_ticker = get_stooq_ticker(ticker)

            if len(dfs) == 0 or stooq_ticker not in dfs:
                print("WARNING: No data fetched for %s in range %s to %s (likely market holiday/closure)" % (ticker, download_start, download_end))
                continue

            df = dfs[stooq_ticker]

            ## check that data isn't empty
            if len(df.index) == 0:
                print("WARNING: No data returned for %s in range %s to %s" % (ticker, download_start, download_end))
            else:
                print("Downloaded %i entries" % len(df.index))
                dfs_to_merge.append(df)

            ## slow down requests between downloads
            if len(ranges_to_download) > 1:
                time.sleep(3)

        # If we downloaded any data, merge it with existing file
        if dfs_to_merge:
            # Merge all downloaded dataframes
            if len(dfs_to_merge) > 1:
                df_new = pd.concat(dfs_to_merge)
            else:
                df_new = dfs_to_merge[0]

            # Merge with existing file if it exists
            if os.path.isfile(filename):
                df_new = df_new.reset_index()
                df_new["date"] = pd.to_datetime(df_new["date"], yearfirst=True)
                df_existing = pd.read_csv(filename)
                print("Merging with existing %s with %i entries." % (filename, len(df_existing.index)))
                df_existing["date"] = pd.to_datetime(df_existing["date"], yearfirst=True)
                df = pd.concat([df_new, df_existing], ignore_index=True)
                df = df.drop_duplicates(subset="date", keep="last")
                df = df.set_index("date")
                df = df.sort_index()
                shutil.copy(filename, filename + ".bak")
            else:
                df = df_new

            ## save data
            print("Saving %s with %i entries." % (filename, len(df.index)))
            directory = os.path.dirname(filename)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            df.to_csv(filename)

        ## slow down requests between tickers
        time.sleep(3)


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


