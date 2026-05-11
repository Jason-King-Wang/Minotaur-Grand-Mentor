# 這是短線雷達的資料收集與來源建置規格

這是 **台股短線雷達** 的資料收集與來源建置規格。目標不是做長期十倍股模型，而是把目前 `projects/short_term_radar_mvp/` 的價量型 MVP 升級成可支援「半年內 3–5 倍或以上候選股」的中短線雷達。這份文件要交給 Codex 執行，請一次性建立資料收集層、正規化 schema、資料品質檢查、CLI、測試與文件。

---

## 0. 給 Codex 的硬性底線

請先遵守這些規則，再開始任何修改：

1. **不要改到其他已有的內容。**
2. **如果需要別的 project 的工具，就複製一份過來用。**
3. 只允許修改或新增 `projects/short_term_radar_mvp/` 底下的內容。
4. 不要移動、刪除、覆蓋牛頭人原本的 VTuber / overlay / docs / assets / dashboard / records 內容。
5. 不要上傳或提交 `.env`、token、憑證、API key、`shioaji.log`、Discord bot runtime、下載資料夾、sqlite、cache、大型 raw data 或任何無關本地檔案。
6. Broker API 只能做 **read-only market data**。不得新增下單、改單、刪單、查帳戶敏感資訊、部位、庫存、損益或任何交易動作。
7. 所有資料 ingestion 要能 graceful degradation：缺資料時不能中斷整個 scan/backtest，但要清楚標記 missing source / degraded radar。
8. 回測與 feature 計算不得有未來資料洩漏。所有 feature 必須以 `as_of_date` 與實際 `announce_date` 控制可用性。
9. Raw data 盡量放本機，不要 commit。GitHub 只保留 source code、schema、sample 小檔、README、tests、config example。

---

## 1. 目前狀態與這次任務

目前短線雷達 MVP 已有：

```text
projects/short_term_radar_mvp/
  short_term_radar/
  configs/short_term_radar/
  tests/short_term_radar/
  reports/short_term_radar/
```

目前核心是價量雷達，已能跑：

```powershell
py -3.14 -m short_term_radar.cli.scan
py -3.14 -m short_term_radar.cli.backtest
py -3.14 -m short_term_radar.cli.report
```

但是現在仍缺短線 3–5 倍雷達最重要的資料：

```text
月營收
三大法人
融資融券 / 借券
注意股 / 處置股
重大訊息 / 催化劑
公司基本資料 / 股本 / 產業
除權息 / 股本事件
季報財報
董監持股 / 質押
估值 / 市值
```

本次任務：

```text
建立 short_term_radar 的資料收集層與資料來源設定。
不要先做複雜模型；先把資料能穩定收、正規化、檢查、輸出、接到既有 pipeline 的 adapter。
```

---

## 2. 短線雷達為什麼需要這些資料

短線雷達的核心不是找「好公司」，而是找：

```text
基本面開始變好
市場還半信半疑
價量剛開始被資金重新定價
法人或主力開始認同
散戶籌碼還沒過熱
接下來 1–6 個月仍有催化劑
注意 / 處置 / 融資過熱風險可控
```

短線雷達公式：

```text
半年多倍股候選 =
  月營收/基本面拐點
+ 市場預期差
+ 價量突破
+ 法人/籌碼確認
+ 題材/族群擴散
+ 催化劑
- 擁擠度與交易風險
```

因此資料收集層要服務這些 feature：

```text
revenue_features
chip_features
price_volume_features
catalyst_features
surveillance_risk_features
corporate_action_features
valuation_size_features
financial_leverage_features
```

---

## 3. 目標資料來源總表

請優先使用官方來源、政府開放資料、TWSE、TPEx、公開資訊觀測站、券商 API 的 read-only market data。第三方網站只能做備援，不要當第一來源。

### P0：一定要做，沒有這些短線雷達不完整

| 優先級 | 資料 | 用途 | 主要來源 |
|---|---|---|---|
| P0 | 既有 5 年全台股日線 | 回測、價量、forward label | 使用本機既有資料 |
| P0 | 每日日線增量 | 每日 scan | TWSE 個股日成交資訊、TPEx 上櫃股票收盤行情、券商 API read-only |
| P0 | 公司基本資料 | universe、產業、股本、上市櫃日期、彈性股篩選 | data.gov.tw / TWSE / TPEx |
| P0 | 月營收 | 基本面拐點、營收加速度、營收驚喜 | 上市 / 上櫃每月營業收入彙總表 |
| P0 | 三大法人 | 法人剛進場、投信連買、籌碼驗證 | TWSE / TPEx |
| P0 | 融資融券 / 借券 | 擁擠度、散戶追高、軋空條件 | TWSE / TPEx / 券商 API read-only |
| P0 | 注意股 / 處置股 | 短線風控、過熱、S5 avoid_chasing | TWSE / TPEx |
| P0 | 除權息 / corporate actions | 回測修正、價格跳動辨識 | TWSE / TPEx |
| P0 | 重大訊息 | 催化劑與風險事件 | data.gov.tw / MOPS |

### P1：強烈建議做，接上後雷達可信度會大幅提高

| 優先級 | 資料 | 用途 | 主要來源 |
|---|---|---|---|
| P1 | 季報 / 財報 | 毛利率、營益率、EPS 轉正、盈利槓桿 | data.gov.tw / MOPS |
| P1 | 董監持股 / 質押 | 治理風險、質押風險 | data.gov.tw |
| P1 | PE / PB / 殖利率 / 市值 proxy | 估值過熱、大型股排除、市值分層 | data.gov.tw / TWSE / TPEx |
| P1 | 上市櫃開休市日曆 | collector 排程、交易日判斷 | TWSE / TPEx / 本機日線推導 |

### P2：之後再做，先不要拖慢 MVP

