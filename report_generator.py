import re
from datetime import datetime


def _arrow(change):
    if change > 0:
        return "▲", "#22c55e"
    elif change < 0:
        return "▼", "#ef4444"
    return "—", "#94a3b8"


def _sparkline(prices):
    """Render a Unicode block-char sparkline (works in all email clients)."""
    if not prices or len(prices) < 2:
        return ""
    blocks = "▁▂▃▄▅▆▇█"
    min_p = min(prices)
    max_p = max(prices)
    if max_p == min_p:
        return '<span style="color:#475569;font-family:monospace;">▄▄▄▄▄▄▄</span>'
    color = "#22c55e" if prices[-1] >= prices[0] else "#ef4444"
    result = "".join(
        blocks[int((p - min_p) / (max_p - min_p) * (len(blocks) - 1))]
        for p in prices
    )
    return f'<span style="color:{color};font-family:monospace;letter-spacing:1px;">{result}</span>'


def _market_table(category, items):
    rows = ""
    for item in items:
        symbol, color = _arrow(item["change"])
        spark = _sparkline(item.get("sparkline", []))
        rows += f"""
        <tr>
          <td style="padding:9px 14px;border-bottom:1px solid #1e293b;color:#e2e8f0;">{item['name']} <span style="color:#475569;font-size:11px;">{item['ticker']}</span></td>
          <td style="padding:9px 14px;border-bottom:1px solid #1e293b;text-align:right;font-weight:600;color:#f1f5f9;">{item['price']:,.2f}</td>
          <td style="padding:9px 14px;border-bottom:1px solid #1e293b;text-align:right;color:{color};font-weight:700;">{symbol} {abs(item['change']):.2f}%</td>
          <td style="padding:9px 14px;border-bottom:1px solid #1e293b;text-align:right;font-size:14px;">{spark}</td>
        </tr>"""
    return f"""
    <div style="margin-bottom:20px;">
      <div style="font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">{category}</div>
      <table style="width:100%;border-collapse:collapse;background:#0f172a;border-radius:8px;overflow:hidden;">
        <thead>
          <tr style="background:#1e293b;">
            <th style="padding:9px 14px;text-align:left;color:#475569;font-size:11px;font-weight:600;">ACTIF</th>
            <th style="padding:9px 14px;text-align:right;color:#475569;font-size:11px;font-weight:600;">PRIX</th>
            <th style="padding:9px 14px;text-align:right;color:#475569;font-size:11px;font-weight:600;">VAR.</th>
            <th style="padding:9px 14px;text-align:right;color:#475569;font-size:11px;font-weight:600;">7J</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
    </div>"""


def _crypto_table(crypto_data):
    rows = ""
    for coin in crypto_data:
        symbol, color = _arrow(coin["change"])
        spark = _sparkline(coin.get("sparkline", []))
        rows += f"""
        <tr>
          <td style="padding:9px 14px;border-bottom:1px solid #1e293b;color:#e2e8f0;">{coin['name']} <span style="color:#475569;font-size:11px;">{coin['symbol']}</span></td>
          <td style="padding:9px 14px;border-bottom:1px solid #1e293b;text-align:right;font-weight:600;color:#f1f5f9;">${coin['price']:,.2f}</td>
          <td style="padding:9px 14px;border-bottom:1px solid #1e293b;text-align:right;color:{color};font-weight:700;">{symbol} {abs(coin['change']):.2f}%</td>
          <td style="padding:9px 14px;border-bottom:1px solid #1e293b;text-align:right;font-size:14px;">{spark}</td>
        </tr>"""
    return f"""
    <div style="margin-bottom:20px;">
      <div style="font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">Crypto — Variation 24h</div>
      <table style="width:100%;border-collapse:collapse;background:#0f172a;border-radius:8px;overflow:hidden;">
        <thead>
          <tr style="background:#1e293b;">
            <th style="padding:9px 14px;text-align:left;color:#475569;font-size:11px;font-weight:600;">COIN</th>
            <th style="padding:9px 14px;text-align:right;color:#475569;font-size:11px;font-weight:600;">PRIX USD</th>
            <th style="padding:9px 14px;text-align:right;color:#475569;font-size:11px;font-weight:600;">24H</th>
            <th style="padding:9px 14px;text-align:right;color:#475569;font-size:11px;font-weight:600;">7J</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
    </div>"""


