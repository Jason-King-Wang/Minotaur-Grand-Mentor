# Z3B-Core v2.0 纏論三買量化模型規格 — 修正版

> 本版只處理「纏論三買模型本體」：1H 趨勢 / 三買情境判定、15m 回調結束確認、入場 / 停損 / 停利。  
> 不包含台股整股、零股、撮合、稅費、漲跌停、T+2 等執行層內容。  
> 核心修正：**先確認 1H 上的纏論三買情境，再啟動 15m 的 A、b-A、兩低不破、多頭趨勢 K 操作。**

---

## 0. 本版要修正的核心錯位

舊版的主要問題是把影片後半段的「15m 回調結束 / 入場確認流程」寫成了整個三買模型本體。正確拆法應該是：

```text
第一層：1H 纏論三買情境 Gate
先確認：有 1H 中樞、有向上離開、有上漲段、有回抽，且回抽不回中樞。
沒有這一層，後面的 15m A、b-A、兩低不破、大陽線全部沒有三買意義。

第二層：15m 回調終結確認
只在第一層成立後，才分析 15m 回調內部結構：A、a/b、b-A、b-a/b-b、兩低不破。

第三層：15m 入場觸發
回調終結後，等待多頭趨勢 K 確認；停損放金 K / 第二低點區域低點，停利放 1H 上攻段前高。
```

因此，本版不再允許：

```text
看到 15m A + b-A + 大陽線，就直接當成三買。
```

必須先有：

```text
1H 中樞向上離開後，第一次有效回抽不進中樞。
```

---

## 1. 一句話定義

`Z3B-Core v2.0` 是一套 1H / 15m 雙週期纏論第三類買點模型：

```text
在 1H 上先找出已完成的中樞 Z。
價格向上離開 Z 並形成上攻段。
隨後出現回抽，但回抽低點不回到 Z 的中樞重疊區內。
這才是 1H 第三類買點候選情境。

然後到 15m 分析這段回抽是否結束。
若 15m 回調結構確認空頭衰竭、兩次低點不破，並出現多頭趨勢 K，
則確認 1H 三買成立並觸發多單。

停損放第二低點 / 金 K 區域的底部極值。
停利放 1H 向上離開後、回抽前形成的上攻段高點。
```

---

## 2. 模型分層

### 2.1 Layer 1：1H 三買情境 Gate

這一層回答：

```text
現在是不是有資格談三買？
```

必要條件：

```text
1. 1H 存在已確認中樞 Z。
2. 價格向上離開 Z。
3. 向上離開後形成上攻段 impulse。
4. 上攻段之後開始回抽。
5. 回抽過程中，價格沒有回到 Z 的中樞重疊區內。
```

只有通過這一層，才允許啟動 15m 結構分析。

### 2.2 Layer 2：15m 回調終結確認

這一層回答：

```text
這段 1H 回抽是否已經結束？
```

分析內容：

```text
1. 回調段內的 15m 主中樞 A。
2. A 前後的下跌段 a / b。
3. 若 A 的 b > a，代表 15m 回調尚未結束，繼續往 b 內部找小中樞 b-A。
4. 若 A 的 b < a，代表 15m 回調本級別已有衰竭跡象，不直接買，仍需兩低不破 + 多頭趨勢 K 確認。
5. 若進入 b-A，則比較 b-a / b-b。
6. b-b < b-a 後，再等待兩次低點不破。
```

### 2.3 Layer 3：15m 入場觸發

這一層回答：

```text
何時可以實際開多？
```

必要條件：

```text
1. Layer 1 的 1H 三買情境仍有效。
2. Layer 2 已確認回調終結。
3. 第二低點不破第一低點。
4. 第二低點區域已形成金 K / golden low。
5. 後續出現多頭趨勢 K。
6. entry > stop_loss。
7. take_profit > entry。
```

---

## 3. 時間週期

```yaml
timeframes:
  trend_tf: 1H
  entry_tf: 15m
```

| 週期 | 用途 |
|---|---|
| 1H | 找主中樞 Z、向上離開、上攻段、回抽不回中樞、三買情境 |
| 15m | 判斷 1H 回抽是否結束、找入場 K、定義停損錨點 |

---

## 4. 基礎結構元件

### 4.1 K 線使用原則

```text
1. 所有判斷只使用已收盤 K 線。
2. 回測不得用尚未收盤的 high / low / close。
3. 所有 swing、leg、center 必須有確認時間 confirmed_time。
4. confirmed_time 之前，不得使用該結構。
```

### 4.2 Swing point

預設工程定義：

```yaml
swing:
  left_bars: 2
  right_bars: 2
```

```text
swing_high[i] = high[i] 是 i-left_bars 到 i+right_bars 區間最高 high
swing_low[i]  = low[i]  是 i-left_bars 到 i+right_bars 區間最低 low
confirmed_time = bar[i + right_bars].close_time
```

