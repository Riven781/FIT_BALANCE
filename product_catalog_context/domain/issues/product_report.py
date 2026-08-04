class ProductReport:
  def __init__(self, id, user_id, product_id, incorrect_values, report_status, reviewed_by = None):
    self.id = id
    self.product_id = product_id
    self.user_id = user_id
    self.incorrect_values = incorrect_values
    self.report_status = report_status
    self.reviewed_by = reviewed_by

  def change_status(self, new_status):
    self.report_status = new_status
