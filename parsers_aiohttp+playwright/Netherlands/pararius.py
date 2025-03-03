import asyncio
import datetime
import json

import aiohttp
from bs4 import BeautifulSoup

from class_model import Parser


class Pararius(Parser):

    def __init__(self):
        self.url = "https://www.pararius.com/apartments/nederland/since-1"
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
                sections = soup.find_all("section")
                if len(sections) >= 1:
                    links = [
                        f"https://www.pararius.com{a.find("a").get("href")}"
                        for a in sections
                    ]
                    return links

    async def parse_apartment(self, link):
        async with aiohttp.ClientSession() as session:
            async with session.get(link, headers=self.headers) as response:
                soup = BeautifulSoup(await response.text(), "html.parser")
                script = soup.find_all("script", attrs={"type": "application/ld+json"})[
                    0
                ]
                apartment_data_json = json.loads(script.string)
                location = soup.find("div", id="map")
                latitude = location.find("wc-detail-map", class_="detail-map map").get(
                    "data-latitude"
                )
                longitude = location.find("wc-detail-map", class_="detail-map map").get(
                    "data-longitude"
                )

                apartment = {
                    "name_of_listing": f"{apartment_data_json.get("address").get("streetAddress")} in "
                    f"{apartment_data_json.get("address").get("addressLocality")} "
                    f"{apartment_data_json.get("address").get("addressRegion")} "
                    f"({apartment_data_json.get("address").get("postalCode")})",
                    "bedrooms": str(
                        apartment_data_json.get("numberOfRooms")[0].get("value")
                    ),
                    "latitude": float(latitude),
                    "longitude": float(longitude),
                    "description": apartment_data_json.get("description"),
                    "images": [apartment_data_json.get("image")],
                    "price": f"{apartment_data_json.get("offers").get("price")} "
                    f"{apartment_data_json.get("offers").get("priceCurrency")}",
                    "time": datetime.datetime.now(),
                    "link": link,
                }
                return apartment

    async def all_apartments(self):
        links = await self.get_all_links_on_apartments()
        if links:
            tasks = [self.parse_apartment(link) for link in links]
            all_apartments = await asyncio.gather(*tasks)
            return all_apartments
