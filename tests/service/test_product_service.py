import pytest

from api.schemas.product import ProductDetail

@pytest.mark.asyncio
async def test_get_correct_id(fake_product_repository):
  fpr = fake_product_repository([ProductDetail(id=8, name="Raw Energy Baton kakaowy Bombus", brand="BB", kcal=300, reference_unit="g", category=[], reference_amount=100)])
  product = await fpr.get(8)
  assert product.id == 8


@pytest.mark.asyncio
async def test_get_wrong_id(fake_product_repository):
  fpr = fake_product_repository([ProductDetail(id=8, name="Raw Energy Baton kakaowy Bombus", brand="BB", kcal=300, reference_unit="g", category=[], reference_amount=100)])
  product = await fpr.get(10)
  assert product is None

@pytest.mark.asyncio
async def test_get_all_without_arguments(fake_product_repository):
  fpr = fake_product_repository(
    [ProductDetail(id=8, name="Raw Energy Baton kakaowy Bombus", brand="BB", kcal=300, reference_unit="g", category=[], reference_amount=100),
     ProductDetail(id=80, name="Raw Dzik", brand="BB", kcal=300, reference_unit="g", category=[], reference_amount=100)
     ])
  products = await fpr.get_all()
  assert len(products) == 2