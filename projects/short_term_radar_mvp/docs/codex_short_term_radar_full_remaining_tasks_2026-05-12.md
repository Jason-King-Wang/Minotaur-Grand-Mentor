# Codex 銝甈⊥批??港遙??嚗蝺?? Smoke ??脣?舐 Semi-Full / Full 鞈??琿?

?交?嚗?026-05-12
Repo嚗Jason-King-Wang/Minotaur-Grand-Mentor`
?桀??格? PR嚗R #4
?桀? base嚗short-term-radar`
?桀? head嚗codex/cl5-official-backfill`

---

## 0. 隞餃?蝮質牧??
?銝隞賭?甈⊥批??港遙??銝撠耨撠?隞餃???
?桀??剔??琿?撌脩?摰?嚗?
- repo scope 靽格迤
- simple mode ?航?
- robot slots ?嗆?
- ScoreBreakdown
- baseline comparison
- report
- monthly revenue official smoke
- institutional trading official parser / collector smoke
- Shioaji / SinoPac injected API read-only hooks
- full mode guard
- root pollution guard

雿?????甇????函? semi-full / full radar嚗??嚗?
1. 敺?鞈?靘?隞??candidate URL ??smoke parser??2. 蝻箏?蝛拙? official fetcher / parser / collector??3. 蝻箏?撖阡? local small-smoke processed parquet??4. 蝻箏?鈭僑??瘚???5. 蝻箏? scan 敺?slot status 撽???6. 蝻箏?鞈??釭??coverage ?梯”??撖阡?霅?7. 蝻箏????脖?????甇???`REVENUE_SLOT`?CHIP_SLOT`?SURVEILLANCE_SLOT`?CATALYST_SLOT` 蝑?slot 敺?partial/missing 霈? installed??
?砌遙?璅?

> 銝甈⊥扳??剔??琿?鞈?靘?撅文?摰嚗??嫣?皞?parser / collector / normalize / validate / upsert / coverage / small-smoke / backfill plan / slot status verification嚗?質?朣?臭誑敺?simple mode 敺 semi-full / full mode ????
---

## 1. ?擃′?扯???scope 銝?

??蝺??摰孵?賢嚗?
```text
projects/short_term_radar_mvp/
```

蝯?銝?啣??耨?寞??剔??琿??券? root files嚗?
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

root `README.md` 敹?蝬剜? Minotaur Grand Mentor / VTuber 撠??批捆??
敹?靽?銝血?撘瘀?

```text
projects/short_term_radar_mvp/tests/short_term_radar/test_scope_guard.py
```

scope guard 敹??脫迫嚗?
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

## 2. 銝 commit ?镼?
銝 commit嚗?
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

?迂 commit嚗?
```text
projects/short_term_radar_mvp/data/quality/.gitkeep
projects/short_term_radar_mvp/tests/fixtures/
撠? mock/sample fixture
撠? sample report
source code
tests
README / handoff
example config
```

憒? local smoke ?Ｙ? processed parquet嚗?賢?祆?撽?嚗???commit??
---

## 3. Broker / Shioaji / SinoPac 摰閬?

broker source ?芾 read-only??
?臭誑嚗?
```text
雿輻 externally managed API object
api.notice()
api.punish()
api.credit_enquires()
api.short_stock_sources()
api.kbars()
api.snapshots()
api.ticks()
api.daily_quotes()
api.scanners()
霈 contract metadata
```

