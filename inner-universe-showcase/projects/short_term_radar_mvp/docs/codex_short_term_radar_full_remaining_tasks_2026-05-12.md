# Codex 一次性完整任務檔：短線雷達從 Smoke 版推進到可用 Semi-Full / Full 資料雷達

日期：2026-05-12  
Repo：`Jason-King-Wang/Minotaur-Grand-Mentor`  
目前目標 PR：PR #4  
目前 base：`short-term-radar`  
目前 head：`codex/cl5-official-backfill`

---

## 0. 任務總說明

這是一份一次性完整任務，不是小修小補任務。

目前短線雷達已經完成：

- repo scope 修正
- simple mode 可跑
- robot slots 架構
- ScoreBreakdown
- baseline comparison
- report
- monthly revenue official smoke
- institutional trading official parser / collector smoke
- Shioaji / SinoPac injected API read-only hooks
- full mode guard
- root pollution guard

但它還沒有真正變成可用的 semi-full / full radar，原因是：

1. 很多資料來源仍只有 candidate URL 或 smoke parser。
2. 缺少穩定 official fetcher / parser / collector。
3. 缺少實際 local small-smoke processed parquet。
4. 缺少五年回補流程。
5. 缺少 scan 後 slot status 驗證。
6. 缺少資料品質與 coverage 報表的真實驗證。
7. 缺少把補進來的資料真正推動 `REVENUE_SLOT`、`CHIP_SLOT`、`SURVEILLANCE_SLOT`、`CATALYST_SLOT` 等 slot 從 partial/missing 變成 installed。

本任務目標：

> 一次性把短線雷達資料來源層做完整：官方來源 parser / collector / normalize / validate / upsert / coverage / small-smoke / backfill plan / slot status verification，全都補齊到可以從 simple mode 往 semi-full / full mode 升級。

---

## 1. 最高硬性規則：scope 不可再錯

所有短線雷達相關內容只能在：

```text
projects/short_term_radar_mvp/
```

絕對不可新增或修改成短線雷達用途的 root files：

```text
README.md
SHORT_TERM_RADAR_HANDOFF.md
short_term_radar/
configs/short_term_radar/
tests/short_term_radar/
reports/short_term_radar/
pytest.ini
data/raw/
data/processed/
data/tmp/
```

root `README.md` 必須維持 Minotaur Grand Mentor / VTuber 專案內容。

必須保留並加強：

```text
projects/short_term_radar_mvp/tests/short_term_radar/test_scope_guard.py
```

scope guard 必須防止：

```text
root short_term_radar/
root configs/short_term_radar/
root tests/short_term_radar/
root reports/short_term_radar/
root SHORT_TERM_RADAR_HANDOFF.md
root pytest.ini
root data/raw
root data/processed
root data/tmp
```

---

## 2. 不可 commit 的東西

不可 commit：

```text
projects/short_term_radar_mvp/data/raw/
projects/short_term_radar_mvp/data/processed/
projects/short_term_radar_mvp/data/tmp/
projects/short_term_radar_mvp/configs/short_term_radar/local.yaml
.env
.env.*
token
credential
broker log
sqlite
cache
large downloaded csv/json/html/parquet
```

允許 commit：

```text
projects/short_term_radar_mvp/data/quality/.gitkeep
projects/short_term_radar_mvp/tests/fixtures/
小型 mock/sample fixture
小型 sample report
source code
tests
README / handoff
example config
```

如果 local smoke 產生 processed parquet，只能在本機驗證，不可 commit。

---

## 3. Broker / Shioaji / SinoPac 安全規則

broker source 只能 read-only。

可以：

```text
使用 externally managed API object
api.notice()
api.punish()
api.credit_enquires()
api.short_stock_sources()
api.kbars()
api.snapshots()
api.ticks()
api.daily_quotes()
api.scanners()
讀 contract metadata
```

不可新增：

