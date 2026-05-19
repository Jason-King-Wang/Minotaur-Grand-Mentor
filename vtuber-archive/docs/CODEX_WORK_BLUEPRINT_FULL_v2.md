# Codex 工作藍圖完整版 v2：Minotaur Grand Mentor VTuber / PNGTuber / Live2D-ready 專案

> 這份文件可以整份貼給 Codex。  
> 目標不是讓 Codex 畫圖或 rig Live2D，而是讓 Codex 把所有「工程、文件、紀錄、規格、dashboard、OBS overlay、Obsidian 專案頁、驗收工具」全部完成。  
> 最終狀態應該是：**工程與資料庫完成，只差正式圖片素材、分層 PSD、Live2D rigging。**

---

# 0. 給 Codex 的執行總指令

你現在是 `Minotaur Grand Mentor` 專案的 Codex 執行 Agent。請不要只輸出計畫，請直接建立檔案、寫程式、寫文件、更新狀態、執行測試，並留下紀錄。

本專案是 YouTube VTuber / PNGTuber / future Live2D avatar 專案。角色是原創牛頭人導師：霸氣、狂野、金融交易感、AI Agent 教學感。第一階段要先做到 **所有 Codex 能做的都完成，只差圖**。

你必須依照以下五段流程執行：

1. **用 LLM 生成專案脈絡**：整理角色、人設、用途、頻道方向、軟體需求。  
2. **建立資料庫**：建立 repo / Obsidian 專案資料夾、docs、data、records、assets、tools、overlay、dashboard。  
3. **定義核心目標 + 底線**：建立 `docs/BOTTOM_LINES.md`，明確禁止修改本專案以外的 Obsidian 內容。  
4. **產出藍圖**：建立可追蹤任務板、狀態 JSON、缺圖清單、驗收標準。  
5. **依藍圖執行並持續更新**：每完成一段就更新紀錄、狀態、dashboard fallback 資料。

請用繁體中文寫主要文件。程式碼、JSON key、HTML/CSS/JS 變數可用英文。

---

# 1. 最高優先級底線：Scope Lock / Obsidian 保護規則

以下規則優先於所有工作。如果任何任務與本頁衝突，以本頁為準。

## 1.1 只允許修改本專案

只允許建立、修改、更新下列專案資料夾內的內容：

```text
Minotaur-Grand-Mentor/
```

如果目前工作環境位於 Obsidian vault 內，仍然只能建立或修改：

```text
Minotaur-Grand-Mentor/
```

不可以修改、移動、刪除、重新命名任何本專案資料夾以外的內容。

## 1.2 不可以動其他 Obsidian 內容

嚴格禁止：

```text
.obsidian/
Daily Notes/
Templates/
Attachments/
任何其他專案資料夾/
任何不是 Minotaur-Grand-Mentor 的筆記/
任何 vault 設定檔/
```

不可掃描整個 vault 來整理筆記。不可把其他筆記搬進本專案。不可自動建立跨 vault 依賴。不可改其他專案的連結。

## 1.3 不可破壞既有資料

禁止執行或等效執行：

```bash
rm -rf
git reset --hard
git clean -fd
清空資料夾
覆蓋 records 舊紀錄
刪除既有 data/run-log.json
```

如果檔案已存在，請優先「合併、追加、補齊」，不要粗暴覆蓋。若必須重寫，先保留原本核心內容。

## 1.4 不可假裝已完成圖片或 Live2D

Codex 不能畫正式圖，不能假裝已完成正式角色圖，不能假裝已經產出 Live2D `.moc3`。

若沒有正式分層 PSD，狀態必須寫：

```text
waiting_for_art_assets
```

若沒有 Live2D Cubism rigging 成品，狀態必須寫：

```text
waiting_for_live2d_rigging
```

## 1.5 缺圖片不能讓系統壞掉

圖片缺失是本階段的正常狀態。overlay、dashboard、validation 都必須能在缺圖狀態下正常執行。

缺圖時：

- overlay 顯示 placeholder。
- dashboard 顯示 missing assets。
- `validate_assets.py` 回報缺圖但不 crash。
- `project-state.json` 記錄 blocked_by_art。

## 1.6 不可產生投資建議

角色可以是交易導師與 AI Agent 導師，但專案不得宣稱投資保證、穩賺、必勝、代操、買賣建議。

所有 README、dashboard、OBS 文件、YouTube 相關文案都要有免責聲明：

```text
本內容僅供研究、教育與娛樂用途，不構成投資建議。
```

## 1.7 不可使用密鑰、token、個資

不可要求或寫入：

```text
API key
token
cookie
密碼
私人絕對路徑
個資
```

## 1.8 靜態網站優先

第一階段必須能用靜態方式執行：

- GitHub Pages
- 本機 `python -m http.server`
- 直接開 HTML 時至少 dashboard 有 fallback 資料

不做後端、不做資料庫服務、不做 server-side framework。

## 1.9 每次執行都要有紀錄

每完成一個 phase，必須更新：

```text
records/
data/run-log.json
data/run-log.js
data/project-state.json
data/dashboard-data.js
```

不可只做事不記錄。

## 1.10 主力目標

所有工作都集中在主專案：

```text
Minotaur-Grand-Mentor
```

