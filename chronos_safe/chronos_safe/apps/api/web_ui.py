"""Web dashboard helpers."""

from __future__ import annotations

from pathlib import Path

from chronos_safe.config.settings import SETTINGS


def _relative_paths(root: Path, patterns: tuple[str, ...]) -> list[str]:
    results: list[str] = []
    for pattern in patterns:
        for path in sorted(root.rglob(pattern)):
            if path.is_file():
                results.append(path.relative_to(root).as_posix())
    return results


def build_catalog_payload() -> dict[str, object]:
    return {
        "fixtures": _relative_paths(SETTINGS.data_root / "fixtures", ("*.json",)),
        "processed_datasets": sorted(
            [
                path.relative_to(SETTINGS.project_root).as_posix()
                for path in (SETTINGS.data_root / "processed").glob("*")
                if path.is_dir()
            ]
        ),
        "checkpoints": _relative_paths(SETTINGS.models_root / "checkpoints", ("*.pt",)),
        "scalers": _relative_paths(SETTINGS.models_root / "checkpoints", ("scaler.json",)),
        "ood_guards": _relative_paths(SETTINGS.models_root / "checkpoints", ("ood_guard.json",)),
        "reports": _relative_paths(SETTINGS.reports_root / "validation", ("*.json", "*.txt")),
        "defaults": {
            "generalist_dataset_dir": str((SETTINGS.data_root / "processed" / "generalist").as_posix()),
            "specialist_dataset_dir": str((SETTINGS.data_root / "processed" / "specialist").as_posix()),
            "generalist_checkpoint_dir": str((SETTINGS.models_root / "checkpoints" / "generalist").as_posix()),
            "specialist_checkpoint_dir": str((SETTINGS.models_root / "checkpoints" / "specialist").as_posix()),
            "simulation_output_path": str((SETTINGS.reports_root / "validation" / "simulation.json").as_posix()),
            "default_fixture": "apophis/apophis_fixture.json",
        },
    }


