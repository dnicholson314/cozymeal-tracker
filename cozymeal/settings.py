import pytz

from environs import env
from pathlib import Path

env.read_env()

API_TOKEN = env.str('API_TOKEN', default='')

EMAIL_PASSWORD = env.str("EMAIL_PASSWORD")
SENDER_EMAIL = env.str("EMAIL_USERNAME")
RECEIVER_EMAIL = env.str("RECEIVER_EMAIL")

LAST_CHECKED_DIR = env.path("LAST_CHECKED_DIR", default=Path("/data"))
LAST_CHECKED_DIR.mkdir(parents=True, exist_ok=True)

LAST_CHECKED_FILENAME = LAST_CHECKED_DIR / 'last_checked_time.json'
LAST_CHECKED_KEY = "last_checked_time"

DEFAULT_TZ = pytz.timezone('America/Los_Angeles')
