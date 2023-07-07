import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

def scrape_product_listing_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    products = soup.find_all('div', {'data-component-type': 's-search-result'})

    data = []
    for product in products:
        product_url_element = product.find('a', {'class': 'a-link-normal s-no-outline'})
        if product_url_element:
            product_url = 'https://www.amazon.in' + product_url_element['href']
        else:
            product_url = ''

        product_name_element = product.find('span', {'class': 'a-size-medium a-color-base a-text-normal'})
        if product_name_element:
            product_name = product_name_element.text.strip()
        else:
            product_name = ''

        price_element = product.find('span', {'class': 'a-price-whole'})
        product_price = price_element.text.strip() if price_element else ''

        rating_element = product.find('span', {'class': 'a-icon-alt'})
        rating = rating_element.text.split()[0] if rating_element else ''

        num_reviews_element = product.find('span', {'class': 'a-size-base'})
        num_reviews = num_reviews_element.text if num_reviews_element else ''

        data.append([product_url, product_name, product_price, rating, num_reviews])

    return data

def scrape_product_details(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    description_element = soup.find('div', {'id': 'productDescription'})
    description = description_element.get_text(separator='\n').strip() if description_element else ''

    asin_match = re.search(r'/dp/([^/]+)', url)
    asin = asin_match.group(1) if asin_match else ''

    manufacturer_element = soup.find('a', {'class': 'a-size-base prodDetAttrValue'})
    manufacturer = manufacturer_element.text.strip() if manufacturer_element else ''

    return description, asin, manufacturer

start_url = 'https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_'
num_pages = 120

all_data = []
for page in range(1, num_pages + 1):
    url = start_url + str(page)
    print(f'Scraping page {page}...')
    data = scrape_product_listing_page(url)
    all_data.extend(data)
    time.sleep(1)

for product in all_data:
    url = product[0]
    description, asin, manufacturer = scrape_product_details(url)
    product.extend([description, asin, manufacturer])
    time.sleep(1)

df = pd.DataFrame(all_data, columns=['Product URL', 'Product Name', 'Product Price', 'Rating', 'Number of Reviews', 'Description', 'ASIN', 'Manufacturer'])
df.to_csv('product_data.csv', index=False)