| 優先級 | 資料 | 用途 | 備註 |
|---|---|---|---|
| P2 | 新聞 | 題材熱度、預期擴散 | 噪音高、授權複雜 |
| P2 | 社群熱度 | 市場心理 | 先不要做爬蟲式重工程 |
| P2 | 分析師覆蓋 | 預期差 | 多數來源偏付費 |
| P2 | 產業供應鏈 mapping | 題材擴散 | 可先手動維護 |

---

## 4. 官方資料來源清單

請把這些來源寫進 `configs/short_term_radar/data_sources.example.yaml`，但不要把任何私密憑證放進去。

### 4.1 日線 OHLCV

#### TWSE 上市個股日成交資訊

- Dataset：盤後資訊 > 個股日成交資訊
- URL：https://data.gov.tw/dataset/11549
- 主要欄位：日期、證券代號、證券名稱、成交股數、成交金額、開盤價、最高價、最低價、收盤價、漲跌價差、成交筆數
- 頻率：每日
- 用途：上市股票 OHLCV 增量

#### TPEx 上櫃股票收盤行情

- Dataset：上櫃股票收盤行情
- URL：https://data.gov.tw/dataset/11371
- TPEx page：https://www.tpex.org.tw/zh-tw/mainboard/trading/info/pricing.html
- 主要欄位：資料日期、代號、名稱、收盤、漲跌、開盤、最高、最低、成交股數、成交金額、成交筆數、發行股數、次日漲停價、次日跌停價
- 頻率：每日
- 用途：上櫃股票 OHLCV 增量

### 4.2 公司基本資料 / Universe

#### TWSE 上市公司基本資料

- Dataset：上市公司基本資料
- URL：https://data.gov.tw/dataset/18419
- 主要欄位：公司代號、公司名稱、公司簡稱、產業別、成立日期、上市日期、實收資本額、已發行普通股數或 TDR 原股發行股數、外國企業註冊地國
- 用途：上市股票 universe、產業、股本彈性、大型股過濾、KY 辨識

#### TPEx 上櫃公司基本資料

- Dataset：上櫃公司基本資料
- URL：https://data.gov.tw/dataset/25036
- 主要欄位：公司代號、公司名稱、公司簡稱、產業別、成立日期、上櫃日期、實收資本額、已發行普通股數或 TDR 原股發行股數、外國企業註冊地國
- 用途：上櫃股票 universe、產業、股本彈性、大型股過濾、KY 辨識

### 4.3 月營收

#### TWSE 上市公司每月營業收入彙總表

- Dataset：上市公司每月營業收入彙總表
- URL：https://data.gov.tw/dataset/18420
- 主要欄位：出表日期、資料年月、公司代號、公司名稱、產業別、營業收入-當月營收、營業收入-上月營收、營業收入-去年當月營收、營業收入-上月比較增減(%)、營業收入-去年同月增減(%)、累計營業收入-當月累計營收、累計營業收入-去年累計營收、累計營業收入-前期比較增減(%)、備註
- 用途：月營收 YoY、MoM、3M/6M YoY、營收加速度、營收創高

#### TPEx 上櫃公司每月營業收入彙總表

- Dataset：上櫃公司每月營業收入彙總表
- URL：https://data.gov.tw/dataset/56510
- 主要欄位同上市月營收
- 用途：月營收 YoY、MoM、3M/6M YoY、營收加速度、營收創高

### 4.4 三大法人

#### TWSE 三大法人買賣超

- 優先：TWSE 官方 API / 官網查詢；若需要完整歷史與格式穩定，可用 TWSE Data E-Shop。
- TWSE Data E-Shop daily / weekly institutional detail products may require subscription.
- 範例產品：三大法人買賣超週報
- URL：https://eshop.twse.com.tw/zh/product/detail/010ebd2cdb854169bb8707378f75b12a
- 主要欄位：外陸資買進/賣出、投信買進/賣出、自營商自行買賣買進/賣出、自營商避險買進/賣出、三大法人買賣超
- 用途：法人籌碼、投信連買、外資由賣轉買、自營商過熱

#### TPEx 三大法人買賣明細

- TPEx page：https://www.tpex.org.tw/zh-tw/mainboard/trading/major-institutional/detail/month.html
- Legacy page：https://www.tpex.org.tw/web/stock/3insti/daily_trade/3itrade.php
- 主要欄位：外資及陸資淨買股數、投信淨買股數、自營商淨買股數、三大法人買賣超股數合計
- 用途：上櫃三大法人日 / 週 / 月資料

### 4.5 融資融券 / 借券

#### TWSE 融資融券餘額

- TWSE page：https://www.twse.com.tw/zh/page/trading/exchange/MI_MARGN.html
- Data E-Shop：https://eshop.twse.com.tw/zh/product/detail/388dd3a09824427d8c01a9d2b21e820b
- 主要欄位：昨日融資餘額、今日融資買進、今日融資賣出、今日現金償還、今日融資餘額、昨日融券餘額、今日融券賣出、今日融券買進、今日現券償還、今日融券餘額、融資限制碼、融券限制碼
- 用途：融資暴增、融券軋空、短線擁擠度

#### TPEx 融資融券與借券

- TPEx page 可從上櫃交易資訊常用頁進入：
  - 上櫃股票行情：https://www.tpex.org.tw/zh-tw/mainboard/trading/info/pricing.html
  - 常用交易資訊包含：融資融券餘額表、融券借券賣出餘額、當日可借券賣出股數、有價證券借貸
- 用途：上櫃融資融券與借券賣出風險

### 4.6 注意股 / 處置股

#### TWSE 注意及處置股票統計資訊

- TWSE Data E-Shop：https://eshop.twse.com.tw/zh/product/detail/ac35dc52883d42c1a2eeacfa332f7e7f
- 主要欄位：注意股票代號、股票名稱、注意交易資訊；處置股票代號、股票名稱、條件、處置期間、處置措施
- 用途：S5 avoid_chasing、處置中禁止 S3、注意股風險扣分

