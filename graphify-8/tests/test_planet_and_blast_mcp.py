"""Tests for the 360° Living Planet engine (planet.py) and MCP blast_radius + SSE telemetry (serve.py)."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import networkx as nx
import pytest

from graphify.cluster import cluster
from graphify.export import to_html, to_planet_html
from graphify import serve as serve_mod


def _make_planet_test_graph() -> nx.Graph:
    G = nx.DiGraph()
    G.add_node("auth_service", label="AuthService", file_type="code", source_file="src/auth.py", source_location="L1", community=0)
    G.add_node("verify_token", label="verify_token()", file_type="code", source_file="src/auth.py", source_location="L42", community=0)
    G.add_node("api_router", label="api_router.py", file_type="code", source_file="src/api_router.py", source_location="L1", community=1)
    G.add_node("test_auth", label="test_auth.py", file_type="code", source_file="tests/test_auth.py", source_location="L1", community=1)
    G.add_edge("auth_service", "verify_token", relation="defines", confidence="EXTRACTED")
    G.add_edge("api_router", "verify_token", relation="calls", confidence="EXTRACTED", source_file="src/api_router.py", source_location="L19")
    G.add_edge("test_auth", "verify_token", relation="calls", confidence="INFERRED", source_file="tests/test_auth.py", source_location="L12")
    return G


def test_to_html_and_to_planet_html_emit_360_planet_engine():
    G = _make_planet_test_graph()
    communities = cluster(G)
    with tempfile.TemporaryDirectory() as tmp:
        html_out = Path(tmp) / "graph.html"
        planet_out = Path(tmp) / "planet.html"
        assert to_html(G, communities, str(html_out)) is True
        assert to_planet_html(G, communities, str(planet_out)) is True

        html_text = html_out.read_text(encoding="utf-8")
        planet_text = planet_out.read_text(encoding="utf-8")

        assert 'id="graphify-planet-engine"' in html_text
        assert 'id="graphify-planet-engine"' in planet_text
        assert "let isPlanetActive = false;" in html_text
        assert "let isPlanetActive = true;" in planet_text
        assert "PLANETA 360" in planet_text


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_planet_engine_executes_in_node_and_computes_3d_continents_and_blast_radius():
    """Verify the embedded 360° Living Planet script initializes cleanly in JS,
    places nodes into orbital layers on the sphere, and computes blast radius."""
    G = _make_planet_test_graph()
    communities = {0: ["auth_service", "verify_token"], 1: ["api_router", "test_auth"]}
    with tempfile.TemporaryDirectory() as tmp:
        planet_out = Path(tmp) / "planet.html"
        to_planet_html(G, communities, str(planet_out), community_labels={0: "Auth Core", 1: "API & Tests"})
        planet_html = planet_out.read_text(encoding="utf-8")

        m_main = re.search(r"<script>\nconst RAW_NODES = (.*?);\nconst RAW_EDGES = (.*?);\nconst LEGEND = (.*?);\n", planet_html)
        assert m_main is not None
        m_planet = re.search(r'<script id="graphify-planet-engine">(.*?)</script>', planet_html, re.DOTALL)
        assert m_planet is not None

        harness = f"""
const RAW_NODES = {m_main.group(1)};
const RAW_EDGES = {m_main.group(2)};
const LEGEND = {m_main.group(3)};

const elements = new Map();
function makeEl(id = '') {{
  const el = {{
    id,
    innerHTML: '',
    textContent: '',
    style: {{}},
    children: [],
    classList: {{
      _set: new Set(),
      add(c) {{ this._set.add(c); }},
      remove(c) {{ this._set.delete(c); }},
      toggle(c, force) {{
        if (force === undefined) {{
          if (this._set.has(c)) this._set.delete(c); else this._set.add(c);
        }} else if (force) this._set.add(c); else this._set.delete(c);
      }},
      contains(c) {{ return this._set.has(c); }}
    }},
    appendChild(child) {{ this.children.push(child); return child; }},
    insertBefore(child) {{
      this.children.unshift(child);
      if (child.id) elements.set(child.id, child);
      // Register inner IDs created via innerHTML
      if (child.innerHTML) {{
        for (const m of child.innerHTML.matchAll(/id="([^"]+)"/g)) {{
          if (!elements.has(m[1])) elements.set(m[1], makeEl(m[1]));
        }}
      }}
      return child;
    }},
    removeChild() {{}},
    addEventListener(type, fn) {{ this['_on_' + type] = fn; }},
    getBoundingClientRect() {{ return {{ left: 0, top: 0, width: 960, height: 720 }}; }},
    getContext() {{
      return new Proxy({{
        createRadialGradient() {{ return {{ addColorStop() {{}} }}; }},
        measureText(t) {{ return {{ width: String(t).length * 6 }}; }}
      }}, {{ get(target, prop) {{ return prop in target ? target[prop] : () => {{}}; }} }});
    }}
  }};
  if (id) elements.set(id, el);
  return el;
}}

