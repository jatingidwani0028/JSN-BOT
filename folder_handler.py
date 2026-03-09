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
        await message.answer("⛔ You are not authorized to create folders\\.", parse_mode="MarkdownV2")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "⚠️ Usage: `/create\\_folder <folder\\_name>`\nExample: `/create\\_folder my\\_data`",
            parse_mode="MarkdownV2",
        )
        return

    folder_name = parts[1].strip()
    success, msg = await create_folder(folder_name)
    await message.answer(msg, parse_mode="MarkdownV2")
