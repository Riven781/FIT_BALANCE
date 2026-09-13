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
    for category in categories:
      print(category.parent_id)
      if category.parent_id is not None and category.parent_id not in ids:
        raise ParentCategoryNotInHierarchy()

  def edit(self, existing_categories: list[ProductCategory], draft_categories: list[ProductCategoryDraft], ids):
    if self.status not in [ProductCategoryHierarchyStatus.DRAFT]:
      raise CategoryHierarchyCannotBeEdited()
    if not self.contains_all_product_categories([category.category_id for category in existing_categories]):
      raise CategoryDoesNotBelongToHierarchy()
    new_id_by_temp = {draft_category.temp_id: ids[i] for i, draft_category in enumerate(draft_categories)}
    new_categories = [ProductCategory(name=item.name, category_id=new_id_by_temp[item.temp_id], parent_id=new_id_by_temp[item.parent_id] if item.parent_id in new_id_by_temp else item.parent_id) for item in draft_categories]
    self._update_parent_ids(existing_categories, new_id_by_temp)
    categories = existing_categories + new_categories
    self._validate_hierarchy(categories)
    self.product_categories = categories
    
  def _update_parent_ids(self, existing_categories: list[ProductCategory], new_id_by_temp):
    for category in existing_categories:
      if category.category_id in new_id_by_temp:
        category.change_parent(new_id_by_temp[category.category_id])

  def update_categories(self, new_product_category_nodes : list[ProductCategory]):
    if self.status != ProductCategoryHierarchyStatus.DRAFT:
      raise OnlyDraftHierarchyCanBeUpdated()
    self._validate_hierarchy(new_product_category_nodes)
    self.product_categories = new_product_category_nodes
    #save -> update hierarchy


  def ensure_can_be_edited(self, existing_product_categories):
    if self.status not in [ProductCategoryHierarchyStatus.DRAFT]:
      raise CategoryHierarchyCannotBeEdited()


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

  def contains_product_category(self, category_id):
    return category_id in [category.category_id for category in self.product_categories]

  def contains_all_product_categories(self, product_category_ids):
    return all(self.contains_product_category(category_id) for category_id in product_category_ids)




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