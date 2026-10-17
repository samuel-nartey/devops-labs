import json
import os
import re
import time
import traceback
import uuid
from decimal import Decimal
from urllib.parse import urlparse

import boto3
from boto3.dynamodb.conditions import Key

table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])
RETENTION_DAYS = int(os.environ.get("RETENTION_DAYS", "7"))
PK = "WALL"

# Only these three sites are accepted. Each entry: allowed hosts, safe base link,
# required path prefix, and the rule a username must follow.
SOCIALS = {
    "linkedin": ({"linkedin.com", "www.linkedin.com"}, "https://www.linkedin.com/in/", "/in/", r"[A-Za-z0-9_%-]{3,100}"),
    "x": ({"x.com", "www.x.com", "twitter.com", "www.twitter.com"}, "https://x.com/", "/", r"[A-Za-z0-9_]{1,15}"),
    "github": ({"github.com", "www.github.com"}, "https://github.com/", "/", r"[A-Za-z0-9-]{1,39}"),
}
LABELS = {"linkedin": "LinkedIn", "x": "X", "github": "GitHub"}


def resp(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json", "Cache-Control": "no-store"},
        "body": json.dumps(body, default=lambda o: int(o) if isinstance(o, Decimal) else str(o)),
    }


def log(level, msg, **fields):
    print(json.dumps({"level": level, "msg": msg, **fields}))


def clean_social(key, value):
    """Accept a username or a profile link for one known site. Always rebuild a clean https link."""
    value = str(value or "").strip()
    if not value:
        return None
    hosts, base, prefix, pattern = SOCIALS[key]
    label = LABELS[key]
    handle = value.lstrip("@")
    explicit = bool(re.match(r"(?i)^https?://", value))
    try:
        parsed = urlparse(value if explicit else "https://" + value)
        host = (parsed.hostname or "").lower()
    except ValueError:
        raise ValueError(f"{label} must be a profile link or username on that site")
    if explicit or host in hosts:
        path = parsed.path.rstrip("/")
        if host not in hosts or not path.startswith(prefix):
            raise ValueError(f"{label} must be a profile link or username on that site")
        handle = path[len(prefix):]
    if not re.fullmatch(pattern, handle):
        raise ValueError(f"{label} username looks invalid")
    return base + handle


def parse_message(event):
    raw = event.get("body") or "{}"
    if len(raw) > 4096:
        raise ValueError("Request too large")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError("Body must be valid JSON")
    if not isinstance(data, dict):
        raise ValueError("Body must be a JSON object")
    name = str(data.get("name", "")).strip()[:40]
    country = str(data.get("country", "")).strip()[:40]
    message = str(data.get("message", "")).strip()[:200]
    if not name or not message:
        raise ValueError("name and message are required")
    raw_socials = data.get("socials") or {}
    if not isinstance(raw_socials, dict):
        raise ValueError("socials must be an object")
    socials = {}
    for key in SOCIALS:
        link = clean_social(key, raw_socials.get(key))
        if link:
            socials[key] = link
    return name, country, message, socials


def list_messages():
    result = table.query(
        KeyConditionExpression=Key("pk").eq(PK),
        ScanIndexForward=False,
        Limit=50,
    )
    return resp(200, [
        {
            "name": i["name"],
            "country": i.get("country", ""),
            "message": i["message"],
            "createdAt": int(i["createdAt"]),
            "socials": i.get("socials", {}),
        }
        for i in result["Items"]
    ])


def create_message(event):
    name, country, message, socials = parse_message(event)
    now_ms = int(time.time() * 1000)
    item = {
        "pk": PK,
        "sk": f"{now_ms:013d}#{uuid.uuid4().hex[:8]}",
        "name": name,
        "country": country,
        "message": message,
        "createdAt": now_ms,
        "expiresAt": now_ms // 1000 + RETENTION_DAYS * 86400,
    }
    if socials:
        item["socials"] = socials
    table.put_item(Item=item)
    log("info", "message_saved", name=name, hasSocials=sorted(socials))
    return resp(201, {"ok": True})


def handler(event, context):
    method = event.get("requestContext", {}).get("http", {}).get("method", "")
    try:
        if method == "GET":
            return list_messages()
        if method == "POST":
            return create_message(event)
        return resp(405, {"error": "Method not allowed"})
    except ValueError as e:
        return resp(400, {"error": str(e)})
    except Exception:
        log("error", "unhandled", trace=traceback.format_exc())
        return resp(500, {"error": "Internal error"})
