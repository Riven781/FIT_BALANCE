import pytest


@pytest.mark.asyncio
async def test_get_by_not_existing_id(refresh_token_repository):
  token = await refresh_token_repository.get_by_id(1)
  assert token is None

@pytest.mark.asyncio
async def test_get_by_id(refresh_token_repository, refresh_token):
  token = await refresh_token_repository.get_by_id(refresh_token.token_id)
  assert token.token_hash == refresh_token.token_hash

@pytest.mark.asyncio
async def test_get_by_hash(refresh_token_repository, refresh_token):
  token = await refresh_token_repository.get_by_hash(refresh_token.token_hash)
  assert token.token_id == refresh_token.token_id

@pytest.mark.asyncio
async def test_get_by_hash_not_existing_token(refresh_token_repository):
  token = await refresh_token_repository.get_by_hash('bad_hash')
  assert token is None