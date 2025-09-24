export function setValueAtPath(obj, path, value) {
  const keys = path.split(".");
  const root = { ...obj };
  let cur = root;
  keys.forEach((key, i) => {
    if (i === keys.length - 1) {
      cur[key] = value;
    } else {
      const next = cur[key];
      const cloned =
        next && typeof next === "object" ? (Array.isArray(next) ? [...next] : { ...next }) : {};
      cur[key] = cloned;
      cur = cur[key];
    }
  });
  return root;
}

export function getValue(obj, path, fallback = "") {
  return path
    .split(".")
    .reduce((acc, k) => (acc && acc[k] !== undefined ? acc[k] : undefined), obj) ?? fallback;
}

export function coerce(type, v) {
  if (type === "number") return v === "" ? "" : Number(v);
  return v;
}

export function deepMergeMissing(dst, src) {
  if (dst === undefined) return src;
  if (src === undefined) return dst;
  if (Array.isArray(dst) || Array.isArray(src)) return dst;
  if (typeof dst === "object" && dst && typeof src === "object" && src) {
    const out = { ...dst };
    for (const k of Object.keys(src)) {
      out[k] = deepMergeMissing(dst[k], src[k]);
    }
    return out;
  }
  return dst;
}

export function buildDefaults(schema) {
  return schema.reduce((acc, f) => setValueAtPath(acc, f.path, f.default ?? ""), {});
}

// combine any number of schemas
export function combineDefaults(schemas) {
  return schemas.reduce((acc, s) => deepMergeMissing(acc, buildDefaults(s)), {});
}