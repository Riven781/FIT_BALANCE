import { useCallback, useEffect, useRef, useState } from "react";

/** Scroll to results only after a user requests and receives a later page. */
export default function usePagination({ loading, data, error }) {
  const [page, setPage] = useState(1);
  const resultsRef = useRef(null);
  const pendingForwardPage = useRef(null);
  const previousData = useRef(null);

  useEffect(() => {
    if (loading || pendingForwardPage.current !== page) return;
    if (data === previousData.current && !error) return;

    pendingForwardPage.current = null;
    if (error) return;

    resultsRef.current?.focus({ preventScroll: true });
    resultsRef.current?.scrollIntoView({ block: "start", behavior: "instant" });
  }, [loading, data, error, page]);

  function changePage(nextPage) {
    if (loading || nextPage < 1 || nextPage === page) return;

    pendingForwardPage.current = nextPage > page ? nextPage : null;
    previousData.current = data;
    setPage(nextPage);
  }

  const resetPage = useCallback((nextPage = 1) => {
    pendingForwardPage.current = null;
    setPage(nextPage);
  }, []);

  return { page, changePage, resetPage, resultsRef };
}
