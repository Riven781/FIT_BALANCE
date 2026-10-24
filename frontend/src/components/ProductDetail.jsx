import React, { useEffect, useRef, useState } from "react";
import { X, Heart, Flame } from "lucide-react";
import { getProduct } from "../api";
import { format } from "../utils/format";
import ProductImage from "./ProductImage";

export default function ProductDetail({ id, close, saved, toggle }) {
  const dialog = useRef(null);
  const [product, setProduct] = useState(null),
    [error, setError] = useState(""),
    [portion, setPortion] = useState("100");
  useEffect(() => {
    const previous = document.activeElement;
    dialog.current.showModal();
    return () => previous?.focus();
  }, []);
  useEffect(() => {
    const controller = new AbortController();
    getProduct(id, controller.signal)
      .then((p) => {
        setProduct(p);
        setPortion(String(p.nutrition_facts.reference_quantity.amount));
      })
      .catch((e) => {
        if (e.name !== "AbortError") setError(e.message);
      });
    return () => controller.abort();
  }, [id]);
  const facts = product?.nutrition_facts;
  const multiplier = facts
    ? Number(portion) / facts.reference_quantity.amount
    : 1;
  return (
    <dialog
      ref={dialog}
      onCancel={close}
      onClick={(e) => {
        if (e.target === dialog.current) close();
      }}
      aria-labelledby="detail-title"
    >
      <div className="detail-content">
        <button
          className="icon-button close"
          aria-label="Zamknij szczegóły"
          onClick={close}
        >
          <X />
        </button>
        {error ? (
          <div role="alert" className="state">
            <h2 id="detail-title">Nie udało się otworzyć produktu</h2>
            <p>{error}</p>
          </div>
        ) : !product ? (
          <div className="state" role="status">
            <h2 id="detail-title">Wczytywanie produktu…</h2>
          </div>
        ) : (
          <>
            <ProductImage product={product} large />
            <div className="detail-body">
              <p className="eyebrow">
                {product.brand_name || "Produkt spożywczy"}
              </p>
              <h2 id="detail-title">{product.name}</h2>
              <p className="muted">
                {product.category_path.map((c) => c.name).join(" / ") ||
                  "Wartości odżywcze produktu"}
              </p>
              <button
                className={`save-button ${saved ? "active" : ""}`}
                onClick={() => toggle(id)}
              >
                <Heart size={17} fill={saved ? "currentColor" : "none"} />
                {saved ? "Zapisano w ulubionych" : "Zapisz w ulubionych"}
              </button>
              <div className="portion">
                <label htmlFor="portion">Twoja porcja</label>
                <div>
                  <input
                    id="portion"
                    type="number"
                    min="0"
                    max="100000"
                    step="any"
                    value={portion}
                    onChange={(e) => setPortion(e.target.value)}
                  />
                  <span>{facts.reference_quantity.unit}</span>
                </div>
              </div>
              <p className="muted small">
                Dane źródłowe na {facts.reference_quantity.amount}{" "}
                {facts.reference_quantity.unit}. Wartości przeliczane dla
                podanej porcji.
              </p>
              <div className="energy">
                <span>
                  <Flame size={20} /> Wartość energetyczna
                </span>
                <strong>
                  {format(facts.kcal * multiplier)} <small>kcal</small>
                </strong>
              </div>
              <table>
                <caption className="sr-only">
                  Wartości odżywcze dla porcji
                </caption>
                <tbody>
                  {[
                    ["fat", "Tłuszcze"],
                    ["saturates", "w tym kwasy nasycone"],
                    ["carbohydrates", "Węglowodany"],
                    ["sugars", "w tym cukry"],
                    ["fiber", "Błonnik"],
                    ["protein", "Białko"],
                    ["salt", "Sól"],
                  ].map(([key, label]) => (
                    <tr key={key}>
                      <th scope="row">{label}</th>
                      <td>
                        {format(
                          facts.nutrients[key] == null
                            ? null
                            : facts.nutrients[key] * multiplier,
                        )}{" "}
                        g
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p className="muted small">„—” oznacza brak danych w katalogu.</p>
            </div>
          </>
        )}
      </div>
    </dialog>
  );
}
