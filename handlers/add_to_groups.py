from gettext import dpgettext

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils import keyboard
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.utils import get_user_groups, send_meme_to_selected_group
from loader import bot

router = Router()



class AddToGroup(StatesGroup):
    add_meme_to_group = State()

@router.message(StateFilter(AddToGroup.add_meme_to_group))
async def add_meme_to_group(message: Message, state: FSMContext, meme_id: int):
    result = await get_user_groups(str(message.from_user.id))

    keyboard = []

    kb_dict = {
        "Send to all groups!": "callback_send_all",
        "Send to selected!": "callback_send_selected",
        # "Make private": "callback_send_private",
        # "Make public": "callback_send_public",
    }

    for i, group in enumerate(result):
        keyboard.append([
            InlineKeyboardButton(
                text = "❌"+" "+group.name,
                callback_data = f"callback_change_status@{group.id}/{i}"
            )]
        )

    for text, callback_data in kb_dict.items():
        keyboard.append([
            InlineKeyboardButton(text = text, callback_data = callback_data)
        ])

    await state.update_data(meme_id=meme_id)
    await state.update_data(keyboard=keyboard)
    await state.set_state(AddToGroup.add_meme_to_group)
    await message.answer(f"Choose groups to add meme to:", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))


@router.callback_query(F.data.contains('change'), StateFilter(AddToGroup.add_meme_to_group))
async def callback_change(callback: CallbackQuery, state: FSMContext):
    keyboard: list[list[InlineKeyboardButton]] = (await state.get_data())["keyboard"]

    data = await state.get_data()

    if "groups_to_add" in data:
        groups_to_add:list = data["groups_to_add"]
    else:
        groups_to_add = []

    i = int(callback.data.split("/")[1])
    group_id: int = int(callback.data.split("@")[1].split("/")[0])


    if "❌" in keyboard[i][0].text:
        keyboard[i][0].text = keyboard[i][0].text.replace("❌", "✅")
        groups_to_add.append(group_id)
    else:
        keyboard[i][0].text = keyboard[i][0].text.replace("✅", "❌")
        groups_to_add.remove(group_id)

    await state.update_data(keyboard=keyboard)
    await state.update_data(groups_to_add=groups_to_add)
    await callback.message.edit_text(text=f"Choose groups to add meme to:",
                                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))


@router.callback_query(F.data.contains('send'), StateFilter(AddToGroup.add_meme_to_group))
async def callback_send(callback: CallbackQuery, state: FSMContext):

    if "selected" in callback.data:
        data = await state.get_data()
        groups_to_add: list = data["groups_to_add"]
        meme_id: int = data["meme_id"]
        await send_meme_to_selected_group(groups_to_add, meme_id)
        await callback.message.edit_text("Successfully sent meme!", reply_markup=InlineKeyboardMarkup(inline_keyboard=[]))
        await state.clear()
        ...
    elif "all" in callback.data:
        ...