處理規則：

```text
1. 連續同方向 swing 必須壓縮，只保留更極端者。
2. 最終 swing 序列必須高低交替。
3. swing 用於建立大級別結構，但入場觸發不得因 right_bars 過度延遲而錯過多頭趨勢 K。
```

### 4.3 Leg / 走勢段

工程定義：

```text
leg = 兩個相鄰、方向相反的 confirmed swing 之間的價格段。
```

對下跌 leg：

```text
down_leg.start = swing_high
down_leg.end   = swing_low
down_leg.drop  = start.high - end.low
down_leg.bars  = end.index - start.index + 1
down_leg.slope = drop / bars
```

對上漲 leg：

```text
up_leg.start = swing_low
up_leg.end   = swing_high
up_leg.rise  = end.high - start.low
up_leg.bars  = end.index - start.index + 1
up_leg.slope = rise / bars
```

---

## 5. 中樞 Z 的正確工程定義

### 5.1 不再使用箱體極值作為中樞上下沿

舊版錯誤：

```text
center_upper = max(high inside center window)
center_lower = min(low inside center window)
```

這只是震盪箱體極值，不是纏論中樞重疊區。第三類買點應該以「中樞重疊區」作為是否回中樞的判準，而不是以整個震盪箱體最高點判準。

### 5.2 中樞重疊區

給定同級別連續三段走勢段 `L1, L2, L3`，每段都有價格區間：

```text
I_j = [leg_low_j, leg_high_j]
```

若三段存在共同重疊：

```text
z_lower = max(leg_low_1, leg_low_2, leg_low_3)
z_upper = min(leg_high_1, leg_high_2, leg_high_3)
```

且：

```text
z_lower <= z_upper
```

則形成中樞候選 `Z`。

資料結構：

```python
Zhongshu = {
    "start_time": ...,
    "end_time": ...,
    "overlap_upper": z_upper,
    "overlap_lower": z_lower,
    "box_high": max(high inside all member legs),   # 只供畫圖，不作三買上沿
    "box_low": min(low inside all member legs),     # 只供畫圖，不作三買下沿
    "member_legs": [L1, L2, L3, ...],
    "level_tf": "1H | 15m",
    "confirmed_time": ...
}
```

### 5.3 中樞延伸

後續 leg 若與中樞重疊區仍有交集，可視為中樞延伸：

```text
leg_interval ∩ [Z.overlap_lower, Z.overlap_upper] ≠ empty
```

延伸時可以更新：

```text
box_high / box_low / duration / member_legs
```

但三買判斷使用的核心邊界仍是：

```text
Z.overlap_upper
Z.overlap_lower
```

不得用 `box_high` 當成三買的中樞上沿。

---

## 6. 1H 三買情境 Gate

### 6.1 1H 主中樞 Z

1H 主中樞必須是已確認的中樞重疊區。

必要條件：

```text
1. 至少由三段 1H leg 的重疊形成。
2. Z.confirmed_time 已經發生。
3. Z 不是用未來資料回頭挑出的最佳中樞。
4. 若同時有多個 Z，只能使用當下已確認、且尚未被新的同級別中樞取代的 active Z。
```

禁止：

```text
1. 先掃完全部歷史，再挑一個跟後面上漲最相關的中樞。
2. 用整個震盪區最高 high 當中樞上沿。
3. 在中樞尚未確認前就使用它。
```

### 6.2 向上離開中樞

向上離開不是單純碰到中樞上方，而是從中樞區間向上形成離開段。

最低條件：

```text
upward_departure =
    close_1h > Z.overlap_upper
AND close_1h > previous_confirmed_1h_swing_high 或 impulse_high > previous_confirmed_1h_swing_high
```

建議加強條件：

```text
1. 離開段至少有一個 1H up_leg。
2. up_leg.end.high > Z.box_high 或 > previous_confirmed_swing_high。
3. 離開段不能只是單根影線刺破後收回。
```

### 6.3 上攻段 impulse

向上離開後，到回抽開始前的最高點，定義為 1H 上攻段高點：

```text
impulse_high = max(high after upward_departure and before pullback_start)
impulse_high_time = time of impulse_high
```

`target_high_1h` 預設等於：

```text
target_high_1h = impulse_high
```

若 impulse_high 已確認為 1H swing_high：

```text
target_source = confirmed_impulse_swing_high
```

若尚未確認但回調已經開始：

```text
target_source = provisional_impulse_high
```

### 6.4 回抽開始

回抽開始必須可觀察，不能在剛向上離開時就假設回抽存在。

回抽開始條件至少滿足其一：

```text
1. 1H 出現 confirmed swing_high，且後續價格向下離開該高點。
2. 15m 從 impulse_high 後形成至少一段 down_leg。
3. 價格從 impulse_high 回落幅度 >= min_pullback_depth。
```

