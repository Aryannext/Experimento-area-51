"""planet - 360 deg Living Planet 3D visualization exporter and interactive ECC Tools Node Workstation."""
from __future__ import annotations

from pathlib import Path


def _planet_styles() -> str:
    return """<style id="graphify-planet-styles">
  #view-mode-bar {
    display: flex; gap: 6px; padding: 10px 12px; border-bottom: 1px solid var(--border);
    background: linear-gradient(180deg, rgba(20,24,48,0.95) 0%, var(--panel) 100%);
  }
  #view-mode-bar button {
    flex: 1; padding: 7px 8px; border-radius: 6px; border: 1px solid var(--input-border);
    background: var(--bg); color: var(--text-2); font-size: 12px; font-weight: 600;
    cursor: pointer; transition: all 0.18s ease; display: flex; align-items: center; justify-content: center; gap: 5px;
  }
  #view-mode-bar button:hover { color: var(--text); border-color: #4E79A7; }
  #view-mode-bar button.active {
    background: linear-gradient(135deg, #2b5876 0%, #4e4376 100%);
    border-color: #6897bb; color: #ffffff; box-shadow: 0 0 12px rgba(78, 121, 167, 0.45);
  }
  #planet-stage {
    flex: 1; position: relative; overflow: hidden; display: none;
    background: radial-gradient(circle at 50% 50%, #0d162c 0%, #060913 68%, #020308 100%);
  }
  #planet-stage.active { display: block; }
  #planet-canvas { width: 100%; height: 100%; display: block; cursor: grab; }
  #planet-canvas:active { cursor: grabbing; }

  /* Persistent HUD visible in BOTH 360 Planet AND 2D Map */
  #planet-hud {
    position: fixed; left: 14px; top: 14px; width: 425px; max-height: calc(100vh - 28px);
    background: rgba(10, 15, 28, 0.94); backdrop-filter: blur(14px);
    border: 1px solid rgba(104, 151, 187, 0.40); border-radius: 12px;
    padding: 14px; color: #e2e8f0; font-size: 12px;
    box-shadow: 0 14px 36px rgba(0, 0, 0, 0.72);
    display: flex; flex-direction: column; gap: 10px; overflow-y: auto; z-index: 999;
  }
  #planet-hud.minimized #planet-hud-body { display: none; }
  #planet-hud.minimized { width: 260px; }
  .planet-hud-header {
    display: flex; align-items: center; justify-content: space-between;
    border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 8px;
  }
  .planet-hud-title {
    font-weight: 700; font-size: 12px; letter-spacing: 0.05em; text-transform: uppercase;
    color: #7dd3fc; display: flex; align-items: center; gap: 6px;
  }
  .planet-live-dot {
    width: 8px; height: 8px; border-radius: 50%; background: #22c55e;
    box-shadow: 0 0 8px #22c55e; animation: planetPulse 2s infinite;
  }
  @keyframes planetPulse {
    0%, 100% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.35); opacity: 0.55; }
  }
  .planet-section-title {
    font-size: 10.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em;
    color: #94a3b8; margin-bottom: 4px;
  }
  .planet-controls-row {
    display: flex; gap: 5px; flex-wrap: wrap;
  }
  .planet-btn {
    background: rgba(30, 41, 59, 0.88); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.25);
    border-radius: 6px; padding: 5px 8px; font-size: 11px; cursor: pointer; transition: all 0.15s;
    flex: 1; text-align: center; white-space: nowrap;
  }
  .planet-btn:hover { background: rgba(51, 65, 85, 0.95); color: #fff; border-color: #7dd3fc; }
  .planet-btn.active { background: rgba(14, 116, 144, 0.60); border-color: #38bdf8; color: #fff; font-weight: 600; }

  .hub-chip {
    display: inline-flex; align-items: center; gap: 4px; margin: 2px 3px 2px 0;
    padding: 4px 8px; border-radius: 6px; font-size: 11px; cursor: pointer;
    background: rgba(30, 41, 59, 0.9); border: 1px solid rgba(125, 211, 252, 0.25);
    color: #e2e8f0; transition: all 0.15s;
  }
  .hub-chip:hover { background: rgba(14, 116, 144, 0.45); border-color: #38bdf8; color: #fff; }
  .hub-chip.selected { background: rgba(14, 116, 144, 0.75); border-color: #7dd3fc; color: #fff; font-weight: 600; }

  #planet-blast-box {
    background: rgba(15, 23, 42, 0.90); border: 1px solid rgba(125, 211, 252, 0.25);
    border-radius: 8px; padding: 10px; font-size: 11.5px; line-height: 1.5;
  }
  .blast-badge {
    display: inline-block; padding: 2px 6px; border-radius: 4px; font-size: 10.5px;
    font-weight: 600; margin-right: 4px; margin-bottom: 3px; cursor: pointer;
  }
  .blast-d1 { background: rgba(239, 68, 68, 0.22); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.45); }
  .blast-d2 { background: rgba(245, 158, 11, 0.20); color: #fcd34d; border: 1px solid rgba(245, 158, 11, 0.45); }
  .blast-out { background: rgba(56, 189, 248, 0.20); color: #7dd3fc; border: 1px solid rgba(56, 189, 248, 0.45); }
  .blast-test { background: rgba(34, 197, 94, 0.20); color: #86efac; border: 1px solid rgba(34, 197, 94, 0.45); }

  /* Touch Tabs (Todo lo que toca) */
  .touch-tabs {
    display: flex; gap: 4px; margin-top: 6px; margin-bottom: 4px;
  }
  .touch-tab {
    flex: 1; padding: 4px 5px; font-size: 10.5px; font-weight: 600; border-radius: 5px;
    background: rgba(30, 41, 59, 0.7); color: #94a3b8; border: 1px solid rgba(148,163,184,0.2);
    cursor: pointer; text-align: center;
  }
  .touch-tab.active {
    background: rgba(15, 118, 110, 0.45); color: #fff; border-color: #2dd4bf;
  }

  .dep-list {
    max-height: 125px; overflow-y: auto; margin-top: 4px; padding: 2px;
    background: rgba(2, 6, 23, 0.45); border-radius: 6px;
  }
  .dep-item {
    padding: 4px 6px; border-radius: 4px; cursor: pointer; font-size: 11px;
    display: flex; justify-content: space-between; align-items: center; gap: 6px;
    border-bottom: 1px solid rgba(255,255,255,0.04);
  }
  .dep-item:hover { background: rgba(56, 189, 248, 0.16); }

  /* ECC Tools Action Bar & Full Agent Catalog inside Node Inspector */
  .ecc-cat-bar {
    display: flex; gap: 4px; flex-wrap: wrap; margin-top: 6px;
  }
  .ecc-cat-pill {
    padding: 3px 7px; border-radius: 999px; font-size: 10px; font-weight: 700;
    background: rgba(30, 41, 59, 0.85); color: #94a3b8; border: 1px solid rgba(148, 163, 184, 0.25);
    cursor: pointer; transition: all 0.14s;
  }
  .ecc-cat-pill:hover { color: #f8fafc; border-color: #818cf8; }
  .ecc-cat-pill.active {
    background: linear-gradient(135deg, #4338ca 0%, #0e7490 100%);
    color: #fff; border-color: #a5b4fc; box-shadow: 0 0 8px rgba(99, 102, 241, 0.45);
  }
  .ecc-search-input {
    width: 100%; margin-top: 6px; padding: 5px 8px; border-radius: 6px;
    background: rgba(2, 6, 23, 0.65); border: 1px solid rgba(129, 140, 248, 0.32);
    color: #f8fafc; font-size: 11px; outline: none; box-sizing: border-box;
  }
  .ecc-search-input:focus { border-color: #38bdf8; box-shadow: 0 0 6px rgba(56, 189, 248, 0.35); }
  .ecc-tools-bar {
    display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 5px;
    margin-top: 6px; max-height: 155px; overflow-y: auto; padding: 3px;
    background: rgba(2, 6, 23, 0.45); border-radius: 6px;
  }
  .ecc-tool-btn {
    padding: 6px 7px; border-radius: 6px; font-size: 10.5px; font-weight: 700;
    background: rgba(30, 27, 75, 0.62); color: #e0e7ff; border: 1px solid rgba(129, 140, 248, 0.32);
    cursor: pointer; text-align: left; transition: all 0.15s; display: flex; flex-direction: column; gap: 2px;
  }
  .ecc-tool-btn:hover { background: rgba(67, 56, 202, 0.78); color: #fff; border-color: #a5b4fc; }
  .ecc-tool-btn.active {
    background: linear-gradient(135deg, #4f46e5 0%, #0369a1 100%);
    color: #fff; border-color: #7dd3fc; box-shadow: 0 0 10px rgba(79, 70, 229, 0.55);
  }
  .ecc-tool-btn.is-rec { border-left: 3px solid #f59e0b; }
  .ecc-tool-sub {
    font-size: 9.5px; font-weight: 500; color: #cbd5e1; opacity: 0.9;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  .ecc-rec-badge {
    display: inline-block; font-size: 9px; font-weight: 700; color: #fde68a;
    background: rgba(245, 158, 11, 0.18); border: 1px solid rgba(245, 158, 11, 0.4);
    border-radius: 4px; padding: 1px 4px; margin-top: 1px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }

  .ecc-gate-box {
    margin-top: 6px; padding: 9px; border-radius: 6px;
    background: rgba(30, 27, 75, 0.68); border-left: 3px solid #818cf8;
    font-size: 11px; color: #e0e7ff; line-height: 1.45;
  }
  .ecc-copy-row {
    display: flex; gap: 5px; margin-top: 7px;
  }
  .ecc-copy-btn {
    flex: 2; padding: 6px 8px; border-radius: 5px;
    background: linear-gradient(135deg, #0284c7 0%, #4f46e5 100%);
    color: #fff; border: 1px solid #7dd3fc; font-size: 11px; font-weight: 700;
    cursor: pointer; text-align: center;
  }
  .ecc-copy-btn.secondary {
    flex: 1; background: rgba(30, 41, 59, 0.9); border-color: rgba(148, 163, 184, 0.45);
    color: #cbd5e1; font-size: 10.5px;
  }
  .ecc-copy-btn:hover { filter: brightness(1.12); }

  #planet-telemetry-feed {
    max-height: 68px; overflow-y: auto; font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: 10.5px; color: #94a3b8; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 6px;
  }
  .telemetry-row { margin-bottom: 3px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .telemetry-row b { color: #38bdf8; }
</style>"""


