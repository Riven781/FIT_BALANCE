from typing import Annotated

from fastapi import Depends

from identity_and_access_context.application.access_service import AccessService
from identity_and_access_context.infrastructure.api.rest.dependencies import get_access_service
from identity_and_access_context.public.api.access_api import AccessApi


def get_access_api(access_service: Annotated[AccessService, Depends(get_access_service)]):
  return AccessApi(access_service)