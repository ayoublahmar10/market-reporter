import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from config import GMAIL_USER, GMAIL_APP_PASSWORD, EMAIL_TO


def send_report(html_content, subject=None):
    date_str = datetime.now().strftime("%d/%m/%Y")
    if subject is None:
        subject = f"Market Report — {date_str}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Market Reporter <{GMAIL_USER}>"
    msg["To"] = EMAIL_TO

    msg.attach(MIMEText(html_content, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, EMAIL_TO, msg.as_string())

    print(f"  Email sent to {EMAIL_TO}")
