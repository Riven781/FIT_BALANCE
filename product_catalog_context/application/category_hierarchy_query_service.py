from product_catalog_context.application.query.active_category_hierarchy import ActiveCategoryHierarchy, CategoryHierarchyNode
from product_catalog_context.infrastructure.aiosqlite_queries.category_hierarchy import ProductCategoryHierarchyQueries


class CategoryHierarchyQueryService:
  def __init__(self, category_hierarchy_queries : ProductCategoryHierarchyQueries):
    self.category_hierarchy_queries = category_hierarchy_queries

  async def get_hierarchy(self) -> ActiveCategoryHierarchy:
    return await self.category_hierarchy_queries.get()

  async def get_categories_by_supercategory(self, category_id) -> CategoryHierarchyNode | None:
    return await self.category_hierarchy_queries.get_by_supercategory(category_id)