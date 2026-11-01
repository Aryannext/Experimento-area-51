#!/usr/bin/env node
'use strict';

const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');

const {
  queryFileBlastRadius,
  getSessionStartGraphSummary,
  recordPendingGraphChange,
} = require('../../scripts/lib/graphify-bridge');
const gateguard = require('../../scripts/hooks/gateguard-fact-force');
const postEditAccum = require('../../scripts/hooks/post-edit-accumulator');

let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    fn();
    console.log(`  \u2713 ${name}`);
    passed++;
  } catch (err) {
    console.error(`  \u2717 ${name}: ${err.message}`);
    failed++;
  }
}

function createTempRepoWithGraph() {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'ecc-graphify-test-'));
  const srcDir = path.join(tmpDir, 'src');
  const testsDir = path.join(tmpDir, 'tests');
  const graphDir = path.join(tmpDir, 'graphify-out');
  fs.mkdirSync(srcDir, { recursive: true });
  fs.mkdirSync(testsDir, { recursive: true });
  fs.mkdirSync(graphDir, { recursive: true });

  fs.writeFileSync(path.join(srcDir, 'auth_token.py'), 'def verify_token(tok):\n    return True\n', 'utf8');
  fs.writeFileSync(path.join(srcDir, 'api_router.py'), 'from src.auth_token import verify_token\n', 'utf8');
  fs.writeFileSync(path.join(testsDir, 'test_auth_token.py'), 'from src.auth_token import verify_token\n', 'utf8');

  const sampleGraph = {
    directed: true,
    built_at_commit: 'abc1234def5678',
    nodes: [
      { id: 'auth_token_mod', label: 'auth_token.py', source_file: 'src/auth_token.py', source_location: 'L1', file_type: 'code', community: 0 },
      { id: 'verify_token_fn', label: 'verify_token()', source_file: 'src/auth_token.py', source_location: 'L1', file_type: 'code', community: 0 },
      { id: 'api_router_mod', label: 'api_router.py', source_file: 'src/api_router.py', source_location: 'L1', file_type: 'code', community: 1 },
      { id: 'checkout_handler', label: 'checkout_handler()', source_file: 'src/checkout.py', source_location: 'L10', file_type: 'code', community: 1 },
      { id: 'test_auth_mod', label: 'test_auth_token.py', source_file: 'tests/test_auth_token.py', source_location: 'L1', file_type: 'code', community: 2 },
    ],
    links: [
      { source: 'auth_token_mod', target: 'verify_token_fn', relation: 'defines', confidence: 'EXTRACTED' },
      { source: 'api_router_mod', target: 'verify_token_fn', relation: 'calls', confidence: 'EXTRACTED' },
      { source: 'checkout_handler', target: 'api_router_mod', relation: 'calls', confidence: 'EXTRACTED' },
      { source: 'test_auth_mod', target: 'verify_token_fn', relation: 'calls', confidence: 'INFERRED' },
    ],
  };

  fs.writeFileSync(path.join(graphDir, 'graph.json'), JSON.stringify(sampleGraph, null, 2), 'utf8');
  fs.writeFileSync(
    path.join(graphDir, '.graphify_learning.json'),
    JSON.stringify({
      nodes: {
        verify_token_fn: { learning_status: 'preferred', learning_stale: false },
      },
    }),
    'utf8'
  );
  fs.writeFileSync(path.join(graphDir, 'planet.html'), '<html></html>', 'utf8');

  return tmpDir;
}

function writeTranscript(tmpDir, records) {
  const tPath = path.join(tmpDir, 'transcript.jsonl');
  fs.writeFileSync(tPath, records.map(r => JSON.stringify(r)).join('\n') + '\n', 'utf8');
  return tPath;
}

console.log('\n=== ECC x Graphify Real-Time Symbiosis Tests ===');

