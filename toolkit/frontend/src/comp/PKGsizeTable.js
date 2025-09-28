import React from "react";
import BasicBlock from "../unit/BasicBlock";

// ---- schema ----
export const schema = [
  { inputType: "text", label: "cow size x", path: "stiffiner.cow_size_x", default: 0, type: "number" },
  { inputType: "text", label: "cow size y", path: "stiffiner.cow_size_y", default: 0, type: "number" },
  { inputType: "text", label: "stiffiner offset East", path: "stiffiner.stiffinerOffsetEastX", default: 200, type: "number" },
  { inputType: "text", label: "stiffiner offset West", path: "stiffiner.stiffinerOffsetWestX", default: 200, type: "number" },
  { inputType: "text", label: "stiffiner offset North", path: "stiffiner.stiffinerOffsetNorthY", default: 200, type: "number" },
  { inputType: "text", label: "stiffiner offset Sourth", path: "stiffiner.stiffinerOffsetSourthY", default: 200, type: "number" },
  { inputType: "text", label: "stiffiner thk East", path: "stiffiner.stiffinerThkEastX", default: 200, type: "number" },
  { inputType: "text", label: "stiffiner thk West", path: "stiffiner.stiffinerThkWestX", default: 200, type: "number" },
  { inputType: "text", label: "stiffiner thk North", path: "stiffiner.stiffinerThkNorthY", default: 200, type: "number" },
  { inputType: "text", label: "stiffiner thk Sourth", path: "stiffiner.stiffinerThkSourthY", default: 200, type: "number" },
  { inputType: "text", label: "stiffiner cut East", path: "stiffiner.stiffinerCutEastX", default: 200, type: "number" },
  { inputType: "text", label: "stiffiner cut West", path: "stiffiner.stiffinerCutWestX", default: 200, type: "number" },
  { inputType: "text", label: "stiffiner cut North", path: "stiffiner.stiffinerCutNorthY", default: 200, type: "number" },
  { inputType: "text", label: "stiffiner cut Sourth", path: "stiffiner.stiffinerCutSourthY", default: 200, type: "number" },
];

export default function PKGsizeTable({ data, setData }) {
  return (
    <BasicBlock
      title="PKG size"
      data={data}
      setData={setData}
      schema={schema}
    />
  );
}
