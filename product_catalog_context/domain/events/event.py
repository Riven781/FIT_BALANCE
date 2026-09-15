from dataclasses import dataclass
from typing import ClassVar


@dataclass
class DomainEvent:
  event_type: ClassVar[str]