const bodyEl = makeEl('body');
const graphEl = makeEl('graph');
graphEl.parentNode = bodyEl;
graphEl.clientWidth = 960;
graphEl.clientHeight = 720;
const sidebarEl = makeEl('sidebar');

global.window = {{
  devicePixelRatio: 1,
  location: {{ protocol: 'file:' }},
  addEventListener() {{}}
}};
global.document = {{
  createElement(tag) {{ return makeEl(tag); }},
  getElementById(id) {{
    if (!elements.has(id)) elements.set(id, makeEl(id));
    return elements.get(id);
  }},
  querySelectorAll() {{ return []; }}
}};
global.performance = {{ now: () => 1000 }};
let rafCallback = null;
global.requestAnimationFrame = (cb) => {{ rafCallback = cb; }};

{m_planet.group(1)}

// Execute one animation frame of the 360° Planet renderer
if (rafCallback) rafCallback(1016);

// Trigger simulated ECC Agent pulse button
const pulseBtn = elements.get('btn-planet-pulse');
if (pulseBtn && pulseBtn._on_click) pulseBtn._on_click();

const blastBox = elements.get('planet-blast-box');
console.log(JSON.stringify({{
  hasPlanetStage: elements.has('planet-stage'),
  blastBoxHtml: blastBox ? blastBox.innerHTML : '',
}}));
"""
        harness_path = Path(tmp) / "harness.js"
        harness_path.write_text(harness, encoding="utf-8")
        proc = subprocess.run(["node", str(harness_path)], capture_output=True, text=True, encoding="utf-8")
        assert proc.returncode == 0, f"STDERR:\n{proc.stderr}\nSTDOUT:\n{proc.stdout}"
        out = json.loads(proc.stdout.strip().splitlines()[-1])
        assert out["hasPlanetStage"] is True
        assert "Impacto Directo" in out["blastBoxHtml"]
        assert "Recomendados" in out["blastBoxHtml"]
        assert "Todos (" in out["blastBoxHtml"]
        assert "python-reviewer" in out["blastBoxHtml"]


def test_mcp_blast_radius_and_http_planet_and_sse_events(tmp_path):
    pytest.importorskip("mcp")
    pytest.importorskip("starlette")
    from starlette.testclient import TestClient

    G = _make_planet_test_graph()
    graph_data = nx.node_link_data(G)
    graph_path = tmp_path / "graph.json"
    graph_path.write_text(json.dumps(graph_data), encoding="utf-8")

    app = serve_mod._build_http_app(str(graph_path), json_response=True)
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    init_body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "ecc-test", "version": "1.0"},
        },
    }
    with TestClient(app, base_url="http://127.0.0.1") as client:
        init_res = client.post("/mcp", headers=headers, json=init_body)
        assert init_res.status_code == 200
        s_headers = {**headers, "mcp-session-id": init_res.headers["mcp-session-id"]}
        client.post("/mcp", headers=s_headers, json={"jsonrpc": "2.0", "method": "notifications/initialized"})

        # 1. Verify blast_radius is registered in tools/list
        tools_res = client.post("/mcp", headers=s_headers, json={"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        tool_names = {t["name"] for t in tools_res.json()["result"]["tools"]}
        assert "blast_radius" in tool_names

        # 2. Call blast_radius on verify_token()
        call_res = client.post(
            "/mcp",
            headers=s_headers,
            json={
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "blast_radius", "arguments": {"label": "verify_token()", "depth": 2}},
            },
        )
        assert call_res.status_code == 200
        blast_text = call_res.json()["result"]["content"][0]["text"]
        assert "Affected nodes for verify_token()" in blast_text
        assert "api_router.py [calls]" in blast_text
        assert "test_auth.py [calls]" in blast_text

        # 3. Verify GET /planet serves the 360° Living Planet HTML
        planet_res = client.get("/planet")
        assert planet_res.status_code == 200
        assert 'id="graphify-planet-engine"' in planet_res.text

        # 4. Verify GET /events?once=1 streams the live telemetry event emitted by blast_radius
        events_res = client.get("/events?once=1")
        assert events_res.status_code == 200
        assert "event: graphify_event" in events_res.text
        assert "MCP:blast_radius" in events_res.text
