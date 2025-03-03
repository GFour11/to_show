from class_model import Parser

import asyncio
import aiohttp
from datetime import datetime


class RightMove(Parser):

    def __init__(self):
        self.url = "https://www.rightmove.co.uk/api/property-search/listing/search?searchLocation=London&useLocationIdentifier=true&locationIdentifier=REGION%5E87490&radius=0.0&_includeLetAgreed=on&includeLetAgreed=false&index=0&sortType=6&channel=RENT&transactionType=LETTING&displayLocationIdentifier=London-87490.html"
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
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url, headers=self.headers) as response:
                data = await response.json()
                pages = data.get("pagination").get("options")
                pages_index = [i.get("value") for i in pages]
                links = [
                    f"https://www.rightmove.co.uk/api/property-search/listing/search?searchLocation=London&useLocationIdentifier=true&locationIdentifier=REGION%5E87490&radius=0.0&_includeLetAgreed=on&includeLetAgreed=false&index={index}&sortType=6&channel=RENT&transactionType=LETTING&displayLocationIdentifier=London-87490.html"
                    for index in pages_index
                ]
                return links

    async def parse_apartment(self, link):
        apartments = []
        async with aiohttp.ClientSession() as session:
            async with session.get(link, headers=self.headers) as response:
                json_data = await response.json()
                properties = json_data.get("properties")
                for record in properties:
                    name = record.get("displayAddress")
                    if record.get("bedrooms") != 0:
                        bedrooms = str(record.get("bedrooms"))
                    else:
                        bedrooms = "Not specified"
                    location = record.get("location")
                    description = record.get("summary")
                    images = [img.get("srcUrl") for img in record.get("images")]
                    price_per_month = (
                        record.get("price").get("displayPrices")[0].get("displayPrice")
                    )
                    price_per_week = (
                        record.get("price").get("displayPrices")[1].get("displayPrice")
                    )
                    url = record.get("propertyUrl")
                    apartments.append(
                        {
                            "name_of_listing": name,
                            "bedrooms": bedrooms,
                            "latitude": float(location.get("latitude")),
                            "longitude": float(location.get("longitude")),
                            "description": description,
                            "images": images,
                            "price": f"{price_per_month} {price_per_week}",
                            "time": datetime.now(),
                            "link": f"https://www.rightmove.co.uk{url}",
                        }
                    )

        return apartments

    async def all_apartments(self):
        all_apartments = []
        links = await self.get_all_links_on_apartments()
        tasks = [self.parse_apartment(link) for link in links]
        all_results = await asyncio.gather(*tasks)

        for record in all_results:
            if record:
                all_apartments.extend(record)
        all_apartments = self.remove_duplicates(all_apartments)
        return all_apartments