不要分散建立其他 repo、不要改其他 Obsidian 內容、不要做與本專案無關的工具。

---

# 2. 專案總目標

## 2.1 核心目標

本階段核心目標是讓 Codex 完成所有不依賴正式角色圖的工作：

- repo 架構
- 文件系統
- Obsidian 專案頁
- 底線頁
- 專案狀態 JSON
- 任務板
- 工作紀錄系統
- dashboard
- OBS Browser Source overlay
- PNGTuber placeholder fallback
- PNGTuber 素材 manifest
- Live2D 素材 manifest
- Live2D 分層 PSD 規格
- rigger 交付文件
- GitHub Pages 部署說明
- OBS 使用說明
- 測試檔案
- 最終驗收報告

完成後，專案應該只剩下：

```text
1. 正式 PNGTuber 表情圖
2. 正式 Live2D 正面母版圖
3. 正式 Live2D 分層 PSD
4. Live2D Cubism rigging
5. .moc3 / model3.json / physics3.json 等 Live2D 輸出
```

## 2.2 第一階段成品狀態

第一階段完成後，`data/project-state.json` 應該顯示：

```json
{
  "overall_status": "ready_waiting_for_art_assets",
  "current_phase": "waiting_for_art",
  "engineering_status": "done",
  "documentation_status": "done",
  "overlay_status": "placeholder_ready",
  "dashboard_status": "ready",
  "live2d_status": "spec_ready_waiting_for_art_and_rigging"
}
```

## 2.3 角色定位

角色名稱：

```text
Minotaur Grand Mentor
```

中文暱稱：

```text
牛導
```

角色設定：

- 原創牛頭人 VTuber
- 霸氣、狂野、導師感
- 金融交易氛圍
- AI Agent 工作流教練
- 黑色皮衣、金色邊線、深藍科技感
- 金色眼睛、巨大牛角、棕色毛髮
- 說話直接、強勢、像教練，但不恐嚇觀眾

頻道用途：

- AI Agent 教學
- Codex / automation 工作流
- Trading model research workflow
- GitHub / Obsidian / dashboard 專案管理
- YouTube 直播或教學影片

角色底線：

- 不要血腥恐怖化
- 不要過度寫實到不可愛
- 不要變成投資喊單角色
- 不要抄現有 IP
- 不要把素材說成已正式授權或已完成 rig

---

# 3. 需要的軟體與用途

請建立 `docs/SOFTWARE_SETUP.md`，內容必須包含以下軟體。

## 3.1 Codex 需要處理的工程軟體

| 軟體 / 工具 | 用途 | Codex 任務 |
|---|---|---|
| Git | 版本控制 | 寫入 repo 結構、避免破壞紀錄 |
| GitHub | 遠端 repo、GitHub Pages | 寫部署文件 |
| VS Code / Codex environment | 工程開發 | 主要工作環境 |
| Python 3.10+ | logging、validation、test | 建立 Python 工具 |
| Browser | dashboard / overlay 測試 | 寫靜態網頁 |
| OBS Studio | 直播 overlay | 寫 OBS 文件與 overlay |

## 3.2 人或畫師需要處理的美術軟體

| 軟體 | 用途 | Codex 任務 |
|---|---|---|
| Photoshop | 分層 PSD | 寫 PSD 規格 |
| Clip Studio Paint | 角色圖與分件 | 寫分件清單 |
| Krita | 免費替代繪圖工具 | 寫替代方案 |
| Live2D Cubism Editor | rigging | 寫 rigger checklist |
| VTube Studio | 測試 Live2D 模型 | 寫後續測試流程 |

## 3.3 本階段不要求 Codex 安裝的項目

Codex 不需要安裝 Live2D，不需要產生 `.moc3`，不需要產生正式圖片。Codex 要做的是把工程與規格準備到位。

---

# 4. 目標資料夾結構

請建立或補齊以下結構。

```text
Minotaur-Grand-Mentor/
  .minotaur-project-root
  README.md
  CODEX.md
  SCOPE_LOCK.md

  docs/
    PROJECT_BRIEF.md
    CHARACTER_BIBLE.md
    STYLE_GUIDE.md
    SOFTWARE_SETUP.md
    BOTTOM_LINES.md
    DISCLAIMER.md
    BLUEPRINT.md
    TASK_BOARD.md
    NEXT_ACTIONS.md
    ASSET_SPEC.md
    IMAGE_PROMPTS.md
    PNGTUBER_MVP.md
    LIVE2D_UPGRADE.md
    LIVE2D_LAYER_SPEC.md
    LIVE2D_RIGGER_CHECKLIST.md
    OBS_SETUP.md
    GITHUB_PAGES_SETUP.md
    OBSIDIAN_PROJECT_PAGE.md
    ACCEPTANCE_CRITERIA.md
    FINAL_HANDOFF.md

  data/
    project-state.json
    task-board.json
    avatar-manifest.json
    live2d-sourcekit-manifest.json
    run-log.json
    run-log.js
    dashboard-data.js

  records/
    README.md

  assets/
    reference/
      README.md
    avatar/
      README.md
      placeholders/
        README.md
      pngtuber/
        README.md
      live2d/
        README.md
        sourcekit_v0_1/
          README.md

  overlay/
    index.html
    app.js
    styles.css

  dashboard/
    index.html
    dashboard.js
    dashboard.css

  obsidian_project/
    README.md
    MinotaurGrandMentor_Home.md
    MinotaurGrandMentor_BottomLines.md
    MinotaurGrandMentor_TaskBoard.md
    MinotaurGrandMentor_AssetStatus.md
    MinotaurGrandMentor_NextActions.md

  tools/
    scope_guard.py
    log_event.py
    validate_assets.py
    build_public_data.py
    generate_placeholder_assets.py
    export_obsidian_project_pages.py
    generate_final_report.py

  tests/
    test_project_files.py
```

