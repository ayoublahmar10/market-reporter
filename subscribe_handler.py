"""
AWS Lambda handler for the subscription API.
API Gateway POST /subscribe → this function → DynamoDB + confirmation email

Expected body: { "email": "...", "name": "...", "markets": ["US", "Crypto"] }
"""
import json
import os
import smtplib
import urllib.parse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from subscribers import add_subscriber, get_subscriber

ALLOWED_MARKETS = {"US", "Europe", "Crypto"}

MARKET_LABELS = {
    "US":     "🇺🇸 US Markets",
    "Europe": "🇪🇺 European Markets",
    "Crypto": "₿ Crypto",
}

FREQUENCY_LABELS = {
    "daily":  "📅 Daily",
    "weekly": "📆 Weekly (Monday)",
}

TIME_LABELS = {
    "morning":   "🌅 8h Morning",
    "afternoon": "📉 16h After-market",
}

LANGUAGE_LABELS = {
    "en": "English",
    "fr": "Français",
}

PROFILE_LABELS = {
    "beginner":     "🌱 Beginner",
    "intermediate": "📊 Intermediate",
    "expert":       "🎯 Expert",
}

CORS_HEADERS = {
    "Access-Control-Allow-Origin":  "*",
    "Access-Control-Allow-Methods": "POST,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Content-Type": "application/json",
}


def handler(event, context):
    # Handle CORS preflight request from the browser
    if event.get("httpMethod") == "OPTIONS":
        return {"statusCode": 200, "headers": CORS_HEADERS, "body": ""}

    try:
        body        = json.loads(event.get("body") or "{}")
        email       = body.get("email", "").strip().lower()
        name        = body.get("name", "").strip()
        markets     = body.get("markets", ["US", "Europe", "Crypto"])
        language    = body.get("language", "en")    if body.get("language")    in ("en", "fr")                              else "en"
        frequency   = body.get("frequency", "daily") if body.get("frequency")  in ("daily", "weekly")                       else "daily"
        report_time = body.get("report_time", "morning") if body.get("report_time") in ("morning", "afternoon")             else "morning"
        profile     = body.get("profile", "beginner") if body.get("profile")   in ("beginner", "intermediate", "expert")    else "beginner"

        if not email or "@" not in email:
            return _error(400, "Invalid email address")

        markets = [m for m in markets if m in ALLOWED_MARKETS]
        if not markets:
            return _error(400, "Select at least one market")

        # Check if already subscribed
        existing = get_subscriber(email)
        if existing and existing.get("active"):
            same_prefs = (
                sorted(existing.get("markets", [])) == sorted(markets)
                and existing.get("frequency", "daily")   == frequency
                and existing.get("report_time", "morning") == report_time
                and existing.get("language", "en")       == language
                and existing.get("profile", "beginner")  == profile
            )
            if same_prefs:
                return {
                    "statusCode": 409,
                    "headers": CORS_HEADERS,
                    "body": json.dumps({"error": "This email is already subscribed to the same markets"}),
                }
            # Any preference changed → update
            add_subscriber(email=email, name=name, markets=markets,
                           language=language, frequency=frequency,
                           report_time=report_time, profile=profile)
            print(f"Updated subscriber: {email} | markets: {markets}")
            _send_update_confirmation(email=email, name=name, markets=markets,
                                      frequency=frequency, report_time=report_time,
                                      language=language, profile=profile)
            return {
                "statusCode": 200,
                "headers": CORS_HEADERS,
                "body": json.dumps({"message": "Preferences updated successfully"}),
            }

        add_subscriber(email=email, name=name, markets=markets,
                       language=language, frequency=frequency,
                       report_time=report_time, profile=profile)
        print(f"New subscriber: {email} | markets: {markets} | lang: {language} | freq: {frequency} | time: {report_time} | profile: {profile}")

        _send_confirmation(email=email, name=name, markets=markets,
                           frequency=frequency, report_time=report_time,
                           language=language, profile=profile)

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({"message": "Subscribed successfully"}),
        }

    except Exception as e:
        print(f"Error: {e}")
        return _error(500, "Internal server error")


def _unsubscribe_link(email):
    api_url = os.environ.get("API_BASE_URL", "")
    if not api_url:
        return ""
    url = f"{api_url}/unsubscribe?email={urllib.parse.quote(email)}"
    return f'<a href="{url}" style="color:#60a5fa">Unsubscribe</a>'


