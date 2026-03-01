from groq import Groq
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

_SCOPE_INSTRUCTIONS = {
    "US": (
        "Tu es un gestionnaire de portefeuille senior spécialisé sur les marchés américains "
        "(S&P 500, Nasdaq, actions US). Tu lis TOUTES les données fournies — indices, actions individuelles, "
        "actualités — pour construire une vue d'ensemble cohérente avant de sélectionner des actions précises.\n"
        "Cite uniquement des tickers US (NVDA, AAPL, JPM, META, XOM, etc.)."
    ),
    "Europe": (
        "Tu es un gestionnaire de portefeuille senior spécialisé sur les marchés européens "
        "(CAC 40, DAX, actions EU, matières premières). Tu lis TOUTES les données fournies — indices, "
        "actions individuelles, matières premières, actualités — pour construire une vue d'ensemble "
        "cohérente avant de sélectionner des actions précises.\n"
        "Cite uniquement des tickers EU (ASML, MC.PA, TTE.PA, SAP.DE, SIE.DE, etc.)."
    ),
    "Crypto": (
        "Tu es un analyste crypto senior. Tu lis TOUTES les données fournies — prix, variations 24h, "
        "tendances 7 jours, actualités — pour construire une vue macro du marché crypto avant de "
        "sélectionner des cryptos précises.\n"
        "Cite toujours le nom + symbole (Bitcoin (BTC), Ethereum (ETH), etc.)."
    ),
}

_SCOPE_PICKS = {
    "US": """
**2. Sélection d'Actions — Aujourd'hui**
Analyse croisée : pars du contexte macro (indices US) → identifie les secteurs porteurs → sélectionne les meilleures actions individuelles.
Pour CHAQUE action, fournis OBLIGATOIREMENT :
- **Nom (TICKER)** — variation aujourd'hui / tendance 7 jours
- **Thèse d'investissement** : pourquoi cette action EST intéressante MAINTENANT (catalyseur précis issu des données ou des actualités)
- **Signal** : 🟢 ACHETER / 🟡 SURVEILLER / 🔴 ÉVITER
Sélectionne 4 actions issues des données fournies. Priorise celles dont la tendance 7j confirme la direction du jour.""",

    "Europe": """
**2. Sélection d'Actions Européennes — Aujourd'hui**
Analyse croisée : pars du contexte macro (CAC 40, DAX, matières premières) → identifie les secteurs porteurs → sélectionne les meilleures actions individuelles.
Pour CHAQUE action, fournis OBLIGATOIREMENT :
- **Nom (TICKER)** — variation aujourd'hui / tendance 7 jours
- **Thèse d'investissement** : pourquoi cette action EST intéressante MAINTENANT (catalyseur précis)
- **Signal** : 🟢 ACHETER / 🟡 SURVEILLER / 🔴 ÉVITER
Sélectionne 4 actions issues des données fournies. Tiens compte de l'impact des matières premières sur les secteurs industriels et énergétiques.""",

    "Crypto": """
**2. Sélection Crypto — Aujourd'hui**
Analyse croisée : commence par le sentiment macro (BTC domine-t-il ou y a-t-il rotation vers les alts ?) → identifie les cryptos avec la meilleure structure de prix.
Pour CHAQUE crypto, fournis OBLIGATOIREMENT :
- **Nom (SYMBOLE)** — variation 24h / tendance 7 jours
- **Thèse** : pourquoi MAINTENANT (momentum, catalyseur, news)
- **Signal** : 🟢 ACHETER / 🟡 SURVEILLER / 🔴 ÉVITER
Sélectionne 3 cryptos. Indique si c'est un marché à dominance BTC ou rotation vers les alts.""",
}