## 4.1 `.minotaur-project-root`

建立一個空白或簡短文字檔：

```text
This marker identifies the allowed project root for Minotaur Grand Mentor.
Codex must not modify files outside this root.
```

## 4.2 `SCOPE_LOCK.md`

此檔案是底線文件的 repo root 版本。內容要等同於 `docs/BOTTOM_LINES.md` 的摘要，並明確寫：

```text
Codex may only modify files under this project root.
If this folder is inside an Obsidian vault, Codex must not modify any other vault content.
```

---

# 5. 資料檔格式規格

## 5.1 `data/project-state.json`

請建立合法 JSON，至少包含：

```json
{
  "project": "Minotaur Grand Mentor",
  "version": "0.2.0",
  "mode": "engineering_until_art_missing",
  "current_phase": "initializing",
  "overall_status": "in_progress",
  "core_goal": "Complete all Codex-capable engineering, docs, dashboard, overlay, logging, and asset specs; leave only final art and Live2D rigging.",
  "scope_lock": "Only modify files inside Minotaur-Grand-Mentor project root. Do not modify other Obsidian content.",
  "engineering_status": "in_progress",
  "documentation_status": "in_progress",
  "overlay_status": "not_started",
  "dashboard_status": "not_started",
  "live2d_status": "spec_not_started",
  "completed_tasks": [],
  "pending_tasks": [],
  "missing_assets": [],
  "blocked_by_art": [],
  "blocked_by_rigging": [],
  "last_updated": "",
  "notes": []
}
```

## 5.2 `data/task-board.json`

請建立任務板資料：

```json
{
  "columns": {
    "not_started": [],
    "in_progress": [],
    "done": [],
    "waiting_for_art": [],
    "waiting_for_rigging": [],
    "blocked": []
  },
  "tasks": [
    {
      "id": "scope-lock",
      "title": "Create bottom lines and Obsidian scope lock",
      "status": "not_started",
      "owner": "codex",
      "acceptance": "docs/BOTTOM_LINES.md exists and states Codex cannot modify other Obsidian content."
    }
  ]
}
```

請至少建立以下 tasks：

```text
scope-lock
project-scaffold
docs-system
software-setup
character-bible
asset-spec
image-prompts
pngtuber-overlay
dashboard
logging-system
asset-validator
placeholder-generator
obsidian-project-pages
live2d-layer-spec
live2d-rigger-checklist
obs-setup-doc
github-pages-doc
tests
final-report
waiting-for-pngtuber-art
waiting-for-live2d-art
waiting-for-live2d-rigging
```

## 5.3 `data/run-log.json`

格式：

```json
[
  {
    "id": "20260428-000000-initialized",
    "timestamp": "2026-04-28T00:00:00",
    "phase": "initialization",
    "status": "done",
    "summary": "Initialized project scaffold",
    "details": "Created docs, data, tools, overlay, dashboard, and scope lock files.",
    "next": "Run asset validation and move to waiting_for_art.",
    "files_changed": []
  }
]
```

如果現在日期不確定，請用執行環境的當下時間。

## 5.4 `data/run-log.js`

格式：

```javascript
window.__MINOTAUR_RUN_LOG__ = [
  // same content as run-log.json
];
```

## 5.5 `data/dashboard-data.js`

格式：

```javascript
window.__MINOTAUR_DASHBOARD_DATA__ = {
  projectState: {},
  taskBoard: {},
  avatarManifest: {},
  live2dManifest: {},
  generatedAt: ""
};
```

## 5.6 `data/avatar-manifest.json`

PNGTuber MVP 素材：

```json
{
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
}
```

## 5.7 `data/live2d-sourcekit-manifest.json`

Live2D 正式素材需求：

```json
{
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
}
```

---

# 6. Phase 0：Preflight / 防呆檢查

## 6.1 目標

先確認目前目錄、安全範圍、既有檔案，不要誤動其他 Obsidian 內容。

## 6.2 必做

1. 確認目前目錄是否為 `Minotaur-Grand-Mentor` 或其內部。
2. 如果不是，建立 `Minotaur-Grand-Mentor/` 作為專案根目錄。
3. 在專案根目錄建立 `.minotaur-project-root`。
4. 建立 `SCOPE_LOCK.md`。
5. 建立 `tools/scope_guard.py`。

## 6.3 `tools/scope_guard.py` 要做什麼

- 檢查目前工作根目錄內是否有 `.minotaur-project-root`。
- 印出允許修改的 project root。
- 如果沒有 marker，提示需要在專案根目錄執行。
- 不可掃描專案根目錄以外的內容。

## 6.4 驗收標準

