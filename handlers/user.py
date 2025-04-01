import json
import re
import secrets

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InputFile, FSInputFile, BufferedInputFile, KeyboardButton, ReplyKeyboardMarkup, \
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command, StateFilter

from database.models import Meme, Group
from database.utils import create_group, add_user, delete_group, delete_meme, get_memes, get_user_groups

router = Router()


class NameGroup(StatesGroup):
    name_group = State()

@router.message(Command("create_group"), StateFilter(None))
async def create_group_handler(message: Message, state: FSMContext):

    await message.answer("Enter group name!")

    await state.set_state(NameGroup.name_group)



@router.message(F.text, StateFilter(NameGroup.name_group))
async def name_group_handler(message: Message, state: FSMContext):
    group_name = message.text.strip()

    pattern = re.compile(r'^[A-Za-zА-Яа-я0-9_]+$')

    match = bool(pattern.fullmatch(group_name))

    if (not match) or (len(group_name)<3):
        await message.answer("Enter correct group name! 3 or more symbols length \n"
                             "You can use only A-z, А-я, 0-9 and _ for spaces!")
        return

    token = secrets.token_hex(16)

    await add_user(str(message.from_user.id), is_admin=False)
    await create_group(str(message.from_user.id), group_name, token)

    await message.answer("Group created! \n"
                         "Invite link: \n"
                         f"https://t.me/inlinusbot?start={token}")

    await state.clear()

@router.message(Command("export_memes"))
async def export_memes_handler(message: Message):
    memes = await get_memes(search_text="*", media_type="*", user_id=str(message.from_user.id))
    data = {}
    meme: Meme
    for meme in memes:
        data["name"] = meme.name
        data["mime_type"] = meme.mime_type
        data["is_public"] = meme.is_public
        data["file_id"] = meme.file_id
        data["user_tg_id"] = meme.user_tg_id

    json_data = json.dumps(data, ensure_ascii=False).encode("utf-8")

    input_file = BufferedInputFile(
        file=json_data,
        filename=f"backup_{message.from_user.id}.json"
    )

    await message.answer_document(input_file)


class DeleteMeme(StatesGroup):
    delete_meme = State()

@router.message(Command("delete_meme"), StateFilter(None))
async def delete_meme_handler(message: Message, state: FSMContext):
    await message.answer("Send meme to delete!")
    await state.set_state(DeleteMeme.delete_meme)

@router.message(StateFilter(DeleteMeme.delete_meme))
async def delete_meme_handler(message: Message, state: FSMContext):

    FILE_SOURCES = {
        'sticker': message.sticker,
        'video': message.video,
        'animation': message.animation,
        'audio': message.audio
    }

    # Find the first valid file source
    file_source = next(
        (content for content in FILE_SOURCES.values() if content),
        None
    )

    if not file_source:
        await message.answer("Wrong file type!")
        await state.clear()
        return
    await message.answer(f"{file_source.file_unique_id}")
    is_deleted = await delete_meme(file_source.file_unique_id, str(message.from_user.id))
    await state.clear()

    await message.answer(
        "Deleted meme!" if is_deleted
        else "You don't own this meme!"
    )

@router.callback_query(F.data.contains("callback_back_to_menu"))
@router.message(Command("show_groups"))
async def show_groups_handler(message: Message = None, callback_query: CallbackQuery = None):
    group_list = await get_user_groups(str(message.from_user.id))
    kb = []
    for group in group_list:
        kb.append(
            [
                InlineKeyboardButton(
                    text=group.name,
                    callback_data=f"callback_group_edit/{group.id}"
                )
            ]
        )

    if message.text:
        await message.answer("Your groups msg: ",reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    else:
        await callback_query.message.edit_text("Your groups call: ", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))


@router.callback_query(F.data.contains("callback_group_edit"))
async def callback_group_edit_handler(callback_query: CallbackQuery):
    group_id = int(callback_query.data.split("/")[1])

    kb = [
        [InlineKeyboardButton(
            text = "❌ Leave from group", callback_data=f"callback_group_remove/{group_id}"
        )],
        [InlineKeyboardButton(
            text = "👥 Manage group members", callback_data=f"callback_edit_members/{group_id}"
        )],
        [InlineKeyboardButton(
            text = "🔙 Back", callback_data="callback_back_to_menu"
        )]
    ]
    await callback_query.message.edit_text(text="Choose option:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))


# class DeleteGroup(StatesGroup):
#     delete_group = State()
#
# @router.message(Command("delete_group"), StateFilter(None))
# async def delete_group_handler(message: Message, state: FSMContext):
#     kb = [
#         [KeyboardButton(text="Delete everything!"),
#         KeyboardButton(text="Just left..."),]
#     ]
#
#
#     await message.answer("Are you sure you want to delete this group and all memes? \n"
#                          "Or you wanna just left and save memes? \n"
#                          "Group will have new admin!", reply_markup=ReplyKeyboardMarkup(keyboard=kb))
#
#     await state.set_state(DeleteGroup.delete_group)
#
# @router.message(F.text == "Delete everything!", StateFilter(DeleteGroup.delete_group))
# async def do_delete_group(message: Message, state: FSMContext):
#     data = await state.get_data()
#     group_id = int(data["delete_group_id"])
#
#     await delete_group(group_id, str(message.from_user.id))
#     await message.answer("Successfully deleted everything! \n"
#                          "Users will miss your memes🥹")
#     await state.clear()