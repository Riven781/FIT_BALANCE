import pytest_asyncio
import pytest
import config
import requests

#docker compose up api-test

@pytest.mark.usefixtures('restart_docker')
def test_created_product_returns_201_and_product_detail(cookies):
  url = config.get_api_url()
  data = {'name' : 'szarlotka', 'brand_name' : 'auchan', 'nutrition_facts' : {
    'kcal' :230,
  }, 'img_src': None}
  r = requests.post(f'{url}/api/v1/products', json=data, cookies=cookies)
  assert r.status_code == 201
  product = r.json()
  assert product['name'] == 'szarlotka'


@pytest.mark.usefixtures('restart_docker')
def test_created_product_returns_422_missing_name(cookies):
  url = config.get_api_url()
  data = {'brand_name' : 'auchan', 'nutrition_facts' : {
    'kcal' :230,
  }, 'img_src': None}
  r = requests.post(f'{url}/api/v1/products', json=data, cookies=cookies)
  assert r.status_code == 422
  #json output: {'detail': [{'type': 'missing', 'loc': ['body', 'name'], 'msg': 'Field required', 'input': {'brand': 'auchan', 'kcal': '200', 'reference_unit': 'g'}}]}

@pytest.mark.usefixtures('restart_docker')
def test_created_product_returns_422_null_name(cookies):
  url = config.get_api_url()
  data = {'name': None, 'brand_name' : 'auchan', 'nutrition_facts' : {
    'kcal' :230,
  }, 'img_src': None}
  r = requests.post(f'{url}/api/v1/products', json=data, cookies=cookies)
  assert r.status_code == 422

@pytest.mark.usefixtures('restart_docker')
def test_created_product_returns_422_additional_field(cookies):
  url = config.get_api_url()
  data = {'name': None, 'brand_name' : 'auchan', 'nutrition_facts' : {
      'kcal' :230,
    }, 'img_src': None, 'nothing' : 0}
  r = requests.post(f'{url}/api/v1/products', json=data, cookies=cookies)
  assert r.status_code == 422

@pytest.mark.usefixtures('restart_docker')
def test_created_product_returns_404_not_existing_category(cookies):
  url = config.get_api_url()
  data = {'name' : 'jablko', 'brand_name' : 'auchan', 'nutrition_facts' : {
      'kcal' : 230,
  }, 'img_src': None, 'current_category_id': 10}
  r = requests.post(f'{url}/api/v1/products', json=data, cookies=cookies)
  assert r.status_code == 422


@pytest.mark.usefixtures('restart_docker')
def test_created_product_returns_422_with_id(cookies):
  url = config.get_api_url()
  data = {'id': 4,'name' : 'szarlotka', 'brand_name' : 'auchan', 'nutrition_facts' : {
      'kcal' : 230,
  }, 'img_src': None, 'current_category_id': 10}
  r = requests.post(f'{url}/api/v1/products', json=data, cookies=cookies)
  assert r.status_code == 422

def insert_product(name = 'szarlotka', brand='auchan', kcal='200', reference_unit='g', cookies=None):
  url = config.get_api_url()
  data = {'name' : name, 'brand_name' : brand, 'nutrition_facts' : {
    'kcal' :kcal,
    'reference_quantity' : {'unit' : reference_unit}
  }, 'img_src': None}
  r = requests.post(f'{url}/api/v1/products', json=data, cookies=cookies)
  return r.json()['product_id']

@pytest.mark.usefixtures('restart_docker')
def test_update_product_returns_200_and_product_detail(cookies):
  id = insert_product(cookies=cookies)
  url = config.get_api_url()
  assert len(requests.get(f'{url}/api/v1/products').json()['data']) == 1 #TEEEEEEST
  data = {'name' : 'szarlotka', 'brand_name' : 'XYZ', 'nutrition_facts' : {
      'kcal' :'200',
      'reference_quantity' : {'unit' : 'g', 'amount': 100},
      'nutrients': {
        'fat': None,
        'saturates': None,
        'carbohydrates': None,
        'sugars': None,
        'protein': None,
        'salt':None,
        'fiber':None}
    }, 'img_src': None, 'current_category_id': None, 'planned_category_id': None, 'ingredients': None, 'allergy_recommendations': None}
  r = requests.put(f'{url}/api/v1/products/{id}', json=data, cookies=cookies)
  print(r.json())
  assert r.status_code == 200
  product = r.json()
  assert product['name'] == 'szarlotka'
  assert product['brand_name'] == 'XYZ'