def _alerts_section(alerts):
    if not alerts:
        return ""
    has_danger = any(a["level"] == "danger" for a in alerts)
    border_color = "#ef4444" if has_danger else "#f59e0b"
    bg_color = "#1a0a0a" if has_danger else "#1a1400"

    items_html = ""
    for alert in alerts:
        icon = "▼" if alert["change"] < 0 else "▲"
        color = "#ef4444" if alert["change"] < 0 else "#22c55e"
        dot_color = "#ef4444" if alert["level"] == "danger" else "#f59e0b"
        items_html += f"""
        <div style="display:flex;justify-content:space-between;align-items:center;padding:7px 0;border-bottom:1px solid #1e293b;">
          <span style="color:#e2e8f0;font-size:13px;">
            <span style="color:{dot_color};margin-right:6px;">●</span>{alert['message']}
          </span>
          <span style="color:{color};font-weight:700;font-size:13px;white-space:nowrap;">{icon} {abs(alert['change']):.1f}%</span>
        </div>"""

    return f"""
    <div style="background:{bg_color};border:1px solid {border_color};border-left:3px solid {border_color};border-radius:12px;padding:16px 20px;margin-bottom:16px;">
      <div style="font-size:13px;font-weight:700;color:{border_color};margin-bottom:10px;">&#9888; Alertes du Jour ({len(alerts)})</div>
      {items_html}
    </div>"""


def _top_picks_section(top_picks):
    if not top_picks:
        return ""

    MEDALS = ["🥇", "🥈", "🥉", "④", "⑤"]

    rows = ""
    for i, stock in enumerate(top_picks):
        day_sym,  day_col  = _arrow(stock["change"])
        tr7_sym,  tr7_col  = _arrow(stock["trend_7d"])
        spark = _sparkline(stock.get("sparkline", []))
        medal = MEDALS[i] if i < 3 else f"<span style='color:#475569;font-weight:700;'>#{i+1}</span>"

        # Score bar (0-100 mapped from -10..+10 typical range)
        bar_pct = max(0, min(100, int((stock["score"] + 10) / 20 * 100)))
        bar_color = "#22c55e" if stock["score"] > 0 else "#ef4444"

        rows += f"""
        <tr>
          <td style="padding:10px 14px;border-bottom:1px solid #1e293b;text-align:center;font-size:16px;">{medal}</td>
          <td style="padding:10px 14px;border-bottom:1px solid #1e293b;">
            <div style="font-weight:700;color:#f1f5f9;font-size:13px;">{stock['name']}</div>
            <div style="color:#475569;font-size:10px;text-transform:uppercase;">{stock['ticker']}</div>
          </td>
          <td style="padding:10px 14px;border-bottom:1px solid #1e293b;text-align:right;">
            <span style="color:{day_col};font-weight:700;font-size:13px;">{day_sym} {abs(stock['change']):.1f}%</span>
            <div style="color:#475569;font-size:10px;">Aujourd'hui</div>
          </td>
          <td style="padding:10px 14px;border-bottom:1px solid #1e293b;text-align:right;">
            <span style="color:{tr7_col};font-weight:600;font-size:13px;">{tr7_sym} {abs(stock['trend_7d']):.1f}%</span>
            <div style="color:#475569;font-size:10px;">7 jours</div>
          </td>
          <td style="padding:10px 14px;border-bottom:1px solid #1e293b;text-align:right;font-size:14px;">{spark}</td>
          <td style="padding:10px 14px;border-bottom:1px solid #1e293b;min-width:70px;">
            <div style="background:#1e293b;border-radius:4px;height:6px;width:100%;">
              <div style="background:{bar_color};border-radius:4px;height:6px;width:{bar_pct}%;"></div>
            </div>
            <div style="color:#475569;font-size:10px;text-align:right;margin-top:3px;">{stock['score']:+.1f}</div>
          </td>
        </tr>"""

    return f"""
    <div style="background:#0a0f1e;border:1px solid #14532d;border-left:3px solid #22c55e;border-radius:12px;padding:20px;margin-bottom:16px;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
        <div style="font-size:15px;font-weight:700;color:#f1f5f9;">Top 5 Actions — Momentum</div>
        <div style="font-size:10px;color:#475569;text-transform:uppercase;letter-spacing:1px;">Score = 40% jour + 60% tendance 7j</div>
      </div>
      <table style="width:100%;border-collapse:collapse;background:#0f172a;border-radius:8px;overflow:hidden;">
        <thead>
          <tr style="background:#1e293b;">
            <th style="padding:8px 14px;color:#475569;font-size:10px;font-weight:600;text-align:center;">#</th>
            <th style="padding:8px 14px;color:#475569;font-size:10px;font-weight:600;text-align:left;">ACTION</th>
            <th style="padding:8px 14px;color:#475569;font-size:10px;font-weight:600;text-align:right;">JOUR</th>
            <th style="padding:8px 14px;color:#475569;font-size:10px;font-weight:600;text-align:right;">7J</th>
            <th style="padding:8px 14px;color:#475569;font-size:10px;font-weight:600;text-align:right;">TENDANCE</th>
            <th style="padding:8px 14px;color:#475569;font-size:10px;font-weight:600;text-align:left;">SCORE</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
    </div>"""


