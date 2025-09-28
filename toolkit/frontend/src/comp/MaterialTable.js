import React from "react";
import BasicBlock from "../unit/BasicBlock";

// ---- schema ----
export const schema = [
  { inputType: "text", label: "PTH material", path: "materialSelected.pth", default: "None", type: "text" },
];

export default function MaterialTable({ data, setData }) {
  return (
    <BasicBlock
      title="Material"
      data={data}
      setData={setData}
      schema={schema}
    />
  );
}
