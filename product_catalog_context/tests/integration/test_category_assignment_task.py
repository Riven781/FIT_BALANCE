from time import sleep

import pytest
import requests

import config
#tests/integration/test_category_assignment_task.py

def get_hierarchy(hierarchy_id, cookies=None):
  url = config.get_api_url()
  r = requests.get(f'{url}/category-hierarchy/{hierarchy_id}', cookies = cookies)
  if r.status_code == 200:
    return r.json()
  elif r.status_code == 404:
    return None
  else:
    raise RuntimeError()

def assign_tasks(user_id, hierarchy_id, current_category_id=204, cookies=None):
  
  insert_products(cookies=cookies)
  request = {
    'current_category_id' : current_category_id,
    'hierarchy_id': hierarchy_id,
    'limit': 10
  }
  url = config.get_api_url()
  r = requests.post(f'{url}/users/{user_id}/category-assignment-tasks', json=request, cookies=cookies)
  if r.status_code != 204:
    raise RuntimeError()

def create_draft_hierarchy(hierarchy_id, cookies=None):
  url = config.get_api_url()
  r = requests.post(f'{url}/category-hierarchy/{hierarchy_id}/draft', cookies = cookies)
  if r.status_code == 201:
    return r.json()['hierarchy_id']
  else:
    raise RuntimeError()
  
def create_planned_for_publication_hierarchy(cookies=None):
  draft_hierarchy_id = create_draft_hierarchy(101, cookies)
  if draft_hierarchy_id is None:
    raise RuntimeError()
  url = config.get_api_url()
  r = requests.put(f'{url}/category-hierarchy/{draft_hierarchy_id}/plan-for-publication', cookies = cookies)
  if r.status_code == 202:
    sleep(4)
    hierarchy = get_hierarchy(draft_hierarchy_id, cookies)
    if hierarchy['status'] == 'PLANNED_FOR_PUBLICATION':
      return hierarchy['hierarchy_id']
    else:
      raise RuntimeError()
  else:
    raise RuntimeError()

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

def get_task(task_id, cookies):
  url = config.get_api_url()
  r = requests.get(f'{url}/category-assignment-tasks/{task_id}', cookies=cookies)
  if r.status_code == 200:
    return r.json()
  else:
    return None

def get_product(product_id):
  url = config.get_api_url()
  r = requests.get(f'{url}/api/v1/products/{product_id}/test')
  if r.status_code == 200:
    return r.json()
  else:
    raise RuntimeError()

def publish_hierarchy(hierarchy_id, cookies):
  url = config.get_api_url()
  r = requests.put(f'{url}/category-hierarchy/{hierarchy_id}/publish', cookies = cookies)
  if r.status_code != 204:
    raise RuntimeError()




@pytest.mark.usefixtures('restart_docker')
def test_assign_tasks_for_user_by_active_category_id(cookies):
  hierarchy_id = create_planned_for_publication_hierarchy(cookies)
  request = {
    'current_category_id' : 204,
    'hierarchy_id': hierarchy_id,
    'limit': 10
  }
  url = config.get_api_url()
  r = requests.post(f'{url}/users/2000/category-assignment-tasks', json=request, cookies=cookies)
  assert r.status_code == 204

@pytest.mark.usefixtures('restart_docker')
def test_assign_tasks_for_user_by_active_category_id_when_products_exist(cookies):
  hierarchy_id = create_planned_for_publication_hierarchy(cookies) #if insert_productsis before this line planning for publication copy product assignments...
  insert_products(cookies=cookies)
  request = {
    'current_category_id' : 204,
    'hierarchy_id': hierarchy_id,
    'limit': 10
  }
  url = config.get_api_url()
  r = requests.post(f'{url}/users/2000/category-assignment-tasks', json=request, cookies=cookies)
  assert r.status_code == 204
  task = get_task(1, cookies=cookies)
  assert task is not None
  assert task['user_id'] == 2000
@pytest.mark.usefixtures('restart_docker')