def _ai_to_html(text, accent="#3b82f6"):
    # Bold
    text = re.sub(r"\*\*(.*?)\*\*", r'<strong style="color:#f1f5f9;">\1</strong>', text)
    # Arrow verdict marker
    text = text.replace("▶", '<span style="color:#22c55e;font-size:14px;">▶</span>')
    # Signal badges
    text = text.replace("🟢 ACHETER",    '<span style="background:#14532d;color:#4ade80;padding:2px 9px;border-radius:4px;font-size:11px;font-weight:700;letter-spacing:0.5px;">&#9646; ACHETER</span>')
    text = text.replace("🟡 SURVEILLER", '<span style="background:#422006;color:#fbbf24;padding:2px 9px;border-radius:4px;font-size:11px;font-weight:700;letter-spacing:0.5px;">&#9646; SURVEILLER</span>')
    text = text.replace("🔴 ÉVITER",     '<span style="background:#450a0a;color:#f87171;padding:2px 9px;border-radius:4px;font-size:11px;font-weight:700;letter-spacing:0.5px;">&#9646; ÉVITER</span>')

    lines = text.split("\n")
    html_lines = []
    in_verdict = False
    for line in lines:
        stripped = line.strip()
        # Section headers (1. 2. 3. ...)
        if re.match(r"^[1-4]\.", stripped):
            is_verdict = stripped.startswith("1.")
            in_verdict = is_verdict
            bg = f"background:{accent}18;" if is_verdict else ""
            border = f"border-left:3px solid {accent};padding-left:10px;" if is_verdict else ""
            html_lines.append(
                f'<div style="margin-top:20px;padding:8px 12px;{bg}{border}'
                f'border-radius:4px;font-weight:700;color:#f1f5f9;font-size:13px;">{stripped}</div>'
            )
        elif stripped.startswith("▶"):
            # Verdict bullet — highlighted row
            html_lines.append(
                f'<div style="margin:8px 0;padding:10px 14px;background:#0f2a1a;'
                f'border:1px solid #166534;border-radius:6px;line-height:1.6;">{stripped}</div>'
            )
        elif stripped.startswith("-"):
            html_lines.append(
                f'<div style="margin:5px 0 5px 12px;color:#94a3b8;line-height:1.6;">'
                f'• {stripped[1:].strip()}</div>'
            )
        elif stripped:
            color = "#e2e8f0" if in_verdict else "#94a3b8"
            html_lines.append(f'<div style="margin:5px 0;line-height:1.7;color:{color};">{stripped}</div>')
        else:
            html_lines.append('<div style="height:5px;"></div>')
    return "\n".join(html_lines)


