-- Proposed database repair. Do not run against the application DB without approval.
-- Adds only missing self/ancestor links; does not change products or assignments.
PRAGMA foreign_keys = ON;
BEGIN IMMEDIATE;

WITH RECURSIVE ancestry(supercategory_id, subcategory_id, depth, hierarchy_id, visited) AS (
  SELECT id, id, 0, hierarchy_id, ',' || id || ','
  FROM ProductCategoryNode
  UNION ALL
  SELECT ancestry.supercategory_id, child.id, ancestry.depth + 1,
         ancestry.hierarchy_id, ancestry.visited || child.id || ','
  FROM ancestry
  JOIN ProductCategoryNode AS child
    ON child.parent_id = ancestry.subcategory_id
    AND child.hierarchy_id = ancestry.hierarchy_id
  WHERE instr(ancestry.visited, ',' || child.id || ',') = 0
)
INSERT INTO ProductCategoryClosure (supercategory_id, subcategory_id, depth)
SELECT supercategory_id, subcategory_id, depth
FROM ancestry
WHERE NOT EXISTS (
  SELECT 1 FROM ProductCategoryClosure AS existing
  WHERE existing.supercategory_id = ancestry.supercategory_id
    AND existing.subcategory_id = ancestry.subcategory_id
);

COMMIT;
