import requests
from bs4 import BeautifulSoup
import json
import time
import os.path
import pandas as pd
import re


class ZillowHouseForRentScraper():
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

                # Remove any non-numeric characters from the floorsizeValue
                floorSize = script_json.get('floorSize', {}).get('value', '')
                floorSize_value = re.sub('[^\d.]', '', floorSize)
                if floorSize_value:
                    floorSize = float(floorSize_value)
                else:
                    floorSize = ''

                price_text = card.find(
                    'span', {'data-test': 'property-card-price'}).text

                # Remove any non-numeric characters from the price_text
                price_value = re.sub('[^\d.]', '', price_text)

                self.results.append({
                    'id': card.find('article', {'role': 'presentation', 'data-test': 'property-card'})['id'],
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
                    'price': float(price_value),
                })

    def to_csv(self):
        existing_data = pd.read_csv('data/zillow_houseRent.csv') if os.path.isfile(
            'data/zillow_houseRent.csv') else pd.DataFrame()
        new_data = pd.DataFrame(self.results)

        updated_data = pd.concat([existing_data, new_data], ignore_index=True)
        updated_data.to_csv('data/zillow_houseRent.csv', index=False)

    def run(self):
        url = "https://www.zillow.com/homes/for_rent/"

        for page in range(1, 21):
            # "currentPage": %s
            parameters = {
                "searchQueryState": '{"pagination":{"currentPage": %s},"mapBounds":{"north":25.694894332474824,"east":-80.15912362922136,"south":25.573867918567334,"west":-80.56081125129167},"mapZoom":12,"regionSelection":[{"regionId":1561,"regionType":4},{"regionId":2964,"regionType":4}],"isMapVisible":true,"filterState":{"isCondo":{"value":false},"isForSaleForeclosure":{"value":false},"isApartment":{"value":false},"isMultiFamily":{"value":false},"isAllHomes":{"value":true},"isAuction":{"value":false},"isNewConstruction":{"value":false},"isForRent":{"value":true},"isLotLand":{"value":false},"isTownhouse":{"value":false},"isManufactured":{"value":false},"isForSaleByOwner":{"value":false},"isComingSoon":{"value":false},"isApartmentOrCondo":{"value":false},"isForSaleByAgent":{"value":false}},"isListVisible":true}' % page
            }
            response_status = self.fetch(url, parameters)
            self.parse(response_status.text)
            time.sleep(2)
            print("Page %s worked!" % page)

        self.to_csv()


if __name__ == "__main__":
    scraper = ZillowHouseForRentScraper()
    scraper.run()
