# 纏論共用核心量化模型 v0

本文建立一套可被多個策略共用的纏論核心模型。它不是 Z3B 專用，也不只服務第三類買點；未來任何纏論延伸模型，都應該先依賴這個核心輸出，再疊加自己的交易規則。

本文件不直接產生交易訊號，而是定義可交易系統需要的結構、狀態、事件與嚴格量化口徑。

## 0. 設計原則

1. 核心結構與策略分離：纏論核心只輸出結構與買賣點候選，不決定倉位。
2. 每個概念都要有資料物件、確認時間、來源 ID、失效條件。
3. 所有確認都以已收盤 K 為準；實盤每分鐘新 1m K 後增量更新。
4. 不能用 swing box、固定 K 數、固定百分比去替代纏論核心。
5. 若不同流派有差異，模型要保留 `definition_profile`，不能混用。

## 1. 參考來源

主要依據：

- 原始 108 課中分型、筆、線段、包含關係的說明：<https://chanlun108.cn/chanzhongshuochan108ke/65.html>
- 原始 108 課中中樞、ZG/ZD、第三類買賣點的說明：<https://www.chanlun.org/chzhshch/chzhshch-trend-center-rank-expansion-and-third-buy-sale-points.html>
- 一、二、三類買賣點整理與原文索引：<https://baiyunju.cc/2002>
- 走勢終完美與走勢分解定理整理：<https://blog.sina.com.cn/s/blog_ba2553920102xu6c.html>
- 量化工程參考與配置差異：<https://chanlun-pro.readthedocs.io/%E7%BC%A0%E8%AE%BA%E9%85%8D%E7%BD%AE%E9%A1%B9%E8%AF%B4%E6%98%8E/>

## 2. 共用資料模型

所有物件共用欄位：

```text
CoreObject {
  id
  object_type
  level
  symbol
  start_time
  end_time
  confirm_time
  status: PENDING | CONFIRMED | INVALIDATED | SUPERSEDED
  source_ids[]
  invalidated_by
  reason_codes[]
  definition_profile
}
```

級別鏈由設定決定，但必須單向遞迴：

```yaml
levels:
  - 1m
  - 5m
  - 15m
  - 1h
  - 1d
```

嚴格版預設：

```text
1m closed bar -> 1m ChanBar -> 1m fractal -> 1m stroke -> 1m segment
1m segment / 1m trend type -> 5m structure
5m structure -> 15m structure
15m structure -> 1H structure
```

實際實作可直接用 1m 聚合成 5m/15m/1H，但高級別纏論結構不能跳過次級別走勢類型的確認。

## 3. 基礎形態學物件

### 3.1 RawBar

```text
RawBar {
  timeframe
  open_time
  close_time
  open
  high
  low
  close
  volume
  amount
  is_closed
  session_id
}
```

只有 `is_closed=true` 才能進入纏論確認流程。

### 3.2 ChanBar

ChanBar 是完成包含處理後的 K 線。

```text
ChanBar {
  high
  low
  raw_bar_ids[]
  merge_direction: UP | DOWN | NONE
}
```

包含關係、上行合併、下行合併依 `Chanlun_Strict_Quant_Definitions_v0_20260519.md` 第 2 節。

### 3.3 Fractal

```text
Fractal {
  kind: TOP | BOTTOM
  pivot_chan_bar_id
  left_chan_bar_id
  right_chan_bar_id
  price
}
```

嚴格條件：

```text
TOP:
  mid.high > left.high and mid.high > right.high
  mid.low  > left.low  and mid.low  > right.low

BOTTOM:
  mid.low  < left.low  and mid.low  < right.low
  mid.high < left.high and mid.high < right.high
```

同型分型連續出現時，保留更極端者。

### 3.4 Stroke / 筆

```text
Stroke {
  direction: UP | DOWN
  start_fractal_id
  end_fractal_id
  start_price
  end_price
  high
  low
  chan_bar_ids[]
}
```

確認條件：

1. 起點與終點必須一頂一底。
2. 起訖分型不得共用 ChanBar。
3. 至少保留一根獨立 ChanBar。
4. `definition_profile=old_bi` 時採原始幾何；`new_bi` 時可加入更嚴格 K 數限制。

### 3.5 Segment / 線段

