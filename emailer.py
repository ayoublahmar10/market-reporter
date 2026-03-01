import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

GMAIL_USER         = os.environ.get("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")


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

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"Market Reporter <{GMAIL_USER}>"
    msg["To"]      = recipient_email
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, recipient_email, msg.as_string())

    print(f"  Email sent to {recipient_email}")
