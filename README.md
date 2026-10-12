# Stock Analysis Pipeline (yfinance)

A Python pipeline that downloads daily prices with **yfinance**, cleans them, computes return and risk metrics, backtests a moving-average crossover strategy, saves charts and reports, and feeds an interactive HTML dashboard.

## What it does
1. **Fetch** daily OHLCV data for any tickers plus a benchmark (default SPY).
2. **Clean** it: remove timezones and duplicate dates, reject non-positive prices, forward-fill short gaps.
3. **Analyze**: cumulative and annualized return, annualized volatility, Sharpe ratio, maximum drawdown, best and worst day, beta versus the benchmark.
4. **Backtest** an SMA 20/50 crossover against buy-and-hold. The signal is lagged one day to avoid look-ahead bias; costs are ignored.
5. **Visualize**: price with moving averages and volume, cumulative return, drawdown, strategy comparison (PNG).
6. **Export** processed CSVs, `summary.csv`, and `dashboard/data.js` for the dashboard.

## Quick start
```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py --tickers AAPL MSFT NVDA --period 5y --benchmark SPY
```
Then open `dashboard/index.html` in a browser. It loads `data.js` automatically.

## Project structure
```
yfinance-project/
├── main.py              # pipeline entry point (CLI)
├── config.py            # tickers, paths, trading days, SMA windows
├── requirements.txt
├── src/
│   ├── fetch.py         # yfinance download, skips failed tickers
│   ├── clean.py         # validation and tidying
│   ├── analyze.py       # metrics and backtest (pure functions)
│   ├── visualize.py     # matplotlib charts
│   └── export.py        # CSV/report/dashboard data output
├── tests/               # pytest unit tests (run offline)
├── dashboard/index.html # single-file dashboard (canvas charts, no libraries)
├── data/                # raw and processed CSVs (git-ignored)
└── outputs/             # charts/ and reports/
```

## Tests
```bash
pytest -q
```
Tests cover returns, drawdown, volatility, Sharpe, beta, moving averages, the backtest's one-day signal lag, and the cleaning step. They use synthetic data, so they run without internet.

## Metric definitions
- **Annualized volatility** = std of daily returns × √252
- **Sharpe ratio** = mean excess daily return / std × √252 (risk-free rate set in `config.py`, default 0)
- **Max drawdown** = lowest value of price / running peak − 1
- **Beta** = covariance(asset, benchmark) / variance(benchmark)

## Limitations
- Backtest ignores trading costs, slippage and taxes. It is a learning exercise, not a trading signal.
- Prices are dividend/split adjusted (`auto_adjust=True`).
- Yahoo Finance data is unofficial and can be delayed or revised.

## Results
_Add after running:_ screenshots from `outputs/charts/`, your Lighthouse scores for `dashboard/index.html`, and the date you ran it.

> Not financial advice.
