from dataclasses import fields


def shallow_asdict(obj):
  return {field.name : getattr(obj, field.name) for field in fields(obj)}