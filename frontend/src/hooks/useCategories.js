import { useEffect, useMemo, useState } from "react";
import { getCategoryHierarchy } from "../api";
import { buildCategoryOptions } from "../utils/categories";

export default function useCategories() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError("");

    async function load() {
      try {
        const hierarchy = await getCategoryHierarchy(controller.signal);
        if (controller.signal.aborted) return;
        if (hierarchy.status !== "ACTIVE") {
          throw new Error(
            "Kategorie są chwilowo niedostępne. Możesz nadal przeszukiwać wszystkie produkty.",
          );
        }
        setCategories(hierarchy.product_categories);
      } catch (error) {
        if (!controller.signal.aborted) {
          setError(
            error instanceof TypeError
              ? "Nie udało się połączyć z listą kategorii."
              : error.message,
          );
        }
      } finally {
        if (!controller.signal.aborted) setLoading(false);
      }
    }

    load();
    return () => controller.abort();
  }, [attempt]);

  const options = useMemo(() => buildCategoryOptions(categories), [categories]);
  return {
    options,
    loading,
    error,
    retry: () => setAttempt((value) => value + 1),
  };
}
