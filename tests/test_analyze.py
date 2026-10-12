import numpy as np
import pandas as pd
import pytest

from src import analyze


def series(values):
    return pd.Series(values, index=pd.date_range("2024-01-01", periods=len(values), freq="B"), dtype=float)


def test_daily_returns():
    r = analyze.daily_returns(series([100, 110, 99]))
    assert r.iloc[0] == pytest.approx(0.10)
    assert r.iloc[1] == pytest.approx(-0.10)


def test_cumulative_return():
    assert analyze.cumulative_return(series([50, 60, 75])).iloc[-1] == pytest.approx(0.5)


def test_max_drawdown():
    # peak 120, trough 90 -> -25%
    assert analyze.max_drawdown(series([100, 120, 90, 110])) == pytest.approx(-0.25)


def test_max_drawdown_rising_prices_is_zero():
    assert analyze.max_drawdown(series([1, 2, 3, 4])) == 0


def test_volatility_of_constant_returns_is_zero():
    r = pd.Series([0.01] * 10)
    assert analyze.annualized_volatility(r) == pytest.approx(0.0, abs=1e-12)


def test_volatility_scaling():
    r = pd.Series([0.01, -0.01] * 50)
    assert analyze.annualized_volatility(r) == pytest.approx(r.std() * np.sqrt(252))


def test_sharpe_zero_when_no_variance():
    assert analyze.sharpe_ratio(pd.Series([0.01] * 10)) == 0.0


def test_sharpe_positive_for_positive_mean():
    rng = np.random.default_rng(0)
    r = pd.Series(rng.normal(0.001, 0.01, 500))
    assert analyze.sharpe_ratio(r) > 0


def test_beta_of_series_against_itself_is_one():
    rng = np.random.default_rng(1)
    r = pd.Series(rng.normal(0, 0.01, 200))
    assert analyze.beta(r, r) == pytest.approx(1.0)


def test_beta_of_doubled_returns_is_two():
    rng = np.random.default_rng(2)
    r = pd.Series(rng.normal(0, 0.01, 200))
    assert analyze.beta(2 * r, r) == pytest.approx(2.0)


def test_moving_average():
    ma = analyze.moving_average(series([1, 2, 3, 4]), 2)
    assert np.isnan(ma.iloc[0])
    assert ma.iloc[-1] == pytest.approx(3.5)


def test_backtest_position_lags_signal_by_one_day():
    close = series(np.linspace(100, 200, 120))
    bt = analyze.sma_crossover_backtest(close, short=5, long=20)
    signal = (analyze.moving_average(close, 5) > analyze.moving_average(close, 20)).astype(int)
    assert bt["position"].iloc[0] == 0
    assert (bt["position"].iloc[1:] == signal.shift(1).fillna(0).iloc[1:]).all()


def test_backtest_stays_in_cash_in_downtrend():
    close = series(np.linspace(200, 100, 150))
    bt = analyze.sma_crossover_backtest(close, short=5, long=20)
    assert bt["strategy"].iloc[-1] >= bt["buy_and_hold"].iloc[-1]
