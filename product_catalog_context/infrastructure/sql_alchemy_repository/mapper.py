from sqlalchemy import Column, DateTime, Double, ForeignKey, Index, Integer, PrimaryKeyConstraint, String, Table, UniqueConstraint, insert, join, text
from sqlalchemy.orm import attribute_mapped_collection, composite, registry, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy import event

from product_catalog_context.domain.category_hierarchy.plan_hiearachy_for_publication_saga.plan_hierarchy_for_publication_saga import PlanHierarchyForPublicationSaga
from product_catalog_context.domain.category_hierarchy.product_category import ProductCategory
from product_catalog_context.domain.category_hierarchy.product_category_hierarchy import ProductCategoryHierarchy
from product_catalog_context.domain.issues.confirmation_saga.product_issue_confirmation_saga import ProductIssueConfirmationSaga
from product_catalog_context.domain.issues.product_issue import ProductIssue
from product_catalog_context.domain.issues.product_issue_status import ProductIssueStatus
from product_catalog_context.domain.product.nutrition_facts import Nutrients, NutritionFacts, ReferenceQuantity
from product_catalog_context.domain.product.product import Product
from product_catalog_context.domain.product.product_assignment import CategoryAssignment
from product_catalog_context.domain.reports.product_report import ProductReport
from product_catalog_context.domain.reports.product_report_item import ProductReportItem
from product_catalog_context.domain.tasks.category_assignment_task import CategoryAssignmentTask


mapper_registry = registry()

product_table = Table(
  "Product",
  mapper_registry.metadata,
  Column("id", Integer, primary_key=True, autoincrement=True),
  Column("name", String, nullable=False),
  Column("brand_name", String),
  Column("kcal", Integer, nullable=False),
  Column("fat", Double),
  Column("saturates", Double),
  Column("carbohydrates", Double),
  Column("sugars", Double),
  Column("protein", Double),
  Column("salt", Double),
  Column("fiber", Double),
  Column("ingredients", String),
  Column("allergy_recommendations", String),
  Column("reference_amount", Integer),
  Column("reference_unit", String),
  Column("img_src", String),
  Column("name_search_standard", String),
  Column("created_at", DateTime, server_default=text("CURRENT_TIMESTAMP")),
  Column("created_by", String),
  Column("version", Integer, nullable=False, default=0)
)

product_category_hierarchy_table = Table(
  "ProductCategoryHierarchy",
  mapper_registry.metadata,
  Column("id", Integer, primary_key=True, autoincrement=True),
  Column("version", Integer, nullable=False, default=0),
  Column("status", String),
  Column("created_by", Integer),
  Column("created_at", DateTime, server_default=text("CURRENT_TIMESTAMP")),
  Column("published_by", Integer),
  Column("published_at", DateTime)
)

product_category_node_table = Table(
  "ProductCategoryNode",
  mapper_registry.metadata,
  Column("id", Integer, primary_key=True, autoincrement=True),
  Column("name", String, nullable=False),
  Column("parent_id", Integer, ForeignKey("ProductCategoryNode.id", ondelete="SET NULL")),
  Column("hierarchy_id", Integer, ForeignKey("ProductCategoryHierarchy.id", ondelete="CASCADE"), nullable=False),
  Column("source_node_id", Integer, ForeignKey("ProductCategoryNode.id", ondelete="SET NULL"))
)

product_category_assignment_table = Table(
  "ProductCategoryAssignment",
  mapper_registry.metadata,
  Column("product_id", Integer, ForeignKey("Product.id", ondelete="CASCADE"), nullable=False),
  Column("node_id", Integer, ForeignKey("ProductCategoryNode.id", ondelete="CASCADE"), nullable=False),
  Column("hierarchy_id", Integer, ForeignKey("ProductCategoryHierarchy.id", ondelete="CASCADE"), nullable=False), #redundatn
  Column("assigned_by", Integer),
  Column("assigned_at", DateTime, server_default=text("CURRENT_TIMESTAMP")),
  Column("version", Integer, nullable=False, default=0),
  PrimaryKeyConstraint("product_id", "hierarchy_id", name="pk_product_category_assignment")
)

