
from product_catalog_context.domain.errors import CategoryAssignmentNotAllowed, DraftCategoryHierarchyCannotBeDeleted, CategoryHierarchyCannotBeRevertedToDraft,ParentCategoryNotInHierarchy, CategoryHierarchyIsNotDraft,CategoryHierarchyCannotBePublished, OnlyDraftHierarchyCanBeUpdated, DraftCategoryHierarchyCannotBeCreated, DraftCategoryIdCountMismatch
from product_catalog_context.domain.enums.product_category_hierarchy_status import ProductCategoryHierarchyStatus
from product_catalog_context.domain.product_category import ProductCategory, ProductCategoryDraft, ProductCategoryNode


class ProductCategoryHierarchy:
  def __init__(self, product_categories : list[ProductCategory], status :ProductCategoryHierarchyStatus=ProductCategoryHierarchyStatus.DRAFT, hierarchy_id=None):
    self.hierarchy_id = hierarchy_id
    self.product_categories = product_categories
    self.status = status


  #def is_hierarchy_structure_correct(self, product_categories: list[ProductCategory]):

  def _validate_hierarchy(self, categories):
    ids = [category.category_id for category in categories]
    print(f'ids: {ids}')
    for category in categories:
      print(category.parent_id)
      if category.parent_id is not None and category.parent_id not in ids:
        raise ParentCategoryNotInHierarchy()
      

  def update_categories(self, new_product_category_nodes : list[ProductCategory]):
    if self.status != ProductCategoryHierarchyStatus.DRAFT:
      raise OnlyDraftHierarchyCanBeUpdated()
    self._validate_hierarchy(new_product_category_nodes)
    self.product_categories = new_product_category_nodes
    #save -> update hierarchy

  def ensure_draft_be_created(self):
    if self.status != ProductCategoryHierarchyStatus.ACTIVE:
      raise DraftCategoryHierarchyCannotBeCreated()

  def ensure_draft_be_deleted(self):
    if self.status != ProductCategoryHierarchyStatus.DRAFT:
      raise DraftCategoryHierarchyCannotBeDeleted()

  def get_non_leaf_category_ids(self):
    return list({category.parent_id for category in self.product_categories if category.parent_id is not None})

  def ensure_category_assignment_allowed(self):
    if self.status != ProductCategoryHierarchyStatus.PLANNED_FOR_PUBLICATION:
      raise CategoryAssignmentNotAllowed 
  

  def create_draft_based_on_hierarchy(self, ids):
    if len(ids) != len(self.product_categories):
      return DraftCategoryIdCountMismatch()
    new_id_by_old_id = {category.category_id : ids[i] for i, category in enumerate(self.product_categories)}
    product_categories_copy = [ProductCategory(name=category.name, parent_id=new_id_by_old_id.get(category.parent_id) , category_id=new_id_by_old_id[category.category_id], source_node_id=category.category_id) for category in self.product_categories]
    return ProductCategoryHierarchy(status=ProductCategoryHierarchyStatus.DRAFT, product_categories=product_categories_copy)

  def product_categories_len(self):
    return len(self.product_categories)

  def contains_product_category(self, id):
    return id in [category.category_id for category in self.product_categories]

  def contains_all_product_categories(self, product_categories):
    return all(self.contains_product_category(category.category_id) for category in product_categories)


  def publish(self):
    if self.status != ProductCategoryHierarchyStatus.PLANNED_FOR_PUBLICATION:
      raise CategoryHierarchyCannotBePublished()

    self.status = ProductCategoryHierarchyStatus.ACTIVE

  def revert_to_draft(self):
    if self.status != ProductCategoryHierarchyStatus.PLANNED_FOR_PUBLICATION:
      raise CategoryHierarchyCannotBeRevertedToDraft()
    self.status = ProductCategoryHierarchyStatus.DRAFT

  def plan_for_publication(self):
    if self.status != ProductCategoryHierarchyStatus.DRAFT:
      raise CategoryHierarchyIsNotDraft
    self.status = ProductCategoryHierarchyStatus.PLANNED_FOR_PUBLICATION