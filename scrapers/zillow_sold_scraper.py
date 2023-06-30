import requests
from bs4 import BeautifulSoup
import json
import time
import os.path
import pandas as pd
import re


class ZillowSoldScraper():
    results = []
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Cookie": "XXXXX",
        "Dnt": "1",
        "Sec-Ch-Ua": "XXXXX",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "Windows",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "XXXXX",
    }

    def fetch(self, url, parameters):
        response = requests.get(
            url, headers=self.headers, params=parameters)
        return response

    def parse(self, response):
        content = BeautifulSoup(response, features="html.parser")
        deck = content.select('ul.photo-cards')
        for card in deck[0].contents:
            script = card.find('script', {'type': 'application/ld+json'})
            if script:
                script_json = json.loads(script.contents[0])

                try:
                    beds_element = card.find('ul', {
                                             'class': 'StyledPropertyCardHomeDetailsList-c11n-8-84-0__sc-1xvdaej-0 ehrLVA'})

                    if beds_element is not None:
                        beds_element = beds_element.find_all(
                            'li')[0].find_all('b')[0]
                        beds = beds_element.text.strip()
                        if beds.isdigit() and float(beds) < 20:
                            beds = float(beds)
                        else:
                            beds = ''
                    else:
                        beds = ''
                except IndexError:
                    beds = ''

                try:
                    bathrooms_element = card.find(
                        'ul', {'class': 'StyledPropertyCardHomeDetailsList-c11n-8-84-0__sc-1xvdaej-0 ehrLVA'})

                    if bathrooms_element is not None:
                        bathrooms_element = bathrooms_element.find_all(
                            'li')[0].find_all('b')[0]
                        bathrooms = bathrooms_element.text.strip()
                        if bathrooms.isdigit() and float(bathrooms) < 20:
                            bathrooms = float(bathrooms)
                        else:
                            bathrooms = ''
                    else:
                        bathrooms = ''
                except IndexError:
                    bathrooms = ''

                price_text = card.find(
                    'span', {'data-test': 'property-card-price'}).text

                # Remove any non-numeric characters from the price_text
                price_value = re.sub('[^\d.]', '', price_text)

                # Check if the price_text has 'M' (representing million)
                if 'M' in price_text:
                    price_value = float(price_value) * 1000000
                else:
                    price_value = float(price_value)

                price = price_value

                # Remove any non-numeric characters from the floorsizeValue
                floorSize = script_json.get('floorSize', {}).get('value', '')
                floorSize_value = re.sub('[^\d.]', '', floorSize)
                if floorSize_value:
                    floorSize = float(floorSize_value)
                else:
                    floorSize = ''

                self.results.append({
                    'id': card.find('article', {'role': 'presentation', 'data-test': 'property-card'})['id'],
                    'soldDate': card.find('span', {'class': 'StyledPropertyCardBadge-c11n-8-84-0__sc-6gojrl-0 kLFrqM'}).text.split(' ')[1],
                    'latitude': script_json.get('geo', {}).get('latitude', ''),
                    'longitude': script_json.get('geo', {}).get('longitude', ''),
                    'floorSize': floorSize,
                    'beds': beds,
                    'bathrooms': bathrooms,
                    'url': script_json.get('url', ''),
                    'address': script_json.get('address', {}).get('streetAddress', ''),
                    'city': script_json.get('address', {}).get('addressLocality', ''),
                    'state': script_json.get('address', {}).get('addressRegion', ''),
                    'zipCode': script_json.get('address', {}).get('postalCode', ''),
                    'price': price,
                })

    def to_csv(self):
        existing_data = pd.read_csv('data/zillow_sold.csv') if os.path.isfile(
            'data/zillow_sold.csv') else pd.DataFrame()
        new_data = pd.DataFrame(self.results)

        updated_data = pd.concat([existing_data, new_data], ignore_index=True)
        updated_data.to_csv('data/zillow_sold.csv', index=False)

    def run(self):
        url = "https://www.zillow.com/fl/sold/"

        for page in range(1, 21):
            # "currentPage": %s
            parameters = {
                "searchQueryState": '{"pagination":{"currentPage": %s},"mapBounds":{"north":26.332365123701646,"east":-80.05526345998386,"south":26.211992671989236,"west":-80.45695108205418},"regionSelection":[{"regionId":1561,"regionType":4},{"regionId":2964,"regionType":4}],"isMapVisible":true,"filterState":{"isForSaleByAgent":{"value":false},"isForSaleByOwner":{"value":false},"isNewConstruction":{"value":false},"isComingSoon":{"value":false},"isAuction":{"value":false},"isForSaleForeclosure":{"value":false},"isRecentlySold":{"value":true},"sortSelection":{"value":"globalrelevanceex"}},"isListVisible":true,"mapZoom":12}' % page
            }
            response_status = self.fetch(url, parameters)
            self.parse(response_status.text)
            time.sleep(2)
            print("Page %s worked!" % page)

        self.to_csv()


if __name__ == "__main__":
    scraper = ZillowSoldScraper()
    scraper.run()
