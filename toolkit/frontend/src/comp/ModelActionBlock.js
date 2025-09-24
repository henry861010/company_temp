import React, { useMemo, useEffect, useCallback, useRef, useState } from "react";
import OptionsUnit from "../unit/OptionsUnit";
import InputUnit from "../unit/InputUnit";
import { buildDefaults, deepMergeMissing } from "../utils/utils";

// schema...
const schema = [
  {
    inputType: "options",
    path: "job.action",
    label: "Rebuild",
    default: "No",
    type: "text",
    options: [
      { value: "Yes", label: "Yes" },
      { value: "No",  label: "No"  },
    ],
  },
  {
    inputType: "text",
    path: "job.cdbPath",
    label: "CDB path (server)",
    default: "",
    type: "text",
  },
  {
    inputType: "text",
    path: "job.notes",
    label: "Notes",
    default: "",
    type: "text",
  },
];

export default function ModelActionBlock({ data, setData, onSubmit }) {
  const defaults = useMemo(() => buildDefaults(schema), []);
  useEffect(() => {
    setData(prev => deepMergeMissing(prev ?? {}, defaults));
  }, [defaults, setData]);

  const fileInputRef   = useRef(null);
  const selectedFileRef = useRef(null);
  const [uploading, setUploading] = useState(false);

  // optional: build payload (now uses cdbPath)
  const buildPayload = useCallback(() => {
    const action  = data?.job?.action || "No";
    const cdbPath = data?.job?.cdbPath || "";
    const notes   = data?.job?.notes || "";
    return { action, cdbPath, notes };
  }, [data]);

  // choose file: store File object and show filename (NOTE: not a real local path)
  const onPickFile = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    selectedFileRef.current = file;

    // Show filename for user feedback
    setData(prev => ({
      ...prev,
      job: { ...(prev?.job || {}), cdbPath: file.name }
    }));
    e.target.value = "";
  };

  // upload to server -> return server path/url
  const uploadFileAndGetServerPath = async (file) => {
    const fd = new FormData();
    fd.append("file", file);
    const res = await fetch("/api/upload", { method: "POST", body: fd });
    if (!res.ok) throw new Error(`Upload failed (${res.status})`);
    // Expect JSON: { path: "/uploads/abc123.bin", url?: "https://..." }
    return res.json();
  };

  const handleSubmit = async () => {
    const action = data?.job?.action || "No";
    const notes  = data?.job?.notes || "";
    let serverPath = data?.job?.cdbPath || ""; // <-- use cdbPath

    try {
      if (selectedFileRef.current) {
        setUploading(true);
        const { path, url } = await uploadFileAndGetServerPath(selectedFileRef.current);
        serverPath = path || url || serverPath;

        // persist the server path
        setData(prev => ({
          ...prev,
          job: { ...(prev?.job || {}), cdbPath: serverPath }
        }));
      }

      if (!serverPath) {
        alert("Please choose a file and/or provide a server CDB path.");
        return;
      }

      const payload = { action, cdbPath: serverPath, notes };
      // or: const payload = buildPayload(); // if you prefer
      onSubmit?.(payload);
    } catch (err) {
      console.error(err);
      alert(err.message || "Upload error.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-3 border rounded-md p-3">
      <h2 className="font-semibold" style={{ margin: "2px" }}>Model Action</h2>

      <div style={{ width: '350px', border: '1px solid black', borderRadius: '5px', padding: '8px', marginLeft: '5px' }}>
        <OptionsUnit
          data={data}
          setData={setData}
          path="job.action"
          label="Rebuild"
          type="text"
          defaultValue="No"
          options={[
            { value: "Yes", label: "Yes" },
            { value: "No",  label: "No"  },
          ]}
        />

        <div className="flex items-center gap-3">
          <InputUnit
            data={data}
            setData={setData}
            path="job.cdbPath"          // <-- use cdbPath consistently
            label="CDB path (server)"
            type="text"
            defaultValue=""
          />
          <label className="text-sm text-gray-600">
            <span className="border px-2 py-1 rounded cursor-pointer">Choose File</span>
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              onChange={onPickFile}
            />
          </label>
        </div>

        <InputUnit
          data={data}
          setData={setData}
          path="job.notes"
          label="Notes"
          type="text"
          defaultValue=""
        />

        <div className="flex gap-2 pt-2 items-center">
          <button
            className="border px-3 py-1 rounded"
            onClick={handleSubmit}
            disabled={uploading}
          >
            {uploading ? "Uploading..." : "Submit"}
          </button>
        </div>
      </div>
    </div>
  );
}