- `.minotaur-project-root` 存在。
- `SCOPE_LOCK.md` 存在。
- `docs/BOTTOM_LINES.md` 之後會引用相同底線。
- 沒有修改專案外部任何檔案。

## 6.5 完成後紀錄

執行或手動等效更新：

```bash
python tools/log_event.py --phase "Phase 0" --status "done" --summary "Created scope lock and project root marker" --details "Initialized safe project root and Obsidian protection rules." --next "Build project context documents."
```

若 `log_event.py` 尚未建立，請先在後續 Phase 建立後補登紀錄。

---

# 7. Phase 1：用 LLM 生成專案脈絡

## 7.1 目標

建立完整背景文件，讓 Codex、使用者、畫師、Live2D rigger 都能理解角色與專案方向。

## 7.2 請建立 / 更新

```text
README.md
CODEX.md
docs/PROJECT_BRIEF.md
docs/CHARACTER_BIBLE.md
docs/STYLE_GUIDE.md
docs/SOFTWARE_SETUP.md
docs/DISCLAIMER.md
```

## 7.3 README.md 必須包含

- 專案名稱
- 一句話介紹
- 第一階段目標
- 目前狀態
- Folder map
- 如何啟動 dashboard
- 如何啟動 overlay
- 如何執行測試
- 如何更新紀錄
- 如何放 PNGTuber 圖
- 如何放 Live2D source kit / final PSD
- 如何部署 GitHub Pages
- 免責聲明

## 7.4 CODEX.md 必須包含

Codex 每次工作前必讀：

```text
docs/BOTTOM_LINES.md
docs/BLUEPRINT.md
docs/NEXT_ACTIONS.md
data/project-state.json
```

Codex 每次工作後必須：

```text
1. 更新紀錄
2. 更新 project-state
3. 更新 dashboard fallback data
4. 不刪除 records
5. 不改專案外 Obsidian 內容
```

## 7.5 docs/PROJECT_BRIEF.md 必須包含

- 專案背景
- 角色用途
- 頻道用途
- 第一階段範圍
- 第二階段範圍
- 第三階段範圍
- 成功標準
- 非目標事項，例如：不做實際投資建議、不直接做 `.moc3`

## 7.6 docs/CHARACTER_BIBLE.md 必須包含

- 角色名稱
- 中文暱稱
- 人設
- 直播說話風格
- 口頭禪
- 視覺特徵
- 禁止偏離
- 表情清單
- 未來可做的直播場景

## 7.7 docs/STYLE_GUIDE.md 必須包含

- 主色
- 輔色
- 線條風格
- 材質風格
- 牛角、眼睛、皮衣、科技感設計規範
- 圖像構圖規範
- 禁止事項

## 7.8 docs/SOFTWARE_SETUP.md 必須包含

前面第 3 頁所有軟體清單，並分成：

- Codex / engineering 必備
- 人類美術必備
- Live2D rigging 必備
- 可選工具

## 7.9 docs/DISCLAIMER.md 必須包含

```text
本內容僅供研究、教育與娛樂用途，不構成投資建議。
```

並說明：

- 不提供買賣建議
- 不保證獲利
- 交易相關內容僅為研究範例

## 7.10 驗收標準

- 文件完整。
- 語氣一致。
- 角色定位清楚。
- 明確寫「本階段做到只差圖」。

---

# 8. Phase 2：建立資料庫 / Repo / Obsidian 專案頁

## 8.1 目標

建立可持續迭代的資料庫結構，包含 docs、data、records、assets、tools、dashboard、overlay、obsidian_project。

## 8.2 必做資料夾

請建立第 4 頁的完整資料夾結構。

## 8.3 `records/README.md`

寫明：

- records 是不可刪除的工作紀錄。
- 每次 Codex 工作都要產生紀錄。
- 格式為 `records/YYYY-MM-DD/HHMMSS-phase.md`。

## 8.4 `obsidian_project/README.md`

寫明：

- 這個資料夾是本專案專用 Obsidian 頁面。
- 不會修改外部 Obsidian vault。
- 使用者可以手動把這些 Markdown 匯入 Obsidian。

## 8.5 Obsidian 專案頁

請建立：

```text
obsidian_project/MinotaurGrandMentor_Home.md
obsidian_project/MinotaurGrandMentor_BottomLines.md
obsidian_project/MinotaurGrandMentor_TaskBoard.md
obsidian_project/MinotaurGrandMentor_AssetStatus.md
obsidian_project/MinotaurGrandMentor_NextActions.md
```

這些頁面只能存在 `obsidian_project/` 內。不得嘗試寫到其他 vault 路徑。

## 8.6 驗收標準

- folder tree 完整。
- Obsidian 頁只在 `obsidian_project/`。
- 不修改任何外部 vault。

---

# 9. Phase 3：定義核心目標 + 底線

## 9.1 目標

建立 Agent 決策基準，避免 Codex 偏離方向。

## 9.2 必做檔案

```text
docs/BOTTOM_LINES.md
docs/BLUEPRINT.md
docs/TASK_BOARD.md
docs/NEXT_ACTIONS.md
docs/ACCEPTANCE_CRITERIA.md
```

## 9.3 docs/BOTTOM_LINES.md 必須是一頁式底線

必須包含：

