import logging
import asyncio
from bot import run_bot
from config import config

if __name__ == "__main__":
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()), format=config.log_format
    )
    asyncio.run(run_bot())
