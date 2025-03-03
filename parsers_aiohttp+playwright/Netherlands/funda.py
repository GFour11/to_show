import asyncio
import datetime
import json

import aiohttp
from bs4 import BeautifulSoup

from class_model import Parser


class Funda(Parser):

    def __init__(self):
        self.url = "https://www.funda.nl/zoeken/huur?publication_date=%221%22"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
        }

    async def get_all_links_on_apartments(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url, headers=self.headers) as response:
                soup = BeautifulSoup(await response.text(), "html.parser")
                scripts = soup.find_all(
                    "script", attrs={"type": "application/ld+json"}
                )[0]
                apartments_json = json.loads(scripts.string)
                apartments_source_links = [
                    apartment.get("url")
                    for apartment in apartments_json.get("itemListElement")
                ]
                return apartments_source_links

    async def parse_apartment(self, link):
        async with aiohttp.ClientSession() as session:
            async with session.get(link, headers=self.headers) as response:
                soup = BeautifulSoup(await response.text(), "html.parser")
                script = soup.find_all("script", attrs={"type": "application/ld+json"})[
                    0
                ]
                apartment_data_json = json.loads(script.string)
                description = soup.find("meta", attrs={"name": "description"})[
                    "content"
                ]
                application_json_script = soup.find_all(
                    "script", attrs={"type": "application/json"}
                )[1]
                apartment_data_extended = json.loads(application_json_script.string)
                for index in range(len(apartment_data_extended)):
                    if apartment_data_extended[index] == "Aantal kamers":
                        bedrooms = apartment_data_extended[index + 1]
                        break
                    else:
                        bedrooms = None
                for index in range(len(apartment_data_extended)):
                    if (
                        type(apartment_data_extended[index]) is dict
                        and "lat" in apartment_data_extended[index].keys()
                    ):
                        latitude = apartment_data_extended[index + 1]
                        longitude = apartment_data_extended[index + 2]
                        break
                apartment = {
                    "name_of_listing": f"{apartment_data_json.get("description").replace(" [funda]", "")}",
                    "bedrooms": str(bedrooms),
                    "latitude": float(latitude),
                    "longitude": float(longitude),
                    "description": description,
                    "images": [
                        image.get("contentUrl")
                        for image in apartment_data_json.get("photo")
                    ],
                    "price": f"{apartment_data_json.get("offers").get("price")} "
                    f"{apartment_data_json.get("offers").get("priceCurrency")}",
                    "time": datetime.datetime.now(),
                    "link": link,
                }
                return apartment

    async def all_apartments(self):
        links = await self.get_all_links_on_apartments()
        tasks = [self.parse_apartment(link) for link in links]
        all_apartments = await asyncio.gather(*tasks)
        return all_apartments
