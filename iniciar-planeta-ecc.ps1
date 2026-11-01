param(
    [string]$Proyecto = "",
    [string]$AuditarArchivo = "",
    [switch]$ServidorEnVivo,
    [switch]$DemoGateGuard,
    [int]$Puerto = 8080
)

$ErrorActionPreference = "Stop"
$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$GraphifyDir = Join-Path $RootDir "graphify-8"
$EccDir = Join-Path $RootDir "ECC-main"
$PlanetHtml = Join-Path $GraphifyDir "graphify-out\planet.html"
$GraphJson = Join-Path $GraphifyDir "graphify-out\graph.json"

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   PLANETA 360° VIVO · ECC TOOLS x GRAPHIFY LAUNCHER" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Si el usuario especifica una carpeta de proyecto, construir el grafo ordenado por Capas Arquitectónicas
if ($Proyecto -ne "") {
    $TargetDir = (Resolve-Path $Proyecto).Path
    Write-Host "[1/2] Analizando AST y organizando Capas Arquitectónicas para: $TargetDir" -ForegroundColor Yellow
    Push-Location $GraphifyDir
    try {
        uv run python -c "
import sys, json
from pathlib import Path
from graphify.extract import collect_files, extract
from graphify.build import build
from graphify.export import to_json, to_html, to_planet_html

target = Path(r'$TargetDir')
all_files = collect_files(target)

def _is_bundled_asset(p: Path) -> bool:
    rel = p.relative_to(target).as_posix().lower()
    if any(x in rel for x in ('android/', 'ios/', 'dist/', 'build/', 'node_modules/', '.capacit')):
        return True
    if '/assets/' in rel and ('-' in p.stem and len(p.stem) > 12):
        return True
    if p.name.endswith(('.min.js', '.bundle.js', '.lock')):
        return True
    return False

files = [f for f in all_files if not _is_bundled_asset(f)]
def _priority(p: Path) -> tuple:
    rel = p.relative_to(target).as_posix().lower()
    is_core = rel.startswith(('src/', 'app/', 'lib/', 'components/', 'services/', 'hooks/', 'pages/', 'server/', 'api/'))
    return (0 if is_core else 1, rel)

files.sort(key=_priority)
if len(files) > 180:
    files = files[:180]

ext = extract(files, parallel=False)
G = build([ext])

# Agrupar nodos en Continentes Arquitectónicos reales y legibles (en lugar de decenas de micro-clusters crípticos)
LAYER_DEFS = [
    (0, 'Vistas / Pantallas (Views)', lambda sf: '/views/' in sf or '/pages/' in sf or sf.startswith('views/') or sf.startswith('pages/')),
    (1, 'Logica / Composables & Hooks', lambda sf: '/composables/' in sf or '/hooks/' in sf or '/stores/' in sf),
    (2, 'Base de Datos & Queries (SQL/DB)', lambda sf: '/database/' in sf or '/db/' in sf or '/models/' in sf or '/queries/' in sf),
    (3, 'Componentes UI', lambda sf: '/components/' in sf),
    (4, 'Servicios & Integraciones (API/Bot)', lambda sf: '/services/' in sf or '/api/' in sf or '/clients/' in sf or '/exporters/' in sf),
    (5, 'Pruebas Automatizadas (Tests/Specs)', lambda sf: 'test' in sf or 'spec' in sf or '__tests__' in sf),
    (6, 'Documentacion & Reglas', lambda sf: sf.endswith('.md') or sf.startswith('docs/')),
    (7, 'Nucleo / Core & Configuracion', lambda sf: True),
]

communities = {}
comm_labels = {}
for cid, label, _ in LAYER_DEFS:
    communities[cid] = []
    comm_labels[cid] = label

for nid, data in G.nodes(data=True):
    sf = ('/' + str(data.get('source_file') or '').replace('\\\\', '/').lower().lstrip('/'))
    for cid, label, pred in LAYER_DEFS:
        if pred(sf):
            communities[cid].append(nid)
            break

# Eliminar capas vacías y reindexar 0..N-1 para mantener colores limpios
non_empty = [(cid, comm_labels[cid], members) for cid, members in sorted(communities.items()) if members]
clean_comms = {}
clean_labels = {}
for new_cid, (_, label, members) in enumerate(non_empty):
    clean_comms[new_cid] = members
    clean_labels[new_cid] = label
    for m in members:
        G.nodes[m]['community'] = new_cid
        G.nodes[m]['community_name'] = label

out_dir = target / 'graphify-out'
out_dir.mkdir(exist_ok=True)
(out_dir / '.graphify_labels.json').write_text(json.dumps({str(k): v for k, v in clean_labels.items()}, indent=2), encoding='utf-8')
if (out_dir / 'graph.json').exists():
    (out_dir / 'graph.json').unlink()
to_json(G, clean_comms, str(out_dir / 'graph.json'))
to_html(G, clean_comms, str(out_dir / 'graph.html'), community_labels=clean_labels)
to_planet_html(G, clean_comms, str(out_dir / 'planet.html'), community_labels=clean_labels)
print(f'Listo: {G.number_of_nodes()} nodos organizados en {len(clean_comms)} Continentes Arquitectonicos claros.')
for k, v in clean_labels.items():
    print(f'  Continente {k + 1}: {v} ({len(clean_comms[k])} simbolos)')
"
        $PlanetHtml = Join-Path $TargetDir "graphify-out\planet.html"
        $GraphJson = Join-Path $TargetDir "graphify-out\graph.json"
    } finally {
        Pop-Location
    }
}

