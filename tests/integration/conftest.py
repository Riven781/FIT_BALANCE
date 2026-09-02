import pytest
import subprocess
import time
import config
import requests



def wait_for_api(timeout=30):
  url = config.get_api_url()
  start = time.time()

  while time.time() < start + timeout:
    try:
      r = requests.get(f'{url}/docs', timeout=0.05)
      if r.status_code < 500:
        return
    except requests.exceptions.ConnectionError:
      pass

  raise RuntimeError('API did not start')



@pytest.fixture
def restart_docker():
  subprocess.run(["docker", "compose", "down", "-v"],check=True)
  subprocess.run(['docker', 'compose', 'up', '-d', 'api-test'], check=True)
  wait_for_api()
  yield
  subprocess.run(["docker", "compose", "down", "-v"],check=True)




@pytest.fixture
def cookies():
  url = config.get_api_url()
  data = {
      'username': 'Pawlo',
      'password': 'strong_password',
    }
  r = requests.post(f'{url}/login/session', json=data)
  print(r.cookies.get('session_id'))
  return {'session_id': r.cookies.get('session_id')}


def login_jwt():
  url = config.get_api_url()
  data = {
      'username': 'Pawlo',
      'password': 'Pawlo@123',
    }
  r = requests.post(f'{url}/login/jwt', json=data)
  return r.json()

method = 'SESSION'



