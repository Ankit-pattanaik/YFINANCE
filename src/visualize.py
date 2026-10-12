"""Save charts as PNG files."""
import matplotlib
matplotlib.use("Agg")  # no display needed
import matplotlib.pyplot as plt

from src import analyze
from config import SMA_SHORT, SMA_LONG


def _save(fig, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_price(ticker, df, path):
    close = df["Close"]
    fig, (ax, axv) = plt.subplots(2, 1, figsize=(10, 6), sharex=True,
                                  gridspec_kw={"height_ratios": [3, 1]})
    ax.plot(close, label="Close", lw=1.6)
    ax.plot(analyze.moving_average(close, SMA_SHORT), label=f"SMA {SMA_SHORT}", lw=1.1)
    ax.plot(analyze.moving_average(close, SMA_LONG), label=f"SMA {SMA_LONG}", lw=1.1)
    ax.set_title(f"{ticker} price and moving averages")
    ax.set_ylabel("Price (USD)")
    ax.legend()
    axv.bar(df.index, df["Volume"], width=1.0)
    axv.set_ylabel("Volume")
    _save(fig, path)


def plot_cumulative(prices, path):
    fig, ax = plt.subplots(figsize=(10, 5))
    for t, df in prices.items():
        ax.plot(analyze.cumulative_return(df["Close"]) * 100, label=t)
    ax.axhline(0, color="grey", lw=0.8)
    ax.set_title("Cumulative return")
    ax.set_ylabel("%")
    ax.legend()
    _save(fig, path)


def plot_drawdown(prices, path):
    fig, ax = plt.subplots(figsize=(10, 4))
    for t, df in prices.items():
        ax.plot(analyze.drawdown_series(df["Close"]) * 100, label=t, lw=1.2)
    ax.set_title("Drawdown from previous peak")
    ax.set_ylabel("%")
    ax.legend()
    _save(fig, path)


def plot_backtest(ticker, close, path):
    bt = analyze.sma_crossover_backtest(close)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot((bt["strategy"] - 1) * 100, label=f"SMA {SMA_SHORT}/{SMA_LONG} crossover")
    ax.plot((bt["buy_and_hold"] - 1) * 100, label="Buy and hold")
    ax.set_title(f"{ticker}: crossover strategy vs buy and hold")
    ax.set_ylabel("Return (%)")
    ax.legend()
    _save(fig, path)
