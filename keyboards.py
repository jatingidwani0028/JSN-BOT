"""Inline keyboard builders."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from models import Folder


def folder_list_keyboard(folders: list[Folder]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for f in folders:
        builder.button(text=f"📁 {f.folder_name}", callback_data=f"folder_select:{f.folder_name}")
    builder.adjust(1)
    return builder.as_markup()


def folder_actions_keyboard(folder_name: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    actions = [
        ("📤 Upload JSON",   f"action:upload:{folder_name}"),
        ("📥 Get JSON",      f"action:get:{folder_name}"),
        ("📊 Statistics",    f"action:stats:{folder_name}"),
        ("🔄 Unused JSONs",  f"action:unused:{folder_name}"),
        ("⚡ Next Unused",   f"action:next_unused:{folder_name}"),
        ("🔍 Preview JSON",  f"action:preview:{folder_name}"),
        ("🗜️ Backup Folder", f"action:backup:{folder_name}"),
        ("🔙 Back",          "action:back"),
    ]
    for text, cb in actions:
        builder.button(text=text, callback_data=cb)
    builder.adjust(2)
    return builder.as_markup()


def back_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Back to Folders", callback_data="action:back")
    return builder.as_markup()
