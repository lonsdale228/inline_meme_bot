from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.filters import Command, StateFilter

router = Router()


class NameGroup(StatesGroup):
    name_group = State()




@router.message(Command("create_group"), StateFilter(None))
async def create_group(message: Message, state: FSMContext):

    await message.answer("Enter group name!")

    await state.set_state(NameGroup.name_group)



@router.message(F.text, StateFilter(NameGroup.name_group))
async def name_group(message: Message, state: FSMContext):


    await message.answer("Group created!")

    await state.clear()