```text
api.login
activate_ca
place_order
update_order
cancel_order
account_balance
positions
realized_pnl
unrealized_pnl
settlements
任何下單 / 改單 / 刪單 / 帳戶 / 部位 / 損益查詢
從 .env 讀 broker credential
內建登入流程
```

必須保留測試確認 production code 不含以上 forbidden methods。測試 fake method 可以存在，但必須是「若被呼叫就 fail」的測試用途。

---

## 4. 模型行為不可破壞

無論資料有沒有補齊：

- `scan` 不可 crash
- `backtest` 不可 crash
- `report` 不可 crash
- 缺資料必須標示 degraded
- 缺 revenue 不可進 S3 candidate_entry
- 處置中必須強制 S5 avoid_chasing
- partial slots 不可觸發 `full_short_term_radar`
- simple mode 必須繼續可跑
- score 不可因為缺資料被灌成完整高分
- no future leakage 必須保留

---

## 5. 本輪總完成目標

請一次完成以下主線：

```text
A. local config / local smoke 流程補齊
B. monthly_revenue 完整 official source 小範圍可用
C. institutional_trading 完整 official source 小範圍可用
D. margin_short official source parser / collector
E. surveillance_daily official source parser / collector
F. material_events official source parser / collector
G. corporate_actions official source parser / collector
H. trading_calendar official source parser / collector
I. valuation / symbol_master 補強
J. coverage / freshness / missing report 真實可用
K. scan slot status 驗證
L. backtest / baseline 不破壞
M. handoff / README 完整更新
N. 最終驗收與回報
```

---

# A. Local Config / Smoke Workflow

## A1. 建立 local.yaml 產生方式，但不可 commit local.yaml

目前 PR 說 `configs/short_term_radar/local.yaml` 不存在，導致無法跑 normalize/write local small-smoke。

請完成：

1. 確認 `configs/short_term_radar/local.yaml.example` 足夠清楚。
2. 補一段 README / handoff 指令，告訴使用者如何從 example 複製成本機 local.yaml。
3. 不可 commit local.yaml。
4. 所有 smoke command 必須能用 local.yaml.example dry-run。
5. 若要真正寫本機 processed parquet，才用 local.yaml。

建議文件指令：

```powershell
cd C:\Users\User\Documents\New project 4\projects\short_term_radar_mvp
Copy-Item configs\short_term_radar\local.yaml.example configs\short_term_radar\local.yaml
```

local.yaml 應該讓使用者設定：

```yaml
data_root: C:\Users\User\Documents\New project 4\data
existing_daily_price_path: C:\Users\User\Documents\New project 4\data\processed\prices_daily.parquet
```

但不要把這個 local.yaml commit。

## A2. TLS / certificate fallback

TWSE institutional live fetch 出現過：

```text
CERTIFICATE_VERIFY_FAILED
```

請不要用 unsafe global disable SSL verification。

請做：

1. fetch error 必須 degraded cleanly。
2. README / handoff 記錄 TLS issue 與處理方式。
3. 如果能安全解決，採用 Python / certifi 標準方式。
4. 若不能解決，保留 degraded message，不 crash。
5. 不可為了通過測試關掉 SSL 驗證。
6. 測試要覆蓋 fetch degraded path。

---

# B. Monthly Revenue 完整化

## B1. 目標

把 `monthly_revenue` 做到：

- official MOPS source request 完整
- TWSE / TPEx
- local / foreign company type
- ROC year/month URL
- HTML parser
- encoding fallback
- normalize
- no future leakage
- upsert
- validate
- small smoke
- five-year backfill command documented

## B2. 必須支援 command

Dry-run：

```powershell
py -3.14 -m short_term_radar.cli.collect `
  --config configs\short_term_radar\local.yaml.example `
  --dataset monthly_revenue `
  --market all `
  --start-month 2026-01 `
  --end-month 2026-03 `
  --source official `
  --dry-run