銝?啣?嚗?
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
隞颱?銝 / ?孵 / ?芸 / 撣單 / ?其? / ???亥岷
敺?.env 霈 broker credential
?批遣?餃瘚?
```

敹?靽?皜祈岫蝣箄? production code 銝隞乩? forbidden methods?葫閰?fake method ?臭誑摮嚗?敹??胯鋡怠?怠停 fail??皜祈岫?券?
---

## 4. 璅∪?銵銝?游?

?∟?鞈?????朣?

- `scan` 銝 crash
- `backtest` 銝 crash
- `report` 銝 crash
- 蝻箄?????蝷?degraded
- 蝻?revenue 銝??S3 candidate_entry
- ?蔭銝剖??撥??S5 avoid_chasing
- partial slots 銝閫貊 `full_short_term_radar`
- simple mode 敹?蝜潛??航?
- score 銝?蝻箄??◤??摰擃?
- no future leakage 敹?靽?

---

## 5. ?祈憚蝮賢??璅?
隢?甈∪??誑銝蜓蝺?

```text
A. local config / local smoke 瘚?鋆?
B. monthly_revenue 摰 official source 撠????C. institutional_trading 摰 official source 撠????D. margin_short official source parser / collector
E. surveillance_daily official source parser / collector
F. material_events official source parser / collector
G. corporate_actions official source parser / collector
H. trading_calendar official source parser / collector
I. valuation / symbol_master 鋆撥
J. coverage / freshness / missing report ?祕?舐
K. scan slot status 撽?
L. backtest / baseline 銝憯?M. handoff / README 摰?湔
N. ?蝯??嗉??
```

---

# A. Local Config / Smoke Workflow

## A1. 撱箇? local.yaml ?Ｙ??孵?嚗?銝 commit local.yaml

?桀? PR 隤?`configs/short_term_radar/local.yaml` 銝??剁?撠?⊥?頝?normalize/write local small-smoke??
隢???

1. 蝣箄? `configs/short_term_radar/local.yaml.example` 頞喳?皜???2. 鋆?畾?README / handoff ?誘嚗?閮港蝙?刻?雿? example 銴ˊ?璈?local.yaml??3. 銝 commit local.yaml??4. ???smoke command 敹??賜 local.yaml.example dry-run??5. ?亥??迤撖急璈?processed parquet嚗???local.yaml??
撱箄降?辣?誘嚗?
```powershell
cd C:\Users\User\Documents\New project 4\projects\short_term_radar_mvp
Copy-Item configs\short_term_radar\local.yaml.example configs\short_term_radar\local.yaml
```

local.yaml ?府霈蝙?刻身摰?

```yaml
data_root: C:\Users\User\Documents\New project 4\data
existing_daily_price_path: C:\Users\User\Documents\New project 4\data\processed\prices_daily.parquet
```

雿?閬???local.yaml commit??
## A2. TLS / certificate fallback

TWSE institutional live fetch ?箇??

```text
CERTIFICATE_VERIFY_FAILED
```

隢?閬 unsafe global disable SSL verification??
隢?嚗?
1. fetch error 敹? degraded cleanly??2. README / handoff 閮? TLS issue ???撘?3. 憒??賢??刻圾瘙綽??∠ Python / certifi 璅??孵???4. ?乩??質圾瘙綽?靽? degraded message嚗? crash??5. 銝?箔???皜祈岫?? SSL 撽???6. 皜祈岫閬???fetch degraded path??
---

# B. Monthly Revenue 摰??
## B1. ?格?

??`monthly_revenue` ?嚗?
- official MOPS source request 摰
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

## B2. 敹??舀 command

Dry-run嚗?
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

Local small smoke嚗?
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

Five-year command must be documented but not automatically run in tests嚗?
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

## B3. 敹?靽? no future leakage

閬?嚗?
```text
銝??fetched_at ??announce_date
?亙??寞???嚗?  announce_date = next_month_day_10(revenue_month)
  announce_date_source = inferred_next_month_day_10
  announce_date_inferred = true
```

?葫??

```text
only rows where announce_date <= as_of_date
```

## B4. 皜祈岫

敹???

```text
test_monthly_revenue_official_fetcher.py
test_no_future_leakage_revenue.py
test_collect_cli.py
test_processed_storage_upsert.py
```

閬?嚗?
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

# C. Institutional Trading 摰??
## C1. ?格?

?桀?撌脫憓?

```text
institutional_trading_official.py
twse_institutional_trading_fetcher.py
tpex_institutional_trading_fetcher.py
twse_t86_sample.json
tpex_3insti_sample.json
```

隢匱蝥??啁?甇??剁?

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

## C2. 敹?頛詨甈?

?喳?嚗?
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

憒?靘??芣? net嚗??賭?憛?buy/sell ??0嚗撩?潸? null??
## C3. 敹??舀 command

Dry-run嚗?
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

Local single-date smoke嚗?
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

Date range command should be supported or explicitly rejected if not yet implemented嚗?
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

憒? range mode 撠撖虫?嚗???蝣箏?荔?銝 silently ignore嚗?
```text
institutional_trading range collect not implemented yet; use --date for single-day smoke
```

## C4. 皜祈岫

敹???

```text
test_institutional_trading_official_fetcher.py
test_institutional_trading_normalizer.py
test_collect_cli.py
test_processed_storage_upsert.py
```

閬?嚗?
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

# D. Margin / Short 摰??
## D1. ?格?

撱箇? official source parser / collector嚗??臬??broker read-only current hook??
?桀?靘??嚗?
TWSE嚗?
```text
https://openapi.twse.com.tw/v1/exchangeReport/MI_MARGN
https://openapi.twse.com.tw/v1/SBL/TWT96U
```

TPEx嚗?
```text
https://www.tpex.org.tw/openapi/v1/tpex_mainboard_margin_balance
https://www.tpex.org.tw/openapi/v1/tpex_margin_sbl
```

?祈憚隢???

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

## D2. 敹?頛詨甈?

?喳?嚗?
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

憒???API 瘝??券甈?嚗撩??null嚗??臭?憛?0??
## D3. command

Dry-run嚗?
```powershell
py -3.14 -m short_term_radar.cli.collect `
  --config configs\short_term_radar\data_sources.example.yaml `
  --dataset margin_short `
  --market all `
  --date 2026-04-30 `
  --source official `
  --dry-run
