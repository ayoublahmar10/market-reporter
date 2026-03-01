"""
AWS Lambda handler for the subscription API.
API Gateway POST /subscribe → this function → DynamoDB

Expected body: { "email": "...", "name": "...", "markets": ["US", "Crypto"] }
"""
import json
from subscribers import add_subscriber

ALLOWED_MARKETS = {"US", "Europe", "Crypto"}

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
        body    = json.loads(event.get("body") or "{}")
        email   = body.get("email", "").strip().lower()
        name    = body.get("name", "").strip()
        markets = body.get("markets", ["US", "Europe", "Crypto"])

        if not email or "@" not in email:
            return _error(400, "Invalid email address")

        markets = [m for m in markets if m in ALLOWED_MARKETS]
        if not markets:
            return _error(400, "Select at least one market")

        add_subscriber(email=email, name=name, markets=markets)
        print(f"New subscriber: {email} | markets: {markets}")

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({"message": "Subscribed successfully"}),
        }

    except Exception as e:
        print(f"Error: {e}")
        return _error(500, "Internal server error")


def _error(status, message):
    return {
        "statusCode": status,
        "headers": CORS_HEADERS,
        "body": json.dumps({"error": message}),
    }
