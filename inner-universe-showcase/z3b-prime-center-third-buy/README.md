# Z3B-Prime 中樞三買模型

本資料夾保存 `Z3B-Prime Center Third-Buy Model` 的量化模型規格與後續研發素材。

目前狀態：v1.4 台股整股 / 零股執行版規格已納入，獨立 Python package、資料載入、核心規則、狀態機、回測、CSV 輸出、SVG 視覺標註、台股整股 / 零股執行 profile 與單元測試已完成。

## 模型定位

`Z3B-Prime` 是由影片規則整理出的第三類買點多單模型。核心邏輯是先在 1H 趨勢週期確認價格向上離開中樞、回抽不跌破中樞上沿，再到 15m 交易週期確認回調結束後才開多。

本模型只用於交易規則量化、歷史回測、條件掃描與下單輔助研究，不提供個股投資建議、不保證收益。

## 來源文件

- `docs/Z3B_Prime_中樞三買量化模型規格_v1_1.md`
- `docs/Z3B_Prime_中樞三買量化模型規格_v1_1.docx`
- `docs/Z3B_Prime_中樞三買量化模型規格_v1_4_台股整股零股執行版.md`
- `docs/Z3B_Prime_中樞三買量化模型規格_v1_4_台股整股零股執行版.docx`
- `RULES.md`：目前保存 v1.4 規格，作為最新人讀規則入口。

## 快速開始

```powershell
cd "C:\Users\User\Documents\New project 6\z3b-prime-center-third-buy"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
python -m pytest
```

## 執行範例回測

本專案內有一組 synthetic sample，只用於驗證流程，不代表真實標的或績效。

```powershell
cd "C:\Users\User\Documents\New project 6\z3b-prime-center-third-buy"
$env:PYTHONPATH="src"
python -m z3b_prime.cli `
  --bars-15m data/sample/TEST_15m.csv `
  --bars-1h data/sample/TEST_1h.csv `
  --config config/sample.synthetic.yaml `
  --symbol TEST `
  --output reports/sample_run
```

輸出：

```text
reports/sample_run/
  signal_log.csv
  trade_log.csv
  performance_report.md
  annotated_chart.svg
```

台股 v1.4 config 已放在：

```text
config/Z3B_Prime_v1_4_tw_round_lot_config.yaml
config/Z3B_Prime_v1_4_tw_odd_lot_config.yaml
```

整股與零股績效請分開跑、分開看，不要混算。

## 目前資料夾結構

```text
z3b-prime-center-third-buy/
  README.md
  RULES.md
  pyproject.toml
  requirements.txt
  config/
  docs/
  data/
  reports/
  scripts/
  src/
  tests/
```

## 已完成的第一版核心

- 獨立 `z3b_prime` Python package。
- 設定檔範例：`config/config.example.yaml`。
- Synthetic 範例設定：`config/sample.synthetic.yaml`。
- v1.4 台股整股 config 與零股 config。
- CSV OHLCV loader，可讀 1H / 15m；若只有 15m，也可 resample 成 1H。
- 核心資料類別：`Bar`、`SwingPoint`、`Center`、`Leg`、`TradeSignal`。
- MACD DIF / DEA 與零軸診斷分類；預設只做 diagnostic，不阻擋交易。
- confirmed swing point 偵測與 confirmation delay。
- price-based 中樞候選偵測。
- a / b、b-a / b-b、b-A smaller-than-A、兩次孤立低點不破、多頭趨勢 K 等核心規則。
- entry 使用下一根 15m open；停損使用 v1.4 的 `golden_k.low`；停利使用 1H target high。
- 台股整股 / 零股 quantity sizing、marketable limit / odd-lot limit、滑價、手續費與交易稅模擬。
- 同根同時碰停損與停利時採 stop first。
- 狀態機與 early bullish K rejection。
- 回測 SL / TP，輸出 `signal_log.csv`、`trade_log.csv`、`performance_report.md`。
- SVG 視覺標註，標出 entry / SL / TP 與 MACD diagnostic 標籤。
- 29 個單元測試。

## 後續建議

1. 用真實 1H / 15m 台股資料跑 smoke，人工抽查每筆中樞、a/b、b-A、golden K、entry / SL / TP。
2. 視需要加入更完整的績效統計，例如最大回撤、連續虧損、分年度表現。
3. 視需要把 SVG 標註升級為互動式 HTML 圖表。
4. 若未來要改 MACD 為硬條件，必須先更新 `RULES.md`，不能直接在程式裡偷偷改。
5. 若交易所規則、券商 API、手續費折扣或稅率更新，需同步更新 v1.4 台股 config。
