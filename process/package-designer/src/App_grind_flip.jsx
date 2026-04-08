import React, { useState, useEffect, useRef } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Grid, Edges } from '@react-three/drei';

/** * 1. INITIAL DATA */
const initialData = {
  id: "root",
  name: "Main Substrate",
  z: 0,
  visible: true,
  showBottom: true,
  opacity: 1.0,
  face: { type: "BOX", dim: [-50, -50, 50, 50] },
  layers: [
    { material: "Core", thk: 10, color: "#444444" },
  ],
  children: []
};

// --- 3D RENDERER COMPONENTS ---

const PackageObject = ({ data, parentBaseZ = 0, selectedId, onSelect }) => {
  const { face, layers, children, z = 0, id, showBottom = true, visible = true, opacity = 1.0 } = data;
  const isSelected = selectedId === id;

  const width = Math.abs(face.dim[2] - face.dim[0]);
  const depth = Math.abs(face.dim[3] - face.dim[1]);

  const centerX = (face.dim[0] + face.dim[2]) / 2;
  const centerZ = (face.dim[1] + face.dim[3]) / 2;
  const myBottomZ = parentBaseZ + z;

  return (
    <group position={[centerX, myBottomZ, centerZ]}>
      {visible && (
        <group>
          {showBottom && (
            <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.02, 0]}>
              <planeGeometry args={[width, depth]} />
              <meshBasicMaterial
                color={isSelected ? "cyan" : "#555"}
                transparent
                opacity={isSelected ? 0.6 : 0.3 * opacity}
                side={2}
              />
            </mesh>
          )}

          {layers.reduce((acc, layer, idx) => {
            const { meshes, cumulativeThk } = acc;
            const yPos = cumulativeThk + layer.thk / 2;
            meshes.push(
              <mesh
                key={`${id}-layer-${idx}`}
                position={[0, yPos, 0]}
                onClick={(e) => { e.stopPropagation(); onSelect(id); }}
              >
                <boxGeometry args={[width, layer.thk, depth]} />
                <meshStandardMaterial
                  key={`mat-${opacity < 1}`}
                  color={isSelected ? "#ff00ff" : (layer.color || "#666")}
                  emissive={isSelected ? "#ff00ff" : "#000"}
                  emissiveIntensity={isSelected ? 0.2 : 0}
                  transparent={opacity < 1}
                  opacity={Number(opacity)}
                  depthWrite={opacity >= 1}
                />
                <Edges color={isSelected ? "cyan" : "white"} />
              </mesh>
            );
            return { meshes, cumulativeThk: cumulativeThk + layer.thk };
          }, { meshes: [], cumulativeThk: 0 }).meshes}
        </group>
      )}

      <group position={[-width / 2, 0, -depth / 2]}>
        {children.map((child) => (
          <PackageObject
            key={child.id}
            data={child}
            parentBaseZ={0}
            selectedId={selectedId}
            onSelect={onSelect}
          />
        ))}
      </group>
    </group>
  );
};

// --- MAIN APPLICATION ---