預設：

```yaml
pullback:
  min_pullback_depth_mode: atr
  min_pullback_depth_atr_mult: 0.5
```

### 6.5 三買候選：回抽不回中樞

在回抽開始後，持續追蹤：

```text
pullback_low = min(low from pullback_start to current_time)
```

三買候選仍有效：

```text
pullback_low > Z.overlap_upper - tolerance
```

嚴格模式：

```text
pullback_low > Z.overlap_upper
```

容忍模式：

```text
pullback_low >= Z.overlap_upper - max(tick_size, ATR_1H * 0.01)
```

失效：

```text
if any low <= Z.overlap_upper - tolerance:
    invalidate current 1H 3B candidate
```

### 6.6 三買不是在這裡直接確認

重要：

```text
pullback_low 沒有回中樞，只代表 1H 三買候選有效。
它還不代表回調已結束。
```

真正確認三買，需要 15m 回調終結確認：

```text
1H_3B_CONFIRMED =
    1H_3B_CONTEXT_ACTIVE
AND 15m_pullback_terminal_confirmed
AND terminal_low > Z.overlap_upper - tolerance
```

---

## 7. 15m 回調段分析啟動條件

15m 分析只能在以下條件成立後啟動：

```text
1. 1H Z 已確認。
2. 1H 已向上離開 Z。
3. 1H impulse_high 已形成。
4. 1H 回抽已開始。
5. 截至目前為止，回抽沒有回到 Z.overlap_upper 以下。
```

禁止：

```text
1. 在沒有 1H 三買候選時搜尋 15m A / b-A。
2. 在任意下跌段中看到 b-A 和大陽線就開多。
3. 用 15m 後半流程反推 1H 三買。
```

15m 回調段時間範圍：

```text
pullback_segment_15m = [impulse_high_time, current_time]
```

---

## 8. 15m 主中樞 A

### 8.1 A 的角色

`A` 不是三買本體。它只是用來判斷：

```text
1H 回抽在 15m 裡是否已經走到衰竭。
```

A 必須位於：

```text
impulse_high_time 之後
且 1H 三買候選失效之前
```

### 8.2 A 的候選條件

```text
1. A 是 15m 中樞重疊區，不是箱體極值。
2. A 至少由三段 15m leg 的重疊形成。
3. A.confirmed_time 已發生。
4. A 必須在 1H pullback_segment_15m 內。
5. A 後方能定義離開 A 的下跌段 b。
```

### 8.3 A 的邊界

A 的三個邊界分開：

```text
A.overlap_upper / A.overlap_lower：用於結構判斷。
A.box_high / A.box_low：只用於畫圖或輔助觀察。
```

不得用 `box_high / box_low` 替代 `overlap_upper / overlap_lower`。

---

## 9. A 的 a / b 段比較

### 9.1 定義

對 15m 回調下跌而言：

```text
a = 進入 A 前的下跌段
b = 離開 A 後的下跌段
```

工程定義：

```text
a_start = A 前最近一個 15m down_leg 的起點 swing_high
a_end   = A 前 / A 內該 down_leg 的終點 swing_low

a_drop = a_start.high - a_end.low
a_bars = a_end.index - a_start.index + 1
a_slope = a_drop / a_bars
```

```text
b_start = A 內或 A 結束附近最後一個 15m swing_high
b_end   = A 後第一個有效 15m swing_low 或下跌延伸低點

b_drop = b_start.high - b_end.low
b_bars = b_end.index - b_start.index + 1
b_slope = b_drop / b_bars
```

比較預設使用：

```text
leg_drop
```

同時記錄：

```text
leg_slope
breakout_drop_from_center
```

避免只用 high-low 長度造成誤判。

### 9.2 容忍區間

不得用精確相等。

```text
equal_tolerance = max(tick_size * 2, ATR_15m * 0.02)
```

```text
if b_drop > a_drop + equal_tolerance:
    relation = B_GT_A
elif b_drop < a_drop - equal_tolerance:
    relation = B_LT_A
else:
    relation = B_APPROX_A
```

### 9.3 路徑選擇

#### Path A：A 的 b > a

```text
B_GT_A
=> 15m 回調在 A 級別尚未衰竭
=> 不能開多
=> 進入 b 段內部，尋找較小中樞 b-A
```

這是影片示範的主要路徑。

#### Path B：A 的 b < a

```text
B_LT_A
=> 15m 回調在 A 級別已有衰竭跡象
=> 仍不能直接買
=> 可以跳過 b-A，直接進入「兩低不破 + 多頭趨勢 K」確認
```

這是修正版補上的完整路徑。原因是：

```text
若 A 級別本身已經 b < a，代表回調有可能已經在 A 級別衰竭。
此時不需要強迫再去找 b 內部的小中樞 b-A。
但它仍然只是衰竭，不是開單。
必須等第二低點不破與多頭趨勢 K。
```

