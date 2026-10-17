import json
import os
import time
import uuid

import boto3
from boto3.dynamodb.conditions import Key

table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])
RETENTION_DAYS = int(os.environ.get("RETENTION_DAYS", "7"))


def respond(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def handler(event, context):
    method = event["requestContext"]["http"]["method"]
    if method == "POST":
        return create_message(event)
    if method == "GET":
        return list_messages()
    return respond(405, {"error": "Method not allowed"})


def create_message(event):
    try:
        data = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return respond(400, {"error": "Body must be valid JSON"})

    # Validate and trim input. Never trust data coming from a browser.
    name = str(data.get("name", "")).strip()[:40]
    country = str(data.get("country", "")).strip()[:40]
    message = str(data.get("message", "")).strip()[:200]
    if not name or not message:
        return respond(400, {"error": "name and message are required"})

    now_ms = int(time.time() * 1000)
    item = {
        "pk": "WALL",
        "sk": f"{now_ms:013d}#{uuid.uuid4().hex[:8]}",
        "name": name,
        "country": country,
        "message": message,
        "createdAt": now_ms,
        "expiresAt": int(time.time()) + RETENTION_DAYS * 86400,
    }
    table.put_item(Item=item)
    print(json.dumps({"event": "message_saved", "name": name}))
    return respond(201, {"ok": True})


def list_messages():
    result = table.query(
        KeyConditionExpression=Key("pk").eq("WALL"),
        ScanIndexForward=False,  # newest first
        Limit=50,
    )
    items = [
        {
            "name": i["name"],
            "country": i.get("country", ""),
            "message": i["message"],
            "createdAt": int(i["createdAt"]),
        }
        for i in result["Items"]
    ]
    return respond(200, items)