```

Local small smoke：

```powershell
py -3.14 -m short_term_radar.cli.collect `
  --config configs\short_term_radar\local.yaml `
  --dataset monthly_revenue `
  --market all `
  --start-month 2026-01 `
  --end-month 2026-03 `
  --source official `
  --normalize `
  --validate
```

Five-year command must be documented but not automatically run in tests：

```powershell
py -3.14 -m short_term_radar.cli.collect `
  --config configs\short_term_radar\local.yaml `
  --dataset monthly_revenue `
  --market all `
  --start-month 2021-01 `
  --end-month 2026-05 `
  --source official `
  --normalize `
  --validate
```

## B3. 必須保留 no future leakage

規則：

```text
不可用 fetched_at 當 announce_date
若官方沒有公告日：
  announce_date = next_month_day_10(revenue_month)
  announce_date_source = inferred_next_month_day_10
  announce_date_inferred = true
```

回測時：

```text
only rows where announce_date <= as_of_date
```

## B4. 測試

必須有：

```text
test_monthly_revenue_official_fetcher.py
test_no_future_leakage_revenue.py
test_collect_cli.py
test_processed_storage_upsert.py
```

覆蓋：

- TWSE / TPEx
- local / foreign
- ROC year/month URL
- HTML parser
- Big5 / cp950 / utf-8
- empty fetch degraded
- invalid HTML degraded
- normalize number
- no empty processed table write
- upsert primary key dedupe
- no future leakage

---

# C. Institutional Trading 完整化

## C1. 目標

目前已新增：

```text
institutional_trading_official.py
twse_institutional_trading_fetcher.py
tpex_institutional_trading_fetcher.py
twse_t86_sample.json
tpex_3insti_sample.json
```

請繼續補到真正可用：

- TWSE T86 JSON parser
- TPEx 3insti JSON parser
- collect CLI
- normalize
- validate
- upsert
- dry-run
- local single-date smoke
- date range collect command
- degraded cleanly on TLS/source issue

## C2. 必須輸出欄位

至少：

```text
trade_date
market
symbol
name
foreign_buy
foreign_sell
foreign_net
investment_trust_buy
investment_trust_sell
investment_trust_net
dealer_buy
dealer_sell
dealer_net
dealer_self_buy
dealer_self_sell
dealer_self_net
dealer_hedge_buy
dealer_hedge_sell
dealer_hedge_net
total_institutional_net
source
source_url
fetched_at
```

如果來源只有 net，不能亂填 buy/sell 為 0；缺值要 null。

## C3. 必須支援 command

Dry-run：

```powershell
py -3.14 -m short_term_radar.cli.collect `
  --config configs\short_term_radar\data_sources.example.yaml `
  --dataset institutional_trading `
  --market TWSE `
  --date 2026-04-30 `
  --source official `
  --dry-run
```

```powershell
py -3.14 -m short_term_radar.cli.collect `
  --config configs\short_term_radar\data_sources.example.yaml `
  --dataset institutional_trading `
  --market TPEX `
  --date 2026-04-30 `
  --source official `
  --dry-run
```

Local single-date smoke：

```powershell
py -3.14 -m short_term_radar.cli.collect `
  --config configs\short_term_radar\local.yaml `
  --dataset institutional_trading `
  --market all `
  --date 2026-04-30 `
  --source official `
  --normalize `
  --validate
```

Date range command should be supported or explicitly rejected if not yet implemented：

```powershell
py -3.14 -m short_term_radar.cli.collect `
  --config configs\short_term_radar\local.yaml `
  --dataset institutional_trading `
  --market all `
  --start 2021-01-01 `
  --end 2026-05-11 `
  --source official `
  --normalize `
  --validate
```

如果 range mode 尚未實作，必須明確報錯，不可 silently ignore：

```text
institutional_trading range collect not implemented yet; use --date for single-day smoke
```

## C4. 測試

必須有：

