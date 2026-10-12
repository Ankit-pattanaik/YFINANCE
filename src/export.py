"""Write cleaned data and reports to disk, and feed the HTML dashboard."""
import json
from datetime import date


def save_processed(prices, directory):
    directory.mkdir(parents=True, exist_ok=True)
    for t, df in prices.items():
        df.to_csv(directory / f"{t}.csv")


def save_summary(summary, directory):
    directory.mkdir(parents=True, exist_ok=True)
    summary.round(4).to_csv(directory / "summary.csv")


def write_dashboard_data(prices, path, period):
    """Create dashboard/data.js so index.html opens with your real data."""
    series = {
        t: [
            {"d": d.strftime("%Y-%m-%d"), "o": round(r.Open, 4), "h": round(r.High, 4),
             "l": round(r.Low, 4), "c": round(r.Close, 4), "v": int(r.Volume)}
            for d, r in df.iterrows()
        ]
        for t, df in prices.items()
    }
    payload = {"meta": {"generated": date.today().isoformat(), "period": period,
                        "source": "Yahoo Finance via yfinance"},
               "series": series}
    path.write_text("window.PRELOADED = " + json.dumps(payload) + ";\n", encoding="utf-8")
