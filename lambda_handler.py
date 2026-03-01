"""
AWS Lambda entry point.
EventBridge Scheduler calls handler(event, context) on each cron schedule.

EventBridge payload examples:
  Morning schedule (8h):    {"time_slot": "morning"}
  Afternoon schedule (16h): {"time_slot": "afternoon"}
"""
from main import run


def handler(event, context):
    # EventBridge Scheduler passes the payload directly as the event
    time_slot = event.get("time_slot", "morning")
    run(time_slot=time_slot)
    return {"statusCode": 200, "body": f"Reports sent for slot: {time_slot}"}
