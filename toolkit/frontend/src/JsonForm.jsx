import React, { useMemo, useState } from "react";

// Example schema mapping: input -> JSON key path, with defaults
const schema = [
  { label: "pkg bottomLeft x",   path: "stiffiner.pkg_bottomLeft_x",   default: 0, type: "number" },
  { label: "pkg bottomLeft y",   path: "stiffiner.pkg_bottomLeft_y",   default: 0, type: "number" },
  { label: "pkg upperRight x",   path: "stiffiner.pkg_upperRight_x",   default: 10000, type: "number" },
  { label: "pkg upperRight y",   path: "stiffiner.pkg_upperRight_y",   default: 10000, type: "number" },
  { label: "cow bottomLeft x",   path: "stiffiner.cow_bottomLeft_x",   default: 0, type: "number" },
  { label: "cow bottomLeft y",   path: "stiffiner.cow_bottomLeft_y",   default: 0, type: "number" },
  { label: "cow upperRight x",   path: "stiffiner.cow_upperRight_x",   default: 10000, type: "number" },
  { label: "cow upperRight y",   path: "stiffiner.cow_upperRight_x",   default: 10000, type: "number" },
];

// Helpers
function getValue(obj, path, fallback = "") {
  return path.split(".").reduce((acc, k) => (acc && acc[k] !== undefined ? acc[k] : undefined), obj) ?? fallback;
}

// Immutable set by path (clones only along the path)
function setValueAtPath(obj, path, value) {
  const keys = path.split(".");
  const root = { ...obj };
  let cur = root;
  keys.forEach((key, i) => {
    if (i === keys.length - 1) {
      cur[key] = value;
    } else {
      const next = cur[key];
      const cloned = (next && typeof next === "object") ? (Array.isArray(next) ? [...next] : { ...next }) : {};
      cur[key] = cloned;
      cur = cur[key];
    }
  });
  return root;
}

// Build initial defaults object from schema
function buildDefaults(schema) {
  return schema.reduce((acc, field) => {
    const val = field.default !== undefined ? field.default : "";
    return setValueAtPath(acc, field.path, val);
  }, {});
}

export default function JsonForm() {
  const defaults = useMemo(() => buildDefaults(schema), []);
  const [formData, setFormData] = useState(defaults);

  const coerce = (type, v) => {
    if (type === "number") {
      // Keep empty string for controlled input; otherwise number
      return v === "" ? "" : Number(v);
    }
    return v;
    // (Extend here for boolean, date, arrays, etc.)
  };

  const handleChange = (path, rawValue, type) => {
    const value = coerce(type, rawValue);
    setFormData(prev => setValueAtPath(prev, path, value));
  };

  const handleReset = () => setFormData(defaults);

  const handleDownload = () => {
    const blob = new Blob([JSON.stringify(formData, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "data.json";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="p-4 space-y-3">
      <h1>JSON Generator</h1>

      {schema.map((field) => (
        <div key={field.path} className="flex items-center gap-2">
          <label className="w-28">{field.label}:</label>
          <input
            type={field.type === "number" ? "number" : "text"}
            value={String(getValue(formData, field.path, field.default ?? ""))}
            onChange={(e) => handleChange(field.path, e.target.value, field.type)}
            className="border px-2 py-1 rounded w-64"
          />
        </div>
      ))}

      <div className="flex gap-2">
        <button onClick={handleDownload} className="border px-3 py-1 rounded">Download JSON</button>
        <button onClick={handleReset} className="border px-3 py-1 rounded">Reset to Defaults</button>
      </div>

      <pre className="bg-gray-100 p-3 rounded overflow-auto">
        {JSON.stringify(formData, null, 2)}
      </pre>
    </div>
  );
}