def _planet_script(default_planet: bool = False) -> str:
    default_mode_js = "true" if default_planet else "false"
    return f"""<script id="graphify-planet-engine">
(function() {{
  if (typeof RAW_NODES === 'undefined' || typeof RAW_EDGES === 'undefined') return;
  const graphEl = document.getElementById('graph');
  const sidebarEl = document.getElementById('sidebar');
  if (!graphEl || !sidebarEl || !graphEl.parentNode) return;
  const esc = s => String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');

  // Inject 2D <-> 360 deg Living Planet switcher at top of sidebar
  const modeBar = document.createElement('div');
  modeBar.id = 'view-mode-bar';
  modeBar.innerHTML = `
    <button type="button" id="btn-mode-2d" class="${{!{default_mode_js} ? 'active' : ''}}">&#x1f5fa;&#xfe0f; Mapa 2D Limpio</button>
    <button type="button" id="btn-mode-planet" class="${{{default_mode_js} ? 'active' : ''}}">&#x1fa90; Planeta 360&deg; Vivo</button>
  `;
  sidebarEl.insertBefore(modeBar, sidebarEl.firstChild);

  // Create the 3D Planet Stage alongside #graph
  const planetStage = document.createElement('div');
  planetStage.id = 'planet-stage';
  planetStage.innerHTML = `<canvas id="planet-canvas"></canvas>`;
  graphEl.parentNode.insertBefore(planetStage, graphEl);

  // Create the Persistent ECC x Graphify HUD (works in BOTH 360 Planet AND 2D Map!)
  const hudEl = document.createElement('div');
  hudEl.id = 'planet-hud';
  hudEl.innerHTML = `
    <div class="planet-hud-header">
      <div class="planet-hud-title"><span class="planet-live-dot" id="planet-live-dot"></span> PLANETA 360&deg; &middot; ECC &times; GRAPHIFY</div>
      <div style="display:flex;align-items:center;gap:6px">
        <span id="planet-fps" style="font-size:10px;color:#64748b">60 FPS</span>
        <button type="button" id="btn-hud-min" style="background:transparent;border:1px solid #475569;color:#cbd5e1;border-radius:4px;padding:1px 6px;cursor:pointer;font-size:10px" title="Minimizar/Expandir panel">_</button>
      </div>
    </div>
    <div id="planet-hud-body" style="display:flex;flex-direction:column;gap:10px">
      <div>
        <div class="planet-section-title">1. Nivel de Claridad (Aplica en 3D y 2D)</div>
        <div class="planet-controls-row">
          <button type="button" class="planet-btn active" id="btn-lod-files" title="Muestra solo los archivos principales sin ruido de funciones">&#x1f3db;&#xfe0f; Solo Archivos</button>
          <button type="button" class="planet-btn" id="btn-lod-tests" title="Incluye archivos de prueba">+ &#x1f9ea; Tests</button>
          <button type="button" class="planet-btn" id="btn-lod-all" title="Muestra todos los simbolos y funciones del AST">&#x1f52c; Todo (${{RAW_NODES.length}})</button>
        </div>
      </div>

      <div>
        <div class="planet-section-title">2. Filtros de Conexiones</div>
        <div class="planet-controls-row">
          <button type="button" class="planet-btn active" id="btn-planet-spin">&#x1f504; Giro Auto</button>
          <button type="button" class="planet-btn active" id="btn-planet-edges-focus">&#x1f3af; Lineas: Solo Nodo Activo</button>
          <button type="button" class="planet-btn" id="btn-planet-reset">&#x1f30d; Ver Todos</button>
        </div>
      </div>

      <div>
        <div class="planet-section-title">3. &#x1f9ed; Nodos Principales (&iquest;Por d&oacute;nde empezar?)</div>
        <div id="planet-top-hubs"></div>
      </div>

      <div>
        <div class="planet-section-title">4. &#x1f6e0;&#xfe0f; Todo lo que toca este Nodo + Herramientas ECC</div>
        <div id="planet-blast-box">
          <span style="color:#94a3b8">Haz clic en cualquier nodo (en el Planeta 3D o en el Mapa 2D) para ver todo lo que toca y ejecutar las herramientas de <b>ECC Tools</b> sobre &eacute;l.</span>
        </div>
      </div>

      <div id="planet-telemetry-feed">
        <div class="telemetry-row"><b>[SISTEMA]</b> Panel ECC activo en 3D y 2D. Haz clic en cualquier nodo.</div>
      </div>
    </div>
  `;
  graphEl.parentNode.insertBefore(hudEl, planetStage);

  const canvas = document.getElementById('planet-canvas');
  const ctx = canvas.getContext('2d');
  let isPlanetActive = {default_mode_js};
  let autoSpin = true;
  let focusEdgesOnly = true;
  let lodMode = 'files'; // 'files' | 'tests' | 'all'
  let activeTouchTab = 'in'; // 'in' (quien lo usa) | 'out' (que toca) | 'tests' (pruebas) | 'symbols' (funciones dentro del archivo)
  let activeEccCategory = 'rec'; // 'rec' | 'arch' | 'frontend' | 'backend' | 'quality' | 'testing' | 'orch' | 'all'
  let eccSearchQuery = '';
  let activeEccTool = 'gateguard';

  let rotY = 0.4;
  let rotX = 0.22;
  let velY = 0.0018;
  let velX = 0.0;
  let zoom = 1.0;
  let targetRotY = null;
  let targetRotX = null;
  let isDragging = false;
  let dragStartX = 0;
  let dragStartY = 0;
  let selectedNodeId = null;
  let hoveredPlanetNodeId = null;

  let blastRadiusMap = new Map();
  let blastEdgesSet = new Set();
  let shockwaves = [];
  let lastStats = null;

  function isTestNode(n) {{
    const sf = String(n.source_file || '').toLowerCase();
    const lbl = String(n.label || '').toLowerCase();
    return sf.includes('test') || sf.includes('spec') || lbl.includes('.spec.') || lbl.includes('.test.') || lbl.startsWith('test_');
  }}

  function isFileLevelNode(n) {{
    const lbl = String(n.label || '');
    const sf = String(n.source_file || '');
    const base = sf.split(/[\\\\/]/).pop() || '';
    if (!lbl.endsWith('()') && (lbl === base || /\\.(vue|js|ts|tsx|jsx|py|go|rs|java|sql|md|json)$/i.test(lbl))) {{
      return true;
    }}
    return false;
  }}

  const primaryNodePerFile = new Map();
  RAW_NODES.forEach(n => {{
    const sf = String(n.source_file || '');
    if (!sf) return;
    const prev = primaryNodePerFile.get(sf);
    if (!prev || isFileLevelNode(n) || (!isFileLevelNode(prev) && (n.degree || 0) > (prev.degree || 0))) {{
      primaryNodePerFile.set(sf, n);
    }}
  }});
  const promotedIds = new Set(Array.from(primaryNodePerFile.values()).map(n => n.id));

  const commIds = Array.from(new Set(RAW_NODES.map(n => n.community ?? 0))).sort((a, b) => a - b);
  const numComms = Math.max(commIds.length, 1);
  const goldenAngle = Math.PI * (3 - Math.sqrt(5));
  const continentCenters = new Map();

  commIds.forEach((cid, idx) => {{
    const y = numComms === 1 ? 0 : 1 - (idx / (numComms - 1)) * 1.65;
    const theta = goldenAngle * idx;
    const lat = Math.asin(Math.max(-1, Math.min(1, y)));
    const lon = ((theta % (Math.PI * 2)) + Math.PI * 2) % (Math.PI * 2) - Math.PI;
    continentCenters.set(cid, {{
      cid,
      lat,
      lon,
      ux: Math.cos(lat) * Math.sin(lon),
      uy: Math.sin(lat),
      uz: Math.cos(lat) * Math.cos(lon),
    }});
  }});

  const nodesByComm = new Map();
  RAW_NODES.forEach(n => {{
    const cid = n.community ?? 0;
    if (!nodesByComm.has(cid)) nodesByComm.set(cid, []);
    nodesByComm.get(cid).push(n);
  }});

  const allDegrees = RAW_NODES.map(n => n.degree || 1).sort((a, b) => a - b);
  const hubThreshold = allDegrees[Math.floor(allDegrees.length * 0.88)] || 5;

  const planetNodes = [];
  const nodeById = new Map();

  nodesByComm.forEach((members, cid) => {{
    const center = continentCenters.get(cid) || {{ lat: 0, lon: 0 }};
    members.sort((a, b) => (b.degree || 0) - (a.degree || 0));
    const count = members.length;
    members.forEach((n, i) => {{
      const isTest = isTestNode(n);
      const isFileOrPromoted = isFileLevelNode(n) || promotedIds.has(n.id);
      const isHub = (n.degree || 0) >= hubThreshold || Boolean(n.member_count);

      let orbitLayer = 'surface';
      let altitude = 1.0;
      if (isHub && isFileOrPromoted && !isTest) {{
        orbitLayer = 'core-hub';
        altitude = 0.96;
      }} else if (isTest || !isFileOrPromoted) {{
        orbitLayer = 'satellite';
        altitude = 1.06 + (i % 3) * 0.02;
      }}

      const maxSpread = Math.min(0.42, 0.12 + Math.sqrt(count) * 0.038);
      const r = count <= 1 ? 0 : maxSpread * Math.sqrt((i + 0.5) / count);
      const a = i * goldenAngle;
      const lat = Math.max(-1.42, Math.min(1.42, center.lat + r * Math.sin(a)));
      const lon = center.lon + (r * Math.cos(a)) / Math.max(0.28, Math.cos(lat));

      const ux = Math.cos(lat) * Math.sin(lon);
      const uy = Math.sin(lat);
      const uz = Math.cos(lat) * Math.cos(lon);
      const bgColor = (n.color && n.color.background) ? n.color.background : '#4E79A7';
      const lStatus = n['learning_' + 'status'] || null;
      const lStale = Boolean(n['learning_' + 'stale']);

      const pNode = {{
        id: n.id,
        label: n.label || String(n.id),
        raw: n,
        community: cid,
        communityName: n.community_name || ('Comunidad ' + cid),
        sourceFile: n.source_file || '',
        degree: n.degree || 1,
        baseSize: Math.max(5, Math.min(18, (n.size || 10) * 0.52)),
        color: bgColor,
        learningStatus: lStatus,
        learningStale: lStale,
        isTest,
        isFileOrPromoted,
        isHub,
        orbitLayer,
        altitude,
        ux, uy, uz,
        orbitPhase: (i * 1.37) % (Math.PI * 2),
        orbitSpeed: orbitLayer === 'satellite' ? (0.0025 + (i % 5) * 0.0005) : 0,
        sx: 0, sy: 0, sz: 0, scale: 1, visible: true,
      }};
      planetNodes.push(pNode);
      nodeById.set(n.id, pNode);
    }});
  }});

  const planetEdges = [];
  const adjacencyReverse = new Map();
  const adjacencyForward = new Map();

  RAW_EDGES.forEach((e, idx) => {{
    const src = nodeById.get(e.from);
    const tgt = nodeById.get(e.to);
    if (!src || !tgt || src === tgt) return;

    const conf = e.confidence || 'EXTRACTED';
    const rel = (e.title || e.label || 'calls').split(' ')[0];
    const chord = Math.hypot(src.ux - tgt.ux, src.uy - tgt.uy, src.uz - tgt.uz);
    let mx = (src.ux + tgt.ux) * 0.5;
    let my = (src.uy + tgt.uy) * 0.5;
    let mz = (src.uz + tgt.uz) * 0.5;
    let mlen = Math.hypot(mx, my, mz);
    if (mlen < 1e-4) {{
      mx = -src.uy; my = src.ux; mz = 0;
      mlen = Math.hypot(mx, my, mz) || 1;
    }}
    mx /= mlen; my /= mlen; mz /= mlen;
    const arcAltitude = 1.07 + chord * 0.34 + (src.community !== tgt.community ? 0.10 : 0.0);

    const edgeObj = {{
      id: idx,
      src,
      tgt,
      relation: rel,
      confidence: conf,
      mx: mx * arcAltitude,
      my: my * arcAltitude,
      mz: mz * arcAltitude,
      photonOffset: (idx * 0.23) % 1.0,
      photonSpeed: conf === 'EXTRACTED' ? 0.006 : (conf === 'INFERRED' ? 0.0035 : 0.002),
    }};
    planetEdges.push(edgeObj);

    if (!adjacencyReverse.has(tgt.id)) adjacencyReverse.set(tgt.id, []);
    adjacencyReverse.get(tgt.id).push({{ peer: src.id, relation: rel, edgeId: idx }});
    if (!adjacencyForward.has(src.id)) adjacencyForward.set(src.id, []);
    adjacencyForward.get(src.id).push({{ peer: tgt.id, relation: rel, edgeId: idx }});
  }});

  function isNodeAllowedByLod(pNode) {{
    if (pNode.id === selectedNodeId || blastRadiusMap.has(pNode.id)) return true;
    if (lodMode === 'files') return pNode.isFileOrPromoted && !pNode.isTest;
    if (lodMode === 'tests') return pNode.isFileOrPromoted || pNode.isTest;
    return true;
  }}

  function syncLodVisibility() {{
    const hiddenComms = typeof hiddenCommunities !== 'undefined' ? hiddenCommunities : new Set();
    planetNodes.forEach(pNode => {{
      pNode.visible = !hiddenComms.has(pNode.community) && isNodeAllowedByLod(pNode);
    }});

    if (typeof nodesDS !== 'undefined' && typeof edgesDS !== 'undefined' && nodesDS.update) {{
      try {{
        const visibleIds = new Set(planetNodes.filter(n => n.visible).map(n => n.id));
        const nodeUpdates = RAW_NODES.map(n => ({{
          id: n.id,
          hidden: !visibleIds.has(n.id),
        }}));
        nodesDS.update(nodeUpdates);

        const edgeUpdates = RAW_EDGES.map((e, i) => {{
          const bothVisible = visibleIds.has(e.from) && visibleIds.has(e.to);
          const isFocused = !focusEdgesOnly || !selectedNodeId || blastEdgesSet.has(i) || e.from === selectedNodeId || e.to === selectedNodeId;
          return {{
            id: i,
            hidden: !(bothVisible && isFocused),
          }};
        }});
        edgesDS.update(edgeUpdates);
      }} catch (_) {{}}
    }}
  }}

  // Compute EVERYTHING this node touches: Incoming (D1/D2), Outgoing (what it calls/imports), Tests, and File Symbols
  function computeBlastRadius(seedId) {{
    blastRadiusMap.clear();
    blastEdgesSet.clear();
    if (!seedId || !nodeById.has(seedId)) {{
      return {{ d1: [], d2: [], tests: [], outgoing: [], fileSymbols: [] }};
    }}

    const seedNode = nodeById.get(seedId);
    const seedGroup = new Set([seedId]);
    const fileSymbols = [];
    if (seedNode.sourceFile) {{
      planetNodes.forEach(n => {{
        if (n.sourceFile === seedNode.sourceFile) {{
          if (seedNode.isFileOrPromoted) seedGroup.add(n.id);
          if (n.id !== seedId) {{
            fileSymbols.push({{ id: n.id, label: n.label, file: n.sourceFile, relation: 'defines' }});
          }}
        }}
      }});
    }}

    seedGroup.forEach(id => blastRadiusMap.set(id, 0));
    const queue = Array.from(seedGroup).map(id => ({{ id, depth: 0 }}));
    const d1List = [];
    const d2List = [];
    const testsList = [];
    const testsSeen = new Set();
    const outgoingList = [];
    const outSeen = new Set();

    // Outgoing: everything this node/file touches (imports, calls, uses, queries)
    seedGroup.forEach(id => {{
      const fwd = adjacencyForward.get(id) || [];
      fwd.forEach(step => {{
        if (seedGroup.has(step.peer)) return;
        blastEdgesSet.add(step.edgeId);
        if (!blastRadiusMap.has(step.peer)) {{
          blastRadiusMap.set(step.peer, 1);
        }}
        const peerNode = nodeById.get(step.peer);
        if (peerNode && !outSeen.has(peerNode.id)) {{
          outSeen.add(peerNode.id);
          outgoingList.push({{
            id: peerNode.id,
            label: peerNode.label,
            file: peerNode.sourceFile,
            relation: step.relation,
          }});
        }}
      }});
    }});

    // Incoming: everything that depends on this node/file (D1 & D2) + Tests
    const d1Seen = new Set();
    while (queue.length > 0) {{
      const curr = queue.shift();
      if (curr.depth >= 2) continue;
      const incoming = adjacencyReverse.get(curr.id) || [];
      for (const step of incoming) {{
        if (seedGroup.has(step.peer)) continue;
        blastEdgesSet.add(step.edgeId);
        const peerNode = nodeById.get(step.peer);
        if (peerNode && peerNode.isTest && !testsSeen.has(peerNode.id)) {{
          testsSeen.add(peerNode.id);
          testsList.push({{
            id: peerNode.id,
            label: peerNode.label,
            file: peerNode.sourceFile || peerNode.label,
            relation: step.relation,
          }});
        }}
        const nextDepth = curr.depth + 1;
        if (nextDepth === 1 && peerNode && !d1Seen.has(peerNode.id)) {{
          d1Seen.add(peerNode.id);
          d1List.push({{
            id: peerNode.id,
            label: peerNode.label,
            file: peerNode.sourceFile,
            relation: step.relation,
          }});
        }}
        if (!blastRadiusMap.has(step.peer)) {{
          blastRadiusMap.set(step.peer, nextDepth);
          if (nextDepth === 2 && peerNode) {{
            d2List.push({{
              id: peerNode.id,
              label: peerNode.label,
              file: peerNode.sourceFile,
              relation: step.relation,
            }});
          }}
          queue.push({{ id: step.peer, depth: nextDepth }});
        }}
      }}
    }}
    return {{ d1: d1List, d2: d2List, tests: testsList, outgoing: outgoingList, fileSymbols }};
  }}

  function triggerShockwave(nodeId, color) {{
    if (!nodeById.has(nodeId)) return;
    shockwaves.push({{
      nodeId,
      radius: 5,
      maxRadius: 72,
      color: color || '#38bdf8',
      alpha: 0.95,
    }});
  }}

  function logTelemetry(actor, text) {{
    const feed = document.getElementById('planet-telemetry-feed');
    if (!feed) return;
    const row = document.createElement('div');
    row.className = 'telemetry-row';
    const ts = new Date().toLocaleTimeString([], {{ hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }});
    row.innerHTML = `<span style="color:#475569">${{ts}}</span> <b>[${{esc(actor)}}]</b> ${{esc(text)}}`;
    feed.insertBefore(row, feed.firstChild);
    while (feed.children.length > 15) feed.removeChild(feed.lastChild);
  }}

  function renderTopHubsBar() {{
    const container = document.getElementById('planet-top-hubs');
    if (!container) return;
    const candidates = planetNodes
      .filter(n => n.isFileOrPromoted && !n.isTest)
      .sort((a, b) => b.degree - a.degree)
      .slice(0, 6);
    const list = candidates.length ? candidates : planetNodes.slice().sort((a, b) => b.degree - a.degree).slice(0, 6);
    container.innerHTML = list.map(n => {{
      const shortName = (n.sourceFile ? n.sourceFile.split(/[\\\\/]/).pop() : n.label) || n.label;
      const isSel = n.id === selectedNodeId ? 'selected' : '';
      return `<button type="button" class="hub-chip ${{isSel}}" data-hub-id="${{esc(n.id)}}">&#x1f4cc; ${{esc(shortName)}} <span style="color:#7dd3fc">(${{n.degree}})</span></button>`;
    }}).join('');
    if (container.querySelectorAll) {{
      container.querySelectorAll('.hub-chip').forEach(btn => {{
        btn.addEventListener('click', () => {{
          const nid = btn.getAttribute('data-hub-id');
          if (nid) flyToPlanetNode(nid, 'NODO-PRINCIPAL');
        }});
      }});
    }}
  }}

  // Full Catalog of ECC Agents, Slash Commands & Hooks (65+ tools from ECC-main)
  const ECC_CATALOG = [
    // --- Control & Hooks ---
    {{ id: 'gateguard', name: 'GateGuard AST', cmd: 'GateGuard', icon: '&#x1f6e1;&#xfe0f;', cat: 'orch', kind: 'Hook Activo', desc: 'Compuerta pre-edicion que exige verificar dependientes antes de tocar el archivo.', focus: 'Proteccion de radio de impacto, contratos de llamadas y prevencion de regresiones.' }},
    // --- Arquitectura & Planificacion ---
    {{ id: 'plan', name: 'planner (/plan)', cmd: '/plan', icon: '&#x1f4d0;', cat: 'arch', kind: 'Agente + Comando', desc: 'Analiza requisitos, riesgos y dependencias del grafo para crear un plan paso a paso.', focus: 'Secuencia de archivos a modificar, contratos de entrada/salida y estrategia de pruebas.' }},
    {{ id: 'architect', name: 'architect', cmd: '@architect', icon: '&#x1f3db;&#xfe0f;', cat: 'arch', kind: 'Agente ECC', desc: 'Arquitecto de sistemas: evalua acoplamiento entre capas, escalabilidad y diseno modular.', focus: 'Desacoplar modulos, evitar dependencias circulares y respetar limites de capas.' }},
    {{ id: 'code-architect', name: 'code-architect', cmd: '@code-architect', icon: '&#x1f9e9;', cat: 'arch', kind: 'Agente ECC', desc: 'Disena patrones de codigo limpios, interfaces y contratos entre componentes.', focus: 'Cohesion interna del archivo, firmas de funciones y reutilizacion limpia.' }},
    {{ id: 'code-explorer', name: 'code-explorer', cmd: '@code-explorer', icon: '&#x1f9ed;', cat: 'arch', kind: 'Agente ECC', desc: 'Rastrea flujos de ejecucion de extremo a extremo a traves de las conexiones del grafo.', focus: 'Trazabilidad completa desde la vista hasta la base de datos o servicio externo.' }},
    {{ id: 'spec-miner', name: 'spec-miner', cmd: '@spec-miner', icon: '&#x26cf;&#xfe0f;', cat: 'arch', kind: 'Agente ECC', desc: 'Extrae reglas de negocio implicitas, invariantes y especificaciones verificables.', focus: 'Documentar y proteger la logica de negocio critica contenida en este nodo.' }},
    {{ id: 'gan-planner', name: 'gan-planner (/gan-design)', cmd: '/gan-design', icon: '&#x2694;&#xfe0f;', cat: 'arch', kind: 'Agente + Comando', desc: 'Planificacion adversaria GAN: propone diseno y lo somete a critica rigurosa.', focus: 'Detectar puntos ciegos arquitectonicos antes de escribir codigo.' }},
    {{ id: 'plan-prd', name: '/plan-prd', cmd: '/plan-prd', icon: '&#x1f4dd;', cat: 'arch', kind: 'Comando ECC', desc: 'Genera un Documento de Requisitos de Producto (PRD) tecnico centrado en este modulo.', focus: 'Alcance funcional, criterios de aceptacion y metricas de exito.' }},
    {{ id: 'multi-plan', name: '/multi-plan', cmd: '/multi-plan', icon: '&#x1f5fa;&#xfe0f;', cat: 'arch', kind: 'Comando ECC', desc: 'Coordina planificacion multi-agente cuando el nodo impacta varias capas a la vez.', focus: 'Sincronizar cambios entre Frontend, Logica y Base de Datos.' }},
    {{ id: 'update-codemaps', name: '/update-codemaps', cmd: '/update-codemaps', icon: '&#x1f5fd;', cat: 'arch', kind: 'Comando ECC', desc: 'Actualiza los mapas de arquitectura y referencias del proyecto a partir del AST.', focus: 'Mantener la cartografia del repositorio al dia tras cambios estructurales.' }},

    // --- Frontend, Vue, React, UI & Accesibilidad ---
    {{ id: 'vue-reviewer', name: 'vue-reviewer (/vue-review)', cmd: '/vue-review', icon: '&#x1f49a;', cat: 'frontend', kind: 'Agente + Comando', desc: 'Especialista en Vue 3, Composition API, reactivity, props/emits, Pinia y ciclo de vida.', focus: 'Reactividad sin fugas de memoria, computed vs watch, props inmutables y limpieza de eventos.' }},
    {{ id: 'a11y-architect', name: 'a11y-architect', cmd: '@a11y-architect', icon: '&#x267f;', cat: 'frontend', kind: 'Agente ECC', desc: 'Arquitecto de Accesibilidad UI: audita WCAG, navegacion por teclado, ARIA y contraste.', focus: 'Roles ARIA, foco de teclado en modales/formularios y etiquetas semanticas.' }},
    {{ id: 'multi-frontend', name: '/multi-frontend', cmd: '/multi-frontend', icon: '&#x1f3a8;', cat: 'frontend', kind: 'Comando ECC', desc: 'Orquestador especializado en construir o mejorar vistas, componentes UI y estados.', focus: 'Consistencia visual, estados de carga/error (skeletons) y experiencia de usuario.' }},
    {{ id: 'react-reviewer', name: 'react-reviewer (/react-review)', cmd: '/react-review', icon: '&#x269b;&#xfe0f;', cat: 'frontend', kind: 'Agente + Comando', desc: 'Especialista en React, Hooks, efectos, memoizacion y renderizado eficiente.', focus: 'Evitar re-renders innecesarios, dependencias de hooks y limpieza de efectos.' }},
    {{ id: 'flutter-reviewer', name: 'flutter-reviewer (/flutter-review)', cmd: '/flutter-review', icon: '&#x1f98b;', cat: 'frontend', kind: 'Agente + Comando', desc: 'Especialista en widgets Flutter, gestion de estado y rendimiento movil.', focus: 'Arbol de widgets limpio, const constructors y disposicion de controladores.' }},
    {{ id: 'seo-specialist', name: 'seo-specialist', cmd: '@seo-specialist', icon: '&#x1f310;', cat: 'frontend', kind: 'Agente ECC', desc: 'Audita metadatos, estructura semantica HTML, rendimiento percibido y rutas publicas.', focus: 'Jerarquia de encabezados, atributos alt y optimizacion de carga.' }},

    // --- Base de Datos, Backend, Redes & Seguridad ---
    {{ id: 'database-reviewer', name: 'database-reviewer', cmd: '@database-reviewer', icon: '&#x1f5c4;&#xfe0f;', cat: 'backend', kind: 'Agente ECC', desc: 'Especialista en Base de Datos, consultas SQL, indices, migraciones y transacciones.', focus: 'Consultas parametrizadas, prevencion de N+1, indices adecuados e integridad transaccional.' }},
    {{ id: 'security-reviewer', name: 'security-reviewer (/security-scan)', cmd: '/security-scan', icon: '&#x1f512;', cat: 'backend', kind: 'Agente + Comando', desc: 'Auditor de Seguridad: detecta inyeccion SQL/XSS, fugas de secretos, auth/PIN y permisos.', focus: 'Validacion de entradas, sanitizacion de payloads, manejo de credenciales y control de acceso.' }},
    {{ id: 'silent-failure-hunter', name: 'silent-failure-hunter', cmd: '@silent-failure-hunter', icon: '&#x1f575;&#xfe0f;', cat: 'backend', kind: 'Agente ECC', desc: 'Cazador de fallos silenciosos: detecta bloques catch vacios, promesas sueltas y errores tragados.', focus: 'Garantizar que ningun error de red, BD o logica pase desapercibido sin log o feedback.' }},
    {{ id: 'performance-optimizer', name: 'performance-optimizer', cmd: '@performance-optimizer', icon: '&#x26a1;', cat: 'backend', kind: 'Agente ECC', desc: 'Detecta cuellos de botella de CPU/memoria, consultas pesadas y bucles ineficientes.', focus: 'Reducir latencia, optimizar estructuras de datos y cachear calculos costosos.' }},
    {{ id: 'network-architect', name: 'network-architect', cmd: '@network-architect', icon: '&#x1f5a7;', cat: 'backend', kind: 'Agente ECC', desc: 'Disena integraciones de red, APIs REST/WebSockets, bots (Telegram/WhatsApp) y webhooks.', focus: 'Resiliencia de red, reintentos con backoff, idempotencia y contratos de API.' }},
    {{ id: 'network-troubleshooter', name: 'network-troubleshooter', cmd: '@network-troubleshooter', icon: '&#x1f4e1;', cat: 'backend', kind: 'Agente ECC', desc: 'Diagnostica timeouts, caidas de sincronizacion, CORS y errores de comunicacion externa.', focus: 'Manejo de desconexion offline, timeouts claros y recuperacion ante fallos de API.' }},
    {{ id: 'multi-backend', name: '/multi-backend', cmd: '/multi-backend', icon: '&#x2699;&#xfe0f;', cat: 'backend', kind: 'Comando ECC', desc: 'Orquestador para desarrollar y blindar servicios backend, persistencia y colas.', focus: 'Arquitectura de servicios robusta, validacion de esquemas y pruebas de integracion.' }},
    {{ id: 'fastapi-reviewer', name: 'fastapi-reviewer (/fastapi-review)', cmd: '/fastapi-review', icon: '&#x1f680;', cat: 'backend', kind: 'Agente + Comando', desc: 'Especialista en APIs FastAPI, Pydantic, async/await e inyeccion de dependencias.', focus: 'Tipado de esquemas Pydantic, endpoints async no bloqueantes y codigos HTTP.' }},
    {{ id: 'django-reviewer', name: 'django-reviewer', cmd: '@django-reviewer', icon: '&#x1f33f;', cat: 'backend', kind: 'Agente ECC', desc: 'Especialista en Django ORM, migraciones, vistas y seguridad de sesiones.', focus: 'select_related/prefetch_related, migraciones seguras y permisos.' }},

    // --- Revision de Codigo, Refactor & Lenguajes ---
    {{ id: 'review', name: 'code-reviewer (/code-review)', cmd: '/code-review', icon: '&#x1f50d;', cat: 'quality', kind: 'Agente + Comando', desc: 'Revisor general de calidad, legibilidad, contratos AST y prevencion de regresiones.', focus: 'Confirmar que los cambios respetan a todos los consumidores directos del nodo.' }},
    {{ id: 'refactor-cleaner', name: 'refactor-cleaner (/refactor-clean)', cmd: '/refactor-clean', icon: '&#x1f9f9;', cat: 'quality', kind: 'Agente + Comando', desc: 'Elimina codigo muerto, imports no usados, duplicacion y deuda tecnica de forma segura.', focus: 'Limpiar funciones obsoletas verificando en el grafo que nadie las llame.' }},
    {{ id: 'code-simplifier', name: 'code-simplifier', cmd: '@code-simplifier', icon: '&#x2702;&#xfe0f;', cat: 'quality', kind: 'Agente ECC', desc: 'Simplifica funciones largas o con alta complejidad ciclomatica sin cambiar su comportamiento.', focus: 'Extraer helpers claros, reducir anidamiento if/else y mejorar legibilidad.' }},
    {{ id: 'typescript-reviewer', name: 'typescript-reviewer', cmd: '@typescript-reviewer', icon: '&#x1f4d8;', cat: 'quality', kind: 'Agente ECC', desc: 'Especialista en TypeScript/JavaScript moderno, inferencia de tipos, promesas y modulos ES.', focus: 'Eliminar any implicitos, asegurar null-safety y contratos de datos claros.' }},
    {{ id: 'type-design-analyzer', name: 'type-design-analyzer', cmd: '@type-design-analyzer', icon: '&#x1f9ec;', cat: 'quality', kind: 'Agente ECC', desc: 'Analiza el diseno de modelos de datos, interfaces, DTOs y estados de dominio.', focus: 'Hacer que los estados invalidos sean irrepresentables mediante buenos modelos.' }},
    {{ id: 'python-reviewer', name: 'python-reviewer (/python-review)', cmd: '/python-review', icon: '&#x1f40d;', cat: 'quality', kind: 'Agente + Comando', desc: 'Especialista en Python idiomatico, type hints, manejo de excepciones y rendimiento.', focus: 'PEP 8, tipado estatico, context managers y estructuras pythonicas.' }},
    {{ id: 'go-reviewer', name: 'go-reviewer (/go-review)', cmd: '/go-review', icon: '&#x1f439;', cat: 'quality', kind: 'Agente + Comando', desc: 'Especialista en Go, goroutines, channels, interfaces y manejo explicito de errores.', focus: 'Concurrencia sin race conditions, context cancellation y errores envueltos.' }},
    {{ id: 'rust-reviewer', name: 'rust-reviewer (/rust-review)', cmd: '/rust-review', icon: '&#x1f980;', cat: 'quality', kind: 'Agente + Comando', desc: 'Especialista en Rust, ownership, borrowing, lifetimes y manejo de Result/Option.', focus: 'Seguridad de memoria sin unwrap peligrosos y uso idiomatico de traits.' }},
    {{ id: 'kotlin-reviewer', name: 'kotlin-reviewer (/kotlin-review)', cmd: '/kotlin-review', icon: '&#x1f536;', cat: 'quality', kind: 'Agente + Comando', desc: 'Especialista en Kotlin, coroutines, Flow y null-safety.', focus: 'Concurrencia estructurada y modelos inmutables.' }},
    {{ id: 'cpp-reviewer', name: 'cpp-reviewer (/cpp-review)', cmd: '/cpp-review', icon: '&#x2699;&#xfe0f;', cat: 'quality', kind: 'Agente + Comando', desc: 'Especialista en C++ moderno (RAII, smart pointers, move semantics).', focus: 'Seguridad de memoria, ciclo de vida de recursos y rendimiento.' }},
    {{ id: 'csharp-reviewer', name: 'csharp-reviewer', cmd: '@csharp-reviewer', icon: '&#x1f7e3;', cat: 'quality', kind: 'Agente ECC', desc: 'Especialista en C# / .NET, LINQ, async/await e inyeccion de dependencias.', focus: 'Buenas practicas .NET, disposicion de recursos y tipado fuerte.' }},
    {{ id: 'java-reviewer', name: 'java-reviewer', cmd: '@java-reviewer', icon: '&#x2615;', cat: 'quality', kind: 'Agente ECC', desc: 'Especialista en Java, concurrencia, streams y arquitectura empresarial.', focus: 'Inmutabilidad, manejo de excepciones y patrones limpios.' }},
    {{ id: 'php-reviewer', name: 'php-reviewer', cmd: '@php-reviewer', icon: '&#x1f418;', cat: 'quality', kind: 'Agente ECC', desc: 'Especialista en PHP moderno, tipado estricto y seguridad web.', focus: 'Validacion, PSR standards y prevencion de vulnerabilidades.' }},
    {{ id: 'ruby-reviewer', name: 'ruby-reviewer', cmd: '@ruby-reviewer', icon: '&#x1f48e;', cat: 'quality', kind: 'Agente ECC', desc: 'Especialista en Ruby / Rails, convenciones limpias y testing.', focus: 'Objetos pequenos, consultas eficientes y codigo expresivo.' }},
    {{ id: 'swift-reviewer', name: 'swift-reviewer', cmd: '@swift-reviewer', icon: '&#x1f985;', cat: 'quality', kind: 'Agente ECC', desc: 'Especialista en Swift, ARC, value types y concurrencia async/await.', focus: 'Evitar retain cycles y asegurar fluidez en UI.' }},
    {{ id: 'comment-analyzer', name: 'comment-analyzer', cmd: '@comment-analyzer', icon: '&#x1f4ac;', cat: 'quality', kind: 'Agente ECC', desc: 'Audita comentarios, JSDoc y docstrings para que coincidan con lo que hace el codigo real.', focus: 'Eliminar comentarios enganosos y documentar funciones publicas clave.' }},
    {{ id: 'commit-reviewer', name: 'commit-reviewer (/review-pr)', cmd: '/review-pr', icon: '&#x1f500;', cat: 'quality', kind: 'Agente + Comando', desc: 'Revisa diffs de commits y Pull Requests evaluando el impacto en todo el grafo.', focus: 'Detectar efectos colaterales antes de hacer merge.' }},
    {{ id: 'quality-gate', name: '/quality-gate', cmd: '/quality-gate', icon: '&#x1f3c1;', cat: 'quality', kind: 'Comando ECC', desc: 'Ejecuta la compuerta integral de calidad (lint, tipos, tests y contratos AST).', focus: 'Validacion de cero errores antes de entregar.' }},

    // --- Testing, TDD & Resolucion de Build ---
    {{ id: 'tdd', name: 'tdd-guide (/tdd)', cmd: '/tdd', icon: '&#x1f9ea;', cat: 'testing', kind: 'Agente + Comando', desc: 'Guia el flujo Test-Driven Development (Red -> Green -> Refactor) para este nodo.', focus: 'Escribir primero la prueba que valida el contrato del nodo y sus consumidores.' }},
    {{ id: 'pr-test-analyzer', name: 'pr-test-analyzer (/test-coverage)', cmd: '/test-coverage', icon: '&#x1f4ca;', cat: 'testing', kind: 'Agente + Comando', desc: 'Analiza huecos de cobertura de pruebas, casos borde faltantes y mocks fragiles.', focus: 'Descubrir que ramas o errores de este nodo aun no tienen test.' }},
    {{ id: 'e2e-runner', name: 'e2e-runner', cmd: '@e2e-runner', icon: '&#x1f3ad;', cat: 'testing', kind: 'Agente ECC', desc: 'Disena y ejecuta pruebas End-to-End (Playwright/ Vitest UI) sobre flujos reales.', focus: 'Probar el flujo completo del usuario que pasa por este nodo.' }},
    {{ id: 'build-error-resolver', name: 'build-error-resolver (/build-fix)', cmd: '/build-fix', icon: '&#x1f527;', cat: 'testing', kind: 'Agente + Comando', desc: 'Resuelve errores de compilacion, Vite/Webpack, imports rotos y conflictos de tipos.', focus: 'Reparar fallos de build analizando las importaciones entrantes y salientes del nodo.' }},
    {{ id: 'verify', name: '/verify (Verificacion Final)', cmd: '/verify', icon: '&#x2705;', cat: 'testing', kind: 'Comando ECC', desc: 'Comprueba en el grafo y en el runner de tests que el cambio no rompio ningun dependiente.', focus: 'Ejecutar pruebas afectadas y confirmar estado verde.' }},

    // --- Orquestacion, Features, Bugs & Documentacion ---
    {{ id: 'orch-add-feature', name: '/orch-add-feature', cmd: '/orch-add-feature', icon: '&#x2728;', cat: 'orch', kind: 'Orquestador ECC', desc: 'Flujo completo asistido para anadir una nueva funcionalidad conectada a este nodo.', focus: 'Diseno -> Tests -> Implementacion -> Revision -> Verificacion.' }},
    {{ id: 'orch-change-feature', name: '/orch-change-feature', cmd: '/orch-change-feature', icon: '&#x1f504;', cat: 'orch', kind: 'Orquestador ECC', desc: 'Flujo seguro para modificar el comportamiento de este nodo protegiendo a sus dependientes.', focus: 'Migracion gradual de contratos sin romper las vistas o servicios que lo usan.' }},
    {{ id: 'orch-fix-defect', name: '/orch-fix-defect', cmd: '/orch-fix-defect', icon: '&#x1f41b;', cat: 'orch', kind: 'Orquestador ECC', desc: 'Caza y corrige un bug en este nodo reproduciendolo primero con un test.', focus: 'Causa raiz en el AST + test de regresion + fix quirurgico.' }},
    {{ id: 'orch-refine-code', name: '/orch-refine-code', cmd: '/orch-refine-code', icon: '&#x1f48e;', cat: 'orch', kind: 'Orquestador ECC', desc: 'Refina calidad, legibilidad y rendimiento de este nodo manteniendo sus tests en verde.', focus: 'Mejora continua sin alterar la API publica del modulo.' }},
    {{ id: 'chief-of-staff', name: 'chief-of-staff', cmd: '@chief-of-staff', icon: '&#x1f396;&#xfe0f;', cat: 'orch', kind: 'Agente ECC', desc: 'Coordinador ejecutivo: divide tareas complejas sobre este nodo y asigna el agente ideal.', focus: 'Orquestar multiples especialistas cuando el cambio cruza varias fronteras.' }},
    {{ id: 'doc-updater', name: 'doc-updater (/update-docs)', cmd: '/update-docs', icon: '&#x1f4da;', cat: 'orch', kind: 'Agente + Comando', desc: 'Actualiza README, guias y documentacion tecnica para reflejar los cambios del nodo.', focus: 'Sincronizar documentacion con las funciones y rutas reales del codigo.' }},
    {{ id: 'docs-lookup', name: 'docs-lookup', cmd: '@docs-lookup', icon: '&#x1f50e;', cat: 'orch', kind: 'Agente ECC', desc: 'Consulta documentacion oficial de las librerias y frameworks que importa este nodo.', focus: 'Verificar APIs actualizadas de Vue, SQLite, Electron/Capacitor, etc.' }},
    {{ id: 'gan-generator', name: 'gan-generator (/gan-build)', cmd: '/gan-build', icon: '&#x1f916;', cat: 'orch', kind: 'Agente + Comando', desc: 'Generador adversario: construye implementaciones robustas listas para superar auditoria.', focus: 'Implementacion de alta exigencia validada contra casos extremos.' }},
    {{ id: 'loop-operator', name: 'loop-operator (/loop-start)', cmd: '/loop-start', icon: '&#x267e;&#xfe0f;', cat: 'orch', kind: 'Agente + Comando', desc: 'Ejecuta un bucle autonomo de mejora y verificacion sobre este modulo hasta cumplir la meta.', focus: 'Iteracion automatica test -> fix -> verify.' }},
    {{ id: 'harness-optimizer', name: 'harness-optimizer (/harness-audit)', cmd: '/harness-audit', icon: '&#x1f6e0;&#xfe0f;', cat: 'orch', kind: 'Agente + Comando', desc: 'Optimiza reglas, hooks y configuracion de agentes ECC para este repositorio.', focus: 'Ajustar guardarrailes y automatizaciones del entorno.' }},
    {{ id: 'rag-pipeline-reviewer', name: 'rag-pipeline-reviewer', cmd: '@rag-pipeline-reviewer', icon: '&#x1f9e0;', cat: 'orch', kind: 'Agente ECC', desc: 'Audita flujos de IA, grafos de conocimiento, prompts y recuperacion de contexto.', focus: 'Precision de contexto, latencia y relevancia semantica.' }},
  ];

  const ECC_TOOL_BY_ID = new Map(ECC_CATALOG.map(t => [t.id, t]));

  // Contextual Recommendation Engine: analyzes the clicked node and recommends the best ECC agents/tools with reasons
  function getRecommendedToolsForNode(pNode, stats) {{
    const recs = [];
    const seen = new Set();
    const addRec = (id, reason) => {{
      if (!seen.has(id) && ECC_TOOL_BY_ID.has(id)) {{
        seen.add(id);
        recs.push({{ tool: ECC_TOOL_BY_ID.get(id), reason }});
      }}
    }};

    const sf = String(pNode.sourceFile || '').toLowerCase();
    const lbl = String(pNode.label || '').toLowerCase();
    const comm = String(pNode.communityName || '').toLowerCase();
    const shortFile = (pNode.sourceFile ? pNode.sourceFile.split(/[\\\\/]/).pop() : pNode.label) || pNode.label;

    // 1. High Blast Radius (many modules depend on this node)
    if (stats.d1.length >= 3) {{
      addRec('gateguard', `Alto impacto: ${{stats.d1.length}} nodos dependen de el`);
      addRec('orch-change-feature', `Cambio seguro para proteger ${{stats.d1.length}} dependientes`);
    }}

    // 2. Vue / Frontend / UI Views & Components
    if (sf.endsWith('.vue') || lbl.endsWith('.vue') || sf.includes('/views/') || sf.includes('/components/') || comm.includes('vista') || comm.includes('ui')) {{
      addRec('vue-reviewer', `Componente/Vista Vue (${{shortFile}})`);
      addRec('a11y-architect', `Accesibilidad, teclado y UI en ${{shortFile}}`);
      addRec('multi-frontend', `Orquestar mejoras de interfaz y estado visual`);
      addRec('e2e-runner', `Probar flujo visual e interaccion de usuario`);
    }}

    // 3. React / JSX / TSX
    if (sf.endsWith('.jsx') || sf.endsWith('.tsx') || lbl.endsWith('.jsx') || lbl.endsWith('.tsx')) {{
      addRec('react-reviewer', `Componente React detectado (${{shortFile}})`);
      addRec('a11y-architect', `Auditar accesibilidad de interfaz`);
    }}

    // 4. Database / SQL / Queries / Backups / Migrations
    if (sf.includes('database') || sf.includes('/db/') || sf.includes('queries') || sf.includes('sql') || sf.includes('schema') || sf.includes('migration') || sf.includes('backup') || comm.includes('base de datos') || lbl.includes('query') || lbl.includes('db')) {{
      addRec('database-reviewer', `Toca Base de Datos / SQL (${{shortFile}})`);
      addRec('security-reviewer', `Prevenir SQL Injection y proteger datos`);
      addRec('silent-failure-hunter', `Evitar fallos silenciosos en transacciones BD`);
      addRec('performance-optimizer', `Optimizar consultas e indices SQL`);
    }}

    // 5. Services / Bots / Network / Sync / Auth / Composable Logic
    if (sf.includes('service') || sf.includes('telegram') || sf.includes('whatsapp') || sf.includes('bot') || sf.includes('sync') || sf.includes('api') || sf.includes('http') || comm.includes('servicio')) {{
      addRec('network-architect', `Servicio / Integracion externa (${{shortFile}})`);
      addRec('network-troubleshooter', `Auditar timeouts, reconexion y errores de red`);
      addRec('silent-failure-hunter', `Cazar promesas o llamadas API sin catch`);
      addRec('security-reviewer', `Proteger tokens, credenciales y payloads`);
    }}

    if (sf.includes('composable') || sf.includes('use') || sf.includes('store') || sf.includes('auth') || sf.includes('pin') || comm.includes('logica')) {{
      addRec('code-architect', `Logica compartida (${{stats.d1.length}} consumidores)`);
      addRec('silent-failure-hunter', `Verificar manejo de errores en logica reactiva`);
      if (sf.includes('auth') || sf.includes('pin') || sf.includes('login') || lbl.includes('auth') || lbl.includes('pin')) {{
        addRec('security-reviewer', `Modulo critico de autenticacion / acceso`);
      }}
    }}

    // 6. Language-specific specialists
    if (sf.endsWith('.py') || lbl.endsWith('.py')) {{
      addRec('python-reviewer', `Archivo Python (${{shortFile}})`);
      if (sf.includes('fastapi') || sf.includes('serve')) addRec('fastapi-reviewer', `Servicio API Python detectado`);
    }}
    if (sf.endsWith('.ts') || sf.endsWith('.js') || lbl.endsWith('.ts') || lbl.endsWith('.js')) {{
      addRec('typescript-reviewer', `Tipado, promesas y modulos JS/TS`);
    }}
    if (sf.endsWith('.go')) addRec('go-reviewer', `Modulo Go detectado`);
    if (sf.endsWith('.rs')) addRec('rust-reviewer', `Modulo Rust detectado`);

    // 7. Test Coverage Analysis
    if (pNode.isTest) {{
      addRec('tdd', `Archivo de pruebas (${{shortFile}})`);
      addRec('pr-test-analyzer', `Evaluar calidad de aserciones y casos borde`);
    }} else if (stats.tests.length === 0 && !sf.endsWith('.md') && !sf.endsWith('.json')) {{
      addRec('tdd', `Sin tests directos: crear prueba antes de editar`);
      addRec('pr-test-analyzer', `Detectar casos borde sin cobertura en ${{shortFile}}`);
    }} else if (stats.tests.length > 0) {{
      addRec('verify', `Tiene ${{stats.tests.length}} test(s) listos para verificar`);
      addRec('tdd', `Ampliar las ${{stats.tests.length}} suites de prueba conectadas`);
    }}

    // 8. High Internal Complexity (many symbols inside file)
    if (stats.fileSymbols.length >= 6) {{
      addRec('code-simplifier', `Contiene ${{stats.fileSymbols.length}} simbolos internos: simplificar`);
      addRec('refactor-cleaner', `Limpiar codigo muerto entre sus ${{stats.fileSymbols.length}} simbolos`);
    }}

    // 9. Documentation / Markdown / Rules
    if (sf.endsWith('.md') || comm.includes('documentacion') || sf.includes('readme') || sf.includes('docs/')) {{
      addRec('doc-updater', `Documento detectado: sincronizar con el codigo`);
      addRec('spec-miner', `Extraer requisitos verificables del documento`);
    }}

    // 10. Always ensure core workflow agents are available in recommendations
    addRec('plan', `Planificar cambios considerando sus ${{stats.d1.length + stats.outgoing.length}} conexiones`);
    addRec('review', `Auditar calidad y contratos con sus ${{stats.d1.length}} dependientes`);
    addRec('orch-fix-defect', `Corregir bugs en ${{shortFile}} sin causar regresiones`);
    addRec('gateguard', `Compuerta pre-edicion AST activa sobre este nodo`);

    return recs;
  }}

  // Build the dynamic ECC Tool Output for ANY selected agent or command in ECC_CATALOG
  function buildEccToolContent(pNode, stats, toolKey, recReason) {{
    const tool = ECC_TOOL_BY_ID.get(toolKey) || ECC_CATALOG[0];
    const targetFile = pNode.sourceFile || pNode.label;
    const shortFile = targetFile.split(/[\\\\/]/).pop() || pNode.label;
    const d1Names = stats.d1.slice(0, 5).map(x => `${{x.label}}${{x.file ? ' (' + x.file.split(/[\\\\/]/).pop() + ')' : ''}}`).join(', ') || 'ninguno directo';
    const outNames = stats.outgoing.slice(0, 5).map(x => `${{x.label}}${{x.file ? ' (' + x.file.split(/[\\\\/]/).pop() + ')' : ''}}`).join(', ') || 'ninguno saliente';
    const symNames = stats.fileSymbols.slice(0, 6).map(x => x.label).join(', ') || 'ninguno adicional';
    const testFiles = Array.from(new Set(stats.tests.map(t => t.file))).slice(0, 4);
    const testStr = testFiles.length ? testFiles.join(' ') : `tests/${{shortFile.replace(/\\.(vue|js|ts|py)$/, '.spec.js')}}`;

    const reasonBanner = recReason
      ? `<div style="margin-bottom:5px;padding:3px 6px;background:rgba(245,158,11,0.16);border:1px solid rgba(245,158,11,0.4);border-radius:4px;color:#fde68a;font-size:10px">&#x2b50; <b>Por que se recomienda aqui:</b> ${{esc(recReason)}}</div>`
      : '';

    const quickCmd = tool.id === 'gateguard'
      ? `.\\\\iniciar-planeta-ecc.ps1 -AuditarArchivo "${{targetFile}}"`
      : (tool.id === 'verify'
          ? (testFiles.length ? `npx vitest run ${{testFiles.join(' ')}}` : `graphify affected "${{targetFile}}"`)
          : `${{tool.cmd}} ${{targetFile}}`);

    const fullPrompt = `${{tool.cmd}} Actua sobre el nodo "${{pNode.label}}" en el archivo "${{targetFile}}" (Capa: ${{pNode.communityName}}).
Contexto real del Grafo AST (Graphify):
- Impacto Directo (${{stats.d1.length}} dependientes que lo usan): ${{d1Names}}
- Dependencias que toca/importa (${{stats.outgoing.length}}): ${{outNames}}
- Simbolos internos del archivo (${{stats.fileSymbols.length}}): ${{symNames}}
- Tests asociados (${{testFiles.length}}): ${{testStr}}
Objetivo con ${{tool.name}}: ${{tool.focus}}`;

    return {{
      title: `${{tool.icon}} ${{esc(tool.name)}} <span style="font-size:9.5px;font-weight:500;color:#94a3b8;padding:1px 5px;border:1px solid rgba(148,163,184,0.3);border-radius:4px">${{esc(tool.kind)}}</span>`,
      html: `
        ${{reasonBanner}}
        <div style="color:#e2e8f0;margin-bottom:4px">${{esc(tool.desc)}}</div>
        <div style="background:rgba(2,6,23,0.50);padding:6px;border-radius:5px;color:#cbd5e1;font-size:10.5px">
          &bull; <b>Enfoque en <code>${{esc(shortFile)}}</code>:</b> ${{esc(tool.focus)}}<br>
          &bull; <b>Proteger dependientes (${{stats.d1.length}}):</b> <code>${{esc(d1Names)}}</code><br>
          &bull; <b>Revisar conexiones (${{stats.outgoing.length}}):</b> <code>${{esc(outNames)}}</code><br>
          &bull; <b>Pruebas (${{testFiles.length}}):</b> <code>${{esc(testStr)}}</code>
        </div>
      `,
      copyText: fullPrompt,
      copyLabel: `&#x1f4cb; Copiar Prompt de ${{esc(tool.cmd)}} con Contexto del Nodo`,
      quickCmd,
      quickLabel: `&#x26a1; Copiar Comando Corto`,
    }};
  }}

  function renderNodeWorkstation() {{
    const blastBox = document.getElementById('planet-blast-box');
    if (!blastBox || !selectedNodeId || !nodeById.has(selectedNodeId)) return;
    const pNode = nodeById.get(selectedNodeId);
    const stats = lastStats || computeBlastRadius(selectedNodeId);

    // Choose list for active touch tab
    let activeList = [];
    let emptyMsg = '';
    let badgeIcon = '&#x1f534;';
    if (activeTouchTab === 'in') {{
      activeList = stats.d1;
      emptyMsg = 'Ningun modulo importa o llama directamente a este nodo (es una vista o punto de entrada).';
      badgeIcon = '&#x1f534;';
    }} else if (activeTouchTab === 'out') {{
      activeList = stats.outgoing;
      emptyMsg = 'Este nodo no llama ni importa a otros modulos del grafo.';
      badgeIcon = '&#x1f535;';
    }} else if (activeTouchTab === 'tests') {{
      activeList = stats.tests;
      emptyMsg = 'No hay archivo .spec/.test conectado directamente a este nodo. Usa tdd-guide abajo para crearlo.';
      badgeIcon = '&#x1f9ea;';
    }} else if (activeTouchTab === 'symbols') {{
      activeList = stats.fileSymbols;
      emptyMsg = 'No hay otros simbolos internos registrados en este archivo.';
      badgeIcon = '&#x2699;&#xfe0f;';
    }}

    const listHtml = activeList.length
      ? activeList.slice(0, 12).map(item => {{
          const shortF = item.file ? item.file.split(/[\\\\/]/).pop() : '';
          return `<div class="dep-item" data-jump-id="${{esc(item.id)}}"><span>${{badgeIcon}} <b>${{esc(item.label)}}</b> <span style="color:#94a3b8">${{esc(shortF ? '(' + shortF + ')' : '')}}</span></span><span style="color:#7dd3fc;font-size:10px">[${{esc(item.relation)}}]</span></div>`;
        }}).join('')
      : `<div style="padding:6px;color:#94a3b8;font-size:11px">${{emptyMsg}}</div>`;

    // Compute contextual recommendations for this node
    const recs = getRecommendedToolsForNode(pNode, stats);
    const recReasonMap = new Map(recs.map(r => [r.tool.id, r.reason]));

    // Filter tools based on activeEccCategory & eccSearchQuery
    const q = eccSearchQuery.trim().toLowerCase();
    let visibleTools = [];
    if (q) {{
      visibleTools = ECC_CATALOG.filter(t =>
        t.name.toLowerCase().includes(q) ||
        t.cmd.toLowerCase().includes(q) ||
        t.desc.toLowerCase().includes(q) ||
        t.focus.toLowerCase().includes(q) ||
        t.id.toLowerCase().includes(q)
      );
    }} else if (activeEccCategory === 'rec') {{
      visibleTools = recs.map(r => r.tool);
    }} else if (activeEccCategory === 'all') {{
      visibleTools = ECC_CATALOG;
    }} else {{
      visibleTools = ECC_CATALOG.filter(t => t.cat === activeEccCategory);
    }}

    if (!ECC_TOOL_BY_ID.has(activeEccTool) && visibleTools.length) {{
      activeEccTool = visibleTools[0].id;
    }}

    const toolsGridHtml = visibleTools.length
      ? visibleTools.map(t => {{
          const isAct = t.id === activeEccTool ? 'active' : '';
          const reason = recReasonMap.get(t.id);
          const isRecClass = reason ? 'is-rec' : '';
          const badgeHtml = reason
            ? `<span class="ecc-rec-badge" title="${{esc(reason)}}">&#x2b50; ${{esc(reason)}}</span>`
            : `<span class="ecc-tool-sub">${{esc(t.desc)}}</span>`;
          return `
            <button type="button" class="ecc-tool-btn ${{isAct}} ${{isRecClass}}" data-ecc-tool="${{esc(t.id)}}">
              <div style="display:flex;justify-content:space-between;align-items:center;gap:4px">
                <span>${{t.icon}} ${{esc(t.name)}}</span>
              </div>
              ${{badgeHtml}}
            </button>
          `;
        }}).join('')
      : `<div style="grid-column:1/-1;padding:6px;color:#94a3b8;font-size:11px">No se encontraron agentes para "${{esc(eccSearchQuery)}}".</div>`;

    const eccTool = buildEccToolContent(pNode, stats, activeEccTool, recReasonMap.get(activeEccTool));

    blastBox.innerHTML = `
      <div style="margin-bottom:6px;border-bottom:1px solid rgba(255,255,255,0.08);padding-bottom:5px">
        <div style="font-size:13px;font-weight:700;color:#f8fafc">&#x1f4c4; ${{esc(pNode.label)}}</div>
        <div style="font-size:10.5px;color:#7dd3fc">${{esc(pNode.sourceFile || 'Nodo global')}} &middot; ${{esc(pNode.communityName)}}</div>
      </div>

      <div style="font-size:10.5px;font-weight:700;color:#cbd5e1">A. TODO LO QUE TOCA ESTE NODO (Clic para saltar):</div>
      <div class="touch-tabs">
        <button type="button" class="touch-tab ${{activeTouchTab === 'in' ? 'active' : ''}}" data-touch-tab="in">&#x1f4e5; Impacto Directo (${{stats.d1.length}})</button>
        <button type="button" class="touch-tab ${{activeTouchTab === 'out' ? 'active' : ''}}" data-touch-tab="out">&#x1f4e4; Toca/Usa (${{stats.outgoing.length}})</button>
        <button type="button" class="touch-tab ${{activeTouchTab === 'tests' ? 'active' : ''}}" data-touch-tab="tests">&#x1f9ea; Tests (${{stats.tests.length}})</button>
        <button type="button" class="touch-tab ${{activeTouchTab === 'symbols' ? 'active' : ''}}" data-touch-tab="symbols">&#x2699;&#xfe0f; Internos (${{stats.fileSymbols.length}})</button>
      </div>
      <div class="dep-list">${{listHtml}}</div>

      <div style="font-size:10.5px;font-weight:700;color:#cbd5e1;margin-top:9px">
        B. AGENTES Y HERRAMIENTAS ECC (Recomendados seg&uacute;n este nodo + Cat&aacute;logo Completo):
      </div>
      <div class="ecc-cat-bar">
        <button type="button" class="ecc-cat-pill ${{activeEccCategory === 'rec' && !q ? 'active' : ''}}" data-ecc-cat="rec">&#x2b50; Recomendados (${{recs.length}})</button>
        <button type="button" class="ecc-cat-pill ${{activeEccCategory === 'arch' && !q ? 'active' : ''}}" data-ecc-cat="arch">&#x1f9e0; Arquitectura</button>
        <button type="button" class="ecc-cat-pill ${{activeEccCategory === 'frontend' && !q ? 'active' : ''}}" data-ecc-cat="frontend">&#x1f3a8; UI/Vue/Web</button>
        <button type="button" class="ecc-cat-pill ${{activeEccCategory === 'backend' && !q ? 'active' : ''}}" data-ecc-cat="backend">&#x1f5c4;&#xfe0f; BD/Seguridad/Red</button>
        <button type="button" class="ecc-cat-pill ${{activeEccCategory === 'quality' && !q ? 'active' : ''}}" data-ecc-cat="quality">&#x1f50d; Revisi&oacute;n/Refactor</button>
        <button type="button" class="ecc-cat-pill ${{activeEccCategory === 'testing' && !q ? 'active' : ''}}" data-ecc-cat="testing">&#x1f9ea; Tests/Build</button>
        <button type="button" class="ecc-cat-pill ${{activeEccCategory === 'orch' && !q ? 'active' : ''}}" data-ecc-cat="orch">&#x1f680; Orquestaci&oacute;n</button>
        <button type="button" class="ecc-cat-pill ${{activeEccCategory === 'all' && !q ? 'active' : ''}}" data-ecc-cat="all">&#x1f4cb; Todos (${{ECC_CATALOG.length}})</button>
      </div>
      <input type="text" id="ecc-agent-search" class="ecc-search-input" placeholder="&#x1f50e; Buscar cualquier agente o comando ECC (ej: vue, database, security, refactor, e2e, gan...)" value="${{esc(eccSearchQuery)}}">
      <div class="ecc-tools-bar">${{toolsGridHtml}}</div>

      <div class="ecc-gate-box">
        <div style="font-weight:700;color:#a5b4fc;margin-bottom:4px;display:flex;justify-content:space-between;align-items:center;gap:6px">${{eccTool.title}}</div>
        ${{eccTool.html}}
        <div class="ecc-copy-row">
          <button type="button" class="ecc-copy-btn" id="btn-ecc-copy">${{eccTool.copyLabel}}</button>
          <button type="button" class="ecc-copy-btn secondary" id="btn-ecc-copy-quick" title="${{esc(eccTool.quickCmd)}}">${{eccTool.quickLabel}}</button>
        </div>
      </div>
    `;

    if (blastBox.querySelectorAll) {{
      blastBox.querySelectorAll('.dep-item').forEach(row => {{
        row.addEventListener('click', () => {{
          const jid = row.getAttribute('data-jump-id');
          if (jid) flyToPlanetNode(jid, 'ECC:Trace');
        }});
      }});
      blastBox.querySelectorAll('.touch-tab').forEach(tab => {{
        tab.addEventListener('click', () => {{
          activeTouchTab = tab.getAttribute('data-touch-tab') || 'in';
          renderNodeWorkstation();
        }});
      }});
      blastBox.querySelectorAll('.ecc-cat-pill').forEach(pill => {{
        pill.addEventListener('click', () => {{
          activeEccCategory = pill.getAttribute('data-ecc-cat') || 'rec';
          eccSearchQuery = '';
          renderNodeWorkstation();
        }});
      }});
      blastBox.querySelectorAll('.ecc-tool-btn').forEach(btn => {{
        btn.addEventListener('click', () => {{
          activeEccTool = btn.getAttribute('data-ecc-tool') || 'gateguard';
          renderNodeWorkstation();
          logTelemetry('ECC:' + activeEccTool.toUpperCase(), `Agente seleccionado para ${{pNode.label}}`);
        }});
      }});
    }}

    const searchInput = document.getElementById('ecc-agent-search');
    if (searchInput && searchInput.addEventListener) {{
      searchInput.addEventListener('input', e => {{
        eccSearchQuery = e.target.value || '';
        renderNodeWorkstation();
        const newSearch = document.getElementById('ecc-agent-search');
        if (newSearch && newSearch.focus) {{
          newSearch.focus();
          try {{ newSearch.setSelectionRange(eccSearchQuery.length, eccSearchQuery.length); }} catch (_) {{}}
        }}
      }});
    }}

    const copyBtn = document.getElementById('btn-ecc-copy');
    if (copyBtn && copyBtn.addEventListener) {{
      copyBtn.addEventListener('click', () => {{
        if (navigator.clipboard && navigator.clipboard.writeText) {{
          navigator.clipboard.writeText(eccTool.copyText);
        }}
        copyBtn.textContent = 'Prompt copiado al portapapeles!';
        logTelemetry('ECC:PROMPT', `Copiado prompt ${{activeEccTool}} para ${{pNode.label}}`);
        setTimeout(() => {{ copyBtn.innerHTML = eccTool.copyLabel; }}, 1800);
      }});
    }}

    const quickCopyBtn = document.getElementById('btn-ecc-copy-quick');
    if (quickCopyBtn && quickCopyBtn.addEventListener) {{
      quickCopyBtn.addEventListener('click', () => {{
        if (navigator.clipboard && navigator.clipboard.writeText) {{
          navigator.clipboard.writeText(eccTool.quickCmd);
        }}
        quickCopyBtn.textContent = 'Copiado!';
        logTelemetry('ECC:CMD', `Copiado: ${{eccTool.quickCmd}}`);
        setTimeout(() => {{ quickCopyBtn.innerHTML = eccTool.quickLabel; }}, 1800);
      }});
    }}
  }}

  function flyToPlanetNode(nodeId, actorLabel) {{
    const pNode = nodeById.get(nodeId);
    if (!pNode) return;
    selectedNodeId = nodeId;
    targetRotY = -Math.atan2(pNode.ux, pNode.uz);
    const clampedY = Math.max(-0.98, Math.min(0.98, pNode.uy));
    targetRotX = Math.asin(clampedY);

    lastStats = computeBlastRadius(nodeId);
    // Automatically pick the #1 recommended ECC agent for this node when switching nodes
    const recs = getRecommendedToolsForNode(pNode, lastStats);
    if (recs.length > 0) {{
      activeEccTool = recs[0].tool.id;
    }}
    syncLodVisibility();
    renderTopHubsBar();
    renderNodeWorkstation();
    triggerShockwave(nodeId, '#38bdf8');

    // Also focus in 2D map if user is in 2D mode
    if (!isPlanetActive && typeof network !== 'undefined' && network.selectNodes) {{
      try {{
        network.selectNodes([nodeId]);
        if (network.focus) network.focus(nodeId, {{ scale: 1.0, animation: true }});
      }} catch (_) {{}}
    }}

    if (actorLabel) {{
      logTelemetry(actorLabel, `${{pNode.label}} -> Lo usan: ${{lastStats.d1.length}}, Toca: ${{lastStats.outgoing.length}}, Tests: ${{lastStats.tests.length}}`);
    }}
    if (typeof showInfo === 'function') showInfo(nodeId);
  }}

  renderTopHubsBar();

  function project3D(x, y, z, cx, cy, planetRadius) {{
    const cosY = Math.cos(rotY), sinY = Math.sin(rotY);
    const x1 = x * cosY + z * sinY;
    const z1 = -x * sinY + z * cosY;
    const cosX = Math.cos(rotX), sinX = Math.sin(rotX);
    const y2 = y * cosX - z1 * sinX;
    const z2 = y * sinX + z1 * cosX;
    const perspective = 2.8 / Math.max(0.9, 2.8 - z2 * 0.65);
    return {{
      sx: cx + x1 * planetRadius * perspective,
      sy: cy - y2 * planetRadius * perspective,
      sz: z2,
      scale: perspective,
    }};
  }}

  function resizeCanvas() {{
    const dpr = window.devicePixelRatio || 1;
    const w = planetStage.clientWidth || graphEl.clientWidth || 960;
    const h = planetStage.clientHeight || graphEl.clientHeight || 720;
    if (canvas.width !== Math.floor(w * dpr) || canvas.height !== Math.floor(h * dpr)) {{
      canvas.width = Math.floor(w * dpr);
      canvas.height = Math.floor(h * dpr);
    }}
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    return {{ w, h }};
  }}

  let lastFrameTime = performance.now();
  let frameCounter = 0;

  function renderPlanet(now) {{
    requestAnimationFrame(renderPlanet);
    if (!isPlanetActive) return;

    frameCounter++;
    if (now - lastFrameTime >= 500) {{
      const fps = Math.min(60, Math.round((frameCounter * 1000) / (now - lastFrameTime)));
      const fpsEl = document.getElementById('planet-fps');
      if (fpsEl) fpsEl.textContent = fps + ' FPS';
      frameCounter = 0;
      lastFrameTime = now;
    }}

    const {{ w, h }} = resizeCanvas();
    const cx = w * 0.58;
    const cy = h * 0.50;
    const planetRadius = Math.min(w * 0.76, h) * 0.34 * zoom;

    if (targetRotY !== null && targetRotX !== null) {{
      let diffY = targetRotY - rotY;
      while (diffY > Math.PI) diffY -= Math.PI * 2;
      while (diffY < -Math.PI) diffY += Math.PI * 2;
      const diffX = targetRotX - rotX;
      rotY += diffY * 0.12;
      rotX += diffX * 0.12;
      if (Math.abs(diffY) < 0.004 && Math.abs(diffX) < 0.004) {{
        targetRotY = null;
        targetRotX = null;
      }}
    }} else if (!isDragging) {{
      if (autoSpin) {{
        rotY += velY;
      }} else {{
        rotY += velY;
        rotX = Math.max(-1.48, Math.min(1.48, rotX + velX));
        velY *= 0.92;
        velX *= 0.92;
      }}
    }}

    ctx.clearRect(0, 0, w, h);

    // 1. Atmospheric Outer Halo & Planetary Core Sphere
    const atmoGrad = ctx.createRadialGradient(cx, cy, planetRadius * 0.75, cx, cy, planetRadius * 1.32);
    atmoGrad.addColorStop(0, 'rgba(30, 64, 175, 0.20)');
    atmoGrad.addColorStop(0.55, 'rgba(56, 189, 248, 0.09)');
    atmoGrad.addColorStop(1, 'rgba(2, 6, 23, 0)');
    ctx.fillStyle = atmoGrad;
    ctx.beginPath();
    ctx.arc(cx, cy, planetRadius * 1.32, 0, Math.PI * 2);
    ctx.fill();

    const globeGrad = ctx.createRadialGradient(
      cx - planetRadius * 0.3, cy - planetRadius * 0.3, planetRadius * 0.08,
      cx, cy, planetRadius
    );
    globeGrad.addColorStop(0, '#132042');
    globeGrad.addColorStop(0.65, '#091126');
    globeGrad.addColorStop(1, '#040814');
    ctx.fillStyle = globeGrad;
    ctx.beginPath();
    ctx.arc(cx, cy, planetRadius, 0, Math.PI * 2);
    ctx.fill();

    ctx.strokeStyle = 'rgba(125, 211, 252, 0.25)';
    ctx.lineWidth = 1.2;
    ctx.stroke();

    // 2. Clean Spherical Graticule
    ctx.lineWidth = 0.6;
    ctx.strokeStyle = 'rgba(148, 163, 184, 0.09)';
    for (let latDeg = -60; latDeg <= 60; latDeg += 30) {{
      const latR = (latDeg * Math.PI) / 180;
      ctx.beginPath();
      let started = false;
      for (let lonDeg = -180; lonDeg <= 180; lonDeg += 12) {{
        const lonR = (lonDeg * Math.PI) / 180;
        const p = project3D(
          Math.cos(latR) * Math.sin(lonR),
          Math.sin(latR),
          Math.cos(latR) * Math.cos(lonR),
          cx, cy, planetRadius
        );
        if (p.sz >= -0.05) {{
          if (!started) {{ ctx.moveTo(p.sx, p.sy); started = true; }}
          else ctx.lineTo(p.sx, p.sy);
        }} else {{
          started = false;
        }}
      }}
      ctx.stroke();
    }}

    // 3. Project All Visible Nodes
    planetNodes.forEach(pNode => {{
      if (!pNode.visible) return;
      let ux = pNode.ux, uy = pNode.uy, uz = pNode.uz;
      if (pNode.orbitSpeed > 0) {{
        pNode.orbitPhase = (pNode.orbitPhase + pNode.orbitSpeed) % (Math.PI * 2);
        const wobble = 0.015;
        ux += Math.cos(pNode.orbitPhase) * wobble;
        uy += Math.sin(pNode.orbitPhase) * wobble;
      }}
      const proj = project3D(ux * pNode.altitude, uy * pNode.altitude, uz * pNode.altitude, cx, cy, planetRadius);
      pNode.sx = proj.sx;
      pNode.sy = proj.sy;
      pNode.sz = proj.sz;
      pNode.scale = proj.scale;
    }});

    // 4. Render 3D Geodesic Arcs
    planetEdges.forEach(edge => {{
      if (!edge.src.visible || !edge.tgt.visible) return;
      const isBlastEdge = blastEdgesSet.has(edge.id);
      const isHoveredEdge = hoveredPlanetNodeId && (edge.src.id === hoveredPlanetNodeId || edge.tgt.id === hoveredPlanetNodeId);

      if (focusEdgesOnly) {{
        if (selectedNodeId) {{
          if (!isBlastEdge) return;
        }} else if (hoveredPlanetNodeId) {{
          if (!isHoveredEdge) return;
        }} else {{
          if (!(edge.src.isHub && edge.tgt.isHub && edge.confidence === 'EXTRACTED')) return;
        }}
      }}

      if (edge.src.sz < -0.35 && edge.tgt.sz < -0.35 && !isBlastEdge) return;

      const midProj = project3D(edge.mx, edge.my, edge.mz, cx, cy, planetRadius);
      ctx.save();
      ctx.beginPath();
      ctx.moveTo(edge.src.sx, edge.src.sy);
      ctx.quadraticCurveTo(midProj.sx, midProj.sy, edge.tgt.sx, edge.tgt.sy);

      const isIncoming = edge.tgt.id === selectedNodeId || (selectedNodeId && nodeById.get(selectedNodeId) && edge.tgt.sourceFile === nodeById.get(selectedNodeId).sourceFile);
      if (isBlastEdge || isHoveredEdge) {{
        ctx.strokeStyle = isIncoming ? 'rgba(248, 113, 113, 0.92)' : 'rgba(56, 189, 248, 0.90)';
        ctx.lineWidth = 2.2;
      }} else {{
        ctx.strokeStyle = 'rgba(148, 163, 184, 0.22)';
        ctx.lineWidth = 1.0;
      }}
      ctx.stroke();

      edge.photonOffset = (edge.photonOffset + edge.photonSpeed) % 1.0;
      const t = edge.photonOffset;
      const invT = 1 - t;
      const px = invT * invT * edge.src.sx + 2 * invT * t * midProj.sx + t * t * edge.tgt.sx;
      const py = invT * invT * edge.src.sy + 2 * invT * t * midProj.sy + t * t * edge.tgt.sy;
      ctx.beginPath();
      ctx.arc(px, py, isBlastEdge ? 3.2 : 2.0, 0, Math.PI * 2);
      ctx.fillStyle = isIncoming ? '#fca5a5' : '#38bdf8';
      ctx.fill();
      ctx.restore();
    }});

    // 5. Render Nodes Sorted Back-to-Front
    const renderOrder = planetNodes.filter(n => n.visible).sort((a, b) => a.sz - b.sz);
    renderOrder.forEach(pNode => {{
      const isFront = pNode.sz >= 0;
      const depthAlpha = isFront ? (0.65 + 0.35 * pNode.sz) : Math.max(0.08, 0.25 + pNode.sz * 0.20);
      const blastDepth = blastRadiusMap.get(pNode.id);
      const isSelected = pNode.id === selectedNodeId;
      const isHovered = pNode.id === hoveredPlanetNodeId;
      const dimFactor = (selectedNodeId && blastDepth === undefined && !isHovered) ? 0.28 : 1.0;
      const finalAlpha = Math.max(0.05, Math.min(1.0, depthAlpha * dimFactor));

      const r = Math.max(3.0, pNode.baseSize * pNode.scale * (isSelected ? 1.55 : (blastDepth === 1 ? 1.28 : 1.0)));

      ctx.save();
      ctx.globalAlpha = finalAlpha;

      if (isSelected || blastDepth === 1 || pNode.isHub) {{
        ctx.beginPath();
        ctx.arc(pNode.sx, pNode.sy, r * 1.9, 0, Math.PI * 2);
        ctx.fillStyle = isSelected
          ? 'rgba(56, 189, 248, 0.38)'
          : (blastDepth === 1 ? 'rgba(239, 68, 68, 0.28)' : 'rgba(125, 211, 252, 0.14)');
        ctx.fill();
      }}

      ctx.beginPath();
      ctx.arc(pNode.sx, pNode.sy, r, 0, Math.PI * 2);
      ctx.fillStyle = isSelected ? '#ffffff' : pNode.color;
      ctx.fill();

      if (isSelected || blastDepth === 1) {{
        ctx.lineWidth = 2.2;
        ctx.strokeStyle = isSelected ? '#38bdf8' : '#ef4444';
        ctx.stroke();
      }}
      ctx.restore();

      const shouldShowLabel = isSelected || isHovered || (isFront && blastDepth === 1) || (isFront && !selectedNodeId && pNode.isHub && pNode.sz > 0.35);
      if (shouldShowLabel) {{
        ctx.save();
        ctx.font = (isSelected || isHovered) ? 'bold 12px -apple-system, Segoe UI, sans-serif' : '600 10.5px -apple-system, Segoe UI, sans-serif';
        const shortLbl = pNode.label.length > 28 ? pNode.label.slice(0, 26) + '..' : pNode.label;
        const tw = ctx.measureText(shortLbl).width;
        const lx = pNode.sx - tw * 0.5;
        const ly = pNode.sy - r - 6;
        ctx.fillStyle = 'rgba(15, 23, 42, 0.85)';
        ctx.fillRect(lx - 4, ly - 11, tw + 8, 15);
        ctx.fillStyle = isSelected ? '#7dd3fc' : (blastDepth === 1 ? '#fca5a5' : '#f8fafc');
        ctx.fillText(shortLbl, lx, ly);
        ctx.restore();
      }}
    }});

    // 6. Render Expanding Blast-Radius Shockwaves
    for (let i = shockwaves.length - 1; i >= 0; i--) {{
      const sw = shockwaves[i];
      const centerNode = nodeById.get(sw.nodeId);
      if (!centerNode) {{ shockwaves.splice(i, 1); continue; }}
      sw.radius += 1.8;
      sw.alpha *= 0.94;
      if (sw.alpha <= 0.03 || sw.radius >= sw.maxRadius) {{
        shockwaves.splice(i, 1);
        continue;
      }}
      ctx.save();
      ctx.beginPath();
      ctx.arc(centerNode.sx, centerNode.sy, sw.radius * centerNode.scale, 0, Math.PI * 2);
      ctx.strokeStyle = sw.color;
      ctx.globalAlpha = sw.alpha;
      ctx.lineWidth = 2.2;
      ctx.stroke();
      ctx.restore();
    }}
  }}

  function findNodeAtScreen(mx, my) {{
    let best = null;
    let bestDist = 18;
    for (let i = 0; i < planetNodes.length; i++) {{
      const n = planetNodes[i];
      if (!n.visible || n.sz < -0.15) continue;
      const d = Math.hypot(mx - n.sx, my - n.sy);
      if (d < bestDist) {{
        bestDist = d;
        best = n;
      }}
    }}
    return best;
  }}

  canvas.addEventListener('mousedown', ev => {{
    isDragging = true;
    targetRotY = null;
    targetRotX = null;
    dragStartX = ev.clientX;
    dragStartY = ev.clientY;
  }});

  window.addEventListener('mousemove', ev => {{
    if (!isPlanetActive) return;
    const rect = canvas.getBoundingClientRect();
    const mx = ev.clientX - rect.left;
    const my = ev.clientY - rect.top;
    if (isDragging) {{
      const dx = ev.clientX - dragStartX;
      const dy = ev.clientY - dragStartY;
      dragStartX = ev.clientX;
      dragStartY = ev.clientY;
      velY = dx * 0.0065;
      velX = dy * 0.0065;
      rotY += velY;
      rotX = Math.max(-1.48, Math.min(1.48, rotX + velX));
    }} else if (mx >= 0 && my >= 0 && mx <= rect.width && my <= rect.height) {{
      const hit = findNodeAtScreen(mx, my);
      hoveredPlanetNodeId = hit ? hit.id : null;
      canvas.style.cursor = hit ? 'pointer' : 'grab';
    }}
  }});

  window.addEventListener('mouseup', ev => {{
    if (!isDragging) return;
    isDragging = false;
    const rect = canvas.getBoundingClientRect();
    const mx = ev.clientX - rect.left;
    const my = ev.clientY - rect.top;
    if (Math.hypot(velY, velX) < 0.008 && mx >= 0 && my >= 0 && mx <= rect.width && my <= rect.height) {{
      const hit = findNodeAtScreen(mx, my);
      if (hit) {{
        flyToPlanetNode(hit.id, 'NODO-3D');
      }}
    }}
  }});

  canvas.addEventListener('wheel', ev => {{
    ev.preventDefault();
    const factor = ev.deltaY < 0 ? 1.10 : 0.91;
    zoom = Math.max(0.55, Math.min(2.6, zoom * factor));
  }}, {{ passive: false }});

  // Connect 2D Network click and right-sidebar Search/Neighbor clicks to the ECC Workstation!
  if (typeof network !== 'undefined' && network.on) {{
    network.on('click', params => {{
      if (params && params.nodes && params.nodes.length > 0) {{
        flyToPlanetNode(params.nodes[0], 'NODO-2D');
      }}
    }});
  }}

  const btn2D = document.getElementById('btn-mode-2d');
  const btnPlanet = document.getElementById('btn-mode-planet');
  const btnHudMin = document.getElementById('btn-hud-min');

  if (btnHudMin) {{
    btnHudMin.addEventListener('click', () => {{
      hudEl.classList.toggle('minimized');
      btnHudMin.textContent = hudEl.classList.contains('minimized') ? '+' : '_';
    }});
  }}

  function setPlanetMode(enablePlanet) {{
    isPlanetActive = Boolean(enablePlanet);
    if (isPlanetActive) {{
      planetStage.classList.add('active');
      graphEl.style.display = 'none';
      btnPlanet.classList.add('active');
      btn2D.classList.remove('active');
    }} else {{
      planetStage.classList.remove('active');
      graphEl.style.display = '';
      btn2D.classList.add('active');
      btnPlanet.classList.remove('active');
      if (typeof network !== 'undefined' && network.redraw) {{
        network.redraw();
      }}
    }}
    syncLodVisibility();
  }}

  btn2D.addEventListener('click', () => setPlanetMode(false));
  btnPlanet.addEventListener('click', () => setPlanetMode(true));

  const btnLodFiles = document.getElementById('btn-lod-files');
  const btnLodTests = document.getElementById('btn-lod-tests');
  const btnLodAll = document.getElementById('btn-lod-all');
  function setLod(mode) {{
    lodMode = mode;
    [btnLodFiles, btnLodTests, btnLodAll].forEach(b => b && b.classList.remove('active'));
    if (mode === 'files' && btnLodFiles) btnLodFiles.classList.add('active');
    if (mode === 'tests' && btnLodTests) btnLodTests.classList.add('active');
    if (mode === 'all' && btnLodAll) btnLodAll.classList.add('active');
    syncLodVisibility();
    logTelemetry('VISTA', `Nivel de claridad cambiado a: ${{mode.toUpperCase()}}`);
  }}
  if (btnLodFiles) btnLodFiles.addEventListener('click', () => setLod('files'));
  if (btnLodTests) btnLodTests.addEventListener('click', () => setLod('tests'));
  if (btnLodAll) btnLodAll.addEventListener('click', () => setLod('all'));

  const btnSpin = document.getElementById('btn-planet-spin');
  const btnEdgesFocus = document.getElementById('btn-planet-edges-focus');
  const btnReset = document.getElementById('btn-planet-reset');
  if (btnSpin) {{
    btnSpin.addEventListener('click', () => {{
      autoSpin = !autoSpin;
      btnSpin.classList.toggle('active', autoSpin);
    }});
  }}
  if (btnEdgesFocus) {{
    btnEdgesFocus.addEventListener('click', () => {{
      focusEdgesOnly = !focusEdgesOnly;
      btnEdgesFocus.classList.toggle('active', focusEdgesOnly);
      btnEdgesFocus.innerHTML = focusEdgesOnly ? '&#x1f3af; Lineas: Solo Nodo Activo' : '&#x1f310; Lineas: Todas';
      syncLodVisibility();
    }});
  }}
  if (btnReset) {{
    btnReset.addEventListener('click', () => {{
      selectedNodeId = null;
      blastRadiusMap.clear();
      blastEdgesSet.clear();
      zoom = 1.0;
      syncLodVisibility();
      renderTopHubsBar();
      logTelemetry('VISTA', 'Mostrando vista general de nodos principales.');
    }});
  }}

  if (typeof window.EventSource !== 'undefined' && /^https?:$/i.test(window.location.protocol)) {{
    try {{
      const es = new EventSource('/events');
      es.addEventListener('graphify_event', ev => {{
        try {{
          const payload = JSON.parse(ev.data);
          const actor = payload.actor || payload.kind || 'ECC-LIVE';
          const target = payload.node_id || payload.file_path || payload.question || '';
          logTelemetry(actor, target ? `Agente consulto ${{target}}` : 'Pulso MCP recibido');
          if (payload.node_id && nodeById.has(payload.node_id)) {{
            flyToPlanetNode(payload.node_id, actor);
          }} else if (payload.file_path) {{
            const match = planetNodes.find(n => n.sourceFile && payload.file_path.endsWith(n.sourceFile));
            if (match) flyToPlanetNode(match.id, actor);
          }}
        }} catch (_) {{}}
      }});
    }} catch (_) {{}}
  }}

  setPlanetMode(isPlanetActive);
  const topFileCandidates = planetNodes.filter(n => n.isFileOrPromoted && !n.isTest).sort((a, b) => b.degree - a.degree);
  if (topFileCandidates.length > 0) {{
    flyToPlanetNode(topFileCandidates[0].id, 'NODO-PRINCIPAL');
  }}
  requestAnimationFrame(renderPlanet);
}})();
</script>"""


def to_planet_html(
    G,
    communities: dict[int, list[str]],
    output_path: str,
    community_labels: dict[int, str] | None = None,
    member_counts: dict[int, int] | None = None,
    node_limit: int | None = None,
    learning_overlay: dict | None = None,
) -> bool:
    """Generate a standalone 360 deg Living Planet HTML visualization (defaults to 3D Planet mode)."""
    from graphify.exporters.html import to_html
    from graphify.paths import write_text_atomic

    written = to_html(
        G,
        communities,
        output_path,
        community_labels=community_labels,
        member_counts=member_counts,
        node_limit=node_limit,
        learning_overlay=learning_overlay,
    )
    if not written:
        return False

    p = Path(output_path)
    content = p.read_text(encoding="utf-8")
    content = content.replace("let isPlanetActive = false;", "let isPlanetActive = true;", 1)
    content = content.replace(
        '<button type="button" id="btn-mode-2d" class="active">',
        '<button type="button" id="btn-mode-2d" class="">',
        1,
    )
    content = content.replace(
        '<button type="button" id="btn-mode-planet" class="">',
        '<button type="button" id="btn-mode-planet" class="active">',
        1,
    )
    write_text_atomic(p, content)
    return True
