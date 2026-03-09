"""
Configuration — set BOT_TOKEN and ADMIN_IDS before deploying.
On Render: add BOT_TOKEN as an Environment Variable in the dashboard.
"""

import os
from pathlib import Path

# ── Bot token ─────────────────────────────────────────────────────────────────
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "8699319947:AAEUI0J648CvcotNwQ5lTdBmLqP_2WDE3Kg")

# ── Admin user IDs ────────────────────────────────────────────────────────────
# Get your ID by messaging @userinfobot on Telegram, then replace 123456789.
ADMIN_IDS: list[int] = [
    8403558393,
]

# ── Storage paths ─────────────────────────────────────────────────────────────
BASE_DIR         = Path(__file__).parent
JSON_STORAGE_DIR = BASE_DIR / "json_storage"
DATABASE_PATH    = BASE_DIR / "json_manager.db"
LOG_FILE         = BASE_DIR / "bot.log"

JSON_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# ── Limits ────────────────────────────────────────────────────────────────────
UNUSED_DISPLAY_LIMIT: int = 50
MAX_JSON_FILE_SIZE:   int = 5 * 1024 * 1024   # 5 MB