class ProductCategoryAssignmentModel:
  def __init__(self, product_id, hierarchy_id, node_id, version, assigned_by=None,  node=None):
    self.assigned_by = assigned_by
    self.product_id = product_id
    self.node_id = node_id
    self.node = node
    self.hierarchy_id = hierarchy_id
    self.version = version

  @property
  def category_assignment(self):
    return CategoryAssignment(category_id=self.node_id, assigned_by=self.assigned_by, version=self.version)

  @category_assignment.setter
  def category_assignment(self, value:CategoryAssignment):
    self.node_id = value.category_id
    self.assigned_by = value.assigned_by
    #self.assigned_at = value.assigned_at

mapper_registry.map_imperatively(ProductCategory, product_category_node_table, properties={
  "category_id" : product_category_node_table.c.id
})

mapper_registry.map_imperatively(ProductCategoryHierarchy, product_category_hierarchy_table, properties={
  "hierarchy_id" : product_category_hierarchy_table.c.id,
  "product_categories" : relationship(ProductCategory, cascade="all, delete-orphan", lazy='selectin')
})

mapper_registry.map_imperatively(ProductCategoryAssignmentModel, product_category_assignment_table, properties={
  "node" : relationship(ProductCategory, lazy='joined', viewonly=True),
}, version_id_col = product_category_assignment_table.c.version)

def nutrition_facts_factory(kcal, reference_amount, reference_unit, fat, saturates, carbohydrates, sugars, protein, salt, fiber):
  return NutritionFacts(
    reference_quantity=ReferenceQuantity(amount=reference_amount, unit=reference_unit),
    nutrients=Nutrients(
      fat=fat,
      saturates=saturates,
      carbohydrates=carbohydrates,
      sugars=sugars,
      protein=protein,
      salt=salt,
      fiber=fiber
    ),
    kcal=kcal
  )

def nutrition_facts_composite_value(self:  NutritionFacts):
  return (
    self.kcal,
    self.reference_quantity.amount,
    self.reference_quantity.unit,
    self.nutrients.fat,
    self.nutrients.saturates,
    self.nutrients.carbohydrates,
    self.nutrients.sugars,
    self.nutrients.protein,
    self.nutrients.salt,
    self.nutrients.fiber,
  )

NutritionFacts.__composite_values__ = nutrition_facts_composite_value

nutrition_facts_composite = composite(
  nutrition_facts_factory,
  product_table.c.kcal,
  product_table.c.reference_amount,
  product_table.c.reference_unit,
  product_table.c.fat,
  product_table.c.saturates,
  product_table.c.carbohydrates,
  product_table.c.sugars,
  product_table.c.protein,
  product_table.c.salt,
  product_table.c.fiber,
)


mapper_registry.map_imperatively(Product, product_table, properties={
  "_product_id" : product_table.c.id,
  "_nutrition_facts" : nutrition_facts_composite,
  "_category_assignments": relationship(ProductCategoryAssignmentModel, collection_class=attribute_mapped_collection("hierarchy_id"), cascade="all, delete-orphan", lazy='selectin'),
  "_name" : product_table.c.name,
  "_brand_name" : product_table.c.brand_name,
}, version_id_col = product_table.c.version)

def product_category_assignment_creator(hierarchy_id, category_assignment: CategoryAssignment):
  #print(f"hierarchy: {hierarchy_id}, node_id: {category_assignment}")
  return ProductCategoryAssignmentModel(
    product_id=None, 
    node_id=category_assignment.category_id,
    hierarchy_id=hierarchy_id,
    version=category_assignment.version,
    assigned_by=category_assignment.assigned_by)

Product.category_assignments = association_proxy("_category_assignments", "category_assignment", creator= product_category_assignment_creator)



product_category_assignment_task_table = Table(
  "ProductCategoryAssignmentTask",
  mapper_registry.metadata,
  Column("id", Integer, primary_key=True, nullable=False),
  Column("product_id", Integer, ForeignKey("Product.id", ondelete="CASCADE"), nullable=False),
  Column("hierarchy_id", Integer, ForeignKey("ProductCategoryHierarchy.id", ondelete="CASCADE"), nullable=False),
  Column("user_id", Integer),
  Column("status", String),
  Column("created_at", DateTime, server_default=text("CURRENT_TIMESTAMP"))
)



mapper_registry.map_imperatively(CategoryAssignmentTask, product_category_assignment_task_table, properties={
  "task_id" : product_category_assignment_task_table.c.id
})

@event.listens_for(ProductCategoryHierarchy, "load")
def receive_load(hierarchy, context):
  hierarchy._events = []


