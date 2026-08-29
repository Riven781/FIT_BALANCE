import pytest
from identity_and_access_context.domain.session.session import Session
from identity_and_access_context.domain.role import Role
from identity_and_access_context.domain.session.session import SessionData
import time
#docker compose up -d redis-test


@pytest.mark.asyncio
async def test_get_by_id(session_repository, example_session):
  session_from_storage = await session_repository.get_by_id(example_session.session_id)
  assert session_from_storage.session_id == example_session.session_id
  assert session_from_storage.session_data.username == example_session.session_data.username
  assert session_from_storage.session_data.user_id == example_session.session_data.user_id

@pytest.mark.asyncio
async def test_get_by_id_not_existing_session(session_repository):
  session_from_storage = await session_repository.get_by_id(1)
  assert session_from_storage is None

@pytest.mark.asyncio
async def test_save_session(session_repository):
  session_id = session_repository.next_id()
  data = SessionData(username='Pawlo', user_id=10)
  session = Session(session_id,session_data=data)
  await session_repository.save(session)
  session_from_storage = await session_repository.get_by_id(session_id)
  assert session_from_storage.session_id == session_id
  assert session_from_storage.session_data.user_id == 10
  assert session_from_storage.session_data.username == 'Pawlo'


@pytest.mark.asyncio
async def test_delete_session(session_repository, example_session):
  await session_repository.delete_by_id(example_session.session_id)
  session_from_storage = await session_repository.get_by_id(example_session.session_id)
  assert session_from_storage is None

@pytest.mark.asyncio
async def test_get_by_user_id(session_repository):
  session_id_1 = session_repository.next_id()
  session_id_2 = session_repository.next_id()
  data = SessionData(username='Pawlo', user_id=10)
  session_1 = Session(session_id_1,session_data=data)
  session_2 = Session(session_id_2,session_data=data)
  await session_repository.save(session_1)
  await session_repository.save(session_2)
  sessions_by_user_id = await session_repository.get_all_by_user_id(10)
  assert len(sessions_by_user_id) == 2

@pytest.mark.asyncio
async def test_get_all_by_session_id(session_repository):
  session_id_1 = session_repository.next_id()
  session_id_2 = session_repository.next_id()
  data = SessionData(username='Pawlo', user_id=10)
  session_1 = Session(session_id_1,session_data=data)
  session_2 = Session(session_id_2,session_data=data)
  await session_repository.save(session_1)
  await session_repository.save(session_2)
  sessions_by_session_id = await session_repository.get_all_by_session_id(session_id_1)
  assert len(sessions_by_session_id) == 2

@pytest.mark.asyncio
async def test_save_with_ttl_increased(session_repository, example_session):
  session_from_storage = await session_repository.get_by_id(example_session.session_id)
  session_from_storage.increase_ttl(60 * 60 * 24) #one day more
  await session_repository.save(session_from_storage)
  session_with_ttl_increased = await session_repository.get_by_id(example_session.session_id)
  assert session_with_ttl_increased.ttl == 60 * 60 * 24 * 8
