import pytest
import requests
import config
import time
from datetime import datetime, timezone, timedelta
#docker compose up api-test

@pytest.mark.usefixtures('restart_docker')
def test_register():
  url = config.get_api_url()
  data = {
    'username': 'Pawlo',
    'password': 'Pawlo@123',
    'password_repeated': 'Pawlo@123',
    'email': 'pawel455@gmail.com'
  }
  r = requests.post(f'{url}/register', json=data)
  assert r.status_code == 204


def register():
  url = config.get_api_url()
  data = {
      'username': 'Pawlo',
      'password': 'Pawlo@123',
      'password_repeated': 'Pawlo@123',
      'email': 'pawel455@gmail.com'
  }
  r = requests.post(f'{url}/register', json=data)

@pytest.mark.usefixtures('restart_docker')
def test_register_user_with_existing_username():
  register()
  url = config.get_api_url()
  data = {
    'username': 'Pawlo',
    'password': 'kot@123',
    'password_repeated': 'kot@123',
    'email': 'kot@gmail.com'
  }
  r = requests.post(f'{url}/register', json=data)
  assert r.status_code == 409
  message = r.json()['message']
  assert message == "Username already exists"

@pytest.mark.usefixtures('restart_docker')
def test_register_user_with_existing_email():
  register()
  url = config.get_api_url()
  data = {
    'username': 'kotek',
    'password': 'kot@123',
    'password_repeated': 'kot@123',
    'email': 'pawel455@gmail.com'
  }
  r = requests.post(f'{url}/register', json=data)
  assert r.status_code == 409
  message = r.json()['message']
  assert message == "Email already exists"

@pytest.mark.usefixtures('restart_docker')
def test_register_different_passwords():
  url = config.get_api_url()
  data = {
    'username': 'Pawlo',
    'password': 'Pawlo@123',
    'password_repeated': 'kot@123',
    'email': 'pawel455@gmail.com'
  }
  r = requests.post(f'{url}/register', json=data)
  assert r.status_code == 422


@pytest.mark.usefixtures('restart_docker')
def test_login_with_session():
  register()
  url = config.get_api_url()
  data = {
    'username': 'Pawlo',
    'password': 'Pawlo@123',
  }
  r = requests.post(f'{url}/login/session', json=data)
  assert r.status_code == 204
  assert r.cookies.get('session_id') is not None
  cookie = next(c for c in r.cookies if c.name == 'session_id')
  expected = datetime.now(tz=timezone.utc) + timedelta(days=30)
  assert (cookie.expires - expected.timestamp()) < 2


@pytest.mark.usefixtures('restart_docker')
def test_login_with_session_invalid_credentials():
  url = config.get_api_url()
  data = {
    'username': 'nothing',
    'password': 'nothing@123',
  }
  r = requests.post(f'{url}/login/session', json=data)
  assert r.status_code == 401
  assert r.cookies.get('session_id') is None


@pytest.mark.usefixtures('restart_docker')
def test_login_with_jwt():
  register()
  url = config.get_api_url()
  data = {
    'username': 'Pawlo',
    'password': 'Pawlo@123',
  }
  r = requests.post(f'{url}/login/jwt', json=data)
  assert r.status_code == 200
  data = r.json()
  assert data.get('access_token') is not None
  assert data.get('refresh_token') is not None

@pytest.mark.usefixtures('restart_docker')
def test_login_with_jwt_invalid_credentials():
  url = config.get_api_url()
  data = {
    'username': 'nothing',
    'password': 'nothing@123',
  }
  r = requests.post(f'{url}/login/jwt', json=data)
  assert r.status_code == 401


def login_session():
  register()
  url = config.get_api_url()
  data = {
      'username': 'Pawlo',
      'password': 'Pawlo@123',
    }
  r = requests.post(f'{url}/login/session', json=data)
  return r.cookies.get('session_id')


def login_jwt():
  register()
  url = config.get_api_url()
  data = {
      'username': 'Pawlo',
      'password': 'Pawlo@123',
    }
  r = requests.post(f'{url}/login/jwt', json=data)
  return r.json()

@pytest.mark.usefixtures('restart_docker')
def test_refresh_session():
  session_id = login_session()
  time.sleep(3)
  url = config.get_api_url()
  r = requests.post(f'{url}/refresh/session', cookies={
    'session_id' : session_id
  })
  assert r.status_code == 204
  cookie = next(c for c in r.cookies if c.name == 'session_id')
  expected = datetime.now(tz=timezone.utc) + timedelta(days=60) - timedelta(seconds=3)
  assert (cookie.expires - expected.timestamp()) < 2

@pytest.mark.usefixtures('restart_docker')
def test_refresh_not_existing_session():
  url = config.get_api_url()
  r = requests.post(f'{url}/refresh/session', cookies={
    'session_id' : '10'
  })
  assert r.status_code == 401


@pytest.mark.usefixtures('restart_docker')
def test_refresh_jwt():
  tokens = login_jwt()
  time.sleep(1)
  url = config.get_api_url()
  r = requests.post(f'{url}/refresh/jwt', json={
    'refresh_token' : tokens['refresh_token']
  })
  assert r.status_code == 200
  new_tokens = r.json()
  assert new_tokens['access_token'] != tokens['access_token']
  assert new_tokens['refresh_token'] == tokens['refresh_token']


@pytest.mark.usefixtures('restart_docker')
def test_refresh_not_existing_refresh_token():
  url = config.get_api_url()
  r = requests.post(f'{url}/refresh/jwt', json={
    'refresh_token' : 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzg4MjczNTEwLCJleHAiOjE3ODgyNzUzMTB9.TPH5cPvec_9CMX2GSMfIpfWBemYocpjxmqxi-nRxlgw'
  })
  assert r.status_code == 401
  

@pytest.mark.usefixtures('restart_docker')
def test_logout_with_session():
  session_id = login_session()
  url = config.get_api_url()
  r = requests.post(f'{url}/logout/session', cookies={
    'session_id' : session_id
  })
  assert r.status_code == 204

  r = requests.post(f'{url}/refresh/session', cookies={
      'session_id' : session_id
    })
  assert r.status_code == 401



@pytest.mark.usefixtures('restart_docker')
def test_logout_with_jwt():
  tokens = login_jwt()
  url = config.get_api_url()
  r = requests.post(f'{url}/logout/jwt', json={
    'refresh_token' : tokens['refresh_token']
  })
  assert r.status_code == 204

  r = requests.post(f'{url}/refresh/jwt', json={
      'refresh_token' : tokens['refresh_token']
  })
  assert r.status_code == 401