"""Download daily price history from Yahoo Finance via yfinance."""
import logging
import yfinance as yf

log = logging.getLogger(__name__)


def fetch_prices(tickers, period="2y", interval="1d"):
    """Return {ticker: DataFrame[Open, High, Low, Close, Volume]}.

    Tickers that return no data are skipped with a warning instead of
    crashing the whole run.
    """
    data = {}
    for t in tickers:
        try:
            df = yf.Ticker(t).history(period=period, interval=interval, auto_adjust=True)
        except Exception as exc:  # network errors, rate limits
            log.warning("Could not download %s: %s", t, exc)
            continue
        if df is None or df.empty:
            log.warning("No data returned for %s", t)
            continue
        data[t] = df
    if not data:
        raise RuntimeError("No price data downloaded. Check tickers and internet connection.")
    return data


def save_raw(data, directory):
    directory.mkdir(parents=True, exist_ok=True)
    for t, df in data.items():
        df.to_csv(directory / f"{t}.csv")