@pytest.mark.usefixtures('restart_docker')
def test_update_product_nutrients_returns_200_and_product_detail(cookies):
  id = insert_product(cookies=cookies)
  url = config.get_api_url()

  assert len(requests.get(f'{url}/api/v1/products').json()['data']) == 1 #TEEEEEEST
  data = {'name' : 'szarlotka', 'brand_name' : 'auchan', 'nutrition_facts' : {
      'kcal' :'200',
      'reference_quantity' : {'unit' : 'g', 'amount': 100},
      'nutrients': {
        'fat': None,
        'saturates': None,
        'carbohydrates': None,
        'sugars': 20,
        'protein': None,
        'salt':None,
        'fiber':None}
    }, 'img_src': None, 'current_category_id': None, 'planned_category_id': None, 'ingredients': None, 'allergy_recommendations': None}
  r = requests.put(f'{url}/api/v1/products/{id}', json=data, cookies=cookies)
  assert r.status_code == 200
  product = r.json()
  assert product['name'] == 'szarlotka'
  assert product['nutrition_facts']['nutrients']['fat'] == None
  assert product['nutrition_facts']['nutrients']['sugars'] == 20
@pytest.mark.usefixtures('restart_docker')
def test_update_product_returns_422_not_existing_category(cookies):
  id = insert_product(cookies=cookies)
  url = config.get_api_url()
  data = {'name' : 'szarlotka', 'brand_name' : 'XYZ', 'nutrition_facts' : {
      'kcal' :'200',
      'reference_quantity' : {'unit' : 'g', 'amount': 100},
      'nutrients': {
        'fat': None,
        'saturates': None,
        'carbohydrates': None,
        'sugars': None,
        'protein': None,
        'salt':None,
        'fiber':None}
    }, 'img_src': None, 'current_category_id': 10, 'planned_category_id': None, 'ingredients': None, 'allergy_recommendations': None}
  r = requests.put(f'{url}/api/v1/products/{id}', json=data, cookies=cookies)
  assert r.status_code == 422



@pytest.mark.usefixtures('restart_docker')
def test_update_product_returns_422_additional_field(cookies):
  id = insert_product(cookies=cookies)
  url = config.get_api_url()
  data = {'name' : 'szarlotka', 'brand_name' : 'XYZ', 'nutrition_facts' : {
      'kcal' :'200',
      'reference_quantity' : {'unit' : 'g', 'amount': 100},
      'nutrients': {
        'fat': None,
        'saturates': None,
        'carbohydrates': None,
        'sugars': None,
        'protein': None,
        'salt':None,
        'fiber':None}
    }, 'img_src': None, 'current_category_id': None, 'planned_category_id': None, 'ingredients': None, 'allergy_recommendations': None, 'nothing' : 0}  
  r = requests.put(f'{url}/api/v1/products/{id}', json=data, cookies=cookies)
  assert r.status_code == 422

@pytest.mark.usefixtures('restart_docker')
def test_update_product_returns_422_null_name(cookies):
  id = insert_product(cookies=cookies)
  url = config.get_api_url()
  data = {'name' : None, 'brand_name' : 'auchan', 'nutrition_facts' : {
        'kcal' :'200',
        'reference_quantity' : {'unit' : 'g', 'amount': 100},
        'nutrients': {
          'fat': None,
          'saturates': None,
          'carbohydrates': None,
          'sugars': None,
          'protein': None,
          'salt':None,
          'fiber':None}
      }, 'img_src': None, 'current_category_id': None, 'planned_category_id': None, 'ingredients': None, 'allergy_recommendations': None}  
  r = requests.put(f'{url}/api/v1/products/{id}', json=data, cookies=cookies)
  assert r.status_code == 422

@pytest.mark.usefixtures('restart_docker')
def test_update_product_returns_404_not_existing_product(cookies):
  url = config.get_api_url()
  data = {'name' : 'jogurt', 'brand_name' : 'auchan', 'nutrition_facts' : {
        'kcal' :'200',
        'reference_quantity' : {'unit' : 'g', 'amount': 100},
        'nutrients': {
          'fat': None,
          'saturates': None,
          'carbohydrates': None,
          'sugars': None,
          'protein': None,
          'salt':None,
          'fiber':None}
      }, 'img_src': None, 'current_category_id': None, 'planned_category_id': None, 'ingredients': None, 'allergy_recommendations': None}    
  r = requests.put(f'{url}/api/v1/products/1000', json=data, cookies=cookies)
  assert r.status_code == 404

