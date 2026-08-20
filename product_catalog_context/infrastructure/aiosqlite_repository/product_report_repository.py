from product_catalog_context.infrastructure.aiosqlite_repository.mapper import ProductReportMapper
from product_catalog_context.infrastructure.aiosqlite_repository.repository import DbRepository


class ProductReportRepository(DbRepository):
  def __init__(self, db, name='ProductReport', mapper=ProductReportMapper):
    super().__init__(db, name, mapper)

  async def get_by_id(self, report_id):
    get_report = """
    SELECT * FROM ProductReport
    WHERE id = ?
    """

    get_reported_items = """
    SELECT * FROM ProductReportItem reported_item
    LEFT JOIN ProductIssue issue ON issue.id = reported_item.issue_id
    WHERE report_id = ?
    """

    async with self.db.execute(get_report, (report_id, )) as cursor:
      report_row = await cursor.fetchone()

    if report_row is None:
      return None

    async with self.db.execute(get_reported_items, (report_id, )) as cursor:
      reported_items = await cursor.fetchall()

    report_dict = dict(report_row)
    print(report_dict)
    report_dict['reported_items'] = reported_items

    return self.mapper.to_report(report_dict)

  async def insert(self, report):
    report_dict = self.mapper.to_storage_dict(report)
    reported_items = report_dict.pop("reported_items")

    insert_report_query = f"""
    INSERT INTO ProductReport ({', '.join(report_dict.keys())}) VALUES ({', '.join(['?'for _ in report_dict.keys()])})
    """
    async with self.db.execute(insert_report_query, list(report_dict.values())) as cursor:
      report_id = cursor.lastrowid

    if not reported_items:
      return report_id

    for reported_item in reported_items:
      reported_item['report_id'] = report_id

    val_row = '(' + ', '.join(['?' for _ in  reported_items[0].keys()])+ ')'
    val_cols = ', '.join([val_row for _ in  reported_items])

    insert_reported_items = f"""
    INSERT INTO ProductReportItem ({', '.join(reported_items[0].keys())})
    VALUES {val_cols}
    """

    print(insert_reported_items)

    args = [val for reported_item in reported_items for val in reported_item.values()]

    async with self.db.execute(insert_reported_items, args) as cursor:
      pass

    return report_id

    