```text
test_institutional_trading_official_fetcher.py
test_institutional_trading_normalizer.py
test_collect_cli.py
test_processed_storage_upsert.py
```

覆蓋：

- TWSE T86 fields + data
- TWSE aaData variant
- TPEx list payload
- TPEx dict payload with data/tables/rows/result
- comma number parsing
- negative number parsing
- ROC date / ISO date normalization
- source_url retention
- fetch degraded
- no empty processed write
- upsert primary key dedupe
- dry-run output

---

# D. Margin / Short 完整化

## D1. 目標

建立 official source parser / collector，而不是只靠 broker read-only current hook。

目前來源候選：

TWSE：

```text
https://openapi.twse.com.tw/v1/exchangeReport/MI_MARGN
https://openapi.twse.com.tw/v1/SBL/TWT96U
```

TPEx：

```text
https://www.tpex.org.tw/openapi/v1/tpex_mainboard_margin_balance
https://www.tpex.org.tw/openapi/v1/tpex_margin_sbl
```

本輪請完成：

- official source class
- TWSE margin parser
- TWSE SBL parser
- TPEx margin parser
- TPEx SBL parser
- merge margin + short / SBL fields by trade_date + market + symbol
- normalize to `margin_short_daily`
- collect CLI dry-run
- local single-date smoke
- degraded if source unavailable
- broker read-only source remains optional current check only

## D2. 必須輸出欄位

至少：

```text
trade_date
market
symbol
name
margin_buy
margin_sell
margin_cash_repay
margin_balance
margin_quota
short_sell
short_buy
short_cash_repay
short_balance
short_quota
sbl_balance
source
source_url
fetched_at
```

如果某 API 沒有全部欄位，缺值 null，不可亂填 0。

## D3. command

Dry-run：

```powershell
py -3.14 -m short_term_radar.cli.collect `
  --config configs\short_term_radar\data_sources.example.yaml `
  --dataset margin_short `
  --market all `
  --date 2026-04-30 `
  --source official `
  --dry-run
```

Local smoke：

```powershell
py -3.14 -m short_term_radar.cli.collect `
  --config configs\short_term_radar\local.yaml `
  --dataset margin_short `
  --market all `
  --date 2026-04-30 `
  --source official `
  --normalize `
  --validate
```

## D4. tests

新增：

```text
test_margin_short_official_fetcher.py
test_margin_short_normalizer.py
test_collect_cli.py
```

覆蓋：

- TWSE margin payload
- TWSE SBL payload
- TPEx margin payload
- TPEx SBL payload
- merge by symbol/date
- degraded source
- no empty processed write
- upsert primary key
- broker read-only boundary remains safe

---

# E. Surveillance / Attention / Disposition 完整化

## E1. 目標

處置資料是短線雷達風控核心。必須讓 `SURVEILLANCE_SLOT` 從 partial 往 installed 推進。

目前已有：

- Shioaji read-only `notice()` / `punish()` hooks
- TPEx attention/disposition skeleton
- `disposition_active_flag` gating
- 處置中強制 S5

還缺：

- official source parser
- direct download/api_url support
- attention/disposition period parsing
- local smoke
- processed table upsert

## E2. 來源

TPEx candidate：

```text
attention dataset 11395
disposition dataset 11396
```

TWSE free endpoint 尚未明確，若只能用 eShop 或 broker current hook，必須明確標註：

```text
TWSE historical surveillance source unresolved
```

但不要假裝 installed。

## E3. 必須輸出欄位

至少：

```text
trade_date
market
symbol
name
attention_flag
attention_reason
disposition_flag
disposition_start
disposition_end
disposition_reason
disposition_measure
disposition_active_flag
source
source_url
fetched_at
```

重點：

```text
as_of_date 在 disposition_start <= as_of_date <= disposition_end 時：
  disposition_active_flag = true
  stage = S5
  entry_zone = avoid_chasing
