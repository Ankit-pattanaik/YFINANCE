"""Run the full pipeline: fetch -> clean -> analyze -> visualize -> export.

Example:
    python main.py --tickers AAPL MSFT NVDA --period 5y --benchmark SPY
"""
import argparse
import logging

import config
from src import fetch, clean, analyze, visualize, export


def run(tickers, period, benchmark):
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    symbols = list(dict.fromkeys(tickers + ([benchmark] if benchmark else [])))

    raw = fetch.fetch_prices(symbols, period, config.INTERVAL)
    fetch.save_raw(raw, config.RAW_DIR)
    prices = clean.clean_all(raw)
    export.save_processed(prices, config.PROCESSED_DIR)

    bench_close = prices[benchmark]["Close"] if benchmark in prices else None
    analysed = {t: prices[t] for t in tickers if t in prices}

    summary = analyze.summarize(analysed, bench_close)
    export.save_summary(summary, config.REPORT_DIR)

    for t, df in analysed.items():
        visualize.plot_price(t, df, config.CHART_DIR / f"{t}_price.png")
        visualize.plot_backtest(t, df["Close"], config.CHART_DIR / f"{t}_backtest.png")
    visualize.plot_cumulative(analysed, config.CHART_DIR / "cumulative_return.png")
    visualize.plot_drawdown(analysed, config.CHART_DIR / "drawdown.png")

    export.write_dashboard_data(analysed, config.DASHBOARD_DIR / "data.js", period)
    return summary


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Stock analysis pipeline using yfinance")
    p.add_argument("--tickers", nargs="+", default=config.DEFAULT_TICKERS)
    p.add_argument("--period", default=config.DEFAULT_PERIOD, help="e.g. 6mo, 1y, 2y, 5y")
    p.add_argument("--benchmark", default=config.DEFAULT_BENCHMARK, help="e.g. SPY, or '' for none")
    a = p.parse_args()
    result = run([t.upper() for t in a.tickers], a.period, a.benchmark.upper() or None)
    print(result.round(3).to_string())
    print("\nSaved charts, reports and dashboard/data.js. Open dashboard/index.html.")
