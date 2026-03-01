import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")  # Windows only — ignored on Lambda (Linux)
except AttributeError:
    pass

import os
from datetime import datetime

from collectors.market_data import get_market_data, get_eur_usd
from collectors.crypto_data import get_crypto_data
from collectors.news_collector import get_news
from analyzer import analyze_market
from report_generator import generate_html_report
from emailer import send_report
from alerts import check_alerts
from screener import get_top_picks
from portfolio_advisor import get_portfolio_advice

# ── Data split ────────────────────────────────────────────────────────────────
US_CATEGORIES     = {"Indices US", "Actions Tech US", "Actions US"}
EUROPE_CATEGORIES = {"Indices Europe", "ETFs", "Matières Premières", "Actions Europe"}


def _filter(market_data, categories):
    return {k: v for k, v in market_data.items() if k in categories and v}


def save_report(html: str, suffix: str) -> str:
    # Lambda: write to /tmp (only writable directory). Local: write to reports/
    if os.path.exists("/tmp"):
        reports_dir = "/tmp/reports"
    else:
        reports_dir = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(reports_dir, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    path = os.path.join(reports_dir, f"{stamp}_{suffix}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path


def _build_and_send(scope, market_data, crypto_data, news, alerts, eur_usd):
    date_str = datetime.now().strftime("%d/%m/%Y")
    label = {"US": "🇺🇸 US", "Europe": "🇪🇺 Europe", "Crypto": "₿ Crypto"}[scope]
    print(f"\n  ── {label} ──")

    top_picks = get_top_picks(market_data, scope=scope) if scope != "Crypto" else []
    if top_picks:
        print("    Top picks: " + ", ".join(f"{s['name']} ({s['score']:+.1f})" for s in top_picks))

    print(f"    AI analysis {label}...")
    ai = analyze_market(market_data, crypto_data, news, scope=scope, eur_usd=eur_usd)

    print(f"    Investment plan {label}...")
    portfolio = get_portfolio_advice(market_data, crypto_data, top_picks, scope=scope, eur_usd=eur_usd)

    html = generate_html_report(
        market_data, crypto_data, news, ai,
        alerts=alerts, top_picks=top_picks, scope=scope,
        portfolio_advice=portfolio, eur_usd=eur_usd,
    )
    path = save_report(html, scope.lower())
    print(f"    Saved: {path}")

    subject = f"Market Report {label} — {date_str}"
    send_report(html, subject=subject)


def run():
    print(f"\n=== Market Reporter — {datetime.now().strftime('%d/%m/%Y %H:%M')} ===\n")

    print("[1/4] Fetching market data...")
    market_data = get_market_data()
    eur_usd = get_eur_usd()
    print(f"  EUR/USD rate: {eur_usd} (1€ = {1/eur_usd:.4f}$)")

    print("[2/4] Fetching crypto data...")
    crypto_data = get_crypto_data()

    print("[3/4] Fetching news...")
    news = get_news()

    all_alerts = check_alerts(market_data, crypto_data)
    if all_alerts:
        print(f"  ⚠ {len(all_alerts)} alert(s): " + " | ".join(a["message"] for a in all_alerts))
    else:
        print("  No alerts triggered")

    print("[4/4] Generating and sending 3 reports...")

    us_data     = _filter(market_data, US_CATEGORIES)
    europe_data = _filter(market_data, EUROPE_CATEGORIES)
    us_alerts     = [a for a in all_alerts if a.get("level") in ("warning", "danger")
                     and any(a["name"] in item["name"]
                             for items in us_data.values() for item in items)]
    europe_alerts = [a for a in all_alerts if a.get("level") in ("warning", "danger")
                     and any(a["name"] in item["name"]
                             for items in europe_data.values() for item in items)]
    crypto_alerts = [a for a in all_alerts if a.get("level") in ("warning", "danger")
                     and any(a["name"].split(" ")[0] in c["name"]
                             for c in crypto_data)]

    _build_and_send("US",     us_data,     [],          news, us_alerts,     eur_usd)
    _build_and_send("Europe", europe_data, [],          news, europe_alerts, eur_usd)
    _build_and_send("Crypto", {},          crypto_data, news, crypto_alerts, eur_usd)

    print("\n✓ 3 reports sent successfully!\n")


if __name__ == "__main__":
    run()