id_seq_table = Table(
  "IdSequence",
  mapper_registry.metadata,
  Column("name", String, primary_key=True, nullable=False),
  Column("next_value", Integer, nullable=False),
)

product_report_table = Table(
  "ProductReport",
  mapper_registry.metadata,
  Column("id", Integer, primary_key=True, nullable=False),
  Column("product_id", Integer, ForeignKey("Product.id", ondelete="CASCADE"), nullable=False),
  Column("user_id", Integer),
  Column("product_version", Integer),
  UniqueConstraint('product_id', 'user_id', 'product_version')
)


product_issue_table = Table(
  "ProductIssue",
  mapper_registry.metadata,
  Column("id", Integer, primary_key=True, nullable=False),
  Column("product_id", Integer, ForeignKey("Product.id", ondelete="CASCADE"), nullable=False),
  Column("status", String),
  Column("reported_field", String),
  Column("old_value", String),
  Column("resolved_value", String),
  Column("resolved_by", Integer),
  Column("version", Integer, nullable=False, default=0),
)

Index(
  "uq_pending_product_issue",
  product_issue_table.c.product_id,
  product_issue_table.c.reported_field,
  product_issue_table.c.old_value,
  unique=True,
  sqlite_where=product_issue_table.c.status == ProductIssueStatus.PENDING,
)

product_issue_confirmation_saga_table = Table(
  "ProductIssueConfirmationSaga",
  mapper_registry.metadata,
  Column("id", Integer, primary_key=True, nullable=False),
  Column("issue_id", Integer, ForeignKey("ProductIssue.id", ondelete="CASCADE"), nullable=False, unique=True),
  Column("status", String),
  Column("version", Integer, nullable=False, default=0),
)



mapper_registry.map_imperatively(ProductIssueConfirmationSaga, product_issue_confirmation_saga_table, properties={
  "saga_id" : product_issue_confirmation_saga_table.c.id
}, version_id_col = product_issue_confirmation_saga_table.c.version)

plan_hierarchy_for_publication_saga_table = Table(
  "PlanHierarchyForPublicationSaga",
  mapper_registry.metadata,
  Column("id", Integer, primary_key=True, nullable=False),
  Column("hierarchy_id", Integer, ForeignKey("ProductIssue.id", ondelete="CASCADE"), nullable=False, unique=True),
  Column("status", String),
  Column("version", Integer, nullable=False, default=0),
)

mapper_registry.map_imperatively(PlanHierarchyForPublicationSaga, plan_hierarchy_for_publication_saga_table, properties={
  "saga_id" : plan_hierarchy_for_publication_saga_table.c.id
}, version_id_col = plan_hierarchy_for_publication_saga_table.c.version)


product_report_item_table = Table(
  "ProductReportItem",
  mapper_registry.metadata,
  Column("id", Integer, primary_key=True, nullable=False),
  Column("report_id", Integer, ForeignKey("ProductReport.id", ondelete="CASCADE"), nullable=False),
  Column("issue_id", Integer, ForeignKey("ProductIssue.id", ondelete="SET NULL")),
  Column("proposed_value", String),
  Column("old_value", String),
  Column("status", String),
  Column("reported_field", String, nullable=False),

  
)

mapper_registry.map_imperatively(ProductIssue, product_issue_table, properties={
  "issue_id" : product_issue_table.c.id,
  "_old_value": product_issue_table.c.old_value
}, version_id_col = product_issue_table.c.version)



mapper_registry.map_imperatively(ProductReportItem, product_report_item_table, properties={
  "_issue" : relationship(ProductIssue, lazy='joined', viewonly=True)
})



mapper_registry.map_imperatively(ProductReport, product_report_table, properties={
  "report_id" : product_report_table.c.id,
  "reported_items" : relationship(ProductReportItem, lazy='selectin', cascade='all, delete-orphan')
})


@event.listens_for(ProductIssue, "load")
def receive_load(issue, context):
  issue._events = []


@event.listens_for(ProductIssueConfirmationSaga, "load")
def receive_load(saga, context):
  saga._commands = []

@event.listens_for(PlanHierarchyForPublicationSaga, "load")
def receive_load(saga, context):
  saga._commands = []


@event.listens_for(ProductReport, "load")
def receive_load(product_report, context):
  product_report._events = []
