"use client";

import React, { useState, useEffect, useRef } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Grid, Edges } from '@react-three/drei';

/** * TYPES & INTERFACES */
interface Layer {
  material: string;
  thk: number;
  color?: string;
}

interface Face {
  type: string;
  dim: number[];
}

interface PackageNode {
  id: string;
  name: string;
  z: number;
  visible: boolean;
  showBottom: boolean;
  opacity: number;
  face: Face;
  layers: Layer[];
  children: PackageNode[];
}

/** * 1. COMPONENT REGISTRY */
const COMPONENT_LIBRARY: Record<string, { model: string, path: string }[]> = {
  HBM: [
    { model: "SKH-HBM3", path: "/resource/hbm/skh-hbm3.json" },
    { model: "SKH-HBM4", path: "/resource/hbm/skh-hbm4.json" }
  ],
  SoIC: [
    { model: "TSMC-SoIC-v1", path: "/resource/soic/soic-v1.json" }
  ]
};

/** * 2. INITIAL DATA */
const initialData: PackageNode = {
  id: "root",
  name: "Main Substrate",
  z: 0,
  visible: true,
  showBottom: true,
  opacity: 1.0,
  face: { type: "BOX", dim: [-50, -50, 50, 50] },
  layers: [{ material: "Core", thk: 10, color: "#444444" }],
  children: []
};

// --- UTILITY FUNCTIONS FOR JSON FORMATTING ---
const formatForExport = (node: PackageNode): any => {
  const { children, ...rest } = node;
  return {
    ...rest,
    child_obj: children ? children.map(formatForExport) : []
  };
};

const formatForImport = (node: any): PackageNode => {
  const { child_obj, children, ...rest } = node;
  const childArray = child_obj || children || [];
  return {
    ...rest,
    children: childArray.map(formatForImport)
  };
};

// --- 3D RENDERER COMPONENTS ---

interface PackageObjectProps {
  data: PackageNode;
  parentBaseZ?: number;
  selectedId: string | null;
  onSelect: (id: string) => void;
}

const PackageObject: React.FC<PackageObjectProps> = ({ data, parentBaseZ = 0, selectedId, onSelect }) => {
  const { face, layers, children, z = 0, id, showBottom = true, visible = true, opacity = 1.0 } = data;
  const isSelected = selectedId === id;

  const isCyl = face.type === "CYLINDER";
  let width = 0, depth = 0, centerX = 0, centerZ = 0, radius = 0;

  if (isCyl) {
    centerX = face.dim[0]; centerZ = face.dim[1]; radius = face.dim[2];
    width = radius * 2; depth = radius * 2;
  } else {
    width = Math.abs(face.dim[2] - face.dim[0]);
    depth = Math.abs(face.dim[3] - face.dim[1]);
    centerX = (face.dim[0] + face.dim[2]) / 2;
    centerZ = (face.dim[1] + face.dim[3]) / 2;
  }

  const myBottomZ = parentBaseZ + z;

  return (
    <group position={[centerX, myBottomZ, centerZ]}>
      {visible && (
        <group>
          {showBottom && (
            <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.02, 0]}>
              {isCyl ? <circleGeometry args={[radius, 32]} /> : <planeGeometry args={[width, depth]} />}
              <meshBasicMaterial color={isSelected ? "cyan" : "#555"} transparent opacity={isSelected ? 0.6 : 0.3 * opacity} side={2} />
            </mesh>
          )}

          {layers.reduce<{ meshes: React.ReactNode[]; cumulativeThk: number }>((acc, layer, idx) => {
            const { meshes, cumulativeThk } = acc;
            const yPos = cumulativeThk + layer.thk / 2;
            meshes.push(
              <mesh key={`${id}-layer-${idx}`} position={[0, yPos, 0]} onClick={(e) => { e.stopPropagation(); onSelect(id); }}>
                {isCyl ? <cylinderGeometry args={[radius, radius, layer.thk, 32]} /> : <boxGeometry args={[width, layer.thk, depth]} />}
                <meshStandardMaterial color={isSelected ? "#ff00ff" : (layer.color || "#666")} emissive={isSelected ? "#ff00ff" : "#000"} emissiveIntensity={isSelected ? 0.2 : 0} transparent={true} opacity={Number(opacity)} depthWrite={Number(opacity) === 1} />
                <Edges color={isSelected ? "cyan" : "white"} />
              </mesh>
            );
            return { meshes, cumulativeThk: cumulativeThk + layer.thk };
          }, { meshes: [], cumulativeThk: 0 }).meshes}
        </group>
      )}
      <group position={isCyl ? [0, 0, 0] : [-width / 2, 0, -depth / 2]}>
        {children.map((child) => <PackageObject key={child.id} data={child} parentBaseZ={0} selectedId={selectedId} onSelect={onSelect} />)}
      </group>
    </group>
  );
};

// --- MAIN APPLICATION ---

