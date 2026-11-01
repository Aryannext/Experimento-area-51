# 🪐 ECC × Graphify — Planeta 360° Vivo & Estación de Control de Agentes IA

[![Licencia: MIT](https://img.shields.io/badge/Licencia-MIT%20%2F%20Apache--2.0-blue.svg)](LICENSE)
[![Open Source](https://img.shields.io/badge/Open%20Source-100%25%20Gratis-brightgreen.svg)](CONTRIBUTING.md)
[![ECC Tools](https://img.shields.io/badge/ECC%20Tools-65%2B%20Agentes%20%26%20GateGuard-indigo.svg)](ECC-main/)
[![Graphify AST](https://img.shields.io/badge/Graphify-AST%20Planeta%20360%C2%B0%20%26%202D-0284c7.svg)](graphify-8/)

**ECC × Graphify** une dos mundos en una sola herramienta **100% gratuita, local y open source**:
1. **🪐 Graphify (Memoria Cartográfica AST en 3D y 2D)**: Analiza determinísticamente cualquier proyecto con `tree-sitter` y lo transforma en un **Planeta 360° Vivo** y un **Mapa 2D Limpio**, organizado por **Continentes Arquitectónicos reales** (`Vistas`, `Lógica/Composables`, `Base de Datos`, `Componentes UI`, `Servicios/APIs`, `Tests`, `Documentación` y `Core`).
2. **🛡️ ECC Tools (Everything Claude Code — Sistema Operativo para Agentes IA)**: Conecta **más de 65 agentes especializados, comandos y el hook GateGuard** directamente a cada nodo del grafo.

---

## ✨ ¿Qué hace única a esta herramienta?

### 1. 🧭 Cero "Bola de Pelos" — Orden Arquitectónico y Nivel de Claridad (3D y 2D)
* **Continentes Arquitectónicos Claros**: En lugar de mezclar cientos de funciones sueltas, agrupa tu código por capas de arquitectura reales.
* **Filtro de Claridad en Vivo**: Alterna con un clic entre **`🏛️ Solo Archivos`** (vista limpia de alto nivel), **`+ 🧪 Tests`** o **`🔬 Todo el AST`** tanto en el **Planeta 360°** como en el **Mapa 2D**.
* **Líneas Enfocadas**: Por defecto muestra solo las conexiones del nodo que estás inspeccionando (`🎯 Líneas: Solo Nodo Activo`), eliminando el ruido visual.

### 2. 🔗 "Todo lo que toca este Nodo" (Explorador de Impacto en 1 Clic)
Al hacer clic en cualquier nodo (en el Planeta 3D o en el Mapa 2D), el panel lateral te muestra al instante:
* **`📥 Impacto Directo`**: ¿Qué vistas, componentes o módulos importan o llaman a este nodo? *(Lo que podrías romper si lo editas)*.
* **`📤 Toca / Usa`**: ¿De qué módulos, queries de base de datos o servicios depende este nodo?
* **`🧪 Tests`**: ¿Qué archivos `.spec` / `.test` cubren este nodo? *(Si es `0`, te avisa al instante)*.
* **`⚙️ Internos`**: Todas las funciones, clases y métodos declarados dentro de ese archivo.

### 3. ⭐ Recomendación Inteligente de Agentes + Catálogo Completo de ECC Tools (65+ Agentes)
Dependiendo del nodo que selecciones, el motor analiza su tecnología, capa, complejidad y cobertura de pruebas para **recomendarte automáticamente los agentes ideales** explicando por qué:
* **Nodo `.vue` / UI** → Recomienda `vue-reviewer (/vue-review)`, `a11y-architect`, `/multi-frontend`, `e2e-runner`.
* **Nodo Base de Datos / SQL** → Recomienda `database-reviewer`, `security-reviewer (/security-scan)`, `silent-failure-hunter`, `performance-optimizer`.
* **Nodo Servicio / API / Bot** → Recomienda `network-architect`, `network-troubleshooter`, `silent-failure-hunter`, `security-reviewer`.
* **Nodo con Alto Radio de Impacto** → Activa `GateGuard AST`, `/orch-change-feature`, `code-architect`.
* **Nodo sin Pruebas (`0 Tests`)** → Recomienda `tdd-guide (/tdd)` y `pr-test-analyzer (/test-coverage)`.

¿Quieres usar cualquier otro agente? Tienes **filtros por categoría** (`🧠 Arquitectura`, `🎨 UI/Vue/Web`, `🗄️ BD/Seguridad/Red`, `🔍 Revisión/Refactor`, `🧪 Tests/Build`, `🚀 Orquestación`, `📋 Todos`) y un **buscador instantáneo** para elegir entre los **65+ agentes y comandos de ECC**, generando en 1 clic el prompt enriquecido con las conexiones reales del nodo.

### 4. 🛡️ Compuerta Pre-Edición `GateGuard` Conectada al Grafo en Tiempo Real
Cuando un agente de IA (en Claude Code, Cursor, Codex, Gemini CLI, etc.) intenta editar un archivo sin haber investigado su impacto, el hook [`gateguard-fact-force.js`](ECC-main/scripts/hooks/gateguard-fact-force.js) consulta `graph.json` en `<5ms` a través de [`graphify-bridge.js`](ECC-main/scripts/lib/graphify-bridge.js) y le exige verificar primero sus dependientes reales y sus tests.

---

## 🚀 Instalación y Uso Rápido (100% Gratis y Local)

### Requisitos previos
* **[Python 3.10+](https://www.python.org/)** + **[uv](https://docs.astral.sh/uv/getting-started/installation/)**
* **[Node.js 18+](https://nodejs.org/)**
* **Git**

### Paso 1: Clonar el repositorio (rama `argon`) e instalar dependencias
```powershell
git clone -b argon https://github.com/Aryannext/Experimento-area-51.git
cd Experimento-area-51

# Preparar el motor AST y servidor MCP de Graphify
cd graphify-8
uv sync --extra mcp
cd ..
```

### Paso 2: Generar y abrir el Planeta 360° + Mapa 2D en CUALQUIER proyecto tuyo
Ejecuta el lanzador pasándole la ruta de tu proyecto:
```powershell
.\iniciar-planeta-ecc.ps1 -Proyecto "C:\ruta\a\tu\proyecto"
```
*(También puedes usar `.\Iniciar-Planeta-360.bat -Proyecto "C:\ruta\a\tu\proyecto"`).*

Esto generará automáticamente en tu proyecto:
* `graphify-out/planet.html` → Visualizador **Planeta 360° Vivo + Mapa 2D + Estación ECC Tools**.
* `graphify-out/graph.json` → Grafo AST consultable por los hooks y agentes de ECC en tiempo real.

### Paso 3: Auditar un archivo con GateGuard o iniciar el Servidor En Vivo (MCP + SSE)
* **Auditar el radio de explosión de un archivo específico con ECC GateGuard**:
  ```powershell
  .\iniciar-planeta-ecc.ps1 -Proyecto "C:\ruta\a\tu\proyecto" -AuditarArchivo "src/db/database.js"
  ```
* **Levantar el Servidor MCP + Telemetría en Tiempo Real (`http://127.0.0.1:8080/planet`)**:
  ```powershell
  .\iniciar-planeta-ecc.ps1 -Proyecto "C:\ruta\a\tu\proyecto" -ServidorEnVivo
  ```

---

## 📂 Estructura del Repositorio

```text
├── graphify-8/                         # Motor AST (tree-sitter), exportador Planeta 360°/2D y servidor MCP/SSE
│   ├── graphify/exporters/planet.py    # Motor visual 3D/2D + Recomendador y Catálogo de 65+ Agentes ECC
│   ├── graphify/serve.py               # Servidor MCP (blast_radius) + Stream SSE (/events, /planet)
│   └── tests/                          # Suite de pruebas pytest (82 tests)
├── ECC-main/                           # Kit de Agentes, Comandos, Reglas y Hooks (Everything Claude Code)
│   ├── agents/                         # 70+ definiciones de agentes especializados (.md)
│   ├── commands/                       # 95+ comandos slash y flujos de orquestación (.md)
│   ├── scripts/lib/graphify-bridge.js  # Puente ultrarrápido (<5ms) entre ECC Hooks y graph.json
│   ├── scripts/hooks/                  # GateGuard (gateguard-fact-force.js), SessionStart y PostToolUse
│   └── tests/hooks/                    # Suite de pruebas de integración ECC × Graphify
├── iniciar-planeta-ecc.ps1             # Lanzador unificado (Análisis por capas, Auditoría y Servidor Vivo)
├── Iniciar-Planeta-360.bat             # Acceso directo para Windows CMD / Doble clic
├── CONTRIBUTING.md                     # Guía paso a paso para colaboradores open source
└── LICENSE                             # Licencia MIT / Apache-2.0
```

---

## 📜 Bitácora Técnica Completa (Rama `argon` — Todo lo construido sin omitir nada)

### 1. En el motor Graphify (`graphify-8/`)
* **[`graphify/exporters/planet.py`](graphify-8/graphify/exporters/planet.py) *(NUEVO)***:
  * **Motor Esférico 360° Vivo**: Proyección 3D con distribución esférica de Fibonacci (Golden Angle) para separar cada comunidad en un Continente Arquitectónico sobre el globo, con rotación 360° libre (mouse drag + inercia + zoom), arcos geodésicos curvos, partículas de flujo en tiempo real (`calls`, `imports`, `references`) y ondas de choque (`shockwaves`) cuando un nodo es inspeccionado o auditado.
  * **HUD Persistente en 3D y 2D (`#planet-hud`)**: Montado de forma persistente sobre el lienzo para que funcione exactamente igual tanto en el **Planeta 360° Vivo** como en el **Mapa 2D Limpio (`vis.Network`)**.
  * **Control de Nivel de Claridad (LOD)**: Filtro sincronizado en 3D y 2D con 3 modos: `🏛️ Solo Archivos` (por defecto, promueve un nodo principal por archivo para eliminar el ruido de funciones internas), `+ 🧪 Tests` y `🔬 Todo el AST`.
  * **Filtro de Conexiones Limpias**: Modo `🎯 Líneas: Solo Nodo Activo` activado por defecto para evitar la saturación visual ("bola de pelos") y mostrar únicamente las aristas entrantes y salientes del nodo seleccionado.
  * **Barra de Nodos Principales (`🧭 ¿Por dónde empezar?`)**: Detecta y muestra los 6 hubs arquitectónicos con mayor grado de conexión para iniciar el recorrido con un clic.
  * **Explorador Interactivo "A. Todo lo que toca este Nodo" (4 pestañas)**:
    1. `📥 Impacto Directo` (BFS inverso de quién importa/llama a este nodo).
    2. `📤 Toca / Usa` (dependencias salientes que este nodo consume).
    3. `🧪 Tests` (archivos `.spec` / `.test` conectados directa o indirectamente).
    4. `⚙️ Internos` (funciones, clases y métodos declarados dentro del mismo `source_file`).
  * **Catálogo Completo + Recomendador Contextual "B. Agentes y Herramientas ECC"**:
    * Integra un catálogo (`ECC_CATALOG`) de **más de 60 agentes, comandos slash y hooks reales de ECC Tools** organizados en 8 vistas (`⭐ Recomendados`, `🧠 Arquitectura`, `🎨 UI/Vue/Web`, `🗄️ BD/Seguridad/Red`, `🔍 Revisión/Refactor`, `🧪 Tests/Build`, `🚀 Orquestación`, `📋 Todos`) más buscador instantáneo (`#ecc-agent-search`).
    * Motor `getRecommendedToolsForNode(pNode, stats)` que inspecciona extensión (`.vue`, `.jsx`, `.py`, `.ts`, `.sql`, `.md`, etc.), ruta (`views`, `components`, `db`, `queries`, `services`, `composables`, `auth`), radio de impacto (`stats.d1`), cobertura de pruebas (`stats.tests`) y complejidad interna (`stats.fileSymbols`) para recomendar automáticamente los agentes ideales indicando **la razón exacta**.
    * Generador dinámico `buildEccToolContent` que construye el prompt completo con contexto AST real (archivos dependientes, dependencias salientes, símbolos internos y suites de prueba) y ofrece doble botón de copiado (`📋 Copiar Prompt con Contexto del Nodo` y `⚡ Copiar Comando Corto`).
* **[`graphify/exporters/html.py`](graphify-8/graphify/exporters/html.py) y [`graphify/export.py`](graphify-8/graphify/export.py) *(MODIFICADOS)***:
  * Inyección de `_planet_styles()` y `_planet_script()` en el exportador HTML y exposición de `to_planet_html()` para generar `planet.html` con el modo Planeta 360° activo de fábrica.
* **[`graphify/serve.py`](graphify-8/graphify/serve.py) *(MODIFICADO)***:
  * Nueva herramienta MCP `blast_radius` respaldada por `graphify.affected.affected_by_file` / `affected_by_nodes`, que devuelve a cualquier agente IA el radio de impacto exacto (distancia 1, distancia 2 y tests afectados).
  * Buffer de eventos en vivo (`_publish_live_event`) y nuevos endpoints HTTP: `GET /planet` (sirve el Planeta 360° conectado en vivo) y `GET /events` (stream Server-Sent Events SSE que ilumina los nodos en tiempo real cuando un agente consulta el MCP).
* **[`tests/test_planet_and_blast_mcp.py`](graphify-8/tests/test_planet_and_blast_mcp.py) *(NUEVO)***:
  * Suite de pruebas automatizadas que valida la exportación de `planet.html`, la ejecución del motor 3D/2D y del recomendador de agentes en Node.js headless, la herramienta MCP `blast_radius` y los endpoints `/planet` y `/events` (82 tests pasando en conjunto con `test_export.py`).

### 2. En ECC Tools (`ECC-main/`)
* **[`scripts/lib/graphify-bridge.js`](ECC-main/scripts/lib/graphify-bridge.js) *(NUEVO)***:
  * Puente nativo en Node.js sin dependencias pesadas que localiza y cachea `graphify-out/graph.json` por `mtimeMs` (lectura en `<5ms`).
  * Calcula determinísticamente `queryFileBlastRadius(filePath, { cwd })` (símbolos del archivo, dependientes directos D1, dependientes indirectos D2, tests asociados y comunidades cruzadas).
  * Provee `getSessionStartGraphSummary` y `recordPendingGraphChange`.
* **[`scripts/hooks/gateguard-fact-force.js`](ECC-main/scripts/hooks/gateguard-fact-force.js) *(MODIFICADO)***:
  * Conecta la compuerta `PreToolUse` de GateGuard con `graphify-bridge.js` para inyectar el bloque `[Graphify Live AST]` con los dependientes reales y tests afectados cuando un agente intenta editar o escribir un archivo sin haber investigado antes.
* **[`scripts/lib/gateguard-turn-scan.js`](ECC-main/scripts/lib/gateguard-turn-scan.js) y [`scripts/lib/gateguard-search-evidence.js`](ECC-main/scripts/lib/gateguard-search-evidence.js) *(MODIFICADOS)***:
  * Reconocen las herramientas `mcp__graphify__*` y los comandos CLI `graphify query|affected|explain|path` como evidencia válida de investigación previa en GateGuard.
* **[`scripts/hooks/session-start.js`](ECC-main/scripts/hooks/session-start.js) y [`scripts/hooks/post-edit-accumulator.js`](ECC-main/scripts/hooks/post-edit-accumulator.js) *(MODIFICADOS)***:
  * Al iniciar sesión (`SessionStart`), inyecta el resumen cartográfico del grafo (`nodos`, `aristas`, `comunidades`).
  * Tras cada edición (`PostToolUse`), registra los archivos modificados en `.graphify_pending_changes.jsonl`.
* **[`mcp-configs/mcp-servers.json`](ECC-main/mcp-configs/mcp-servers.json), [`agents/planner.md`](ECC-main/agents/planner.md) y [`agents/code-reviewer.md`](ECC-main/agents/code-reviewer.md) *(MODIFICADOS)***:
  * Registro oficial del servidor MCP `graphify` y actualización de los agentes `planner` y `code-reviewer` para consultar `blast_radius` antes de planificar o aprobar cambios.
* **[`tests/hooks/gateguard-graphify-bridge.test.js`](ECC-main/tests/hooks/gateguard-graphify-bridge.test.js) *(NUEVO)***:
  * Suite de pruebas de integración que verifica el cálculo de radio de explosión, bloqueo informativo de GateGuard, acreditación de herramientas `mcp__graphify__*`, inyección en `SessionStart` y registro en `PostToolUse` (6/6 tests en verde + 1,104 aserciones de GateGuard pasando).

### 3. En la Raíz del Ecosistema Unificado
* **[`iniciar-planeta-ecc.ps1`](iniciar-planeta-ecc.ps1) e [`Iniciar-Planeta-360.bat`](Iniciar-Planeta-360.bat) *(NUEVOS)***:
  * Lanzador todo-en-uno que analiza el AST de cualquier proyecto, filtra bundles/assets minificados, organiza los nodos en **8 Continentes Arquitectónicos legibles** (`Vistas`, `Lógica/Composables`, `Base de Datos`, `Componentes UI`, `Servicios`, `Tests`, `Documentación`, `Core`), exporta `graph.json`, `graph.html` y `planet.html`, permite auditar archivos con GateGuard (`-AuditarArchivo`) y levantar el servidor MCP+SSE en vivo (`-ServidorEnVivo`).

---

## 🤝 Cómo Contribuir

¡Las contribuciones de la comunidad son bienvenidas! Lee nuestra [**Guía de Contribución (`CONTRIBUTING.md`)**](CONTRIBUTING.md) para ver cómo añadir nuevos agentes al recomendador, soportar más capas de frameworks o mejorar el motor 3D/2D.