```

## E4. command

Dry-run：

```powershell
py -3.14 -m short_term_radar.cli.collect `
  --config configs\short_term_radar\data_sources.example.yaml `
  --dataset surveillance `
  --market all `
  --date 2026-04-30 `
  --source official `
  --dry-run
```

Local smoke：

```powershell
py -3.14 -m short_term_radar.cli.collect `
  --config configs\short_term_radar\local.yaml `
  --dataset surveillance `
  --market all `
  --date 2026-04-30 `
  --source official `
  --normalize `
  --validate
```

## E5. tests

必須有：

```text
test_surveillance_official_fetcher.py
test_surveillance_normalizer.py
test_disposition_blocks_candidate_entry.py
test_stage_gating_with_missing_data.py
```

覆蓋：

- attention parser
- disposition parser
- period parsing
- active flag calculation
- source missing degraded
- TWSE unresolved source not treated installed
- TPEx parser
- Shioaji read-only payload parser
- no account/order calls

---

# F. Material Events / Catalyst 完整化

## F1. 目標

建立 MOPS material events official fetcher / parser，讓 CATALYST_SLOT 從 partial 往 installed 推進。

來源候選：

TWSE：

```text
https://openapi.twse.com.tw/v1/opendata/t187ap04_L
```

TPEx：

```text
https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap04_O
```

## F2. 必須輸出欄位

至少：

```text
announce_date
market
symbol
name
event_title
event_content
event_type
is_positive_catalyst
is_negative_risk
catalyst_score_hint
source
source_url
fetched_at
```

event_type 初步分類：

```text
法說
接單
併購
增資
減資
處分資產
訴訟
停工
財測
營收
產品
合作
董事會
其他
```

## F3. command

Dry-run：

```powershell
py -3.14 -m short_term_radar.cli.collect `
  --config configs\short_term_radar\data_sources.example.yaml `
  --dataset material_events `
  --market all `
  --date 2026-04-30 `
  --source official `
  --dry-run
```

Local smoke：

```powershell
py -3.14 -m short_term_radar.cli.collect `
  --config configs\short_term_radar\local.yaml `
  --dataset material_events `
  --market all `
  --date 2026-04-30 `
  --source official `
  --normalize `
  --validate