若要完全複製影片單一路徑，可用 config 關閉：

```yaml
entry_paths:
  direct_A_exhaustion_path: false
  nested_bA_path: true
```

建議完整模型預設：

```yaml
entry_paths:
  direct_A_exhaustion_path: true
  nested_bA_path: true
```

#### Path C：A 的 b ≈ a

```text
B_APPROX_A
=> 力度不明確
=> 不開單
=> 等新結構，或重建 A
```

---

## 10. b 段內部小中樞 b-A

### 10.1 啟動條件

只有當：

```text
1H_3B_CONTEXT_ACTIVE == true
AND A_relation == B_GT_A
```

才允許搜尋 `b-A`。

### 10.2 b-A 的角色

`b-A` 是 A 的 b 段內部較小級別的多空平衡區。它用來判斷：

```text
A 的 b 段是否在更小級別裡出現下跌衰竭。
```

### 10.3 b-A 候選條件

```text
1. b-A 必須位於 A 的 b 段內部或 b 段延伸內。
2. b-A 至少由三段 15m 或更細粒度 leg 的重疊形成。
3. b-A.confirmed_time 已發生。
4. b-A 不得與 A 完全重疊成同一個中樞。
5. b-A 的級別必須小於 A。
```

### 10.4 b-A 小於 A 的判準

不得只用價格 range。

建議判準：

```text
bA.duration_bars < A.duration_bars
AND bA.member_leg_count <= A.member_leg_count
AND bA.score < A.score
AND bA.overlap_range <= A.overlap_range * max_bA_range_ratio
```

預設：

```yaml
bA:
  max_duration_ratio: 0.8
  max_score_ratio: 0.8
  max_overlap_range_ratio: 0.8
```

其中：

```text
score = overlap_range * duration_bars
```

注意：

```text
range 條件只是輔助，不是唯一條件。
```

---

## 11. b-A 的 b-a / b-b 比較

### 11.1 定義

在 b-A 內部：

```text
b-a = 進入 b-A 前的下跌段
b-b = 離開 b-A 後的下跌段
```

工程定義：

```text
b_a_start = b-A 前最近 down_leg 的起點 swing_high
b_a_end   = b-A 前 / b-A 內該 down_leg 的終點 swing_low
b_a_drop  = b_a_start.high - b_a_end.low
b_a_bars  = b_a_end.index - b_a_start.index + 1
b_a_slope = b_a_drop / b_a_bars
```

```text
b_b_start = b-A 內或 b-A 後最近 down_leg 的起點 swing_high
b_b_end   = b-A 後第一個有效 swing_low 或下跌延伸低點
b_b_drop  = b_b_start.high - b_b_end.low
b_b_bars  = b_b_end.index - b_b_start.index + 1
b_b_slope = b_b_drop / b_b_bars
```

### 11.2 小轉大衰竭條件

預設：

```text
b_b_drop < b_a_drop - equal_tolerance
```

建議加強：

```text
AND b_b_slope <= b_a_slope
```

原因：

```text
影片中的 b-b < b-a 是下跌力度衰竭語義，不應只看絕對長度。
斜率可以防止「跌幅小但速度很快」被誤判為衰竭。
```

成立後：

```text
lower_tf_exhaustion = true
```

但仍然不能直接開單。接著等兩低不破。

---

## 12. 回調終結確認：兩次低點不破

### 12.1 適用路徑

兩低不破適用於兩種路徑：

```text
Path A：A 的 b < a 後，直接進入兩低確認。
Path B：A 的 b > a，進入 b-A，且 b-b < b-a 後，進入兩低確認。
```

### 12.2 低點定義

`low_1`：衰竭結構後的第一個明確低點。  
`low_2`：價格反彈後第二次回測低位形成的低點。

```text
low_1 = first_terminal_low_after_exhaustion
low_2 = second_retest_low_after_low_1
```

### 12.3 「孤立」條件

為避免普通小低點被誤認為兩低不破，必須要求：

```text
1. low_1 與 low_2 之間有明確反彈。
2. 反彈至少突破一個 15m minor swing_high，或反彈高度 >= min_rebound。
3. low_2 不能只是緊貼 low_1 後一兩根 K 的雜訊。
```

預設：

```yaml
isolated_lows:
  min_bars_between_lows: 3
  min_rebound_mode: atr
  min_rebound_atr_mult: 0.3
  require_minor_swing_break_between_lows: true
```

### 12.4 不破條件

```text
low_2.price >= low_1.price - break_tolerance
```

預設：

```yaml
break_tolerance:
  mode: max_tick_atr
  tick_mult: 1
  atr_mult: 0.01
```

可選的「回測低位」條件：

```text
low_2.price <= low_1.price + retest_upper_tolerance
```

若不加這條，模型會把「高位小回踩」也當成第二低點。建議開啟。