```text
Segment {
  direction: UP | DOWN
  stroke_ids[]
  seed_stroke_ids[3]
  high
  low
  destroyed_by_segment_id
}
```

確認條件：

1. 至少三筆。
2. 前三筆價格區間有重疊。
3. 反向線段 seed 成立後，前一線段才正式封存。

## 4. 中樞模型

### 4.1 Center / 走勢中樞

```text
Center {
  level
  component_type: SEGMENT | TREND_TYPE
  component_ids[]
  ZD
  ZG
  GG
  G
  D
  DD
  direction_context: UP | DOWN | NEUTRAL
  lifecycle: NEW | EXTENDING | LEFT_UP | LEFT_DOWN | UPGRADED | TERMINATED
}
```

三個連續次級別走勢類型：

```text
Zi = [di, gi]

ZD = max(d1, d2, d3)
ZG = min(g1, g2, g3)
center_valid = ZD <= ZG
```

嚴格版中，`Zi` 不能是任意 K，也不能是簡化 swing；必須是已確認次級別線段或走勢類型。

### 4.2 中樞延伸

後續次級別走勢 `Z_n` 與 `[ZD, ZG]` 有重疊：

```text
extends = Z_n.low <= ZG and Z_n.high >= ZD
```

則中樞進入 `EXTENDING`。延伸只代表同一中樞繼續震盪，不代表新趨勢。

### 4.3 中樞新生

某中樞離開後，後續形成不與原中樞重疊的新中樞：

```text
new_up_center =
  C2.DD > C1.GG

new_down_center =
  C2.GG < C1.DD
```

此時可判定同級別趨勢延續。

### 4.4 中樞擴展 / 擴張 / 升級

為避免流派用語混亂，工程上統一定義三種升級事件：

```text
CenterUpgrade {
  kind: EXTENSION_UPGRADE | OVERLAP_UPGRADE | RETURN_UPGRADE
}
```

`EXTENSION_UPGRADE`：同一中樞延伸段數達到設定門檻，視為更高級別震盪。

`OVERLAP_UPGRADE`：兩個同級中樞的波動區間重疊：

```text
overlap(C1, C2) = max(C1.DD, C2.DD) <= min(C1.GG, C2.GG)
```

`RETURN_UPGRADE`：出現第三類買賣點候選後，價格未延續反而回到原中樞，原三買/三賣失效，結構升級。

## 5. 走勢類型與走勢終完美

### 5.1 TrendType / 走勢類型

```text
TrendType {
  kind: UP_TREND | DOWN_TREND | CONSOLIDATION
  level
  center_ids[]
  component_ids[]
}
```

量化定義：

```text
CONSOLIDATION = 已完成且至少包含 1 個中樞
UP_TREND      = 已完成且至少包含 2 個依次向上新生的同級中樞
DOWN_TREND    = 已完成且至少包含 2 個依次向下新生的同級中樞
```

### 5.2 走勢終完美

工程化表達：

```text
completed_trend_type.valid =
  trend_type.completed
  and trend_type.center_count >= 1
```

任何策略要使用「一段走勢已完成」，必須引用 `TrendType.completed=true`，不能只看單根 K 或未完成線段。

### 5.3 同級別分解

所有走勢都拆成同級別 `UP_TREND / DOWN_TREND / CONSOLIDATION` 的連接。

```text
SameLevelDecomposition {
  level
  trend_type_ids[]
  no_cross_level_mix: true
}
```

嚴格規則：

1. 不允許拿 1H 中樞直接和 15m 筆比較。
2. 不允許在同一個判斷式裡混用不同級別的完成狀態。
3. 若要跨級別，只能用「高級別候選 + 低級別確認」。

## 6. 買賣點模型

所有買賣點都是候選事件，不等於直接下單。

```text
BuySellPoint {
  kind:
    FIRST_BUY | SECOND_BUY | THIRD_BUY
    FIRST_SELL | SECOND_SELL | THIRD_SELL
    CENTER_OSC_BUY | CENTER_OSC_SELL
  level
  price
  time
  source_center_id
  source_trend_type_ids[]
  confirmation_level
  invalidation_price
  invalidation_rule
}
```

### 6.1 第一類買點 / 第一類賣點

第一類買點：某級別下跌趨勢背馳後形成的轉折低點。

