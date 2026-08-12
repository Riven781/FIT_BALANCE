import sqlite3

conn = sqlite3.connect('./shared/database/fit-balance-v2.db')

cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON")

product_table_query = """
  CREATE TABLE IF NOT EXISTS Product (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    brand_name TEXT,
    kcal REAL,
    fat REAL,
    saturates REAL,
    carbohydrates REAL,
    sugars REAL,
    protein REAL,
    salt REAL,
    fiber REAL,
    ingredients TEXT,
    allergy_recommendations TEXT,
    reference_amount INTEGER,
    reference_unit TEXT,
    img_src TEXT,
    name_search_standard TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER,
    version INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (created_by) REFERENCES User(id)
      ON DELETE SET NULL,
    FOREIGN KEY (updated_by) REFERENCES User(id)
      ON DELETE SET NULL
  ) STRICT;
"""



product_category_node_table_query = """
  CREATE TABLE IF NOT EXISTS ProductCategoryNode(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    parent_id INTEGER,
    hierarchy_id INTEGER NOT NULL,
    FOREIGN KEY (parent_id) REFERENCES ProductCategoryNode(id)
      ON DELETE SET NULL,
    FOREIGN KEY (hierarchy_id) REFERENCES ProductCategoryHierarchy(id)
      ON DELETE CASCADE
  ) STRICT;
"""

product_category_hierarchy_query = """
  CREATE TABLE IF NOT EXISTS ProductCategoryHierarchy(
    id INTEGER PRIMARY KEY,
    version INTEGER NOT NULL DEFAULT 0,
    status TEXT,
    created_by INTEGER,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    published_by INTEGER,
    published_at TEXT,
    FOREIGN KEY (created_by) REFERENCES User(id)
      ON DELETE SET NULL,
    FOREIGN KEY (published_by) REFERENCES User(id)
      ON DELETE SET NULL
  )STRICT;
"""

product_category_assignment = """
  CREATE TABLE IF NOT EXISTS ProductCategoryAssignment(
    product_id INTEGER NOT NULL,
    node_id INTEGER NOT NULL,
    assigned_by INTEGER,
    assigned_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES Product(id)
      ON DELETE CASCADE,
    FOREIGN KEY (node_id) REFERENCES ProductCategoryNode(id)
      ON DELETE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES User(id)
      ON DELETE SET NULL,
    PRIMARY KEY (product_id, node_id)
  ) STRICT;
"""

product_category_assignment_task = """
  CREATE TABLE IF NOT EXISTS ProductCategoryAssignmentTask(
    product_id INTEGER NOT NULL,
    hierarchy_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES Product(id)
      ON DELETE CASCADE,
    FOREIGN KEY (hierarchy_id) REFERENCES ProductCategoryHierarchy(id)
      ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES User(id)
      ON DELETE CASCADE,
    PRIMARY KEY (product_id, hierarchy_id)
  ) STRICT;
"""

product_category_closure_query = """
  CREATE TABLE IF NOT EXISTS ProductCategoryClosure(
    supercategory_id INTEGER,
    subcategory_id INTEGER,
    depth INTEGER NOT NULL,

    PRIMARY KEY (supercategory_id, subcategory_id),

    FOREIGN KEY (supercategory_id) REFERENCES ProductCategoryNode(id)
      ON DELETE CASCADE,
    FOREIGN KEY (subcategory_id) REFERENCES ProductCategoryNode(id)
      ON DELETE CASCADE,

    UNIQUE (subcategory_id, depth)
  );
"""

fields = """
  CREATE TABLE IF NOT EXISTS Field(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
  ) STRICT;
"""

report = """
  CREATE TABLE IF NOT EXISTS ProductReport(
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    user_id INTEGER,
    FOREIGN KEY (product_id) REFERENCES Product(id)
      ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES User(id)
      ON DELETE SET NULL 
  )STRICT;
"""

report_item = """
  CREATE TABLE IF NOT EXISTS ProductReportItem(
    id INTEGER PRIMARY KEY,
    report_id INTEGER NOT NULL,
    issue_id INTEGER NOT NULL,
    proposed_value TEXT,
    proposed_value_outcome TEXT,
    FOREIGN KEY (report_id) REFERENCES ProductReport(id)
      ON DELETE CASCADE,
    FOREIGN KEY (issue_id) REFERENCES ProductIssue(id)
      ON DELETE CASCADE
  )STRICT;
"""
issue = """
  CREATE TABLE IF NOT EXISTS ProductIssue(
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    field_id INTEGER NOT NULL,
    status TEXT,
    resolved_by INTEGER,
    FOREIGN KEY (product_id) REFERENCES Product(id)
      ON DELETE CASCADE,
    FOREIGN KEY (field_id) REFERENCES Field(id)
      ON DELETE RESTRICT,
    FOREIGN KEY (resolved_by) REFERENCES User(id)
      ON DELETE SET NULL
  ) STRICT;
"""
user = """
  CREATE TABLE IF NOT EXISTS User(
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    hashed_password TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
  ) STRICT;
"""

role = """
  CREATE TABLE IF NOT EXISTS Role(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    UNIQUE(name)
  ) STRICT;
"""

user_role = """
   CREATE TABLE IF NOT EXISTS UserRole(
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(id)
      ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES Role(id)
      ON DELETE CASCADE,
    PRIMARY KEY(user_id, role_id)
   ) STRICT;
"""
if __name__ == '__main__':
  cursor.execute(product_table_query)
  cursor.execute(product_category_node_table_query)
  cursor.execute(product_category_hierarchy_query)
  cursor.execute(product_category_assignment)
  cursor.execute(product_category_assignment_task)
  cursor.execute(product_category_closure_query)
  cursor.execute(fields)
  cursor.execute(report)
  cursor.execute(report_item)

  cursor.execute(issue)
  cursor.execute(user)
  cursor.execute(role)
  cursor.execute(user_role)

conn.commit()
conn.close()