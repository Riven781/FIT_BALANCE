from time import sleep
import pytest
import requests
import config

#pytest tests/integration/test_category_hierarchy.py

def create_draft_hierarchy(hierarchy_id, cookies=None):
  url = config.get_api_url()
  r = requests.post(f'{url}/category-hierarchy/{hierarchy_id}/draft', cookies = cookies)
  if r.status_code == 201:
    return r.json()['hierarchy_id']
  else:
    raise RuntimeError()


def get_hierarchy(hierarchy_id, cookies=None):
  url = config.get_api_url()
  r = requests.get(f'{url}/category-hierarchy/{hierarchy_id}', cookies = cookies)
  if r.status_code == 200:
    return r.json()
  elif r.status_code == 404:
    return None
  else:
    raise RuntimeError()

def create_planned_for_publication_hierarchy(cookies=None):
  draft_hierarchy_id = create_draft_hierarchy(101, cookies)
  if draft_hierarchy_id is None:
    raise RuntimeError()
  url = config.get_api_url()
  r = requests.put(f'{url}/category-hierarchy/{draft_hierarchy_id}/plan-for-publication', cookies = cookies)
  if r.status_code == 202:
    sleep(3)
    hierarchy = get_hierarchy(draft_hierarchy_id, cookies)
    if hierarchy['status'] == 'PLANNED_FOR_PUBLICATION':
      return hierarchy['hierarchy_id']
    else:
      raise RuntimeError()
  else:
    raise RuntimeError()


@pytest.mark.usefixtures('restart_docker')
def test_get_hierarchy(cookies):
  url = config.get_api_url()
  r = requests.get(f'{url}/category-hierarchy/101', cookies = cookies)
  assert r.status_code == 200
  hierarchy = r.json()
  assert hierarchy['hierarchy_id'] == 101
  assert len(hierarchy['product_categories']) == 5
  assert hierarchy['status'] == 'ACTIVE'
  cake_category = next(category for category in hierarchy['product_categories'] if category['category_id'] == 204)
  assert cake_category['name'] == 'Ciasto'
  assert cake_category['parent_id'] == 202
  assert cake_category['source_node_id'] is None

@pytest.mark.usefixtures('restart_docker')
def test_edit_active_hierarchy(cookies):
  hierarchy = {
      'existing_categories' : [],
      'draft_categories' : [{ 'name' : 'all', 'parent_id' : None, 'temp_id' : 'id1'}]
  }
  url = config.get_api_url()
  r = requests.put(f'{url}/category-hierarchy/101', cookies = cookies, json=hierarchy)
  assert r.status_code == 409
  assert r.json()['message'] == "Only draft can be edited."

@pytest.mark.usefixtures('restart_docker')
def test_create_draft_hierarchy(cookies):
  url = config.get_api_url()
  r = requests.post(f'{url}/category-hierarchy/101/draft', cookies = cookies)
  assert r.status_code == 201
  hierarchy = r.json()
  assert len(hierarchy['product_categories']) == 5
  assert hierarchy['status'] == 'DRAFT'
  cake_category = next(category for category in hierarchy['product_categories'] if category['name'] == 'Ciasto')
  assert cake_category['name'] == 'Ciasto'
  assert cake_category['source_node_id'] == 204

@pytest.mark.usefixtures('restart_docker')
def test_create_draft_hierarchy_based_on_draft_hierarchy(cookies):
  draft_hierarchy_id = create_draft_hierarchy(101, cookies)
  url = config.get_api_url()
  r = requests.post(f'{url}/category-hierarchy/{draft_hierarchy_id}/draft', cookies = cookies)
  assert r.status_code == 409
  hierarchy = r.json()
  assert hierarchy['message'] == "Draft hierarchy already exists."

