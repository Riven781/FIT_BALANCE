from product_catalog_context.domain.enums.reported_field import ReportedField
from product_catalog_context.domain.product.product import Product
from product_catalog_context.domain.reports.product_report import ProductReport

def get_product_value_by_reported_field(product: Product, field: ReportedField):
  if field == ReportedField.NAME:
    return product.name
  if field == ReportedField.KCAL:
    return product.nutrition_facts.kcal
  if field == ReportedField.CARBOHYDRATES:
    return product.nutrition_facts.nutrients.carbohydrates
  if field == ReportedField.FAT:
    return product.nutrition_facts.nutrients.fat
  if field == ReportedField.FIBER:
    return product.nutrition_facts.nutrients.fiber
  if field == ReportedField.PROTEIN:
    return product.nutrition_facts.nutrients.protein
  if field == ReportedField.SALT:
    return product.nutrition_facts.nutrients.salt
  if field == ReportedField.SATURATES:
    return product.nutrition_facts.nutrients.saturates
  if field == ReportedField.SUGARS:
    return product.nutrition_facts.nutrients.sugars



def update_report_item_statuses(product_report: ProductReport, product: Product):
  reported_fields = product_report.get_reported_fields()
  for reported_field in reported_fields:
    product_value = get_product_value_by_reported_field(product, reported_field)
    product_report.evaluate_status(reported_field, product_value)


    