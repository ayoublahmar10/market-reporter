import yfinance as yf

WATCHLIST = {
    "Indices Europe": {
        "^FCHI": "CAC 40",
        "^GDAXI": "DAX",
        "^AEX": "AEX (Amsterdam)",
        "^STOXX50E": "Euro Stoxx 50",
    },
    "Indices US": {
        "^GSPC": "S&P 500",
        "^IXIC": "Nasdaq",
        "^DJI": "Dow Jones",
        "^RUT": "Russell 2000",
    },
    "ETFs": {
        "SPY": "SPDR S&P 500",
        "QQQ": "Invesco QQQ (Nasdaq)",
        "IWDA.AS": "iShares MSCI World",
        "CSPX.L": "iShares Core S&P 500",
    },
    "Matières Premières": {
        "GC=F": "Or (Gold)",
        "CL=F": "Pétrole WTI",
        "NG=F": "Gaz Naturel",
        "SI=F": "Argent (Silver)",
    },
    "Actions Tech US": {
        "NVDA": "Nvidia",
        "AAPL": "Apple",
        "MSFT": "Microsoft",
        "AMZN": "Amazon",
        "GOOGL": "Alphabet (Google)",
        "META": "Meta",
        "TSLA": "Tesla",
        "AMD": "AMD",
    },
    "Actions US": {
        "JPM":   "JPMorgan Chase",
        "BAC":   "Bank of America",
        "XOM":   "ExxonMobil",
        "UNH":   "UnitedHealth",
        "BRK-B": "Berkshire Hathaway",
    },
    "Actions Europe": {
        "ASML":   "ASML",
        "MC.PA":  "LVMH",
        "TTE.PA": "TotalEnergies",
        "SAP.DE": "SAP",
        "SIE.DE": "Siemens",
    },
}


def get_eur_usd() -> float:
    """Fetch today's EUR/USD rate. Returns 0.92 as fallback."""
    try:
        hist = yf.Ticker("EURUSD=X").history(period="2d")
        if not hist.empty:
            return round(float(hist["Close"].iloc[-1]), 4)
    except Exception:
        pass
    return 0.92


def get_market_data():
    results = {}
    for category, tickers in WATCHLIST.items():
        results[category] = []
        for ticker, name in tickers.items():
            try:
                data = yf.Ticker(ticker)
                hist = data.history(period="10d")
                if len(hist) >= 2:
                    prev_close = hist["Close"].iloc[-2]
                    current = hist["Close"].iloc[-1]
                    change = ((current - prev_close) / prev_close) * 100
                    sparkline = list(hist["Close"].tail(7))
                    results[category].append(
                        {
                            "name": name,
                            "ticker": ticker,
                            "price": round(current, 2),
                            "change": round(change, 2),
                            "sparkline": sparkline,
                        }
                    )
            except Exception as e:
                print(f"  Error fetching {ticker}: {e}")
    return results