```yaml
retest_upper_tolerance:
  enabled: true
  atr_mult: 0.5
```

### 12.5 失效

```text
if low_2.price < low_1.price - break_tolerance:
    invalidate 15m terminal candidate
```

同時，只要 1H 回抽低點跌回 Z.overlap_upper 以下：

```text
invalidate entire 1H 3B candidate
```

---

## 13. 金 K / golden low / 停損錨點

### 13.1 分開三個概念

舊版把 golden_k、第二低點確認 K、多頭趨勢 K 混在一起。修正版分開：

```text
golden_low       = 第二低點區域的最低 low。
risk_anchor_bar  = 打出 golden_low 的那根 K。
confirmation_bar = 第一根確認第二低點不破且開始轉強的 K。
bullish_trend_k  = 光頭光腳大陽線 / 多頭趨勢 K，可與 confirmation_bar 同一根，也可在其後。
```

### 13.2 停損

停損使用：

```text
stop_loss = golden_low
```

也就是：

```text
stop_loss = risk_anchor_bar.low
```

禁止：

```text
stop_loss = bullish_trend_k.low
```

### 13.3 避免 lookahead 的 golden low 定義

若第二低點只有單根 K：

```text
golden_low = that_bar.low
risk_anchor_bar = that_bar
```

若第二低點是一段低位停住區：

```text
golden_low = min(low inside second-low cluster up to confirmation_bar)
risk_anchor_bar = bar that produced golden_low
```

不可使用 confirmation_bar 之後的 K 來回頭修改 golden_low。

---

## 14. 多頭趨勢 K

### 14.1 語義

多頭趨勢 K 是入場確認，不是三買環境本身，也不是停損來源。

它必須代表：

```text
1. 第二低點不破後，多頭明確反攻。
2. 收盤接近高位。
3. 實體明顯。
4. 位置上突破局部壓力。
```

### 14.2 量化條件

預設：

```text
bullish_trend_k =
    close > open
AND body / full_range >= min_body_range_ratio
AND upper_wick / full_range <= max_upper_wick_ratio
AND close_position >= min_close_position
AND body >= min_body_abs
AND close > local_resistance
```

其中：

```text
body = close - open
full_range = high - low
upper_wick = high - close
close_position = (close - low) / full_range
```

`min_body_abs` 可採用：

```text
max(0.25 * terminal_center_range, ATR_15m * body_atr_mult)
```

若是 nested b-A 路徑：

```text
terminal_center_range = bA.overlap_upper - bA.overlap_lower
local_resistance = max(bA.overlap_upper, most_recent_minor_swing_high)
```

若是 direct A exhaustion 路徑：

```text
terminal_center_range = A.overlap_upper - A.overlap_lower
local_resistance = most_recent_minor_swing_high after low_2
```

預設參數：

```yaml
bullish_trend_k:
  min_body_range_ratio: 0.60
  max_upper_wick_ratio: 0.20
  min_close_position: 0.75
  body_atr_mult: 0.5
  body_center_range_ratio: 0.25
  require_close_above_local_resistance: true
```

### 14.3 時間限制

多頭趨勢 K 必須在第二低點後有限時間內出現。

```yaml
bullish_trend_k:
  max_bars_after_low2: 8
```

若超過仍未出現：

```text
NO_BULLISH_TREND_K_TIMEOUT
```

### 14.4 失效條件

等待多頭趨勢 K 期間，若發生以下任何一項，候選失效：

```text
1. low < golden_low - break_tolerance。
2. low < low_1.price - break_tolerance。
3. 1H 回抽 low 回到 Z.overlap_upper 以下。
4. 形成新的更低下跌中樞，原低點結構失效。
5. 等待超過 max_bars_after_low2。
```

---

## 15. 三買確認與開多條件

### 15.1 1H 三買確認

在多頭趨勢 K 收盤時，同時確認：

```text
1H_3B_CONFIRMED =
    Z confirmed
AND upward_departure confirmed
AND impulse_high exists
AND pullback started
AND all pullback lows > Z.overlap_upper - tolerance
AND 15m terminal structure confirmed
AND golden_low > Z.overlap_upper - tolerance
AND bullish_trend_k valid
```

### 15.2 開多條件

所有條件同時成立：

```text
1. 1H_3B_CONTEXT_ACTIVE == true。
2. 15m 回調終結 confirmed。
3. golden_low 已定義。
4. bullish_trend_k 已收盤且有效。
5. entry_price > stop_loss。
6. target_high_1h > entry_price。
```

### 15.3 進場

訊號時間：

```text
signal_time = bullish_trend_k.close_time
```

回測預設成交：

```text
entry_price = next_15m_bar.open
```

不可用：

```text
entry_price = bullish_trend_k.close
```

除非特別模擬「收盤前即時偵測並成交」，否則會有執行偏誤。

---

