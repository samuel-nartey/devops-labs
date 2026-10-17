import base64
import json
import os
import re
import time
import traceback
import uuid
from decimal import Decimal
from urllib.parse import urlparse

import boto3
from boto3.dynamodb.conditions import Attr, Key

db = boto3.resource("dynamodb")
table = db.Table(os.environ["TABLE_NAME"])
client = db.meta.client
TABLE_NAME = os.environ["TABLE_NAME"]
EVENT_ID = os.environ.get("EVENT_ID", "workshop")
RETENTION_DAYS = int(os.environ.get("RETENTION_DAYS", "30"))
PK = f"EVENT#{EVENT_ID}"
STATS_KEY = {"pk": "STATS", "sk": EVENT_ID}


def resp(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json", "Cache-Control": "no-store"},
        "body": json.dumps(body, default=lambda o: int(o) if isinstance(o, Decimal) else str(o)),
    }


def log(level, msg, **fields):
    print(json.dumps({"level": level, "msg": msg, **fields}))


def claims(event):
    return event["requestContext"].get("authorizer", {}).get("jwt", {}).get("claims", {})


def is_admin(c):
    groups = str(c.get("cognito:groups", "")).strip("[]").replace(",", " ").split()
    return "admin" in groups


SOCIALS = {
    "linkedin": ({"linkedin.com", "www.linkedin.com"}, "https://www.linkedin.com/in/", "/in/", r"[A-Za-z0-9_%-]{3,100}"),
    "x": ({"x.com", "www.x.com", "twitter.com", "www.twitter.com"}, "https://x.com/", "/", r"[A-Za-z0-9_]{1,15}"),
    "github": ({"github.com", "www.github.com"}, "https://github.com/", "/", r"[A-Za-z0-9-]{1,39}"),
}


def clean_social(key, value):
    """Accept a username or a profile URL for one known site. Always rebuild a safe canonical link."""
    value = str(value or "").strip()
    if not value:
        return None
    hosts, base, prefix, pattern = SOCIALS[key]
    handle = value.lstrip("@")
    if value.lower().startswith(("http://", "https://")):
        parsed = urlparse(value)
        path = parsed.path.rstrip("/")
        if (parsed.hostname or "").lower() not in hosts or not path.startswith(prefix):
            raise ValueError(f"{key} must be a profile link or username on that site")
        handle = path[len(prefix):]
    if not re.fullmatch(pattern, handle):
        raise ValueError(f"{key} username looks invalid")
    return base + handle


def parse_review(event):
    raw = event.get("body") or "{}"
    if len(raw) > 4096:
        raise ValueError("Request too large")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError("Body must be valid JSON")
    name = str(data.get("name", "")).strip()[:40]
    country = str(data.get("country", "")).strip()[:40]
    message = str(data.get("message", "")).strip()[:200]
    try:
        rating = int(data.get("rating"))
    except (TypeError, ValueError):
        raise ValueError("rating must be a whole number from 1 to 5")
    if not name or not message:
        raise ValueError("name and message are required")
    if rating < 1 or rating > 5:
        raise ValueError("rating must be a whole number from 1 to 5")
    raw_socials = data.get("socials") or {}
    if not isinstance(raw_socials, dict):
        raise ValueError("socials must be an object")
    socials = {}
    for key in SOCIALS:
        link = clean_social(key, raw_socials.get(key))
        if link:
            socials[key] = link
    return name, country, message, rating, socials


def public(item):
    return {
        "id": item["sk"],
        "ownerId": item["userId"],
        "name": item["name"],
        "country": item.get("country", ""),
        "message": item["message"],
        "rating": int(item["rating"]),
        "createdAt": int(item["createdAt"]),
        "socials": item.get("socials", {}),
        "edited": "updatedAt" in item,
    }


def stats_update(count_delta, rating_delta):
    return {
        "Update": {
            "TableName": TABLE_NAME,
            "Key": STATS_KEY,
            "UpdateExpression": "ADD reviewCount :c, ratingSum :r",
            "ExpressionAttributeValues": {":c": count_delta, ":r": rating_delta},
        }
    }


def get_review(review_id):
    item = table.get_item(Key={"pk": PK, "sk": review_id}).get("Item")
    if not item:
        raise LookupError("Review not found")
    return item