```text
FIRST_BUY.valid =
  trend_type.kind == DOWN_TREND
  and trend_type.completed
  and divergence.kind == TREND_DIVERGENCE
  and divergence.direction == DOWN_WEAKENING
  and turning_structure.confirmed
```

第一類賣點相反：

```text
FIRST_SELL.valid =
  trend_type.kind == UP_TREND
  and trend_type.completed
  and divergence.kind == TREND_DIVERGENCE
  and divergence.direction == UP_WEAKENING
  and turning_structure.confirmed
```

嚴格要求：第一類買賣點必須依賴背馳與轉折確認，不能只是「創低反彈」或「創高回落」。

### 6.2 第二類買點 / 第二類賣點

第二類買點：第一類買點後的第一次次級別回調低點，且不破第一類買點。

```text
SECOND_BUY.valid =
  first_buy.confirmed
  and first_rebound_after_first_buy.completed
  and first_pullback_after_rebound.completed
  and first_pullback_after_rebound.low >= first_buy.price
```

第二類賣點：

```text
SECOND_SELL.valid =
  first_sell.confirmed
  and first_drop_after_first_sell.completed
  and first_rebound_after_drop.completed
  and first_rebound_after_drop.high <= first_sell.price
```

第二類買賣點可與第三類買賣點重合，但資料物件要保留兩個 `kind`，不能只存一個。

### 6.3 第三類買點 / 第三類賣點

第三類買點：次級別走勢向上離開中樞後，第一次次級別回調不回中樞。

```text
THIRD_BUY.valid =
  center.confirmed
  and leave_trend.level == center.level - 1
  and leave_trend.direction == UP
  and leave_trend.completed
  and first_pullback.level == center.level - 1
  and first_pullback.completed
  and first_pullback.low >= center.ZG
```

第三類賣點：

```text
THIRD_SELL.valid =
  center.confirmed
  and leave_trend.level == center.level - 1
  and leave_trend.direction == DOWN
  and leave_trend.completed
  and first_rebound.level == center.level - 1
  and first_rebound.completed
  and first_rebound.high <= center.ZD
```

### 6.4 中樞震盪買賣點

這不是三類買賣點，但實盤常用：

```text
CENTER_OSC_BUY =
  center.extending
  and price_reaches_near_ZD
  and lower_level_down_force_weakens
  and lower_level_turning_confirmed

CENTER_OSC_SELL =
  center.extending
  and price_reaches_near_ZG
  and lower_level_up_force_weakens
  and lower_level_turning_confirmed
```

震盪買賣點必須標成 `CENTER_OSC_*`，不能冒充一買二買三買。

## 7. 背馳模型

背馳是動力學物件，不是價格形態本身。

```text
Divergence {
  kind: TREND_DIVERGENCE | CONSOLIDATION_DIVERGENCE | SEGMENT_DIVERGENCE | STROKE_DIVERGENCE
  direction: UP_WEAKENING | DOWN_WEAKENING
  level
  compare_a_id
  compare_b_id
  center_id
  force_a
  force_b
  result: DIVERGED | NOT_DIVERGED | INSUFFICIENT_DATA
}
```

### 7.1 趨勢背馳

趨勢背馳必須發生在有至少兩個同級中樞的趨勢中，對比中樞前後同方向走勢段。

```text
TREND_DIVERGENCE.valid =
  trend_type.kind in [UP_TREND, DOWN_TREND]
  and trend_type.center_count >= 2
  and compare_a.direction == compare_b.direction
  and compare_a.level == compare_b.level
  and compare_b makes new extreme
  and force_b < force_a
```

### 7.2 盤整背馳

盤整背馳發生在單中樞震盪內，相鄰同方向段力度減弱。

```text
CONSOLIDATION_DIVERGENCE.valid =
  trend_type.kind == CONSOLIDATION
  and same_direction_legs_inside_center
  and latest_leg makes local extreme
  and force_latest < force_previous
```

盤整背馳通常只保證中樞內部震盪轉折，不自動推出大級別反轉。

### 7.3 力度量化

力度不壓成單一值，先保留向量：

```text
ForceVector {
  price_distance
  price_new_extreme: true | false
  duration_bars
  slope
  macd_hist_area
  macd_hist_peak
  dif_dea_distance_to_zero
  volume_sum
  volume_efficiency
}
```