```text
1. 只能修改 Minotaur-Grand-Mentor 專案內的內容。
2. 如果專案位於 Obsidian vault，不得修改任何其他 Obsidian 筆記、附件、設定、模板或資料夾。
3. 不得刪除既有 records。
4. 不得假裝正式圖片或 Live2D rig 已完成。
5. 缺圖必須使用 placeholder。
6. 不得產生投資建議或保證獲利。
7. 不得使用 API key、token、cookie、密碼或個資。
8. 必須使用靜態優先設計。
9. 每次完成工作都要留下紀錄。
10. 主力目標是做到只差圖。
```

## 9.4 docs/BLUEPRINT.md

請用類似流程圖的方式寫：

```text
1. 用 LLM 生成專案脈絡
   產出：README、CODEX、PROJECT_BRIEF、CHARACTER_BIBLE、STYLE_GUIDE

2. 建立資料庫
   產出：docs、data、records、assets、tools、overlay、dashboard、obsidian_project

3. 定義核心目標 + 底線
   產出：BOTTOM_LINES、TASK_BOARD、NEXT_ACTIONS、ACCEPTANCE_CRITERIA

4. 產出藍圖
   產出：可執行任務板、狀態 JSON、缺圖清單、Live2D 分層規格

5. 依藍圖執行並持續更新
   產出：overlay、dashboard、logging、validation、tests、final handoff

最終成果：工程完成，只差圖與 Live2D rigging。
```

## 9.5 docs/NEXT_ACTIONS.md

初始化時寫 Codex 的下一步。最後完成時改成：

```text
下一步由使用者 / 畫師 / rigger 處理：
1. 生成或繪製正式 Live2D 正面母版圖。
2. 製作分層 PSD。
3. 補 PNGTuber 表情圖。
4. 執行 validate_assets.py。
5. OBS 實測 overlay。
6. 交給 Live2D rigger。
```

## 9.6 docs/ACCEPTANCE_CRITERIA.md

列出最終驗收條件：

- dashboard 可開
- overlay 可開
- 缺圖也不壞
- 底線頁存在
- Obsidian 保護規則存在
- run-log 有紀錄
- tests 通過
- final handoff 清楚列出還缺什麼

---

# 10. Phase 4：Logging / 記錄系統

## 10.1 目標

每次 Codex 工作都能留下紀錄，讓 dashboard 與 Obsidian 可追蹤進度。

## 10.2 建立 `tools/log_event.py`

功能要求：

- Python 標準函式庫。
- 自動建立 `records/YYYY-MM-DD/`。
- 自動產生 `HHMMSS-phase.md`。
- append `data/run-log.json`。
- regenerate `data/run-log.js`。
- 更新 `data/project-state.json.last_updated`。
- 不覆蓋既有紀錄。
- 若資料檔不存在，自動建立安全初始值。

參數：

```bash
--phase
--status
--summary
--details
--next
--files
```

範例：

```bash
python tools/log_event.py \
  --phase "Phase 4" \
  --status "done" \
  --summary "Built logging system" \
  --details "Added log_event.py, run-log JSON, run-log JS, and records folder." \
  --next "Build asset validator."
```

## 10.3 建立 `tools/build_public_data.py`

功能：

- 讀 `data/project-state.json`
- 讀 `data/task-board.json`
- 讀 `data/avatar-manifest.json`
- 讀 `data/live2d-sourcekit-manifest.json`
- 讀 `data/run-log.json`
- 產生 `data/run-log.js`
- 產生 `data/dashboard-data.js`

這是為了讓 dashboard 在 `file:///` 或 fetch 失敗時仍能顯示資料。

## 10.4 驗收標準

- 可執行 `python tools/log_event.py ...`。
- `records/` 產生一筆 Markdown。
- `data/run-log.json` 有紀錄。
- `data/run-log.js` 有 JS fallback。
- `data/project-state.json.last_updated` 更新。

---

# 11. Phase 5：Asset manifest / 缺圖檢查 / Placeholder

## 11.1 目標

在正式圖片尚未完成前，系統仍能知道缺什麼、顯示 placeholder，並把缺圖狀態展示在 dashboard。

## 11.2 建立 `docs/ASSET_SPEC.md`

內容分成：

1. PNGTuber MVP 素材
2. Live2D 正式素材
3. 圖片規格
4. 檔名規則
5. 放置路徑
6. 驗收標準

PNGTuber 必要檔案：

```text
assets/avatar/pngtuber/idle_closed.png
assets/avatar/pngtuber/talk_open.png
assets/avatar/pngtuber/blink_closed.png
assets/avatar/pngtuber/happy.png
```

PNGTuber 可選檔案：

```text
assets/avatar/pngtuber/angry.png
assets/avatar/pngtuber/thinking.png
assets/avatar/pngtuber/gesture_point.png
assets/avatar/pngtuber/shock.png
```

圖片規格：

```text
尺寸：2048x2048 或 3000x3000
格式：transparent PNG
構圖：正面或 3/4 正面半身
牛角：不可裁切
風格：一致
用途：OBS overlay
```

## 11.3 建立 `tools/validate_assets.py`

功能：

- 讀 `data/avatar-manifest.json`
- 讀 `data/live2d-sourcekit-manifest.json`
- 檢查每個 required asset 是否存在
- 檢查 optional asset 是否存在
- 更新 `data/project-state.json.missing_assets`
- 更新 `data/project-state.json.blocked_by_art`
- 缺圖不 crash
- 印出清楚報告

