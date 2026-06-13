import os
from dotenv import load_dotenv

load_dotenv()

def get_api_url():
  host = os.getenv('API_HOST')
  port = os.getenv('API_PORT')
  return f'http://{host}:{port}'