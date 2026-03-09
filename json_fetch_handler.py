"""JSON retrieval and status handlers."""

import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile

from json_service import get_json_file, set_json_status, get_next_unused, preview_json
from config import ADMIN_IDS

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("get_json"))
async def cmd_get_json(message: Message) -> None:
    parts = message.text.split()
    if len(parts) != 3:
        await message.answer("⚠️ Usage: /get_json folder_name number\nExample: /get_json folder_1 5")
        return
    folder_name = parts[1].lower()
    try:
        json_number = int(parts[2])
        assert json_number > 0
    except (ValueError, AssertionError):
        await message.answer("❌ JSON number must be a positive integer.")
        return

    path, msg = await get_json_file(folder_name, json_number)
    clean_msg = msg.replace("*", "").replace("\\", "")
    await message.answer(clean_msg)
    if path:
        await message.answer_document(
            FSInputFile(path, filename=f"{folder_name}_json_{json_number}.json"),
            caption=f"📄 JSON #{json_number} from {folder_name}",
        )
        logger.info("User %s downloaded JSON #%d from '%s'", message.from_user.id, json_number, folder_name)


@router.message(Command("next_unused"))
async def cmd_next_unused(message: Message) -> None:
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("⚠️ Usage: /next_unused folder_name")
        return
    folder_name = parts[1].lower()
    path, json_number, err = await get_next_unused(folder_name)
    if err:
        clean_err = err.replace("*", "").replace("\\", "")
        await message.answer(clean_err)
        return
    await message.answer(f"⚡ Next unused: #{json_number} in {folder_name}")
    await message.answer_document(FSInputFile(path, filename=f"{folder_name}_json_{json_number}.json"))


@router.message(Command("mark_used"))
async def cmd_mark_used(message: Message) -> None:
    await _mark_status(message, "USED")


@router.message(Command("mark_unused"))
async def cmd_mark_unused(message: Message) -> None:
    await _mark_status(message, "UNUSED")


async def _mark_status(message: Message, status: str) -> None:
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Only admins can change JSON status.")
        return
    parts = message.text.split()
    if len(parts) != 3:
        cmd = "mark_used" if status == "USED" else "mark_unused"
        await message.answer(f"⚠️ Usage: /{cmd} folder_name number")
        return
    folder_name = parts[1].lower()
    try:
        json_number = int(parts[2])
    except ValueError:
        await message.answer("❌ JSON number must be an integer.")
        return
    success, msg = await set_json_status(folder_name, json_number, status)
    clean_msg = msg.replace("*", "").replace("\\", "")
    await message.answer(clean_msg)


@router.message(Command("preview"))
async def cmd_preview(message: Message) -> None:
    parts = message.text.split()
    if len(parts) != 3:
        await message.answer("⚠️ Usage: /preview folder_name number")
        return
    folder_name = parts[1].lower()
    try:
        json_number = int(parts[2])
    except ValueError:
        await message.answer("❌ JSON number must be an integer.")
        return
    preview, err = await preview_json(folder_name, json_number)
    if err:
        await message.answer(err.replace("*", "").replace("\\", ""))
        return
    # Send preview as plain text to avoid any formatting issues
    await message.answer(f"🔍 Preview — {folder_name} #{json_number}\n\n{preview[:3000]}")


# ── Inline callbacks ──────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data and c.data.startswith("action:get:"))
async def cb_get_json(callback: CallbackQuery) -> None:
    folder_name = callback.data.split(":", 2)[2]
    await callback.message.answer(f"📥 Use: /get_json {folder_name} number\nExample: /get_json {folder_name} 1")
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("action:next_unused:"))
async def cb_next_unused(callback: CallbackQuery) -> None:
    folder_name = callback.data.split(":", 2)[2]
    path, json_number, err = await get_next_unused(folder_name)
    if err:
        await callback.message.answer(err.replace("*", "").replace("\\", ""))
        await callback.answer()
        return
    await callback.message.answer(f"⚡ Next unused: #{json_number} in {folder_name}")
    await callback.message.answer_document(FSInputFile(path, filename=f"{folder_name}_json_{json_number}.json"))
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("action:preview:"))
async def cb_preview(callback: CallbackQuery) -> None:
    folder_name = callback.data.split(":", 2)[2]
    await callback.message.answer(f"🔍 Use: /preview {folder_name} number\nExample: /preview {folder_name} 1")
    await callback.answer()
