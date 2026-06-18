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

def test_created_product_returns_404_not_existing_category():
  url = config.get_api_url()
  data = {'name': 'jablko', 'brand' : 'auchan', 'kcal':'200', 'reference_unit':'g', 'category_id': 10}
  r = requests.post(f'{url}/api/v1/products', json=data)
  assert r.status_code == 404

def test_created_product_returns_422_with_id():
  url = config.get_api_url()
  data = {'id':4, 'name' : 'szarlotka', 'brand' : 'auchan', 'kcal':'200', 'reference_unit':'g'}
  r = requests.post(f'{url}/api/v1/products', json=data)
  assert r.status_code == 422
  

def insert_product():
  url = config.get_api_url()
  data = {'name' : 'szarlotka', 'brand' : 'auchan', 'kcal':'200', 'reference_unit':'g'}
  r = requests.post(f'{url}/api/v1/products', json=data)
  return r.json()['id']

def test_update_product_returns_200_and_product_detail():
  id = insert_product()
  url = config.get_api_url()
  data = {'brand' : 'XYZ'}
  r = requests.patch(f'{url}/api/v1/products/{id}', json=data)
  assert r.status_code == 200
  product = r.json()
  assert product['name'] == 'szarlotka'
  assert product['brand'] == 'XYZ'

def test_update_product_returns_404_not_existing_category():
  id = insert_product()
  url = config.get_api_url()
  data = {'category_id' : 10}
  r = requests.patch(f'{url}/api/v1/products/{id}', json=data)
  assert r.status_code == 404


def test_update_product_returns_422_additional_field():
  id = insert_product()
  url = config.get_api_url()
  data = {'nothing' : 0}
  r = requests.patch(f'{url}/api/v1/products/{id}', json=data)
  assert r.status_code == 422

def test_update_product_returns_422_null_name():
  id = insert_product()
  url = config.get_api_url()
  data = {'name' : None}
  r = requests.patch(f'{url}/api/v1/products/{id}', json=data)
  assert r.status_code == 422

def test_update_product_returns_404_not_existing_product():
  url = config.get_api_url()
  data = {'name' : 'jogurt'}
  r = requests.patch(f'{url}/api/v1/products/1000', json=data)
  assert r.status_code == 404

def test_update_product_returns_200_correct_id_in_body():
  id = insert_product()
  url = config.get_api_url()
  data = {'id' : f'{id}','name' : 'jogurt'}
  r = requests.patch(f'{url}/api/v1/products/{id}', json=data)
  assert r.status_code == 200

def test_update_product_returns_400_wrong_id_in_body():
  id = insert_product()
  url = config.get_api_url()
  data = {'id' : f'{id + 1}','name' : 'jogurt'}
  r = requests.patch(f'{url}/api/v1/products/{id}', json=data)
  assert r.status_code == 400
  assert r.json()['message'] == 'Bad Request'

def test_update_product_returns_422_empty_body():
  id = insert_product()
  url = config.get_api_url()
  data = {}
  r = requests.patch(f'{url}/api/v1/products/{id}', json=data)
  assert r.status_code == 422
