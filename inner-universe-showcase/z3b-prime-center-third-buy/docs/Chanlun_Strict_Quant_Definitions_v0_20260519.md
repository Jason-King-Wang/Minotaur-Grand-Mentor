# 纏論嚴格量化定義 v0

本文是後續重寫 Z3B-Prime 嚴格版前的定義層規格。目的不是調參，而是先把纏論裡會用到的市場結構全部量化成可回測、可實盤、可重現的資料模型。

本文件先定義嚴格版，不直接改現有簡單版程式。現有簡單版用 confirmed swing 和 price box 近似中樞；嚴格版必須改成「K 線包含處理 -> 分型 -> 筆 -> 線段 -> 中樞 -> 走勢類型 -> 買賣點」的遞迴結構。

## 0. 來源與優先級

優先級如下：

1. 原始 108 課幾何定義：分型、筆、線段、中樞、第三類買賣點。
2. 可工程化的量化實作約束：同一輸入、同一時間點，輸出必須唯一。
3. 我們 Z3B 既有口述策略：1H 前高 gate + 15m A / b-A / 金 K / 多頭趨勢 K，只能建立在嚴格結構上。

參考來源：

- 分型、筆、線段與包含關係：<https://chanlun108.cn/chanzhongshuochan108ke/65.html>
- 分型與筆的原始幾何說明：<https://baiyunju.cc/1874>
- 中樞、ZG/ZD、第三類買賣點：<https://www.chanlun.org/chzhshch/chzhshch-trend-center-rank-expansion-and-third-buy-sale-points.html>
- PDF 版 108 課相同段落備查：<https://xqdoc.imedao.com/15621999f6b25803feb29d4c.pdf>
- 工程配置參考：<https://chanlun-pro.readthedocs.io/%E7%BC%A0%E8%AE%BA%E9%85%8D%E7%BD%AE%E9%A1%B9%E8%AF%B4%E6%98%8E/>

## 1. 實盤資料前提

嚴格版預設未來可以實時取得 1m、5m、15m、1H 等多級別 K 線。最底層事件源以 1m closed bar 為準。

### 1.1 已收盤與未收盤

1. 所有確認訊號只允許使用已收盤 K。
2. 未收盤 K 可更新 watch state，但不可確認分型、筆、線段、中樞或買點。
3. 每分鐘新增一根 1m closed bar 後，才觸發一次結構遞迴更新。
4. 5m / 15m / 1H 由 1m 聚合時，必須等該週期完整收盤後才進入該週期結構。
5. 實盤若交易所直接提供高級別 K，也要和 1m 聚合結果做時間邊界一致性檢查。

### 1.2 Session 邊界

1. 台股 regular session 不得把午休、收盤、隔夜硬接成連續 K。
2. 任何 resample 必須以交易所 session calendar 為準。
3. 若訊號確認在收盤後或最後一根可交易 K，entry 必須順延到下一個有效 regular session。
4. 停損 / 停利在實盤可能遇到跳空、漲跌停、流動性不足；模型層記理論觸發，執行層另外記實際成交。

### 1.3 當下性與狀態不可污染

每一級別都維護下列狀態：

```text
raw_bars_closed
chan_bars_resolved
fractals_confirmed
strokes_confirmed
segments_confirmed
centers_confirmed
latest_provisional_structure
```

已確認物件不可因後續資料任意改寫；允許改寫的只有最新未完成結構，例如最新一筆、最新線段、最新中樞延伸候選。

## 2. K 線包含處理

原始 K 只保留高低點參與纏論幾何；open / close / volume 保留給交易執行與動力學，但不影響分型幾何。

定義第 `i` 根 K 的區間：

```text
K_i = [d_i, g_i]
d_i = low_i
g_i = high_i
```

兩根 K 有包含關係：

```text
contains(K_a, K_b) =
    (g_a >= g_b and d_a <= d_b)
 or (g_a <= g_b and d_a >= d_b)
```

### 2.1 合併方向

若 `K_n` 與 `K_{n+1}` 有包含，且 `K_n` 與前一根非包含 K `K_{n-1}` 無包含：

