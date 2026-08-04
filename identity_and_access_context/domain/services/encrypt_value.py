import hashlib

def encrypt_value(value: str):
  return hashlib.sha256(value.encode('UTF-8')).hexdigest()
