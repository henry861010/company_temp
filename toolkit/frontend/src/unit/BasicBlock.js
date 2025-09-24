import React, { useEffect, useMemo } from "react";
import InputUnit from "./InputUnit";
import OptionsUnit from "./OptionsUnit";
import { deepMergeMissing, buildDefaults } from "../utils/utils";

export default function BasicBlock({ data, setData, schema, title = "Block" }) {
  // seed defaults for this schema only (non-destructive)
  const defaults = useMemo(() => buildDefaults(schema), [schema]);

  useEffect(() => {
    setData(prev => deepMergeMissing(prev ?? {}, defaults));
  }, [defaults, setData]);

  return (
    <div className="p-4 space-y-3">
      <h2 style={{margin: "2px"}}>{title}</h2>
      <div className="space-y-2" style={{ width: '350px', border: '1px solid black', borderRadius: '5px', padding: '5px', marginLeft: '5px'}}>
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
          return f.inputType === "options"
            ? <OptionsUnit {...common} options={f.options} dependsOn={f.dependsOn} />
            : <InputUnit {...common} />;
        })}
      </div>
    </div>
  );
}