## 16. 停損與停利

### 16.1 停損

```text
stop_loss = golden_low
```

若：

```text
entry_price <= stop_loss
```

拒絕交易：

```text
INVALID_RISK_ENTRY_LE_STOP
```

### 16.2 停利

```text
take_profit = target_high_1h
```

其中：

```text
target_high_1h = impulse_high before current pullback
```

注意：

```text
target_high_1h 必須在回抽開始後才能鎖定。
不能在剛向上離開中樞時就鎖定。
```

若：

```text
take_profit <= entry_price
```

拒絕交易：

```text
INVALID_TARGET_LE_ENTRY
```

### 16.3 盈虧比

```text
risk = entry_price - stop_loss
reward = take_profit - entry_price
rr = reward / risk
```

預設：

```yaml
risk_reward:
  hard_filter_enabled: false
  min_rr: null
```

建議回測同時記錄：

```text
rr
risk_distance_pct
entry_to_target_pct
```

若發現大陽線後追價導致 RR 長期過低，再把 `min_rr` 打開，而不是一開始就把影片案例的 1:4.5 寫死。

---

## 17. 狀態機

```text
WAIT_1H_ZHONGSHU
    -> WAIT_1H_UPWARD_DEPARTURE
    -> WAIT_1H_IMPULSE_HIGH
    -> WAIT_1H_PULLBACK_START
    -> ACTIVE_1H_3B_CONTEXT
    -> WAIT_15M_CENTER_A
    -> WAIT_15M_A_AB_COMPARE
    -> DIRECT_WAIT_TWO_LOWS              # A 的 b < a 路徑
    -> WAIT_15M_BA_CENTER                # A 的 b > a 路徑
    -> WAIT_15M_BA_INTERNAL_EXHAUSTION
    -> WAIT_TWO_LOWS_AND_GOLDEN_LOW
    -> WAIT_BULLISH_TREND_K
    -> CONFIRM_1H_3B_AND_SIGNAL
    -> IN_POSITION
    -> TRADE_CLOSED
```

狀態說明：

| State | 目的 | 失效 |
|---|---|---|
| `WAIT_1H_ZHONGSHU` | 找 1H 中樞 Z | 無 |
| `WAIT_1H_UPWARD_DEPARTURE` | 等價格向上離開 Z | 新低破 Z 或 Z 被取代 |
| `WAIT_1H_IMPULSE_HIGH` | 建立上攻段高點 | 無明確上攻段 |
| `WAIT_1H_PULLBACK_START` | 等回抽真的開始 | 無回抽則等待 |
| `ACTIVE_1H_3B_CONTEXT` | 1H 三買候選有效 | 回抽進入 Z.overlap_upper 以下 |
| `WAIT_15M_CENTER_A` | 在 1H 回抽內找 15m A | 找不到則等待；1H 失效則重置 |
| `WAIT_15M_A_AB_COMPARE` | 比較 A 的 a/b | b≈a 不明確 |
| `DIRECT_WAIT_TWO_LOWS` | A 的 b<a，直接等兩低 | 第二低破第一低 |
| `WAIT_15M_BA_CENTER` | A 的 b>a，往 b 內找 b-A | 找不到且超時 |
| `WAIT_15M_BA_INTERNAL_EXHAUSTION` | 比較 b-a/b-b | b-b 不小於 b-a |
| `WAIT_TWO_LOWS_AND_GOLDEN_LOW` | 找第二低點不破與 golden_low | 破低 / 1H 失效 |
| `WAIT_BULLISH_TREND_K` | 等多頭趨勢 K | 破 golden_low / 超時 / 1H 失效 |
| `CONFIRM_1H_3B_AND_SIGNAL` | 三買確認並產生訊號 | target 或 risk 無效 |
| `IN_POSITION` | 管理 SL / TP | 觸發出場 |
| `TRADE_CLOSED` | 記錄交易 | 回到等待下一候選 |

---

## 18. Reason codes

```text
NO_1H_ZHONGSHU
ZHONGSHU_NOT_CONFIRMED
NO_UPWARD_DEPARTURE
NO_IMPULSE_HIGH
NO_PULLBACK_START
PULLBACK_ENTERED_ZHONGSHU
ACTIVE_1H_3B_CONTEXT
NO_15M_CENTER_A
A_B_GT_A_GO_NESTED_BA
A_B_LT_A_DIRECT_EXHAUSTION_PATH
A_B_APPROX_A_AMBIGUOUS
NO_BA_CENTER
BA_NOT_SMALLER_THAN_A
BA_BB_NOT_LESS_THAN_BA
LOW2_BROKE_LOW1
LOW2_NOT_A_VALID_RETEST
NO_GOLDEN_LOW
GOLDEN_LOW_CONFIRMED
NO_BULLISH_TREND_K
NO_BULLISH_TREND_K_TIMEOUT
BULLISH_K_FAILED_BODY_RATIO
BULLISH_K_FAILED_WICK_RATIO
BULLISH_K_FAILED_CLOSE_POSITION
BULLISH_K_FAILED_LOCAL_RESISTANCE
CONFIRMED_1H_3B_SIGNAL
INVALID_RISK_ENTRY_LE_STOP
INVALID_TARGET_LE_ENTRY
STOP_LOSS_HIT
TAKE_PROFIT_HIT
```