test('queryFileBlastRadius returns deterministic AST callers, transitive count, tests, and work-memory status', () => {
  const repo = createTempRepoWithGraph();
  const res = queryFileBlastRadius('src/auth_token.py', { cwd: repo });
  assert.strictEqual(res.found, true);
  assert.strictEqual(res.importersAndCallers.length, 2);
  assert.strictEqual(res.transitiveCount, 1); // checkout_handler -> api_router_mod -> verify_token_fn
  assert.deepStrictEqual(res.affectedTests, ['tests/test_auth_token.py']);
  const note = res.formatGateGuardNote();
  assert.ok(note.includes('[Graphify Live AST]'), note);
  assert.ok(note.includes('api_router.py (src/api_router.py) [calls]'), note);
  assert.ok(note.includes('tests in blast radius: tests/test_auth_token.py'), note);
  assert.ok(note.includes('work-memory: verify_token()=preferred'), note);
});

test('getSessionStartGraphSummary reports nodes, edges, communities, god nodes, and planet.html path', () => {
  const repo = createTempRepoWithGraph();
  const summary = getSessionStartGraphSummary(repo);
  assert.ok(summary);
  assert.strictEqual(summary.nodeCount, 5);
  assert.strictEqual(summary.edgeCount, 4);
  assert.strictEqual(summary.communityCount, 3);
  assert.ok(summary.planetPath && summary.planetPath.endsWith('planet.html'));
  assert.ok(summary.topGodNodes[0].includes('verify_token()'));
});

test('GateGuard first-touch denial injects [Graphify Live AST] blast radius facts when graph.json exists', () => {
  const repo = createTempRepoWithGraph();
  const stateDir = fs.mkdtempSync(path.join(os.tmpdir(), 'gg-state-'));
  const prevStateDir = process.env.GATEGUARD_STATE_DIR;
  process.env.GATEGUARD_STATE_DIR = stateDir;
  try {
    const targetFile = path.join(repo, 'src', 'auth_token.py');
    const result = gateguard.run(
      JSON.stringify({
        session_id: 'sess-deny-ast',
        cwd: repo,
        tool_name: 'Edit',
        tool_input: {
          file_path: targetFile,
          old_string: 'return True',
          new_string: 'return bool(tok)',
        },
      })
    );
    const parsed = JSON.parse(result.stdout);
    assert.strictEqual(parsed.hookSpecificOutput.permissionDecision, 'deny');
    const reason = parsed.hookSpecificOutput.permissionDecisionReason;
    assert.ok(reason.includes('[Graphify Live AST]'), `Expected Graphify AST facts in denial:\n${reason}`);
    assert.ok(reason.includes('api_router.py (src/api_router.py) [calls]'), reason);
    assert.ok(reason.includes('tests/test_auth_token.py'), reason);
  } finally {
    if (prevStateDir === undefined) delete process.env.GATEGUARD_STATE_DIR;
    else process.env.GATEGUARD_STATE_DIR = prevStateDir;
  }
});

test('GateGuard credits prior mcp__graphify__blast_radius call and allows first-touch Edit with AST context', () => {
  const repo = createTempRepoWithGraph();
  const stateDir = fs.mkdtempSync(path.join(os.tmpdir(), 'gg-state-mcp-'));
  const prevStateDir = process.env.GATEGUARD_STATE_DIR;
  process.env.GATEGUARD_STATE_DIR = stateDir;
  try {
    const transcriptPath = writeTranscript(repo, [
      { type: 'user', uuid: 'u-1', message: { role: 'user', content: 'Update verify_token in auth_token.py' } },
      {
        type: 'assistant',
        message: {
          id: 'msg-1',
          role: 'assistant',
          content: [
            {
              type: 'tool_use',
              id: 'tu-graphify-1',
              name: 'mcp__graphify__blast_radius',
              input: { label: 'src/auth_token.py', depth: 2 },
            },
          ],
        },
      },
      {
        type: 'user',
        message: {
          role: 'user',
          content: [{ type: 'tool_result', tool_use_id: 'tu-graphify-1', content: 'Affected nodes for auth_token.py...' }],
        },
      },
      {
        type: 'assistant',
        message: {
          id: 'msg-2',
          role: 'assistant',
          content: [
            {
              type: 'tool_use',
              id: 'tu-edit-1',
              name: 'Edit',
              input: { file_path: path.join(repo, 'src', 'auth_token.py') },
            },
          ],
        },
      },
    ]);

    const result = gateguard.run(
      JSON.stringify({
        session_id: 'sess-credit-mcp',
        cwd: repo,
        transcript_path: transcriptPath,
        tool_use_id: 'tu-edit-1',
        tool_name: 'Edit',
        tool_input: {
          file_path: path.join(repo, 'src', 'auth_token.py'),
          old_string: 'return True',
          new_string: 'return bool(tok)',
        },
      })
    );
    assert.strictEqual(result.exitCode, 0);
    assert.ok(result.additionalContext, 'Expected credit additionalContext');
    assert.ok(result.additionalContext.includes('mcp__graphify__blast_radius'), result.additionalContext);
    assert.ok(result.additionalContext.includes('[Graphify Live AST]'), result.additionalContext);
  } finally {
    if (prevStateDir === undefined) delete process.env.GATEGUARD_STATE_DIR;
    else process.env.GATEGUARD_STATE_DIR = prevStateDir;
  }
});