export default function App() {
  const [tree, setTree] = useState(initialData);
  const [selectedId, setSelectedId] = useState(null);

  // --- CALCULATE TOTAL HEIGHT HELPER ---
  const getNodeHeight = (node) => {
    const layerHeight = node.layers.reduce((sum, l) => sum + l.thk, 0);
    const childrenMaxReach = node.children.reduce((max, child) => {
      return Math.max(max, child.z + getNodeHeight(child));
    }, 0);
    return Math.max(layerHeight, childrenMaxReach);
  };

  // --- FLIP LOGIC ---
  const handleFlip = () => {
    const processFlip = (node) => {
      const totalH = getNodeHeight(node);
      const flippedLayers = [...node.layers].reverse();
      const flippedChildren = node.children.map(child => {
        const childH = getNodeHeight(child);
        return processFlip({
          ...child,
          z: totalH - (child.z + childH)
        });
      });

      return {
        ...node,
        layers: flippedLayers,
        children: flippedChildren
      };
    };
    setTree(processFlip(tree));
  };

  // --- GRIND LOGIC ---
  const calculateMaxZ = (node, currentBaseZ) => {
    const myBottom = currentBaseZ + node.z;
    const totalLayerThk = node.layers.reduce((sum, l) => sum + l.thk, 0);
    let maxZ = myBottom + totalLayerThk;

    node.children.forEach(child => {
      const childMax = calculateMaxZ(child, 0);
      maxZ = Math.max(maxZ, myBottom + childMax);
    });
    return maxZ;
  };

  const handleGrind = () => {
    const globalTopZ = calculateMaxZ(tree, 0);
    const depthStr = prompt(`Current Top Z: ${globalTopZ.toFixed(2)}\nHow many units to grind from the top?`, "5");
    const depth = parseFloat(depthStr);
    if (isNaN(depth) || depth <= 0) return;

    const grindPlaneZ = globalTopZ - depth;

    const processGrind = (node, parentBaseZ) => {
      const myBottomZ = parentBaseZ + node.z;
      let currentCumulative = myBottomZ;
      const newLayers = [];

      node.layers.forEach(layer => {
        const layerBottom = currentCumulative;
        const layerTop = currentCumulative + layer.thk;
        if (layerBottom < grindPlaneZ) {
          if (layerTop > grindPlaneZ) {
            newLayers.push({ ...layer, thk: grindPlaneZ - layerBottom });
          } else {
            newLayers.push(layer);
          }
        }
        currentCumulative = layerTop;
      });

      const newChildren = node.children
        .map(child => processGrind(child, 0))
        .filter(child => child.layers.length > 0 || child.children.length > 0);

      return { ...node, layers: newLayers, children: newChildren };
    };

    setTree(processGrind(tree, 0));
  };

  // --- CRUD HELPERS ---
  const updateNodeRecursive = (id, callback) => {
    const update = (node) => {
      if (node.id === id) return callback(node);
      return { ...node, children: node.children.map(update) };
    };
    setTree(update(tree));
  };

  const handleImportChild = (parentId, jsonData) => {
    const reassignIds = (node) => ({
      ...node,
      id: Math.random().toString(36).substr(2, 6),
      children: node.children ? node.children.map(reassignIds) : []
    });
    const newChild = reassignIds(jsonData);
    updateNodeRecursive(parentId, n => ({ ...n, children: [...n.children, newChild] }));
    setSelectedId(newChild.id);
  };

  const handleRootUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (evt) => {
      try { setTree(JSON.parse(evt.target.result)); }
      catch (err) { alert("Invalid JSON file"); }
    };
    reader.readAsText(file);
  };

  return (
    <div style={{ display: 'flex', width: '100vw', height: '100vh', background: '#0a0a0a', color: '#eee', fontFamily: 'monospace' }}>

      {/* LEFT SIDEBAR */}
      <div style={{ width: '400px', padding: '15px', borderRight: '1px solid #333', overflowY: 'auto', background: '#111' }}>
        <h2 style={{ color: '#00d4ff', fontSize: '1.2rem', margin: '0 0 15px 0' }}>PKG DESIGNER</h2>

        <div style={{ background: '#222', padding: '12px', borderRadius: '4px', marginBottom: '15px' }}>
          <div style={{ marginBottom: '10px' }}>
            <label style={{ fontSize: '9px', color: '#888', display: 'block' }}>Import Config</label>
            <input type="file" accept=".json" onChange={handleRootUpload} style={{ fontSize: '10px' }} />
          </div>
          <button style={btnMain} onClick={() => {
            const blob = new Blob([JSON.stringify(tree, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a'); a.href = url; a.download = 'package.json'; a.click();
          }}>Export Entire JSON</button>
        </div>

        <TreeItem
          node={tree}
          selectedId={selectedId}
          onSelect={setSelectedId}
          onAdd={(pid) => updateNodeRecursive(pid, n => ({ ...n, children: [...n.children, { id: Math.random().toString(36).substr(2, 6), name: "New Die", z: 0, visible: true, opacity: 1.0, showBottom: true, face: { type: "BOX", dim: [0, 0, 20, 20] }, layers: [{ material: "Si", thk: 5, color: "#369" }], children: [] }] }))}
          onImportChild={handleImportChild}
          onAddLayer={(id) => updateNodeRecursive(id, n => ({ ...n, layers: [...n.layers, { material: "New", thk: 2, color: "#e67e22" }] }))}
          onDeleteLayer={(oid, idx) => updateNodeRecursive(oid, n => ({ ...n, layers: n.layers.filter((_, i) => i !== idx) }))}
          onUpdateLayer={(oid, idx, f, v) => updateNodeRecursive(oid, n => {
            const nl = [...n.layers]; nl[idx] = { ...nl[idx], [f]: f === 'thk' ? parseFloat(v) || 0 : v };
            return { ...n, layers: nl };
          })}
          onUpdateNode={(id, patch) => updateNodeRecursive(id, n => ({ ...n, ...patch }))}
          onUpdateFace={(id, idx, val) => updateNodeRecursive(id, n => {
            const nd = [...n.face.dim]; nd[idx] = parseFloat(val) || 0;
            return { ...n, face: { ...n.face, dim: nd } };
          })}
          onDelete={(id) => id !== 'root' && setTree(n => {
            const remove = (node) => ({ ...node, children: node.children.filter(c => c.id !== id).map(remove) });
            return remove(n);
          })}
        />
      </div>

      {/* CENTER */}
      <div style={{ flex: 1 }}>
        <Canvas camera={{ position: [150, 150, 150] }} onPointerMissed={() => setSelectedId(null)}>
          <ambientLight intensity={0.6} />
          <pointLight position={[100, 100, 100]} intensity={1} />
          <Grid infiniteGrid fadeDistance={500} cellColor="#333" />
          <PackageObject data={tree} selectedId={selectedId} onSelect={setSelectedId} />
          <OrbitControls makeDefault />
        </Canvas>
      </div>

      {/* RIGHT SIDEBAR */}
      <div style={{ width: '250px', padding: '15px', borderLeft: '1px solid #333', background: '#111' }}>
        <h3 style={{ fontSize: '10px', color: '#2ecc71', marginTop: 0, letterSpacing: '1px', textTransform: 'uppercase' }}>Process</h3>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {/* GRIND BUTTON */}
          <div style={{ background: '#1a1a1a', padding: '12px', borderRadius: '4px', border: '1px solid #2ecc7133' }}>
            <button
              style={{ ...btnMain, background: '#2ecc71', color: '#000' }}
              onClick={handleGrind}
            >
              ⚡ EXECUTE GRIND ⚡
            </button>
            <p style={{ fontSize: '9px', color: '#666', marginTop: '10px', lineHeight: '1.4' }}>
              Grinding removes layers and components from the global top surface downwards.
            </p>
          </div>

          {/* FLIP BUTTON */}
          <div style={{ background: '#1a1a1a', padding: '12px', borderRadius: '4px', border: '1px solid #2ecc7133' }}>
            <button
              style={{ ...btnMain, background: '#2ecc71', color: '#000' }}
              onClick={handleFlip}
            >
              🔄 FLIP WAFER / CHIP 🔄
            </button>
            <p style={{ fontSize: '9px', color: '#666', marginTop: '10px', lineHeight: '1.4' }}>
              Inverts the layer stack-up and child positions.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

// --- UI ITEM COMPONENT ---

const TreeItem = (props) => {
  const { node, selectedId, onSelect, onAdd, onImportChild, onAddLayer, onDeleteLayer, onUpdateLayer, onUpdateNode, onUpdateFace, onDelete } = props;
  const [isCollapsed, setIsCollapsed] = useState(false);
  const isSelected = selectedId === node.id;
  const panelRef = useRef(null);
  const fileInputRef = useRef(null);

  const x1 = node.face.dim[0];
  const y1 = node.face.dim[1];
  const x2 = node.face.dim[2];
  const y2 = node.face.dim[3];
  const width = x2 - x1;
  const length = y2 - y1;

  useEffect(() => {
    if (isSelected) {
      setIsCollapsed(false);
      panelRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }, [isSelected]);

  return (
    <div ref={panelRef} style={{ marginLeft: '12px', borderLeft: isSelected ? '2px solid #ff00ff' : '1px solid #444', paddingLeft: '8px', marginBottom: '8px' }}>
      <div onClick={() => onSelect(node.id)} style={{ display: 'flex', alignItems: 'center', background: isSelected ? '#301a30' : 'transparent', padding: '4px', cursor: 'pointer', borderRadius: '2px' }}>
        <span onClick={(e) => { e.stopPropagation(); setIsCollapsed(!isCollapsed); }} style={{ cursor: 'pointer', color: '#888', width: '15px', fontSize: '10px' }}>
          {isCollapsed ? '▶' : '▼'}
        </span>
        <input
          style={{ background: 'transparent', color: isSelected ? '#ff00ff' : (node.visible ? '#00d4ff' : '#555'), border: 'none', fontSize: '11px', fontWeight: 'bold', width: '100%', outline: 'none' }}
          value={node.name} onChange={(e) => onUpdateNode(node.id, { name: e.target.value })} onClick={(e) => e.stopPropagation()}
        />
        <div style={{ display: 'flex', gap: '2px' }}>
          <button onClick={(e) => { e.stopPropagation(); onUpdateNode(node.id, { visible: !node.visible }); }}
            style={{ ...btnAction, background: node.visible ? '#2ecc71' : '#333' }}>V</button>
          <button onClick={(e) => { e.stopPropagation(); onAdd(node.id); }} style={btnAction}>+C</button>
          <button onClick={(e) => { e.stopPropagation(); fileInputRef.current.click(); }} style={{ ...btnAction, background: '#f39c12' }}>📂</button>
          <input type="file" ref={fileInputRef} onChange={(e) => {
            const file = e.target.files[0]; if (!file) return;
            const reader = new FileReader();
            reader.onload = (evt) => { onImportChild(node.id, JSON.parse(evt.target.result)); };
            reader.readAsText(file); e.target.value = null;
          }} style={{ display: 'none' }} accept=".json" />
          <button onClick={(e) => { e.stopPropagation(); onDelete(node.id); }} style={btnAction}>D</button>
        </div>
      </div>

      {!isCollapsed && (
        <div style={{ marginTop: '5px' }}>
          <div style={{ background: '#1a1a1a', padding: '6px', borderRadius: '4px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <span style={{ fontSize: '9px', color: '#666' }}>Z Offset</span>
              <input type="number" style={{ ...inputStyle, width: '45px' }} value={node.z} onChange={e => onUpdateNode(node.id, { z: parseFloat(e.target.value) || 0 })} />
              <button onClick={(e) => { e.stopPropagation(); onUpdateNode(node.id, { showBottom: !node.showBottom }); }}
                style={{ ...btnAction, background: node.showBottom ? '#00d4ff' : '#333', color: node.showBottom ? '#000' : '#eee', marginLeft: 'auto' }}>Footprint</button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <span style={{ fontSize: '8px', color: '#888', width: '30px' }}>POS:</span>
                <div style={coordBox}><label style={labelStyle}>X</label><input style={coordInput} type="number" value={x1} onChange={e => { const val = parseFloat(e.target.value) || 0; onUpdateNode(node.id, { face: { ...node.face, dim: [val, y1, val + width, y2] } }); }} /></div>
                <div style={coordBox}><label style={labelStyle}>Y</label><input style={coordInput} type="number" value={y1} onChange={e => { const val = parseFloat(e.target.value) || 0; onUpdateNode(node.id, { face: { ...node.face, dim: [x1, val, x2, val + length] } }); }} /></div>
              </div>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <span style={{ fontSize: '8px', color: '#888', width: '30px' }}>SIZE:</span>
                <div style={coordBox}><label style={labelStyle}>W</label><input style={coordInput} type="number" value={width} onChange={e => { const val = parseFloat(e.target.value) || 0; onUpdateFace(node.id, 2, x1 + val); }} /></div>
                <div style={coordBox}><label style={labelStyle}>L</label><input style={coordInput} type="number" value={length} onChange={e => { const val = parseFloat(e.target.value) || 0; onUpdateFace(node.id, 3, y1 + val); }} /></div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
                <span style={{ fontSize: '8px', color: '#888', width: '30px' }}>OPAC:</span>
                <input type="range" min="0.0" max="1.0" step="0.01" style={{ flex: 1, height: '4px' }} value={node.opacity ?? 1.0} onChange={e => onUpdateNode(node.id, { opacity: parseFloat(e.target.value) })} />
                <span style={{ fontSize: '9px', color: '#00d4ff', width: '25px' }}>{Math.round((node.opacity ?? 1) * 100)}%</span>
              </div>
            </div>
          </div>

          <div style={{ marginTop: '5px', background: '#222', padding: '6px', borderRadius: '4px' }}>
            {node.layers.map((l, i) => (
              <div key={i} style={{ display: 'flex', gap: '3px', marginBottom: '2px' }}>
                <input style={{ ...inputStyle, flex: 1 }} value={l.material} onChange={e => onUpdateLayer(node.id, i, 'material', e.target.value)} />
                <input type="number" style={{ ...inputStyle, width: '35px' }} value={l.thk} onChange={e => onUpdateLayer(node.id, i, 'thk', e.target.value)} />
                <button onClick={() => onDeleteLayer(node.id, i)} style={{ ...btnAction, background: '#500' }}>×</button>
              </div>
            ))}
            <button onClick={() => onAddLayer(node.id)} style={{ fontSize: '8px', width: '100%', marginTop: '4px' }}>+ Add Layer</button>
          </div>
          {node.children.map(c => <TreeItem key={c.id} {...props} node={c} />)}
        </div>
      )}
    </div>
  );
};

// --- STYLES ---
const btnMain = { width: '100%', padding: '8px', cursor: 'pointer', background: '#00d4ff', color: '#000', fontWeight: 'bold', border: 'none', borderRadius: '4px', fontSize: '11px' };
const btnAction = { fontSize: '8px', cursor: 'pointer', background: '#333', color: '#eee', border: '1px solid #444', padding: '1px 4px', borderRadius: '2px' };
const inputStyle = { background: '#000', color: '#00d4ff', border: '1px solid #333', fontSize: '10px', padding: '2px', borderRadius: '2px', outline: 'none' };
const coordBox = { display: 'flex', alignItems: 'center', background: '#000', border: '1px solid #333', borderRadius: '2px', padding: '1px 3px' };
const labelStyle = { fontSize: '7px', color: '#555', marginRight: '3px' };
const coordInput = { background: 'transparent', color: '#00d4ff', border: 'none', fontSize: '10px', width: '35px', outline: 'none' };