#### TPEx 上櫃公布注意股票資訊

- Dataset：https://data.gov.tw/dataset/11395
- 主要欄位：公告日期、證券代號、證券名稱、注意交易資訊、收盤價、本益比
- 用途：上櫃注意股風控

#### TPEx 上櫃處置有價證券資訊

- Dataset：https://data.gov.tw/dataset/11396
- 主要欄位：公布日期、證券代號、證券名稱、處置起訖時間、處置原因、處置內容
- 用途：上櫃處置股風控

### 4.7 除權息 / Corporate Actions

#### TWSE 上市股票除權除息預告表

- Dataset：https://data.gov.tw/dataset/89748
- 主要欄位：除權息日期、股票代號、名稱、除權息、無償配股率、現金增資配股率、現金增資認購價、現金股利
- 用途：回測除權息標記、價格跳動辨識、股本事件

#### TPEx 上櫃股票除權除息計算結果表

- Dataset：https://data.gov.tw/dataset/11633
- 主要欄位：除權息日期、代號、名稱、除權息前收盤價、除權息參考價、權值、息值、現金股利、每仟股無償配股、現金增資股數、現金增資認購價
- 用途：回測除權息標記、價格跳動辨識、股本事件

### 4.8 重大訊息 / 催化劑

#### TWSE 上市公司每日重大訊息

- Dataset：https://data.gov.tw/en/datasets/18415
- 主要欄位：出表日期、發言日期、發言時間、公司代號、公司名稱、主旨、符合條款、事實發生日、說明
- 用途：重大事件、催化劑、風險公告、法說會、訂單、新產品、產能、財報事件

#### TPEx 上櫃公司每日重大訊息

- Dataset：https://data.gov.tw/dataset/18418
- 主要欄位：出表日期、發言日期、發言時間、公司代號、公司名稱、主旨、符合條款、事實發生日、說明
- 用途：重大事件、催化劑、風險公告、法說會、訂單、新產品、產能、財報事件

### 4.9 季報 / 財報

#### TWSE 上市公司綜合損益表一般業

- Dataset family：上市公司綜合損益表，一般業 / 金融業 / 保險業 / 證券期貨業等
- Example URL：https://data.gov.tw/dataset/91998
- 用途：營業收入、毛利、營業利益、稅前淨利、本期淨利、EPS、毛利率、營益率

#### TPEx 上櫃公司財報資訊一般業

- Dataset：https://data.gov.tw/dataset/94865
- 主要欄位：年度、季別、公司代號、公司名稱、營業收入、營業成本、營業毛利、營業費用、營業利益、稅前淨利、本期淨利、基本每股盈餘
- 用途：毛利率、營益率、EPS、虧轉盈、本業槓桿

### 4.10 董監持股 / 質押

#### TWSE 上市公司董監事持股餘額明細資料

- Dataset：https://data.gov.tw/dataset/22811
- 主要欄位：資料年月、公司代號、公司名稱、職稱、姓名、目前持股、設質股數、設質股數佔持股比例、內部人關係人目前持股合計、內部人關係人設質股數、內部人關係人設質比例
- 用途：高質押風險、治理風險

#### TPEx 上櫃公司董監事持股餘額明細資料

- Dataset：https://data.gov.tw/dataset/22812
- 主要欄位同上市董監持股
- 用途：高質押風險、治理風險

### 4.11 估值 / PE / PB / 殖利率

#### TWSE 上市個股 PE / PB / 殖利率

- Dataset by date：https://data.gov.tw/dataset/11764
- Dataset by code：https://data.gov.tw/dataset/11547
- 主要欄位：日期、證券代號、證券名稱、收盤價、殖利率、本益比、股價淨值比
- 用途：估值過熱、權值股分層、市值 proxy

#### TPEx 上櫃個股 PE / PB / 殖利率

- Dataset：https://data.gov.tw/dataset/11373
- 主要欄位：資料日期、股票代號、名稱、本益比、每股股利、殖利率、股價淨值比、財報年/季
- 用途：估值過熱、上櫃估值分層

---

## 5. 新增資料夾結構

請在 `projects/short_term_radar_mvp/` 內新增或整理以下結構：

```text
projects/short_term_radar_mvp/
  short_term_radar/
    data_sources/
      __init__.py
      base.py
      config.py
      fetchers/
        __init__.py
        http_fetcher.py
        local_file_fetcher.py
        broker_readonly_fetcher.py
      sources/
        __init__.py
        twse_open_data.py
        tpex_open_data.py
        twse_eshop.py
        mops_open_data.py
        broker_readonly.py
      normalizers/
        __init__.py
        common.py
        symbol_master.py
        prices_daily.py
        monthly_revenue.py
        institutional_trading.py
        margin_short.py
        surveillance.py
        corporate_actions.py
        material_events.py
        financials.py
        insider_holding.py
        valuation.py
      storage.py
      quality.py
      registry.py
    cli/
      collect.py
      normalize.py
      validate_data.py
      coverage.py
  configs/
    short_term_radar/
      data_sources.example.yaml
      local.yaml.example
  data/
    raw/
    processed/
    quality/
    samples/
  tests/
    short_term_radar/
      data_sources/
```

### Git ignore rule

更新 `projects/short_term_radar_mvp/.gitignore`：

```text
# Local data, never commit full raw/processed data
/data/raw/
/data/processed/
/data/cache/
/data/tmp/
/data/*.sqlite
/data/*.sqlite3

# Keep only small samples and quality report examples if explicitly created
!/data/samples/
!/data/samples/**
!/data/quality/.gitkeep

# Local config and secrets
configs/short_term_radar/local.yaml
.env
.env.*
*.log
shioaji.log
```

