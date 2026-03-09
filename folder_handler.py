"""Admin /create_folder command."""

import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from config import ADMIN_IDS
from folder_service import create_folder

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("create_folder"))
async def cmd_create_folder(message: Message) -> None:
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ You are not authorized to create folders.")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "⚠️ Usage: /create_folder folder_name\nExample: /create_folder my_data"
        )
        return

    folder_name = parts[1].strip()
    success, msg = await create_folder(folder_name)
    # Strip markdown from service layer — send plain
    clean_msg = msg.replace("*", "").replace("\\", "")
    await message.answer(clean_msg)
