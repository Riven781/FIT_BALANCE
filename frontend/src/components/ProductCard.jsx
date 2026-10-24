import React from "react";
import { ArrowRight, Flame, Heart } from "lucide-react";
import { format } from "../utils/format";
import ProductImage from "./ProductImage";

export default function ProductCard({
  product,
  saved,
  onOpen,
  onToggleFavorite,
}) {
  return (
    <article className="product-card">
      <div className="card-visual">
        <button
          className="image-button"
          onClick={() => onOpen(product.product_id)}
          aria-label={`Szczegóły: ${product.name}`}
        >
          <ProductImage product={product} />
        </button>
        <button
          className={`favorite-button ${saved ? "is-saved" : ""}`}
          aria-label={`${saved ? "Usuń z" : "Dodaj do"} ulubionych: ${product.name}`}
          aria-pressed={saved}
          onClick={() => onToggleFavorite(product.product_id)}
        >
          <Heart size={18} fill={saved ? "currentColor" : "none"} />
        </button>
        <span className="category-tag">
          {product.category_path.at(-1)?.name || "Produkt spożywczy"}
        </span>
      </div>
      <div className="card-body">
        <p className="product-brand">
          {product.brand_name || "Katalog produktów"}
        </p>
        <h3>
          <button onClick={() => onOpen(product.product_id)}>
            {product.name}
          </button>
        </h3>
        <div className="calories">
          <span>
            <Flame size={17} />
            <strong>{format(product.nutrition_facts.kcal)}</strong> kcal
          </span>
          <small>
            / {product.nutrition_facts.reference_quantity.amount}{" "}
            {product.nutrition_facts.reference_quantity.unit}
          </small>
        </div>
        <div className="macros">
          {[
            ["protein", "Białko", "protein"],
            ["carbohydrates", "Węglow.", "carbs"],
            ["fat", "Tłuszcze", "fat"],
          ].map(([key, label, css]) => (
            <div key={key}>
              <span>
                <i className={css} />
                {label}
              </span>
              <strong>
                {format(product.nutrition_facts.nutrients[key])}{" "}
                <small>g</small>
              </strong>
            </div>
          ))}
        </div>
        <button
          className="details-link"
          onClick={() => onOpen(product.product_id)}
        >
          Poznaj produkt <ArrowRight size={16} />
        </button>
      </div>
    </article>
  );
}
