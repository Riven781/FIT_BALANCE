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