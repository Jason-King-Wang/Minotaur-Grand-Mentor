(function () {
  "use strict";

  const DEFAULT_STATE = {
    project: "Minotaur Grand Mentor",
    version: "0.1.0",
    current_phase: "pngtuber-mvp",
    overall_status: "Open through a local server or GitHub Pages for live JSON loading.",
    completed_tasks: [],
    pending_tasks: [
      "Generate idle_closed.png",
      "Generate talk_open.png",
      "Generate blink_closed.png",
      "Generate happy.png",
      "Run validate_assets.py",
      "Test overlay in OBS"
    ],
    missing_assets: [
      "assets/avatar/pngtuber/idle_closed.png",
      "assets/avatar/pngtuber/talk_open.png",
      "assets/avatar/pngtuber/blink_closed.png",
      "assets/avatar/pngtuber/happy.png"
    ],
    last_updated: "not loaded",
    notes: "Fallback state is displayed because JSON fetch is unavailable in this context."
  };

  const DEFAULT_MANIFEST = {
    required_assets: [
      { id: "idle_closed", path: "assets/avatar/pngtuber/idle_closed.png", required: true },
      { id: "talk_open", path: "assets/avatar/pngtuber/talk_open.png", required: true },
      { id: "blink_closed", path: "assets/avatar/pngtuber/blink_closed.png", required: true },
      { id: "happy", path: "assets/avatar/pngtuber/happy.png", required: true }
    ],
    optional_assets: [
      { id: "angry", path: "assets/avatar/pngtuber/angry.png", required: false },
      { id: "thinking", path: "assets/avatar/pngtuber/thinking.png", required: false },
      { id: "gesture_point", path: "assets/avatar/pngtuber/gesture_point.png", required: false },
      { id: "shock", path: "assets/avatar/pngtuber/shock.png", required: false }
    ]
  };

  const stateList = document.getElementById("stateList");
  const missingAssets = document.getElementById("missingAssets");
  const completedTasks = document.getElementById("completedTasks");
  const pendingTasks = document.getElementById("pendingTasks");
  const assetChecklist = document.getElementById("assetChecklist");
  const runLogs = document.getElementById("runLogs");

  async function loadJson(path, fallback) {
    try {
      const response = await fetch(path, { cache: "no-store" });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.warn(`Using fallback for ${path}`, error);
      return fallback;
    }
  }

  function renderList(element, values, emptyText) {
    element.innerHTML = "";
    const items = values && values.length ? values : [emptyText];
    for (const value of items) {
      const li = document.createElement("li");
      li.textContent = value;
      element.appendChild(li);
    }
  }

  function renderState(state) {
    stateList.innerHTML = "";
    const rows = {
      Project: state.project,
      Version: state.version,
      Phase: state.current_phase,
      Status: state.overall_status,
      Updated: state.last_updated,
      Notes: state.notes
    };
    for (const [label, value] of Object.entries(rows)) {
      const dt = document.createElement("dt");
      const dd = document.createElement("dd");
      dt.textContent = label;
      dd.textContent = value || "not set";
      stateList.append(dt, dd);
    }
  }

  function renderAssets(manifest, missing) {
    assetChecklist.innerHTML = "";
    const allAssets = [
      ...(manifest.required_assets || []),
      ...(manifest.optional_assets || [])
    ];
    const missingSet = new Set(missing || []);
    for (const asset of allAssets) {
      const row = document.createElement("article");
      const status = missingSet.has(asset.path) ? "missing" : "pending-check";
      row.className = `asset-row ${status}`;
      row.innerHTML = `
        <strong>${asset.id}</strong>
        <span>${asset.required ? "Required" : "Optional"}</span>
        <code>${asset.path}</code>
      `;
      assetChecklist.appendChild(row);
    }
  }

  function renderLogs(entries) {
    runLogs.innerHTML = "";
    const items = entries && entries.length ? entries.slice().reverse().slice(0, 10) : [];
    if (!items.length) {
      const li = document.createElement("li");
      li.textContent = "No run logs yet.";
      runLogs.appendChild(li);
      return;
    }
    for (const entry of items) {
      const li = document.createElement("li");
      li.innerHTML = `
        <strong>${entry.phase || "Event"} · ${entry.status || "recorded"}</strong>
        <span>${entry.summary || entry.event || ""}</span>
        <small>${entry.timestamp || entry.date || ""}</small>
      `;
      runLogs.appendChild(li);
    }
  }

  async function boot() {
    const [state, manifest, runLogJson] = await Promise.all([
      loadJson("../data/project-state.json", DEFAULT_STATE),
      loadJson("../data/avatar-manifest.json", DEFAULT_MANIFEST),
      loadJson("../data/run-log.json", null)
    ]);

    const runLog = Array.isArray(runLogJson)
      ? runLogJson
      : (window.__MINOTAUR_RUN_LOG__ || []);

    renderState(state);
    renderList(missingAssets, state.missing_assets, "No missing required assets recorded.");
    renderList(completedTasks, state.completed_tasks, "No completed tasks recorded.");
    renderList(pendingTasks, state.pending_tasks, "No pending tasks recorded.");
    renderAssets(manifest, state.missing_assets);
    renderLogs(runLog);
  }

  boot();
})();

