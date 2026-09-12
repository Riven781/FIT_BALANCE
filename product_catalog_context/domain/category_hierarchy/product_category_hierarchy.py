from product_catalog_context.domain.errors import CategoryAssignmentTaskNotAllowed, CategoryDoesNotBelongToHierarchy, CategoryHierarchyCannotBeEdited, DraftCategoryHierarchyCannotBeDeleted, CategoryHierarchyCannotBeRevertedToDraft,ParentCategoryNotInHierarchy, CategoryHierarchyIsNotDraft,CategoryHierarchyCannotBePublished, OnlyDraftHierarchyCanBeUpdated, DraftCategoryHierarchyCannotBeCreated, DraftCategoryIdCountMismatch
from product_catalog_context.domain.category_hierarchy.product_category_hierarchy_status import ProductCategoryHierarchyStatus
from product_catalog_context.domain.category_hierarchy.product_category import ProductCategory, ProductCategoryDraft, ProductCategoryNode
from product_catalog_context.domain.category_hierarchy.events import ProductCategoryHierarchyPublished, ProductCategoryHierarchyRevertedToDraft


class ProductCategoryHierarchy:
  def __init__(self, product_categories : list[ProductCategory], status :ProductCategoryHierarchyStatus=ProductCategoryHierarchyStatus.DRAFT, hierarchy_id=None, created_by=None, published_by=None):
    self.hierarchy_id = hierarchy_id
    self.product_categories = product_categories
    self.status = status
    self.created_by = created_by
    self.published_by = published_by
    self._events = []


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

  def ensure_can_be_edited(self, existing_product_categories):
    if self.status not in [ProductCategoryHierarchyStatus.DRAFT]:
      raise CategoryHierarchyCannotBeEdited()
    if not self.contains_all_product_categories(existing_product_categories):
      raise CategoryDoesNotBelongToHierarchy()

  def ensure_draft_be_created(self):
    if self.status != ProductCategoryHierarchyStatus.ACTIVE:
      raise DraftCategoryHierarchyCannotBeCreated()

  def ensure_draft_be_deleted(self):
    if self.status != ProductCategoryHierarchyStatus.DRAFT:
      raise DraftCategoryHierarchyCannotBeDeleted()

  def get_non_leaf_category_ids(self):
    return list({category.parent_id for category in self.product_categories if category.parent_id is not None})

  def ensure_category_assignment_allowed(self): #planned_assignment
    if self.status != ProductCategoryHierarchyStatus.PLANNED_FOR_PUBLICATION:
      raise CategoryAssignmentTaskNotAllowed()
  
  def ensure_can_complete_task(self, category_id): #planned_assignment
    if self.status != ProductCategoryHierarchyStatus.PLANNED_FOR_PUBLICATION:
      raise CategoryAssignmentTaskNotAllowed()
    if not self.contains_product_category(category_id):
      raise CategoryDoesNotBelongToHierarchy()

  def ensure_can_assign_tasks(self): #planned_assignment
    if self.status != ProductCategoryHierarchyStatus.PLANNED_FOR_PUBLICATION:
      raise CategoryAssignmentTaskNotAllowed()

    
  def create_draft_based_on_hierarchy(self, ids, user_id):
    if len(ids) != len(self.product_categories):
      return DraftCategoryIdCountMismatch()
    new_id_by_old_id = {category.category_id : ids[i] for i, category in enumerate(self.product_categories)}
    product_categories_copy = [ProductCategory(name=category.name, parent_id=new_id_by_old_id.get(category.parent_id) , category_id=new_id_by_old_id[category.category_id], source_node_id=category.category_id) for category in self.product_categories]
    return ProductCategoryHierarchy(status=ProductCategoryHierarchyStatus.DRAFT, product_categories=product_categories_copy, created_by=user_id)

  def product_categories_len(self):
    return len(self.product_categories)

  def contains_product_category(self, id):
    return id in [category.category_id for category in self.product_categories]

  def contains_all_product_categories(self, product_categories):
    return all(self.contains_product_category(category.category_id) for category in product_categories)


  def publish(self, user_id):
    if self.status != ProductCategoryHierarchyStatus.PLANNED_FOR_PUBLICATION:
      raise CategoryHierarchyCannotBePublished()
    self._events.append(ProductCategoryHierarchyPublished(self.hierarchy_id))

    self.status = ProductCategoryHierarchyStatus.ACTIVE
    self.published_by = user_id

  def revert_to_draft(self):
    if self.status != ProductCategoryHierarchyStatus.PLANNED_FOR_PUBLICATION:
      raise CategoryHierarchyCannotBeRevertedToDraft()
    self.status = ProductCategoryHierarchyStatus.DRAFT
    self._events.append(ProductCategoryHierarchyRevertedToDraft(self.hierarchy_id))

  def pull_events(self):
    events = self._events
    self._events = []
    return events
  
  def plan_for_publication(self):
    if self.status != ProductCategoryHierarchyStatus.DRAFT:
      raise CategoryHierarchyIsNotDraft()
    self.status = ProductCategoryHierarchyStatus.PLANNED_FOR_PUBLICATION