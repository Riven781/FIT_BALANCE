export const format = (value) =>
  value == null
    ? "—"
    : new Intl.NumberFormat("pl-PL", { maximumFractionDigits: 1 }).format(
        value,
      );
