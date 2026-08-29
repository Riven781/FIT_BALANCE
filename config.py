import os
from dotenv import load_dotenv

load_dotenv()

def get_api_url():
  host = os.getenv('API_HOST')
  port = os.getenv('API_PORT')
  return f'http://{host}:{port}'

DB_PATH = os.getenv('DB_PATH')
MODE = os.getenv('MODE')

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
JWT_SECRET = os.getenv('JWT_SECRET')

