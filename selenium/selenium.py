import undetected_chromedriver as uc
import re
import time
from bs4 import BeautifulSoup
import json
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime

def clean_url(url):
    """Remove any URL parameters."""
    return url.split('?')[0]

def extract_id(url):
    """Extract the property ID from the URL."""
    return url.strip('/').split('/')[-1]

def extract_price(page_source):
    """Extract price using regex."""
    price_match = re.search(r'"price_actual":"(\d+)"', page_source)
    return price_match.group(1) if price_match else None

def extract_bed(page_source):
    """Extract number of bedrooms."""
    bed_match = re.search(r'"numBedrooms\\":(\d+)', page_source)
    return bed_match.group(1) if bed_match else None

def extract_lat_long(page_source):
    """Extract latitude and longitude."""
    lat_long_match = re.search(r'"latitude\\":(-?\d+\.\d+),\\"longitude\\":(-?\d+\.\d+)', page_source)
    if lat_long_match:
        return lat_long_match.group(1), lat_long_match.group(2)
    return None, None

def extract_image_urls(page_source):
    """Extract unique image URLs using regex."""
    img_pattern = r'https://lid\.zoocdn\.com/u/1024/768/[\w/-]+\.jpg'
    return list(set(re.findall(img_pattern, page_source)))


def extract_description(soup):
    """Extract the property description."""
    description = soup.find('meta', {'name': 'description'})
    return description['content'] if description else 'No description available'



def get_page_data(url, chrome):
    """Extract the property data from the given URL."""
    try:
        chrome.get(url)
        time.sleep(2)
        soup = BeautifulSoup(chrome.page_source, 'lxml')

        title = soup.find('title').text.strip() if soup.find('title') else 'No title available'


        price = extract_price(chrome.page_source)
        bed = extract_bed(chrome.page_source)
        latitude, longitude = extract_lat_long(chrome.page_source)

        image_urls = extract_image_urls(chrome.page_source)

        description = extract_description(soup)

        return {
            'title': title,
            'bedroom': bed,
            'latitude': float(latitude),
            'longitude': float(longitude),
            'description': description,
            'image_urls': image_urls,
            'price': price,
            'link': url
        }
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None


def scrape_zoopla():
    chrome = uc.Chrome()

    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f'{timestamp}_zoopla_data.json'
    with open(filename, 'w', encoding='utf-8') as json_file:
        json_file.write('[')

    for page in range(1, 41):
        url = f'https://www.zoopla.co.uk/to-rent/property/london/?price_frequency=per_month&q=London&search_source=home&pn={page}'
        chrome.get(url)
        WebDriverWait(chrome, 30).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        soup = BeautifulSoup(chrome.page_source, 'html.parser')
        elements = soup.find_all('a', class_='_1lw0o5c1')


        urls = ['https://www.zoopla.co.uk' + element.get('href') for element in elements if element.get('href')]
        cleaned_urls = [clean_url(url) for url in urls]


        for url in cleaned_urls:
            data = get_page_data(url, chrome)
            if data:
                print(data)
                with open(filename, 'a', encoding='utf-8') as json_file:
                    json.dump(data, json_file, ensure_ascii=False, indent=4)
                    json_file.write(',\n')

        time.sleep(2)


    chrome.quit()

    with open(filename, 'a', encoding='utf-8') as json_file:
        json_file.write(']')

    print(f"Data has been successfully exported to '{filename}'")

if __name__ == '__main__':
    scrape_zoopla()
