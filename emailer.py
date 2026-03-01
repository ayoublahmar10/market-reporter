import os
import boto3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

SES_SENDER = os.environ.get("SES_SENDER", "")


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
    msg["From"]    = f"Market Reporter <{SES_SENDER}>"
    msg["To"]      = recipient_email
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    client = boto3.client("ses")
    client.send_raw_email(
        Source=SES_SENDER,
        Destinations=[recipient_email],
        RawMessage={"Data": msg.as_string()},
    )

    print(f"  Email sent to {recipient_email}")
