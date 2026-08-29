from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Table, null, text
from sqlalchemy.orm import registry, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from identity_and_access_context.domain.refresh_token.refresh_token import RefreshToken
from identity_and_access_context.domain.role import Role
from identity_and_access_context.domain.user.user import User
from identity_and_access_context.domain.user_roles.user_roles import UserRoles

mapper_registry = registry()

user_table = Table(
  "User",
  mapper_registry.metadata,
  Column("id", Integer, primary_key=True, autoincrement=True),
  Column("username", String, nullable=False, unique=True),
  Column("email", String, nullable=False, unique=True),
  Column("hashed_password", String),
  Column("created_at", DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
)

user_roles_table = Table(
  "UserRoles",
  mapper_registry.metadata,
  Column("user_id", Integer, ForeignKey("User.id", ondelete='CASCADE'), primary_key=True),
  Column("version", Integer, nullable=False)
)

user_role_table = Table(
  "UserRole",
  mapper_registry.metadata,
  Column("user_id", Integer, ForeignKey("UserRoles.user_id", ondelete='CASCADE'), primary_key=True),
  Column("role", Enum(Role, native_enum=False), primary_key=True)
)

class UserRoleModel:
  def __init__(self, role):
    self.role = role

mapper_registry.map_imperatively(
  UserRoleModel,
  user_role_table
)


mapper_registry.map_imperatively(UserRoles, user_roles_table, properties={
  "_user_roles" : relationship(UserRoleModel, cascade="all, delete-orphan"),
})
UserRoles.roles = association_proxy("_user_roles", "role", creator=lambda role: UserRoleModel(role=role))


mapper_registry.map_imperatively(User, user_table, properties={
  "user_id" : user_table.c.id,
  #"_user_roles" : relationship(UserRoleModel, cascade="all, delete-orphan"),
})



refresh_token_table = Table(
  "RefreshToken",
  mapper_registry.metadata,
  Column("id", Integer, primary_key=True),
  Column("token_hash", String, nullable=False, unique=True),
  Column("user_id", Integer, ForeignKey("User.id"), nullable=False),
  Column("expires_at", DateTime(timezone=True), nullable=False),
  Column("revoked_at", DateTime(timezone=True)),
  Column("created_at", DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
)

mapper_registry.map_imperatively(
  RefreshToken,
  refresh_token_table, properties={
    "token_id" : refresh_token_table.c.id
  }
)