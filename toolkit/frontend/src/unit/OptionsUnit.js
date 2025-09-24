import React, { useEffect, useMemo } from "react";
import { setValueAtPath, getValue, coerce } from "../utils/utils";

function normalizeOptions(arr) {
  const options = Array.isArray(arr) ? arr : []; // ensure array
  return options.map((opt) =>
    typeof opt === "object" && opt !== null
      ? { value: opt.value, label: opt.label ?? String(opt.value) }
      : { value: opt, label: String(opt) }
  );
}
const toSet = (items) => new Set(items.map(o => String(o.value)));

export default function OptionsUnit({
  data,
  setData,
  path,
  label,
  type,
  defaultValue,
  options,          // array OR function (data) => array
  placeholder,
  dependsOn = [],   // array of paths to watch
}) {
  const value = getValue(data, path, defaultValue);

  // Support options as function or array; always normalize to [{value,label}]
  const items = useMemo(() => {
    const raw = typeof options === "function" ? options(data) : options;
    return normalizeOptions(raw);
  }, [options, data]);

  // If current value becomes invalid due to upstream change, reset it
  useEffect(() => {
    const allowed = toSet(items);
    const current = value === undefined || value === null ? "" : String(value);

    // If there are no items, clear the value
    if (items.length === 0) {
      setData(prev => setValueAtPath(prev, path, ""));
      return;
    }
    // If current not allowed, set to default if allowed, else first option
    if (!allowed.has(current)) {
      const defaultStr = defaultValue != null ? String(defaultValue) : null;
      const fallback =
        defaultStr && allowed.has(defaultStr) ? defaultValue : items[0].value;
      setData(prev => setValueAtPath(prev, path, fallback));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    JSON.stringify(items), // changes when upstream affects options
    ...dependsOn.map(dep => getValue(data, dep, "")), // watch dependencies
  ]);

  const onChange = (e) => {
    const raw = e.target.value;
    const next = raw === "" ? "" : coerce(type, raw);
    setData(prev => setValueAtPath(prev, path, next));
  };

  const current = value === undefined || value === null ? "" : String(value);

  return (
    <div className="flex items-center gap-2">
      <label className="w-44">{label}:</label>
      <select
        className="border px-2 py-1 rounded w-64"
        value={current}
        onChange={onChange}
      >
        {placeholder !== undefined && <option value="">{placeholder}</option>}
        {items.map(opt => (
          <option key={String(opt.value)} value={String(opt.value)}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}