_SCOPE_TAIL = {
    "US": """
**3. Contexte Macro & Risques**
- Sentiment global (Bullish / Bearish / Neutre) en 2 phrases
- 2 risques concrets pour les 24-48h prochaines

**4. Points Clés du Jour**
3 observations factuelles tirées directement des chiffres (mouvements notables, divergences).""",

    "Europe": """
**3. Contexte Macro EU & Risques**
- Sentiment global sur les marchés européens en 2 phrases
- Impact or / pétrole / gaz sur les secteurs industriels et énergétiques
- 2 risques concrets pour les 24-48h prochaines

**4. Points Clés du Jour**
3 observations factuelles tirées directement des chiffres.""",

    "Crypto": """
**3. Contexte Macro Crypto & Risques**
- Dominance BTC et structure du marché en 2 phrases
- 2 risques concrets (réglementaire, technique, liquidité)

**4. Points Clés du Jour**
3 observations factuelles tirées directement des chiffres.""",
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
                trend = f" | 7j: {sign_7}{t7:.1f}%"
            else:
                trend = ""
            market_summary += (
                f"  {item['name']} ({item['ticker']}): "
                f"{item['price']:,.2f}  Jour: {sign_d}{item['change']:.2f}%{trend}\n"
            )

    crypto_summary = ""
    if crypto_data:
        crypto_summary = "\nCrypto (24h | 7j):\n"
        for coin in crypto_data:
            sign_d = "+" if coin["change"] >= 0 else ""
            sparkline = coin.get("sparkline", [])
            if len(sparkline) >= 2 and sparkline[0] != 0:
                t7 = (sparkline[-1] - sparkline[0]) / sparkline[0] * 100
                sign_7 = "+" if t7 >= 0 else ""
                trend = f" | 7j: {sign_7}{t7:.1f}%"
            else:
                trend = ""
            crypto_summary += (
                f"  {coin['name']} ({coin['symbol']}): "
                f"${coin['price']:,.2f}  24h: {sign_d}{coin['change']:.2f}%{trend}\n"
            )

    news_summary = "\nActualités du jour (pour identifier les catalyseurs):\n"
    for article in news[:20]:
        news_summary += f"- [{article['source']}] {article['title']}\n"
        if article["summary"]:
            news_summary += f"  {article['summary'][:180]}\n"

    return market_summary, crypto_summary, news_summary


def analyze_market(market_data, crypto_data, news, scope="US", eur_usd=0.92):
    instructions  = _SCOPE_INSTRUCTIONS.get(scope, _SCOPE_INSTRUCTIONS["US"])
    picks_section = _SCOPE_PICKS.get(scope, _SCOPE_PICKS["US"])
    tail_sections = _SCOPE_TAIL.get(scope, _SCOPE_TAIL["US"])

    market_summary, crypto_summary, news_summary = _build_summary(
        market_data, crypto_data, news
    )

    eur_context = ""
    if scope == "US" and eur_usd:
        usd_per_eur = round(1 / eur_usd, 4)
        eur_context = (
            f"\n⚠️ Contexte devise : l'investisseur achète en EUROS."
            f" Taux du jour : 1 € = {usd_per_eur} $ (EUR/USD = {eur_usd})."
            f" Intègre systématiquement le risque de change EUR/USD dans tes recommandations US.\n"
        )

    prompt = f"""{instructions}
{eur_context}
Voici les données complètes du marché — variation du JOUR et tendance sur 7 JOURS :
{market_summary}{crypto_summary}{news_summary}

Produis une analyse ACTIONNABLE en français. Structure OBLIGATOIRE (dans cet ordre) :

**1. Verdict du Jour — Que faire maintenant ?**
Commence directement par la conclusion opérationnelle : les 1 ou 2 actifs précis à acheter AUJOURD'HUI, avec une phrase de justification chacun.
Format : "▶ **Nom (TICKER)** — raison en 1 phrase."
Ensuite : position générale en 1 ligne (acheter / attendre / défensif).
{picks_section}
{tail_sections}

RÈGLES ABSOLUES :
- Toujours citer nom + ticker. Jamais de "un titre tech" ou "une valeur défensive".
- Chaque recommandation DOIT s'appuyer sur un chiffre ou une actualité fourni(e).
- Si la tendance 7j contredit la variation du jour (ex: jour +2% mais 7j -15%), signale-le comme risque.
- Priorise les actifs dont jour ET 7j sont alignés dans la même direction."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=2200,
    )
    return response.choices[0].message.content
