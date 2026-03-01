"""
AWS Lambda entry point.
EventBridge calls handler(event, context) on the configured cron schedule.
"""
from main import run


def handler(event, context):
    run()
    return {"statusCode": 200, "body": "Reports sent successfully"}
