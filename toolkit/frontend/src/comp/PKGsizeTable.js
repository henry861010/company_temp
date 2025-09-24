import React from "react";
import BasicBlock from "../unit/BasicBlock";

// ---- schema ----
export const schema = [
  { inputType: "text", label: "pkg bottomLeft x", path: "stiffiner.pkg_bottomLeft_x", default: 0, type: "number" },
  { inputType: "text", label: "pkg bottomLeft y", path: "stiffiner.pkg_bottomLeft_y", default: 0, type: "number" },
  { inputType: "text", label: "pkg upperRight x", path: "stiffiner.pkg_upperRight_x", default: 10000, type: "number" },
  { inputType: "text", label: "pkg upperRight y", path: "stiffiner.pkg_upperRight_y", default: 10000, type: "number" },
  { inputType: "text", label: "cow bottomLeft x", path: "stiffiner.cow_bottomLeft_x", default: 0, type: "number" },
  { inputType: "text", label: "cow bottomLeft y", path: "stiffiner.cow_bottomLeft_y", default: 0, type: "number" },
  { inputType: "text", label: "cow upperRight x", path: "stiffiner.cow_upperRight_x", default: 10000, type: "number" },
  { inputType: "text", label: "cow upperRight y", path: "stiffiner.cow_upperRight_y", default: 10000, type: "number" },
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
