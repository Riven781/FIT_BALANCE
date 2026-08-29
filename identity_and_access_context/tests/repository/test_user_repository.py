import pytest
from identity_and_access_context.infrastructure.sql_alchemy_repository import user_repository
from identity_and_access_context.domain.role import Role
from identity_and_access_context.domain.user.user import User

@pytest.mark.asyncio
async def test_get_by_not_existing_id(user_repository):
  user = await user_repository.get_by_id(1)
  assert user is None

@pytest.mark.asyncio
async def test_get_by_id(user_repository, user):
  user_in_db = await user_repository.get_by_id(user.user_id)
  assert user_in_db.user_id == user.user_id
  assert user_in_db.username == user.username
  assert user_in_db.hashed_password == user.hashed_password
  assert user_in_db.email == user.email



@pytest.mark.asyncio
async def test_get_from_authentic_credentials_not_existing_usernam(user_repository, user):
  user_in_db = await user_repository.get_from_authentic_credentials('kawa', user.hashed_password)
  assert user_in_db is None

@pytest.mark.asyncio
async def test_get_from_authentic_credentials_wrong_password(user_repository, user):
  user_in_db = await user_repository.get_from_authentic_credentials(user.username, 'bad_password')
  assert user_in_db is None

@pytest.mark.asyncio
async def test_get_from_authentic_credentials(user_repository, user):
  user_in_db = await user_repository.get_from_authentic_credentials(user.username, user.hashed_password)
  assert user_in_db.user_id == user.user_id
  assert user_in_db.username == user.username
  assert user_in_db.hashed_password == user.hashed_password
  assert user_in_db.email == user.email



@pytest.mark.asyncio
async def test_save_new_user(user_repository):
  user = User(username='Jacek', hashed_password='123', email='jacek123@gm.com')
  await user_repository.save(user)
  assert user.user_id == 1
  assert user.username == 'Jacek'


@pytest.mark.asyncio
async def test_save_existing_user_update_password(user_repository, user):
  user_in_db = await user_repository.get_by_id(user.user_id)
  user_in_db.change_password('strong_password')
  await user_repository.save(user_in_db)
  updated_user = await user_repository.get_by_id(user_in_db.user_id)
  assert updated_user.hashed_password == 'strong_password'


@pytest.mark.asyncio
async def test_delete_user(user_repository, user, db_session):
  user_in_db = await user_repository.get_by_id(user.user_id)
  await user_repository.delete(user_in_db)
  await db_session.flush()
  deleted_user = await user_repository.get_by_id(user_in_db.user_id)
  assert deleted_user is None


@pytest.mark.asyncio
async def test_exists_by_email_not_existing_user(user_repository):
  exists = await user_repository.exists_by_email('hoho')
  assert exists == False

@pytest.mark.asyncio
async def test_exists_by_email(user_repository, user):
  exists = await user_repository.exists_by_email(user.email)
  assert exists == True


@pytest.mark.asyncio
async def test_exists_by_username_not_existing_user(user_repository):
  exists = await user_repository.exists_by_username('hoho')
  assert exists == False

@pytest.mark.asyncio
async def test_exists_by_username(user_repository, user):
  exists = await user_repository.exists_by_username(user.username)
  assert exists == True