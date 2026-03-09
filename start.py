"""
/start, /help, /folders handlers + folder navigation callbacks.
"""

import logging
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from folder_service import list_folders
from keyboards import folder_list_keyboard, folder_actions_keyboard

router = Router()
logger = logging.getLogger(__name__)

HELP_TEXT = """
🤖 *JSON File Manager Bot*

*Admin Commands:*
`/create\\_folder <name>` — Create a new folder
`/upload <folder>` — Upload a JSON file to folder
`/mark\\_used <folder> <n>` — Mark JSON \\#n as USED
`/mark\\_unused <folder> <n>` — Mark JSON \\#n as UNUSED
`/backup <folder>` — Download folder as ZIP

*Retrieval Commands:*
`/get\\_json <folder> <n>` — Download JSON file \\#n
`/next\\_unused <folder>` — Get next unused JSON
`/preview <folder> <n>` — Preview JSON content

*Info Commands:*
`/stats <folder>` — Folder statistics
`/unused <folder>` — List unused JSON numbers
`/folders` — Browse all folders

Use /folders to browse with buttons 📁
"""


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    logger.info("User %s started the bot", message.from_user.id)
    folders = await list_folders()
    if not folders:
        await message.answer(
            "👋 Welcome to *JSON File Manager*\\!\n\nNo folders yet\\. "
            "Use `/create\\_folder <name>` to get started\\.",
            parse_mode="MarkdownV2",
        )
        return
    await message.answer(
        "👋 Welcome to *JSON File Manager*\\!\n\nSelect a folder:",
        reply_markup=folder_list_keyboard(folders),
        parse_mode="MarkdownV2",
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT, parse_mode="MarkdownV2")


@router.message(Command("folders"))
async def cmd_folders(message: Message) -> None:
    folders = await list_folders()
    if not folders:
        await message.answer("📂 No folders found\\. Use `/create\\_folder <name>` to create one\\.", parse_mode="MarkdownV2")
        return
    await message.answer("📂 *Select a folder:*", reply_markup=folder_list_keyboard(folders), parse_mode="MarkdownV2")


@router.callback_query(lambda c: c.data and c.data.startswith("folder_select:"))
async def cb_folder_select(callback: CallbackQuery) -> None:
    folder_name = callback.data.split(":", 1)[1]
    await callback.message.edit_text(
        f"📁 *Folder: {folder_name}*\n\nChoose an action:",
        reply_markup=folder_actions_keyboard(folder_name),
        parse_mode="MarkdownV2",
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "action:back")
async def cb_back(callback: CallbackQuery) -> None:
    folders = await list_folders()
    await callback.message.edit_text(
        "📂 *Select a folder:*",
        reply_markup=folder_list_keyboard(folders),
        parse_mode="MarkdownV2",
    )
    await callback.answer()