def test_assign_tasks_for_user_by_active_category_id_in_draft_hierarchy(cookies):
  hierarchy_id = create_draft_hierarchy(hierarchy_id=101, cookies=cookies)
  request = {
    'current_category_id' : 204,
    'hierarchy_id': hierarchy_id,
    'limit': 10
  }
  url = config.get_api_url()
  r = requests.post(f'{url}/users/2000/category-assignment-tasks', json=request, cookies=cookies)
  assert r.status_code == 409
  assert r.json()['message'] == 'Hierarchy must be planned for publication.'

@pytest.mark.usefixtures('restart_docker')
def test_assign_tasks_for_user_by_active_category_id_in_active_hierarchy(cookies):
  request = {
    'current_category_id' : 204,
    'hierarchy_id': 101,
    'limit': 10
  }
  url = config.get_api_url()
  r = requests.post(f'{url}/users/2000/category-assignment-tasks', json=request, cookies=cookies)
  assert r.status_code == 409
  assert r.json()['message'] == 'Hierarchy must be planned for publication.'

@pytest.mark.usefixtures('restart_docker')
def test_assign_tasks_for_user_by_active_category_id_not_existing_user(cookies):
  hierarchy_id = create_planned_for_publication_hierarchy(cookies)
  request = {
    'current_category_id' : 204,
    'hierarchy_id': hierarchy_id,
    'limit': 10
  }
  url = config.get_api_url()
  r = requests.post(f'{url}/users/6767/category-assignment-tasks', json=request, cookies=cookies)
  assert r.status_code == 422


@pytest.mark.usefixtures('restart_docker')
def test_allocate_tasks_for_users(cookies):
  hierarchy_id = create_planned_for_publication_hierarchy(cookies) #if insert_productsis before this line planning for publication copy product assignments...
  insert_products(cookies=cookies)
  request = {
    'editor_ids' : [2000, 3000],
    'hierarchy_id': hierarchy_id
  }
  url = config.get_api_url()
  r = requests.post(f'{url}/category-assignment-task-allocation', json=request, cookies=cookies)
  assert r.status_code == 204
  task = get_task(1, cookies=cookies)
  assert task is not None

@pytest.mark.usefixtures('restart_docker')
def test_allocate_tasks_for_users_in_draft_hierarchy(cookies):
  hierarchy_id = create_draft_hierarchy(hierarchy_id=101, cookies=cookies)
  insert_products(cookies=cookies)
  request = {
    'editor_ids' : [2000, 3000],
    'hierarchy_id': hierarchy_id
  }
  url = config.get_api_url()
  r = requests.post(f'{url}/category-assignment-task-allocation', json=request, cookies=cookies)
  assert r.status_code == 409
  assert r.json()['message'] == 'Hierarchy must be planned for publication.'

@pytest.mark.usefixtures('restart_docker')
def test_allocate_tasks_for_users_in_active_hierarchy(cookies):
  insert_products(cookies=cookies)
  request = {
    'editor_ids' : [2000, 3000],
    'hierarchy_id': 101
  }
  url = config.get_api_url()
  r = requests.post(f'{url}/category-assignment-task-allocation', json=request, cookies=cookies)
  assert r.status_code == 409
  assert r.json()['message'] == 'Hierarchy must be planned for publication.'


@pytest.mark.usefixtures('restart_docker')
def test_complete_task(cookies):
  hierarchy_id = create_planned_for_publication_hierarchy(cookies)
  assign_tasks(user_id=1000, hierarchy_id=hierarchy_id, cookies=cookies)
  hierarchy = get_hierarchy(hierarchy_id, cookies)
  category_id = next(category['category_id'] for category in hierarchy['product_categories'] if category['source_node_id'] == 203)
  request={
    'category_id': category_id
  }
  url = config.get_api_url()
  r = requests.put(f'{url}/category-assignment-tasks/1/complete', json=request, cookies=cookies)
  assert r.status_code == 204
  task = get_task(1, cookies=cookies)
  assert task['status'] == 'COMPLETED'
  publish_hierarchy(hierarchy_id, cookies)
  product = get_product(task['product_id'])
  print(product)
  assert product['category_assignments'][str(hierarchy_id)]['category_id'] == category_id

