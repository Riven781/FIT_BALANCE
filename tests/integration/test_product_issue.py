from time import sleep

import pytest
import requests

import config
#pytest tests/integration/test_product_issue.py 

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


def create_report(cookies, product_id=1, reported_field= 'kcal', proposed_value=None, old_value=None):
  insert_products(cookies)
  url = config.get_api_url()
  data = {
    'product_id' : product_id,
    'reported_items' : [
      {
        'reported_field' : reported_field,
        'proposed_value' : proposed_value,
        'old_value' : old_value
      }
    ]
  }
  r = requests.post(f'{url}/product-reports', json=data, cookies=cookies)
  if r.status_code != 201:
    raise RuntimeError()
  
def get_product(product_id):
  url = config.get_api_url()
  r = requests.get(f'{url}/api/v1/products/{product_id}/test')
  if r.status_code == 200:
    return r.json()
  else:
    raise RuntimeError()


def confirm_issue(cookies):
  create_report(cookies, reported_field='kcal', proposed_value='10', old_value='110')
  sleep(1)
  url = config.get_api_url()
  data = {
    'resolved_value' : 100
  }
  r = requests.put(f'{url}/product-issues/1/confirm', json=data, cookies=cookies)
  if r.status_code != 202:
    raise RuntimeError()
  else:
    return r.json()

def reject_issue(cookies):
  create_report(cookies, reported_field='kcal', proposed_value='10', old_value='110')
  sleep(1)
  url = config.get_api_url()

  r = requests.put(f'{url}/product-issues/1/reject', cookies=cookies)
  if r.status_code != 200:
    raise RuntimeError()
  else:
    return r.json()

@pytest.mark.usefixtures('restart_docker')
def test_confirm_kcal_issue(cookies):
  create_report(cookies, reported_field='kcal', proposed_value='10', old_value='110')
  sleep(1)
  url = config.get_api_url()
  data = {
    'resolved_value' : 100
  }
  r = requests.put(f'{url}/product-issues/1/confirm', json=data, cookies=cookies)
  issue = r.json()
  assert r.status_code == 202
  assert issue['product_id'] == 1
  assert issue['reported_field'] == 'kcal'
  assert issue['resolved_value'] == 100
  assert issue['old_value'] == 110
  sleep(2)
  product = get_product(issue['product_id'])
  assert product['nutrition_facts']['kcal'] == 100


@pytest.mark.usefixtures('restart_docker')
def test_confirm_name_issue(cookies):
  create_report(cookies, reported_field='name', proposed_value='10', old_value='Mleko Light')
  sleep(1)
  url = config.get_api_url()
  data = {
    'resolved_value' : 'Mleko Lekkie'
  }
  r = requests.put(f'{url}/product-issues/1/confirm', json=data, cookies=cookies)
  issue = r.json()
  assert r.status_code == 202
  assert issue['product_id'] == 1
  assert issue['reported_field'] == 'name'
  assert issue['resolved_value'] == 'Mleko Lekkie'
  assert issue['old_value'] == 'Mleko Light'
  sleep(2)
  product = get_product(issue['product_id'])
  assert product['name'] == 'Mleko Lekkie'

@pytest.mark.usefixtures('restart_docker')
def test_confirm_not_existing_issue(cookies):
  url = config.get_api_url()
  data = {
    'resolved_value' : 'Mleko Lekkie'
  }
  r = requests.put(f'{url}/product-issues/6767/confirm', json=data, cookies=cookies)
  assert r.status_code == 404
  assert r.json()['message'] == 'Product Issue not found.'

@pytest.mark.usefixtures('restart_docker')
def test_confirm_rejected_issue(cookies):
  issue = reject_issue(cookies)
  sleep(3)
  url = config.get_api_url()
  data = {
    'resolved_value' : 'Mleko Lekkie'
  }
  r = requests.put(f'{url}/product-issues/{issue["issue_id"]}/confirm', json=data, cookies=cookies)
  assert r.status_code == 409
  assert r.json()['message'] == 'Issue cannot be confirmed.'


@pytest.mark.usefixtures('restart_docker')
def test_reject_issue(cookies):
  create_report(cookies, reported_field='kcal', proposed_value='10', old_value='110')
  sleep(1)
  url = config.get_api_url()
  r = requests.put(f'{url}/product-issues/1/reject', cookies=cookies)
  issue = r.json()
  assert r.status_code == 200
  assert issue['product_id'] == 1
  assert issue['reported_field'] == 'kcal'
  assert issue['resolved_value'] is None
  assert issue['old_value'] == 110

@pytest.mark.usefixtures('restart_docker')
def test_reject_not_existing_issue(cookies):
  url = config.get_api_url()
  data = {
    'resolved_value' : 'Mleko Lekkie'
  }
  r = requests.put(f'{url}/product-issues/6767/reject', json=data, cookies=cookies)
  assert r.status_code == 404
  assert r.json()['message'] == 'Product Issue not found.'

@pytest.mark.usefixtures('restart_docker')
def test_reject_confirmed_issue(cookies):
  issue = confirm_issue(cookies)
  sleep(3)
  url = config.get_api_url()
  r = requests.put(f'{url}/product-issues/{issue["issue_id"]}/reject',  cookies=cookies)
  assert r.status_code == 409
  assert r.json()['message'] == 'Issue cannot be rejected.'



