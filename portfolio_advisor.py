from groq import Groq
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

# Categories whose prices are denominated in USD (need EUR conversion)
USD_CATEGORIES = {"Indices US", "Actions Tech US", "Actions US", "ETFs"}


def _build_context(market_data, crypto_data, top_picks, eur_usd: float, scope: str):
    """Build a compact price context with EUR conversion where relevant."""
    lines = []

    if top_picks:
        lines.append("Meilleures opportunités momentum du jour :")
        for i, s in enumerate(top_picks, 1):
            sign_d = "+" if s["change"] >= 0 else ""
            sign_7 = "+" if s["trend_7d"] >= 0 else ""
            price_eur = round(s["price"] * eur_usd, 2) if scope in ("US", "Crypto") else s["price"]
            lines.append(
                f"  {i}. {s['name']} ({s['ticker']}) — "
                f"prix: {price_eur:,.2f}€  |  jour: {sign_d}{s['change']:.1f}%  |  "
                f"7j: {sign_7}{s['trend_7d']:.1f}%  |  score: {s['score']:+.1f}"
            )

    lines.append("\nTous les actifs disponibles (prix converti en EUR) :")
    for category, items in market_data.items():
        is_usd = category in USD_CATEGORIES
        for item in items:
            price_eur = round(item["price"] * eur_usd, 2) if is_usd else item["price"]
            price_str = f"{item['price']:,.2f}$ = {price_eur:,.2f}€" if is_usd else f"{item['price']:,.2f}€"
            lines.append(f"  {item['name']} ({item['ticker']}) — {price_str}")

    for coin in crypto_data:
        price_eur = round(coin["price"] * eur_usd, 2)
        lines.append(f"  {coin['name']} ({coin['symbol']}) — ${coin['price']:,.2f} = {price_eur:,.2f}€")

    return "\n".join(lines)


def get_portfolio_advice(market_data, crypto_data, top_picks, scope="US", eur_usd=0.92):
    """
    Generate concrete monthly investment plans for 3 budget tiers.
    All amounts are in EUR. USD assets are converted using the real-time eur_usd rate.
    """
    usd_note = ""
    if scope in ("US", "Crypto"):
        usd_note = (
            f"\nTAUX DE CHANGE DU JOUR : 1 USD = {eur_usd:.4f} EUR "
            f"(1 EUR = {1/eur_usd:.4f} USD). "
            "Tous les montants dans les plans ci-dessous DOIVENT être en EUR."
        )

    scope_desc = {
        "US": (
            "marchés américains (actions US et ETFs cotés en USD). "
            "L'investisseur est européen et investit en EUR via Trade Republic ou DEGIRO. "
            "Les prix USD ont été convertis en EUR dans les données ci-dessous."
        ),
        "Europe": (
            "marchés européens (actions EU et ETFs en EUR). "
            "L'investisseur est européen, aucune conversion nécessaire."
        ),
        "Crypto": (
            "marchés crypto. Les prix sont en USD mais l'investisseur investit en EUR. "
            "Les prix ont été convertis en EUR dans les données ci-dessous."
        ),
    }.get(scope, "")

    context_data = _build_context(market_data, crypto_data, top_picks, eur_usd, scope)

    currency_risk_note = ""
    if scope == "US":
        currency_risk_note = (
            f"\nRISQUE DE CHANGE : Les actions US sont cotées en USD. Si l'EUR/USD varie, "
            f"la valeur en euros de tes actions change même si le prix USD reste stable. "
            f"Mentionne ce risque dans la stratégie du budget 500-1000€."
        )

    prompt = f"""Tu es un conseiller en gestion de patrimoine pour un investisseur particulier européen, spécialisé sur les {scope_desc}{usd_note}

{context_data}
{currency_risk_note}

Génère un plan d'investissement mensuel CONCRET ET RÉALISTE pour 3 budgets différents.
Utilise UNIQUEMENT les actifs dont les prix sont listés ci-dessus. TOUS les montants sont en EUR (€).

RÈGLES CRITIQUES :
- Convertis TOUS les prix USD en EUR en utilisant le taux fourni avant de juger l'accessibilité.
- Si le prix unitaire en EUR dépasse 50% du budget mensuel, indique "(fractions disponibles sur Trade Republic)" ou remplace par un ETF.
- Pour les petits budgets (100-300€), priorise les ETFs diversifiés et les actions < 150€.
- Base chaque choix sur le score momentum ET le prix en EUR réel.
- Les montants doivent totaliser exactement le budget.

FORMAT OBLIGATOIRE :

**BUDGET 100-300€/mois**
Stratégie : [1 phrase concise]
- [Nom (TICKER)] — [X]€ ([Y]%) — [raison courte]
- [Nom (TICKER)] — [X]€ ([Y]%) — [raison courte]
- [Nom (TICKER)] — [X]€ ([Y]%) — [raison courte]

**BUDGET 300-500€/mois**
Stratégie : [1 phrase concise]
- [Nom (TICKER)] — [X]€ ([Y]%) — [raison courte]
- [Nom (TICKER)] — [X]€ ([Y]%) — [raison courte]
- [Nom (TICKER)] — [X]€ ([Y]%) — [raison courte]
- [Nom (TICKER)] — [X]€ ([Y]%) — [raison courte]

**BUDGET 500-1000€/mois**
Stratégie : [1 phrase concise]
- [Nom (TICKER)] — [X]€ ([Y]%) — [raison courte]
- [Nom (TICKER)] — [X]€ ([Y]%) — [raison courte]
- [Nom (TICKER)] — [X]€ ([Y]%) — [raison courte]
- [Nom (TICKER)] — [X]€ ([Y]%) — [raison courte]
- [Nom (TICKER)] — [X]€ ([Y]%) — [raison courte]"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1000,
    )
    return response.choices[0].message.content
