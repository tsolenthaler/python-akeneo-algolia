from os import getenv
import json
import sys
from akeneo import akeneo
from algoliasearch.search_client import SearchClient
from algoliasearch.configs import SearchConfig
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

AKENEO_HOST = getenv('AKENEO_HOST')
AKENEO_CLIENT_ID = getenv('AKENEO_CLIENT_ID')
AKENEO_CLIENT_SECRET = getenv('AKENEO_CLIENT_SECRET')
AKENEO_USERNAME = getenv('AKENEO_USERNAME')
AKENEO_PASSWORD = getenv('AKENEO_PASSWORD')
ALGOLIA_APP_ID = getenv('ALGOLIA_APP_ID')
ALGOLIA_API_KEY = getenv('ALGOLIA_API_KEY')
ALGOLIA_INDEX_NAME = getenv('ALGOLIA_INDEX_NAME')

## Exract Data from Akeneo
def getDatafromAkeneo():
    client = akeneo.Akeneo(AKENEO_HOST, AKENEO_CLIENT_ID, AKENEO_CLIENT_SECRET, AKENEO_USERNAME, AKENEO_PASSWORD)
    products = client.getProducts('{"enabled":[{"operator":"=","value":true}],"family":[{"operator":"IN","value":["Place"]}],"completeness":[{"operator":"=","value":100,"scope":"ecommerce"}]}')
    return products

## Mapping / Transform Data / test
def transformData(products):
    importProducts = []
    i = 0
    for product in products:
        print(product['identifier'])
        importProduct = {}
        importProduct['objectID'] = product['identifier']
        importProduct['name'] = product['values']['name'][0]['data']
        if 'description' in product['values']:
            importProduct['description'] = product['values']['description'][0]['data']
        if 'disambiguatingDescription' in product['values']:
            importProduct['disambiguatingDescription'] = product['values']['disambiguatingDescription'][0]['data']
        if 'image' in product['values']:
            importProduct['image'] = product['values']['image'][0]['data']
        if 'categories' in product:
            importProduct['categories'] = product['categories']
        if 'family' in product:
            importProduct['type'] = product['family']
        if 'groups' in product:
            importProduct['groups'] = product['groups']
        if 'latitude' in product['values']:
            latitude = product['values']['latitude'][0]['data']
        if 'longitude' in product['values']:
            longitude = product['values']['longitude'][0]['data']
            importProduct['_geoloc'] = {
                "lat": float(latitude),
                "lng": float(longitude)
            }
        if 'addressLocality' in product['values']:
            importProduct['city'] = product['values']['addressLocality'][0]['data']
        if 'addressCountry' in product['values']:
            importProduct['country'] = product['values']['addressCountry'][0]['data']
        if 'season' in product['values']:
            importProduct['season'] = product['values']['season'][0]['data']
        if 'duration' in product['values']:
            importProduct['duration'] = product['values']['duration'][0]['data']
        if 'priceRange' in product['values']:
            importProduct['priceRange'] = product['values']['priceRange'][0]['data']
        if 'indoor_outdoor' in product['values']:
            importProduct['indoor_outdoor'] = product['values']['indoor_outdoor'][0]['data']
        if 'ost_suitable_for' in product['values']:
            importProduct['ost_suitable_for'] = product['values']['ost_suitable_for'][0]['data']
        if 'ost_claim' in product['values']:
            importProduct['ost_claim'] = product['values']['ost_claim'][0]['data']
        if 'url' in product['values']:
            importProduct['url'] = product['values']['url'][0]['data']
        importProducts.append(importProduct)
        i += 1
    return importProducts

## LOAD - Import Data to Algolia
def importDataToAlgolia(importProducts):
    config = SearchConfig(ALGOLIA_APP_ID, ALGOLIA_API_KEY)
    config.batch_size = 999999

    # Connect and authenticate with your Algolia app
    #client = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_API_KEY)
    client = SearchClient.create_with_config(config)

    # Create a new index and add a record
    index = client.init_index(ALGOLIA_INDEX_NAME)

    index.set_settings({
        'searchableAttributes': [
            'name',
            'categories',
            'unordered(description)'
        ],
        'customRanking': [
            'desc(popularity)'
        ],
        'attributesForFaceting': [
            'type',
            'searchable(categories)',
            'groups',
            'city',
            'country',
            'season',
            'duration.amount',
            'duration.unit'
            'priceRange',
            'indoor_outdoor',
            'ost_suitable_for',
            'ost_claim'
        ]
    })
    # Save the object
    index.save_objects(importProducts)

def savetoFile(products):
    with open('../public/importProducts.json', 'w') as outfile:
        json.dump(products, outfile)

def __main__():
    print("Start Import to Algolia")
    print(f"Arguments count: {len(sys.argv)}")
    for i, arg in enumerate(sys.argv):
        print(f"Argument {i:>6}: {arg}")
    products = getDatafromAkeneo()
    importProducts = transformData(products)
    savetoFile(importProducts)
    importDataToAlgolia(importProducts)

if __name__== "__main__":
    __main__()