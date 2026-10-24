import React, { useState } from "react";
import { Sprout } from "lucide-react";

export default function ProductImage({ product, large = false }) {
  const [failed, setFailed] = useState(false);
  return (
    <div className={`product-image ${large ? "large" : ""}`}>
      {product.img_src && !failed ? (
        <img
          src={product.img_src}
          alt={product.name}
          onError={() => setFailed(true)}
          loading="lazy"
        />
      ) : (
        <div className="image-placeholder">
          <Sprout size={large ? 70 : 48} strokeWidth={1} />
          <span>Fit Balance</span>
        </div>
      )}
    </div>
  );
}