---

## 6. Config 設計

新增：

```text
configs/short_term_radar/data_sources.example.yaml
configs/short_term_radar/local.yaml.example
```

`local.yaml` 不得 commit。

### data_sources.example.yaml 範例

```yaml
data_root: ${TW_RADAR_DATA_ROOT:-data}
existing_daily_price_path: ${TW_EQUITIES_DATA_PATH:-}

fetch:
  user_agent: "short-term-radar-mvp/0.2"
  timeout_seconds: 30
  retry_count: 3
  sleep_seconds: 1.0
  respect_source_rate_limits: true

sources:
  twse:
    enabled: true
    open_data_base: "https://data.gov.tw"
    api_base: "https://openapi.twse.com.tw"
    datasets:
      prices_daily:
        dataset_id: 11549
        url: "https://data.gov.tw/dataset/11549"
      symbol_master:
        dataset_id: 18419
        url: "https://data.gov.tw/dataset/18419"
      monthly_revenue:
        dataset_id: 18420
        url: "https://data.gov.tw/dataset/18420"
      material_events:
        dataset_id: 18415
        url: "https://data.gov.tw/en/datasets/18415"
      corporate_actions:
        dataset_id: 89748
        url: "https://data.gov.tw/dataset/89748"
      insider_holding:
        dataset_id: 22811
        url: "https://data.gov.tw/dataset/22811"
      valuation_daily_by_date:
        dataset_id: 11764
        url: "https://data.gov.tw/dataset/11764"

  tpex:
    enabled: true
    open_data_base: "https://data.gov.tw"
    api_base: "https://www.tpex.org.tw/openapi"
    datasets:
      prices_daily:
        dataset_id: 11371
        url: "https://data.gov.tw/dataset/11371"
      symbol_master:
        dataset_id: 25036
        url: "https://data.gov.tw/dataset/25036"
      monthly_revenue:
        dataset_id: 56510
        url: "https://data.gov.tw/dataset/56510"
      material_events:
        dataset_id: 18418
        url: "https://data.gov.tw/dataset/18418"
      attention:
        dataset_id: 11395
        url: "https://data.gov.tw/dataset/11395"
      disposition:
        dataset_id: 11396
        url: "https://data.gov.tw/dataset/11396"
      corporate_actions:
        dataset_id: 11633
        url: "https://data.gov.tw/dataset/11633"
      insider_holding:
        dataset_id: 22812
        url: "https://data.gov.tw/dataset/22812"
      valuation_daily:
        dataset_id: 11373
        url: "https://data.gov.tw/dataset/11373"

  twse_eshop:
    enabled: false
    note: "Use only if official free endpoints are insufficient or a paid subscription exists. Do not hardcode credentials."
    datasets:
      surveillance:
        url: "https://eshop.twse.com.tw/zh/product/detail/ac35dc52883d42c1a2eeacfa332f7e7f"
      margin_short:
        url: "https://eshop.twse.com.tw/zh/product/detail/388dd3a09824427d8c01a9d2b21e820b"

  broker_api:
    enabled: false
    provider: "shioaji"
    readonly_only: true
    allow_order_methods: false
```

### local.yaml.example 範例

```yaml
data_root: "C:/Users/User/Documents/short_term_radar_data"
existing_daily_price_path: "C:/Users/User/Documents/New project 6/tw-golden-cross-star/data/tw_equities"

sources:
  broker_api:
    enabled: false
    provider: "shioaji"
    readonly_only: true
```

---

## 7. 正規化 Schema

請所有 collector 最後輸出 parquet。CSV 可作為 debug / sample，但 processed layer 以 parquet 為主。

### 7.1 `symbol_master.parquet`

```text
symbol: str
name: str
short_name: str | null
market: str                  # TWSE / TPEX / Emerging / Unknown
industry: str | null
listing_date: date | null
established_date: date | null
paid_in_capital: float | null
issued_shares: float | null
par_value: str | null
foreign_registration_country: str | null
is_ky: bool
is_etf: bool
is_warrant: bool
is_etn: bool
is_tdr: bool
is_common_stock: bool
is_full_delivery: bool | null
is_attention: bool | null
is_disposition: bool | null
source: str
source_url: str
fetched_at: datetime
```

### 7.2 `prices_daily.parquet`

```text
trade_date: date
market: str
symbol: str
name: str | null
open: float | null
high: float | null
low: float | null
close: float | null
change: float | null
volume: float | null          # shares
amount: float | null          # TWD
transactions: float | null
issued_shares: float | null
next_limit_up: float | null
next_limit_down: float | null
source: str
source_url: str
fetched_at: datetime
```

### 7.3 `monthly_revenue.parquet`

```text
revenue_month: str            # YYYYMM
announce_date: date | null    # 出表日期 / collector date if missing
market: str
symbol: str
name: str
industry: str | null
revenue_current: float | null
revenue_previous_month: float | null
revenue_last_year_same_month: float | null
revenue_mom_pct: float | null
revenue_yoy_pct: float | null
cumulative_revenue_current: float | null
cumulative_revenue_last_year: float | null
cumulative_yoy_pct: float | null
note: str | null
source: str
source_url: str
fetched_at: datetime
```

Important no-future rule:

```text
When scanning as_of_date, monthly revenue can only be used if announce_date <= as_of_date.
If announce_date is missing, infer conservatively:
  announce_date = first available fetched_at date if available
  otherwise use next month day 10 as fallback
Never use revenue_month alone as available date.
```

### 7.4 `institutional_trading_daily.parquet`

