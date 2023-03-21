from os import getenv
import json
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


# Create a client
client = akeneo.Akeneo(AKENEO_HOST, 
                AKENEO_CLIENT_ID, 
                AKENEO_CLIENT_SECRET, 
                AKENEO_USERNAME, 
                AKENEO_PASSWORD)

# Get a list of products
product = client.getProductByCode('dedf67a1-2e33-49a0-ad6c-b3bb91049167')
products = client.getProducts('{"categories":[{"operator":"IN","value":["Place"]}]}')
#product['objectID'] = product['identifier']
for index, product in enumerate(products):
    products[index]['objectID'] = product['identifier']

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
    importProduct['image'] = product['values']['image'][0]['data']
    print(importProduct)
    importProducts.append(importProduct)
    i += 1
    
#print(products)

config = SearchConfig(ALGOLIA_APP_ID, ALGOLIA_API_KEY)
config.batch_size = 999999

# Connect and authenticate with your Algolia app
#client = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_API_KEY)
client = SearchClient.create_with_config(config)

# Create a new index and add a record
index = client.init_index(ALGOLIA_INDEX_NAME)

print(importProducts)
with open('result.json', 'w') as fp:
    json.dump(importProducts, fp)

#index.save_object(product).wait()
index.save_objects(importProducts)

# Search the index and print the results
#results = index.search("TSO AG")
#print(results["hits"][0])