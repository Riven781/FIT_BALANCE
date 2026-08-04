class Product:
  def __init__(self, product_id, name, brand_name, nutrients):
    self._id = product_id
    self.rename(name)
    self.change_brand_name(brand_name)
    self.change_nutrients(nutrients)

  @property
  def id(self):
    return self._id
  
  @property
  def name(self) -> str:
    return self._name
  
  def rename(self, new_name : str):
    if not new_name:
      raise ValueError('Product name cannot be empty.')
    self._name = new_name

  @property
  def brand(self) -> str:
    return self._brand
  

  def change_brand_name(self, brand: str):
    if not brand:
      raise ValueError('Brand name cannot be empty.')
    self._brand = brand

  @property
  def nutrients(self):
    return self._nutrients
  

  def change_nutrients(self, nutrients):
    self._nutrients = nutrients



  


    