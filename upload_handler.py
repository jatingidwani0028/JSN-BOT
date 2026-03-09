"""JSON file upload handler with FSM."""

import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, Document
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from json_service import save_json_file
from config import ADMIN_IDS, MAX_JSON_FILE_SIZE

router = Router()
logger = logging.getLogger(__name__)


class UploadState(StatesGroup):
    waiting_for_file = State()


@router.message(Command("upload"))
async def cmd_upload(message: Message, state: FSMContext) -> None:
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Only admins can upload JSON files\\.", parse_mode="MarkdownV2")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("⚠️ Usage: `/upload <folder\\_name>`", parse_mode="MarkdownV2")
        return

    folder_name = parts[1].strip().lower()
    await state.set_state(UploadState.waiting_for_file)
    await state.update_data(folder_name=folder_name)
    await message.answer(
        f"📤 Ready to upload to *{folder_name}*\\.\nSend your \\.json file now\\.",
        parse_mode="MarkdownV2",
    )


@router.callback_query(lambda c: c.data and c.data.startswith("action:upload:"))
async def cb_upload_action(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Admins only.", show_alert=True)
        return
    folder_name = callback.data.split(":", 2)[2]
    await state.set_state(UploadState.waiting_for_file)
    await state.update_data(folder_name=folder_name)
    await callback.message.answer(
        f"📤 Ready to upload to *{folder_name}*\\.\nSend your \\.json file now\\.",
        parse_mode="MarkdownV2",
    )
    await callback.answer()


@router.message(UploadState.waiting_for_file, F.document)
async def handle_json_upload(message: Message, state: FSMContext) -> None:
    doc: Document = message.document

    if not doc.file_name.endswith(".json"):
        await message.answer("❌ Please send a `.json` file\\.", parse_mode="MarkdownV2")
        return

    if doc.file_size > MAX_JSON_FILE_SIZE:
        await message.answer(
            f"❌ File too large \\({doc.file_size // 1024} KB\\)\\. Max: {MAX_JSON_FILE_SIZE // 1024} KB\\.",
            parse_mode="MarkdownV2",
        )
        return

    data = await state.get_data()
    folder_name = data.get("folder_name")
    if not folder_name:
        await message.answer("❌ Session expired\\. Please use /upload again\\.", parse_mode="MarkdownV2")
        await state.clear()
        return

    file = await message.bot.get_file(doc.file_id)
    bio = await message.bot.download_file(file.file_path)
    content: bytes = bio.read()

    success, msg = await save_json_file(folder_name, content)
    await message.answer(msg, parse_mode="MarkdownV2")

    if success:
        logger.info("User %s uploaded to '%s' (%d bytes)", message.from_user.id, folder_name, len(content))

    await message.answer("📤 Send another \\.json file or /cancel to stop\\.", parse_mode="MarkdownV2")


@router.message(UploadState.waiting_for_file)
async def upload_wrong_input(message: Message) -> None:
    if message.text and message.text.startswith("/cancel"):
        return
    await message.answer("⚠️ Please send a \\.json file, or /cancel to abort\\.", parse_mode="MarkdownV2")


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    if await state.get_state():
        await state.clear()
        await message.answer("❎ Operation cancelled\\.", parse_mode="MarkdownV2")
    else:
        await message.answer("Nothing to cancel\\.", parse_mode="MarkdownV2")
