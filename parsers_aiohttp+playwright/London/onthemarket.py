import json
import logging
import re
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from datetime import datetime

from class_model import Parser

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class OnTheMarket(Parser):

    def __init__(self):
        self.url = "https://www.onthemarket.com/to-rent/property/london/?recently-added=24-hours&sort-field=update_date&view=map-list"
        self.useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
        self.locale = "en-US"

    def remove_duplicates(self, array):
        seen_links = set()
        filtered_apartments = []

        for item in array:
            if item["link"] not in seen_links:
                seen_links.add(item["link"])
                filtered_apartments.append(item)

        return filtered_apartments

    async def get_all_links_on_apartments(self):
        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent=self.useragent, locale=self.locale
                )
                page = await context.new_page()
                await page.route(
                    "**/*",
                    lambda route: (
                        route.abort()
                        if route.request.resource_type in ["image", "media", "font"]
                        else route.continue_()
                    ),
                )
                await page.goto(self.url)
                full_html = await page.content()
                await browser.close()
                soup = BeautifulSoup(full_html, "html.parser")
                last_page_block = soup.find("div", class_="M4_NK1")
                if last_page_block:
                    last_page = last_page_block.find_all("li")[-1]
                    try:
                        last_page = int(last_page.text)
                        if last_page >= 2:
                            all_urls = [
                                f"https://www.onthemarket.com/to-rent/property/london/?page={i}&recently-added=24-hours&sort-field=update_date&view=map-list"
                                for i in range(2, last_page + 1)
                            ]
                            all_urls.append(self.url)
                            return all_urls
                        else:
                            return [self.url]
                    except TypeError:
                        logging.info("not int")
            except Exception as e:
                logging.info(e)

    async def parse_apartment(self, link):
        apartments = []
        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent=self.useragent, locale=self.locale
                )
                page = await context.new_page()
                await page.goto(link)

                full_html = await page.content()
                await browser.close()
                soup = BeautifulSoup(full_html, "html.parser")
                script = soup.find("script", id="__NEXT_DATA__")
                script_text = json.loads(script.text)
                locations = (
                    script_text.get("props").get("pageProps").get("maps").get("list")
                )
                ul = soup.find("ul", id="maincontent")
                li = ul.find_all("li")

                for i in li:
                    pattern = re.compile(r"result-(\d+)")
                    try:
                        match = pattern.match(i["id"])
                        if match:
                            id = match.group(1)
                            images = i.find_all("picture")
                            images = [
                                img.find("img") for img in images if img is not None
                            ]
                            images = list(set(picture.get("src") for picture in images))
                            name = (
                                i.find("div", attrs={"data-component": "price-title"})
                                .find("address")
                                .text
                            )
                            price = (
                                i.find("div", attrs={"data-component": "price-title"})
                                .find("a")
                                .text
                            )
                            bed_bath = i.find(
                                "div", attrs={"data-component": "BedBathCounts"}
                            )
                            bedrooms = None
                            if bed_bath:
                                spans = bed_bath.find_all("span")
                                for span in spans:
                                    use = span.find("use")
                                    if use:
                                        href = use.get("href")
                                        if href == "#icon-bed-front":
                                            bedrooms = span.text
                            for record in locations:
                                if id == record.get("id"):
                                    location = record.get("location")
                                    if location:
                                        apartments.append(
                                            {
                                                "name_of_listing": name,
                                                "bedrooms": (
                                                    bedrooms
                                                    if bedrooms
                                                    else "Not specified"
                                                ),
                                                "latitude": float(location.get("lat")),
                                                "longitude": float(location.get("lon")),
                                                "description": None,
                                                "images": images,
                                                "price": price,
                                                "time": datetime.now(),
                                                "link": f"https://www.onthemarket.com/details/{id}",
                                            }
                                        )
                    except KeyError:
                        pass
            except Exception as e:
                logging.info(e)
        return apartments

    async def all_apartments(self):
        all_apartments = []
        links = await self.get_all_links_on_apartments()
        for link in links:
            apartments_info = await self.parse_apartment(link)
            if apartments_info:
                all_apartments.extend(apartments_info)
        all_apartments = self.remove_duplicates(all_apartments)
        return all_apartments