輸出範例：

```text
PNGTuber required assets:
[MISSING] idle_closed -> assets/avatar/pngtuber/idle_closed.png
[MISSING] talk_open -> assets/avatar/pngtuber/talk_open.png
[MISSING] blink_closed -> assets/avatar/pngtuber/blink_closed.png
[MISSING] happy -> assets/avatar/pngtuber/happy.png

Live2D required final files:
[MISSING] final_front_master
[MISSING] final_layered_psd

Status: waiting_for_art_assets
```

## 11.4 建立 `tools/generate_placeholder_assets.py`

功能：

- 產生 SVG placeholder。
- 放到 `assets/avatar/placeholders/`。
- 每個 placeholder 都明確寫：`Placeholder only, not final art`。
- 產生：

```text
placeholder_idle_closed.svg
placeholder_talk_open.svg
placeholder_blink_closed.svg
placeholder_happy.svg
placeholder_live2d_master.svg
```

## 11.5 驗收標準

- 缺圖時 validation 不 crash。
- dashboard 能顯示 missing list。
- overlay 能使用 placeholder。

---

# 12. Phase 6：PNGTuber OBS Overlay

## 12.1 目標

建立一個第一階段可以在 OBS Browser Source 使用的 overlay，即使沒有正式圖片也能顯示 placeholder。

## 12.2 建立檔案

```text
overlay/index.html
overlay/app.js
overlay/styles.css
```

## 12.3 功能要求

1. 靜態頁，不需要後端。
2. 背景透明。
3. 適合 OBS Browser Source。
4. 預設讀取 `../data/avatar-manifest.json`。
5. fetch 失敗時仍用內建 fallback manifest。
6. 圖片不存在時使用 placeholder。
7. 支援 Web Audio API 偵測麥克風。
8. 音量超過 threshold 顯示 `talk_open`。
9. 音量低於 threshold 顯示 `idle_closed`。
10. 每 3～7 秒隨機眨眼。
11. 有輕微呼吸動畫。
12. 支援表情熱鍵。
13. 支援 debug panel。
14. 支援 URL query params。

## 12.4 熱鍵

```text
1 = default / idle
2 = happy
3 = angry
4 = thinking
5 = gesture_point
6 = shock
0 = reset
D = toggle debug panel
M = toggle mic detection
```

## 12.5 URL 參數

```text
?debug=1
?threshold=0.05
?scale=1.0
?x=0
?y=0
?mic=1
```

## 12.6 Debug panel 顯示

- mic permission status
- current volume
- threshold
- current expression
- loaded assets
- missing assets
- blink status
- current mode

## 12.7 CSS 需求

- viewport full screen
- transparent background
- avatar positioned bottom center
- scale configurable
- no scrollbars
- high z-index debug panel
- readable debug text

## 12.8 OBS 使用文件

在 `docs/OBS_SETUP.md` 寫：

本機測試：

```bash
python -m http.server 8000
```

開啟：

```text
http://localhost:8000/overlay/?debug=1
```

OBS Browser Source：

```text
URL: http://localhost:8000/overlay/
Width: 1920
Height: 1080
Custom CSS: background: transparent;
```

## 12.9 驗收標準

- 沒有圖片也能開 overlay。
- debug panel 可顯示。
- placeholder 可顯示。
- JS 沒有 console fatal error。

---

# 13. Phase 7：Live2D 升級規格

## 13.1 目標

把未來要交給畫師 / rigger 的規格寫完整，讓下一步只需要照規格畫圖與 rig。

## 13.2 建立文件

```text
docs/LIVE2D_UPGRADE.md
docs/LIVE2D_LAYER_SPEC.md
docs/LIVE2D_RIGGER_CHECKLIST.md
docs/IMAGE_PROMPTS.md
```

## 13.3 `docs/LIVE2D_UPGRADE.md`

內容必須包含：

- 從 PNGTuber 到 Live2D 的流程
- 哪些是 Codex 可做
- 哪些是畫師要做
- 哪些是 rigger 要做
- Live2D Cubism 交付流程
- VTube Studio 測試流程
- 最終輸出格式

流程：

```text
1. 角色正面母版圖
2. 分層 PSD
3. Live2D Cubism 匯入
4. mesh 切割
5. deformers
6. parameter rigging
7. physics
8. expressions
9. export .moc3 / model3.json
10. VTube Studio 測試
```

## 13.4 `docs/LIVE2D_LAYER_SPEC.md`

必須寫完整分層規則：

```text
000_body/
  010_torso_jacket
  020_neck
  030_choker

010_head/
  010_head_base
  020_muzzle
  030_nose
  040_front_hair
  050_back_hair
  060_cheek_shadow
  070_fur_highlights

020_horns_ears/
  010_left_horn
  020_right_horn
  030_left_ear
  040_right_ear

030_eyes/
  010_left_eye_white
  011_left_iris
  012_left_pupil
  013_left_eye_highlight
  014_left_upper_eyelid
  015_left_lower_eyelid
  020_right_eye_white
  021_right_iris
  022_right_pupil
  023_right_eye_highlight
  024_right_upper_eyelid
  025_right_lower_eyelid
  030_left_eyebrow
  040_right_eyebrow

040_mouth/
  010_upper_lip
  020_lower_lip
  030_mouth_inner
  040_upper_teeth
  050_lower_teeth
  060_tongue
  070_mouth_shadow

050_clothes/
  010_jacket_body
  020_left_collar
  030_right_collar
  040_zipper
  050_gold_trim_left
  060_gold_trim_right

060_optional_hands/
  010_left_hand
  020_right_hand
  030_pointing_hand

070_fx_optional/
  010_blue_energy_ring
  020_gold_sparks
```

