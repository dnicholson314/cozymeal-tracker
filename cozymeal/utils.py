import json

from cozymeal import settings
from datetime import datetime as dt, timedelta as tdel
from flask import Request
from json.decoder import JSONDecodeError

def get_date_a_week_ago(tz = settings.DEFAULT_TZ) -> dt:
    return dt.now(tz) - tdel(days=7)

def get_date_a_week_before(timestamp: dt) -> dt:
    return timestamp - tdel(days=7)

def set_last_checked(timestamp: dt) -> None:
    with open(settings.LAST_CHECKED_FILENAME, 'w') as file:
        json.dump({settings.LAST_CHECKED_KEY: timestamp.isoformat()}, file)

def get_last_checked() -> dt | None:
    try:
        with open(settings.LAST_CHECKED_FILENAME, 'r') as file:
            data = json.load(file)
            return dt.fromisoformat(data[settings.LAST_CHECKED_KEY])
    except (FileNotFoundError, KeyError, JSONDecodeError):
        return None

def verify_token(request: Request) -> bool:
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return False

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return False

    token = parts[1]
    expected_token = settings.API_TOKEN

    if not expected_token:
        # If no token is configured, default to deny
        return False

    return token == expected_token
