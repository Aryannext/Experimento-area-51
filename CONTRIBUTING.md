# 🤝 Guía de Contribución — ECC × Graphify (Planeta 360° Vivo)

¡Gracias por tu interés en mejorar **ECC × Graphify**! Este proyecto es 100% gratuito y open source, diseñado para que cualquier desarrollador pueda visualizar la arquitectura de sus proyectos como un **Planeta 360° Vivo** y potenciar sus agentes de IA con el catálogo completo de **ECC Tools**.

---

## 🛠️ Requisitos del Entorno de Desarrollo

1. **Python 3.10+** y **[uv](https://docs.astral.sh/uv/)** (para el motor AST de Graphify y el servidor MCP/SSE).
2. **Node.js 18+** (para los hooks de ECC Tools, GateGuard y el puente en tiempo real con `graph.json`).
3. **Git** instalado.

---

## 🚀 Cómo levantar el proyecto localmente para desarrollar

1. **Haz un Fork** de este repositorio en GitHub y clónalo en la rama `argon`:
   ```bash
   git clone -b argon https://github.com/Aryannext/Experimento-area-51.git
   cd Experimento-area-51
   ```

2. **Sincroniza el entorno de Graphify (`graphify-8`)**:
   ```powershell
   cd graphify-8
   uv sync --extra mcp
   cd ..
   ```

3. **Ejecuta las pruebas automatizadas antes de enviar cambios**:
   * **Pruebas del Planeta 360°, Exportador HTML/2D y Servidor MCP (`graphify-8`)**:
     ```powershell
     cd graphify-8
     uv run --extra mcp pytest tests/test_export.py tests/test_planet_and_blast_mcp.py -q
     ```
   * **Pruebas del Puente ECC GateGuard × Graphify (`ECC-main`)**:
     ```powershell
     cd ECC-main
     node tests/hooks/gateguard-graphify-bridge.test.js
     ```

---

## 🌟 ¿En qué puedes contribuir?

1. **Nuevos Agentes y Reglas de Recomendación Contextual**:
   * El catálogo interactivo (`ECC_CATALOG`) y el motor de recomendación por nodo (`getRecommendedToolsForNode`) viven en [`graphify-8/graphify/exporters/planet.py`](graphify-8/graphify/exporters/planet.py).
   * Los prompts base de los agentes viven en [`ECC-main/agents/`](ECC-main/agents/) y los comandos en [`ECC-main/commands/`](ECC-main/commands/).
2. **Nuevos Continentes / Capas Arquitectónicas**:
   * Puedes mejorar las heurísticas de agrupación por capas en [`iniciar-planeta-ecc.ps1`](iniciar-planeta-ecc.ps1) para soportar más frameworks (Next.js, NestJS, Django, Laravel, Spring Boot, Flutter, Rust, Go).
3. **Visualización 3D / 2D y Telemetría en Tiempo Real**:
   * Mejoras de rendimiento en Canvas/WebGL, filtros adicionales o integración directa con más IDEs mediante SSE (`/events`).

---

## 📬 Flujo para enviar un Pull Request (PR)

1. Crea una rama descriptiva:
   ```bash
   git checkout -b feat/nombre-de-tu-mejora
   ```
2. Realiza tus cambios y verifica que los tests en `graphify-8` y `ECC-main` pasen en verde.
3. Haz commit siguiendo un formato claro:
   ```bash
   git commit -m "feat(planet): agregar soporte para agentes de Laravel y Rust"
   ```
4. Sube tu rama y abre un **Pull Request**:
   ```bash
   git push origin feat/nombre-de-tu-mejora
   ```