@pytest.mark.usefixtures('restart_docker')
def test_update_product_returns_422_correct_id_in_body(cookies):
  id = insert_product(cookies=cookies)
  url = config.get_api_url()
  data = {'id' : f'{id}', 'name' : 'jogurt', 'brand_name' : 'auchan', 'nutrition_facts' : {
        'kcal' :'200',
        'reference_quantity' : {'unit' : 'g', 'amount': 100},
        'nutrients': {
          'fat': None,
          'saturates': None,
          'carbohydrates': None,
          'sugars': None,
          'protein': None,
          'salt':None,
          'fiber':None}
      }, 'img_src': None, 'current_category_id': None, 'planned_category_id': None, 'ingredients': None, 'allergy_recommendations': None}      
  r = requests.put(f'{url}/api/v1/products/{id}', json=data, cookies=cookies)
  assert r.status_code == 422



@pytest.mark.usefixtures('restart_docker')
def test_update_product_returns_422_empty_body(cookies):
  id = insert_product(cookies=cookies)
  url = config.get_api_url()
  data = {}
  r = requests.put(f'{url}/api/v1/products/{id}', json=data, cookies=cookies)
  assert r.status_code == 422

@pytest.mark.usefixtures('restart_docker')
def test_delete_returns_204(cookies):
  id = insert_product(cookies=cookies)
  url = config.get_api_url()
  r = requests.delete(f'{url}/api/v1/products/{id}', cookies=cookies)
  assert r.status_code == 204

@pytest.mark.usefixtures('restart_docker')
def test_delete_returns_404_id_not_exists(cookies):
  url = config.get_api_url()
  r = requests.delete(f'{url}/api/v1/products/1000', cookies=cookies)
  assert r.status_code == 404

@pytest.mark.usefixtures('restart_docker')
def test_get_returns_200_by_id(cookies):
  id = insert_product(cookies=cookies)
  url = config.get_api_url()
  r = requests.get(f'{url}/api/v1/products/{id}', cookies=cookies)
  assert r.status_code == 200
  product = r.json()
  assert product['name'] == 'szarlotka'

@pytest.mark.usefixtures('restart_docker')
def test_get_returns_404_not_existing_id():
  url = config.get_api_url()
  r = requests.get(f'{url}/api/v1/products/1000')
  assert r.status_code == 404

def insert_20_products(cookies):
  insert_product('Budyń mleczny', kcal=100,cookies=cookies)
  insert_product('Lody mleczne', kcal=90,cookies=cookies)
  insert_product('Masło', kcal=300,cookies=cookies)
  insert_product('Masło', brand='opolskie', kcal=310,cookies=cookies)
  insert_product('Masło light', brand='opolskie', kcal=240,cookies=cookies)
  insert_product('Mozzarella light', kcal=220,cookies=cookies)
  insert_product('Mozzarella klasyczna', kcal=300,cookies=cookies)
  insert_product('Rolada Klasyczna', kcal=180,cookies=cookies)
  insert_product('Rolada Rolowana', kcal=170,cookies=cookies)
  insert_product('Kiełbasa Śląska', kcal=190,cookies=cookies)
  insert_product('Kiełbasa Roślinna', kcal=110,cookies=cookies)
  insert_product('Kiełbasa Roleska', kcal=100,cookies=cookies)
  insert_product('Mleko Light', kcal=110,cookies=cookies)
  insert_product('Mleko Tłuste', kcal=330,cookies=cookies)
  insert_product('Mleko', kcal=220,cookies=cookies)
  insert_product('Parówki Tik', kcal=100,cookies=cookies)
  insert_product('Baton Tikitaki', kcal=100,cookies=cookies)
  insert_product('Baton Tom', kcal=120,cookies=cookies)
  insert_product('Baton Roślinny', kcal=100,cookies=cookies)
  insert_product('Baton Mleczny', kcal=100,cookies=cookies)

