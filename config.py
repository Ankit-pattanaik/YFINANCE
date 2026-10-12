"""Central settings for the pipeline. Override tickers/period from the command line."""
from pathlib import Path

ROOT = Path(__file__).parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
CHART_DIR = ROOT / "outputs" / "charts"
REPORT_DIR = ROOT / "outputs" / "reports"
DASHBOARD_DIR = ROOT / "dashboard"

DEFAULT_TICKERS = ["AAPL", "MSFT", "TSLA"]
DEFAULT_BENCHMARK = "SPY"
DEFAULT_PERIOD = "2y"
INTERVAL = "1d"

TRADING_DAYS = 252
RISK_FREE_RATE = 0.0      # annual, used in the Sharpe ratio
SMA_SHORT = 20
SMA_LONG = 50
