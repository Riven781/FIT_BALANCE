import React, { useEffect, useRef, useState } from "react";
import {
  ArrowDownUp,
  ArrowLeft,
  ArrowRight,
  Bookmark,
  Check,
  ChevronRight,
  Heart,
  Leaf,
  Search,
  SlidersHorizontal,
  Sprout,
  Utensils,
  X,
} from "lucide-react";
import { getProduct, getProducts } from "./api";
import ProductCard from "./components/ProductCard";
import ProductDetail from "./components/ProductDetail";
import CategoryFilter from "./components/CategoryFilter";
import useCategories from "./hooks/useCategories";
import usePagination from "./hooks/usePagination";
import { format } from "./utils/format";
import { isProductInCategory } from "./utils/categories";

function readSaved() {
  try {
    const value = JSON.parse(
      localStorage.getItem("fit-balance-favorites") || "[]",
    );
    return Array.isArray(value) ? value.filter(Number.isInteger) : [];
  } catch {
    return [];
  }
}
export default function App() {
  const [view, setView] = useState("catalog");
  const [query, setQuery] = useState("");
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState("name:asc");
  const [categoryId, setCategoryId] = useState(null);
  const categories = useCategories();
  const selectedCategory = categories.options.find(
    (category) => category.category_id === categoryId,
  );
  const [favorites, setFavorites] = useState(readSaved);
  const [selected, setSelected] = useState(null);
  const [data, setData] = useState([]);
  const [meta, setMeta] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [retry, setRetry] = useState(0);
  const { page, changePage, resetPage, resultsRef } = usePagination({
    loading,
    data,
    error,
  });
  const searchRef = useRef(null);
  const favoriteProducts = useRef(new Map());
  // Saving a heart in the catalog must not invalidate the product search.
  const favoriteIds = view === "favorites" ? favorites : null;
  useEffect(() => {
    const handler = (event) => {
      if (
        event.key === "/" &&
        !["INPUT", "TEXTAREA", "SELECT"].includes(
          document.activeElement?.tagName,
        ) &&
        !document.querySelector("dialog[open]")
      ) {
        event.preventDefault();
        searchRef.current?.focus();
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);
  useEffect(() => {
    const timer = setTimeout(() => {
      setSearch(query.trim());
      resetPage();
    }, 350);
    return () => clearTimeout(timer);
  }, [query, resetPage]);
  useEffect(() => {
    const controller = new AbortController();
    if (
      view !== "favorites" ||
      favoriteIds.some((id) => !favoriteProducts.current.has(id))
    )
      setLoading(true);
    setError("");
    const [sort_by, order] = sort.split(":");
    const load = async () => {
      if (view === "favorites") {
        const results = await Promise.allSettled(
          favoriteIds.map(async (id) => {
            if (favoriteProducts.current.has(id))
              return favoriteProducts.current.get(id);
            const product = await getProduct(id, controller.signal);
            if (!controller.signal.aborted)
              favoriteProducts.current.set(id, product);
            return product;
          }),
        );
        if (controller.signal.aborted) return;
        const failed = results.filter((r) => r.status === "rejected");
        if (failed.length)
          throw new Error(
            "Nie udało się pobrać części ulubionych produktów. Produkt mógł zostać usunięty lub API jest niedostępne.",
          );
        let items = results
          .map((r) => r.value)
          .filter((p) =>
            p.name
              .toLocaleLowerCase("pl")
              .includes(search.toLocaleLowerCase("pl")),
          )
          .filter((product) => isProductInCategory(product, categoryId));
        items.sort(
          (a, b) =>
            (sort_by === "kcal"
              ? a.nutrition_facts.kcal - b.nutrition_facts.kcal
              : a.name.localeCompare(b.name, "pl")) *
            (order === "asc" ? 1 : -1),
        );
        const totalPages = Math.ceil(items.length / 12);
        const currentPage = Math.min(page, Math.max(1, totalPages));
        if (currentPage !== page) resetPage(currentPage);
        setData(items.slice((currentPage - 1) * 12, currentPage * 12));
        setMeta({ total: items.length, total_pages: totalPages });
      } else {
        const response = await getProducts(
          {
            page,
            limit: 12,
            sort_by,
            order,
            ...(search ? { name: search } : {}),
            ...(categoryId !== null ? { category_id: categoryId } : {}),
          },
          controller.signal,
        );
        setData(response.data);
        setMeta(response.pagination);
      }
    };
    load()
      .catch((e) => {
        if (e.name !== "AbortError")
          setError(
            e instanceof TypeError
              ? "Nie można połączyć się z katalogiem. Sprawdź, czy backend jest uruchomiony, i spróbuj ponownie."
              : e.message,
          );
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [search, sort, page, view, favoriteIds, retry, resetPage, categoryId]);

  function selectCategory(id) {
    setCategoryId(id);
    resetPage();
  }
  function toggle(id) {
    setFavorites((old) => {
      const next = old.includes(id)
        ? old.filter((x) => x !== id)
        : [...old, id];
      try {
        localStorage.setItem("fit-balance-favorites", JSON.stringify(next));
      } catch {
        /* Favorites remain usable in memory. */
      }
      return next;
    });
  }
  function navigate(next) {
    setView(next);
    resetPage();
    setQuery("");
    setSearch("");
    setCategoryId(null);
  }
  return (
    <div className="app">
      <aside className="sidebar">
        <a
          className="brand"
          href="#"
          onClick={(e) => {
            e.preventDefault();
            navigate("catalog");
          }}
        >
          <span className="brand-icon">
            <Sprout size={26} />
          </span>
          fit<span className="brand-light">balance</span>
          <span className="brand-dot">.</span>
        </a>
        <div className="nav-label">TWOJA PRZESTRZEŃ</div>
        <nav aria-label="Menu główne">
          <button
            className={view === "catalog" ? "nav-item active" : "nav-item"}
            onClick={() => navigate("catalog")}
          >
            <Search size={19} /> Odkrywaj produkty <ChevronRight size={16} />
          </button>
          <button
            className={view === "favorites" ? "nav-item active" : "nav-item"}
            onClick={() => navigate("favorites")}
          >
            <Heart size={19} /> Ulubione{" "}
            <span className="count">{favorites.length}</span>
          </button>
        </nav>
        <div className="sidebar-tip">
          <span className="tip-icon">
            <Leaf size={22} />
          </span>
          <h3>
            Małe wybory.
            <br />
            Duża różnica.
          </h3>
          <p>Poznaj to, co jesz, i znajdź swój codzienny balans.</p>
          <div className="tip-line" />
        </div>
        <div className="sidebar-bottom">
          <Sprout size={17} /> Świadomie, każdego dnia.
        </div>
      </aside>
      <main>
        <header className="topbar">
          <span>Twój przewodnik po dobrym jedzeniu</span>
          <span className="topbar-note">
            <span /> Jedz świadomie
          </span>
        </header>
        <div className="main-content">
          <div className="breadcrumbs">
            Fit Balance <ChevronRight size={13} />{" "}
            {view === "catalog" ? "Baza produktów" : "Ulubione"}
          </div>
          <section className="hero">
            <div className="hero-copy">
              <div className="eyebrow">
                <span /> WIEDZA NA DOBRY POCZĄTEK
              </div>
              <h1>
                {view === "catalog" ? (
                  <>
                    Dobre wybory zaczynają się
                    <br className="desktop-break" /> od{" "}
                    <em>poznania składu.</em>
                  </>
                ) : (
                  <>
                    Twoje ulubione.
                    <br />
                    <em>Zawsze pod ręką.</em>
                  </>
                )}
              </h1>
              <p>
                Sprawdź kalorie i wartości odżywcze produktów.
                <br className="desktop-break" /> Odkrywaj, porównuj i jedz tak,
                jak lubisz.
              </p>
              <div className="hero-badges">
                <span>
                  <Check size={14} /> Wartości odżywcze
                </span>
                <span>
                  <Check size={14} /> Przelicznik porcji
                </span>
              </div>
            </div>
            <div className="hero-art" aria-hidden="true">
              <div className="art-circle" />
              <div className="art-orbit" />
              <div className="leaf-one">
                <Leaf />
              </div>
              <div className="leaf-two">
                <Sprout />
              </div>
              <div className="nutrition-note">
                <span className="note-symbol">
                  <Utensils size={22} />
                </span>
                <div>
                  Dobry skład.
                  <br />
                  <strong>Dobry balans.</strong>
                </div>
              </div>
              <div className="mini-note">
                <span>
                  <Check size={13} />
                </span>{" "}
                Wiesz, co jesz
              </div>
            </div>
          </section>
          <section className="catalog" aria-labelledby="catalog-title">
            <div className="section-heading">
              <div>
                <p className="eyebrow">ODKRYWAJ SWÓJ BALANS</p>
                <h2 id="catalog-title">
                  {view === "catalog" ? "Baza produktów" : "Ulubione produkty"}
                  <span className="heading-dot" />
                </h2>
              </div>
              <span className="section-note">
                <Bookmark size={16} />{" "}
                {view === "catalog"
                  ? "Znajdź coś dla siebie"
                  : "Zapisane w tej przeglądarce"}
              </span>
            </div>
            <div className="search-panel">
              <div className="search-input">
                <Search size={21} />
                <input
                  ref={searchRef}
                  aria-label="Szukaj produktu"
                  placeholder={
                    selectedCategory
                      ? `Szukaj w: ${selectedCategory.name}…`
                      : "Czego szukasz? Wpisz nazwę produktu…"
                  }
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                />
                {query && (
                  <button
                    className="icon-button"
                    aria-label="Wyczyść wyszukiwanie"
                    onClick={() => setQuery("")}
                  >
                    <X size={17} />
                  </button>
                )}
                <kbd>/</kbd>
              </div>
              <label className="sort-control">
                <ArrowDownUp size={17} />
                <span className="sr-only">Sortowanie</span>
                <select
                  value={sort}
                  onChange={(e) => {
                    setSort(e.target.value);
                    resetPage();
                  }}
                >
                  <option value="name:asc">Nazwa: A–Z</option>
                  <option value="name:desc">Nazwa: Z–A</option>
                  <option value="kcal:asc">Kalorie: rosnąco</option>
                  <option value="kcal:desc">Kalorie: malejąco</option>
                </select>
              </label>
            </div>
            <CategoryFilter
              options={categories.options}
              loading={categories.loading}
              error={categories.error}
              retry={categories.retry}
              value={categoryId}
              onChange={selectCategory}
            />
            <div
              className="results-bar"
              ref={resultsRef}
              tabIndex={-1}
              aria-label="Początek wyników wyszukiwania"
            >
              <p role="status">
                {loading ? (
                  "Wyszukiwanie produktów…"
                ) : error ? (
                  "Katalog chwilowo niedostępny"
                ) : (
                  <>
                    <strong>{format(meta?.total || 0)}</strong> produktów{" "}
                    {search ? <>dla „{search}”</> : "do odkrycia"}
                    {selectedCategory && (
                      <>
                        {" "}
                        w kategorii <strong>{selectedCategory.name}</strong>
                      </>
                    )}
                  </>
                )}
              </p>
              <span>
                <SlidersHorizontal size={14} /> Wartości na ilość referencyjną
              </span>
            </div>
            {error ? (
              <div className="state error" role="alert">
                <span className="state-icon">
                  <Leaf />
                </span>
                <h3>Jeszcze chwila, wrócimy do równowagi</h3>
                <p>{error}</p>
                <button
                  className="primary-button"
                  onClick={() => setRetry((x) => x + 1)}
                >
                  Spróbuj ponownie <ArrowRight size={16} />
                </button>
              </div>
            ) : loading && !data.length ? (
              <div
                className="product-grid"
                aria-label="Ładowanie produktów"
                aria-busy="true"
              >
                {Array.from({ length: 6 }, (_, i) => (
                  <div key={i} className="skeleton-card">
                    <div />
                    <span />
                    <span />
                  </div>
                ))}
              </div>
            ) : !data.length ? (
              <div className="state">
                <Search size={34} />
                <h3>
                  {view === "favorites" && !favorites.length
                    ? "Miejsce na Twoje ulubione"
                    : "Nie znaleźliśmy produktów"}
                </h3>
                <p>
                  {view === "favorites" && !favorites.length
                    ? "Kliknij serce na karcie produktu, aby zapisać go na później."
                    : "Spróbuj innej nazwy, wybierz szerszą kategorię lub wyczyść filtry."}
                </p>
                {categoryId !== null && (
                  <button
                    className="save-button"
                    onClick={() => selectCategory(null)}
                  >
                    Szukaj we wszystkich kategoriach <X size={16} />
                  </button>
                )}
                <button
                  className="primary-button"
                  onClick={() => {
                    navigate("catalog");
                    searchRef.current?.focus();
                  }}
                >
                  Przeglądaj produkty <ArrowRight size={16} />
                </button>
              </div>
            ) : (
              <div className="product-grid" aria-busy={loading}>
                {data.map((product) => (
                  <ProductCard
                    key={product.product_id}
                    product={product}
                    saved={favorites.includes(product.product_id)}
                    onOpen={setSelected}
                    onToggleFavorite={toggle}
                  />
                ))}
              </div>
            )}
            {!error && meta?.total_pages > 1 && (
              <nav className="pagination" aria-label="Strony wyników">
                <button
                  disabled={loading || page <= 1}
                  onClick={() => changePage(page - 1)}
                  aria-label="Poprzednia strona"
                >
                  <ArrowLeft size={17} />
                </button>
                <span>
                  Strona <strong>{page}</strong> z {meta.total_pages}
                </span>
                <button
                  disabled={loading || page >= meta.total_pages}
                  onClick={() => changePage(page + 1)}
                  aria-label="Następna strona"
                >
                  <ArrowRight size={17} />
                </button>
              </nav>
            )}
          </section>
          <footer>
            <span>
              <Sprout size={17} /> Trochę wiedzy. Więcej równowagi.
            </span>
            <span>Fit Balance · Jedz po swojemu.</span>
          </footer>
        </div>
      </main>
      {selected !== null && (
        <ProductDetail
          key={selected}
          id={selected}
          close={() => setSelected(null)}
          saved={favorites.includes(selected)}
          toggle={toggle}
        />
      )}
    </div>
  );
}