```

## F4. tests

新增：

```text
test_material_events_official_fetcher.py
test_material_events_classifier.py
test_catalyst_adapter.py
```

覆蓋：

- TWSE material event payload
- TPEx material event payload
- date parse
- symbol parse
- event classifier
- positive / negative / neutral
- no future leakage
- degraded when source unavailable

---

# G. Corporate Actions 完整化

## G1. 目標

建立 corporate actions official fetcher / parser。

來源候選：

TWSE：

```text
https://openapi.twse.com.tw/v1/exchangeReport/TWT48U_ALL
https://openapi.twse.com.tw/v1/opendata/t187ap45_L
```

TPEx：

```text
https://www.tpex.org.tw/openapi/v1/tpex_exright_prepost
https://www.tpex.org.tw/openapi/v1/tpex_exright_daily
```

## G2. 欄位

至少：

```text
action_date
market
symbol
name
action_type
ex_date
record_date
cash_dividend
stock_dividend
capital_reduction_ratio
reference_price
source
source_url
fetched_at
```

action_type：

```text
cash_dividend
stock_dividend
ex_right
ex_dividend
capital_reduction
split
other
```

## G3. tests

新增：

```text
test_corporate_actions_official_fetcher.py
test_corporate_actions_normalizer.py
```

覆蓋：

- ex-dividend
- ex-right
- capital reduction
- date normalization
- symbol normalization
- missing fields null
- source degraded

---

# H. Trading Calendar 完整化

## H1. 目標

目前 coverage/backtest 主要從 `prices_daily` 推交易日，這可以當 fallback，但 full radar 應有 official calendar。

來源候選：

```text
https://openapi.twse.com.tw/v1/holidaySchedule/holidaySchedule
```

## H2. 欄位

```text
trade_date
is_trading_day
market
holiday_name
source
source_url
fetched_at
```

## H3. 邏輯

coverage expected dates：

1. 優先用 official `trading_calendar`
2. 若缺，使用 `prices_daily` 的日期集合
3. 若再缺，才用 weekday fallback

不可把週末當 missing。

## H4. tests

新增：

```text
test_trading_calendar_official_fetcher.py
test_coverage_reports.py
```

覆蓋：

- holiday parse
- weekend exclude
- prices_daily fallback
- weekday fallback
- event-driven dataset 不要求 daily coverage

---

# I. Valuation / Symbol Master 補強

## I1. 目標

估值與股本資料支援：

- 市值
- PE
- PB
- 股本
- 產業
- 市場
- symbol metadata

來源候選已在 config。

TWSE：

```text
BWIBBU_d
t187ap03_L
```

TPEx：

```text
tpex_mainboard_peratio_analysis
tpex_daily_market_value
mopsfin_t187ap03_O
```

## I2. 欄位

valuation_daily：

```text
trade_date
market
symbol
name
market_cap
pe
pb
dividend_yield
share_capital
source
source_url
fetched_at
```

symbol_master：

```text
symbol
name
market
industry
listed_date
share_capital
is_etf
is_warrant
is_full_delivery
source
source_url
fetched_at
```

## I3. tests

新增或補強：

```text
test_symbol_master_official_fetcher.py
test_valuation_official_fetcher.py
test_symbol_master_normalizer.py
test_valuation_normalizer.py
```

---

# J. Coverage / Freshness / Missing Reports

## J1. 目標

讓 coverage 不只是 dry-run，而是真的可以產出：

```text
data/quality/data_coverage_report.csv
data/quality/missing_dates_report.csv
data/quality/freshness_report.csv
```

注意：這些 generated report 可以在 local 產生，但除非是小型 sample，不要 commit 大量報表。

## J2. 必須支援

```powershell
py -3.14 -m short_term_radar.cli.coverage `
  --config configs\short_term_radar\local.yaml `
  --start 2021-01-01 `
  --end 2026-05-11 `
  --write-reports
```

## J3. 規則

- daily datasets 用 trading calendar / prices_daily / weekday fallback
- monthly datasets 用 month range
- event-driven datasets 不要求每天有資料
- source_missing 要和 missing_dates 區分
- stale / fresh 要明確
- processed table 不存在要 degraded，不 crash

---

# K. Scan Slot Status 驗證

## K1. 目標

每補完一個 processed table，要確認 scan output 的 slot 狀態有變。

必須新增或確認 scan output 包含：

```text
mode
robot_slot_statuses
robot_slot_coverage_ratio
score_data_coverage_ratio
available_radars
degraded_radars
core_data_ready_flag
```

## K2. 必測情境

1. 只有 price：
   - `simple_price_volume_mode`
   - revenue degraded
   - core_data_ready false
   - 不可 S3

2. price + monthly_revenue：
   - REVENUE_SLOT installed
   - revenue score 有效
   - 若 surveillance missing，仍不可過度樂觀

3. price + revenue + surveillance：
   - semi_full_short_term_radar
   - 若非處置中，可允許更高 stage
   - 若處置中，必須 S5

4. all full slots installed：
   - full_short_term_radar
   - partial 不可觸發 full

## K3. tests

新增或補強：

```text
test_pipeline_score_breakdown.py
test_stage_gating_with_missing_data.py
test_disposition_blocks_candidate_entry.py
test_slot_status_transitions.py
```

---

# L. Backtest / Baseline 不可破壞

必須保留：

```text
radar_model
random_top_n
breakout_120d_only
volume_expansion_only
ma_alignment_only
```

`breakout_120d_only` 必須只看：

```text
breakout_120d_flag == true
```

backtest CLI 必須保留：

```text
--include-baselines
--random-seed
```

驗證：

```powershell
py -3.14 -m short_term_radar.cli.backtest `
  --config configs\short_term_radar/default.yaml `
  --start 2021-05-01 `
  --end 2026-04-30 `
  --top-n 20 `
  --horizon-days 126 `
  --target-multiple 3 `
  --include-baselines `
  --random-seed 42 `
  --output reports/short_term_radar/backtest_2021-05-01_2026-04-30.csv
```

