import json
import re
import asyncio

import aiohttp
from black import datetime
from bs4 import BeautifulSoup
from class_model import Parser


class OpenRent(Parser):

    def __init__(self):
        self.url = "https://www.openrent.co.uk/properties-to-rent/london?term=London"
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
        apartments_data = []
        headers = self.headers
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url, headers=headers) as response:
                outer_html = await response.text()
                soup = BeautifulSoup(outer_html, "html.parser")
                scripts = soup.find_all("script", attrs={"type": "text/javascript"})
                for script in scripts:
                    if script.string and "var PROPERTYIDS =" in script.string:
                        match_ids = re.search(
                            r"var PROPERTYIDS = \[(.*?)\];", script.string
                        )
                        if match_ids:
                            ids = match_ids[1].strip().split(",")
                            match_latitudes = (
                                script.string.split("var PROPERTYLISTLATITUDES = [")[1]
                                .split("var PROPERTYLISTLONGITUDES = [")[0]
                                .replace("];", "")
                                .strip()
                            )
                            match_latitudes = match_latitudes.split(",")
                            match_longitudes = (
                                script.string.split("var PROPERTYLISTLONGITUDES = [")[1]
                                .split("var PROPERTYLISTCOMMORDISTANCEUNIT = ")[0]
                                .replace("];", "")
                                .strip()
                            )
                            match_longitudes = match_longitudes.split(",")
                            for i in range(len(ids[:-1])):
                                apartments_data.append(
                                    {
                                        "id": ids[i],
                                        "latitude": match_latitudes[i],
                                        "longitude": match_longitudes[i],
                                    }
                                )

        batch_size = 20
        all_links = []
        for i in range(0, len(apartments_data), batch_size):
            batch = apartments_data[i : i + batch_size]
            json_link_request = "https://www.openrent.co.uk/search/propertiesbyid?"
            for b in batch:
                json_link_request += f"ids={b.get("id")}&"
            all_links.append(json_link_request[:-1])
        return all_links, apartments_data

    async def parse_apartment(self, link):
        apartments_data = []
        async with aiohttp.ClientSession() as session:
            async with session.get(link, headers=self.headers) as response:
                outer_html = await response.text()
                data_json = json.loads(outer_html)
                for record in data_json:
                    id_ = record.get("id")
                    name = record.get("title")
                    description = record.get("description").strip()
                    images = [f"https:{record.get('imageUrl')}"]
                    details = record.get("details")
                    price = f"£{int(record.get('rentPerMonth'))} per month, £{int(record.get('rentPerWeek'))} per week."
                    link_name = name.replace(",", "").replace(" ", "-").lower()
                    url = f"https://www.openrent.co.uk/property-to-rent/london/{link_name}/{id_}"
                    for i in details:
                        if "Bed" in i:
                            beds = i.split(" ")[0]
                            if beds:
                                beds = str(beds)
                            else:
                                beds = "Not specified"
                            apartments_data.append(
                                {
                                    "id": id_,
                                    "name_of_listing": name,
                                    "bedrooms": beds,
                                    "description": description,
                                    "images": images,
                                    "price": price,
                                    "time": datetime.now(),
                                    "link": url,
                                }
                            )
                return apartments_data

    async def all_apartments(self):
        all_apartments = []
        links_and_locations = await self.get_all_links_on_apartments()
        batch_size = 10
        for i in range(0, len(links_and_locations[0]), batch_size):
            batch = links_and_locations[0][i : i + batch_size]
            tasks = [self.parse_apartment(url) for url in batch]
            apartments_info = await asyncio.gather(*tasks)
            for apartments_data in apartments_info:
                all_apartments.extend(apartments_data)
        for record in all_apartments:
            for location in links_and_locations[1]:
                if str(record.get("id")) == str(location.get("id")):
                    record.update(
                        {
                            "latitude": float(location.get("latitude")),
                            "longitude": float(location.get("longitude")),
                        }
                    )
            del record["id"]
        all_apartments = self.remove_duplicates(all_apartments)
        return all_apartments
