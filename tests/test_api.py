import pytest_asyncio
import pytest
import config
import requests

  

def test_created_product_returns_201_and_product_detail():
  url = config.get_api_url()
  data = {'name' : 'szarlotka', 'brand' : 'auchan', 'kcal':'200', 'reference_unit':'g'}
  r = requests.post(f'{url}/api/v1/products', json=data)
  assert r.status_code == 201
  product = r.json()
  assert product['name'] == 'szarlotka'

def test_created_product_returns_422_missing_name():
  url = config.get_api_url()
  data = {'brand' : 'auchan', 'kcal':'200', 'reference_unit':'g'}
  r = requests.post(f'{url}/api/v1/products', json=data)
  assert r.status_code == 422
  #json output: {'detail': [{'type': 'missing', 'loc': ['body', 'name'], 'msg': 'Field required', 'input': {'brand': 'auchan', 'kcal': '200', 'reference_unit': 'g'}}]}

def test_created_product_returns_422_null_name():
  url = config.get_api_url()
  data = {'name': None, 'brand' : 'auchan', 'kcal':'200', 'reference_unit':'g'}
  r = requests.post(f'{url}/api/v1/products', json=data)
  assert r.status_code == 422

def test_created_product_returns_422_additional_field():
  url = config.get_api_url()
  data = {'name': 'kefir', 'brand' : 'auchan', 'kcal':'200', 'reference_unit':'g', 'nothing' : 0}
  r = requests.post(f'{url}/api/v1/products', json=data)
  assert r.status_code == 422
