import pytest
import requests

import config

def insert_product(name = 'szarlotka', brand='auchan', kcal='200', reference_unit='g', current_category_id=None, cookies=None):
  url = config.get_api_url()
  data = {'name' : name, 'brand_name' : brand, 'nutrition_facts' : {
    'kcal' :kcal,
    'reference_quantity' : {'unit' : reference_unit}
  }, 'img_src': None, 'current_category_id': current_category_id}
  r = requests.post(f'{url}/api/v1/products', json=data, cookies=cookies)
  return r.json()['product_id']

def insert_products(cookies):
  insert_product('Mleko Light', kcal=110,cookies=cookies, current_category_id=203)
  insert_product('Mleko Tłuste', kcal=330,cookies=cookies, current_category_id=203)
  insert_product('Mleko', kcal=220,cookies=cookies, current_category_id=203)
  insert_product('Ciasto Tik', kcal=100,cookies=cookies, current_category_id=204)

@pytest.mark.usefixtures('restart_docker')
def test_create_report(cookies):
  insert_products(cookies)
  url = config.get_api_url()
  data = {
    'product_id' : 1,
    'reported_items' : [
      {
        'reported_field' : 'kcal',
        'proposed_value' : '10',
        'old_value' : '110'
      }
    ]
  }
  r = requests.post(f'{url}/product-reports', json=data, cookies=cookies)
  assert r.status_code == 200
  report = r.json()
  assert report['reported_items'][0]['reported_field'] == 'kcal'
  assert report['reported_items'][0]['status'] == 'accepted'
  assert report['reported_items'][0]['issue_id'] is None #because it will be done in events

@pytest.mark.usefixtures('restart_docker')
def test_create_report_with_outdated_old_value(cookies):
  insert_products(cookies)
  url = config.get_api_url()
  data = {
    'product_id' : 1,
    'reported_items' : [
      {
        'reported_field' : 'kcal',
        'proposed_value' : '10',
        'old_value' : '6767'
      }
    ]
  }
  r = requests.post(f'{url}/product-reports', json=data, cookies=cookies)
  assert r.status_code == 200
  report = r.json()
  assert report['reported_items'][0]['reported_field'] == 'kcal'
  assert report['reported_items'][0]['status'] == 'outdated'
  assert report['reported_items'][0]['issue_id'] is None

@pytest.mark.usefixtures('restart_docker')
def test_create_reports_for_the_same_product_version(cookies):
  insert_products(cookies)
  url = config.get_api_url()
  data = {
    'product_id' : 1,
    'reported_items' : [
      {
        'reported_field' : 'kcal',
        'proposed_value' : '10',
        'old_value' : '110'
      }
    ]
  }
  r = requests.post(f'{url}/product-reports', json=data, cookies=cookies)
  r = requests.post(f'{url}/product-reports', json=data, cookies=cookies)
  assert r.status_code == 409
  assert r.json()['message'] == 'You have already created a report for this product version.'
