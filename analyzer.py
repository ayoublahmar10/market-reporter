from groq import Groq
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

_SCOPE_INSTRUCTIONS = {
    "US": (
        "You are a senior portfolio manager specialized in US markets "
        "(S&P 500, Nasdaq, US stocks). Read ALL provided data — indices, individual stocks, "
        "news — to build a coherent overview before selecting specific stocks.\n"
        "Only cite US tickers (NVDA, AAPL, JPM, META, XOM, etc.)."
    ),
    "Europe": (
        "You are a senior portfolio manager specialized in European markets "
        "(CAC 40, DAX, EU stocks, commodities). Read ALL provided data — indices, "
        "individual stocks, commodities, news — to build a coherent overview "
        "before selecting specific stocks.\n"
        "Only cite EU tickers (ASML, MC.PA, TTE.PA, SAP.DE, SIE.DE, etc.)."
    ),
    "Crypto": (
        "You are a senior crypto analyst. Read ALL provided data — prices, 24h changes, "
        "7-day trends, news — to build a macro view of the crypto market before "
        "selecting specific cryptos.\n"
        "Always cite name + symbol (Bitcoin (BTC), Ethereum (ETH), etc.)."
    ),
}

_SCOPE_PICKS = {
    "US": """
**2. Stock Picks — Today**
Cross-analysis: start from macro context (US indices) → identify leading sectors → select the best individual stocks.
For EACH stock, provide MANDATORY:
- **Name (TICKER)** — today's change / 7-day trend
- **Investment thesis**: why this stock IS interesting NOW (specific catalyst from data or news)
- **Signal**: 🟢 BUY / 🟡 WATCH / 🔴 AVOID
Select 4 stocks from the provided data. Prioritize those where the 7-day trend confirms today's direction.""",

    "Europe": """
**2. European Stock Picks — Today**
Cross-analysis: start from macro context (CAC 40, DAX, commodities) → identify leading sectors → select the best individual stocks.
For EACH stock, provide MANDATORY:
- **Name (TICKER)** — today's change / 7-day trend
- **Investment thesis**: why this stock IS interesting NOW (specific catalyst)
- **Signal**: 🟢 BUY / 🟡 WATCH / 🔴 AVOID
Select 4 stocks from the provided data. Account for the impact of commodities on industrial and energy sectors.""",

    "Crypto": """
**2. Crypto Picks — Today**
Cross-analysis: start with macro sentiment (is BTC dominant or is there altcoin rotation?) → identify cryptos with the best price structure.
For EACH crypto, provide MANDATORY:
- **Name (SYMBOL)** — 24h change / 7-day trend
- **Thesis**: why NOW (momentum, catalyst, news)
- **Signal**: 🟢 BUY / 🟡 WATCH / 🔴 AVOID
Select 3 cryptos. Indicate whether it is a BTC-dominant market or altcoin rotation.""",
}

_SCOPE_TAIL = {
    "US": """
**3. Macro Context & Risks**
- Overall sentiment (Bullish / Bearish / Neutral) in 2 sentences
- 2 concrete risks for the next 24-48 hours

**4. Key Points of the Day**
3 factual observations drawn directly from the numbers (notable moves, divergences).""",

    "Europe": """
**3. EU Macro Context & Risks**
- Overall sentiment on European markets in 2 sentences
- Impact of gold / oil / gas on industrial and energy sectors
- 2 concrete risks for the next 24-48 hours

**4. Key Points of the Day**
3 factual observations drawn directly from the numbers.""",

    "Crypto": """
**3. Crypto Macro Context & Risks**
- BTC dominance and market structure in 2 sentences
- 2 concrete risks (regulatory, technical, liquidity)

**4. Key Points of the Day**
3 factual observations drawn directly from the numbers.""",
}

_PROFILE_INSTRUCTIONS = {
    "beginner": (
        "⚠️ IMPORTANT — The investor is a BEGINNER: "
        "use simple language, avoid technical jargon, briefly explain each key term "
        "(e.g. 'the S&P 500 is an index of the 500 largest US companies'). "
        "Focus on 'what to do' rather than 'why technically'. "
        "Limit yourself to a maximum of 2 recommendations. Reassure and educate."
    ),
    "intermediate": (
        "ℹ️ The investor is INTERMEDIATE level: "
        "you can use standard financial terms (P/E, support, resistance, momentum) "
        "without defining them. Provide a balanced analysis with macro context and asset selection."
    ),
    "expert": (
        "ℹ️ The investor is an EXPERT: "
        "use full professional vocabulary (RSI, MACD, correlation, beta, spread, etc.). "
        "Provide deep technical analysis, flag subtle divergences, "
        "and do not hesitate to mention advanced strategies (hedging, sector rotation, etc.)."
    ),
}

