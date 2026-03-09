"""Statistics, unused list, and backup handlers."""

import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile

from folder_service import get_folder_stats
from json_service import get_unused_json_numbers, backup_folder
from keyboards import folder_actions_keyboard
from config import ADMIN_IDS

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("⚠️ Usage: `/stats <folder>`", parse_mode="MarkdownV2")
        return
    stats = await get_folder_stats(parts[1].lower())
    if not stats:
        await message.answer(f"❌ Folder *{parts[1]}* not found\\.", parse_mode="MarkdownV2")
        return
    pct = (stats.used / stats.total * 100) if stats.total else 0
    bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
    await message.answer(
        f"📊 *Statistics — {stats.folder_name}*\n\n"
        f"Total : `{stats.total}`\n"
        f"✅ Used   : `{stats.used}`\n"
        f"🔄 Unused : `{stats.unused}`\n\n"
        f"`[{bar}]` {pct:.1f}% used",
        parse_mode="MarkdownV2",
    )


@router.message(Command("unused"))
async def cmd_unused(message: Message) -> None:
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("⚠️ Usage: `/unused <folder>`", parse_mode="MarkdownV2")
        return
    numbers, err = await get_unused_json_numbers(parts[1].lower())
    if err:
        await message.answer(err, parse_mode="MarkdownV2")
        return
    if not numbers:
        await message.answer(f"✅ No unused JSON files in *{parts[1]}*\\.", parse_mode="MarkdownV2")
        return
    nums_str = ", ".join(str(n) for n in numbers)
    await message.answer(
        f"🔄 *Unused in {parts[1]}:*\n\n`{nums_str}`\n\n_Showing up to 50 results_",
        parse_mode="MarkdownV2",
    )


@router.message(Command("backup"))
async def cmd_backup(message: Message) -> None:
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Only admins can create backups\\.", parse_mode="MarkdownV2")
        return
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("⚠️ Usage: `/backup <folder>`", parse_mode="MarkdownV2")
        return
    await message.answer("🗜️ Creating backup, please wait\\.\\.\\.", parse_mode="MarkdownV2")
    zip_path, msg = await backup_folder(parts[1].lower())
    if not zip_path:
        await message.answer(msg, parse_mode="MarkdownV2")
        return
    await message.answer_document(
        FSInputFile(zip_path, filename=f"{parts[1]}_backup.zip"),
        caption=msg, parse_mode="MarkdownV2",
    )
    zip_path.unlink(missing_ok=True)


# ── Inline callbacks ──────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data and c.data.startswith("action:stats:"))
async def cb_stats(callback: CallbackQuery) -> None:
    folder_name = callback.data.split(":", 2)[2]
    stats = await get_folder_stats(folder_name)
    if not stats:
        await callback.message.answer(f"❌ Folder *{folder_name}* not found\\.", parse_mode="MarkdownV2")
        await callback.answer()
        return
    pct = (stats.used / stats.total * 100) if stats.total else 0
    bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
    await callback.message.edit_text(
        f"📊 *Statistics — {stats.folder_name}*\n\n"
        f"Total : `{stats.total}`\n✅ Used   : `{stats.used}`\n🔄 Unused : `{stats.unused}`\n\n"
        f"`[{bar}]` {pct:.1f}% used",
        reply_markup=folder_actions_keyboard(folder_name),
        parse_mode="MarkdownV2",
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("action:unused:"))
async def cb_unused(callback: CallbackQuery) -> None:
    folder_name = callback.data.split(":", 2)[2]
    numbers, err = await get_unused_json_numbers(folder_name)
    if err:
        await callback.message.answer(err, parse_mode="MarkdownV2")
        await callback.answer()
        return
    if not numbers:
        text = f"✅ No unused JSON files in *{folder_name}*\\."
    else:
        nums_str = ", ".join(str(n) for n in numbers)
        text = f"🔄 *Unused in {folder_name}:*\n`{nums_str}`"
    await callback.message.edit_text(
        text, reply_markup=folder_actions_keyboard(folder_name), parse_mode="MarkdownV2"
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("action:backup:"))
async def cb_backup(callback: CallbackQuery) -> None:
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Admins only.", show_alert=True)
        return
    folder_name = callback.data.split(":", 2)[2]
    await callback.message.answer("🗜️ Creating backup\\.\\.\\.", parse_mode="MarkdownV2")
    zip_path, msg = await backup_folder(folder_name)
    if not zip_path:
        await callback.message.answer(msg, parse_mode="MarkdownV2")
        await callback.answer()
        return
    await callback.message.answer_document(
        FSInputFile(zip_path, filename=f"{folder_name}_backup.zip"),
        caption=msg, parse_mode="MarkdownV2",
    )
    zip_path.unlink(missing_ok=True)
    await callback.answer("Backup sent!")
