"""Disk I/O helpers for JSON files and folders."""

from pathlib import Path
from config import JSON_STORAGE_DIR
import logging

logger = logging.getLogger(__name__)


def create_folder_on_disk(folder_name: str) -> Path:
    path = JSON_STORAGE_DIR / folder_name
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_json_to_disk(folder_name: str, json_number: int, content: bytes) -> Path:
    folder_path = JSON_STORAGE_DIR / folder_name
    folder_path.mkdir(parents=True, exist_ok=True)
    file_path = folder_path / f"json_{json_number}.json"
    file_path.write_bytes(content)
    return file_path


def get_json_path(folder_name: str, json_number: int) -> Path:
    return JSON_STORAGE_DIR / folder_name / f"json_{json_number}.json"
