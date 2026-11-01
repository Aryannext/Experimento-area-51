'use strict';

const fs = require('fs');
const path = require('path');

const IMPACT_RELATIONS = new Set([
  'calls',
  'indirect_call',
  'references',
  'imports',
  'imports_from',
  'dynamic_import',
  're_exports',
  'inherits',
  'extends',
  'implements',
  'uses',
  'mixes_in',
  'embeds',
  'defines',
  'requires',
]);

// Process-local mtime cache so repeated GateGuard checks in the same process take <1ms
const _graphCache = new Map();

function normalizePosix(p) {
  return String(p || '').replace(/\\/g, '/').replace(/^\.\//, '');
}

/**
 * Locate `graphify-out/graph.json` in `cwd` (or `CLAUDE_PROJECT_DIR` / `GRAPHIFY_GRAPH_PATH`).
 */
function findGraphJsonPath(cwd) {
  const candidates = [];
  if (process.env.GRAPHIFY_GRAPH_PATH) {
    candidates.push(process.env.GRAPHIFY_GRAPH_PATH);
  }
  const baseDir = cwd || process.env.CLAUDE_PROJECT_DIR || process.cwd();
  if (baseDir) {
    candidates.push(path.join(path.resolve(baseDir), 'graphify-out', 'graph.json'));
  }

  for (const candidate of candidates) {
    try {
      if (fs.existsSync(candidate) && fs.statSync(candidate).isFile()) {
        return candidate;
      }
    } catch {
      // ignore inaccessible paths
    }
  }
  return null;
}

/**
 * Load and index `graph.json` + optional `.graphify_learning.json` sidecar.
 */
function loadGraphCached(graphPath) {
  try {
    const resolved = path.resolve(graphPath);
    const stat = fs.statSync(resolved);
    const key = `${stat.mtimeMs}:${stat.size}`;
    const cached = _graphCache.get(resolved);
    if (cached && cached.key === key) {
      return cached.index;
    }

    const raw = JSON.parse(fs.readFileSync(resolved, 'utf8'));
    const nodes = Array.isArray(raw.nodes) ? raw.nodes : [];
    const edges = Array.isArray(raw.links)
      ? raw.links
      : Array.isArray(raw.edges)
        ? raw.edges
        : [];

    const nodeById = new Map();
    const nodesByFile = new Map();
    const degreeById = new Map();

    for (const n of nodes) {
      if (!n || !n.id) continue;
      nodeById.set(String(n.id), n);
      degreeById.set(String(n.id), 0);
      if (n.source_file) {
        const normFile = normalizePosix(n.source_file).toLowerCase();
        if (!nodesByFile.has(normFile)) nodesByFile.set(normFile, []);
        nodesByFile.get(normFile).push(n);
      }
    }

    // Reverse adjacency: targetId -> [{ sourceId, relation, confidence, source_file, source_location }]
    const reverseAdj = new Map();
    for (const e of edges) {
      if (!e || e.source == null || e.target == null) continue;
      const src = String(e.source);
      const tgt = String(e.target);
      degreeById.set(src, (degreeById.get(src) || 0) + 1);
      degreeById.set(tgt, (degreeById.get(tgt) || 0) + 1);
      const rel = String(e.relation || 'related');
      if (!reverseAdj.has(tgt)) reverseAdj.set(tgt, []);
      reverseAdj.get(tgt).push({
        sourceId: src,
        relation: rel,
        confidence: String(e.confidence || 'EXTRACTED'),
        source_file: e.source_file || null,
        source_location: e.source_location || null,
      });
    }

    // Load optional .graphify_learning.json sidecar
    const learningPath = path.join(path.dirname(resolved), '.graphify_learning.json');
    let learningOverlay = {};
    try {
      if (fs.existsSync(learningPath)) {
        const lRaw = JSON.parse(fs.readFileSync(learningPath, 'utf8'));
        learningOverlay = (lRaw && typeof lRaw === 'object' && lRaw.nodes) ? lRaw.nodes : lRaw;
      }
    } catch {
      learningOverlay = {};
    }

    const repoRoot = path.dirname(path.dirname(resolved));
    const index = {
      graphPath: resolved,
      repoRoot,
      builtAtCommit: typeof raw.built_at_commit === 'string' ? raw.built_at_commit.trim() : null,
      nodes,
      edges,
      nodeById,
      nodesByFile,
      degreeById,
      reverseAdj,
      learningOverlay,
    };

    _graphCache.set(resolved, { key, index });
    return index;
  } catch {
    return null;
  }
}

function isTestFilePath(filePath) {
  const norm = normalizePosix(filePath).toLowerCase();
  const base = path.posix.basename(norm);
  return (
    norm.includes('/test/') ||
    norm.includes('/tests/') ||
    norm.includes('/__tests__/') ||
    base.startsWith('test_') ||
    base.endsWith('_test.py') ||
    base.endsWith('_test.go') ||
    base.includes('.test.') ||
    base.includes('.spec.')
  );
}

/**
 * Compute deterministic AST blast radius for `targetPath` from `graphify-out/graph.json`.
 */
function queryFileBlastRadius(targetPath, options = {}) {
  if (!targetPath || typeof targetPath !== 'string') {
    return { found: false };
  }
  const cwd = options.cwd || process.env.CLAUDE_PROJECT_DIR || process.cwd();
  const graphPath = options.graphPath || findGraphJsonPath(cwd);
  if (!graphPath) {
    return { found: false };
  }
  const idx = loadGraphCached(graphPath);
  if (!idx) {
    return { found: false };
  }

  const normTarget = normalizePosix(targetPath).toLowerCase();
  const targetBase = path.posix.basename(normTarget);
  let relToRepo = normTarget;
  if (path.isAbsolute(targetPath)) {
    const rel = normalizePosix(path.relative(idx.repoRoot, targetPath)).toLowerCase();
    if (!rel.startsWith('..')) {
      relToRepo = rel;
    }
  }

  // Match nodes belonging to this file
  let matchedNodes = idx.nodesByFile.get(relToRepo) || idx.nodesByFile.get(normTarget) || [];
  if (matchedNodes.length === 0) {
    // Suffix or basename match on source_file
    for (const [fileKey, fileNodes] of idx.nodesByFile.entries()) {
      if (
        fileKey.endsWith('/' + relToRepo) ||
        relToRepo.endsWith('/' + fileKey) ||
        path.posix.basename(fileKey) === targetBase
      ) {
        matchedNodes = matchedNodes.concat(fileNodes);
      }
    }
  }

  if (matchedNodes.length === 0) {
    return { found: false, graphPath };
  }

  const seedIds = new Set(matchedNodes.map(n => String(n.id)));
  const visited = new Set(seedIds);
  const depth1Hits = [];
  const depth2Nodes = new Set();
  const affectedTestsSet = new Set();

  // BFS depth 1 -> 2 over reverse impact edges
  const queue = Array.from(seedIds).map(id => ({ id, depth: 0 }));
  while (queue.length > 0) {
    const { id: currId, depth } = queue.shift();
    if (depth >= 2) continue;
    const incoming = idx.reverseAdj.get(currId) || [];
    for (const edge of incoming) {
      if (!IMPACT_RELATIONS.has(edge.relation)) continue;
      const peerNode = idx.nodeById.get(edge.sourceId);
      const peerFile = peerNode ? normalizePosix(peerNode.source_file || '') : '';
      if (peerFile && isTestFilePath(peerFile)) {
        affectedTestsSet.add(peerFile);
      }
      if (visited.has(edge.sourceId)) continue;
      visited.add(edge.sourceId);
      const nextDepth = depth + 1;
      if (nextDepth === 1 && peerNode) {
        depth1Hits.push({
          id: edge.sourceId,
          label: String(peerNode.label || edge.sourceId),
          source_file: peerFile || null,
          relation: edge.relation,
          confidence: edge.confidence,
        });
      } else if (nextDepth === 2) {
        depth2Nodes.add(edge.sourceId);
      }
      queue.push({ id: edge.sourceId, depth: nextDepth });
    }
  }

  // Deduplicate depth1 external file/symbol dependents
  const externalCallers = [];
  const seenCallerKey = new Set();
  for (const h of depth1Hits) {
    const key = `${h.source_file || ''}:${h.label}:${h.relation}`;
    if (seenCallerKey.has(key)) continue;
    seenCallerKey.add(key);
    externalCallers.push(h);
  }

  // Check learning overlay annotations on matched nodes
  const learningNotes = [];
  for (const n of matchedNodes) {
    const entry = idx.learningOverlay && idx.learningOverlay[String(n.id)];
    const status = (entry && entry.learning_status) || n.learning_status;
    if (status) {
      learningNotes.push({
        label: String(n.label || n.id),
        status: String(status),
        stale: Boolean((entry && entry.learning_stale) || n.learning_stale),
      });
    }
  }

  const symbols = matchedNodes
    .map(n => String(n.label || n.id))
    .filter((v, i, a) => a.indexOf(v) === i)
    .slice(0, 6);

  const affectedTests = Array.from(affectedTestsSet).slice(0, 5);

  function formatGateGuardNote() {
    const parts = [];
    if (externalCallers.length > 0) {
      const topCallers = externalCallers
        .slice(0, 4)
        .map(c => `${c.label}${c.source_file ? ` (${c.source_file})` : ''} [${c.relation}]`)
        .join(', ');
      const extra = externalCallers.length > 4 ? ` +${externalCallers.length - 4} more` : '';
      parts.push(`direct dependents (${externalCallers.length}): ${topCallers}${extra}`);
    } else {
      parts.push(`0 external callers/importers in graph (${symbols.length} symbol(s): ${symbols.slice(0, 3).join(', ')})`);
    }
    if (depth2Nodes.size > 0) {
      parts.push(`transitive depth-2 impact: ${depth2Nodes.size} node(s)`);
    }
    if (affectedTests.length > 0) {
      parts.push(`tests in blast radius: ${affectedTests.join(', ')}`);
    }
    if (learningNotes.length > 0) {
      const lStr = learningNotes
        .slice(0, 2)
        .map(l => `${l.label}=${l.status}${l.stale ? '(STALE)' : ''}`)
        .join(', ');
      parts.push(`work-memory: ${lStr}`);
    }
    return `[Graphify Live AST] ${parts.join(' | ')}`;
  }

  return {
    found: true,
    graphPath: idx.graphPath,
    matchedNodes,
    symbols,
    importersAndCallers: externalCallers,
    transitiveCount: depth2Nodes.size,
    affectedTests,
    learningNotes,
    formatGateGuardNote,
  };
}

/**
 * Build a concise architectural summary for ECC's SessionStart hook.
 */
function getSessionStartGraphSummary(cwd) {
  const graphPath = findGraphJsonPath(cwd);
  if (!graphPath) return null;
  const idx = loadGraphCached(graphPath);
  if (!idx) return null;

  const commSet = new Set();
  for (const n of idx.nodes) {
    if (n && n.community != null) commSet.add(n.community);
  }

  // Top 5 God Nodes by degree
  const sortedNodes = idx.nodes
    .slice()
    .sort((a, b) => (idx.degreeById.get(String(b.id)) || 0) - (idx.degreeById.get(String(a.id)) || 0))
    .slice(0, 5)
    .map(n => `${n.label || n.id} (${idx.degreeById.get(String(n.id)) || 0} edges)`);

  const planetPath = path.join(path.dirname(graphPath), 'planet.html');
  const htmlPath = path.join(path.dirname(graphPath), 'graph.html');

  return {
    graphPath,
    planetPath: fs.existsSync(planetPath) ? planetPath : null,
    htmlPath: fs.existsSync(htmlPath) ? htmlPath : null,
    nodeCount: idx.nodes.length,
    edgeCount: idx.edges.length,
    communityCount: commSet.size,
    topGodNodes: sortedNodes,
    builtAtCommit: idx.builtAtCommit,
  };
}

/**
 * Record an edited file in `graphify-out/.ecc_pending_changes.json` so the
 * knowledge graph and 360° Planet stay aware of real-time agent edits.
 */
function recordPendingGraphChange(filePath, cwd) {
  if (!filePath || typeof filePath !== 'string') return false;
  const graphPath = findGraphJsonPath(cwd);
  if (!graphPath) return false;
  try {
    const outDir = path.dirname(graphPath);
    const pendingFile = path.join(outDir, '.ecc_pending_changes.json');
    let state = { updatedAt: null, files: [] };
    if (fs.existsSync(pendingFile)) {
      try {
        state = JSON.parse(fs.readFileSync(pendingFile, 'utf8')) || state;
      } catch {
        // reset corrupt file
      }
    }
    const norm = normalizePosix(filePath);
    const files = Array.isArray(state.files) ? state.files : [];
    if (!files.includes(norm)) {
      files.push(norm);
    }
    const nextState = {
      updatedAt: new Date().toISOString(),
      files: files.slice(-50),
    };
    fs.writeFileSync(pendingFile, JSON.stringify(nextState, null, 2), 'utf8');
    return true;
  } catch {
    return false;
  }
}

module.exports = {
  findGraphJsonPath,
  loadGraphCached,
  queryFileBlastRadius,
  getSessionStartGraphSummary,
  recordPendingGraphChange,
};