```text
trade_date: date
market: str
symbol: str
name: str | null
foreign_buy: float | null
foreign_sell: float | null
foreign_net: float | null
investment_trust_buy: float | null
investment_trust_sell: float | null
investment_trust_net: float | null
dealer_buy: float | null
dealer_sell: float | null
dealer_net: float | null
dealer_self_buy: float | null
dealer_self_sell: float | null
dealer_self_net: float | null
dealer_hedge_buy: float | null
dealer_hedge_sell: float | null
dealer_hedge_net: float | null
total_institutional_net: float | null
source: str
source_url: str
fetched_at: datetime
```

### 7.5 `margin_short_daily.parquet`

```text
trade_date: date
market: str
symbol: str
name: str | null
margin_buy: float | null
margin_sell: float | null
margin_redeem: float | null
margin_balance: float | null
margin_balance_prev: float | null
short_sell: float | null
short_cover: float | null
short_redeem: float | null
short_balance: float | null
short_balance_prev: float | null
short_margin_ratio: float | null
sbl_short_sell_volume: float | null
sbl_balance: float | null
sbl_short_sell_balance: float | null
margin_limit_code: str | null
short_limit_code: str | null
source: str
source_url: str
fetched_at: datetime
```

### 7.6 `surveillance_daily.parquet`

```text
trade_date: date
market: str
symbol: str
name: str | null
attention_flag: bool
attention_reason: str | null
attention_close: float | null
attention_pe: float | null
disposition_flag: bool
disposition_start: date | null
disposition_end: date | null
disposition_condition: str | null
disposition_reason: str | null
disposition_measure: str | null
attention_count_recent: int | null
source: str
source_url: str
fetched_at: datetime
```

Rules:

```text
if disposition_flag is true and as_of_date in [disposition_start, disposition_end]:
  candidate cannot be S3 candidate_entry
  entry_zone = avoid_chasing or risk_watch
  add risk flag: 處置中

if attention_flag is true:
  add risk flag: 注意股
  apply risk penalty
```

### 7.7 `corporate_actions.parquet`

```text
action_date: date
market: str
symbol: str
name: str | null
action_type: str | null       # ex_dividend / ex_right / capital_increase / split / reduction / unknown
cash_dividend: float | null
stock_dividend_ratio: float | null
capital_increase_ratio: float | null
subscription_price: float | null
reference_price: float | null
previous_close: float | null
right_value: float | null
interest_value: float | null
source: str
source_url: str
fetched_at: datetime
```

### 7.8 `material_events.parquet`

```text
announce_date: date
announce_time: str | null
market: str
symbol: str
name: str
title: str
rule_clause: str | null
event_date: date | null
description: str | null
event_type: str | null        # classifier output
catalyst_score: float | null
risk_score: float | null
source: str
source_url: str
fetched_at: datetime
```

Event classifier keyword buckets:

```text
investor_conference
monthly_revenue
earnings_release
major_order
new_product
capacity_expansion
customer_supply_chain
strategic_alliance
merger_acquisition
capital_increase
share_buyback
dividend
lawsuit
production_halt
regulatory_penalty
financial_warning
other
```

### 7.9 `financial_statement_quarterly.parquet`

```text
year: int
quarter: int
market: str
symbol: str
name: str
industry_type: str | null      # general / financial / insurance / securities / other
announce_date: date | null
revenue: float | null
cost: float | null
gross_profit: float | null
gross_margin: float | null
operating_expense: float | null
operating_profit: float | null
operating_margin: float | null
pretax_income: float | null
net_income: float | null
eps: float | null
source: str
source_url: str
fetched_at: datetime
```

### 7.10 `insider_holding_monthly.parquet`

```text
data_month: str               # YYYYMM
market: str
symbol: str
name: str
title: str | null
insider_name: str | null
shares_at_election: float | null
current_holding: float | null
pledged_shares: float | null
pledge_ratio: float | null
related_party_holding: float | null
related_party_pledged_shares: float | null
related_party_pledge_ratio: float | null
source: str
source_url: str
fetched_at: datetime
```

### 7.11 `valuation_daily.parquet`

```text
trade_date: date
market: str
symbol: str
name: str | null
close: float | null
pe: float | null
pb: float | null
dividend_yield: float | null
dividend_per_share: float | null
financial_year_quarter: str | null
market_cap: float | null       # derive if close * issued_shares available
source: str
source_url: str
fetched_at: datetime
```

---

## 8. Collector CLI 設計

新增 CLI：

```powershell
py -3.14 -m short_term_radar.cli.collect --config configs/short_term_radar/local.yaml --dataset symbol_master --market all
py -3.14 -m short_term_radar.cli.collect --config configs/short_term_radar/local.yaml --dataset prices_daily --market all --date 2026-05-11
py -3.14 -m short_term_radar.cli.collect --config configs/short_term_radar/local.yaml --dataset monthly_revenue --market all --month 202604
py -3.14 -m short_term_radar.cli.collect --config configs/short_term_radar/local.yaml --dataset institutional_trading --market all --date 2026-05-11
py -3.14 -m short_term_radar.cli.collect --config configs/short_term_radar/local.yaml --dataset margin_short --market all --date 2026-05-11
py -3.14 -m short_term_radar.cli.collect --config configs/short_term_radar/local.yaml --dataset surveillance --market all --date 2026-05-11
py -3.14 -m short_term_radar.cli.collect --config configs/short_term_radar/local.yaml --dataset corporate_actions --market all --date 2026-05-11
py -3.14 -m short_term_radar.cli.collect --config configs/short_term_radar/local.yaml --dataset material_events --market all --date 2026-05-11
```

Backfill commands:

```powershell
py -3.14 -m short_term_radar.cli.collect --config configs/short_term_radar/local.yaml --dataset prices_daily --market all --start 2021-01-01 --end 2026-05-11
py -3.14 -m short_term_radar.cli.collect --config configs/short_term_radar/local.yaml --dataset monthly_revenue --market all --start-month 202101 --end-month 202604
py -3.14 -m short_term_radar.cli.collect --config configs/short_term_radar/local.yaml --dataset institutional_trading --market all --start 2021-01-01 --end 2026-05-11
```