export default function Page() {
  const [tree, setTree] = useState<PackageNode>(initialData);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  
  const [alignMode, setAlignMode] = useState<string | null>(null);
  
  // Export Path State
  const [exportPath, setExportPath] = useState<string>("");

  // Refs
  const globalFileInputRef = useRef<HTMLInputElement>(null);

  // Form States
  const [showMcForm, setShowMcForm] = useState<boolean>(false);
  const [mcParams, setMcParams] = useState({ material: "Epoxy_MC", thickness: 15 });

  const [showGrindForm, setShowGrindForm] = useState<boolean>(false);
  const [grindParams, setGrindParams] = useState({ depth: 5 });

  const [showRdlForm, setShowRdlForm] = useState<boolean>(false);
  const [rdlParams, setRdlParams] = useState({ count: 3, metalMat: "Cu", metalThk: 2, pmMat: "PI", pmThk: 3 });

  // PnP Form States
  const [showPnpForm, setShowPnpForm] = useState<boolean>(false);
  const [pnpSourceType, setPnpSourceType] = useState<'library' | 'custom'>('library');
  const [pnpLibCategory, setPnpLibCategory] = useState<string>("");
  const [pnpLibModel, setPnpLibModel] = useState<string>("");
  const [pnpCustomData, setPnpCustomData] = useState<any>(null);
  const [pnpCoordinates, setPnpCoordinates] = useState<string>("");

  // Helpers
  const getNodeLayerHeight = (node: PackageNode) => node.layers.reduce((sum, l) => sum + (parseFloat(l.thk as unknown as string) || 0), 0);

  const calculateMaxZ = (node: PackageNode, baseZ: number): number => {
    const myBottom = baseZ + node.z;
    let maxZ = myBottom + getNodeLayerHeight(node);
    node.children.forEach(c => { maxZ = Math.max(maxZ, calculateMaxZ(c, myBottom)); }); 
    return maxZ;
  };

  const findNodeById = (node: PackageNode, id: string): PackageNode | null => {
    if (node.id === id) return node;
    for (let child of node.children) {
      const found = findNodeById(child, id);
      if (found) return found;
    }
    return null;
  };

  const updateNodeRecursive = (id: string, callback: (n: PackageNode) => PackageNode) => {
    const update = (node: PackageNode): PackageNode => node.id === id ? callback(node) : { ...node, children: node.children.map(update) };
    setTree(update(tree));
  };

  const handleSelectNode = (id: string) => {
    if (alignMode) {
      if (id !== alignMode) {
        const targetNode = findNodeById(tree, id);
        if (targetNode) {
          const targetTopZ = targetNode.z + getNodeLayerHeight(targetNode);
          updateNodeRecursive(alignMode, n => ({ ...n, z: targetTopZ }));
        }
      }
      setAlignMode(null);
    } else {
      setSelectedId(id);
    }
  };

  const handleImportChild = (parentId: string, jsonData: any) => {
    const reassignIds = (node: any): PackageNode => ({ 
        ...node, 
        id: Math.random().toString(36).substr(2, 6), 
        children: node.children ? node.children.map(reassignIds) : [] 
    });
    const newChild = reassignIds(jsonData);
    updateNodeRecursive(parentId, n => ({ ...n, children: [...n.children, newChild] }));
    setSelectedId(newChild.id);
  };

  // --- DIRECT STRING EXPORT (WITH "child_obj" MAPPING) ---
  const handleExport = () => {
    const exportData = formatForExport(tree);
    const jsonStr = JSON.stringify(exportData, null, 2);
    
    const defaultFileName = `${tree.name.replace(/\s+/g, '_').toLowerCase()}.json`;
    const finalFileName = exportPath.trim() || defaultFileName;

    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); 
    a.href = url; 
    a.download = finalFileName; 
    
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // --- PROCESS: PICK AND PRESS (PNP) ---
  const submitPnP = async () => {
    if (!selectedId) return alert("Select a base object for PnP!");
    const baseNode = findNodeById(tree, selectedId);
    if (!baseNode) return;

    // 1. Resolve Die Model Data Once
    let nodeData: any = null;
    if (pnpSourceType === 'library') {
      if (!pnpLibCategory || !pnpLibModel) return alert("Please select a library model.");
      const modelObj = COMPONENT_LIBRARY[pnpLibCategory].find(m => m.model === pnpLibModel);
      if (modelObj) {
        try {
          const res = await fetch(modelObj.path);
          nodeData = await res.json();
        } catch (e) {
          return alert("Failed to load library component JSON.");
        }
      }
    } else {
      if (!pnpCustomData) return alert("Please upload a custom JSON.");
      nodeData = pnpCustomData;
    }

    if (!nodeData) return;

    // 2. Parse Bulk Coordinates
    const lines = pnpCoordinates.trim().split('\n');
    const parsedCoords: {x: number, y: number}[] = [];
    
    for (const line of lines) {
      if (!line.trim()) continue;
      // Split by spaces, tabs, or commas
      const parts = line.trim().split(/[\s,\t]+/);
      if (parts.length >= 2) {
        const x = parseFloat(parts[0]);
        const y = parseFloat(parts[1]);
        if (!isNaN(x) && !isNaN(y)) {
          parsedCoords.push({ x, y });
        }
      }
    }

    if (parsedCoords.length === 0) return alert("No valid coordinates found! Ensure format is 'X Y' per row.");

    const topZ = baseNode.z + getNodeLayerHeight(baseNode);
    const newNodes: PackageNode[] = [];

    // 3. Generate instances for each coordinate
    for (const coord of parsedCoords) {
      // FIX: Deep clone nodeData so each die gets completely independent memory references
      // otherwise, updating the face dim for one updates it for all of them!
      const clonedNodeData = JSON.parse(JSON.stringify(nodeData));
      
      const formattedNode = formatForImport(clonedNodeData);
      
      const reassignIds = (n: PackageNode): PackageNode => ({ 
          ...n, 
          id: "pnp-" + Math.random().toString(36).substr(2, 6), 
          children: n.children ? n.children.map(reassignIds) : [] 
      });
      
      const newNode = reassignIds(formattedNode);
      
      newNode.z = topZ;
      
      const isCyl = newNode.face.type === "CYLINDER";
      if (isCyl) {
        newNode.face.dim = [coord.x, coord.y, newNode.face.dim[2]];
      } else {
        const w = newNode.face.dim[2] - newNode.face.dim[0];
        const l = newNode.face.dim[3] - newNode.face.dim[1];
        newNode.face.dim = [coord.x, coord.y, coord.x + w, coord.y + l];
      }

      newNodes.push(newNode);
    }

    // Insert the new nodes at the "same level" (siblings of the selected base object)
    if (selectedId === 'root') {
      setTree(prev => ({ ...prev, children: [...prev.children, ...newNodes] }));
    } else {
      const addSiblings = (curr: PackageNode): PackageNode => {
        if (curr.children && curr.children.some(c => c.id === selectedId)) {
          return { ...curr, children: [...curr.children, ...newNodes] };
        }
        return curr.children ? { ...curr, children: curr.children.map(addSiblings) } : curr;
      };
      setTree(addSiblings(tree));
    }

    // Cleanup
    setShowPnpForm(false);
  };

  // --- PROCESS: FILL MC (FORM-BASED) ---
  const submitFillMC = () => {
    if (!selectedId || selectedId === 'root') return alert("Select an object to base the MC on!");
    const baseNode = findNodeById(tree, selectedId);
    if (!baseNode) return;
    
    const { material, thickness } = mcParams;
    if (thickness <= 0 || isNaN(thickness)) return alert("Thickness must be > 0");

    const mcZ = baseNode.z + getNodeLayerHeight(baseNode);
    const processTree = (curr: PackageNode): PackageNode => {
      if (curr.children && curr.children.some(c => c.id === selectedId)) {
        const toWrap = curr.children.filter(c => c.z >= baseNode.z && c.id !== selectedId);
        const stayOutside = curr.children.filter(c => c.z < baseNode.z || c.id === selectedId);
        const newMC: PackageNode = {
          id: "mc-" + Math.random().toString(36).substr(2, 4),
          name: `MC: ${material}`, z: mcZ, visible: true, opacity: 0.4, showBottom: false,
          face: JSON.parse(JSON.stringify(baseNode.face)),
          layers: [{ material, thk: thickness, color: "#2c3e50" }],
          children: toWrap.map(child => ({ ...child, z: child.z - mcZ }))
        };
        return { ...curr, children: [...stayOutside, newMC] };
      }
      return curr.children ? { ...curr, children: curr.children.map(processTree) } : curr;
    };
    
    setTree(processTree(tree));
    setShowMcForm(false);
  };

  // --- PROCESS: GRIND (FORM-BASED) ---
  const submitGrind = () => {
    const globalTopZ = calculateMaxZ(tree, 0);
    const depth = parseFloat(grindParams.depth as unknown as string);
    if (isNaN(depth) || depth <= 0) return alert("Grind depth must be > 0");
    
    const grindZ = globalTopZ - depth;

    const processGrind = (node: PackageNode, baseZ: number): PackageNode => {
      const myBottomZ = baseZ + node.z;
      let curr = myBottomZ;
      const newLayers: Layer[] = [];
      
      node.layers.forEach(l => {
        if (curr < grindZ) {
          newLayers.push(curr + l.thk > grindZ ? { ...l, thk: grindZ - curr } : l);
        }
        curr += l.thk;
      });

      const newChildren = node.children.map(c => processGrind(c, myBottomZ)).filter(c => c.layers.length > 0 || c.children.length > 0);
      return { ...node, layers: newLayers, children: newChildren };
    };
    
    setTree(processGrind(tree, 0));
    setShowGrindForm(false);
  };

  // --- PROCESS: FLIP ---
  const handleFlip = () => {
    const processFlip = (node: PackageNode): PackageNode => {
      const h = getNodeLayerHeight(node);
      return { ...node, layers: [...node.layers].reverse(), children: node.children.map(c => processFlip({ ...c, z: h - (c.z + getNodeLayerHeight(c)) })) };
    };
    setTree(processFlip(tree));
  };

  // --- RDL GENERATION ---
  const submitRDL = () => {
    const baseNode = findNodeById(tree, selectedId!);
    if (!baseNode) return;

    const { count, metalMat, metalThk, pmMat, pmThk } = rdlParams;
    if (count <= 0 || metalThk <= 0 || pmThk <= 0) return alert("Values must be greater than 0");

    const tierThk = pmThk + metalThk;
    const totalHeight = (count * tierThk) + pmThk;

    const rdlZ = baseNode.z + getNodeLayerHeight(baseNode);
    const isCyl = baseNode.face.type === "CYLINDER";
    
    const childDim = isCyl 
      ? [0, 0, baseNode.face.dim[2]] 
      : [0, 0, baseNode.face.dim[2] - baseNode.face.dim[0], baseNode.face.dim[3] - baseNode.face.dim[1]];

    const rdlChildren: PackageNode[] = Array.from({ length: count }).map((_, i) => ({
      id: "rdl-tier-" + Math.random().toString(36).substr(2, 4),
      name: `${metalMat}_${pmMat}_${i + 1}`,
      z: i * tierThk,
      visible: true,
      opacity: 1.0,
      showBottom: false,
      face: { type: baseNode.face.type, dim: childDim },
      layers: [
        { material: pmMat, thk: pmThk, color: "#8B4513" },
        { material: metalMat, thk: metalThk, color: "#B87333" } 
      ],
      children: []
    }));

    rdlChildren.push({
      id: "rdl-cap-" + Math.random().toString(36).substr(2, 4),
      name: `${pmMat}_Cap`,
      z: count * tierThk,
      visible: true,
      opacity: 1.0,
      showBottom: false,
      face: { type: baseNode.face.type, dim: childDim },
      layers: [
        { material: pmMat, thk: pmThk, color: "#8B4513" }
      ],
      children: []
    });

    const newRDL: PackageNode = {
      id: "rdl-" + Math.random().toString(36).substr(2, 4),
      name: `RDL Stack`,
      z: rdlZ,
      visible: true,
      opacity: 0.1, 
      showBottom: false,
      face: JSON.parse(JSON.stringify(baseNode.face)),
      layers: [{ material: "EMPTY", thk: totalHeight, color: "#ffffff" }],
      children: rdlChildren
    };

    if (selectedId === 'root') {
      setTree(prev => ({ ...prev, children: [...prev.children, newRDL] }));
    } else {
      const addSibling = (curr: PackageNode): PackageNode => {
        if (curr.children && curr.children.some(c => c.id === selectedId)) {
          return { ...curr, children: [...curr.children, newRDL] };
        }
        return curr.children ? { ...curr, children: curr.children.map(addSibling) } : curr;
      };
      setTree(addSibling(tree));
    }

    setShowRdlForm(false); 
  };

  return (
    <div style={{ display: 'flex', width: '100vw', height: '100vh', background: '#0a0a0a', color: '#eee', fontFamily: 'monospace' }}>
      
      {/* LEFT SIDEBAR */}
      <div style={{ width: '450px', minWidth: '450px', flexShrink: 0, padding: '15px', borderRight: '1px solid #333', overflowY: 'auto', background: '#111' }}>
        <h2 style={{ color: '#00d4ff', fontSize: '1.2rem', margin: '0 0 15px 0' }}>PKG DESIGNER</h2>
        
        {/* FILE IO PANEL */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '20px' }}>
          
          {/* IMPORT CARD */}
          <div style={ioBoxStyle}>
            <div>
              <span style={{ fontSize: '12px', color: '#00d4ff', fontWeight: 'bold', display: 'block' }}>📥 Import Workspace</span>
              <span style={{ fontSize: '9px', color: '#777' }}>Load a previously saved JSON design.</span>
            </div>
            <button style={{ ...btnMain, background: '#222', color: '#eee', border: '1px solid #444' }} onClick={() => globalFileInputRef.current?.click()}>
              Browse Files...
            </button>
            <input type="file" accept=".json" ref={globalFileInputRef} style={{ display: 'none' }} onChange={(e) => {
               const file = e.target.files?.[0]; if (!file) return;
               const reader = new FileReader();
               reader.onload = (evt) => { 
                 try { 
                   if (evt.target?.result) {
                       const parsed = JSON.parse(evt.target.result as string);
                       setTree(formatForImport(parsed)); 
                   }
                 } catch (err) { alert("Invalid JSON"); } 
               };
               reader.readAsText(file);
               e.target.value = '';
            }} />
          </div>

          {/* EXPORT CARD */}
          <div style={ioBoxStyle}>
            <div>
              <span style={{ fontSize: '12px', color: '#00d4ff', fontWeight: 'bold', display: 'block' }}>📤 Export Workspace</span>
              <span style={{ fontSize: '9px', color: '#777' }}>Save current design to your downloads folder.</span>
            </div>
            <input 
              style={{ ...inputStyle, width: '100%', boxSizing: 'border-box' }} 
              placeholder="e.g. models/design_v2.json (leave blank for default)" 
              value={exportPath}
              onChange={(e) => setExportPath(e.target.value)}
            />
            <button style={btnMain} onClick={handleExport}>
              Download JSON
            </button>
          </div>
          
        </div>

        <TreeItem
          node={tree} selectedId={selectedId} onSelect={handleSelectNode}
          alignMode={alignMode} setAlignMode={setAlignMode}
          onImportChild={handleImportChild}
          onAddLayer={(id) => updateNodeRecursive(id, n => ({ ...n, layers: [...n.layers, { material: "EMPTY", thk: 2, color: "#e67e22" }] }))}
          onDeleteLayer={(oid, idx) => updateNodeRecursive(oid, n => ({ ...n, layers: n.layers.filter((_, i) => i !== idx) }))}
          onUpdateLayer={(oid, idx, f, v) => updateNodeRecursive(oid, n => {
            const nl = [...n.layers]; nl[idx] = { ...nl[idx], [f]: f === 'thk' ? parseFloat(v) || 0 : v };
            return { ...n, layers: nl };
          })}
          onUpdateNode={(id, patch) => updateNodeRecursive(id, n => ({ ...n, ...patch }))}
          onUpdateFace={(id, idx, val) => updateNodeRecursive(id, n => {
            const nd = [...n.face.dim]; nd[idx] = parseFloat(val as string) || 0;
            return { ...n, face: { ...n.face, dim: nd } };
          })}
          onDelete={(id) => id !== 'root' && setTree(n => {
            const remove = (node: PackageNode): PackageNode => ({ ...node, children: node.children.filter(c => c.id !== id).map(remove) });
            return remove(n);
          })}
        />
      </div>

      {/* CENTER CANAVAS */}
      <div style={{ flex: 1, minWidth: 0, position: 'relative' }}>
        <Canvas camera={{ position: [150, 150, 150] }} onPointerMissed={() => {
            if (alignMode) setAlignMode(null);
            else setSelectedId(null);
        }}>
          <ambientLight intensity={0.6} /><pointLight position={[100, 100, 100]} intensity={1} />
          <Grid infiniteGrid fadeDistance={500} cellColor="#333" />
          <PackageObject data={tree} selectedId={selectedId} onSelect={handleSelectNode} />
          <OrbitControls makeDefault />
        </Canvas>
      </div>

      {/* RIGHT SIDEBAR */}
      <div style={{ width: '250px', minWidth: '250px', flexShrink: 0, padding: '15px', borderLeft: '1px solid #333', background: '#111', overflowY: 'auto' }}>
        <h3 style={{ fontSize: '10px', color: '#2ecc71', marginTop: 0 }}>Process Tools</h3>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          
          <button 
            style={{ ...btnMain, background: showMcForm ? '#e74c3c' : '#2ecc71', color: showMcForm ? '#fff' : '#000' }} 
            onClick={() => setShowMcForm(!showMcForm)}>
            {showMcForm ? '❌ CANCEL MC' : '🏺 FILL MC 🏺'}
          </button>
          
          {showMcForm && (
            <div style={{ background: '#1a2a33', padding: '10px', borderRadius: '4px', border: '1px solid #2ecc71', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={coordBox}>
                <label style={{...labelStyle, width: '60px', color: '#fff'}}>Material</label>
                <input style={{...coordInput, width: '100%'}} value={mcParams.material} onChange={e => setMcParams({...mcParams, material: e.target.value})} />
              </div>
              <div style={coordBox}>
                <label style={{...labelStyle, width: '60px', color: '#fff'}}>Thickness</label>
                <input style={{...coordInput, width: '100%'}} type="number" value={mcParams.thickness} onChange={e => setMcParams({...mcParams, thickness: parseFloat(e.target.value) || 0})} />
              </div>
              <button style={{...btnMain, background: '#2ecc71', marginTop: '5px'}} onClick={submitFillMC}>EXECUTE FILL</button>
            </div>
          )}

          <button 
            style={{ ...btnMain, background: showGrindForm ? '#e74c3c' : '#2ecc71', color: showGrindForm ? '#fff' : '#000' }} 
            onClick={() => setShowGrindForm(!showGrindForm)}>
            {showGrindForm ? '❌ CANCEL GRIND' : '⚡ EXECUTE GRIND ⚡'}
          </button>

          {showGrindForm && (
            <div style={{ background: '#1a2a33', padding: '10px', borderRadius: '4px', border: '1px solid #2ecc71', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ fontSize: '9px', color: '#888', marginBottom: '4px', textAlign: 'center' }}>
                Global Top Z: <b>{calculateMaxZ(tree, 0).toFixed(2)}</b>
              </div>
              <div style={coordBox}>
                <label style={{...labelStyle, width: '60px', color: '#fff'}}>Grind Depth</label>
                <input style={{...coordInput, width: '100%'}} type="number" value={grindParams.depth} onChange={e => setGrindParams({...grindParams, depth: parseFloat(e.target.value) || 0})} />
              </div>
              <button style={{...btnMain, background: '#2ecc71', marginTop: '5px'}} onClick={submitGrind}>EXECUTE GRIND</button>
            </div>
          )}
          
          <button 
            style={{ ...btnMain, background: showPnpForm ? '#e74c3c' : '#9b59b6', color: showPnpForm ? '#fff' : '#000' }} 
            onClick={() => {
              if (!selectedId) return alert("Select a base object for PnP!");
              setShowPnpForm(!showPnpForm);
            }}>
            {showPnpForm ? '❌ CANCEL PNP' : '🤖 BULK PNP 🤖'}
          </button>

          {showPnpForm && (
            <div style={{ background: '#1a2a33', padding: '10px', borderRadius: '4px', border: '1px solid #9b59b6', display: 'flex', flexDirection: 'column', gap: '10px' }}>
              
              <div style={{ display: 'flex', gap: '4px' }}>
                <button style={{...btnAction, flex: 1, background: pnpSourceType === 'library' ? '#3498db' : '#333'}} onClick={() => setPnpSourceType('library')}>Library</button>
                <button style={{...btnAction, flex: 1, background: pnpSourceType === 'custom' ? '#3498db' : '#333'}} onClick={() => setPnpSourceType('custom')}>Custom File</button>
              </div>

              {pnpSourceType === 'library' ? (
                <>
                  <select style={{...inputStyle, width: '100%'}} value={pnpLibCategory} onChange={e => { setPnpLibCategory(e.target.value); setPnpLibModel(''); }}>
                    <option value="">Select Category...</option>
                    {Object.keys(COMPONENT_LIBRARY).map(k => <option key={k} value={k}>{k}</option>)}
                  </select>
                  {pnpLibCategory && (
                    <select style={{...inputStyle, width: '100%'}} value={pnpLibModel} onChange={e => setPnpLibModel(e.target.value)}>
                      <option value="">Select Model...</option>
                      {COMPONENT_LIBRARY[pnpLibCategory].map(m => <option key={m.model} value={m.model}>{m.model}</option>)}
                    </select>
                  )}
                </>
              ) : (
                <div style={{ background: '#222', padding: '6px', borderRadius: '4px' }}>
                  <input type="file" accept=".json" style={{ fontSize: '9px', color: '#fff', width: '100%', overflow: 'hidden' }} onChange={(e) => {
                    const file = e.target.files?.[0]; if (!file) return;
                    const reader = new FileReader();
                    reader.onload = (evt) => {
                        if (evt.target?.result) {
                            try {
                                const parsed = JSON.parse(evt.target.result as string);
                                setPnpCustomData(parsed);
                            } catch(err) { alert("Invalid JSON file"); }
                        }
                    };
                    reader.readAsText(file);
                  }} />
                  {pnpCustomData && <div style={{ fontSize: '8px', color: '#2ecc71', marginTop: '4px' }}>✓ Loaded Custom Die</div>}
                </div>
              )}

              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                <label style={{ fontSize: '9px', color: '#00d4ff', fontWeight: 'bold' }}>Paste Coordinates (X Y):</label>
                <span style={{ fontSize: '8px', color: '#777' }}>One die per line, separated by space or tab</span>
                <textarea 
                  style={{ ...inputStyle, width: '100%', minHeight: '80px', boxSizing: 'border-box', whiteSpace: 'pre', fontFamily: 'monospace' }}
                  placeholder="0  0&#10;10 0&#10;0  10&#10;10 10"
                  value={pnpCoordinates}
                  onChange={(e) => setPnpCoordinates(e.target.value)}
                />
              </div>

              <button style={{...btnMain, background: '#9b59b6', color: '#fff'}} onClick={submitPnP}>PLACE DIES</button>
            </div>
          )}

          <button style={{ ...btnMain, background: '#2ecc71', color: '#000' }} onClick={handleFlip}>🔄 FLIP STACK 🔄</button>
        </div>

        <h3 style={{ fontSize: '10px', color: '#3498db', marginTop: '20px' }}>Layer Panel</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <button 
            style={{ ...btnMain, background: showRdlForm ? '#e74c3c' : '#3498db', color: '#fff' }} 
            onClick={() => {
              if (!selectedId) return alert("Select a base object for the RDL!");
              setShowRdlForm(!showRdlForm);
            }}>
            {showRdlForm ? '❌ CANCEL RDL' : '🥞 ADD RDL 🥞'}
          </button>

          {showRdlForm && (
            <div style={{ background: '#1a2a33', padding: '10px', borderRadius: '4px', border: '1px solid #3498db', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              
              <div style={coordBox}>
                <label style={{...labelStyle, width: '60px', color: '#fff'}}>Layers</label>
                <input style={{...coordInput, width: '100%'}} type="number" value={rdlParams.count} onChange={e => setRdlParams({...rdlParams, count: parseInt(e.target.value) || 1})} />
              </div>
              
              <div style={coordBox}>
                <label style={{...labelStyle, width: '60px', color: '#fff'}}>Metal Mat</label>
                <input style={{...coordInput, width: '100%'}} value={rdlParams.metalMat} onChange={e => setRdlParams({...rdlParams, metalMat: e.target.value})} />
              </div>
              <div style={coordBox}>
                <label style={{...labelStyle, width: '60px', color: '#fff'}}>Metal Thk</label>
                <input style={{...coordInput, width: '100%'}} type="number" value={rdlParams.metalThk} onChange={e => setRdlParams({...rdlParams, metalThk: parseFloat(e.target.value) || 0})} />
              </div>

              <div style={coordBox}>
                <label style={{...labelStyle, width: '60px', color: '#fff'}}>PM Mat</label>
                <input style={{...coordInput, width: '100%'}} value={rdlParams.pmMat} onChange={e => setRdlParams({...rdlParams, pmMat: e.target.value})} />
              </div>
              <div style={coordBox}>
                <label style={{...labelStyle, width: '60px', color: '#fff'}}>PM Thk</label>
                <input style={{...coordInput, width: '100%'}} type="number" value={rdlParams.pmThk} onChange={e => setRdlParams({...rdlParams, pmThk: parseFloat(e.target.value) || 0})} />
              </div>
              
              <button style={{...btnMain, background: '#3498db', color: '#fff', marginTop: '5px'}} onClick={submitRDL}>GENERATE RDL</button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// --- UI COMPONENTS ---

interface TreeItemProps {
  node: PackageNode;
  selectedId: string | null;
  onSelect: (id: string) => void;
  alignMode: string | null;
  setAlignMode: (id: string | null) => void;
  onImportChild: (parentId: string, data: any) => void;
  onAddLayer: (id: string) => void;
  onDeleteLayer: (id: string, idx: number) => void;
  onUpdateLayer: (id: string, idx: number, field: string, value: any) => void;
  onUpdateNode: (id: string, patch: Partial<PackageNode>) => void;
  onUpdateFace: (id: string, idx: number, val: string | number) => void;
  onDelete: (id: string) => void;
}

const TreeItem: React.FC<TreeItemProps> = (props) => {
  const { node, selectedId, onSelect, alignMode, setAlignMode, onImportChild, onAddLayer, onDeleteLayer, onUpdateLayer, onUpdateNode, onUpdateFace, onDelete } = props;
  const [isCollapsed, setIsCollapsed] = useState<boolean>(false);
  const [showAddMenu, setShowAddMenu] = useState<boolean>(false);
  const [libType, setLibType] = useState<string>("");
  
  const isSelected = selectedId === node.id;
  const fileInputRef = useRef<HTMLInputElement>(null);
  const addMenuRef = useRef<HTMLDivElement>(null);

  const isCyl = node.face.type === "CYLINDER";
  const dim = node.face.dim;
  const width = !isCyl ? dim[2] - dim[0] : 0;
  const length = !isCyl ? dim[3] - dim[1] : 0;

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (addMenuRef.current && !addMenuRef.current.contains(event.target as Node)) {
        setShowAddMenu(false);
      }
    };
    if (showAddMenu) {
      document.addEventListener('click', handleClickOutside);
    }
    return () => document.removeEventListener('click', handleClickOutside);
  }, [showAddMenu]);

  return (
    <div style={{ marginLeft: '12px', borderLeft: isSelected ? '2px solid #ff00ff' : '1px solid #444', paddingLeft: '8px', marginBottom: '8px' }}>
      
      <div 
        onClick={() => onSelect(node.id)} 
        style={{ display: 'flex', alignItems: 'center', background: isSelected ? '#301a30' : 'transparent', padding: '4px', cursor: 'pointer', borderRadius: '2px' }}
      >
        <span onClick={(e) => { e.stopPropagation(); setIsCollapsed(!isCollapsed); }} style={{ cursor: 'pointer', color: '#888', width: '15px', fontSize: '10px' }}>{isCollapsed ? '▶' : '▼'}</span>
        <input style={{ background: 'transparent', color: isSelected ? '#ff00ff' : (node.visible ? '#00d4ff' : '#555'), border: 'none', fontSize: '11px', fontWeight: 'bold', width: '100%', outline: 'none' }} value={node.name} onChange={(e) => onUpdateNode(node.id, { name: e.target.value })} onClick={(e) => e.stopPropagation()} />
        
        <select value={node.face.type} onClick={(e) => e.stopPropagation()} onChange={(e) => onUpdateNode(node.id, { face: { ...node.face, type: e.target.value, dim: e.target.value === "CYLINDER" ? [0,0,25] : [0,0,50,50] } })} style={{ fontSize: '9px', background: '#222', color: '#fff', border: 'none', marginRight: '5px' }}>
          <option value="BOX">BOX</option><option value="CYLINDER">CYL</option>
        </select>

        <div style={{ display: 'flex', gap: '2px' }}>
          <button onClick={(e) => { e.stopPropagation(); onUpdateNode(node.id, { visible: !node.visible }); }} style={{ ...btnAction, background: node.visible ? '#2ecc71' : '#333' }}>V</button>
          <button onClick={(e) => { e.stopPropagation(); setShowAddMenu(!showAddMenu); onSelect(node.id); setIsCollapsed(false); }} style={{ ...btnAction, background: showAddMenu ? '#e74c3c' : '#00d4ff', color:'#000', fontWeight:'bold' }}>+</button>
          {node.id !== 'root' && <button onClick={(e) => { e.stopPropagation(); onDelete(node.id); }} style={btnAction}>D</button>}
        </div>
      </div>

      {!isCollapsed && (
        <div style={{ marginTop: '5px' }}>
          
          <div style={{ background: '#1a1a1a', padding: '6px', borderRadius: '4px', border: '1px solid #333' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <span style={{ fontSize: '9px', color: '#666' }}>Z Offset</span>
              <input type="number" style={{ ...inputStyle, width: '45px' }} value={node.z} onChange={e => onUpdateNode(node.id, { z: parseFloat(e.target.value) || 0 })} />
              
              <button 
                onClick={(e) => { e.stopPropagation(); setAlignMode(alignMode === node.id ? null : node.id); }} 
                style={{ ...btnAction, background: alignMode === node.id ? '#e74c3c' : '#f39c12', fontWeight: 'bold' }}
                title="Click another object to snap to its top Z"
              >
                {alignMode === node.id ? 'Cancel 🎯' : '🎯 Pick'}
              </button>

              <button onClick={(e) => { e.stopPropagation(); onUpdateNode(node.id, { showBottom: !node.showBottom }); }} style={{ ...btnAction, background: node.showBottom ? '#00d4ff' : '#333', color: node.showBottom ? '#000' : '#eee', marginLeft: 'auto' }}>Footprint</button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              {isCyl ? (
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  <div style={coordBox}><label style={labelStyle}>CX</label><input style={coordInput} type="number" value={dim[0]} onChange={e => onUpdateFace(node.id, 0, e.target.value)} /></div>
                  <div style={coordBox}><label style={labelStyle}>CY</label><input style={coordInput} type="number" value={dim[1]} onChange={e => onUpdateFace(node.id, 1, e.target.value)} /></div>
                  <div style={coordBox}><label style={labelStyle}>R</label><input style={coordInput} type="number" value={dim[2]} onChange={e => onUpdateFace(node.id, 2, e.target.value)} /></div>
                </div>
              ) : (
                <>
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  <span style={{ fontSize: '8px', color: '#888', width: '30px' }}>POS:</span>
                  <div style={coordBox}><label style={labelStyle}>X</label><input style={coordInput} type="number" value={dim[0]} onChange={e => { const v = parseFloat(e.target.value) || 0; onUpdateNode(node.id, { face: { ...node.face, dim: [v, dim[1], v + width, dim[3]] } }); }} /></div>
                  <div style={coordBox}><label style={labelStyle}>Y</label><input style={coordInput} type="number" value={dim[1]} onChange={e => { const v = parseFloat(e.target.value) || 0; onUpdateNode(node.id, { face: { ...node.face, dim: [dim[0], v, dim[2], v + length] } }); }} /></div>
                </div>
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  <span style={{ fontSize: '8px', color: '#888', width: '30px' }}>SIZE:</span>
                  <div style={coordBox}><label style={labelStyle}>W</label><input style={coordInput} type="number" value={width} onChange={e => { const v = parseFloat(e.target.value) || 0; onUpdateFace(node.id, 2, dim[0] + v); }} /></div>
                  <div style={coordBox}><label style={labelStyle}>L</label><input style={coordInput} type="number" value={length} onChange={e => { const v = parseFloat(e.target.value) || 0; onUpdateFace(node.id, 3, dim[1] + v); }} /></div>
                </div>
                </>
              )}
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
            <button onClick={() => onAddLayer(node.id)} style={{ fontSize: '8px', width: '100%', marginTop: '4px' }}>+ Layer</button>
          </div>

          {showAddMenu && (
            <div ref={addMenuRef} style={{ background: '#1a2a33', padding: '8px', margin: '5px 0', borderRadius: '4px', border: '1px solid #00d4ff' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                <button style={btnSmall} onClick={() => { 
                  onImportChild(node.id, { 
                    id: Math.random().toString(36).substr(2,6), 
                    name: "New Component", 
                    z: 0, 
                    visible: true, 
                    opacity: 1.0, 
                    showBottom: true, 
                    face: { type: "BOX", dim: [0, 0, 20, 20] }, 
                    layers: [{ material: "EMPTY", thk: 5, color: "#369" }], 
                    children: [] 
                  }); 
                  setShowAddMenu(false); 
                }}>+ Quick Dummy</button>
                
                <div style={{ borderTop: '1px solid #333', paddingTop: '5px' }}>
                  <select style={{...inputStyle, width:'100%'}} value={libType} onChange={(e) => setLibType(e.target.value)}>
                    <option value="">Library Category...</option>
                    {Object.keys(COMPONENT_LIBRARY).map(k => <option key={k} value={k}>{k}</option>)}
                  </select>
                  {libType && COMPONENT_LIBRARY[libType].map(m => (
                    <button key={m.model} style={{...btnSmall, width:'100%', marginTop:'2px'}} onClick={async () => {
                      try {
                        const res = await fetch(m.path);
                        const data = await res.json();
                        onImportChild(node.id, formatForImport(data));
                      } catch {
                        onImportChild(node.id, { 
                          name: m.model, 
                          z: 0, 
                          face: { type: "BOX", dim: [0, 0, 15, 15] }, 
                          layers: [{ material: "EMPTY", thk: 5, color: "#9b59b6" }], 
                          children: [] 
                        });
                      }
                      setShowAddMenu(false);
                    }}>{m.model}</button>
                  ))}
                </div>
                <button style={btnSmall} onClick={() => fileInputRef.current?.click()}>📂 Local JSON</button>
                <input type="file" ref={fileInputRef} style={{display:'none'}} onChange={(e) => {
                   const file = e.target.files?.[0]; if(!file) return;
                   const reader = new FileReader();
                   reader.onload = (evt) => {
                     if (evt.target?.result) {
                         const importedNode = JSON.parse(evt.target.result as string);
                         onImportChild(node.id, formatForImport(importedNode));
                     }
                   };
                   reader.readAsText(file); e.target.value = ''; setShowAddMenu(false);
                }} />
              </div>
            </div>
          )}

          {node.children.map(c => <TreeItem key={c.id} {...props} node={c} />)}
        </div>
      )}
    </div>
  );
};

// --- STYLES ---
const btnMain: React.CSSProperties = { width: '100%', padding: '8px', cursor: 'pointer', background: '#00d4ff', color: '#000', fontWeight: 'bold', border: 'none', borderRadius: '4px', fontSize: '11px' };
const btnAction: React.CSSProperties = { fontSize: '8px', cursor: 'pointer', background: '#333', color: '#eee', border: '1px solid #444', padding: '1px 4px', borderRadius: '2px' };
const btnSmall: React.CSSProperties = { background: '#444', color: '#eee', border: 'none', padding: '4px', fontSize: '9px', cursor: 'pointer', borderRadius: '2px', textAlign:'left' };
const inputStyle: React.CSSProperties = { background: '#000', color: '#00d4ff', border: '1px solid #333', fontSize: '10px', padding: '2px', borderRadius: '2px', outline: 'none' };
const coordBox: React.CSSProperties = { display: 'flex', alignItems: 'center', background: '#000', border: '1px solid #333', borderRadius: '2px', padding: '1px 3px' };
const labelStyle: React.CSSProperties = { fontSize: '7px', color: '#555', marginRight: '3px' };
const coordInput: React.CSSProperties = { background: 'transparent', color: '#00d4ff', border: 'none', fontSize: '10px', width: '32px', outline: 'none' };
const ioBoxStyle: React.CSSProperties = { background: '#1a1a1a', border: '1px solid #333', borderRadius: '6px', padding: '10px', display: 'flex', flexDirection: 'column', gap: '8px' };