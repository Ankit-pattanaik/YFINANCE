"""Offline tests for clean -> analyze using synthetic data (no network)."""
import numpy as np
import pandas as pd

from src import clean, analyze


def fake_prices(n=120, tz=True):
    rng = np.random.default_rng(42)
    idx = pd.date_range("2024-01-01", periods=n, freq="B", tz="America/New_York" if tz else None)
    close = 100 * np.exp(np.cumsum(rng.normal(0.0005, 0.01, n)))
    return pd.DataFrame({"Open": close, "High": close * 1.01, "Low": close * 0.99,
                         "Close": close, "Volume": 1_000_000.0}, index=idx)


def test_clean_removes_timezone_and_duplicates():
    df = fake_prices()
    df = pd.concat([df, df.iloc[[5]]])
    out = clean.clean_prices(df)
    assert out.index.tz is None
    assert out.index.is_unique and out.index.is_monotonic_increasing


def test_clean_fills_small_gaps_and_rejects_bad_prices():
    df = fake_prices(tz=False)
    df.iloc[10, df.columns.get_loc("Close")] = np.nan
    df.iloc[20, df.columns.get_loc("Close")] = -5
    out = clean.clean_prices(df)
    assert out["Close"].notna().all()
    assert (out["Close"] > 0).all()


def test_summary_has_expected_columns():
    prices = {"TEST": clean.clean_prices(fake_prices())}
    bench = clean.clean_prices(fake_prices())["Close"]
    s = analyze.summarize(prices, bench)
    for col in ["Total Return", "Ann. Volatility", "Sharpe", "Max Drawdown", "Beta vs Benchmark"]:
        assert col in s.columns
    assert s.loc["TEST", "Max Drawdown"] <= 0