說明：

- 所有圖層必須在同一張 PSD 畫布座標。
- 不要把每個零件各自裁切到不同畫布。
- 被遮擋的部位要補完整。
- 嘴巴內部必須分件。
- 眼皮必須能蓋住眼球。
- 虹膜與瞳孔要分開。
- 牛角要獨立於頭。
- 耳朵要獨立於頭。
- 頭髮前後要分開。
- 外套領子可獨立晃動。

## 13.5 `docs/LIVE2D_RIGGER_CHECKLIST.md`

內容：

```text
交付給 rigger 前檢查：
[ ] 有 final_layered_model.psd
[ ] PSD 不是扁平圖
[ ] 所有 layer 命名清楚
[ ] 所有 layer 在同一畫布座標
[ ] 眼睛可獨立動
[ ] 眼皮可閉合
[ ] 嘴巴可開合
[ ] 牙齒、舌頭、mouth inner 分開
[ ] 角、耳、頭髮可獨立動
[ ] 背景透明
[ ] 沒有 watermark
[ ] 沒有多餘文字
[ ] 角色角沒有被裁切
[ ] 已附角色設定與表情需求
```

## 13.6 `docs/IMAGE_PROMPTS.md`

請寫出給生圖工具或畫師用的 prompts。

正式母版 prompt：

```text
Create an original front-facing Live2D VTuber character design for a charismatic anthropomorphic minotaur mentor. Half-body composition, symmetrical enough for rigging, large curved horns fully visible, warm brown fur, expressive golden eyes, black futuristic leather jacket with subtle gold trim, cyber trading mentor personality, confident and powerful but friendly for livestreaming. Transparent background, clean silhouette, no text, no logo, no watermark, no cropped horns, no horror, no gore.
```

PNGTuber prompt：

```text
Create an original anthropomorphic minotaur VTuber PNGTuber avatar, half-body, transparent background, black futuristic jacket with gold trim, golden eyes, large horns fully visible, cyber trading mentor vibe. Expression: {expression}. No text, no logo, no watermark, no cropped horns.
```

Negative prompt：

```text
text, logo, watermark, cropped horns, extra fingers, gore, horror, realistic blood, messy background, different character, investment advice text, stock ticker symbols, copyrighted character, low resolution
```

## 13.7 驗收標準

- 文件足以交給畫師與 rigger。
- 明確說 Codex 沒有完成正式 Live2D。
- 下一步清楚。

---

# 14. Phase 8：Dashboard

## 14.1 目標

建立一個可以在 GitHub Pages 或本機靜態開啟的專案 dashboard，用來看目前進度、缺圖、紀錄、下一步。

## 14.2 建立檔案

```text
dashboard/index.html
dashboard/dashboard.js
dashboard/dashboard.css
```

## 14.3 Dashboard 必須顯示

- Project title
- Character name
- Current phase
- Overall status
- Core goal
- Scope lock notice
- Obsidian protection notice
- Engineering status
- Documentation status
- Overlay status
- Dashboard status
- Live2D status
- Missing PNGTuber assets
- Missing Live2D assets
- Blocked by art list
- Blocked by rigging list
- Completed tasks
- Pending tasks
- Recent run logs
- Links to docs
- Link to overlay
- Link to Obsidian project page
- Disclaimer

## 14.4 資料讀取方式

優先 fetch：

```text
../data/project-state.json
../data/task-board.json
../data/avatar-manifest.json
../data/live2d-sourcekit-manifest.json
../data/run-log.json
```

fallback：

```text
../data/run-log.js
../data/dashboard-data.js
```

如果 fetch 和 fallback 都失敗，也要顯示基本靜態資訊，不可空白。

## 14.5 UI 風格

- 深色背景
- 黑、金、深藍、棕色
- cyber trading mentor dashboard
- 卡片式資訊
- 狀態 badge
- missing assets 用醒目區塊
- bottom lines 用固定警示區塊

## 14.6 驗收標準

- dashboard 可開。
- 沒有 data 也不完全壞。
- 有 data 時能顯示資料。
- 明確顯示：「不可修改其他 Obsidian 內容」。

---

# 15. Phase 9：GitHub Pages / OBS / 使用文件

## 15.1 `docs/GITHUB_PAGES_SETUP.md`

內容：

- 如何 push 到 GitHub
- 如何啟用 GitHub Pages
- Branch 選擇
- Root 選擇
- dashboard URL
- overlay URL
- 相對路徑注意事項
- fetch 失敗 fallback 說明

## 15.2 `docs/OBS_SETUP.md`

內容：

- 本機 server 啟動
- OBS Browser Source 設定
- 麥克風權限
- threshold
- debug mode
- 透明背景
- 常見問題

