(function () {
  "use strict";

  const bundle = window.__MINOTAUR_DASHBOARD_DATA__ || {};

  const DEFAULT_STATE = bundle.projectState || {
    project: "Minotaur Grand Mentor",
    version: "0.2.0",
    current_phase: "waiting_for_art",
    overall_status: "ready_waiting_for_art_assets",
    core_goal: "Complete engineering and wait for final art.",
    scope_lock: "Only modify files inside Minotaur-Grand-Mentor project root.",
    engineering_status: "done",
    documentation_status: "done",
    overlay_status: "placeholder_ready",
    dashboard_status: "ready",
    live2d_status: "spec_ready_waiting_for_art_and_rigging",
    completed_tasks: [],
    pending_tasks: [],
    missing_assets: [],
    blocked_by_art: [],
    blocked_by_rigging: [],
    last_updated: "not loaded",
    notes: []
  };

  const DEFAULT_MANIFEST = bundle.avatarManifest || { required_assets: [], optional_assets: [] };
  const DEFAULT_LIVE2D = bundle.live2dManifest || { required_final_files: [] };
  const DEFAULT_COMPONENTS = bundle.live2dComponentManifest || { status: {}, same_canvas_outputs: {} };
  const DEFAULT_STAGE_06_VALIDATION = bundle.stage06Validation || {};
  const DEFAULT_TASKS = bundle.taskBoard || { tasks: [] };

  const stateList = document.getElementById("stateList");
  const missingAssets = document.getElementById("missingAssets");
  const completedTasks = document.getElementById("completedTasks");
  const pendingTasks = document.getElementById("pendingTasks");
  const assetChecklist = document.getElementById("assetChecklist");
  const stage06State = document.getElementById("stage06State");
  const runLogs = document.getElementById("runLogs");

  async function loadJson(path, fallback) {
    try {
      const response = await fetch(path, { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.warn(`Using fallback for ${path}`, error);
      return fallback;
    }
  }

  function asArray(value) {
    return Array.isArray(value) ? value : value ? [String(value)] : [];
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
      Goal: state.core_goal,
      Scope: state.scope_lock,
      Engineering: state.engineering_status,
      Documentation: state.documentation_status,
      Overlay: state.overlay_status,
      Dashboard: state.dashboard_status,
      Live2D: state.live2d_status,
      Updated: state.last_updated,
      Notes: asArray(state.notes).join(" | ") || state.notes
    };
    for (const [label, value] of Object.entries(rows)) {
      const dt = document.createElement("dt");
      const dd = document.createElement("dd");
      dt.textContent = label;
      dd.textContent = value || "not set";
      stateList.append(dt, dd);
    }
  }

  function renderAssets(manifest, live2d, missing) {
    assetChecklist.innerHTML = "";
    const allAssets = [
      ...(manifest.required_assets || []),
      ...(manifest.optional_assets || []),
      ...(live2d.required_final_files || [])
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

  function renderStage06(componentManifest, validation) {
    if (!stage06State) return;
    stage06State.innerHTML = "";
    const status = componentManifest.status || {};
    const outputs = componentManifest.same_canvas_outputs || {};
    const pngValidation = componentManifest.png_validation || validation || {};
    const rows = {
      "PNGTuber": status.pngtuber,
      "Live2D Components": status.live2d_source_components,
      "Same Canvas Pack": status.same_canvas_layer_pack,
      "Visual Review": status.visual_review,
      "Final PSD": status.final_layered_model_psd,
      ".moc3": status.live2d_moc3,
      "Output Folder": outputs.output_folder || componentManifest.canvas_plan?.output_folder,
      "Output PNGs": outputs.count,
      "Canvas": outputs.canvas_size ? outputs.canvas_size.join("x") : "",
      "Validation": pngValidation.summary || ""
    };
    for (const [label, value] of Object.entries(rows)) {
      const dt = document.createElement("dt");
      const dd = document.createElement("dd");
      dt.textContent = label;
      dd.textContent = value || "pending";
      stage06State.append(dt, dd);
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

  function taskTitles(taskBoard, status) {
    return (taskBoard.tasks || [])
      .filter((task) => task.status === status)
      .map((task) => `${task.id}: ${task.title}`);
  }

  async function boot() {
    const [state, manifest, live2d, componentManifest, validation, taskBoard, runLogJson] = await Promise.all([
      loadJson("../data/project-state.json", DEFAULT_STATE),
      loadJson("../data/avatar-manifest.json", DEFAULT_MANIFEST),
      loadJson("../data/live2d-sourcekit-manifest.json", DEFAULT_LIVE2D),
      loadJson("../data/live2d-component-manifest.json", DEFAULT_COMPONENTS),
      loadJson("../data/stage-06-validation-report.json", DEFAULT_STAGE_06_VALIDATION),
      loadJson("../data/task-board.json", DEFAULT_TASKS),
      loadJson("../data/run-log.json", bundle.runLog || window.__MINOTAUR_RUN_LOG__ || [])
    ]);

    const runLog = Array.isArray(runLogJson)
      ? runLogJson
      : (bundle.runLog || window.__MINOTAUR_RUN_LOG__ || []);

    renderState(state);
    renderList(missingAssets, state.missing_assets, "No missing required assets recorded.");
    renderList(completedTasks, state.completed_tasks.length ? state.completed_tasks : taskTitles(taskBoard, "done"), "No completed tasks recorded.");
    renderList(pendingTasks, state.pending_tasks.length ? state.pending_tasks : [
      ...taskTitles(taskBoard, "waiting_for_art"),
      ...taskTitles(taskBoard, "waiting_for_rigging")
    ], "No pending tasks recorded.");
    renderAssets(manifest, live2d, state.missing_assets);
    renderStage06(componentManifest, validation);
    renderLogs(runLog);
  }

  boot();
})();
