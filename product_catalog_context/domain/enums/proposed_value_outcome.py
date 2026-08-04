from enum import StrEnum


class ProposedValueOutcome(StrEnum):
  NOT_PROVIDED = 'not_provided'
  CORRECT = 'correct'
  INCORRECT = 'incorrect'