test('GateGuard credits prior `graphify affected` CLI command in Bash', () => {
  const repo = createTempRepoWithGraph();
  const stateDir = fs.mkdtempSync(path.join(os.tmpdir(), 'gg-state-cli-'));
  const prevStateDir = process.env.GATEGUARD_STATE_DIR;
  process.env.GATEGUARD_STATE_DIR = stateDir;
  try {
    const transcriptPath = writeTranscript(repo, [
      { type: 'user', uuid: 'u-2', message: { role: 'user', content: 'Refactor auth_token.py' } },
      {
        type: 'assistant',
        message: {
          id: 'msg-cli-1',
          role: 'assistant',
          content: [
            {
              type: 'tool_use',
              id: 'tu-bash-1',
              name: 'Bash',
              input: { command: 'graphify affected src/auth_token.py' },
            },
          ],
        },
      },
      {
        type: 'user',
        message: {
          role: 'user',
          content: [{ type: 'tool_result', tool_use_id: 'tu-bash-1', content: 'Affected nodes...' }],
        },
      },
      {
        type: 'assistant',
        message: {
          id: 'msg-cli-2',
          role: 'assistant',
          content: [
            {
              type: 'tool_use',
              id: 'tu-edit-2',
              name: 'Edit',
              input: { file_path: path.join(repo, 'src', 'auth_token.py') },
            },
          ],
        },
      },
    ]);

    const result = gateguard.run(
      JSON.stringify({
        session_id: 'sess-credit-cli',
        cwd: repo,
        transcript_path: transcriptPath,
        tool_use_id: 'tu-edit-2',
        tool_name: 'Edit',
        tool_input: {
          file_path: path.join(repo, 'src', 'auth_token.py'),
          old_string: 'return True',
          new_string: 'return bool(tok)',
        },
      })
    );
    assert.strictEqual(result.exitCode, 0);
    assert.ok(result.additionalContext && result.additionalContext.includes('Bash graphify affected src/auth_token.py'), result.additionalContext);
  } finally {
    if (prevStateDir === undefined) delete process.env.GATEGUARD_STATE_DIR;
    else process.env.GATEGUARD_STATE_DIR = prevStateDir;
  }
});

test('PostToolUse post-edit-accumulator records edited files in graphify-out/.ecc_pending_changes.json', () => {
  const repo = createTempRepoWithGraph();
  postEditAccum.run(
    JSON.stringify({
      session_id: 'sess-post-edit',
      cwd: repo,
      tool_name: 'Edit',
      tool_input: { file_path: 'src/auth_token.py' },
    })
  );
  const pendingFile = path.join(repo, 'graphify-out', '.ecc_pending_changes.json');
  assert.ok(fs.existsSync(pendingFile), 'Expected .ecc_pending_changes.json to be created');
  const data = JSON.parse(fs.readFileSync(pendingFile, 'utf8'));
  assert.ok(Array.isArray(data.files) && data.files.includes('src/auth_token.py'));
});

console.log(`\nPassed: ${passed}, Failed: ${failed}`);
if (failed > 0) process.exit(1);