如果 local data 不存在，至少 dry-run / test path 不可壞掉。

---

# M. README / Handoff 更新

必須更新：

```text
projects/short_term_radar_mvp/README.md
projects/short_term_radar_mvp/SHORT_TERM_RADAR_HANDOFF.md
```

內容要包含：

1. 目前完成哪些 official sources
2. 哪些可 dry-run
3. 哪些可 local small smoke
4. 哪些可五年 backfill
5. 哪些仍只是 candidate
6. 哪些 slot 是 installed / partial / missing
7. 如何建立 local.yaml
8. 不可 commit 哪些 local data
9. TLS / endpoint issue
10. 下一步操作

不要把 handoff 寫成一堆模糊自述，要能讓下一個分頁直接接手。

---

# N. 最終驗證指令

從：

```powershell
cd C:\Users\User\Documents\New project 4\projects\short_term_radar_mvp
```

執行：

## N1. 基本驗證

```powershell
py -3.14 -m compileall -q short_term_radar tests\short_term_radar
py -3.14 -m pytest -q tests\short_term_radar
git diff --check
```

## N2. Dry-runs

```powershell
py -3.14 -m short_term_radar.cli.collect --config configs\short_term_radar\local.yaml.example --dataset monthly_revenue --market all --start-month 2026-01 --end-month 2026-03 --source official --dry-run
py -3.14 -m short_term_radar.cli.collect --config configs\short_term_radar\data_sources.example.yaml --dataset institutional_trading --market TWSE --date 2026-04-30 --source official --dry-run
py -3.14 -m short_term_radar.cli.collect --config configs\short_term_radar\data_sources.example.yaml --dataset institutional_trading --market TPEX --date 2026-04-30 --source official --dry-run
py -3.14 -m short_term_radar.cli.collect --config configs\short_term_radar\data_sources.example.yaml --dataset margin_short --market all --date 2026-04-30 --source official --dry-run
py -3.14 -m short_term_radar.cli.collect --config configs\short_term_radar\data_sources.example.yaml --dataset surveillance --market all --date 2026-04-30 --source official --dry-run
py -3.14 -m short_term_radar.cli.collect --config configs\short_term_radar\data_sources.example.yaml --dataset material_events --market all --date 2026-04-30 --source official --dry-run
py -3.14 -m short_term_radar.cli.collect --config configs\short_term_radar\data_sources.example.yaml --dataset corporate_actions --market all --date 2026-04-30 --source official --dry-run
py -3.14 -m short_term_radar.cli.coverage --config configs\short_term_radar\local.yaml.example --start 2021-01-01 --end 2026-05-11 --dry-run
```

## N3. Local small smoke

如果本機建立了 local.yaml，請跑：

```powershell
py -3.14 -m short_term_radar.cli.collect --config configs\short_term_radar\local.yaml --dataset monthly_revenue --market all --start-month 2026-01 --end-month 2026-03 --source official --normalize --validate
py -3.14 -m short_term_radar.cli.collect --config configs\short_term_radar\local.yaml --dataset institutional_trading --market all --date 2026-04-30 --source official --normalize --validate
py -3.14 -m short_term_radar.cli.collect --config configs\short_term_radar\local.yaml --dataset margin_short --market all --date 2026-04-30 --source official --normalize --validate
py -3.14 -m short_term_radar.cli.collect --config configs\short_term_radar\local.yaml --dataset surveillance --market all --date 2026-04-30 --source official --normalize --validate
py -3.14 -m short_term_radar.cli.coverage --config configs\short_term_radar\local.yaml --start 2021-01-01 --end 2026-05-11 --write-reports
```

