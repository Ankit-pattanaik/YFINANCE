"""Return, risk and strategy metrics. All functions are pure and unit tested."""
import numpy as np
import pandas as pd

from config import TRADING_DAYS, RISK_FREE_RATE, SMA_SHORT, SMA_LONG


def daily_returns(close):
    return close.pct_change().dropna()


def cumulative_return(close):
    return close / close.iloc[0] - 1


def annualized_return(returns):
    return returns.mean() * TRADING_DAYS


def annualized_volatility(returns):
    return returns.std() * np.sqrt(TRADING_DAYS)


def sharpe_ratio(returns, risk_free=RISK_FREE_RATE):
    excess = returns - risk_free / TRADING_DAYS
    sd = excess.std()
    return 0.0 if np.isnan(sd) or sd < 1e-12 else excess.mean() / sd * np.sqrt(TRADING_DAYS)


def drawdown_series(close):
    return close / close.cummax() - 1


def max_drawdown(close):
    return drawdown_series(close).min()


def moving_average(close, window):
    return close.rolling(window).mean()


def beta(returns, benchmark_returns):
    """Sensitivity of an asset to the benchmark (covariance / benchmark variance)."""
    joined = pd.concat([returns, benchmark_returns], axis=1, join="inner").dropna()
    if len(joined) < 2:
        return np.nan
    var = joined.iloc[:, 1].var()
    return np.nan if var == 0 else joined.iloc[:, 0].cov(joined.iloc[:, 1]) / var


def sma_crossover_backtest(close, short=SMA_SHORT, long=SMA_LONG):
    """Long when the short SMA is above the long SMA, otherwise in cash.

    The signal is shifted one day so a trade uses yesterday's information
    (no look-ahead bias). Costs and slippage are ignored.
    """
    signal = (moving_average(close, short) > moving_average(close, long)).astype(int)
    position = signal.shift(1).fillna(0)
    asset_ret = close.pct_change().fillna(0)
    return pd.DataFrame({
        "strategy": (1 + position * asset_ret).cumprod(),
        "buy_and_hold": (1 + asset_ret).cumprod(),
        "position": position,
    })


def summarize(prices, benchmark=None):
    """One row of metrics per ticker. `benchmark` is a Close Series (optional)."""
    bench_ret = daily_returns(benchmark) if benchmark is not None else None
    rows = {}
    for t, df in prices.items():
        close = df["Close"]
        ret = daily_returns(close)
        bt = sma_crossover_backtest(close)
        row = {
            "Last Price": close.iloc[-1],
            "Total Return": cumulative_return(close).iloc[-1],
            "Ann. Return": annualized_return(ret),
            "Ann. Volatility": annualized_volatility(ret),
            "Sharpe": sharpe_ratio(ret),
            "Max Drawdown": max_drawdown(close),
            "Best Day": ret.max(),
            "Worst Day": ret.min(),
            "SMA Strategy Return": bt["strategy"].iloc[-1] - 1,
        }
        if bench_ret is not None:
            row["Beta vs Benchmark"] = beta(ret, bench_ret)
        rows[t] = row
    return pd.DataFrame(rows).T