```text
up_direction   = g_n >= g_{n-1}
down_direction = d_n <= d_{n-1}
```

上行合併：

```text
merged.high = max(high_a, high_b)
merged.low  = max(low_a, low_b)
```

下行合併：

```text
merged.high = min(high_a, high_b)
merged.low  = min(low_a, low_b)
```

包含不具傳遞律，所以必須嚴格按時間順序逐根合併：先合併 1/2，再用新 K 和第 3 根比較，直到不存在包含。

### 2.2 工程物件

```text
ChanBar {
  timeframe
  start_time
  end_time
  high
  low
  raw_bar_ids[]
  merge_direction: UP | DOWN | NONE
  is_closed: true
}
```

## 3. 分型

分型必須建立在包含處理後的 ChanBar 上。

對三根連續 ChanBar `A, B, C`：

頂分型：

```text
B.high > A.high
B.high > C.high
B.low  > A.low
B.low  > C.low
```

底分型：

```text
B.low  < A.low
B.low  < C.low
B.high < A.high
B.high < C.high
```

若遇到相等值，嚴格版預設不確認分型，除非未來明確定義 tie-break。理由是實盤交易要避免把不明確結構硬判成訊號。

### 3.1 分型確認時間

分型 `B` 只有在右側 `C` 已收盤且包含處理完成後才確認。

```text
fractal.confirm_time = C.end_time
fractal.price =
  top: B.high
  bottom: B.low
```

## 4. 筆

筆由相鄰且相反的分型構成。

向上筆：

```text
start = confirmed bottom fractal
end   = later confirmed top fractal
end.price > start.price
```

向下筆：

```text
start = confirmed top fractal
end   = later confirmed bottom fractal
end.price < start.price
```

嚴格最低條件：

1. 必須一頂一底，不能同型分型成筆。
2. 起訖分型不得共用 ChanBar。
3. 起訖分型之間至少有 1 根獨立 ChanBar。
4. 若在一個頂到底或底到頂之前出現連續同型分型，保留更極端者：頂取更高，底取更低；較弱者視為不足以成筆的轉折。

### 4.1 老筆 / 新筆

嚴格原始幾何的最低要求是「不共用 K + 至少一根獨立 K」。工程上可提供兩種模式，但策略必須明確選一種：

```yaml
stroke_mode:
  old:
    min_independent_chan_bars_between_fractals: 1
  new:
    min_raw_bars_between_extreme_bars: 5
```

嚴格交易版預設先採 `old`，因為它最貼近原始幾何定義；若要切 `new`，必須先重跑全市場回測比較，不可混用。

### 4.2 筆的確認與延伸

最新一筆在相反分型確認前只能是 pending。已確認筆的 endpoint 可被同方向更極端分型取代，直到相反筆確認。相反筆確認後，前一筆封存。

## 5. 線段

線段由至少三筆構成，但不是任意三筆都能成線段；前三筆必須有重疊區間。

每一筆 `B_i` 的價格區間：

```text
B_i.interval = [min(start.price, end.price), max(start.price, end.price)]
```

三筆重疊：

```text
overlap_low  = max(B1.low, B2.low, B3.low)
overlap_high = min(B1.high, B2.high, B3.high)
segment_seed_valid = overlap_low <= overlap_high
```

### 5.1 向上線段破壞

向上線段的分型序列：

```text
d1, g1, d2, g2, d3, g3, ...
```

若存在 `j >= i + 2` 使：

```text
d_j <= g_i
```

則向上線段被筆破壞。

### 5.2 向下線段破壞

向下線段的分型序列：

```text
g1, d1, g2, d2, g3, d3, ...
```

若存在 `j >= i + 2` 使：

```text
g_j >= d_i
```

則向下線段被筆破壞。

### 5.3 線段確認

線段破壞的充要條件是被另一個線段破壞。工程上：

1. 線段 seed 由前三筆重疊確認。
2. 最新線段可延伸。
3. 只有反向線段 seed 成立時，原線段才完成封存。

## 6. 中樞

嚴格中樞不是固定 K 數，也不是 swing box。某級別中樞由至少三個連續次級別走勢類型重疊而成。

