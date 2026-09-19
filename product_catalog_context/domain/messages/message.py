from dataclasses import dataclass, field
from typing import ClassVar


@dataclass
class DomainMessage:
  saga_id: int | None = field(default=None, kw_only=True)


@dataclass
class DomainEvent(DomainMessage):
  event_type: ClassVar[str]


@dataclass
class DomainCommand(DomainMessage):
  command_type: ClassVar[str]