---

## 19. Lookahead 防呆規則

### 19.1 中樞選擇

禁止：

```text
選 center_score 高且與後續離開最相關者。
```

修正為：

```text
只能從當下 confirmed active centers 中選。
若多個 active center 同時存在，使用固定優先規則：
1. 最近完成者優先；
2. 級別較大者優先；
3. duration 較長者優先；
4. 不得使用後續漲跌結果作為選擇依據。
```

### 19.2 impulse_high

```text
impulse_high 只能在回抽開始後鎖定。
```

### 19.3 15m A / b-A

```text
A / b-A 必須在 confirmed_time 後才可用。
不得先知道後面會出現 b 段，再回頭選 A。
```

### 19.4 golden_low

```text
golden_low 只能使用 second-low cluster 到 confirmation_bar 為止的 low。
不得用 confirmation_bar 之後的新低回頭修改。
```

### 19.5 bullish_trend_k

```text
bullish_trend_k 必須在收盤後才有效。
回測進場使用下一根 K 的 open。
```

---

## 20. 預設 config

```yaml
strategy:
  name: Z3B-Core
  version: "2.0"
  trend_tf: "1H"
  entry_tf: "15m"

swing:
  left_bars: 2
  right_bars: 2

zhongshu:
  min_member_legs: 3
  boundary_source: "overlap"      # not box_extreme
  strict_no_reentry: true
  active_selection:
    priority: ["recent_confirmed", "larger_level", "longer_duration"]

pullback:
  min_pullback_depth_mode: "atr"
  min_pullback_depth_atr_mult: 0.5
  reentry_tolerance_mode: "strict" # strict: low must stay > Z.overlap_upper

ab_compare:
  metric: "leg_drop"
  log_slope: true
  equal_tolerance_mode: "max_tick_atr"
  equal_tolerance_tick_mult: 2
  equal_tolerance_atr_mult: 0.02

entry_paths:
  direct_A_exhaustion_path: true
  nested_bA_path: true

bA:
  max_duration_ratio: 0.8
  max_score_ratio: 0.8
  max_overlap_range_ratio: 0.8

isolated_lows:
  min_bars_between_lows: 3
  min_rebound_mode: "atr"
  min_rebound_atr_mult: 0.3
  require_minor_swing_break_between_lows: true
  break_tolerance_mode: "max_tick_atr"
  break_tolerance_tick_mult: 1
  break_tolerance_atr_mult: 0.01
  retest_upper_tolerance_enabled: true
  retest_upper_tolerance_atr_mult: 0.5

bullish_trend_k:
  min_body_range_ratio: 0.60
  max_upper_wick_ratio: 0.20
  min_close_position: 0.75
  body_atr_mult: 0.5
  body_center_range_ratio: 0.25
  require_close_above_local_resistance: true
  max_bars_after_low2: 8

risk_reward:
  hard_filter_enabled: false
  min_rr: null
```

---

## 21. 最小可實作 pseudocode

