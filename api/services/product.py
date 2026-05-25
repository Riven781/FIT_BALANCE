from typing import Annotated

from fastapi import Depends

from api.dependencies.filters import ProductsFilters
from api.enums.product import NameMode, ViewMode
from api.schemas.product import ProductDetail, ProductSummary



def name_filter(name_query, name, mode):
  if mode == NameMode.CONTAINS:
    return name_query.lower() in name.lower()
  if mode == NameMode.STARTS_WITH:
    return name.lower().startswith(name_query.lower())
  if mode == NameMode.EXAC:
    return name == name_query


def get_products(products_filters: ProductsFilters, product_by_id, products_hierarchy):
  results = set(product_by_id)
  if products_filters.category is not None:
    matched_category = products_hierarchy.get(products_filters.category)
    if matched_category is None:
      return []
    products_id = matched_category['products']
    results = results.intersection(products_id)
  if products_filters.name:
    results = set(id for id in results if name_filter(products_filters.name, product_by_id[id]['name'], products_filters.name_mode))
  
  products_result = [ProductDetail(**product_by_id[id]) if products_filters.view_mode == ViewMode.DETAIL else ProductSummary(**product_by_id[id])  for id in results]

  products_result = sorted(products_result, key=lambda product: getattr(product, products_filters.sort_by.value), reverse=True if products_filters.order == 'desc' else False)

  return products_result