比較函數：

```text
force_b < force_a =
  price_new_extreme == true
  and (
       macd_hist_area_b < macd_hist_area_a
    or macd_hist_peak_b < macd_hist_peak_a
    or slope_b < slope_a
  )
```

實盤模型必須輸出每個子條件，不可只輸出一個「背馳=true」。

## 8. 區間套與跨級別確認

區間套是把高級別候選縮小到低級別精確觸發。

```text
IntervalNest {
  higher_level_candidate_id
  lower_level_search_window
  lower_level_trigger_id
}
```

嚴格流程：

1. 高級別出現買賣點候選或背馳候選。
2. 只在高級別候選的時間 / 價格窗口內搜尋低級別結構。
3. 低級別必須形成自己的買賣點或背馳確認。
4. 低級別觸發不能反過來創造高級別候選。

## 9. 實時狀態機

每分鐘 1m closed bar 進來後：

```text
on_new_1m_bar(bar):
  append RawBar
  update 1m ChanBar
  update 1m Fractal
  update 1m Stroke
  update 1m Segment
  update 1m Center
  update 1m TrendType
  roll up completed objects to 5m
  repeat for 5m, 15m, 1H
  emit structure events
  emit buy/sell point candidates
```

事件輸出：

```text
ChanlunEvent {
  event_type:
    BAR_CLOSED
    FRACTAL_CONFIRMED
    STROKE_CONFIRMED
    SEGMENT_CONFIRMED
    CENTER_CONFIRMED
    CENTER_LEFT_UP
    CENTER_LEFT_DOWN
    CENTER_UPGRADED
    TREND_TYPE_COMPLETED
    DIVERGENCE_CONFIRMED
    BUY_SELL_POINT_CONFIRMED
  object_id
  event_time
  confirm_time
  payload
}
```

## 10. 審計與除錯輸出

每個候選買賣點都必須能追溯：

```text
AuditTrace {
  candidate_id
  accepted: true | false
  failed_reason_codes[]
  source_center
  source_trend_types[]
  source_segments[]
  source_strokes[]
  source_fractals[]
  force_comparison
  invalidation_level
  invalidation_price
}
```

常用拒絕碼：

```text
NO_CONFIRMED_CENTER
CENTER_NOT_LEFT
PULLBACK_RETURNED_TO_CENTER
MISSING_LOWER_LEVEL_CONFIRMATION
FORCE_NOT_WEAKENED
TREND_TYPE_NOT_COMPLETED
CROSS_LEVEL_MIXED
USING_UNCLOSED_BAR
```

## 11. 和策略的關係

策略只能訂閱核心事件：

```text
StrategyInput =
  confirmed centers
  completed trend types
  divergence events
  buy/sell point candidates
  force vectors
  audit traces
```

例如 Z3B 嚴格版未來應該這樣接：

```text
1H condition:
  subscribe THIRD_BUY / center leave / previous high context

15m condition:
  subscribe completed center A
  subscribe completed center b-A
  compare force vectors for a/b and b-a/b-b
  wait custom golden_k + bullish_trend_k
```

其他模型可以完全不使用 Z3B 的金 K，也可以只用一買二買或中樞震盪策略。

## 12. 建議實作模組

```text
chanlun_core/
  models.py          # dataclass / pydantic schema
  calendar.py        # session, resample boundary
  bars.py            # raw bars and ChanBar inclusion
  fractals.py
  strokes.py
  segments.py
  centers.py
  trend_types.py
  divergence.py
  buy_sell_points.py
  interval_nest.py
  realtime_engine.py
  audit.py
```

## 13. 最小可驗收標準

第一階段完成後，必須能做到：

1. 任一股票輸入 1m K，輸出 1m/5m/15m/1H 的分型、筆、線段、中樞。
2. 任一輸出都有 `confirm_time`，不能事後偷看。
3. 能標出三類買賣點候選與失效原因。
4. 能輸出背馳比較的完整 `ForceVector`。
5. 同一份歷史資料全量跑與逐分鐘增量跑，結果必須一致。

## 14. 本輪結論

纏論共用核心應該先被實作成結構引擎，不應直接寫死任何單一策略。Z3B、三買、區間套、一買二買、中樞震盪，都只是訂閱這套核心事件後的策略層組合。