## N4. Scan slot verification

```powershell
py -3.14 -m short_term_radar.cli.scan `
  --config configs\short_term_radar\default.yaml `
  --date 2026-04-30 `
  --top 50 `
  --output reports\short_term_radar\scan_2026-04-30.csv
```

確認：

```text
mode
robot_slot_statuses
robot_slot_coverage_ratio
score_data_coverage_ratio
available_radars
degraded_radars
core_data_ready_flag
```

---

# O. 回報格式

完成後請用以下格式回報：

```text
Scope
- changed files 是否全部在 projects/short_term_radar_mvp/
- root README 是否 untouched
- root pollution guard 是否通過
- 是否有 commit raw/processed/local.yaml/secrets

Implemented Sources
- monthly_revenue: dry-run / smoke / parser / validate / upsert 狀態
- institutional_trading: dry-run / smoke / parser / validate / upsert 狀態
- margin_short: dry-run / smoke / parser / validate / upsert 狀態
- surveillance: dry-run / smoke / parser / validate / upsert 狀態
- material_events: dry-run / smoke / parser / validate / upsert 狀態
- corporate_actions: dry-run / smoke / parser / validate / upsert 狀態
- trading_calendar: dry-run / smoke / parser / validate / upsert 狀態
- valuation/symbol_master: 狀態

Validation
- compileall result
- pytest result
- dry-run commands result
- local small-smoke result
- scan slot status result
- coverage result
- git diff --check result

Data
- 是否產生 local raw/processed
- 是否確認未 commit raw/processed
- 每個 processed table local rows count
- 每個 processed table quality result

Slot Status
- PRICE_SLOT
- UNIVERSE_SLOT
- REVENUE_SLOT
- CHIP_SLOT
- SURVEILLANCE_SLOT
- CATALYST_SLOT
- CORPORATE_SLOT
- VALUATION_SLOT
- CALENDAR_SLOT
- final mode

Still Missing
- 哪些 source 還只是 candidate
- 哪些 parser 還沒做
- 哪些 live fetch 還有 TLS / endpoint issue
- 哪些只能 degraded
- 是否還不能 full mode

Risks
- endpoint 不穩
- 欄位 mapping 不確定
- TLS / certificate
- official source unavailable
- Shioaji current-only limitations
```

---

# P. Merge / PR 狀態

本任務完成前，PR #4 可以繼續 draft。

完成後：

1. PR #4 從 draft 轉 ready。
2. 確認 mergeable。
3. 先 merge PR #4 into `short-term-radar`。
4. 再更新 PR #3。
5. PR #3 才 merge into `main`。

不要跳過 PR #4 直接處理 PR #3。

---

# Q. 最終目標定義

本輪完成後，理想狀態是：

```text
simple mode：穩定可跑
monthly_revenue：official smoke + local small processed 成功
institutional_trading：official smoke + local small processed 成功
margin_short：official parser / dry-run / small smoke 至少部分成功
surveillance：official/broker read-only parser / dry-run / small smoke 至少部分成功
material_events：official parser / dry-run 可用
corporate_actions：official parser / dry-run 可用
trading_calendar：official parser / fallback 邏輯可用
coverage reports：可產出
scan：能反映 slot 狀態變化
tests：全過
root：乾淨
data：不 commit
broker：read-only
```

如果時間不夠，優先順序如下：

```text
1. monthly_revenue local small smoke 成功
2. institutional_trading local single-date smoke 成功
3. surveillance / disposition 風控資料
4. margin_short / chip crowding
5. material_events / catalyst
6. corporate_actions
7. trading_calendar
8. valuation / symbol_master 補強
```

但請盡量一次完成完整資料來源層，不要再只做一點點。
