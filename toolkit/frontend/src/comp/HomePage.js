import React, { useMemo, useState, useCallback } from "react";
import SBTlayerTable, { schema as schema1 } from "./SBTlayerTable";
import PKGsizeTable, { schema as schema2 } from "./PKGsizeTable";
import ModelActionBlock from "./ModelActionBlock";
import { deepMergeMissing, combineDefaults } from "../utils/utils";

const all_schema = [schema1, schema2]
const tables = [PKGsizeTable, SBTlayerTable];

// ---------- helpers ----------
const handleModelSubmit = (payload) => {
  console.log("Submitting payload:", payload);
  // call your API here
  // fetch("/api/model-run", { method: "POST", headers: {...}, body: JSON.stringify(payload) })
};


export default function HomePage() {
  // 1) keep schemas in an array (add more as you create more tables)
  const schemas = useMemo(() => all_schema, []);
  // 2) compute one combined defaults object
  const combinedDefaults = useMemo(() => combineDefaults(schemas), [schemas]);

  const [data, setData] = useState(combinedDefaults);

  // Optional: central Load/Paste/Reset/Download
  const loadJsonString = useCallback((text) => {
    try {
      const loaded = JSON.parse(text);
      const merged = deepMergeMissing(loaded, combinedDefaults); // keep defaults for missing keys
      setData(merged);
    } catch (e) {
      console.error(e);
      alert("Invalid JSON.");
    }
  }, [combinedDefaults]);

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => loadJsonString(String(reader.result ?? ""));
    reader.readAsText(file);
    e.target.value = "";
  };
  const handlePaste = () => {
    const text = prompt("Paste JSON here:");
    if (text != null) loadJsonString(text);
  };
  const handleReset = () => setData(combinedDefaults);
  const handleDownload = () => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = "data.json"; a.click();
    URL.revokeObjectURL(url);
  };

  // 3) (optional) render tables from a list so it scales to many


  return (
    <div className="p-4 space-y-3">
      <div className="flex items-center gap-3">
        <input type="file" accept=".json,application/json" onChange={handleFileChange} />
        <button className="border px-3 py-1 rounded" onClick={handlePaste}>Paste JSON</button>
        <button className="border px-3 py-1 rounded" onClick={handleReset}>Reset to Defaults</button>
        <button className="border px-3 py-1 rounded" onClick={handleDownload}>Download JSON</button>
      </div>

      <ModelActionBlock data={data} setData={setData} onSubmit={handleModelSubmit} />
      <PKGsizeTable key="1" data={data} setData={setData} />
      <SBTlayerTable key="2" data={data} setData={setData} />

      <pre className="bg-gray-100 p-3 rounded overflow-auto">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
}
