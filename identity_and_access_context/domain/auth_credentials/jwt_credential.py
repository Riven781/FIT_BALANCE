from dataclasses import dataclass


@dataclass
class JwtCredential:
  value: str

@dataclass
class JwtAccessTokenCredential(JwtCredential):
  value: str

@dataclass
class JwtRefreshTokenCredential(JwtCredential):
  value: str