Normalize command:

```powershell
py -3.14 -m short_term_radar.cli.normalize --config configs/short_term_radar/local.yaml --dataset all
```

Quality validation:

```powershell
py -3.14 -m short_term_radar.cli.validate_data --config configs/short_term_radar/local.yaml --dataset all --as-of 2026-05-11
py -3.14 -m short_term_radar.cli.coverage --config configs/short_term_radar/local.yaml --start 2021-01-01 --end 2026-05-11
```

---

## 9. Storage 規範

Raw layer：

```text
data/raw/{source}/{dataset}/yyyy={YYYY}/mm={MM}/dd={DD}/raw.{csv|json|txt}
```

Processed layer：

```text
data/processed/symbol_master.parquet
data/processed/prices_daily.parquet
data/processed/monthly_revenue.parquet
data/processed/institutional_trading_daily.parquet
data/processed/margin_short_daily.parquet
data/processed/surveillance_daily.parquet
data/processed/corporate_actions.parquet
data/processed/material_events.parquet
data/processed/financial_statement_quarterly.parquet
data/processed/insider_holding_monthly.parquet
data/processed/valuation_daily.parquet
```

Quality layer：

```text
data/quality/data_coverage_report.csv
data/quality/missing_dates_report.csv
data/quality/duplicate_rows_report.csv
data/quality/schema_validation_report.csv
data/quality/source_freshness_report.csv
```

Sample layer：

```text
data/samples/*.csv
```

Only small samples are allowed in GitHub.

---

## 10. Normalization Requirements

請建立共用 normalizer 工具：

```text
roc_year_to_ad_date
parse_tw_date
parse_number_zh_tw
parse_percent
strip_commas
parse_dash_as_null
normalize_symbol
normalize_market
normalize_bool_flag
safe_float
safe_int
```

台股資料常見問題要處理：

```text
民國年格式，例如 115/05/11
中文欄位名
Big5 / UTF-8 / UTF-8-SIG
數字含逗號
--、X、空白、N/A
同一資料源上市 / 上櫃欄位不同名
ETF、ETN、權證、TDR、KY 混雜
除權息造成價格跳動
資料日期與公告日期不同
```

---

## 11. No Future Leakage Rules

這段一定要寫進程式與測試。

### 11.1 日線資料

```text
若 scan 是盤後 EOD：可以用 trade_date == as_of_date 的日線。
若 scan 是盤中：只能用上一個完整交易日，除非 broker API snapshot 明確標記為 intraday_snapshot。
```

### 11.2 月營收

```text
只要 announce_date > as_of_date，就不能用。
revenue_month 不代表資料已公開。
回測時必須以 announce_date 控制，而不是以 revenue_month 控制。
```

### 11.3 財報

```text
只要 announce_date > as_of_date，就不能用。
若 announce_date 缺失，用保守 fallback，不得用季度截止日直接視為可用。
```

### 11.4 重大訊息

```text
announce_date / announce_time <= as_of_date 才可用。
如果只有 event_date，但沒有 announce_date，不得假設 event_date 前市場已知道。
```

### 11.5 Corporate actions

```text
回測 label 可以標記除權息事件，但 feature 不得使用未公告的未來除權息。
```

---

## 12. Data Quality Checks

每個 processed table 必須做 quality check：

```text
schema columns exist
primary key uniqueness
date parse success
no future date beyond today unless explicitly allowed
numeric columns parse success
market must be TWSE/TPEX/Emerging/Unknown
symbol not null
fetched_at not null
source not null
source_url not null
```

各表 primary key：

```text
symbol_master: market + symbol
prices_daily: trade_date + market + symbol
monthly_revenue: revenue_month + market + symbol
institutional_trading_daily: trade_date + market + symbol
margin_short_daily: trade_date + market + symbol
surveillance_daily: trade_date + market + symbol + attention/disposition type if needed
corporate_actions: action_date + market + symbol + action_type
material_events: announce_date + announce_time + market + symbol + title
financial_statement_quarterly: year + quarter + market + symbol
insider_holding_monthly: data_month + market + symbol + title + insider_name
valuation_daily: trade_date + market + symbol
```

Freshness checks：

```text
prices_daily: should have latest trading date after each market close
monthly_revenue: should update during each month 1–10 day window, but must not assume all companies report at same time
institutional_trading: should update after market close
margin_short: should update after market close or official release time
surveillance: should update after official release
```

---

## 13. Feature 接口設計

先讓資料可以被目前 radar 使用。請新增或更新 adapters：

```text
short_term_radar/adapters/processed_data_adapter.py
short_term_radar/adapters/revenue_adapter.py
short_term_radar/adapters/chip_adapter.py
short_term_radar/adapters/surveillance_adapter.py
short_term_radar/adapters/catalyst_adapter.py
short_term_radar/adapters/corporate_action_adapter.py
short_term_radar/adapters/valuation_adapter.py
```

### 13.1 revenue features

從 `monthly_revenue.parquet` 產出：

```text
rev_yoy_1m
rev_mom_1m
rev_yoy_3m
rev_yoy_6m
rev_acceleration_3m_vs_12m
rev_new_high_flag
rev_same_month_high_flag
rev_turn_positive_flag
rev_positive_streak_months
rev_surprise_proxy
latest_revenue_month
latest_revenue_announce_date
```

Scoring hint：

```text
連續 2–3 個月 YoY 加速加分
YoY 由負轉正加分
創歷史新高 / 同期新高加分
股價尚未大幅反應時加分
營收好但股價已暴漲則降預期差
```

### 13.2 chip features

從 `institutional_trading_daily.parquet` 與 `margin_short_daily.parquet` 產出：

