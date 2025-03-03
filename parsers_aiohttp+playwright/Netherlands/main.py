import asyncio

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from concurrent.futures import ThreadPoolExecutor
from funda import Funda
from huurwoningen import Huurwoningen
from pararius import Pararius
from db.postgres_operations import netherland
from db.postgres_connection import async_session
import logging

logging.basicConfig(
    level=logging.INFO,  # Встановлюємо рівень на INFO
    format="%(asctime)s - %(levelname)s - %(message)s",
)

funda = Funda()
huurwoningen = Huurwoningen()
pararius = Pararius()


def timer(func):
    async def wrapper(*args, **kwargs):
        while True:
            logging.info("START OPERATION")
            await func(*args, **kwargs)
            logging.info("OPERATION FINISH")
            await asyncio.sleep(15 * 60)

    return wrapper


async def start_scrapping():
    parsers = [
        funda.all_apartments(),
        huurwoningen.all_apartments(),
        pararius.all_apartments(),
    ]
    with ThreadPoolExecutor(max_workers=(len(parsers))) as executor:
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(executor, asyncio.run, parser) for parser in parsers
        ]

        gather_return = await asyncio.gather(*tasks)
        scrapped_apartments_data = []
        for lst in gather_return:
            scrapped_apartments_data.extend(lst)

    return scrapped_apartments_data


async def add_to_db(scrapped_apartments_data):
    async with async_session() as session:
        duplicates = await netherland.find_duplicates(session, scrapped_apartments_data)
        new_objects = await netherland.add_to_db(session, duplicates)
        logging.info(f"----------------------------------------------")
        logging.info(f"--------------{new_objects[0]}-----------------")
        logging.info(f"----------------------------------------------")


@timer
async def main_cycle():
    scrapping_data = await start_scrapping()
    await add_to_db(scrapping_data)


if __name__ == "__main__":
    asyncio.run(main_cycle())
