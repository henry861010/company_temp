import React, { useEffect, useMemo } from "react";
import InputUnit from "../unit/InputUnit";
import OptionsUnit from "../unit/OptionsUnit";
import { deepMergeMissing, buildDefaults } from "../utils/utils";

// ---------- schema ----------
export const schema = [
  {
    inputType: "options",
    path: "sbt.sbtType",
    label: "SBT type",
    default: "Single",
    type: "text",
    options: ["Single", "Dual"],
  },
  {
    inputType: "options",
    path: "sbt.LayerString",
    label: "Layer string",
    default: "1-1-1",
    type: "text",
    options: (data) => {
      const sbt = data?.sbt?.sbtType;
      return sbt === "Dual"
        ? ["2-2-2", "2-3-2", "2-4-2"]
        : ["1-1-1", "1-2-1", "1-3-1"];
    },
    dependsOn: ["sbt.sbtType"],
  },
  {
    inputType: "options",
    path: "sbt.coreType",
    label: "Core type",
    default: "Throught",
    type: "text",
    options: ["Throught", "No Throught"],
  },
];

// ---------- local helpers ----------
const LAYER_DEFAULT = { thk: 10, del_thk: 10, density: 10 };

// get obj value by the path key (a.b.c.d)
function get(obj, path, fb = undefined) {
  return path.split(".").reduce((a, k) => (a && a[k] !== undefined ? a[k] : undefined), obj) ?? fb;
}

// set obj value by the path key (a.b.c.d)
function set(obj, path, value) {
  const keys = path.split(".");
  const root = { ...obj };
  let cur = root;
  keys.forEach((k, i) => {
    if (i === keys.length - 1) cur[k] = value;
    else {
      const n = cur[k];
      cur[k] = n && typeof n === "object" ? (Array.isArray(n) ? [...n] : { ...n }) : {};
      cur = cur[k];
    }
  });
  return root;
}

// parse middle number in patterns like "1-3-1" or "2-4-2"
function parseMiddle(layerString) {
  if (typeof layerString !== "string") return null;
  const m = layerString.split("-")[1];
  const n = Number(m);
  return Number.isFinite(n) ? n : null;
}

// compute how many layer objects to create
function computeLayerCount(sbtType, layerString) {
  const n = parseMiddle(layerString);
  if (!n) return 0;
  if (sbtType === "Dual") return Math.max(0, 2 * (n - 1));
  // Single (or unknown) -> 2 * n
  return 2 * n;
}

// build next `sbt.layer` keeping existing values where possible
function buildLayerTree(prevLayers = {}, count) {
  const next = {};
  for (let i = 1; i <= count; i++) {
    const key = `layer${i}`;
    next[key] = { ...LAYER_DEFAULT, ...(prevLayers?.[key] || {}) };
  }
  return next;
}

// shallow compare keys & primitive values of layer trees to avoid noisy setState
function isSameLayerTree(a = {}, b = {}) {
  const ak = Object.keys(a);
  const bk = Object.keys(b);
  if (ak.length !== bk.length) return false;
  for (const k of ak) {
    const av = a[k] || {};
    const bv = b[k] || {};
    if (av.thk !== bv.thk || av.del_thk !== bv.del_thk || av.density !== bv.density) {
      return false;
    }
  }
  return true;
}

function LayerEditor({ data, setData }) {
  const layers = data?.sbt?.layer ?? {};

  const layerKeys = React.useMemo(
    () =>
      Object.keys(layers).sort((a, b) => {
        const ai = Number(String(a).replace(/[^\d]/g, "")) || 0;
        const bi = Number(String(b).replace(/[^\d]/g, "")) || 0;
        return ai - bi;
      }),
    [layers]
  );

  if (layerKeys.length === 0) {
    return <div className="text-sm text-gray-500">No layers to edit.</div>;
  }

  return (
    <div className="space-y-2">
      <div className="grid grid-cols-4 gap-2 items-start" style={{padding: "5px"}}>
        {layerKeys.map((key) => (
          <React.Fragment key={key}>
            {/* left column: layer label */}
            <div className="text-sm font-medium">{key}</div>

            {/* right column: block of three inputs with outline */}
            <div style={{marginLeft: '10px'}}>
              <InputUnit
                data={data}
                setData={setData}
                path={`sbt.layer.${key}.thk`}
                label="Thk"
                type="number"
                defaultValue={10}
              />
              <InputUnit
                data={data}
                setData={setData}
                path={`sbt.layer.${key}.del_thk`}
                label="Del_Thk"
                type="number"
                defaultValue={10}
              />
              <InputUnit
                data={data}
                setData={setData}
                path={`sbt.layer.${key}.density`}
                label="Density"
                type="number"
                defaultValue={10}
              />
            </div>
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}

export default function SBTlayerTable({ data, setData }) {
  const defaults = useMemo(() => buildDefaults(schema), []);

  // seed defaults for sbt.sbtType / sbt.LayerString / sbt.coreType
  useEffect(() => {
    setData((prev) => deepMergeMissing(prev ?? {}, defaults));
  }, [defaults, setData]);

  useEffect(() => {
    const sbtType = get(data, "sbt.sbtType", "Single");
    const layerStr = get(data, "sbt.LayerString", "1-1-1");
    const desiredCount = computeLayerCount(sbtType, layerStr);

    const prevLayers = get(data, "sbt.layer", {});
    const nextLayers = buildLayerTree(prevLayers, desiredCount);

    if (!isSameLayerTree(prevLayers, nextLayers)) {
      setData((prev) => set(prev, "sbt.layer", nextLayers));
    }
  }, [data?.sbt?.sbtType, data?.sbt?.LayerString, setData]);

  return (
    <div className="p-4 space-y-3" >
      <h2  style={{margin: "2px"}}>SBT layer</h2>
      <div style={{ width: '350px', border: '1px solid black', borderRadius: '5px', padding: '5px', marginLeft: '5px' }}>
        <div className="space-y-2" style={{ width: '330px', height: '75px', border: '1px solid black', borderRadius: '5px'}}>
          {schema.map((f) => {
            const common = {
              key: f.path,
              data,
              setData,
              path: f.path,
              label: f.label,
              type: f.type,
              defaultValue: f.default,
            };
            return f.inputType === "options" ? (
              <OptionsUnit {...common} options={f.options} dependsOn={f.dependsOn} />
            ) : (
              <InputUnit {...common} />
            );
          })}
        </div>
        <LayerEditor data={data} setData={setData} />
      </div>
      
    </div>
  );
}
