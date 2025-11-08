from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

rt = Router()

@rt.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer("Привет, я бот для создания профессиональных резюме!")