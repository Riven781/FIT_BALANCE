from pydantic import BaseModel, Field

class RefreshJwtRequest(BaseModel):
  refresh_token: str


class TokensResponse(BaseModel):
  access_token: str
  refresh_token: str

class LoggedInMessage(BaseModel):
  message : str = Field(default="logged in")