```

Local smoke嚗?
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

?啣?嚗?
```text
test_margin_short_official_fetcher.py
test_margin_short_normalizer.py
test_collect_cli.py
```

閬?嚗?
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

# E. Surveillance / Attention / Disposition 摰??
## E1. ?格?

?蔭鞈??舐蝺?◢?扳敹??? `SURVEILLANCE_SLOT` 敺?partial 敺 installed ?券脯?
?桀?撌脫?嚗?
- Shioaji read-only `notice()` / `punish()` hooks
- TPEx attention/disposition skeleton
- `disposition_active_flag` gating
- ?蔭銝剖撥??S5

?撩嚗?
- official source parser
- direct download/api_url support
- attention/disposition period parsing
- local smoke
- processed table upsert

## E2. 靘?

TPEx candidate嚗?
```text
attention dataset 11395
disposition dataset 11396
```

TWSE free endpoint 撠?Ⅱ嚗?芾??eShop ??broker current hook嚗???蝣箸?閮鳴?

```text
TWSE historical surveillance source unresolved
```

雿?閬?鋆?installed??
## E3. 敹?頛詨甈?

?喳?嚗?
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

??嚗?
```text
as_of_date ??disposition_start <= as_of_date <= disposition_end ??
  disposition_active_flag = true
  stage = S5
  entry_zone = avoid_chasing
```

## E4. command

Dry-run嚗?
```powershell
py -3.14 -m short_term_radar.cli.collect `
  --config configs\short_term_radar\data_sources.example.yaml `
  --dataset surveillance `
  --market all `
  --date 2026-04-30 `
  --source official `
  --dry-run
```

Local smoke嚗?
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

敹???

```text
test_surveillance_official_fetcher.py
test_surveillance_normalizer.py
test_disposition_blocks_candidate_entry.py
test_stage_gating_with_missing_data.py
```

閬?嚗?
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

# F. Material Events / Catalyst 摰??
## F1. ?格?

撱箇? MOPS material events official fetcher / parser嚗? CATALYST_SLOT 敺?partial 敺 installed ?券脯?
靘??嚗?
TWSE嚗?
```text
https://openapi.twse.com.tw/v1/opendata/t187ap04_L
```

TPEx嚗?
```text
https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap04_O
```

## F2. 敹?頛詨甈?

?喳?嚗?
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

event_type ?郊??嚗?
```text
瘜牧
?亙
雿菔頃
憓?
皜?
??鞈
閮渲?
?極
鞎⊥葫
?
?Ｗ?
??
??????嗡?
```

## F3. command

Dry-run嚗?
```powershell
py -3.14 -m short_term_radar.cli.collect `
  --config configs\short_term_radar\data_sources.example.yaml `
  --dataset material_events `
  --market all `
  --date 2026-04-30 `
  --source official `
  --dry-run
