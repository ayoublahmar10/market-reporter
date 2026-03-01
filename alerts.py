# Alert rules — minimum % change required to trigger an alert
ALERT_RULES = [
    # Crypto
    {"name": "Bitcoin",              "key": "BTC",                  "type": "crypto", "threshold": 5.0},
    {"name": "Ethereum",             "key": "ETH",                  "type": "crypto", "threshold": 7.0},
    {"name": "Solana",               "key": "SOL",                  "type": "crypto", "threshold": 8.0},
    # Indices
    {"name": "CAC 40",               "key": "CAC 40",               "type": "market", "threshold": 2.0},
    {"name": "S&P 500",              "key": "S&P 500",              "type": "market", "threshold": 2.0},
    {"name": "Nasdaq",               "key": "Nasdaq",               "type": "market", "threshold": 2.5},
    # Commodities
    {"name": "Or (Gold)",            "key": "Or (Gold)",            "type": "market", "threshold": 2.0},
    {"name": "Pétrole WTI",          "key": "Pétrole WTI",          "type": "market", "threshold": 3.0},
    {"name": "Gaz Naturel",          "key": "Gaz Naturel",          "type": "market", "threshold": 4.0},
    # US Tech stocks
    {"name": "Nvidia (NVDA)",        "key": "Nvidia",               "type": "market", "threshold": 5.0},
    {"name": "Tesla (TSLA)",         "key": "Tesla",                "type": "market", "threshold": 6.0},
    {"name": "Apple (AAPL)",         "key": "Apple",                "type": "market", "threshold": 4.0},
    {"name": "Microsoft (MSFT)",     "key": "Microsoft",            "type": "market", "threshold": 4.0},
    {"name": "Meta (META)",          "key": "Meta",                 "type": "market", "threshold": 5.0},
    {"name": "AMD",                  "key": "AMD",                  "type": "market", "threshold": 5.0},
    # European stocks
    {"name": "ASML",                 "key": "ASML",                 "type": "market", "threshold": 4.0},
    {"name": "LVMH",                 "key": "LVMH",                 "type": "market", "threshold": 3.0},
    {"name": "TotalEnergies",        "key": "TotalEnergies",        "type": "market", "threshold": 3.0},
    {"name": "SAP",                  "key": "SAP",                  "type": "market", "threshold": 4.0},
    {"name": "Siemens",              "key": "Siemens",              "type": "market", "threshold": 4.0},
]


def check_alerts(market_data, crypto_data):
    """
    Compare each asset's daily change against its threshold.
    Returns a list of alert dicts sorted by magnitude.
    level = "danger"  if change >= 1.5x threshold
    level = "warning" if change >= threshold
    """
    alerts = []

    crypto_by_symbol = {c["symbol"]: c for c in crypto_data}
    all_market_items = [item for items in market_data.values() for item in items]
    market_by_name = {item["name"]: item for item in all_market_items}

    for rule in ALERT_RULES:
        if rule["type"] == "crypto":
            asset = crypto_by_symbol.get(rule["key"])
        else:
            asset = market_by_name.get(rule["key"])

        if not asset:
            continue

        change = asset["change"]
        if abs(change) >= rule["threshold"]:
            direction = "en hausse" if change > 0 else "en baisse"
            level = "danger" if abs(change) >= rule["threshold"] * 1.5 else "warning"
            alerts.append({
                "level": level,
                "name": rule["name"],
                "change": change,
                "message": f"{rule['name']} {direction} de {abs(change):.1f}%",
            })

    alerts.sort(key=lambda x: abs(x["change"]), reverse=True)
    return alerts
