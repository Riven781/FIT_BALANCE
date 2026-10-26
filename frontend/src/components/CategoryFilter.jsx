import React from "react";
import { ChevronRight, Layers, X } from "lucide-react";
import "./CategoryFilter.css";
import CategoryTree from "./CategoryTree";

export default function CategoryFilter({
  options,
  loading,
  error,
  retry,
  value,
  onChange,
}) {
  const selected = options.find((category) => category.category_id === value);
  const children = options.filter((category) => category.parent_id === value);

  return (
    <section
      className="category-filter"
      aria-labelledby="category-filter-title"
    >
      <div className="category-filter-heading">
        <div>
          <h3 id="category-filter-title">
            <Layers size={18} /> Odkrywaj kategoriami
          </h3>
          <p>
            Kliknij nazwę, aby zobaczyć całą kategorię z podkategoriami.
            Strzałką rozwiń bardziej szczegółowy wybór.
          </p>
        </div>
        <label className="category-select">
          <span className="sr-only">Wybierz kategorię produktów</span>
          <select
            value={value ?? ""}
            disabled={loading || !options.length}
            onChange={(event) =>
              onChange(
                event.target.value === "" ? null : Number(event.target.value),
              )
            }
          >
            <option value="">
              {loading ? "Wczytywanie kategorii…" : "Wszystkie kategorie"}
            </option>
            {options.map((category) => (
              <option key={category.category_id} value={category.category_id}>
                {category.label}
              </option>
            ))}
          </select>
        </label>
      </div>
      {error ? (
        <div className="category-message" role="alert">
          <span>{error}</span>
          <button onClick={retry}>Spróbuj ponownie</button>
        </div>
      ) : loading ? (
        <p className="category-message" role="status">
          Przygotowujemy kategorie do odkrycia…
        </p>
      ) : !options.length ? (
        <p className="category-message">
          W katalogu nie ma jeszcze kategorii. Wyszukaj produkt po nazwie.
        </p>
      ) : (
        <>
          <details className="category-tree-menu" open>
            <summary>Przeglądaj drzewo kategorii</summary>
            <CategoryTree options={options} value={value} onChange={onChange} />
          </details>
          <nav
            className="category-path"
            aria-label="Ścieżka wybranej kategorii"
          >
            <button
              onClick={() => onChange(null)}
              aria-current={value === null ? "true" : undefined}
            >
              Wszystkie produkty
            </button>
            {selected?.path.map((category) => (
              <React.Fragment key={category.category_id}>
                <ChevronRight size={14} aria-hidden="true" />
                <button
                  onClick={() => onChange(category.category_id)}
                  aria-current={
                    category.category_id === value ? "true" : undefined
                  }
                >
                  {category.name}
                </button>
              </React.Fragment>
            ))}
          </nav>
          {children.length > 0 && (
            <div
              className="category-suggestions"
              role="group"
              aria-label={selected ? "Podkategorie" : "Kategorie główne"}
            >
              {children.map((category) => (
                <button
                  key={category.category_id}
                  onClick={() => onChange(category.category_id)}
                >
                  {category.name}
                  <ChevronRight size={14} />
                </button>
              ))}
            </div>
          )}
          {selected && (
            <div className="category-active" role="status">
              <span>
                Wyszukujesz w: <strong>{selected.name}</strong> i jej
                podkategoriach
              </span>
              <button
                onClick={() => onChange(null)}
                aria-label="Usuń filtr kategorii"
              >
                <X size={15} /> Wyczyść kategorię
              </button>
            </div>
          )}
        </>
      )}
    </section>
  );
}
