import logging
from os import getenv

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import config
from rag import rag_service

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(f"Привет, {html.bold(message.from_user.full_name)}!")


@dp.message()
async def message_handler(message: Message) -> None:
    """ """
    try:
        logging.info(
            f"Message '{message.text}' with id {message.message_id} was received successfully"
        )
        answer_text = rag_service(message.text)
        await message.answer(answer_text)
        logging.info(f"Answer with text '{answer_text}' was sent successfully")
    except Exception as e:
        logging.exception(f"Error occurred while handling message: {e}")

        try:
            await message.answer("Bad request!")
        except Exception as e:
            logging.exception(f"Failed to send error message: {e}")


async def run_bot() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(
        token=config.telegram_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    # And the run events dispatching
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=["message, edited_message"])
