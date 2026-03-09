"""
/start, /help, /folders handlers + folder navigation callbacks.
Uses plain HTML parse mode — much simpler and no escaping issues.
"""

import logging
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from folder_service import list_folders
from keyboards import folder_list_keyboard, folder_actions_keyboard

router = Router()
logger = logging.getLogger(__name__)

HELP_TEXT = (
    "🤖 <b>JSON File Manager Bot</b>\n\n"
    "<b>Admin Commands:</b>\n"
    "/create_folder &lt;name&gt; — Create a new folder\n"
    "/upload &lt;folder&gt; — Upload a JSON file\n"
    "/mark_used &lt;folder&gt; &lt;n&gt; — Mark JSON #n as USED\n"
    "/mark_unused &lt;folder&gt; &lt;n&gt; — Mark JSON #n as UNUSED\n"
    "/backup &lt;folder&gt; — Download folder as ZIP\n\n"
    "<b>Retrieval Commands:</b>\n"
    "/get_json &lt;folder&gt; &lt;n&gt; — Download JSON file #n\n"
    "/next_unused &lt;folder&gt; — Get next unused JSON\n"
    "/preview &lt;folder&gt; &lt;n&gt; — Preview JSON content\n\n"
    "<b>Info Commands:</b>\n"
    "/stats &lt;folder&gt; — Folder statistics\n"
    "/unused &lt;folder&gt; — List unused JSON numbers\n"
    "/folders — Browse all folders with buttons\n"
)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    logger.info("User %s started the bot", message.from_user.id)
    try:
        folders = await list_folders()
        if not folders:
            await message.answer(
                "👋 Welcome to <b>JSON File Manager</b>!\n\n"
                "No folders yet.\n"
                "Admin: use /create_folder to get started.\n\n"
                "Use /help to see all commands.",
                parse_mode="HTML",
            )
            return
        await message.answer(
            "👋 Welcome to <b>JSON File Manager</b>!\n\nSelect a folder:",
            reply_markup=folder_list_keyboard(folders),
            parse_mode="HTML",
        )
    except Exception as e:
        logger.error("Error in /start: %s", e)
        await message.answer("✅ Bot is running! Use /help to see commands.")


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    try:
        await message.answer(HELP_TEXT, parse_mode="HTML")
    except Exception as e:
        logger.error("Error in /help: %s", e)
        await message.answer("Bot is running. Commands: /folders /stats /help")


@router.message(Command("folders"))
async def cmd_folders(message: Message) -> None:
    try:
        folders = await list_folders()
        if not folders:
            await message.answer(
                "📂 No folders found.\nAdmin: use /create_folder name to create one."
            )
            return
        await message.answer(
            "📂 <b>Select a folder:</b>",
            reply_markup=folder_list_keyboard(folders),
            parse_mode="HTML",
        )
    except Exception as e:
        logger.error("Error in /folders: %s", e)
        await message.answer("Error loading folders. Check logs.")


@router.callback_query(lambda c: c.data and c.data.startswith("folder_select:"))
async def cb_folder_select(callback: CallbackQuery) -> None:
    try:
        folder_name = callback.data.split(":", 1)[1]
        await callback.message.edit_text(
            f"📁 <b>Folder: {folder_name}</b>\n\nChoose an action:",
            reply_markup=folder_actions_keyboard(folder_name),
            parse_mode="HTML",
        )
    except Exception as e:
        logger.error("Error in folder_select callback: %s", e)
    await callback.answer()


@router.callback_query(lambda c: c.data == "action:back")
async def cb_back(callback: CallbackQuery) -> None:
    try:
        folders = await list_folders()
        await callback.message.edit_text(
            "📂 <b>Select a folder:</b>",
            reply_markup=folder_list_keyboard(folders),
            parse_mode="HTML",
        )
    except Exception as e:
        logger.error("Error in back callback: %s", e)
    await callback.answer()
