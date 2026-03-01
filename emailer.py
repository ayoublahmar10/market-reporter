import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

GMAIL_USER         = os.environ.get("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
API_BASE_URL       = os.environ.get("API_BASE_URL", "")  # API Gateway base URL


def send_report(html_content, recipient_email, subject=None, greeting=None):
    date_str = datetime.now().strftime("%d/%m/%Y")
    if subject is None:
        subject = f"Market Report — {date_str}"

    # Inject personalized greeting at the top of the HTML body
    if greeting:
        html_content = html_content.replace(
            "<body>",
            f"<body><p style='font-family:sans-serif;padding:12px 24px'>{greeting}</p>",
            1,
        )

    # Inject unsubscribe footer before closing </body>
    if API_BASE_URL:
        import urllib.parse
        unsubscribe_url = f"{API_BASE_URL}/unsubscribe?email={urllib.parse.quote(recipient_email)}"
        unsubscribe_footer = (
            f"<div style='font-family:sans-serif;text-align:center;padding:24px;"
            f"color:#94a3b8;font-size:0.8rem'>"
            f"You're receiving this because you subscribed to Market Reporter.<br>"
            f"<a href='{unsubscribe_url}' style='color:#60a5fa'>Unsubscribe</a>"
            f"</div>"
        )
        html_content = html_content.replace("</body>", f"{unsubscribe_footer}</body>", 1)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"Market Reporter <{GMAIL_USER}>"
    msg["To"]      = recipient_email
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, recipient_email, msg.as_string())

    print(f"  Email sent to {recipient_email}")