## 15.3 `docs/PNGTUBER_MVP.md`

內容：

- PNGTuber MVP 是什麼
- 需要哪些圖
- 如何放圖
- 如何驗證
- 如何測 OBS
- 如何升級 Live2D

## 15.4 驗收標準

- 使用者照文件可開 dashboard。
- 使用者照文件可開 overlay。
- 使用者知道下一步要放哪些圖。

---

# 16. Phase 10：測試

## 16.1 建立 `tests/test_project_files.py`

測試項目：

- 必要資料夾存在
- 必要 docs 存在
- 必要 data JSON 存在且合法
- overlay 三檔存在
- dashboard 三檔存在
- tools 檔案存在
- `docs/BOTTOM_LINES.md` 包含 `Obsidian`
- `docs/BOTTOM_LINES.md` 包含 `不得修改`
- `SCOPE_LOCK.md` 存在
- `.minotaur-project-root` 存在
- `data/avatar-manifest.json` 至少有 4 個 required assets
- `data/live2d-sourcekit-manifest.json` 至少有 final PSD 需求

## 16.2 執行

```bash
python tests/test_project_files.py
```

如果失敗，請修正後再執行。

---

# 17. Phase 11：最終驗收與交付

## 17.1 建立 `docs/FINAL_HANDOFF.md`

內容：

- 已完成項目
- 尚缺項目
- 如何打開 dashboard
- 如何打開 overlay
- 如何更新紀錄
- 如何驗證素材
- 如何放入正式圖片
- 如何進入 Live2D 階段
- 最終狀態

## 17.2 最終執行順序

請在最後執行：

```bash
python tools/generate_placeholder_assets.py
python tools/validate_assets.py
python tools/build_public_data.py
python tests/test_project_files.py
python tools/log_event.py --phase "Final Handoff" --status "done" --summary "Completed all non-art deliverables" --details "Project scaffold, docs, overlay, dashboard, logging, validation, Obsidian project pages, and Live2D specs are complete. Waiting for final art assets and Live2D rigging." --next "Create final PNGTuber images and Live2D layered PSD."
```

若某些命令因環境限制無法執行，請在 final report 中清楚說明並補上手動替代方式。

## 17.3 最終 `project-state.json` 應更新成

```json
{
  "current_phase": "waiting_for_art",
  "overall_status": "ready_waiting_for_art_assets",
  "engineering_status": "done",
  "documentation_status": "done",
  "overlay_status": "placeholder_ready",
  "dashboard_status": "ready",
  "live2d_status": "spec_ready_waiting_for_art_and_rigging",
  "blocked_by_art": [
    "PNGTuber expression PNG files",
    "Live2D final front master image",
    "Live2D final layered PSD"
  ],
  "blocked_by_rigging": [
    "Live2D Cubism rigging",
    ".moc3 export",
    "VTube Studio test"
  ]
}
```

---

# 18. 做到「只差圖」的最終清單

Codex 完成後，以下應該全部為 done：

```text
[ ] Scope lock done
[ ] Obsidian protection page done
[ ] Project scaffold done
[ ] README done
[ ] CODEX.md done
[ ] Character bible done
[ ] Style guide done
[ ] Software setup done
[ ] Asset spec done
[ ] Image prompts done
[ ] PNGTuber overlay done
[ ] Placeholder fallback done
[ ] Dashboard done
[ ] Logging system done
[ ] Asset validator done
[ ] Public data builder done
[ ] Obsidian project pages done
[ ] Live2D layer spec done
[ ] Rigger checklist done
[ ] OBS setup doc done
[ ] GitHub Pages setup doc done
[ ] Tests done
[ ] Final handoff done
[ ] Run log updated
[ ] Project state updated
[ ] Dashboard fallback data generated
```

以下應該是 waiting：

```text
[ ] waiting_for_pngtuber_art
[ ] waiting_for_live2d_front_master
[ ] waiting_for_live2d_layered_psd
[ ] waiting_for_live2d_rigging
```

---

# 19. Codex 最後回覆格式

完成後，請用以下格式回覆：

```text
## 完成狀態
- Overall status:
- Current phase:
- Engineering:
- Documentation:
- Overlay:
- Dashboard:
- Live2D:

## 已建立 / 更新的主要檔案
列出 docs、data、tools、overlay、dashboard、obsidian_project。

## 如何開啟 Dashboard
提供本機與 GitHub Pages 方式。

## 如何開啟 OBS Overlay
提供本機 URL、OBS Browser Source 設定、debug URL。

## 如何更新紀錄
提供 log_event.py 指令。

## 如何驗證素材
提供 validate_assets.py 指令。

## 目前缺少的圖片
列出 PNGTuber 與 Live2D 缺圖。

## 下一步使用者要做什麼
列出正式圖片、PSD、rigging。

## Scope Lock 確認
明確寫：本次工作只修改 Minotaur-Grand-Mentor 專案內檔案，沒有修改其他 Obsidian 內容。

## 測試結果
列出 tests/test_project_files.py 是否通過。如果未通過，說明原因。
```

---

# 20. 直接開始

請現在開始實作。不要只輸出計畫。不要修改本專案以外的任何 Obsidian 內容。完成後更新紀錄並回報。
