/** Build full paths once, independently of the order returned by the API. */
export function buildCategoryOptions(categories) {
  const byId = new Map(
    categories.map((category) => [category.category_id, category]),
  );

  function getPath(category) {
    const path = [];
    const visited = new Set();
    let current = category;
    while (current && !visited.has(current.category_id)) {
      visited.add(current.category_id);
      path.unshift(current);
      current = byId.get(current.parent_id);
    }
    return path;
  }

  return categories
    .map((category) => {
      const path = getPath(category);
      return {
        ...category,
        path,
        label: path.map((item) => item.name).join(" / "),
      };
    })
    .sort((a, b) => a.label.localeCompare(b.label, "pl"));
}

export function isProductInCategory(product, categoryId) {
  return (
    categoryId === null ||
    product.category_path.some((item) => item.category_id === categoryId)
  );
}
