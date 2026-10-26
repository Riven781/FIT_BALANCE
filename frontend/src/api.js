const base = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");
async function fetchJson(path, signal) {
  const response = await fetch(`${base}${path}`, {
    signal,
    headers: { Accept: "application/json" },
  });
  if (!response.ok)
    throw new Error(
      response.status === 404
        ? "Nie znaleziono danych w katalogu."
        : `Nie udało się pobrać danych (HTTP ${response.status}). Spróbuj ponownie.`,
    );
  return response.json();
}
export const request = (path, signal) => fetchJson(`/api/v1${path}`, signal);
export const getCategoryHierarchy = (signal) => {
  const hierarchyId = import.meta.env.VITE_CATEGORY_HIERARCHY_ID || "1";
  return fetchJson(
    `/category-hierarchy/${encodeURIComponent(hierarchyId)}`,
    signal,
  );
};
export const getProduct = (id, signal) =>
  request(`/products/${encodeURIComponent(id)}`, signal);
export const getProducts = (params, signal) =>
  request(`/products?${new URLSearchParams(params)}`, signal);
