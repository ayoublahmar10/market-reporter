"""
DynamoDB subscriber management.
Table: market-reporter-subscribers
  PK: email (String)
  Attributes: name, markets (List), language, tier, active (Boolean)
"""
import boto3
import os

TABLE_NAME = os.environ.get("SUBSCRIBERS_TABLE", "market-reporter-subscribers")


def _table():
    dynamodb = boto3.resource("dynamodb")
    return dynamodb.Table(TABLE_NAME)


def get_active_subscribers():
    """Return all active subscribers from DynamoDB."""
    response = _table().scan(
        FilterExpression="active = :a",
        ExpressionAttributeValues={":a": True},
    )
    return response.get("Items", [])


def get_subscriber(email):
    """Return a subscriber by email, or None if not found."""
    response = _table().get_item(Key={"email": email})
    return response.get("Item")


def add_subscriber(email, name="", markets=None, language="en"):
    """Add or update a subscriber."""
    if markets is None:
        markets = ["US", "Europe", "Crypto"]
    _table().put_item(Item={
        "email":    email,
        "name":     name,
        "markets":  markets,
        "language": language,
        "tier":     "free",
        "active":   True,
    })


def remove_subscriber(email):
    """Deactivate a subscriber (soft delete)."""
    _table().update_item(
        Key={"email": email},
        UpdateExpression="SET active = :a",
        ExpressionAttributeValues={":a": False},
    )
