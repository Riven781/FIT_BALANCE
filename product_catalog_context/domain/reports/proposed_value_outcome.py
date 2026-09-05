from enum import StrEnum


class ProposedValueOutcome(StrEnum):#it can be calculated by analytics in sql
  NOT_PROVIDED = 'not_provided'
  CORRECT = 'correct'
  INCORRECT = 'incorrect'