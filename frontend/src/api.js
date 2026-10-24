const base = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");
export async function request(path, signal) {
  const response = await fetch(`${base}/api/v1${path}`, {
    signal,
    headers: { Accept: "application/json" },
  });
  if (!response.ok)
    throw new Error(
      response.status === 404
        ? "Nie znaleziono produktu."
        : `Nie udało się pobrać danych (HTTP ${response.status}). Spróbuj ponownie.`,
    );
  return response.json();
}
export const getProduct = (id, signal) =>
  request(`/products/${encodeURIComponent(id)}`, signal);
export const getProducts = (params, signal) =>
  request(`/products?${new URLSearchParams(params)}`, signal);