@pytest.mark.usefixtures('restart_docker')
def test_create_draft_hierarchy_based_on_planned_for_publication_hierarchy(cookies):
  planned_hierarchy_id = create_planned_for_publication_hierarchy(cookies)
  url = config.get_api_url()
  r = requests.post(f'{url}/category-hierarchy/{planned_hierarchy_id}/draft', cookies = cookies)
  assert r.status_code == 409
  hierarchy = r.json()
  assert hierarchy['message'] == "Draft only can be created based on active category."


@pytest.mark.usefixtures('restart_docker')
def test_edit_draft_hierarchy(cookies):
  draft_hierarchy_id = create_draft_hierarchy(101, cookies)
  new_hierarchy = {
      'existing_categories' : [],
      'draft_categories' : [{ 'name' : 'all', 'parent_id' : None, 'temp_id' : 'id1'}]
  }
  url = config.get_api_url()
  r = requests.put(f'{url}/category-hierarchy/{draft_hierarchy_id}', cookies = cookies, json=new_hierarchy)
  assert r.status_code == 200
  hierarchy = r.json()
  assert hierarchy['hierarchy_id'] == draft_hierarchy_id
  assert len(hierarchy['product_categories']) == 1
  assert hierarchy['status'] == 'DRAFT'
  all_category = next(category for category in hierarchy['product_categories'] if category['name'] == 'all')
  assert all_category['parent_id'] is None
  assert all_category['category_id'] is not None

@pytest.mark.usefixtures('restart_docker')
def test_edit_active_hierarchy(cookies):
  new_hierarchy = {
      'existing_categories' : [],
      'draft_categories' : [{ 'name' : 'all', 'parent_id' : None, 'temp_id' : 'id1'}]
  }
  url = config.get_api_url()
  r = requests.put(f'{url}/category-hierarchy/101', cookies = cookies, json=new_hierarchy)
  assert r.status_code == 409
  hierarchy = r.json()
  assert hierarchy['message'] == "Only draft can be edited."

@pytest.mark.usefixtures('restart_docker')
def test_edit_planned_for_publication_hierarchy(cookies):
  planned_hierarchy_id = create_planned_for_publication_hierarchy(cookies)
  new_hierarchy = {
      'existing_categories' : [],
      'draft_categories' : [{ 'name' : 'all', 'parent_id' : None, 'temp_id' : 'id1'}]
  }
  url = config.get_api_url()
  r = requests.put(f'{url}/category-hierarchy/{planned_hierarchy_id}', cookies = cookies, json=new_hierarchy)
  assert r.status_code == 409
  hierarchy = r.json()
  assert hierarchy['message'] == "Only draft can be edited."
   

@pytest.mark.usefixtures('restart_docker')
def test_delete_draft_hierarchy(cookies):
  draft_hierarchy_id = create_draft_hierarchy(101, cookies)
  url = config.get_api_url()
  r = requests.delete(f'{url}/category-hierarchy/{draft_hierarchy_id}', cookies = cookies)
  assert r.status_code == 204
  hierarchy = get_hierarchy(draft_hierarchy_id, cookies)
  assert hierarchy is None

@pytest.mark.usefixtures('restart_docker')
def test_delete_active_hierarchy(cookies):
  url = config.get_api_url()
  r = requests.delete(f'{url}/category-hierarchy/101', cookies = cookies)
  assert r.status_code == 409
  assert r.json()['message'] == 'Only draft category can be deleted.'

@pytest.mark.usefixtures('restart_docker')
def test_delete_planned_hierarchy(cookies):
  planned_hierarchy_id = create_planned_for_publication_hierarchy(cookies)
  url = config.get_api_url()
  r = requests.delete(f'{url}/category-hierarchy/{planned_hierarchy_id}', cookies = cookies)
  assert r.status_code == 409
  assert r.json()['message'] == 'Only draft category can be deleted.'