# Output language instruction — placed LAST in the prompt as the absolute final rule
_LANGUAGE_OUTPUT = {
    "fr": "⚠️ RÈGLE ABSOLUE : Rédige TOUTE ta réponse en FRANÇAIS. Chaque mot, chaque titre, chaque phrase doit être en français.",
    "en": "⚠️ ABSOLUTE RULE: Write your ENTIRE response in ENGLISH. Every word, every heading, every sentence must be in English.",
}


def _build_summary(market_data, crypto_data, news):
    """Build a rich data summary including 7-day trends from sparklines."""
    market_summary = ""
    for category, items in market_data.items():
        if not items:
            continue
        market_summary += f"\n{category}:\n"
        for item in items:
            sign_d = "+" if item["change"] >= 0 else ""
            sparkline = item.get("sparkline", [])
            if len(sparkline) >= 2 and sparkline[0] != 0:
                t7 = (sparkline[-1] - sparkline[0]) / sparkline[0] * 100
                sign_7 = "+" if t7 >= 0 else ""
                trend = f" | 7d: {sign_7}{t7:.1f}%"
            else:
                trend = ""
            market_summary += (
                f"  {item['name']} ({item['ticker']}): "
                f"{item['price']:,.2f}  Day: {sign_d}{item['change']:.2f}%{trend}\n"
            )

    crypto_summary = ""
    if crypto_data:
        crypto_summary = "\nCrypto (24h | 7d):\n"
        for coin in crypto_data:
            sign_d = "+" if coin["change"] >= 0 else ""
            sparkline = coin.get("sparkline", [])
            if len(sparkline) >= 2 and sparkline[0] != 0:
                t7 = (sparkline[-1] - sparkline[0]) / sparkline[0] * 100
                sign_7 = "+" if t7 >= 0 else ""
                trend = f" | 7d: {sign_7}{t7:.1f}%"
            else:
                trend = ""
            crypto_summary += (
                f"  {coin['name']} ({coin['symbol']}): "
                f"${coin['price']:,.2f}  24h: {sign_d}{coin['change']:.2f}%{trend}\n"
            )

    news_summary = "\nToday's news (to identify catalysts):\n"
    for article in news[:20]:
        news_summary += f"- [{article['source']}] {article['title']}\n"
        if article["summary"]:
            news_summary += f"  {article['summary'][:180]}\n"

    return market_summary, crypto_summary, news_summary


def analyze_market(market_data, crypto_data, news, scope="US", eur_usd=0.92, profile="beginner", language="fr"):
    instructions      = _SCOPE_INSTRUCTIONS.get(scope, _SCOPE_INSTRUCTIONS["US"])
    picks_section     = _SCOPE_PICKS.get(scope, _SCOPE_PICKS["US"])
    tail_sections     = _SCOPE_TAIL.get(scope, _SCOPE_TAIL["US"])
    profile_directive = _PROFILE_INSTRUCTIONS.get(profile, _PROFILE_INSTRUCTIONS["intermediate"])
    language_output   = _LANGUAGE_OUTPUT.get(language, _LANGUAGE_OUTPUT["fr"])

    market_summary, crypto_summary, news_summary = _build_summary(
        market_data, crypto_data, news
    )

    eur_context = ""
    if scope == "US" and eur_usd:
        usd_per_eur = round(1 / eur_usd, 4)
        eur_context = (
            f"\n⚠️ Currency context: the investor buys in EUROS."
            f" Today's rate: 1 € = {usd_per_eur} $ (EUR/USD = {eur_usd})."
            f" Always factor in the EUR/USD exchange risk in your US recommendations.\n"
        )

    prompt = f"""{instructions}
{profile_directive}
{eur_context}
Here is the complete market data — DAY change and 7-DAY trend:
{market_summary}{crypto_summary}{news_summary}

Produce an ACTIONABLE analysis. MANDATORY structure (in this order):

**1. Today's Verdict — What to do now?**
Start directly with the operational conclusion: the 1 or 2 specific assets to buy TODAY, with one justification sentence each.
Format: "▶ **Name (TICKER)** — reason in 1 sentence."
Then: overall position in 1 line (buy / wait / defensive).
{picks_section}
{tail_sections}

ABSOLUTE RULES:
- Always cite name + ticker. Never say "a tech stock" or "a defensive value".
- Each recommendation MUST be backed by a figure or a piece of news provided.
- If the 7-day trend contradicts today's move (e.g. day +2% but 7d -15%), flag it as a risk.
- Prioritize assets where day AND 7d are aligned in the same direction.

{language_output}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=2200,
    )
    return response.choices[0].message.content
