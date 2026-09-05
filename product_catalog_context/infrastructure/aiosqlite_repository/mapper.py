from product_catalog_context.domain.tasks.category_assignment_task import CategoryAssignmentTask
from product_catalog_context.domain.enums import reported_field
from product_catalog_context.domain.issues.product_issue import ProductIssue
from product_catalog_context.domain.reports.product_report import ProductReport
from product_catalog_context.domain.reports.product_report_item import ProductReportItem
from product_catalog_context.domain.product.nutrition_facts import Nutrients, NutritionFacts, ReferenceQuantity
from product_catalog_context.domain.product.product import Product
from product_catalog_context.domain.category_hierarchy.product_category_hierarchy import ProductCategoryHierarchy
from product_catalog_context.domain.category_hierarchy.product_category import ProductCategory


class ProductMapper:
  def __init__(self):
    pass

  @staticmethod
  def to_storage_dict(product: Product):
    print(product.nutrition_facts)
    out_dict = {}
    if product.product_id is not None:
      out_dict['id'] = product.product_id
    out_dict['name'] = product.name
    out_dict['brand_name'] = product.brand_name
    out_dict['img_src'] = product.img_src
    out_dict['ingredients'] = product.ingredients
    out_dict['allergy_recommendations'] = product.allergy_recommendations
    out_dict['reference_unit'] = product.nutrition_facts.reference_quantity.unit
    out_dict['reference_amount'] = product.nutrition_facts.reference_quantity.amount
    out_dict['fiber'] = product.nutrition_facts.nutrients.fiber
    out_dict['salt'] = product.nutrition_facts.nutrients.salt
    out_dict['protein'] = product.nutrition_facts.nutrients.protein
    out_dict['sugars'] = product.nutrition_facts.nutrients.sugars
    out_dict['carbohydrates'] = product.nutrition_facts.nutrients.carbohydrates
    out_dict['saturates'] = product.nutrition_facts.nutrients.saturates
    out_dict['fat'] = product.nutrition_facts.nutrients.fat
    out_dict['kcal'] = product.nutrition_facts.kcal
    out_dict['name_search_standard'] = product.name_search_standard
    out_dict['category_assignments'] = product.category_assignments
    
    return out_dict

  @staticmethod
  def to_product(row):
    nutrients = Nutrients(
      fat=row['fat'],
      saturates=row['saturates'],
      carbohydrates=row['carbohydrates'],
      sugars=row['sugars'],
      protein=row['protein'],
      salt=row['salt'],
      fiber=row['fiber'])
    nutrition_facts = NutritionFacts(
      ReferenceQuantity(row['reference_amount'], row['reference_unit']),
      row['kcal'],
      nutrients=nutrients
      )
    return Product(
      product_id = row['id'],
      name = row['name'],
      brand_name= row['brand_name'],
      nutrition_facts=nutrition_facts,
      img_src=row['img_src'],
      ingredients=row['ingredients'],
      allergy_recommendations=row['allergy_recommendations'],
      category_assignments=row['category_assignments']
      )


class ProductCategoryHierarchyMapper:
  def __init__(self):
    pass

  @staticmethod
  def to_hierarchy(row):
    categories =[ProductCategory(name=category['name'], parent_id=category['parent_id'], category_id=category['id'])  for category in row['categories']] 
    return ProductCategoryHierarchy(hierarchy_id=row['id'], status=row['status'], product_categories=categories)

  @staticmethod
  def to_storage_dict(hierarchy: ProductCategoryHierarchy):
    out_dict = {}
    if hierarchy.hierarchy_id is not None:
      out_dict['id'] = hierarchy.hierarchy_id
    out_dict['status'] = hierarchy.status
    out_dict['categories'] = [{'name': category.name, 'parent_id': category.parent_id, 'id': category.category_id} for category in hierarchy.product_categories]
    return out_dict

class CategoryAssignmentTaskMapper:
  def __init__(self):
    pass

  @staticmethod
  def to_task(row):
    return CategoryAssignmentTask(
      task_id=row['id'],
      product_id=row['product_id'],
      hierarchy_id=row['hierarchy_id'],
      user_id=row['user_id'],
      status=row['status']
    )
  
  @staticmethod
  def to_storage_dict(task: CategoryAssignmentTask):
    out_dict = {}
    if task.task_id is not None:
      out_dict['id'] = task.task_id
    out_dict['product_id'] = task.product_id
    out_dict['hierarchy_id'] = task.hierarchy_id
    out_dict['user_id'] = task.user_id
    out_dict['status'] = task.status
    return out_dict

class ProductIssueMapper:
  def __init__(self):
    pass

  @staticmethod
  def to_issue(row):
    return ProductIssue(
      issue_id=row['id'],
      reported_field=row['reported_field'],
      status=row['status'],
      product_id=row['product_id'],
      resolved_value=row['resolved_value']
    )

  @staticmethod
  def to_storage_dict(product_issue : ProductIssue):
    out_dict = {}
    if product_issue.issue_id is not None:
      out_dict['id'] = product_issue.issue_id
    out_dict['product_id'] = product_issue.product_id
    out_dict['reported_field'] = product_issue.reported_field
    out_dict['status'] = product_issue.status
    out_dict['resolved_value'] = product_issue.resolved_value
    return out_dict

class ProductReportMapper:
  def __init__(self):
    pass
  @staticmethod
  def to_report(row):
    reported_items = [ProductReportItem(reported_field=reported_item['reported_field'], proposed_value=reported_item['proposed_value'], issue_id=reported_item['issue_id']) for reported_item in row['reported_items']]
    return ProductReport(report_id=row['id'], product_id=row['product_id'], user_id=row['user_id'], reported_items=reported_items)

  @staticmethod
  def to_storage_dict(product_report : ProductReport):
    out_dict = {}
    if product_report.report_id is not None:
      out_dict['id'] = product_report.report_id
    out_dict['product_id'] = product_report.product_id
    out_dict['user_id'] = product_report.user_id
    out_dict['reported_items'] = [{ 'proposed_value' : report_item.proposed_value, 'issue_id': report_item.issue_id}for report_item in product_report.reported_items]
    return out_dict