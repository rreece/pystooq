"""
pystooq/pystooq/stooq_data_fetcher.py
"""

from datetime import date, datetime
import io
import requests
import pandas as pd
import typing as t


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
}


def _new_session() -> requests.Session:
    """Create a fresh session with cookies from the Stooq homepage.

    Stooq issues a per-session uid cookie and appears to allow only a small
    number of data downloads per uid before throttling. Fetching a fresh
    homepage cookie per ticker keeps each download within a clean budget.
    """
    session = requests.Session()
    session.headers.update(HEADERS)
    session.get("https://stooq.com/")
    return session


class StooqDataFetcher:

    def __init__(self):
        pass

    @staticmethod
    def _get_url(ticker: str, start: date, end: date):
        return (
            f"https://stooq.com/q/d/l/"
            f"?s={ticker}&d1={start.strftime('%Y%m%d')}&d2={end.strftime('%Y%m%d')}&i=d"
        )

    def _get_data_for_ticker(self, ticker: str, start: date, end: date) -> pd.DataFrame:
        session = _new_session()
        url = self._get_url(ticker, start, end)
        referer = f"https://stooq.com/q/d/?s={ticker}"
        resp = session.get(url, headers={"Referer": referer})
        resp.raise_for_status()
        text = resp.text.strip()
        if not text or text.lower() == "no data":
            raise ValueError(f"No data returned for {ticker} ({start} to {end})")
        df = pd.read_csv(io.StringIO(text))
        df.columns = [el.lower() for el in df.columns]
        df["date"] = [datetime.strptime(el, "%Y-%m-%d").date() for el in df["date"]]
        df.set_index(inplace=True, keys=["date"])
        return df

    def get_data(
            self,
            tickers: t.Union[str, t.List[str]],
            start: date,
            end: date
    ) -> pd.DataFrame:
        data = dict(zip(tickers, [None] * len(tickers)))
        no_data = []
        for ticker in tickers:
            try:
                data[ticker] = self._get_data_for_ticker(ticker, start, end)
            except Exception as e:
                print(f"ERROR: Caught exception {e} when fetching data for ticker {ticker} for dates range "
                      f"{start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}")

        for ticker_, data_ in data.items():
            if data_ is None:
                no_data.append(ticker_)

        if no_data:
            print(f"ERROR: No data has been fetched for the following tickers: {', '.join(no_data)}")

        for ticker in no_data:
            data.pop(ticker)

        return data
