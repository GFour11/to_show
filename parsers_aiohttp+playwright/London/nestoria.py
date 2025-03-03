import json
import asyncio
import logging
import time
from datetime import datetime

from bs4 import BeautifulSoup
import aiohttp

from class_model import Parser

proxies = [
    "http://snzakpfz:zdawuph7260g@107.172.163.27:6543",
    "http://snzakpfz:zdawuph7260g@207.244.217.165:6712",
    "http://snzakpfz:zdawuph7260g@198.23.239.134:6540",
]

logging.basicConfig(
    level=logging.INFO,  # Встановлюємо рівень на INFO
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class Nestoria(Parser):

    def __init__(self):
        self.url = "https://www.nestoria.co.uk/london/property/rent?sort=newest"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
        }

    def remove_duplicates(self, array):
        seen_links = set()
        filtered_apartments = []

        for item in array:
            if item["link"] not in seen_links:
                seen_links.add(item["link"])
                filtered_apartments.append(item)

        return filtered_apartments

    async def get_all_links_on_apartments(self):
        pages_links = [
            f"https://www.nestoria.co.uk/london/property/rent/{i}?sort=newest"
            for i in range(2, 5)
        ]
        pages_links.insert(0, self.url)
        return pages_links

    async def parse_apartment(self, link):
        try:
            time.sleep(0.5)
            apartments = []
            async with aiohttp.ClientSession() as session:
                async with session.get(link, headers=self.headers) as response:
                    outer_html = await response.text()
                    soup = BeautifulSoup(outer_html, "html.parser")
                    li_blocks = soup.find_all("li", class_="rating__new")
                    apartment_links = []
                    for l in li_blocks:
                        price = l.find(
                            "div", class_="result__details__price price_click_origin"
                        ).text
                        href = l.find("a").get("data-href")
                        apartment_links.append(
                            {
                                "link": f"https://www.nestoria.co.uk{href}",
                                "price": price,
                            }
                        )

                    script = soup.find_all(
                        "script", attrs={"type": "application/ld+json"}
                    )[1]
                    script_data = json.loads(script.text)
                    apartments_data = script_data.get("about")
                    for record_index in range(len(apartment_links)):
                        apartments.append(
                            {
                                "name_of_listing": apartments_data[record_index].get(
                                    "name"
                                ),
                                "bedrooms": str(
                                    apartments_data[record_index].get(
                                        "numberOfBedrooms"
                                    )
                                ),
                                "latitude": float(
                                    apartments_data[record_index]
                                    .get("geo")
                                    .get("latitude")
                                ),
                                "longitude": float(
                                    apartments_data[record_index]
                                    .get("geo")
                                    .get("longitude")
                                ),
                                "description": apartments_data[record_index].get(
                                    "description"
                                ),
                                "images": [apartments_data[record_index].get("image")],
                                "price": apartment_links[record_index].get("price"),
                                "time": datetime.now(),
                                "link": apartment_links[record_index].get("link"),
                            }
                        )
            return apartments
        except Exception as exception:
            logging.info(exception)

    async def all_apartments(self):
        all_apartments = []
        links = await self.get_all_links_on_apartments()
        tasks = [self.parse_apartment(link) for link in links]
        tasks_result = await asyncio.gather(*tasks)
        for data_set in tasks_result:
            if data_set:
                all_apartments.extend(data_set)

        all_apartments = self.remove_duplicates(all_apartments)
        return all_apartments
