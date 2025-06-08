import React, { useState } from 'react';

function JsonEditor() {
  const [jsonData, setJsonData] = useState(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const data = JSON.parse(event.target.result);
      setJsonData(data);
    };
    reader.readAsText(file);
  };

  const handleValueChange = (section, key, field, value) => {
    setJsonData(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [key]: {
          ...prev[section][key],
          [field]: value
        }
      }
    }));
  };

  const downloadModifiedJson = () => {
    const blob = new Blob([JSON.stringify(jsonData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'modified.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  const renderEditableSection = (title, sectionName, keys) => (
    <>
      <h3>{title}</h3>
      {keys.map((key) => (
        <div key={key} style={{ marginBottom: '10px' }}>
          <strong>{key}</strong>
          {Object.entries(jsonData[sectionName][key]).map(([field, value]) => (
            <div key={field}>
              <label>{field}: </label>
              <input
                value={value}
                onChange={(e) => handleValueChange(sectionName, key, field, e.target.value)}
              />
            </div>
          ))}
        </div>
      ))}
    </>
  );

  const renderOrderedContent = () => {
    if (!jsonData) return null;

    const layers = Object.keys(jsonData.layer || {});
    const players = Object.keys(jsonData.player || {});
    const cores = Object.keys(jsonData.core || {});

    const halfL = Math.floor(layers.length / 2);
    const halfP = Math.floor(players.length / 2);

    return (
      <>
        {renderEditableSection("Layers (Top Half)", "layer", layers.slice(0, halfL))}
        {renderEditableSection("Players (Top Half)", "player", players.slice(0, halfP))}
        {renderEditableSection("Cores", "core", cores)}
        {renderEditableSection("Players (Bottom Half)", "player", players.slice(halfP))}
        {renderEditableSection("Layers (Bottom Half)", "layer", layers.slice(halfL))}
      </>
    );
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>JSON Viewer and Editor</h2>
      <input type="file" accept=".json" onChange={handleFileChange} />

      {jsonData && (
        <>
          {renderOrderedContent()}
          <button onClick={downloadModifiedJson} style={{ marginTop: 20 }}>
            Download Modified JSON
          </button>
        </>
      )}
    </div>
  );
}

export default JsonEditor;