def _portfolio_section(advice_text):
    if not advice_text:
        return ""

    # Color theme per budget tier
    TIER_THEME = {
        "100-300": ("#166534", "#4ade80", "#052e16"),   # green — modest
        "300-500": ("#1e3a8a", "#60a5fa", "#0c1a3a"),   # blue  — intermediate
        "500-1000": ("#7c2d12", "#fb923c", "#2c0f06"),  # orange — active
    }

    lines = advice_text.split("\n")
    html_lines = []
    current_theme = ("#1e293b", "#94a3b8", "#0f172a")  # default

    for line in lines:
        stripped = line.strip()
        if not stripped:
            html_lines.append('<div style="height:5px;"></div>')
            continue

        # Detect tier headers
        for key, theme in TIER_THEME.items():
            if key in stripped and stripped.startswith("**"):
                current_theme = theme
                break

        rendered = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", stripped)
        border_col, text_col, bg_col = current_theme

        if stripped.startswith("**BUDGET"):
            html_lines.append(
                f'<div style="margin-top:18px;padding:11px 16px;'
                f'background:{bg_col};border:1px solid {border_col}88;'
                f'border-left:3px solid {text_col};border-radius:6px;'
                f'font-size:13px;font-weight:700;color:{text_col};">'
                f'💶 {rendered.replace("**", "")}</div>'
            )
        elif stripped.lower().startswith("stratégie"):
            html_lines.append(
                f'<div style="margin:6px 2px 6px 16px;color:#64748b;'
                f'font-size:11px;font-style:italic;">{rendered}</div>'
            )
        elif stripped.startswith("-"):
            html_lines.append(
                f'<div style="margin:4px 0;padding:8px 12px 8px 14px;'
                f'background:#0f172a;border-left:2px solid {border_col}77;'
                f'border-radius:0 4px 4px 0;line-height:1.5;'
                f'color:#e2e8f0;font-size:12px;">• {rendered[1:].strip()}</div>'
            )
        else:
            html_lines.append(
                f'<div style="margin:4px 0;color:#64748b;font-size:12px;">{rendered}</div>'
            )

    return f"""
    <div style="background:#0a0f1e;border:1px solid #1e293b;border-radius:12px;padding:20px;margin-bottom:16px;">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;padding-bottom:12px;border-bottom:1px solid #1e293b;">
        <div style="font-size:15px;font-weight:700;color:#f1f5f9;">Plan d'Investissement Mensuel</div>
        <div style="background:#1e293b;color:#64748b;font-size:10px;font-weight:700;padding:2px 8px;border-radius:4px;text-transform:uppercase;letter-spacing:0.5px;">3 budgets</div>
      </div>
      {"".join(html_lines)}
    </div>"""


# Per-scope visual theme: (accent_color, header_gradient_start, badge_label)
_SCOPE_THEME = {
    "US":     ("#3b82f6", "#0f2744", "🇺🇸 Marchés US"),
    "Europe": ("#8b5cf6", "#1a0f2e", "🇪🇺 Marchés Europe"),
    "Crypto": ("#f59e0b", "#1a1100", "₿ Marchés Crypto"),
}


