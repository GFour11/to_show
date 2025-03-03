from abc import ABC, abstractmethod
import datetime
import logging

logging.basicConfig(
    level=logging.INFO,  # Встановлюємо рівень на INFO
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class MetaParser(ABC):
    @abstractmethod
    async def get_all_links_on_apartments(self):
        pass

    @abstractmethod
    async def parse_apartment(self, link):
        pass

    @abstractmethod
    async def all_apartments(self):
        pass


class Parser(MetaParser):

    def logger_main(self, func):
        async def wrapper(*args, **kwargs):
            class_name = self.__class__.__name__
            start_time = datetime.datetime.now()

            logging.info(f"[{class_name}] Operation: {func.__name__}")
            logging.info(f"[{class_name}] Start time: {start_time}")

            try:
                result = await func(*args, **kwargs)

                result_length = (
                    len(result) if isinstance(result, list) else "Not a list"
                )
                logging.info(f"[{class_name}] Finished without eny errors.")
                logging.info(f"[{class_name}] Result length: {result_length}")

                return result

            except Exception as e:
                logging.error(f"[{class_name}] Error: {e}", exc_info=True)

        return wrapper

    def logger_second(self, func):
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                logging.error(f"[{func.__name__}] Error: {e}", exc_info=True)

        return wrapper

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.all_apartments = cls().logger_main(cls.all_apartments)
        cls.get_all_links_on_apartments = cls().logger_second(
            cls.get_all_links_on_apartments
        )
        cls.parse_apartment = cls().logger_second(cls.parse_apartment)

    async def get_all_links_on_apartments(self):
        pass

    async def parse_apartment(self, link):
        pass

    async def all_apartments(self):
        pass