```python
def on_new_15m_bar(bar):
    update_1h_if_needed()
    update_swings_and_legs()
    update_active_zhongshu()

    # Layer 1: 1H 三買情境 Gate
    if state == "WAIT_1H_ZHONGSHU":
        Z = get_confirmed_active_1h_zhongshu()
        if Z:
            ctx.Z = Z
            state = "WAIT_1H_UPWARD_DEPARTURE"

    if state == "WAIT_1H_UPWARD_DEPARTURE":
        if upward_departure_confirmed(ctx.Z):
            ctx.departure_time = current_time
            state = "WAIT_1H_IMPULSE_HIGH"

    if state == "WAIT_1H_IMPULSE_HIGH":
        if pullback_started_after_departure():
            ctx.impulse_high = lock_impulse_high()
            ctx.target_high_1h = ctx.impulse_high.price
            ctx.pullback_start_time = current_time
            state = "ACTIVE_1H_3B_CONTEXT"

    if state in STATES_AFTER_3B_CONTEXT:
        if pullback_low_since(ctx.pullback_start_time) <= ctx.Z.overlap_upper - tolerance:
            reset(reason="PULLBACK_ENTERED_ZHONGSHU")
            return

    if state == "ACTIVE_1H_3B_CONTEXT":
        state = "WAIT_15M_CENTER_A"

    # Layer 2: 15m 回調終結確認
    if state == "WAIT_15M_CENTER_A":
        A = find_confirmed_15m_center_A(ctx.pullback_start_time, current_time)
        if A:
            ctx.A = A
            state = "WAIT_15M_A_AB_COMPARE"

    if state == "WAIT_15M_A_AB_COMPARE":
        relation = compare_A_a_b(ctx.A)
        if relation == "B_GT_A":
            state = "WAIT_15M_BA_CENTER"
        elif relation == "B_LT_A" and config.entry_paths.direct_A_exhaustion_path:
            ctx.exhaustion_source = "A_DIRECT"
            state = "WAIT_TWO_LOWS_AND_GOLDEN_LOW"
        else:
            reset_or_wait(reason="A_B_APPROX_A_AMBIGUOUS")

    if state == "WAIT_15M_BA_CENTER":
        bA = find_confirmed_bA_inside_A_b_leg(ctx.A)
        if bA and is_smaller_center(bA, ctx.A):
            ctx.bA = bA
            state = "WAIT_15M_BA_INTERNAL_EXHAUSTION"

    if state == "WAIT_15M_BA_INTERNAL_EXHAUSTION":
        if compare_bA_internal_ba_bb(ctx.bA) == "BB_LT_BA":
            ctx.exhaustion_source = "NESTED_BA"
            state = "WAIT_TWO_LOWS_AND_GOLDEN_LOW"
        else:
            wait_or_reset(reason="BA_BB_NOT_LESS_THAN_BA")

    # Layer 3: 入場確認
    if state == "WAIT_TWO_LOWS_AND_GOLDEN_LOW":
        lows = detect_two_isolated_lows_after_exhaustion(ctx)
        if lows.valid:
            ctx.low1 = lows.low1
            ctx.low2 = lows.low2
            ctx.golden_low = lows.golden_low
            ctx.risk_anchor_bar = lows.risk_anchor_bar
            state = "WAIT_BULLISH_TREND_K"
        elif lows.broke:
            reset(reason="LOW2_BROKE_LOW1")

    if state == "WAIT_BULLISH_TREND_K":
        if broke_golden_low_or_timeout(ctx):
            reset(reason="NO_BULLISH_TREND_K_TIMEOUT")
            return

        if is_valid_bullish_trend_k(bar, ctx):
            entry = next_bar_open_estimate_or_schedule()
            stop = ctx.golden_low
            target = ctx.target_high_1h

            if entry <= stop:
                reset(reason="INVALID_RISK_ENTRY_LE_STOP")
                return
            if target <= entry:
                reset(reason="INVALID_TARGET_LE_ENTRY")
                return

            emit_signal(
                reason="CONFIRMED_1H_3B_SIGNAL",
                entry_trigger_bar=bar,
                risk_anchor_bar=ctx.risk_anchor_bar,
                stop_loss=stop,
                take_profit=target,
            )
            state = "IN_POSITION"
```

---

## 22. 舊版規則對照修正

| 舊版寫法 | 修正版 |
|---|---|
| 先找 15m A、b-A，再當作三買模型 | 先通過 1H 三買情境 Gate，才允許 15m 操作 |
| `center_upper = max(high)` | `Z.overlap_upper = min(leg_highs)`，箱體高點只供畫圖 |
| `pullback_low >= center_upper` 就啟動完整流程 | 這只是候選有效；三買要等 15m 終結確認 |
| A 的 `b < a` 只作觀念、不走入場 | 修正為可走 direct exhaustion path，但仍需兩低不破 + 多頭 K |
| b-A 小於 A 只看 range | 改看 duration、score、overlap_range、member legs |
| golden_k = 第二低點確認最後一根 K | 改成 golden_low / risk_anchor_bar / confirmation_bar 分離 |
| 多頭趨勢 K 只看陽線 body >= 0.25*bA_range | 加入 body/range、上影線、收盤位置、突破局部壓力 |
| 等多頭趨勢 K 無超時 / 失效 | 加入破 golden_low、破 1H 中樞上沿、超時、新低等失效 |
| target_high 在向上離開時鎖定 | 改為回抽開始後鎖定 impulse_high |
| `b == a` 精確相等 | 改用 tolerance |

---

## 23. 總結

本版的核心是：

```text
三買不是 15m 大陽線。
三買也不是 15m b-A。
三買首先是 1H 中樞向上離開後的回抽不回中樞。
15m 的 A、b-A、兩低不破、多頭趨勢 K，只是用來確認這個回抽已經結束，並決定實際入場點與停損點。
```

因此，實作時必須先過：

```text
1H_ZHONGSHU -> UPWARD_DEPARTURE -> IMPULSE_HIGH -> PULLBACK_NO_REENTRY
```

再進入：

```text
15M_A -> AB_COMPARE -> optional bA -> TWO_LOWS -> BULLISH_TREND_K
```

否則後半段規則即使全部成立，也不能視為纏論第三類買點。
