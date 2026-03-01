"""
AWS Lambda handler for unsubscribe.
API Gateway GET /unsubscribe?email=xxx → deactivates subscriber → returns HTML page
"""
import json
from subscribers import remove_subscriber

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Content-Type": "text/html",
}

HTML_SUCCESS = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Unsubscribed — Market Reporter</title>
  <style>
    body {{ font-family: sans-serif; background: #0f1117; color: #e2e8f0;
           display: flex; align-items: center; justify-content: center;
           min-height: 100vh; margin: 0; }}
    .card {{ background: #1a1d27; border: 1px solid #2d3148; border-radius: 16px;
             padding: 48px 40px; max-width: 420px; text-align: center; }}
    h1 {{ font-size: 1.4rem; margin: 16px 0 8px; color: #f1f5f9; }}
    p  {{ color: #94a3b8; line-height: 1.6; }}
  </style>
</head>
<body>
  <div class="card">
    <div style="font-size:2.5rem">👋</div>
    <h1>You've been unsubscribed</h1>
    <p>Sorry to see you go, <strong>{email}</strong>.<br>
       You won't receive any more emails from Market Reporter.</p>
  </div>
</body>
</html>
"""

HTML_ERROR = """
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"/><title>Error — Market Reporter</title>
<style>
  body {{ font-family:sans-serif; background:#0f1117; color:#e2e8f0;
         display:flex; align-items:center; justify-content:center; min-height:100vh; }}
  .card {{ background:#1a1d27; border:1px solid #2d3148; border-radius:16px;
           padding:48px 40px; max-width:420px; text-align:center; }}
</style></head>
<body><div class="card">
  <div style="font-size:2.5rem">⚠️</div>
  <h1 style="color:#f87171">Something went wrong</h1>
  <p style="color:#94a3b8">Invalid or missing email address.</p>
</div></body></html>
"""


def handler(event, context):
    params = event.get("queryStringParameters") or {}
    email  = (params.get("email") or "").strip().lower()

    if not email or "@" not in email:
        return {"statusCode": 400, "headers": CORS_HEADERS, "body": HTML_ERROR}

    try:
        remove_subscriber(email)
        print(f"Unsubscribed: {email}")
        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": HTML_SUCCESS.format(email=email),
        }
    except Exception as e:
        print(f"Error unsubscribing {email}: {e}")
        return {"statusCode": 500, "headers": CORS_HEADERS, "body": HTML_ERROR}