```text
foreign_net_5d
foreign_net_20d
investment_trust_net_5d
investment_trust_net_20d
dealer_net_5d
total_institutional_net_5d
total_institutional_net_20d
institutional_net_amount_ratio_5d
margin_balance_change_5d
margin_balance_change_20d
margin_balance_pct_change_20d
short_balance_change_5d
sbl_short_sell_ratio
financing_overcrowded_flag
short_squeeze_candidate_flag
```

Scoring hint：

```text
投信 5D/20D 連買加分
外資由賣轉買加分
法人剛開始買、融資未爆增加分
股價已漲很多 + 融資暴增扣分
法人連賣扣分
```

### 13.3 surveillance features

從 `surveillance_daily.parquet` 產出：

```text
attention_flag
attention_reason
disposition_flag
disposition_active_flag
disposition_days_left
attention_count_recent
surveillance_risk_score
```

Hard rules：

```text
處置中不能進 S3 candidate_entry
處置中 entry_zone = avoid_chasing 或 risk_watch
注意股加風險旗標
注意股 + 爆量 + 近 20 日大漲 => S5
```

### 13.4 catalyst features

從 `material_events.parquet` 產出：

```text
material_event_count_30d
positive_catalyst_count_30d
risk_event_count_30d
investor_conference_flag
major_order_flag
new_product_flag
capacity_expansion_flag
customer_supply_chain_flag
capital_raise_risk_flag
lawsuit_or_penalty_flag
latest_material_event_title
latest_material_event_type
```

Scoring hint：

```text
大單、新產品、產能、法說展望、進供應鏈加分
現增、訴訟、停工、財報警訊扣分
沒有任何催化劑時，不得因價量高分直接 S3
```

### 13.5 corporate action features

從 `corporate_actions.parquet` 產出：

```text
nearby_corporate_action_flag
ex_dividend_nearby_flag
capital_increase_nearby_flag
stock_split_or_reduction_flag
corporate_action_risk_note
```

用途：

```text
避免回測把除權息誤判成價格崩跌
避免現增 / 減資造成價格解讀錯誤
```

### 13.6 valuation / size features

從 `valuation_daily.parquet` + `symbol_master.parquet` + `prices_daily.parquet` 產出：

```text
market_cap
paid_in_capital
issued_shares
pe
pb
dividend_yield
large_cap_flag
small_mid_cap_flag
elasticity_bucket
valuation_overheated_flag
```

用途：

```text
半年 3–5 倍主榜排除大型權值股
大型股另做 strong trend list
```

---

## 14. Broker API Read-only Adapter

你的電腦有券商 API，可以查台股。請只做 read-only adapter：

Allowed：

```text
kbars
snapshots
ticks
daily_quotes
contract metadata
attention/disposition if API provides notice()/punish()
credit enquiries if API provides read-only credit info
short stock source if read-only
scanner rankings if read-only
```

Forbidden：

```text
place_order
update_order
cancel_order
account_balance
positions
realized_pnl
unrealized_pnl
settlements
any account mutation
```

Implementation rules：

```text
Do not login inside collector.
Do not store credentials.
Accept an already logged-in API object only when caller passes it.
Default broker_api.enabled = false.
All broker methods must be unit-tested with fake API object.
```

---

## 15. Backfill Plan

### 15.1 既有 5 年日線

你本機已有 5 年全台股日線。請先使用：

```text
existing_daily_price_path: ${TW_EQUITIES_DATA_PATH}
```

不要搬動別的 project 的資料。如果需要 converter，就複製一份工具到本 project 使用。

### 15.2 P0 backfill

請優先 backfill 最近 5 年：

```text
monthly_revenue: 2021-01 至 today
institutional_trading_daily: 2021-01-01 至 today
margin_short_daily: 2021-01-01 至 today
surveillance_daily: 2021-01-01 至 today
corporate_actions: 2021-01-01 至 today
material_events: 2021-01-01 至 today
symbol_master: latest, then snapshots if possible
```

若來源無法一次查五年或需付費，請：

```text
1. 實作 collector interface
2. 實作 incremental daily collection
3. 在 handoff 記錄 backfill limitation
4. 不要讓整個系統壞掉
```

---

## 16. Integration with Existing Radar

完成資料收集層後，更新 scan pipeline：

```text
scan_candidates(...)
  load_daily_prices
  load_processed_revenue_features
  load_processed_chip_features
  load_processed_surveillance_features
  load_processed_catalyst_features
  load_processed_corporate_action_features
  load_processed_valuation_features
  compute scores
  compute data_coverage_ratio
  generate reasons/risk flags
```

Data coverage rules：

```text
if revenue missing:
  cannot enter S3 candidate_entry
  add risk flag: revenue 缺資料，基本面未驗證

if chip missing:
  add risk flag: chip 缺資料，籌碼未驗證

if catalyst missing:
  add risk flag: catalyst 缺資料，缺少 1–6 個月重估催化劑

if surveillance missing:
  add risk flag: surveillance 缺資料，注意/處置風險未驗證

if core data coverage too low:
  cap score_total
```

Suggested scoring cap：

```text
if revenue, chip, catalyst all missing:
  score_total_cap = 70

if surveillance missing:
  score_total_cap = min(score_total_cap, 80)

if revenue missing:
  stage max = S2

if active disposition:
  stage = S5
  entry_zone = avoid_chasing
```

---

## 17. Tests Required

請新增測試：

```text
tests/short_term_radar/data_sources/test_date_parsing.py
tests/short_term_radar/data_sources/test_number_parsing.py
tests/short_term_radar/data_sources/test_symbol_master_normalizer.py
tests/short_term_radar/data_sources/test_monthly_revenue_normalizer.py
tests/short_term_radar/data_sources/test_prices_daily_normalizer.py
tests/short_term_radar/data_sources/test_institutional_trading_normalizer.py
tests/short_term_radar/data_sources/test_margin_short_normalizer.py
tests/short_term_radar/data_sources/test_surveillance_normalizer.py
tests/short_term_radar/data_sources/test_material_events_classifier.py
tests/short_term_radar/data_sources/test_quality_checks.py
tests/short_term_radar/data_sources/test_no_future_leakage_revenue.py
tests/short_term_radar/data_sources/test_broker_readonly_adapter.py
tests/short_term_radar/test_stage_gating_with_missing_data.py
tests/short_term_radar/test_disposition_blocks_candidate_entry.py
```