@pytest.mark.usefixtures('restart_docker')
def test_complete_not_existing_task(cookies):
  request={
    'category_id': 120
  }
  url = config.get_api_url()
  r = requests.put(f'{url}/category-assignment-tasks/100/complete', json=request, cookies=cookies)
  assert r.status_code == 404
  assert r.json()['message'] == 'Task does not exist.'


@pytest.mark.usefixtures('restart_docker')
def test_complete_task_in_active_hierarchy(cookies):
  hierarchy_id = create_planned_for_publication_hierarchy(cookies)
  assign_tasks(user_id=1000, hierarchy_id=hierarchy_id, cookies=cookies)
  hierarchy = get_hierarchy(hierarchy_id, cookies)
  publish_hierarchy(hierarchy_id, cookies)
  category_id = next(category['category_id'] for category in hierarchy['product_categories'] if category['source_node_id'] == 203)
  request={
    'category_id': category_id
  }
  url = config.get_api_url()
  r = requests.put(f'{url}/category-assignment-tasks/1/complete', json=request, cookies=cookies)
  assert r.status_code == 409
  assert r.json()['message'] == 'Hierarchy must be planned for publication.'

@pytest.mark.usefixtures('restart_docker')
def test_delete_task(cookies):
  hierarchy_id = create_planned_for_publication_hierarchy(cookies)
  assign_tasks(user_id=1000, hierarchy_id=hierarchy_id, cookies=cookies)
  url = config.get_api_url()
  r = requests.delete(f'{url}/category-assignment-tasks/1', cookies=cookies)
  assert r.status_code == 204
  task = get_task(1, cookies=cookies)
  assert task is None 

@pytest.mark.usefixtures('restart_docker')
def test_delete_not_existing_task(cookies):
  url = config.get_api_url()
  r = requests.delete(f'{url}/category-assignment-tasks/6767', cookies=cookies)
  assert r.status_code == 404
  assert r.json()['message'] == 'Task does not exist.'

@pytest.mark.usefixtures('restart_docker')
def test_delete_tasks_by_user(cookies):
  hierarchy_id = create_planned_for_publication_hierarchy(cookies)
  assign_tasks(user_id=1000, hierarchy_id=hierarchy_id, cookies=cookies)
  url = config.get_api_url()
  r = requests.delete(f'{url}/users/1000/category-assignment-tasks', cookies=cookies)
  assert r.status_code == 204
  task = get_task(1, cookies=cookies)
  assert task is None

@pytest.mark.usefixtures('restart_docker')
def test_delete_not_rxisting_tasks_by_user(cookies):
  url = config.get_api_url()
  r = requests.delete(f'{url}/users/1000/category-assignment-tasks', cookies=cookies)
  assert r.status_code == 404
  assert r.json()['message'] == 'Task does not exist.'

@pytest.mark.usefixtures('restart_docker')
def test_delete_tasks_by_user_and_product(cookies):
  hierarchy_id = create_planned_for_publication_hierarchy(cookies)
  assign_tasks(user_id=1000, hierarchy_id=hierarchy_id, cookies=cookies)
  task = get_task(1, cookies=cookies)
  url = config.get_api_url()
  r = requests.delete(f'{url}/users/1000/category-assignment-tasks/products/{task["product_id"]}', cookies=cookies)
  assert r.status_code == 204

@pytest.mark.usefixtures('restart_docker')
def test_delete_not_existing_tasks_by_user_and_product(cookies):
  url = config.get_api_url()
  r = requests.delete(f'{url}/users/1000/category-assignment-tasks/products/6767', cookies=cookies)
  assert r.status_code == 404
  assert r.json()['message'] == 'Task does not exist.'
