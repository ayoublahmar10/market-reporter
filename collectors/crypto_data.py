import requests

CRYPTOS = ["bitcoin", "ethereum", "solana", "binancecoin", "ripple", "cardano"]


def get_crypto_data():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "ids": ",".join(CRYPTOS),
            "order": "market_cap_desc",
            "per_page": 10,
            "page": 1,
            "sparkline": True,
            "price_change_percentage": "24h",
        }
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        results = []
        for coin in data:
            # CoinGecko returns 168 hourly points (7 days) — sample to 7 daily points
            sparkline_raw = coin.get("sparkline_in_7d", {}).get("price", [])
            if sparkline_raw:
                step = max(1, len(sparkline_raw) // 7)
                sparkline = sparkline_raw[::step][-7:]
            else:
                sparkline = []
            results.append(
                {
                    "name": coin["name"],
                    "symbol": coin["symbol"].upper(),
                    "price": coin["current_price"],
                    "change": round(coin.get("price_change_percentage_24h", 0), 2),
                    "market_cap": coin["market_cap"],
                    "sparkline": sparkline,
                }
            )
        return results
    except Exception as e:
        print(f"  Error fetching crypto data: {e}")
        return []