# 2. Si el usuario quiere auditar un archivo real con ECC GateGuard + Graphify AST
if ($AuditarArchivo -ne "") {
    $TargetDir = if ($Proyecto -ne "") { (Resolve-Path $Proyecto).Path } else { $RootDir }
    Write-Host ""
    Write-Host "==========================================================" -ForegroundColor Yellow
    Write-Host "   AUDITORIA REAL ECC GATEGUARD + GRAPHIFY AST" -ForegroundColor Yellow
    Write-Host "==========================================================" -ForegroundColor Yellow
    Push-Location $EccDir
    try {
        node -e "
const path = require('path');
const bridge = require('./scripts/lib/graphify-bridge');
const gg = require('./scripts/hooks/gateguard-fact-force');
const repo = process.argv[1];
const file = process.argv[2];
const blast = bridge.queryFileBlastRadius(file, { cwd: repo });
console.log('Archivo auditado :', file);
console.log('Proyecto         :', repo);
console.log('');
if (blast.found) {
  console.log('1. [RADIO DE EXPLOSION AST DETERMINISTA]');
  console.log('   ' + blast.formatGateGuardNote());
  console.log('');
}
const res = gg.run(JSON.stringify({
  session_id: 'audit-' + Date.now(),
  cwd: repo,
  tool_name: 'Edit',
  tool_input: { file_path: path.resolve(repo, file), old_string: 'a', new_string: 'b' }
}));
if (res && res.stdout) {
  const parsed = JSON.parse(res.stdout);
  console.log('2. [COMPUERTA DE SEGURIDAD ECC GATEGUARD (PreToolUse)]');
  console.log('   Decision:', parsed.hookSpecificOutput.permissionDecision.toUpperCase());
  console.log('----------------------------------------------------------');
  console.log(parsed.hookSpecificOutput.permissionDecisionReason);
}
" "$TargetDir" "$AuditarArchivo"
    } finally {
        Pop-Location
    }
}

# 3. Si pide probar la suite de simbiosis de GateGuard en consola
if ($DemoGateGuard) {
    Write-Host ""
    Write-Host "[DEMO] Ejecutando suite de pruebas ECC GateGuard + Graphify..." -ForegroundColor Green
    Push-Location $EccDir
    try {
        node tests/hooks/gateguard-graphify-bridge.test.js
    } finally {
        Pop-Location
    }
}

# 4. Si pide Servidor En Vivo (MCP + SSE en http://127.0.0.1:8080/planet)
if ($ServidorEnVivo) {
    $Url = "http://127.0.0.1:$Puerto/planet"
    Write-Host ""
    Write-Host "[SERVIDOR VIVO] Iniciando servidor Graphify MCP + Telemetria SSE en:" -ForegroundColor Green
    Write-Host "  -> Planeta 360° en Vivo : $Url" -ForegroundColor White
    Write-Host "  -> Endpoint MCP (HTTP)  : http://127.0.0.1:$Puerto/mcp" -ForegroundColor White
    Write-Host "  -> Stream SSE           : http://127.0.0.1:$Puerto/events" -ForegroundColor White
    Write-Host "Presiona Ctrl+C para detener el servidor." -ForegroundColor DarkGray
    Start-Process $Url
    Push-Location $GraphifyDir
    try {
        uv run --extra mcp python -m graphify.serve $GraphJson --transport http --host 127.0.0.1 --port $Puerto
    } finally {
        Pop-Location
    }
} else {
    Write-Host ""
    Write-Host "[PLANETA 360°] Abriendo visualizador limpio y ordenado en tu navegador:" -ForegroundColor Green
    Write-Host "  -> $PlanetHtml" -ForegroundColor White
    Start-Process $PlanetHtml
}
