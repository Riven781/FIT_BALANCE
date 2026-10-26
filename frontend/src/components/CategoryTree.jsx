import React, { useMemo, useState } from "react";
import { ChevronRight } from "lucide-react";

function CategoryBranch({
  category,
  childrenByParent,
  value,
  selectedPath,
  onChange,
  ancestors,
}) {
  const [expanded, setExpanded] = useState(null);
  const children = childrenByParent.get(category.category_id) || [];
  const hasChildren = children.length > 0;
  const containsSelection = selectedPath.some(
    (item) => item.category_id === category.category_id,
  );
  const open = expanded ?? containsSelection;
  const visited = new Set([...ancestors, category.category_id]);

  return (
    <li>
      <div
        className={`category-tree-row ${value === category.category_id ? "selected" : ""}`}
      >
        {hasChildren ? (
          <button
            className="category-tree-toggle"
            aria-expanded={open}
            aria-label={`${open ? "Zwiń" : "Rozwiń"} kategorię ${category.name}`}
            onClick={() => setExpanded(!open)}
          >
            <ChevronRight size={17} className={open ? "expanded" : ""} />
          </button>
        ) : (
          <span className="category-tree-spacer" />
        )}
        <button
          className="category-tree-choice"
          onClick={() => {
            onChange(category.category_id);
            if (hasChildren) setExpanded(true);
          }}
          aria-current={value === category.category_id ? "true" : undefined}
        >
          <span>{category.name}</span>
          {hasChildren && <small>Cała kategoria</small>}
        </button>
      </div>
      {hasChildren && open && (
        <ul>
          {children
            .filter((child) => !visited.has(child.category_id))
            .map((child) => (
              <CategoryBranch
                key={child.category_id}
                category={child}
                childrenByParent={childrenByParent}
                value={value}
                selectedPath={selectedPath}
                onChange={onChange}
                ancestors={visited}
              />
            ))}
        </ul>
      )}
    </li>
  );
}

export default function CategoryTree({ options, value, onChange }) {
  const childrenByParent = useMemo(() => {
    const result = new Map();
    const ids = new Set(options.map((category) => category.category_id));
    for (const category of options) {
      const parentId = ids.has(category.parent_id) ? category.parent_id : null;
      if (!result.has(parentId)) result.set(parentId, []);
      result.get(parentId).push(category);
    }
    return result;
  }, [options]);
  const selectedPath =
    options.find((category) => category.category_id === value)?.path || [];

  return (
    <nav className="category-tree" aria-label="Hierarchia kategorii produktów">
      <button
        className={`category-tree-all ${value === null ? "selected" : ""}`}
        onClick={() => onChange(null)}
        aria-current={value === null ? "true" : undefined}
      >
        Wszystkie produkty
      </button>
      <ul>
        {(childrenByParent.get(null) || []).map((category) => (
          <CategoryBranch
            key={category.category_id}
            category={category}
            childrenByParent={childrenByParent}
            value={value}
            selectedPath={selectedPath}
            onChange={onChange}
            ancestors={new Set()}
          />
        ))}
      </ul>
    </nav>
  );
}