def render_dashboard_html() -> str:
    return """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CHRONOS-SAFE Control Center</title>
  <style>
    :root {
      --bg: #f4efe6;
      --panel: rgba(255, 250, 242, 0.92);
      --panel-strong: #fff8ef;
      --ink: #1d2227;
      --muted: #666f78;
      --line: rgba(25, 32, 40, 0.12);
      --accent: #0f7a5c;
      --accent-2: #c76725;
      --danger: #a8362f;
      --shadow: 0 18px 50px rgba(28, 34, 41, 0.12);
      --radius: 18px;
      --mono: "Consolas", "SFMono-Regular", monospace;
      --serif: "Georgia", "Times New Roman", serif;
      --sans: "Segoe UI", "Trebuchet MS", sans-serif;
    }

    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: var(--sans);
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(15, 122, 92, 0.18), transparent 30%),
        radial-gradient(circle at top right, rgba(199, 103, 37, 0.18), transparent 32%),
        linear-gradient(180deg, #f7f1e6 0%, #efe5d5 100%);
      min-height: 100vh;
    }

    .shell {
      width: min(1200px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 28px 0 40px;
    }

    .hero {
      display: grid;
      grid-template-columns: 1.2fr 0.8fr;
      gap: 20px;
      margin-bottom: 22px;
    }

    .hero-card, .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      backdrop-filter: blur(8px);
    }

    .hero-card {
      padding: 28px;
      position: relative;
      overflow: hidden;
    }

    .hero-card::after {
      content: "";
      position: absolute;
      inset: auto -30px -30px auto;
      width: 180px;
      height: 180px;
      background: linear-gradient(135deg, rgba(15, 122, 92, 0.18), rgba(199, 103, 37, 0.18));
      border-radius: 50%;
      filter: blur(4px);
    }

    h1, h2 {
      margin: 0;
      font-family: var(--serif);
      font-weight: 700;
      letter-spacing: -0.03em;
    }

    h1 { font-size: clamp(2rem, 5vw, 3.6rem); line-height: 0.95; }
    h2 { font-size: 1.2rem; margin-bottom: 14px; }

    .subtitle {
      color: var(--muted);
      max-width: 62ch;
      margin-top: 14px;
      line-height: 1.55;
    }

    .badge-row {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-top: 18px;
    }

    .badge {
      padding: 8px 12px;
      border-radius: 999px;
      font-size: 0.88rem;
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.65);
    }

    .stats {
      padding: 24px;
      display: grid;
      gap: 12px;
      align-content: start;
    }

    .stat {
      background: var(--panel-strong);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 14px 16px;
    }

    .stat strong {
      display: block;
      font-size: 1.35rem;
      margin-top: 6px;
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 18px;
    }

    .panel {
      padding: 20px;
    }

    form {
      display: grid;
      gap: 12px;
    }

    .row {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }

    label {
      display: grid;
      gap: 6px;
      font-size: 0.92rem;
      color: var(--muted);
    }

    input, select, button, textarea {
      width: 100%;
      border-radius: 12px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.95);
      padding: 11px 12px;
      font: inherit;
      color: var(--ink);
    }

    textarea {
      min-height: 320px;
      resize: vertical;
      font-family: var(--mono);
      font-size: 0.88rem;
      background: #10161d;
      color: #dfe8ef;
      border-color: #26303a;
    }

    button {
      border: none;
      background: linear-gradient(135deg, var(--accent), #127b8f);
      color: white;
      font-weight: 700;
      cursor: pointer;
      transition: transform 160ms ease, opacity 160ms ease;
    }

    button.secondary {
      background: linear-gradient(135deg, var(--accent-2), #d28f3b);
    }

    button:hover { transform: translateY(-1px); }
    button:disabled { opacity: 0.55; cursor: wait; transform: none; }

    .toolbar {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-bottom: 10px;
    }

    .hint {
      color: var(--muted);
      font-size: 0.88rem;
      line-height: 1.45;
      margin-top: 8px;
    }

    .status {
      font-family: var(--mono);
      font-size: 0.88rem;
      padding: 10px 12px;
      border-radius: 12px;
      background: rgba(15, 122, 92, 0.08);
      border: 1px solid rgba(15, 122, 92, 0.16);
      color: #0d5a44;
      margin-bottom: 12px;
      white-space: pre-wrap;
    }

    @media (max-width: 980px) {
      .hero, .grid, .row {
        grid-template-columns: 1fr;
      }
      .shell {
        width: min(100vw - 18px, 1200px);
      }
    }
  </style>
</head>
<body>
  <div class="shell">
    <section class="hero">
      <div class="hero-card">
        <p style="margin:0 0 10px;color:var(--accent);font-weight:700;letter-spacing:0.12em;text-transform:uppercase;">Control Center</p>
        <h1>CHRONOS-SAFE</h1>
        <p class="subtitle">
          Interface visual para gerar datasets, treinar o residual GNN, rodar simulação híbrida e validar o cenário Apophis sem depender do terminal.
        </p>
        <div class="badge-row">
          <span class="badge">REBOUND fallback</span>
          <span class="badge">Residual GNN</span>
          <span class="badge">Safety guard</span>
          <span class="badge">Offline fixtures</span>
        </div>
      </div>
      <aside class="hero-card stats">
        <div class="stat">
          <span>Health</span>
          <strong id="health-value">loading...</strong>
        </div>
        <div class="stat">
          <span>Fixtures detectados</span>
          <strong id="fixtures-count">0</strong>
        </div>
        <div class="stat">
          <span>Checkpoints detectados</span>
          <strong id="checkpoints-count">0</strong>
        </div>
      </aside>
    </section>

    <div class="grid">
      <section class="panel">
        <h2>1. Gerar Datasets</h2>
        <div class="row">
          <form id="generalist-form">
            <label>Saída
              <input type="text" name="output_dir" data-fill="generalist_dataset_dir">
            </label>
            <div class="row">
              <label>Amostras
                <input type="number" name="num_samples" value="128" min="1">
              </label>
              <label>dt (dias)
                <input type="number" name="dt_days" value="1.0" min="0.01" step="0.01">
              </label>
            </div>
            <div class="row">
              <label>Min corpos
                <input type="number" name="min_bodies" value="2" min="2">
              </label>
              <label>Max corpos
                <input type="number" name="max_bodies" value="6" min="2">
              </label>
            </div>
            <button type="submit">Gerar Generalista</button>
          </form>

          <form id="specialist-form">
            <label>Saída
              <input type="text" name="output_dir" data-fill="specialist_dataset_dir">
            </label>
            <label>Fixture
              <select name="fixture_name" data-select="fixtures"></select>
            </label>
            <div class="row">
              <label>Amostras
                <input type="number" name="num_samples" value="64" min="1">
              </label>
              <label>dt (dias)
                <input type="number" name="dt_days" value="1.0" min="0.01" step="0.01">
              </label>
            </div>
            <button type="submit" class="secondary">Gerar Especialista</button>
          </form>
        </div>
        <p class="hint">Os datasets são persistidos em `NPZ + JSON` e reaparecem automaticamente na interface após atualização do catálogo.</p>
      </section>

      <section class="panel">
        <h2>2. Treinar Modelos</h2>
        <div class="row">
          <form id="train-generalist-form">
            <label>Dataset generalista
              <input type="text" name="dataset_dir" data-fill="generalist_dataset_dir">
            </label>
            <label>Saída do checkpoint
              <input type="text" name="output_dir" data-fill="generalist_checkpoint_dir">
            </label>
            <div class="row">
              <label>Épocas
                <input type="number" name="epochs" value="10" min="1">
              </label>
              <label>Batch
                <input type="number" name="batch_size" value="8" min="1">
              </label>
            </div>
            <button type="submit">Treinar Generalista</button>
          </form>

          <form id="train-specialist-form">
            <label>Dataset especialista
              <input type="text" name="dataset_dir" data-fill="specialist_dataset_dir">
            </label>
            <label>Saída do checkpoint
              <input type="text" name="output_dir" data-fill="specialist_checkpoint_dir">
            </label>
            <div class="row">
              <label>Épocas
                <input type="number" name="epochs" value="6" min="1">
              </label>
              <label>Batch
                <input type="number" name="batch_size" value="8" min="1">
              </label>
            </div>
            <button type="submit" class="secondary">Treinar Especialista</button>
          </form>
        </div>
        <p class="hint">A interface usa as mesmas rotas da CLI. Se `torch` não estiver instalado, o backend retorna erro explícito.</p>
      </section>

      <section class="panel">
        <h2>3. Simulação Híbrida</h2>
        <form id="simulate-form">
          <div class="row">
            <label>Fixture
              <select name="fixture_name" data-select="fixtures"></select>
            </label>
            <label>Passos
              <input type="number" name="steps" value="30" min="1">
            </label>
          </div>
          <div class="row">
            <label>dt (dias)
              <input type="number" name="dt_days" value="1.0" min="0.01" step="0.01">
            </label>
            <label>Checkpoint
              <select name="checkpoint_path" data-select="checkpoints" data-allow-empty="true"></select>
            </label>
          </div>
          <div class="row">
            <label>Scaler
              <select name="scaler_path" data-select="scalers" data-allow-empty="true"></select>
            </label>
            <label>OOD guard
              <select name="ood_guard_path" data-select="ood_guards" data-allow-empty="true"></select>
            </label>
          </div>
          <button type="submit">Rodar Simulação</button>
        </form>
      </section>

      <section class="panel">
        <h2>4. Validação Apophis</h2>
        <form id="apophis-form">
          <div class="row">
            <label>Passos
              <input type="number" name="steps" value="180" min="1">
            </label>
            <label>dt (dias)
              <input type="number" name="dt_days" value="1.0" min="0.01" step="0.01">
            </label>
          </div>
          <div class="row">
            <label>Checkpoint
              <select name="checkpoint_path" data-select="checkpoints" data-allow-empty="true"></select>
            </label>
            <label>Scaler
              <select name="scaler_path" data-select="scalers" data-allow-empty="true"></select>
            </label>
          </div>
          <div class="row">
            <label>OOD guard
              <select name="ood_guard_path" data-select="ood_guards" data-allow-empty="true"></select>
            </label>
            <div></div>
          </div>
          <button type="submit" class="secondary">Validar Apophis</button>
        </form>
      </section>
    </div>

    <section class="panel" style="margin-top:18px;">
      <div class="toolbar">
        <button id="refresh-button" type="button">Atualizar Catálogo</button>
        <button id="health-button" type="button" class="secondary">Revalidar Health</button>
      </div>
      <div id="status-box" class="status">Pronto.</div>
      <textarea id="output-box" readonly>{}</textarea>
    </section>
  </div>

  <script>
    const state = { catalog: null };

    function setStatus(message) {
      document.getElementById("status-box").textContent = message;
    }

    function setOutput(payload) {
      const text = typeof payload === "string" ? payload : JSON.stringify(payload, null, 2);
      document.getElementById("output-box").value = text;
    }

    function fillDefaults(catalog) {
      document.querySelectorAll("[data-fill]").forEach((input) => {
        const key = input.getAttribute("data-fill");
        if (catalog.defaults[key]) {
          input.value = catalog.defaults[key];
        }
      });
    }

    function fillSelects(catalog) {
      document.querySelectorAll("[data-select]").forEach((select) => {
        const key = select.getAttribute("data-select");
        const allowEmpty = select.getAttribute("data-allow-empty") === "true";
        const values = catalog[key] || [];
        select.innerHTML = "";
        if (allowEmpty) {
          const empty = document.createElement("option");
          empty.value = "";
          empty.textContent = "(nenhum)";
          select.appendChild(empty);
        }
        values.forEach((value) => {
          const option = document.createElement("option");
          option.value = key === "fixtures" ? value : value.startsWith("models/") || value.startsWith("data/") || value.startsWith("reports/") ? value : `${key === "checkpoints" || key === "scalers" || key === "ood_guards" ? "models/checkpoints/" : ""}${value}`;
          option.textContent = value;
          select.appendChild(option);
        });
        if (!allowEmpty && values.length === 0) {
          const option = document.createElement("option");
          option.value = "";
          option.textContent = "(vazio)";
          select.appendChild(option);
        }
      });
      document.getElementById("fixtures-count").textContent = String((catalog.fixtures || []).length);
      document.getElementById("checkpoints-count").textContent = String((catalog.checkpoints || []).length);
    }

    async function loadHealth() {
      const response = await fetch("/health");
      const payload = await response.json();
      document.getElementById("health-value").textContent = `${payload.status} v${payload.version}`;
      return payload;
    }

    async function loadCatalog() {
      const response = await fetch("/ui/catalog");
      const payload = await response.json();
      state.catalog = payload;
      fillDefaults(payload);
      fillSelects(payload);
      return payload;
    }

    async function callApi(url, body, button) {
      try {
        button.disabled = true;
        setStatus(`Executando ${url}...`);
        const response = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });
        const payload = await response.json();
        setOutput(payload);
        if (!response.ok) {
          throw new Error(payload.detail || `Falha HTTP ${response.status}`);
        }
        setStatus(`Concluido: ${url}`);
        await loadCatalog();
      } catch (error) {
        setStatus(`Erro: ${error.message}`);
      } finally {
        button.disabled = false;
      }
    }

    function formToObject(form) {
      const data = new FormData(form);
      const payload = {};
      for (const [key, value] of data.entries()) {
        if (value === "") {
          payload[key] = null;
          continue;
        }
        if (["num_samples", "min_bodies", "max_bodies", "epochs", "batch_size", "steps"].includes(key)) {
          payload[key] = Number(value);
        } else if (["dt_days"].includes(key)) {
          payload[key] = Number(value);
        } else {
          payload[key] = value;
        }
      }
      return payload;
    }

    function bindForm(id, url) {
      const form = document.getElementById(id);
      form.addEventListener("submit", async (event) => {
        event.preventDefault();
        await callApi(url, formToObject(form), form.querySelector("button[type='submit']"));
      });
    }

    document.getElementById("refresh-button").addEventListener("click", async () => {
      setStatus("Atualizando catalogo...");
      await loadCatalog();
      setStatus("Catalogo atualizado.");
    });

    document.getElementById("health-button").addEventListener("click", async () => {
      setStatus("Validando health...");
      const payload = await loadHealth();
      setOutput(payload);
      setStatus("Health atualizado.");
    });

    bindForm("generalist-form", "/generate/generalist");
    bindForm("specialist-form", "/generate/specialist");
    bindForm("train-generalist-form", "/train/generalist");
    bindForm("train-specialist-form", "/train/specialist");
    bindForm("simulate-form", "/simulate");
    bindForm("apophis-form", "/validate/apophis");

    (async () => {
      try {
        await loadHealth();
        const catalog = await loadCatalog();
        setOutput(catalog);
        setStatus("Interface pronta.");
      } catch (error) {
        setStatus(`Falha ao inicializar interface: ${error.message}`);
      }
    })();
  </script>
</body>
</html>
"""
