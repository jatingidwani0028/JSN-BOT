"""Async SQLite connection and table initialisation."""

import aiosqlite
import logging
from config import DATABASE_PATH

logger = logging.getLogger(__name__)
_DB = str(DATABASE_PATH)


async def get_db() -> aiosqlite.Connection:
    conn = await aiosqlite.connect(_DB)
    conn.row_factory = aiosqlite.Row
    await conn.execute("PRAGMA journal_mode=WAL")
    await conn.execute("PRAGMA synchronous=NORMAL")
    await conn.execute("PRAGMA cache_size=-64000")
    await conn.execute("PRAGMA foreign_keys=ON")
    return conn


async def init_db() -> None:
    logger.info("Initialising database at %s", _DB)
    async with await get_db() as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS folders (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                folder_name TEXT    NOT NULL UNIQUE COLLATE NOCASE,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS json_files (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                folder_id   INTEGER NOT NULL REFERENCES folders(id) ON DELETE CASCADE,
                json_number INTEGER NOT NULL,
                file_path   TEXT    NOT NULL,
                status      TEXT    NOT NULL DEFAULT 'UNUSED'
                                    CHECK(status IN ('USED','UNUSED')),
                created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
                UNIQUE(folder_id, json_number)
            )
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_json_folder_number
            ON json_files(folder_id, json_number)
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_json_status
            ON json_files(folder_id, status)
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_folders_name
            ON folders(folder_name)
        """)
        await db.commit()
    logger.info("Database ready.")
