window.__MINOTAUR_DASHBOARD_DATA__ = {
  "projectState": {
    "project": "Minotaur Grand Mentor",
    "version": "0.2.0",
    "mode": "engineering_until_art_missing",
    "current_phase": "pngtuber_mvp_ready",
    "overall_status": "pngtuber_mvp_ready_waiting_for_live2d_assets",
    "core_goal": "Complete all Codex-capable engineering, docs, dashboard, overlay, logging, and asset specs; leave only final art and Live2D rigging.",
    "scope_lock": "Only modify files inside Minotaur-Grand-Mentor project root. Do not modify other Obsidian content.",
    "engineering_status": "done",
    "documentation_status": "done",
    "overlay_status": "pngtuber_assets_ready",
    "dashboard_status": "ready",
    "live2d_status": "spec_ready_waiting_for_art_and_rigging",
    "completed_tasks": [
      "Phase 1: Created project scaffold",
      "Phase 2: Wrote project documentation",
      "Phase 3: Created data formats",
      "Phase 4: Implemented project tools",
      "Phase 5: Built PNGTuber overlay MVP",
      "Phase 6: Built static dashboard",
      "Phase 7: Ran project file tests",
      "Phase 8: Completed PNGTuber MVP initialization",
      "GitHub Upload: Prepared repository content for GitHub upload",
      "Final Handoff: Completed all non-art deliverables",
      "Blueprint Archive: Archived full v2 Codex blueprint",
      "PNGTuber Assets: Imported MVP PNGTuber assets",
      "PNGTuber Status Cleanup: Updated tasks after PNGTuber asset import",
      "GitHub Sync: Prepared PNGTuber asset sync"
    ],
    "pending_tasks": [
      "Test overlay/index.html in OBS Browser Source",
      "Confirm microphone mouth switching with overlay/index.html?debug=1",
      "Create Live2D final front master artwork",
      "Create Live2D layered PSD",
      "Send PSD and checklist to Live2D rigger"
    ],
    "missing_assets": [
      "assets/avatar/live2d/final/final_front_master.png",
      "assets/avatar/live2d/final/final_layered_model.psd"
    ],
    "blocked_by_art": [
      "Live2D final front master image",
      "Live2D final layered PSD"
    ],
    "blocked_by_rigging": [
      "Live2D Cubism rigging",
      ".moc3 export",
      "VTube Studio test"
    ],
    "last_updated": "2026-04-29T07:20:09+08:00",
    "notes": "Push imported PNGTuber assets and updated project status to GitHub main."
  },
  "taskBoard": {
    "columns": {
      "not_started": [],
      "in_progress": [],
      "done": [
        "scope-lock",
        "project-scaffold",
        "docs-system",
        "software-setup",
        "character-bible",
        "asset-spec",
        "image-prompts",
        "pngtuber-overlay",
        "dashboard",
        "logging-system",
        "asset-validator",
        "placeholder-generator",
        "obsidian-project-pages",
        "live2d-layer-spec",
        "live2d-rigger-checklist",
        "obs-setup-doc",
        "github-pages-doc",
        "tests",
        "final-report",
        "waiting-for-pngtuber-art"
      ],
      "waiting_for_art": [
        "waiting-for-live2d-art"
      ],
      "waiting_for_rigging": [
        "waiting-for-live2d-rigging"
      ],
      "blocked": []
    },
    "tasks": [
      {
        "id": "scope-lock",
        "title": "Create bottom lines and Obsidian scope lock",
        "status": "done",
        "owner": "codex",
        "acceptance": "docs/BOTTOM_LINES.md exists and states Codex cannot modify other Obsidian content."
      },
      {
        "id": "project-scaffold",
        "title": "Complete v2 project scaffold",
        "status": "done",
        "owner": "codex",
        "acceptance": "Required folders, root marker, docs, data, overlay, dashboard, tools, tests, and obsidian_project pages exist."
      },
      {
        "id": "docs-system",
        "title": "Write project documentation system",
        "status": "done",
        "owner": "codex",
        "acceptance": "Core docs describe project, safety rules, setup, acceptance criteria, and handoff."
      },
      {
        "id": "software-setup",
        "title": "Document software setup",
        "status": "done",
        "owner": "codex",
        "acceptance": "docs/SOFTWARE_SETUP.md covers engineering, art, and Live2D tools."
      },
      {
        "id": "character-bible",
        "title": "Define character bible",
        "status": "done",
        "owner": "codex",
        "acceptance": "docs/CHARACTER_BIBLE.md defines persona, voice, visuals, and boundaries."
      },
      {
        "id": "asset-spec",
        "title": "Define asset specifications",
        "status": "done",
        "owner": "codex",
        "acceptance": "docs/ASSET_SPEC.md covers PNGTuber and Live2D assets."
      },
      {
        "id": "image-prompts",
        "title": "Write image prompts",
        "status": "done",
        "owner": "codex",
        "acceptance": "docs/IMAGE_PROMPTS.md includes base, expression, negative, character sheet, and three-view prompts."
      },
      {
        "id": "pngtuber-overlay",
        "title": "Build PNGTuber overlay",
        "status": "done",
        "owner": "codex",
        "acceptance": "Overlay supports placeholder, mic volume, hotkeys, query params, blink, breathing, and debug panel."
      },
      {
        "id": "dashboard",
        "title": "Build static dashboard",
        "status": "done",
        "owner": "codex",
        "acceptance": "Dashboard reads JSON and JS fallback data."
      },
      {
        "id": "logging-system",
        "title": "Build logging system",
        "status": "done",
        "owner": "codex",
        "acceptance": "tools/log_event.py appends JSON logs and writes Markdown records."
      },
      {
        "id": "asset-validator",
        "title": "Build asset validator",
        "status": "done",
        "owner": "codex",
        "acceptance": "tools/validate_assets.py reports missing PNGTuber and Live2D assets without crashing."
      },
      {
        "id": "placeholder-generator",
        "title": "Build placeholder generator",
        "status": "done",
        "owner": "codex",
        "acceptance": "tools/generate_placeholder_assets.py creates engineering-only SVG placeholders."
      },
      {
        "id": "obsidian-project-pages",
        "title": "Create Obsidian project pages",
        "status": "done",
        "owner": "codex",
        "acceptance": "obsidian_project pages summarize home, bottom lines, task board, asset status, and next actions."
      },
      {
        "id": "live2d-layer-spec",
        "title": "Write Live2D layer spec",
        "status": "done",
        "owner": "codex",
        "acceptance": "docs/LIVE2D_LAYER_SPEC.md defines PSD layer groups and names."
      },
      {
        "id": "live2d-rigger-checklist",
        "title": "Write rigger checklist",
        "status": "done",
        "owner": "codex",
        "acceptance": "docs/LIVE2D_RIGGER_CHECKLIST.md defines handoff and delivery checks."
      },
      {
        "id": "obs-setup-doc",
        "title": "Write OBS setup doc",
        "status": "done",
        "owner": "codex",
        "acceptance": "docs/OBS_SETUP.md explains local, GitHub Pages, microphone, and hotkey setup."
      },
      {
        "id": "github-pages-doc",
        "title": "Write GitHub Pages setup doc",
        "status": "done",
        "owner": "codex",
        "acceptance": "docs/GITHUB_PAGES_SETUP.md explains dashboard and overlay publication."
      },
      {
        "id": "tests",
        "title": "Create project tests",
        "status": "done",
        "owner": "codex",
        "acceptance": "tests/test_project_files.py checks required files and JSON."
      },
      {
        "id": "final-report",
        "title": "Create final handoff",
        "status": "done",
        "owner": "codex",
        "acceptance": "docs/FINAL_HANDOFF.md explains completed work, missing art, and next steps."
      },
      {
        "id": "waiting-for-pngtuber-art",
        "title": "Final PNGTuber MVP art imported",
        "status": "done",
        "owner": "user",
        "acceptance": "Final PNGTuber expression PNG files are added to assets/avatar/pngtuber/."
      },
      {
        "id": "waiting-for-live2d-art",
        "title": "Waiting for final Live2D artwork and PSD",
        "status": "waiting_for_art",
        "owner": "user",
        "acceptance": "Final front master and layered PSD exist under assets/avatar/live2d/final/."
      },
      {
        "id": "waiting-for-live2d-rigging",
        "title": "Waiting for Live2D rigging",
        "status": "waiting_for_rigging",
        "owner": "rigger",
        "acceptance": "Live2D Cubism model and VTube Studio test are complete."
      }
    ]
  },
  "avatarManifest": {
    "project": "Minotaur Grand Mentor",
    "version": "0.2.0",
    "mode": "pngtuber-mvp",
    "required_assets": [
      {
        "id": "idle_closed",
        "path": "assets/avatar/pngtuber/idle_closed.png",
        "required": true,
        "description": "Neutral idle pose, mouth closed"
      },
      {
        "id": "talk_open",
        "path": "assets/avatar/pngtuber/talk_open.png",
        "required": true,
        "description": "Talking pose, mouth open"
      },
      {
        "id": "blink_closed",
        "path": "assets/avatar/pngtuber/blink_closed.png",
        "required": true,
        "description": "Blinking pose, eyes closed"
      },
      {
        "id": "happy",
        "path": "assets/avatar/pngtuber/happy.png",
        "required": true,
        "description": "Happy confident expression"
      }
    ],
    "optional_assets": [
      {
        "id": "angry",
        "path": "assets/avatar/pngtuber/angry.png",
        "required": false,
        "description": "Comedic angry expression"
      },
      {
        "id": "thinking",
        "path": "assets/avatar/pngtuber/thinking.png",
        "required": false,
        "description": "Thinking expression"
      },
      {
        "id": "gesture_point",
        "path": "assets/avatar/pngtuber/gesture_point.png",
        "required": false,
        "description": "Pointing mentor pose"
      },
      {
        "id": "shock",
        "path": "assets/avatar/pngtuber/shock.png",
        "required": false,
        "description": "Shocked reaction"
      }
    ]
  },
  "live2dManifest": {
    "project": "Minotaur Grand Mentor",
    "version": "0.2.0",
    "mode": "live2d-source-prep",
    "status": "waiting_for_final_art_and_layered_psd",
    "required_final_files": [
      {
        "id": "final_front_master",
        "path": "assets/avatar/live2d/final/final_front_master.png",
        "required": true,
        "description": "Final front-facing master artwork"
      },
      {
        "id": "final_layered_psd",
        "path": "assets/avatar/live2d/final/final_layered_model.psd",
        "required": true,
        "description": "Final layered PSD for Live2D rigging"
      }
    ],
    "required_layers": [
      "torso_jacket",
      "neck",
      "head_base",
      "muzzle",
      "nose",
      "front_hair",
      "back_hair",
      "left_horn",
      "right_horn",
      "left_ear",
      "right_ear",
      "left_eye_white",
      "left_iris",
      "left_pupil",
      "left_upper_eyelid",
      "left_lower_eyelid",
      "right_eye_white",
      "right_iris",
      "right_pupil",
      "right_upper_eyelid",
      "right_lower_eyelid",
      "left_eyebrow",
      "right_eyebrow",
      "upper_lip",
      "lower_lip",
      "mouth_inner",
      "upper_teeth",
      "lower_teeth",
      "tongue",
      "jacket_body",
      "left_collar",
      "right_collar",
      "zipper"
    ]
  },
  "runLog": [
    {
      "timestamp": "2026-04-27T00:56:33+08:00",
      "phase": "Phase 1",
      "status": "done",
      "summary": "Created project scaffold",
      "details": "Verified the Minotaur Grand Mentor vault structure with docs, assets, overlay, dashboard, data, records, tools, and tests folders.",
      "next": "Proceed to documentation and data system setup.",
      "record": "records/2026-04-27/005633-phase-1.md"
    },
    {
      "timestamp": "2026-04-27T00:56:33+08:00",
      "phase": "Phase 2",
      "status": "done",
      "summary": "Wrote project documentation",
      "details": "Filled README, CODEX, project brief, character bible, style guide, asset spec, image prompts, OBS setup, Live2D upgrade notes, and next actions with the PNGTuber MVP direction.",
      "next": "Create structured project data and manifests.",
      "record": "records/2026-04-27/005633-phase-2.md"
    },
    {
      "timestamp": "2026-04-27T00:56:33+08:00",
      "phase": "Phase 3",
      "status": "done",
      "summary": "Created data formats",
      "details": "Defined avatar-manifest.json, project-state.json, run-log.json, and run-log.js for static dashboard and file-based workflows.",
      "next": "Use the logging and validation tools to maintain records.",
      "record": "records/2026-04-27/005633-phase-3.md"
    },
    {
      "timestamp": "2026-04-27T00:56:33+08:00",
      "phase": "Phase 4",
      "status": "done",
      "summary": "Implemented project tools",
      "details": "Built standard-library Python tools for logging events, validating assets, and generating public run-log data.",
      "next": "Validate missing assets and keep static data synchronized.",
      "record": "records/2026-04-27/005633-phase-4.md"
    },
    {
      "timestamp": "2026-04-27T00:56:33+08:00",
      "phase": "Phase 5",
      "status": "done",
      "summary": "Built PNGTuber overlay MVP",
      "details": "Implemented transparent OBS overlay with manifest loading, placeholder fallback, microphone volume detection, talk state switching, random blink, idle breathing, hotkeys, and debug URL parameters.",
      "next": "Open overlay/index.html in OBS Browser Source and test microphone permissions.",
      "record": "records/2026-04-27/005633-phase-5.md"
    },
    {
      "timestamp": "2026-04-27T00:56:33+08:00",
      "phase": "Phase 6",
      "status": "done",
      "summary": "Built static dashboard",
      "details": "Implemented dashboard/index.html, dashboard.js, and dashboard.css with project status, missing assets, tasks, run logs, docs links, overlay link, asset checklist, and disclaimer.",
      "next": "Run validation and tests, then hand off asset creation tasks.",
      "record": "records/2026-04-27/005633-phase-6.md"
    },
    {
      "timestamp": "2026-04-27T00:56:54+08:00",
      "phase": "Phase 7",
      "status": "done",
      "summary": "Ran project file tests",
      "details": "Executed tests/test_project_files.py with Python unittest. Required files and JSON data checks passed.",
      "next": "User should perform the OBS Browser Source microphone and visual test after adding or previewing assets.",
      "record": "records/2026-04-27/005654-phase-7.md"
    },
    {
      "timestamp": "2026-04-27T00:56:54+08:00",
      "phase": "Phase 8",
      "status": "done",
      "summary": "Completed PNGTuber MVP initialization",
      "details": "Finished static docs, data files, records workflow, overlay, dashboard, tools, and tests for the Minotaur Grand Mentor PNGTuber MVP.",
      "next": "Generate the four required PNGTuber assets, place them in assets/avatar/pngtuber, run validate_assets.py, and test overlay in OBS.",
      "record": "records/2026-04-27/005654-phase-8.md"
    },
    {
      "timestamp": "2026-04-27T00:59:53+08:00",
      "phase": "GitHub Upload",
      "status": "done",
      "summary": "Prepared repository content for GitHub upload",
      "details": "Prepared Minotaur Grand Mentor docs, data, records, overlay, dashboard, tools, and tests for upload to Jason-King-Wang/Minotaur-Grand-Mentor.",
      "next": "Push the static PNGTuber MVP project content to GitHub main branch.",
      "record": "records/2026-04-27/005953-github-upload.md"
    },
    {
      "id": "20260429-000818-final-handoff",
      "timestamp": "2026-04-29T00:08:18+08:00",
      "phase": "Final Handoff",
      "status": "done",
      "summary": "Completed all non-art deliverables",
      "details": "Project scaffold, docs, overlay, dashboard, logging, validation, Obsidian project pages, placeholder assets, and Live2D specs are complete. Waiting for final art assets and Live2D rigging.",
      "next": "Create final PNGTuber images and Live2D layered PSD.",
      "files_changed": [
        "README.md",
        "CODEX.md",
        "SCOPE_LOCK.md",
        "docs/BOTTOM_LINES.md",
        "docs/FINAL_HANDOFF.md",
        "data/project-state.json",
        "data/task-board.json",
        "data/live2d-sourcekit-manifest.json",
        "data/dashboard-data.js",
        "tools/scope_guard.py",
        "tools/generate_placeholder_assets.py",
        "tools/generate_final_report.py",
        "overlay/app.js",
        "dashboard/dashboard.js",
        "tests/test_project_files.py"
      ],
      "record": "records/2026-04-29/000818-final-handoff.md"
    },
    {
      "id": "20260429-001050-blueprint-archive",
      "timestamp": "2026-04-29T00:10:50+08:00",
      "phase": "Blueprint Archive",
      "status": "done",
      "summary": "Archived full v2 Codex blueprint",
      "details": "Copied the ChatGPT Pro generated full v2 blueprint into docs/CODEX_WORK_BLUEPRINT_FULL.md and linked it from README, CODEX, BLUEPRINT, and tests.",
      "next": "Use docs/CODEX_WORK_BLUEPRINT_FULL.md as the long-form source spec for future Codex work.",
      "files_changed": [
        "docs/CODEX_WORK_BLUEPRINT_FULL.md",
        "README.md",
        "CODEX.md",
        "docs/BLUEPRINT.md",
        "tests/test_project_files.py"
      ],
      "record": "records/2026-04-29/001050-blueprint-archive.md"
    },
    {
      "id": "20260429-071542-pngtuber-assets",
      "timestamp": "2026-04-29T07:15:42+08:00",
      "phase": "PNGTuber Assets",
      "status": "done",
      "summary": "Imported MVP PNGTuber assets",
      "details": "Imported idle_closed, talk_open, blink_closed, and happy PNG files from pngtuber_mvp_assets.zip. Archived the contact sheet in assets/reference.",
      "next": "Test overlay in OBS, then create Live2D front master and layered PSD.",
      "files_changed": [
        "assets/avatar/pngtuber/idle_closed.png",
        "assets/avatar/pngtuber/talk_open.png",
        "assets/avatar/pngtuber/blink_closed.png",
        "assets/avatar/pngtuber/happy.png",
        "assets/reference/pngtuber_mvp_contact_sheet.png",
        "docs/NEXT_ACTIONS.md",
        "data/task-board.json",
        "tools/validate_assets.py"
      ],
      "record": "records/2026-04-29/071542-pngtuber-assets.md"
    },
    {
      "id": "20260429-071627-pngtuber-status-cleanup",
      "timestamp": "2026-04-29T07:16:27+08:00",
      "phase": "PNGTuber Status Cleanup",
      "status": "done",
      "summary": "Updated tasks after PNGTuber asset import",
      "details": "Removed completed PNG generation tasks from pending_tasks, kept OBS testing and Live2D art/PSD as remaining work, and updated final handoff to mention imported MVP assets.",
      "next": "Test overlay in OBS, then create Live2D front master and layered PSD.",
      "files_changed": [
        "data/project-state.json",
        "docs/FINAL_HANDOFF.md"
      ],
      "record": "records/2026-04-29/071627-pngtuber-status-cleanup.md"
    },
    {
      "id": "20260429-072002-github-sync",
      "timestamp": "2026-04-29T07:20:02+08:00",
      "phase": "GitHub Sync",
      "status": "done",
      "summary": "Prepared PNGTuber asset sync",
      "details": "Validated imported PNGTuber MVP assets and prepared updated state, records, and dashboard fallback data for GitHub upload.",
      "next": "Push imported PNGTuber assets and updated project status to GitHub main.",
      "files_changed": [
        "assets/avatar/pngtuber/idle_closed.png",
        "assets/avatar/pngtuber/talk_open.png",
        "assets/avatar/pngtuber/blink_closed.png",
        "assets/avatar/pngtuber/happy.png",
        "assets/reference/pngtuber_mvp_contact_sheet.png",
        "data/project-state.json",
        "data/run-log.json",
        "data/run-log.js",
        "data/dashboard-data.js",
        "docs/NEXT_ACTIONS.md"
      ],
      "record": "records/2026-04-29/072002-github-sync.md"
    }
  ],
  "generatedAt": "2026-04-29T07:20:12+08:00"
};
