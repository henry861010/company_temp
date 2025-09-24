import React from "react";
import { setValueAtPath, getValue, coerce } from "../utils/utils";

export default function InputUnit({ 
  data, 
  setData, 
  path, 
  label, 
  type, 
  defaultValue ,
  placeholder
}) {
  const value = getValue(data, path, defaultValue);
  const onChange = (e) => {
    const next = coerce(type, e.target.value);
    setData((prev) => setValueAtPath(prev, path, next));
  };

  return (
    <div className="flex items-center gap-2">
      <label className="w-44">{label}:</label>
      <input
        className="border px-2 py-1 rounded w-64"
        type={type === "number" ? "number" : "text"}
        value={String(value)}
        onChange={onChange}
      />
    </div>
  );
}