def _send_confirmation(email, name, markets,
                       frequency="daily", report_time="morning",
                       language="en", profile="beginner"):
    gmail_user     = os.environ.get("GMAIL_USER", "")
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD", "")

    if not gmail_user or not gmail_password:
        print("  Gmail not configured — skipping confirmation email")
        return

    greeting    = f"Hi {name}," if name else "Hi,"
    market_list = "".join(
        f"<li style='padding:4px 0'>{MARKET_LABELS.get(m, m)}</li>"
        for m in markets
    )

    html = f"""
    <div style="font-family:sans-serif;max-width:480px;margin:0 auto;padding:32px 24px;color:#1a1d27;background:#f8fafc">
      <div style="background:white;border-radius:12px;padding:32px;box-shadow:0 2px 12px rgba(0,0,0,0.08)">
        <div style="font-size:2rem;margin-bottom:12px">📈</div>
        <h1 style="font-size:1.4rem;margin:0 0 8px;color:#1e293b">You're subscribed!</h1>
        <p style="color:#64748b;margin:0 0 24px">{greeting} Welcome to Market Reporter.</p>

        <p style="color:#374151;margin:0 0 8px">Markets:</p>
        <ul style="color:#374151;padding-left:20px;margin:0 0 20px">
          {market_list}
        </ul>

        <div style="background:#f1f5f9;border-radius:8px;padding:12px 16px;margin-bottom:20px">
          <table style="width:100%;font-size:0.9rem;color:#475569;border-collapse:collapse">
            <tr>
              <td style="padding:4px 0">📅 Frequency</td>
              <td style="padding:4px 0;text-align:right;color:#1e293b"><strong>{FREQUENCY_LABELS.get(frequency, frequency)}</strong></td>
            </tr>
            <tr>
              <td style="padding:4px 0">🕒 Delivery</td>
              <td style="padding:4px 0;text-align:right;color:#1e293b"><strong>{TIME_LABELS.get(report_time, report_time)}</strong></td>
            </tr>
            <tr>
              <td style="padding:4px 0">🌐 Language</td>
              <td style="padding:4px 0;text-align:right;color:#1e293b"><strong>{LANGUAGE_LABELS.get(language, language)}</strong></td>
            </tr>
            <tr>
              <td style="padding:4px 0">👤 Profile</td>
              <td style="padding:4px 0;text-align:right;color:#1e293b"><strong>{PROFILE_LABELS.get(profile, profile)}</strong></td>
            </tr>
          </table>
        </div>

        <p style="color:#64748b;font-size:0.9rem;margin:0">
          Your first report will arrive tomorrow.
        </p>
      </div>
      <p style="color:#94a3b8;font-size:0.8rem;text-align:center;margin-top:16px">
        Market Reporter — Daily financial intelligence<br>
        {_unsubscribe_link(email)}
      </p>
    </div>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Welcome to Market Reporter 📈"
    msg["From"]    = f"Market Reporter <{gmail_user}>"
    msg["To"]      = email
    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, email, msg.as_string())

    print(f"  Confirmation email sent to {email}")


def _send_update_confirmation(email, name, markets,
                              frequency="daily", report_time="morning",
                              language="en", profile="beginner"):
    gmail_user     = os.environ.get("GMAIL_USER", "")
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD", "")

    if not gmail_user or not gmail_password:
        print("  Gmail not configured — skipping update email")
        return

    greeting    = f"Hi {name}," if name else "Hi,"
    market_list = "".join(
        f"<li style='padding:4px 0'>{MARKET_LABELS.get(m, m)}</li>"
        for m in markets
    )

    html = f"""
    <div style="font-family:sans-serif;max-width:480px;margin:0 auto;padding:32px 24px;color:#1a1d27;background:#f8fafc">
      <div style="background:white;border-radius:12px;padding:32px;box-shadow:0 2px 12px rgba(0,0,0,0.08)">
        <div style="font-size:2rem;margin-bottom:12px">⚙️</div>
        <h1 style="font-size:1.4rem;margin:0 0 8px;color:#1e293b">Preferences updated!</h1>
        <p style="color:#64748b;margin:0 0 24px">{greeting} Your Market Reporter preferences have been updated.</p>

        <p style="color:#374151;margin:0 0 8px">Markets:</p>
        <ul style="color:#374151;padding-left:20px;margin:0 0 20px">
          {market_list}
        </ul>

        <div style="background:#f1f5f9;border-radius:8px;padding:12px 16px;margin-bottom:20px">
          <table style="width:100%;font-size:0.9rem;color:#475569;border-collapse:collapse">
            <tr>
              <td style="padding:4px 0">📅 Frequency</td>
              <td style="padding:4px 0;text-align:right;color:#1e293b"><strong>{FREQUENCY_LABELS.get(frequency, frequency)}</strong></td>
            </tr>
            <tr>
              <td style="padding:4px 0">🕒 Delivery</td>
              <td style="padding:4px 0;text-align:right;color:#1e293b"><strong>{TIME_LABELS.get(report_time, report_time)}</strong></td>
            </tr>
            <tr>
              <td style="padding:4px 0">🌐 Language</td>
              <td style="padding:4px 0;text-align:right;color:#1e293b"><strong>{LANGUAGE_LABELS.get(language, language)}</strong></td>
            </tr>
            <tr>
              <td style="padding:4px 0">👤 Profile</td>
              <td style="padding:4px 0;text-align:right;color:#1e293b"><strong>{PROFILE_LABELS.get(profile, profile)}</strong></td>
            </tr>
          </table>
        </div>

        <p style="color:#64748b;font-size:0.9rem;margin:0">
          Changes take effect from tomorrow's report.
        </p>
      </div>
      <p style="color:#94a3b8;font-size:0.8rem;text-align:center;margin-top:16px">
        Market Reporter — Daily financial intelligence<br>
        {_unsubscribe_link(email)}
      </p>
    </div>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Preferences updated — Market Reporter ⚙️"
    msg["From"]    = f"Market Reporter <{gmail_user}>"
    msg["To"]      = email
    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, email, msg.as_string())

    print(f"  Update confirmation email sent to {email}")


def _error(status, message):
    return {
        "statusCode": status,
        "headers": CORS_HEADERS,
        "body": json.dumps({"error": message}),
    }