```

Local smoke嚗?
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

?啣?嚗?
```text
test_material_events_official_fetcher.py
test_material_events_classifier.py
test_catalyst_adapter.py
```

閬?嚗?
- TWSE material event payload
- TPEx material event payload
- date parse
- symbol parse
- event classifier
- positive / negative / neutral
- no future leakage
- degraded when source unavailable

---

# G. Corporate Actions 摰??
## G1. ?格?

撱箇? corporate actions official fetcher / parser??
靘??嚗?
TWSE嚗?
```text
https://openapi.twse.com.tw/v1/exchangeReport/TWT48U_ALL
https://openapi.twse.com.tw/v1/opendata/t187ap45_L
```

TPEx嚗?
```text
https://www.tpex.org.tw/openapi/v1/tpex_exright_prepost
https://www.tpex.org.tw/openapi/v1/tpex_exright_daily
```

## G2. 甈?

?喳?嚗?
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

action_type嚗?
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

?啣?嚗?
```text
test_corporate_actions_official_fetcher.py
test_corporate_actions_normalizer.py
```

閬?嚗?
- ex-dividend
- ex-right
- capital reduction
- date normalization
- symbol normalization
- missing fields null
- source degraded

---

# H. Trading Calendar 摰??
## H1. ?格?

?桀? coverage/backtest 銝餉?敺?`prices_daily` ?其漱?嚗隞亦 fallback嚗? full radar ?? official calendar??
靘??嚗?
```text
https://openapi.twse.com.tw/v1/holidaySchedule/holidaySchedule
```

## H2. 甈?

```text
trade_date
is_trading_day
market
holiday_name
source
source_url
fetched_at
```

## H3. ?摩

coverage expected dates嚗?
1. ?芸???official `trading_calendar`
2. ?亦撩嚗蝙??`prices_daily` ?????3. ?亙?蝻綽?? weekday fallback

銝?望??missing??
## H4. tests

?啣?嚗?
```text
test_trading_calendar_official_fetcher.py
test_coverage_reports.py
```

閬?嚗?
- holiday parse
- weekend exclude
- prices_daily fallback
- weekday fallback
- event-driven dataset 銝?瘙?daily coverage

---

# I. Valuation / Symbol Master 鋆撥

## I1. ?格?

隡啣潸??⊥鞈??舀嚗?
- 撣?- PE
- PB
- ?⊥
- ?Ｘ平
- 撣
- symbol metadata

靘??撌脣 config??
TWSE嚗?
```text
BWIBBU_d
t187ap03_L
```

TPEx嚗?
```text
tpex_mainboard_peratio_analysis
tpex_daily_market_value
mopsfin_t187ap03_O
```

## I2. 甈?

valuation_daily嚗?
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

symbol_master嚗?
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

?啣???撘瘀?

```text
test_symbol_master_official_fetcher.py
test_valuation_official_fetcher.py
test_symbol_master_normalizer.py
test_valuation_normalizer.py
```

---

# J. Coverage / Freshness / Missing Reports

## J1. ?格?

霈?coverage 銝??dry-run嚗???臭誑?Ｗ嚗?
```text
data/quality/data_coverage_report.csv
data/quality/missing_dates_report.csv
data/quality/freshness_report.csv
```

瘜冽?嚗? generated report ?臭誑??local ?Ｙ?嚗??日??臬???sample嚗?閬?commit 憭折??梯”??
## J2. 敹??舀

```powershell
py -3.14 -m short_term_radar.cli.coverage `
  --config configs\short_term_radar\local.yaml `
  --start 2021-01-01 `
  --end 2026-05-11 `
  --write-reports