工程上，本級別 `L` 的中樞輸入單元採用次級別 `L-1` 的已確認線段或已完成走勢類型，不能直接用單根 K 或簡化 swing。

三個連續次級別區間：

```text
Z1 = [d1, g1]
Z2 = [d2, g2]
Z3 = [d3, g3]
```

中樞核心區間：

```text
ZD = max(d1, d2, d3)
ZG = min(g1, g2, g3)
center_valid = ZD <= ZG
center_range = [ZD, ZG]
```

其中：

```text
ZD = 中樞低沿
ZG = 中樞高沿
GG = max(g_n)
G  = min(g_n)
D  = max(d_n)
DD = min(d_n)
```

### 6.1 中樞延伸

後續同級 `Z_n = [d_n, g_n]` 若與 `[ZD, ZG]` 有重疊，視為中樞延伸：

```text
extends_center = d_n <= ZG and g_n >= ZD
```

若出現：

```text
d_n > ZG
```

代表向上離開該中樞；若出現：

```text
g_n < ZD
```

代表向下離開該中樞。

### 6.2 中樞級別擴張與趨勢

兩個前後同級中樞 `C_prev`, `C_next`：

上漲延續：

```text
C_next.DD > C_prev.GG
```

下跌延續：

```text
C_next.GG < C_prev.DD
```

若兩個中樞不是乾淨地向上或向下分離，而是互相跨越，則可能形成更高級別中樞，不能直接判定趨勢延續。

## 7. 走勢類型

某級別已完成走勢類型分三種：

```text
uptrend      = 至少兩個同級中樞依次向上
downtrend    = 至少兩個同級中樞依次向下
consolidation = 只包含一個同級中樞
```

嚴格版必須等走勢類型完成，才能把它當成上一級別的組件。未完成走勢只能作為 pending state。

## 8. 第三類買點

第三類買點是中樞離開後的第一次不回中樞確認。

對某級別中樞 `C`：

1. 一個次級別走勢類型向上離開 `C`。
2. 接著第一個次級別回試走勢類型完成。
3. 該回試低點不跌破 `ZG`。
4. 第三類買點是該回試走勢類型完成時的低點。

量化：

```text
leave_up.valid =
  leave_type.level == C.level - 1
  and leave_type.direction == UP
  and leave_type.end_time > C.end_time
  and leave_type.end_price > ZG
  and leave_type contains a post-center interval [d, g] where d > ZG

pullback.valid =
  pullback_type.level == C.level - 1
  and pullback_type.direction == DOWN
  and pullback_type.low >= ZG
  and pullback_type is first pullback after leave_up

third_buy.price = pullback_type.low
third_buy.time  = pullback_type.end_time
```

嚴格版不可把單根 K 的 low 不破 ZG 當成第三類買點；必須是次級別走勢類型完成。

### 8.1 級別鏈

若我們交易用：

```text
1H = 趨勢級別
15m = 交易級別
5m = 15m 的次級別
1m = 最底層實時資料級別
```

那麼：

1. 1H 中樞應由 15m 已完成走勢類型構成。
2. 15m 走勢類型應由 5m 線段 / 中樞構成。
3. 5m 結構應由 1m 筆 / 線段構成。
4. 實盤每分鐘更新 1m 後，逐級向上刷新 pending 結構。

## 9. 背馳與力度

現有簡單模型用 `b > a`、`b-b < b-a` 做回調力度比較。嚴格版不能只用長度，必須把「完成的同向走勢段」和「動力學力度」分開。

### 9.1 可比較段

只有同級、同方向、已完成的走勢段可比較。不能拿不同級別、未完成段、或單根 K 互相比。

```text
comparable(A, C) =
  A.level == C.level
  and A.direction == C.direction
  and A.completed
  and C.completed
```

### 9.2 力度向量

每段走勢的力度先輸出向量，不急著壓成單一分數：

