import assert from "node:assert/strict";
import test from "node:test";
import {
  buildCategoryOptions,
  isProductInCategory,
} from "../src/utils/categories.js";

test("builds full paths even when children arrive before their parents", () => {
  const options = buildCategoryOptions([
    { category_id: 3, parent_id: 2, name: "Jogurty" },
    { category_id: 1, parent_id: null, name: "Produkty" },
    { category_id: 2, parent_id: 1, name: "Nabiał" },
  ]);
  const selected = options.find((category) => category.category_id === 3);
  assert.equal(selected.label, "Produkty / Nabiał / Jogurty");
  assert.deepEqual(
    selected.path.map((category) => category.category_id),
    [1, 2, 3],
  );
});

test("handles empty data, missing parents and malformed cycles safely", () => {
  assert.deepEqual(buildCategoryOptions([]), []);
  assert.equal(
    buildCategoryOptions([{ category_id: 1, parent_id: 99, name: "Owoce" }])[0]
      .label,
    "Owoce",
  );
  const cyclic = buildCategoryOptions([
    { category_id: 1, parent_id: 2, name: "A" },
    { category_id: 2, parent_id: 1, name: "B" },
  ]);
  assert.ok(cyclic.every((category) => category.path.length === 2));
});

test("favorites match both their own category and ancestors, not unrelated branches", () => {
  const product = {
    category_path: [{ category_id: 1 }, { category_id: 2 }, { category_id: 3 }],
  };
  assert.equal(isProductInCategory(product, null), true);
  assert.equal(isProductInCategory(product, 1), true);
  assert.equal(isProductInCategory(product, 3), true);
  assert.equal(isProductInCategory(product, 4), false);
  assert.equal(isProductInCategory({ category_path: [] }, 1), false);
});

test("a snack category includes each descendant while a selected child excludes siblings", () => {
  const categories = [
    { category_id: 1, parent_id: null, name: "Słodycze i przekąski" },
    { category_id: 2, parent_id: 1, name: "Lody i mrożone desery" },
    { category_id: 3, parent_id: 1, name: "Słodycze" },
    { category_id: 4, parent_id: 1, name: "Słone przekąski" },
    { category_id: 5, parent_id: 1, name: "Dżemy, miody i kremy" },
    { category_id: 6, parent_id: 3, name: "Czekolady" },
  ];
  const options = buildCategoryOptions(categories);
  const products = options.slice(1).map(category => ({ category_path: category.path }));
  assert.equal(products.filter(product => isProductInCategory(product, 1)).length, 5);
  assert.equal(products.filter(product => isProductInCategory(product, 3)).length, 2);
  assert.equal(products.filter(product => isProductInCategory(product, 5)).length, 1);
  assert.equal(options.find(category => category.category_id === 6).label, "Słodycze i przekąski / Słodycze / Czekolady");
});
