# Default categories per scope
SCREENER_CATEGORIES = {
    "US":     {"Actions Tech US", "Actions US"},
    "Europe": {"Actions Europe"},
}


def _momentum_score(item):
    """
    Composite momentum score (0-100 scale, can be negative):
      - 40% weight on today's daily change
      - 60% weight on 7-day trend (sparkline first→last)
    """
    day = item["change"]

    sparkline = item.get("sparkline", [])
    if len(sparkline) >= 2 and sparkline[0] != 0:
        trend_7d = (sparkline[-1] - sparkline[0]) / sparkline[0] * 100
    else:
        trend_7d = 0

    score = day * 0.4 + trend_7d * 0.6
    return round(score, 2), round(trend_7d, 2)


def get_top_picks(market_data, n=5, scope="US"):
    """
    Scan individual stocks for the given scope and return the top n by momentum score.
    Each result dict adds:
      - trend_7d  : % change over last 7 trading days (from sparkline)
      - score     : composite momentum score
    """
    categories = SCREENER_CATEGORIES.get(scope, set())
    candidates = []
    for category, items in market_data.items():
        if category not in categories:
            continue
        for item in items:
            score, trend_7d = _momentum_score(item)
            candidates.append({**item, "trend_7d": trend_7d, "score": score})

    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[:n]