@pytest.mark.usefixtures('restart_docker')
def test_plan_hierarchy_for_publication(cookies):
  draft_hierarchy_id = create_draft_hierarchy(101, cookies)
  url = config.get_api_url()
  r = requests.put(f'{url}/category-hierarchy/{draft_hierarchy_id}/plan-for-publication', cookies = cookies)
  assert r.status_code == 202
  hierarchy = get_hierarchy(draft_hierarchy_id, cookies)
  assert hierarchy['status'] == 'PLANNING_FOR_PUBLICATION'

@pytest.mark.usefixtures('restart_docker')
def test_plan_active_hierarchy_for_publication(cookies):
  url = config.get_api_url()
  r = requests.put(f'{url}/category-hierarchy/101/plan-for-publication', cookies = cookies)
  assert r.status_code == 409
  assert r.json()['message'] == 'Only draft can be planned for publication.'

@pytest.mark.usefixtures('restart_docker')
def test_plan_planned_hierarchy_for_publication(cookies):
  planned_hierarchy_id = create_planned_for_publication_hierarchy(cookies)
  url = config.get_api_url()
  r = requests.put(f'{url}/category-hierarchy/{planned_hierarchy_id}/plan-for-publication', cookies = cookies)
  assert r.status_code == 409
  assert r.json()['message'] == 'Only draft can be planned for publication.'

@pytest.mark.usefixtures('restart_docker')
def test_plan_hierarchy_for_publication_with_sleep(cookies):
  draft_hierarchy_id = create_draft_hierarchy(101, cookies)
  url = config.get_api_url()
  r = requests.put(f'{url}/category-hierarchy/{draft_hierarchy_id}/plan-for-publication', cookies = cookies)
  assert r.status_code == 202
  sleep(3)
  hierarchy = get_hierarchy(draft_hierarchy_id, cookies)
  assert hierarchy['status'] == 'PLANNED_FOR_PUBLICATION'
  
@pytest.mark.usefixtures('restart_docker')
def test_revert_to_draft(cookies):
  planned_hierarchy_id = create_planned_for_publication_hierarchy(cookies)
  url = config.get_api_url()
  r = requests.put(f'{url}/category-hierarchy/{planned_hierarchy_id}/draft', cookies = cookies)
  assert r.status_code == 204
  hierarchy = get_hierarchy(planned_hierarchy_id, cookies)
  assert hierarchy['status'] == 'DRAFT'

@pytest.mark.usefixtures('restart_docker')
def test_revert_active_hierarchy_to_draft(cookies):
  url = config.get_api_url()
  r = requests.put(f'{url}/category-hierarchy/101/draft', cookies = cookies)
  assert r.status_code == 409
  assert r.json()['message'] == "Only planned for publication hierarchy can be reverted to draft."

@pytest.mark.usefixtures('restart_docker')
def test_revert_draft_hierarchy_to_draft(cookies):
  draft_hierarchy_id = create_draft_hierarchy(101, cookies)
  url = config.get_api_url()
  r = requests.put(f'{url}/category-hierarchy/{draft_hierarchy_id}/draft', cookies = cookies)
  assert r.status_code == 204

@pytest.mark.usefixtures('restart_docker')
def test_publish_hierarchy(cookies):
  planned_hierarchy_id = create_planned_for_publication_hierarchy(cookies)
  url = config.get_api_url()
  r = requests.put(f'{url}/category-hierarchy/{planned_hierarchy_id}/publish', cookies = cookies)
  assert r.status_code == 204
  hierarchy = get_hierarchy(planned_hierarchy_id, cookies)
  assert hierarchy['status'] == 'ACTIVE'

@pytest.mark.usefixtures('restart_docker')
def test_publish_draft_hierarchy(cookies):
  draft_hierarchy_id = create_draft_hierarchy(101, cookies)
  url = config.get_api_url()
  r = requests.put(f'{url}/category-hierarchy/{draft_hierarchy_id}/publish', cookies = cookies)
  assert r.status_code == 409
  assert r.json()['message'] == "Only planned for publication can be published."