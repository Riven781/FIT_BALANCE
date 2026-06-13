import pytest_asyncio
import pytest
import config
import requests

def wait_for_webapp_to_come_up():
  url = config.get_api_url()
  

def test_created_product_returns_201_and_product_detail():
  url = config.get_api_url()
  data = {'name' : 'szarlotka', 'brand' : 'auchan', 'kcal':'200', 'reference_unit':'g', }
  r = requests.post(f'{url}/api/v1/products', json=data)
  assert r.status_code == 201
  product = r.json()
  assert product['name'] == 'szarlotka'