```text
force_vector(segment) = {
  price_distance: abs(end.price - start.price),
  price_extreme_break: 是否創新高/新低,
  duration_bars,
  slope: price_distance / duration_bars,
  macd_area: sum(abs(MACD_hist) over segment),
  macd_peak: max(abs(MACD_hist) over segment),
  volume_sum,
  volume_price_efficiency: price_distance / max(volume_sum, 1)
}
```

嚴格策略判定時，必須記錄每個子條件。是否要求 MACD area 同步收斂，之後用回測決定，但不能把「價格長度比較」說成完整背馳。

### 9.3 Z3B 的 a/b 映射

在嚴格版裡：

```text
a   = 進入 15m A 前的已完成下跌走勢段
b   = 離開 15m A 後的已完成下跌走勢段
b-a = 進入 b-A 前的已完成下跌走勢段
b-b = 離開 b-A 後的已完成下跌走勢段
```

每一段都必須是線段或走勢類型，不再是 swing-high 到 swing-low 的近似距離。

## 10. 金 K、入場 K、停損

這是 Z3B 策略層，不是原始纏論核心定義；但嚴格版要依附於前面結構。

### 10.1 金 K

```text
golden_k =
  b-b 走勢段完成後，
  第二個不破前低的低點所對應的已收盤交易級別 K
```

嚴格要求：

1. `b-b` 已完成。
2. `b-b.low >= b-a.low`。
3. golden_k 必須是已收盤 K。
4. stop_loss = golden_k.low。

### 10.2 多頭趨勢 K

暫定為交易級別已收盤 K，且出現在 golden_k 之後：

```text
bullish_trend_k.valid =
  close > open
  and body / full_range >= min_body_ratio
  and close_position_in_range >= min_close_position
  and upper_wick / full_range <= max_upper_wick_ratio
  and body >= terminal_center.range * min_body_vs_center_range
```

這只是入場確認，不可用來替代中樞、筆、線段或背馳定義。

## 11. 與現有簡單模型的差異

| 元件 | 現有簡單版 | 嚴格版 |
|---|---|---|
| K 線 | 直接用 OHLC | 先做包含處理 |
| 分型 | confirmed swing 近似 | 三根 ChanBar 嚴格分型 |
| 筆 | 無正式筆 | 相鄰頂底分型成筆 |
| 線段 | 無正式線段 | 至少三筆且前三筆重疊 |
| 中樞 | swing window / price box | 三個連續次級別走勢類型重疊 |
| 三買 | 1H gate + swing low | 次級別離開後第一次回試不回中樞 |
| a/b | swing high-low 距離 | 已完成同級走勢段力度 |
| 實時 | 回測批次掃描 | 1m closed bar 驅動的狀態機 |

## 12. 嚴格版工程模組

建議拆成以下模組，先做結構引擎，再套 Z3B：

```text
chanlun_strict/
  bars.py          # 1m ingestion, resample, session calendar
  inclusion.py     # ChanBar merge
  fractals.py      # top/bottom fractal
  strokes.py       # bi
  segments.py      # xianduan
  centers.py       # zhongshu
  trends.py        #走势类型
  buy_points.py    # first/second/third buy/sell
  realtime.py      # incremental state machine
  audit.py         # explain every decision
```

每個輸出物件都要有：

```text
id
level
start_time
end_time
confirm_time
source_ids[]
status: PENDING | CONFIRMED | INVALIDATED
reason_codes[]
```

## 13. 下一步

1. 先實作嚴格纏論結構引擎，不放交易條件。
2. 用現有 1H / 15m / 未來 1m 資料跑結構輸出，人工抽查分型、筆、線段、中樞。
3. 把現有簡單 Z3B 訊號和嚴格結構對齊，標出哪些訊號在嚴格版下不成立。
4. 再把 1H 前高 gate、15m A / b-A、金 K、多頭趨勢 K 接到嚴格結構上。
5. 最後才重新跑 50 檔與全市場回測。

## 14. 本輪結論

嚴格版最大的改動不是調整參數，而是更換市場結構基礎。現有模型的中樞、a/b、b-A 都是簡化近似；若要實盤交易，必須先建立 1m 驅動、跨級別、可當下確認、可審計的纏論結構引擎，再把 Z3B 策略掛上去。