Test cases must cover：

```text
民國年轉西元年
數字去逗號
-- 轉 null
百分比 parsing
月營收 announce_date gating
處置中禁止 S3
缺 revenue 時 max stage S2
broker adapter has no order methods
quality report detects duplicate primary keys
```

---

## 18. Validation Commands

完成後請確保這些命令能跑：

```powershell
py -3.14 -m pytest -q tests\short_term_radar
py -3.14 -m compileall -q short_term_radar tests\short_term_radar

py -3.14 -m short_term_radar.cli.collect --config configs/short_term_radar/local.yaml.example --dataset symbol_master --market all --dry-run
py -3.14 -m short_term_radar.cli.normalize --config configs/short_term_radar/local.yaml.example --dataset all --dry-run
py -3.14 -m short_term_radar.cli.validate_data --config configs/short_term_radar/local.yaml.example --dataset all --dry-run
py -3.14 -m short_term_radar.cli.coverage --config configs/short_term_radar/local.yaml.example --start 2021-01-01 --end 2026-05-11 --dry-run
```

If a live fetch cannot run without network / credentials / subscription, the CLI must still support `--dry-run` and tests must use fixture CSV/JSON samples.

---

## 19. Sample Data Fixtures

請建立小型 sample fixtures，不要放大型 raw data：

```text
tests/fixtures/twse_prices_daily_sample.csv
tests/fixtures/tpex_prices_daily_sample.csv
tests/fixtures/twse_monthly_revenue_sample.csv
tests/fixtures/tpex_monthly_revenue_sample.csv
tests/fixtures/twse_symbol_master_sample.csv
tests/fixtures/tpex_symbol_master_sample.csv
tests/fixtures/tpex_attention_sample.csv
tests/fixtures/tpex_disposition_sample.csv
tests/fixtures/material_events_sample.csv
```

每個 fixture 只需要 2–5 rows，涵蓋中文欄位、民國年、逗號數字、空值即可。

---

## 20. Reports and Handoff

更新：

```text
SHORT_TERM_RADAR_HANDOFF.md
short_term_radar/README.md
configs/short_term_radar/data_sources.example.yaml
configs/short_term_radar/local.yaml.example
```

Handoff 要寫：

```text
完成哪些 collector
哪些來源已接
哪些來源只是 registry / dry-run
哪些資料需要付費或手動設定
哪些資料還缺 backfill
如何跑 collect / normalize / validate / coverage
如何避免 commit raw data
下一步如何把 data features 接進 score
```

---

## 21. Acceptance Criteria

完成後必須滿足：

1. `projects/short_term_radar_mvp/` 內有完整 data source registry。
2. 每個 P0 資料都有 collector interface、normalizer、schema、quality check。
3. 至少 P0 的 sample fixtures 測試通過。
4. `local.yaml.example` 支援環境變數，不硬編本機路徑。
5. Raw / processed data 被 `.gitignore` 排除。
6. Broker API adapter 明確 read-only，且測試確認沒有下單相關方法。
7. 月營收 feature 有 announce_date gating 測試，避免未來資料洩漏。
8. 處置股可阻擋 S3 candidate_entry。
9. 缺 revenue / chip / catalyst / surveillance 時，報告要顯示 degraded radars。
10. 不得改動牛頭人 repo 其他既有內容。

---

## 22. 建議實作順序

### Sprint 1：資料收集骨架與 P0 sample

```text
1. data_sources folder
2. config loader
3. storage helper
4. common normalizer
5. symbol_master normalizer
6. monthly_revenue normalizer
7. prices_daily normalizer
8. quality checker
9. CLI dry-run
10. tests + fixtures
```

### Sprint 2：P0 實際 collector / processed parquet

```text
1. TWSE/TPEX prices_daily
2. TWSE/TPEX symbol_master
3. TWSE/TPEX monthly_revenue
4. TPEx attention/disposition
5. corporate_actions
6. material_events
7. processed parquet outputs
8. coverage report
```

### Sprint 3：籌碼與風控

```text
1. institutional_trading_daily
2. margin_short_daily
3. broker read-only enrichment
4. surveillance active period logic
5. chip feature adapter
6. revenue feature adapter
7. gating rules in scan pipeline
```

### Sprint 4：回測接入

```text
1. backtest 使用 revenue announce_date gating
2. backtest 使用 surveillance gating
3. baseline comparison 加入資料覆蓋率
4. report 顯示 degraded radars
```

---

## 23. 這次不要做的事

本輪不要做：

```text
不要做下單系統
不要做策略自動交易
不要做部位管理
不要做券商帳戶查詢
不要做新聞/社群大爬蟲
不要做大型 dashboard
不要把 raw data commit 到 GitHub
不要把別的 project 整包搬過來
```

本輪重點只有：

```text
資料來源可追蹤
資料可收集
資料可正規化
資料可驗證
資料可被短線雷達 pipeline 使用
```

---

## 24. 最終產物

完成後，repo 應該能提供：

```text
一套乾淨、可擴充、read-only、無未來資料洩漏的台股短線雷達資料收集層。
```

它要讓後續雷達能從現在的：

```text
價量突破 MVP
```

升級成：

```text
月營收拐點 + 價量突破 + 法人籌碼 + 擁擠度風控 + 催化劑 + 處置風險 的短線 3–5 倍候選股雷達。
```
