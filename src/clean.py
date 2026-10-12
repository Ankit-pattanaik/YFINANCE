"""Validate and tidy raw price data."""
import pandas as pd

COLUMNS = ["Open", "High", "Low", "Close", "Volume"]


def clean_prices(df, max_gap=3):
    """Return a cleaned copy of a price DataFrame.

    Steps: keep OHLCV columns, drop timezone, sort, drop duplicate dates,
    treat non-positive prices as missing, forward-fill gaps up to `max_gap`
    days, then drop any rows that are still missing a Close.
    """
    out = df[[c for c in COLUMNS if c in df.columns]].copy()
    out.index = pd.to_datetime(out.index)
    if out.index.tz is not None:
        out.index = out.index.tz_localize(None)
    out.index = out.index.normalize()
    out = out[~out.index.duplicated(keep="last")].sort_index()

    price_cols = [c for c in ["Open", "High", "Low", "Close"] if c in out.columns]
    out[price_cols] = out[price_cols].where(out[price_cols] > 0)
    out[price_cols] = out[price_cols].ffill(limit=max_gap)
    if "Volume" in out.columns:
        out["Volume"] = out["Volume"].fillna(0)

    return out.dropna(subset=["Close"])


def clean_all(data):
    return {t: clean_prices(df) for t, df in data.items()}
