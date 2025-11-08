from aiogram import Dispatcher
from bot.handlers.start_handler import rt as start_rt

def router(dp: Dispatcher) -> None:
    dp.include_router(start_rt)