def generate_html_report(market_data, crypto_data, news, ai_analysis,
                         alerts=None, top_picks=None, scope="US", portfolio_advice=None,
                         eur_usd=None):
    date_str = datetime.now().strftime("%A %d %B %Y — %H:%M")
    accent, grad_start, badge = _SCOPE_THEME.get(scope, _SCOPE_THEME["US"])

    # Currency badge shown only on US reports
    eur_badge = ""
    if scope == "US" and eur_usd:
        usd_per_eur = round(1 / eur_usd, 4)
        eur_badge = (
            f'<div style="margin-top:10px;display:inline-block;'
            f'background:#0f2744;border:1px solid {accent}44;border-radius:6px;'
            f'padding:4px 12px;font-size:11px;color:{accent};font-weight:600;">'
            f'💱 1 € = {usd_per_eur} $ &nbsp;|&nbsp; EUR/USD {eur_usd}</div>'
        )

    alerts_html    = _alerts_section(alerts or [])
    top_picks_html = _top_picks_section(top_picks or [])
    portfolio_html = _portfolio_section(portfolio_advice or "")
    markets_html   = "".join(_market_table(cat, items) for cat, items in market_data.items())
    crypto_html    = _crypto_table(crypto_data) if crypto_data else ""

    news_items = ""
    for article in news[:12]:
        news_items += f"""
        <div style="padding:10px 0;border-bottom:1px solid #1e293b;">
          <span style="color:{accent};font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;">{article['source']}</span>
          <a href="{article['link']}" style="display:block;color:#e2e8f0;text-decoration:none;font-size:13px;margin:3px 0 0 0;font-weight:500;line-height:1.4;">{article['title']}</a>
        </div>"""

    ai_html = _ai_to_html(ai_analysis, accent=accent)

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{badge} — {date_str}</title>
</head>
<body style="margin:0;padding:0;background:#020617;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,sans-serif;color:#e2e8f0;">
  <div style="max-width:680px;margin:0 auto;padding:20px 16px;">

    <!-- Header -->
    <div style="text-align:center;padding:28px 20px;background:linear-gradient(135deg,{grad_start} 0%,#0f172a 100%);border-radius:12px;border:1px solid {accent}33;margin-bottom:20px;">
      <div style="font-size:10px;color:{accent};text-transform:uppercase;letter-spacing:2px;margin-bottom:10px;">Daily Market Intelligence</div>
      <div style="font-size:26px;font-weight:800;color:#f1f5f9;margin-bottom:6px;">{badge}</div>
      <div style="color:#475569;font-size:13px;">{date_str}</div>
      {eur_badge}
    </div>

    <!-- Alertes (si présentes) -->
    {alerts_html}

    <!-- ★ Analyse IA en premier — section la plus importante -->
    <div style="background:#0a0f1e;border:1px solid {accent}55;border-left:3px solid {accent};border-radius:12px;padding:22px;margin-bottom:16px;">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid #1e293b;">
        <div style="font-size:15px;font-weight:700;color:#f1f5f9;">Analyse &amp; Recommandations IA</div>
        <div style="background:{accent}22;color:{accent};font-size:10px;font-weight:700;padding:2px 8px;border-radius:4px;text-transform:uppercase;letter-spacing:0.5px;">Llama 3.3</div>
      </div>
      <div style="font-size:13px;line-height:1.75;">{ai_html}</div>
    </div>

    <!-- Top 5 Momentum -->
    {top_picks_html}

    <!-- Plan d'investissement mensuel -->
    {portfolio_html}

    <!-- Données de marché -->
    <div style="background:#0a0f1e;border:1px solid #1e293b;border-radius:12px;padding:20px;margin-bottom:16px;">
      <div style="font-size:15px;font-weight:700;color:#f1f5f9;margin-bottom:16px;">Données de Marché</div>
      {markets_html}
      {crypto_html}
    </div>

    <!-- News -->
    <div style="background:#0a0f1e;border:1px solid #1e293b;border-radius:12px;padding:20px;margin-bottom:16px;">
      <div style="font-size:15px;font-weight:700;color:#f1f5f9;margin-bottom:14px;">Actualités</div>
      {news_items}
    </div>

    <!-- Footer -->
    <div style="text-align:center;color:#1e293b;font-size:11px;padding:12px 0;">
      Rapport généré automatiquement • À titre informatif uniquement • Pas un conseil financier
    </div>

  </div>
</body>
</html>"""
