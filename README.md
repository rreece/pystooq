pystooq
=========================================

[![CI badge](https://github.com/rreece/pystooq/actions/workflows/ci.yml/badge.svg)](https://github.com/rreece/pystooq/actions)

This package provides simple interface for downloading 
daily time series stock ticker data from [Stooq](https://stooq.com) website.

Please note that the authors of this package are not affiliated with 
Stooq in any way.


## Installation

Add the latest commit to your `requirements.txt`

```
pystooq @ git+https://github.com/rreece/pystooq@9e8c1b6601226ab49cebcd64687d53aa9f8618e1
```


## Usage

In order to download Stooq time series of prices for tickers,
saving the data to csv files so that it doesn't  downloaded if you try
to load it again, you can just

```
from pystooq.load import get_ticker_df
ticker = "VOO"
date_range = ("2022-01-01", "2022-01-31")
save_tickers([ticker], date_range)
df = get_ticker_df(ticker, date_range)
```

The dataframe will look like this:

```
                open     high      low    close        volume
date                                                        
2022-01-03  418.392  419.677  416.206  419.657  6.298281e+06
2022-01-04  420.924  421.576  417.711  419.486  6.554652e+06
2022-01-05  419.208  419.813  411.319  411.443  7.891669e+06
2022-01-06  411.012  413.525  408.809  410.898  8.343778e+06
2022-01-07  411.022  412.116  408.147  409.468  6.445063e+06
2022-01-10  406.402  409.085  401.043  408.929  1.097097e+07
2022-01-11  408.597  412.679  405.825  412.517  7.622496e+06
2022-01-12  414.214  415.632  411.904  413.754  8.656516e+06
2022-01-13  414.721  415.325  407.082  408.050  7.872482e+06
2022-01-14  405.031  408.500  403.946  408.174  1.042593e+07
2022-01-18  403.765  406.018  398.713  401.013  1.119752e+07
2022-01-19  402.385  403.687  396.555  396.806  8.566263e+06
2022-01-20  398.559  402.932  391.983  392.434  9.323544e+06
2022-01-21  391.428  393.545  384.698  384.728  1.698360e+07
2022-01-24  379.539  386.816  369.580  386.328  2.407172e+07
2022-01-25  380.404  386.223  375.210  381.640  1.762250e+07
2022-01-26  387.564  389.989  376.751  380.777  1.504870e+07
2022-01-27  384.957  387.860  377.203  378.851  1.303682e+07
2022-01-28  380.068  388.207  375.755  388.140  1.266167e+07
2022-01-31  387.574  395.501  386.308  395.232  9.630049e+06
```


## Basic usage

In order to download Stooq time series of prices for tickers 
`VOO` and `GLD` for a specified time period:

```python
from pystooq.stooq_data_fetcher import StooqDataFetcher

tickers = ["VOO", "GLD"]
stooq_tickers = [ get_stooq_ticker(_t) for _t in tickers ]
fetcher = StooqDataFetcher()
dfs = fetcher.get_data(
    tickers=stooq_tickers,
    start=date.fromisoformat("2022-01-01"),
    end=date.fromisoformat("2022-01-31"),
)
```

This returns a dataframe like above.
This does _not_ save the data in csv files.

