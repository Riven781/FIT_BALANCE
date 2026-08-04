from dataclasses import dataclass, fields, replace

@dataclass(frozen=True)
class Nutrients:
  fat: float | None
  saturates: float | None
  carbohydrates: float| None
  sugars: float | None
  protein: float | None
  salt: float | None
  fiber: float | None

  def __post_init__(self):
    for field in fields(self):
      value = getattr(self, field.name)
      if value is not None and value < 0:
        raise ValueError(f'{field.name} cannot be less than 0')
  
  def with_updates(self, **changes) -> "Nutrients":
    return replace(self, **changes)

@dataclass(frozen=True)
class ReferenceQuantity:
  amount: int
  unit: str

  def __post_init__(self) -> None:
    if self.amount <= 0:
      raise ValueError("Reference amount must be greater than 0")
    
  def with_updates(self, **changes) -> "ReferenceQuantity":
    return replace(self, **changes)

@dataclass(frozen=True)
class NutritionFacts:
  reference_quantity : ReferenceQuantity
  kcal : int
  nutrients : Nutrients

  def with_updates(
      self, *, 
      reference_quantity : ReferenceQuantity | None = None, 
      kcal: int | None = None, 
      nutrients: dict | None = None) -> "NutritionFacts":
    return replace(
      self,
      reference_quantity = self.reference_quantity if reference_quantity is None else self.reference_quantity.with_updates(**reference_quantity),
      kcal = self.kcal if kcal is None else kcal,
      nutrients = self.nutrients if nutrients is None else self.nutrients.with_updates(**nutrients))
  
"""
lepiej w doemenie:
new_reference = facts.reference_quantity.with_updates(
    amount=250
)

new_nutrients = facts.nutrients.with_updates(
    salt=0.5
)

new_facts = facts.with_updates(
    reference_quantity=new_reference,
    nutrients=new_nutrients,
)

JSON / Pydantic
    ↓ słowniki
Application service / mapper
    ↓ obiekty domenowe
NutritionFacts
    ├── ReferenceQuantity
    └── Nutrients

"""