def list_reviews(event):
    params = event.get("queryStringParameters") or {}
    try:
        limit = max(1, min(int(params.get("limit", 20)), 50))
    except ValueError:
        raise ValueError("limit must be a number")
    query = {
        "KeyConditionExpression": Key("pk").eq(PK),
        "FilterExpression": Attr("expiresAt").gt(int(time.time())),
        "ScanIndexForward": False,
        "Limit": limit,
    }
    token = params.get("nextToken")
    if token:
        try:
            start = json.loads(base64.urlsafe_b64decode(token.encode()))
        except Exception:
            raise ValueError("Invalid nextToken")
        if start.get("pk") != PK:
            raise ValueError("Invalid nextToken")
        query["ExclusiveStartKey"] = {"pk": start["pk"], "sk": str(start["sk"])}
    result = table.query(**query)
    next_token = None
    if "LastEvaluatedKey" in result:
        key = {"pk": result["LastEvaluatedKey"]["pk"], "sk": result["LastEvaluatedKey"]["sk"]}
        next_token = base64.urlsafe_b64encode(json.dumps(key).encode()).decode()
    stats = table.get_item(Key=STATS_KEY).get("Item", {})
    count = int(stats.get("reviewCount", 0))
    total = int(stats.get("ratingSum", 0))
    return resp(200, {
        "items": [public(i) for i in result["Items"]],
        "nextToken": next_token,
        "stats": {"count": count, "average": round(total / count, 2) if count else 0},
    })


def create_review(event):
    c = claims(event)
    name, country, message, rating, socials = parse_review(event)
    now_ms = int(time.time() * 1000)
    review_id = f"{now_ms:013d}#{uuid.uuid4().hex[:8]}"
    item = {
        "pk": PK, "sk": review_id, "userId": c["sub"], "name": name, "country": country,
        "message": message, "rating": rating, "socials": socials, "createdAt": now_ms,
        "expiresAt": now_ms // 1000 + RETENTION_DAYS * 86400,
    }
    client.transact_write_items(TransactItems=[
        {"Put": {"TableName": TABLE_NAME, "Item": item, "ConditionExpression": "attribute_not_exists(pk)"}},
        stats_update(1, rating),
    ])
    log("info", "review_created", reviewId=review_id, userId=c["sub"])
    return resp(201, public(item))


def update_review(event):
    c = claims(event)
    review_id = event["pathParameters"]["id"]
    item = get_review(review_id)
    if item["userId"] != c["sub"]:
        raise PermissionError("You can only edit your own review")
    name, country, message, rating, socials = parse_review(event)
    now_ms = int(time.time() * 1000)
    client.transact_write_items(TransactItems=[
        {"Update": {
            "TableName": TABLE_NAME,
            "Key": {"pk": PK, "sk": review_id},
            "UpdateExpression": "SET #n = :n, country = :c, message = :m, rating = :r, socials = :s, updatedAt = :u",
            "ConditionExpression": "attribute_exists(pk) AND userId = :uid",
            "ExpressionAttributeNames": {"#n": "name"},
            "ExpressionAttributeValues": {
                ":n": name, ":c": country, ":m": message, ":r": rating, ":s": socials, ":u": now_ms, ":uid": c["sub"],
            },
        }},
        stats_update(0, rating - int(item["rating"])),
    ])
    log("info", "review_updated", reviewId=review_id, userId=c["sub"])
    item.update(name=name, country=country, message=message, rating=rating, socials=socials, updatedAt=now_ms)
    return resp(200, public(item))


def delete_review(event):
    c = claims(event)
    review_id = event["pathParameters"]["id"]
    item = get_review(review_id)
    admin = is_admin(c)
    if item["userId"] != c["sub"] and not admin:
        raise PermissionError("You can only delete your own review")
    client.transact_write_items(TransactItems=[
        {"Delete": {
            "TableName": TABLE_NAME,
            "Key": {"pk": PK, "sk": review_id},
            "ConditionExpression": "attribute_exists(pk)",
        }},
        stats_update(-1, -int(item["rating"])),
    ])
    log("info", "review_deleted", reviewId=review_id, userId=c["sub"], byAdmin=admin)
    return resp(200, {"ok": True})


ROUTES = {
    "GET /reviews": list_reviews,
    "POST /reviews": create_review,
    "PUT /reviews/{id}": update_review,
    "DELETE /reviews/{id}": delete_review,
}


def handler(event, context):
    fn = ROUTES.get(event.get("routeKey"))
    if not fn:
        return resp(404, {"error": "Not found"})
    try:
        return fn(event)
    except ValueError as e:
        return resp(400, {"error": str(e)})
    except PermissionError as e:
        return resp(403, {"error": str(e)})
    except LookupError as e:
        return resp(404, {"error": str(e)})
    except Exception:
        log("error", "unhandled", trace=traceback.format_exc())
        return resp(500, {"error": "Internal error"})