```

## J3. 閬?

- daily datasets ??trading calendar / prices_daily / weekday fallback
- monthly datasets ??month range
- event-driven datasets 銝?瘙?憭拇?鞈?
- source_missing 閬? missing_dates ???- stale / fresh 閬?蝣?- processed table 銝??刻? degraded嚗? crash

---

# K. Scan Slot Status 撽?

## K1. ?格?

瘥?摰???processed table嚗?蝣箄? scan output ??slot ???霈?
敹??啣??Ⅱ隤?scan output ?嚗?
```text
mode
robot_slot_statuses
robot_slot_coverage_ratio
score_data_coverage_ratio
available_radars
degraded_radars
core_data_ready_flag
```

## K2. 敹葫??

1. ?芣? price嚗?   - `simple_price_volume_mode`
   - revenue degraded
   - core_data_ready false
   - 銝 S3

2. price + monthly_revenue嚗?   - REVENUE_SLOT installed
   - revenue score ??
   - ??surveillance missing嚗?銝?漲璅?

3. price + revenue + surveillance嚗?   - semi_full_short_term_radar
   - ?仿??蔭銝哨??臬?閮望擃?stage
   - ?亥?蝵桐葉嚗???S5

4. all full slots installed嚗?   - full_short_term_radar
   - partial 銝閫貊 full

## K3. tests

?啣???撘瘀?

```text
test_pipeline_score_breakdown.py
test_stage_gating_with_missing_data.py
test_disposition_blocks_candidate_entry.py
test_slot_status_transitions.py
```

---

# L. Backtest / Baseline 銝?游?

敹?靽?嚗?
```text
radar_model
random_top_n
breakout_120d_only
volume_expansion_only
ma_alignment_only
```

`breakout_120d_only` 敹??芰?嚗?
```text
breakout_120d_flag == true
```

backtest CLI 敹?靽?嚗?
```text
--include-baselines
--random-seed
```

撽?嚗?
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

憒? local data 銝??剁??喳? dry-run / test path 銝憯???
---

# M. README / Handoff ?湔

敹??湔嚗?
```text
projects/short_term_radar_mvp/README.md
projects/short_term_radar_mvp/SHORT_TERM_RADAR_HANDOFF.md
```

?批捆閬??恬?

1. ?桀?摰??芯? official sources
2. ?芯???dry-run
3. ?芯???local small smoke
4. ?芯??臭?撟?backfill
5. ?芯?隞??candidate
6. ?芯? slot ??installed / partial / missing
7. 憒?撱箇? local.yaml
8. 銝 commit ?芯? local data
9. TLS / endpoint issue
10. 銝?甇交?雿?
銝???handoff 撖急?銝?芋蝟餈堆?閬霈?銝????交??
---

# N. ?蝯?霅?隞?
敺?

```powershell
cd C:\Users\User\Documents\New project 4\projects\short_term_radar_mvp
```

?瑁?嚗?
## N1. ?箸撽?

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

憒??祆?撱箇?鈭?local.yaml嚗?頝?

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

蝣箄?嚗?
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

# O. ??澆?

摰?敺??其誑銝撘??梧?

```text
Scope
- changed files ?臬?券??projects/short_term_radar_mvp/
- root README ?臬 untouched
- root pollution guard ?臬??
- ?臬??commit raw/processed/local.yaml/secrets

Implemented Sources
- monthly_revenue: dry-run / smoke / parser / validate / upsert ???- institutional_trading: dry-run / smoke / parser / validate / upsert ???- margin_short: dry-run / smoke / parser / validate / upsert ???- surveillance: dry-run / smoke / parser / validate / upsert ???- material_events: dry-run / smoke / parser / validate / upsert ???- corporate_actions: dry-run / smoke / parser / validate / upsert ???- trading_calendar: dry-run / smoke / parser / validate / upsert ???- valuation/symbol_master: ???
Validation
- compileall result
- pytest result
- dry-run commands result
- local small-smoke result
- scan slot status result
- coverage result
- git diff --check result

Data
- ?臬?Ｙ? local raw/processed
- ?臬蝣箄???commit raw/processed
- 瘥?processed table local rows count
- 瘥?processed table quality result

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
- ?芯? source ???candidate
- ?芯? parser ????- ?芯? live fetch ?? TLS / endpoint issue
- ?芯??芾 degraded
- ?臬????full mode

Risks
- endpoint 銝帘
- 甈? mapping 銝Ⅱ摰?- TLS / certificate
- official source unavailable
- Shioaji current-only limitations
```

---

# P. Merge / PR ???
?砌遙????嚗R #4 ?臭誑蝜潛? draft??
摰?敺?

1. PR #4 敺?draft 頧?ready??2. 蝣箄? mergeable??3. ??merge PR #4 into `short-term-radar`??4. ???PR #3??5. PR #3 ??merge into `main`??
銝?頝喲? PR #4 ?湔?? PR #3??
---

# Q. ?蝯璅?蝢?
?祈憚摰?敺????嚗?
```text
simple mode嚗帘摰頝?monthly_revenue嚗fficial smoke + local small processed ??
institutional_trading嚗fficial smoke + local small processed ??
margin_short嚗fficial parser / dry-run / small smoke ?喳??典???
surveillance嚗fficial/broker read-only parser / dry-run / small smoke ?喳??典???
material_events嚗fficial parser / dry-run ?舐
corporate_actions嚗fficial parser / dry-run ?舐
trading_calendar嚗fficial parser / fallback ?摩?舐
coverage reports嚗?Ｗ
scan嚗?? slot ?????tests嚗??root嚗嗾瘛?data嚗? commit
broker嚗ead-only
```

憒???銝?嚗??摨?銝?

```text
1. monthly_revenue local small smoke ??
2. institutional_trading local single-date smoke ??
3. surveillance / disposition 憸冽鞈?
4. margin_short / chip crowding
5. material_events / catalyst
6. corporate_actions
7. trading_calendar
8. valuation / symbol_master 鋆撥
```

雿??⊿?銝甈∪????渲???皞惜嚗?閬??芸?銝暺???