@pytest.mark.usefixtures('restart_docker')
def test_get_returns_200_all_products(cookies):
  insert_20_products(cookies)
  url = config.get_api_url()
  r = requests.get(f'{url}/api/v1/products', params={'page': 1, 'limit': 20})
  assert r.status_code == 200
  data = r.json()
  pagination = data['pagination']
  assert pagination['page'] == 1
  assert pagination['limit'] == 20
  assert pagination['total_pages'] == 1
  assert pagination['total'] == 20
  products = data['data']
  assert len(products) == 20

@pytest.mark.usefixtures('restart_docker')
def test_get_returns_200_all_products_limit_5(cookies):
  insert_20_products(cookies)
  url = config.get_api_url()
  r = requests.get(f'{url}/api/v1/products', params={'page': 2, 'limit': 5})
  assert r.status_code == 200
  data = r.json()
  pagination = data['pagination']
  assert pagination['page'] == 2
  assert pagination['limit'] == 5
  assert pagination['total_pages'] == 4
  assert pagination['total'] == 20
  products = data['data']
  assert len(products) == 5

@pytest.mark.usefixtures('restart_docker')
def test_get_returns_200_empty_list(cookies):
  url = config.get_api_url()
  r = requests.get(f'{url}/api/v1/products', params={'page': 1, 'limit': 5})
  assert r.status_code == 200
  data = r.json()
  pagination = data['pagination']
  assert pagination['page'] == 1
  assert pagination['limit'] == 5
  assert pagination['total_pages'] == 0
  assert pagination['total'] == 0
  products = data['data']
  assert len(products) == 0

@pytest.mark.usefixtures('restart_docker')
def test_get_returns_200_all_products_sort_by_kcal_desc(cookies):
  insert_20_products(cookies)
  url = config.get_api_url()
  r = requests.get(f'{url}/api/v1/products', params={'page': 1, 'limit': 20, 'sort_by' : 'kcal', 'order':'desc'})
  assert r.status_code == 200
  data = r.json()
  products = data['data']
  assert len(products) == 20
  assert products[0]['nutrition_facts']['kcal'] == 330 and products[0]['name'] == 'Mleko Tłuste'
  assert products[19]['nutrition_facts']['kcal'] == 90 and products[19]['name'] == 'Lody mleczne'

@pytest.mark.usefixtures('restart_docker')
def test_get_returns_200_all_products_sort_by_kcal_asc(cookies):
  insert_20_products(cookies)
  url = config.get_api_url()
  r = requests.get(f'{url}/api/v1/products', params={'page': 1, 'limit': 20, 'sort_by' : 'kcal', 'order':'asc'})
  assert r.status_code == 200
  data = r.json()
  products = data['data']
  assert len(products) == 20
  assert products[0]['nutrition_facts']['kcal'] == 90 and products[0]['name'] == 'Lody mleczne'
  assert products[19]['nutrition_facts']['kcal'] == 330 and products[19]['name'] == 'Mleko Tłuste'
  
@pytest.mark.usefixtures('restart_docker')
def test_get_returns_200_products_with_name(cookies):
  insert_20_products(cookies)
  url = config.get_api_url()
  r = requests.get(f'{url}/api/v1/products', params={'page': 1, 'limit': 5, 'name' : 'mleko','sort_by':'id'})
  assert r.status_code == 200
  data = r.json()
  pagination = data['pagination']
  products = data['data']
  assert pagination['page'] == 1
  assert pagination['limit'] == 5
  assert pagination['total_pages'] == 1
  assert pagination['total'] == 3
  
  assert len(products) == 3
  assert products[0]['name'] == 'Mleko Light'
  assert products[1]['name'] == 'Mleko Tłuste'
  assert products[2]['name'] == 'Mleko'

@pytest.mark.usefixtures('restart_docker')
def test_get_returns_200_not_existing_name(cookies):
  insert_20_products(cookies)
  url = config.get_api_url()
  r = requests.get(f'{url}/api/v1/products', params={'page': 1, 'limit': 5, 'name' : 'pizza','sort_by':'id'})
  assert r.status_code == 200
  data = r.json()
  pagination = data['pagination']
  products = data['data']
  assert pagination['page'] == 1
  assert pagination['limit'] == 5
  assert pagination['total_pages'] == 0
  assert pagination['total'] == 0
  assert len(products) == 0


#TODO: test get, search by category