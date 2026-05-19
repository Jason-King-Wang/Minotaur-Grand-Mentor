# Z3B-Prime 中樞三買量化模型規格 v1.1

**中文名**：Z3B-Prime 中樞三買模型  
**英文名**：Z3B-Prime Center Third-Buy Model  
**策略代號**：`Z3B-Prime`  
**模組 / repo 建議名稱**：`z3b_prime`  
**方向**：只做多  
**主策略來源**：第一部影片  
**觀念輔助來源**：第二部影片  

---

## 0. v1.1 重要修正

使用者已確認：前後兩部影片是不同內容；**第一部是策略實作主體，第二部主要是中樞觀念教學**。

因此本版做以下修正：

```text
1. 第一部影片 = 開單流程、停損、停利、15m 確認邏輯的最高優先來源。
2. 第二部影片 = 用來理解「中樞是多空平衡區」與「MACD DIF/DEA 零軸可輔助判斷中樞級別」。
3. 第二部不能反過來新增第一部沒有使用的開單路徑。
4. MACD 零軸判斷在 v1.1 預設為 diagnostic / advisory，不是硬性開單或拒單條件。
5. 原先文件中的 Z3B-MACD 名稱容易讓人誤解 MACD 是策略核心，因此改名為 Z3B-Prime。
```

---

## 1. 一句話定義

`Z3B-Prime` 是一套第一部影片規則導出的第三類買點多單模型：

```text
先在 1H 找到上漲趨勢樹立後的第三類買點環境：
價格向上離開中樞，回抽不跌破中樞上沿。

再到 15m 判斷這段回抽是否真的結束：
主中樞 A 之後若 b > a，不能買，繼續往 b 段內部找小中樞 b-A。
只有 b-A 內部出現 b-b < b-a、兩次孤立低點不破，
並且出現多頭趨勢 K，才開多。

停損放多頭趨勢 K 的底部極值點。
停利放 1H 趨勢週期前高。
```

---

## 2. 來源權重規則

### 2.1 第一部影片：策略來源

第一部影片負責定義：

```text
1. 策略方向：第 3 類買點做多。
2. 週期：1H 趨勢週期 + 15m 交易週期。
3. 不抄底，等上漲趨勢樹立。
4. 1H 向上離開中樞，回抽不跌破中樞上沿。
5. 15m 回調內先看中樞 A。
6. 主中樞 A 後 b > a，代表沒有背馳 / 回調未結束，不開多。
7. 繼續看 b 段內部的小中樞 b-A。
8. b-b < b-a，代表小級別空頭力量衰竭，可等待確認。
9. 兩次孤立低點不破。
10. 下一根 / 後續出現多頭趨勢 K，直接入場做多。
11. 停損 = 金 K / 多頭趨勢 K 的底部極值點。
12. 停利 = 趨勢週期 1H 的前高。
```

### 2.2 第二部影片：觀念輔助

第二部影片只能用於：

```text
1. 理解中樞 = 多空平衡區 / 區間震盪 / 價格來回拉扯的地方。
2. 理解 a = 進入中樞前的下跌段，b = 離開中樞後的下跌段。
3. 理解 b > a = 空頭力量仍強，不能猜底。
4. 理解 b < a = 空頭力量衰弱，但仍然需要確認，不能直接開單。
5. 理解 MACD DIF/DEA 與 0 軸的關係可輔助判斷中樞級別。
```

第二部影片**不能**用於：

```text
1. 不能新增「主中樞 A 的 b < a 就直接開多」路徑。
2. 不能把 MACD 0 軸變成硬性開單條件，除非使用者之後明確要求。
3. 不能改掉第一部的停損、停利。
4. 不能改掉第一部的入場確認：兩次孤立低點不破 + 多頭趨勢 K。
5. 不能把策略改成 MACD 背離策略。
```

---

## 3. 名稱說明

本版不再使用 `Z3B-MACD` 作為主名，因為 MACD 來自第二部觀念影片，預設只是輔助辨識中樞級別，不是核心交易觸發條件。

```text
Z3B = Zhongshu / Zero context + Third Buy
Prime = 第一部影片為主，策略主線不被第二部觀念覆蓋
```

建議：

```text
strategy_id: Z3B-Prime
package_name: z3b_prime
```

保留一個 optional module：

```text
macd_zero_axis_diagnostics
```

它只負責輸出中樞級別註記，不直接決定買賣。

---

## 4. 絕對原則

### 4.1 不做的事

```text
1. 不做空。
2. 不抄底。
3. 不做 1 買猜底。
4. 不使用均線交叉作為進出場。
5. 不使用 RSI / KD / 布林通道作為必要條件。
6. 不使用 MACD 金叉死叉作為進出場。
7. 不把 MACD 背離當成核心開單條件。
8. 不把停利改成固定盈虧比。
9. 不把停損改成 ATR 或固定百分比。
10. 不因為主中樞 A 的 b < a 就直接開多。
11. 不因為價格出現大陽線就直接開多；前面結構必須完整。
```

### 4.2 必須遵守的事

```text
1. 所有訊號只能使用已收盤 K 線。
2. 所有 swing、center、leg 都必須可重現，不允許人工畫線。
3. 第一部影片的完整路徑缺一不可。
4. 所有未開單原因都要記錄 reason_code。
5. 預設寧可少開單，也不要誤判成第三類買點。
6. 所有低階識別參數集中在 config。
7. 工程識別參數不可被當作策略優化結果。
```

---

## 5. 時間週期

| 名稱 | 週期 | 用途 |
|---|---:|---|
| `trend_tf` | 1H | 趨勢週期：找主中樞、向上離開、結構突破、潛在 3 買、停利前高 |
| `entry_tf` | 15m | 交易週期：找回調內中樞 A、b-A、兩次低點不破、多頭趨勢 K、入場與停損 |

```yaml
timeframes:
  trend_tf: 1h
  entry_tf: 15m
```

---

## 6. 輸入資料

每個標的、每個週期至少需要：

```text
timestamp
symbol
open
high
low
close
volume
```

要求：

```text
1. 15m 必須能對應到最新已收盤 1H。
2. 不可在 1H 尚未收盤時使用該 1H K 的 close/high/low 判斷 1H 狀態。
3. 不可在 15m 尚未收盤時使用該 15m K 產生訊號。
4. 若資料直接只有 15m，可以由 15m resample 成 1H，但 resample 後仍必須遵守收盤時間。
```

---

## 7. 低階市場結構元件

本節是讓電腦能自動識別影片中人眼看到的結構。這些是工程識別定義，不是外加交易邏輯。

### 7.1 Confirmed swing point

為避免 lookahead bias，swing point 必須延遲確認。

預設：

```yaml
swing:
  left_bars: 2
  right_bars: 2
```

定義：

```text
swing_high[i] = high[i] 是 i-left_bars 到 i+right_bars 區間最高 high
swing_low[i]  = low[i]  是 i-left_bars 到 i+right_bars 區間最低 low
```

確認時間：

```text
confirmed_time = bar[i + right_bars].close_time
```

注意：

```text
1. 在 confirmed_time 之前，不得使用該 swing。
2. 連續同方向 swing 必須壓縮，只保留更極端者。
3. 最終 swing 序列必須高低交替。
```

### 7.2 中樞 / 多空平衡區

中樞不是固定 K 數，也不是固定 ATR 箱體。

本模型依據第一部策略和第二部觀念，將中樞定義為：

```text
趨勢中價格停下來、反覆震盪、多空拉扯的區域。
```

自動化候選條件：

```text
1. 區間內至少有 min_center_swings 個 confirmed swing point。
2. swing high / swing low 呈交替結構。
3. 價格在區間內至少出現 min_midline_crosses 次中位線穿越。
4. 區間 K 數 >= min_center_bars。
```

預設：

```yaml
center_detection:
  min_center_swings: 4
  min_center_bars: 5
  min_midline_crosses: 2
  use_edges: wick_extreme
```

中樞上下沿採用影線極值：

```text
center_upper = max(high inside center window)
center_lower = min(low inside center window)
center_mid   = (center_upper + center_lower) / 2
center_range = center_upper - center_lower
```

### 7.3 中樞分數

若同一段有多個候選中樞，使用價格結構分數選擇，而不是先用 MACD 排除。

```text
center_score = center_range * center_duration_bars
```

若分數接近，選較晚形成者或與當前回調段最相關者。

---

## 8. MACD 零軸診斷模組

### 8.1 v1.1 的定位

第二部影片提到 MACD DIF / DEA 與 0 軸可輔助判斷中樞級別。使用者已確認第二部是教觀念，因此 v1.1 將 MACD 設為：

```text
diagnostic only / advisory only
```

也就是：

```text
1. 可以記錄中樞級別診斷。
2. 可以畫在圖上供檢查。
3. 可以輸出到 signal log。
4. 預設不能單獨決定開單或拒單。
```

### 8.2 MACD 公式

```text
DIF = EMA(close, fast) - EMA(close, slow)
DEA = EMA(DIF, signal)
HIST = DIF - DEA
```

預設：

```yaml
macd:
  fast: 12
  slow: 26
  signal: 9
```

### 8.3 只看 DIF / DEA，不看柱狀圖

```yaml
center_level_diagnostic:
  enabled: true
  zero_axis_source: [DIF, DEA]
  use_histogram: false
  hard_filter: false
```

### 8.4 觸碰 / 穿越 0 軸

```text
dif_touch_zero = min(DIF in center) <= 0 <= max(DIF in center)
dea_touch_zero = min(DEA in center) <= 0 <= max(DEA in center)
```

穿越次數：

```text
cross_count(line) = line 的正負號切換次數
```

診斷分類：

```text
if not dif_touch_zero and not dea_touch_zero:
    center_level_diag = BELOW_CURRENT

elif dif_touch_zero and dea_touch_zero and not (dif_cross_count >= 2 and dea_cross_count >= 2):
    center_level_diag = CURRENT_LIKE

elif dif_cross_count >= 2 and dea_cross_count >= 2:
    center_level_diag = ABOVE_CURRENT_LIKE
```

重要：

```text
center_level_diag 不得在 v1.1 預設模式下直接阻擋交易。
```

---

## 9. 1H 趨勢週期邏輯

### 9.1 1H 主中樞

在 1H 上使用 price-based center detector 找主中樞。

主中樞選擇：

```text
1. 必須是價格反覆震盪的多空平衡區。
2. 使用影線極值定義上下沿。
3. 不要求 MACD 診斷必須為 CURRENT_LIKE。
4. 若多個候選，選 center_score 較高且與後續向上離開最相關者。
```

資料結構：

```python
Center1H = {
    "start_time": ...,
    "end_time": ...,
    "upper": ...,
    "lower": ...,
    "mid": ...,
    "range": ...,
    "score": ...,
    "macd_level_diag": "BELOW_CURRENT | CURRENT_LIKE | ABOVE_CURRENT_LIKE | UNKNOWN"
}
```

### 9.2 上漲趨勢樹立

第一部影片的核心是：不要抄底，等上漲趨勢樹立。

自動化條件：

```text
1. 1H 已找到主中樞。
2. 價格向上離開主中樞。
3. 價格突破前一個已確認 1H swing_high。
```

向上離開：

```text
close_1h > center_upper
```

結構突破：

```text
close_1h > previous_confirmed_1h_swing_high
```

二者可以同一根 1H K 完成，也可以先後完成。

### 9.3 1H 潛在第三類買點

上漲趨勢樹立後，等待 1H 回抽。

潛在 3 買成立：

```text
pullback_low_1h >= center_upper
```

嚴格規則：

```text
1. center_upper 使用主中樞內 high 的最大值。
2. pullback_low_1h 使用影線 low。
3. v1.1 不允許影線跌破後收回。
4. 只要 low < center_upper，該次 1H 3 買候選失效。
```

1H 潛在 3 買成立後：

```text
不直接開單，只啟動 15m 入場檢查。
```

### 9.4 1H 停利前高

第一部影片停利放趨勢週期前高。

```text
take_profit = target_high_1h
```

`target_high_1h` 定義：

```text
在 1H 向上離開中樞後、目前回抽開始前，形成的最高已確認 swing_high。
```

若尚未形成 confirmed swing_high：

```text
使用向上離開後到回抽開始前的最高 high，並標記：
target_source = unconfirmed_impulse_high
```

---

## 10. 15m 回調段

15m 只在 1H 潛在 3 買存在時啟動。

### 10.1 回調段時間範圍

```text
pullback_segment_15m = 從 1H 向上離開後的最高點 / 回抽開始點，到目前 15m K 線。
```

工程映射：

```text
pullback_start_15m_time >= 1H impulse_high_time
```

---

## 11. 15m 主中樞 A

### 11.1 A 的定位

`A` 是 15m 回調段裡的主要多空平衡區。

它不是隨便的短暫反彈，也不是只用 MACD 決定。

候選條件：

```text
1. 位於 15m pullback_segment 內。
2. 滿足 price-based center candidate 條件。
3. 區間內價格有明顯來回震盪。
4. A 之後能定義出離開中樞的 b 段。
```

選擇規則：

```text
score = center_range * center_duration_bars
選 score 較高且符合回調主結構者。
```

MACD 零軸診斷只記錄：

```text
A.macd_level_diag = BELOW_CURRENT | CURRENT_LIKE | ABOVE_CURRENT_LIKE | UNKNOWN
```

不可因 A.macd_level_diag 不是 CURRENT_LIKE 而預設拒單。

---

## 12. a / b 段定義

對 15m 回調下跌而言：

```text
a = 進入中樞 A 前的下跌段
b = 離開中樞 A 後的下跌段
```

自動化定義：

```text
a_start = A_start 前最近一個 confirmed swing_high
a_end   = A_start 附近 / A 內第一個 confirmed swing_low

a_length = a_start.high - a_end.low
```

```text
b_start = A 內或 A_end 附近最後一個 confirmed swing_high
b_end   = A_end 之後第一個 confirmed swing_low

b_length = b_start.high - b_end.low
```

若找不到 confirmed swing，允許 fallback 到該區間價格極值，但必須記錄：

```text
fallback_used = true
fallback_reason = missing_confirmed_swing
```

---

## 13. a / b 判斷：以第一部為主

### 13.1 b > a

第一部影片示範的核心路徑：

```text
b > a
=> 沒有背馳 / 空頭力量仍強 / 15m 回調尚未結束
=> 不開多
=> 繼續往 b 段內部找 b-A
```

策略狀態轉移：

```text
if b_length > a_length:
    log(B_GREATER_THAN_A_WAIT_BA)
    state = WAIT_15M_BA_CENTER
```

### 13.2 b == a

```text
if b_length == a_length:
    不明確，不開單，等待新結構。
```

### 13.3 b < a

第二部觀念影片說 b < a 代表空頭力量衰弱，但使用者已確認第二部是觀念教學，不應新增第一部沒有的入場路徑。

因此 v1.1 規則為：

```text
if b_length < a_length:
    記錄空頭衰弱診斷
    不直接開多
    不進入第一部 b-A 路徑，除非後續仍形成完整 b-A 結構
```

reason code：

```text
A_B_LESS_THAN_A_CONCEPT_ONLY_NO_ENTRY
```

也就是：

```text
b < a 只作為市場狀態註記，不作為 v1.1 開單條件。
```

---

## 14. b 段內部小中樞 b-A

### 14.1 b-A 的定位

第一部影片的有效入場路徑是：主中樞 A 比較後 `b > a`，再往 b 段內部找小中樞 `b-A`。

`b-A` 是 b 段內部的較小多空平衡區，不是單根反彈。

候選條件：

```text
1. 出現在 b 段內部或 b 段後續延伸的下跌結構中。
2. 滿足 price-based center candidate 條件。
3. 區間內價格有來回震盪。
4. b-A 的 range / score 應小於 A，符合「小中樞」語義。
5. MACD 診斷只記錄，不預設硬性拒絕。
```

建議硬條件：

```text
bA.range < A.range
```

如不滿足：

```text
NO_SMALLER_BA_CENTER
```

### 14.2 b-a 與 b-b

在 b-A 內部再比較兩段下跌力量：

```text
b-a = 進入 b-A 前的下跌段
b-b = 離開 b-A 後的下跌段
```

自動化定義：

```text
b_a_start = b-A 前最近 confirmed swing_high
b_a_end   = b-A 內第一個 confirmed swing_low
b_a_length = b_a_start.high - b_a_end.low
```

```text
b_b_start = b-A 內或 b-A 結束附近最後 confirmed swing_high
b_b_end   = b-A 後第一個 confirmed swing_low
b_b_length = b_b_start.high - b_b_end.low
```

### 14.3 小轉大條件

第一部影片的關鍵條件：

```text
b-b < b-a
```

量化：

```text
small_to_big_exhaustion = b_b_length < b_a_length
```

若：

```text
b_b_length >= b_a_length
```

則：

```text
不開單，繼續等待或重置候選。
```

reason code：

```text
BB_NOT_LESS_THAN_BA
```

---

## 15. 兩次孤立低點不破

### 15.1 定義

使用者補充後的自動化定義：

```text
iso_low_1 = b-A 開始那次回彈的起點低點
iso_low_2 = b-A 後第二次回到低位的低點
```

程式定義：

```text
iso_low_1 = b-A start 附近第一個 confirmed swing_low
iso_low_2 = b-A end 之後第一個 confirmed swing_low
```

不破條件：

```text
iso_low_2.low >= iso_low_1.low
```

v1.1 嚴格使用影線 low：

```text
不允許跌破後收回。
```

### 15.2 等待確認

如果 `iso_low_2` 尚未 confirmed：

```text
不能提前判斷不破。
不能提前開單。
```

若：

```text
iso_low_2.low < iso_low_1.low
```

則失效：

```text
SECOND_LOW_BROKE_FIRST_LOW
```

---

## 16. 多頭趨勢 K

### 16.1 定義

第一部影片入場前要看到 15m 多頭趨勢 K / 光頭光腳大陽線。使用者指定可用 b-A 高低落差的 1/4 量化。

```text
bullish_trend_k =
    close > open
AND (close - open) >= 0.25 * bA_range
```

其中：

```text
bA_range = bA.upper - bA.lower
```

### 16.2 出現順序

多頭趨勢 K 必須在以下條件都成立後才有效：

```text
1. 1H 潛在 3 買成立。
2. 15m 主中樞 A 出現。
3. A 的 b > a，進入 b-A 觀察。
4. b-A 出現。
5. b-b < b-a。
6. 兩次孤立低點不破。
7. 然後才等多頭趨勢 K。
```

若大陽線提前出現：

```text
EARLY_BULLISH_K_BEFORE_STRUCTURE_COMPLETE
```

不可開單。

---

## 17. 開單、停損、停利

### 17.1 完整開多條件

所有條件同時成立才開多：

```text
1. 1H 找到 price-based 主中樞。
2. 1H close 向上離開中樞上沿。
3. 1H close 突破前 confirmed swing_high，代表上漲趨勢樹立。
4. 1H 回抽 low 不跌破中樞上沿。
5. 15m 回調段內找到主中樞 A。
6. A 的 b_length > a_length。
7. b 段內部找到小中樞 b-A。
8. bA.range < A.range。
9. b_b_length < b_a_length。
10. iso_low_2.low >= iso_low_1.low。
11. 出現 15m 多頭趨勢 K。
```

注意：

```text
A 的 b_length < a_length 在 v1.1 不是開多條件。
```

### 17.2 進場

回測預設：

```text
entry_price = 多頭趨勢 K 後下一根 15m K 線 open
```

訊號時間：

```text
signal_time = bullish_trend_k.close_time
```

實盤告警可以在多頭趨勢 K 收盤後觸發，但回測不能用同根 close 成交，避免 lookahead / execution bias。

### 17.3 停損

照第一部影片：

```text
stop_loss = bullish_trend_k.low
```

若：

```text
entry_price <= stop_loss
```

不開單：

```text
INVALID_RISK_ENTRY_LE_STOP
```

### 17.4 停利

照第一部影片：

```text
take_profit = target_high_1h
```

若：

```text
take_profit <= entry_price
```

不開單：

```text
INVALID_TARGET_LE_ENTRY
```

### 17.5 盈虧比

盈虧比只計算，不作固定門檻：

```text
risk = entry_price - stop_loss
reward = take_profit - entry_price
rr = reward / risk
```

影片案例的 1:4.5 只是該筆交易自然算出的結果，不是固定策略條件。

---

## 18. 狀態機

策略必須實作成狀態機。

```text
WAIT_1H_CENTER
    -> WAIT_1H_UPWARD_LEAVE
    -> WAIT_1H_STRUCTURE_BREAK
    -> WAIT_1H_PULLBACK_3BUY
    -> WAIT_15M_CENTER_A
    -> WAIT_15M_AB_COMPARE
    -> WAIT_15M_BA_CENTER
    -> WAIT_15M_BA_BB_COMPARE
    -> WAIT_15M_ISOLATED_LOWS
    -> WAIT_15M_BULLISH_TREND_K
    -> IN_POSITION
    -> TRADE_CLOSED
```

| State | 目的 | 失效 / 等待條件 |
|---|---|---|
| `WAIT_1H_CENTER` | 找 1H 主中樞 | 無中樞則等待 |
| `WAIT_1H_UPWARD_LEAVE` | 等 close_1h > center_upper | 跌破 center_lower 則重找 |
| `WAIT_1H_STRUCTURE_BREAK` | 等突破前 1H swing_high | 回到中樞內則重找 |
| `WAIT_1H_PULLBACK_3BUY` | 等回抽 low >= center_upper | low < center_upper 則失效 |
| `WAIT_15M_CENTER_A` | 找 15m 回調主中樞 A | 找不到則等待 |
| `WAIT_15M_AB_COMPARE` | 比較 A 的 a/b | b <= a 不走第一部入場路徑 |
| `WAIT_15M_BA_CENTER` | 在 b 段內找 b-A | 找不到則等待 |
| `WAIT_15M_BA_BB_COMPARE` | 比較 b-a / b-b | b-b >= b-a 則等待或失效 |
| `WAIT_15M_ISOLATED_LOWS` | 等第二低點確認不破 | 第二低點破第一低點則失效 |
| `WAIT_15M_BULLISH_TREND_K` | 等多頭趨勢 K | 未出現則等待 |
| `IN_POSITION` | 管理 SL / TP | 觸發 SL 或 TP 出場 |
| `TRADE_CLOSED` | 記錄交易 | 回到等待下一候選 |

---

## 19. Reason codes

```text
NO_1H_CENTER
NO_UPWARD_LEAVE
NO_STRUCTURE_BREAK
PULLBACK_BROKE_CENTER_UPPER
NO_15M_CENTER_A
B_GREATER_THAN_A_WAIT_BA
A_B_LESS_THAN_A_CONCEPT_ONLY_NO_ENTRY
B_EQUAL_A_NOT_CLEAR
NO_BA_CENTER
NO_SMALLER_BA_CENTER
BB_NOT_LESS_THAN_BA
SECOND_LOW_BROKE_FIRST_LOW
NO_BULLISH_TREND_K
EARLY_BULLISH_K_BEFORE_STRUCTURE_COMPLETE
INVALID_RISK_ENTRY_LE_STOP
INVALID_TARGET_LE_ENTRY
ENTRY_SIGNAL_VALID
STOP_LOSS_HIT
TAKE_PROFIT_HIT
AMBIGUOUS_BAR_STOP_FIRST
MACD_DIAG_BELOW_CURRENT
MACD_DIAG_CURRENT_LIKE
MACD_DIAG_ABOVE_CURRENT_LIKE
FALLBACK_MISSING_CONFIRMED_SWING
```

---

## 20. 回測規則

### 20.1 持倉限制

```yaml
position:
  side: long_only
  max_positions_per_symbol: 1
  allow_pyramiding: false
```

### 20.2 手續費與滑點

```yaml
execution:
  fee_rate: 0.0005
  slippage_bps: 0
```

滑點計算：

```text
long_entry_fill = entry_price * (1 + slippage_bps / 10000)
long_exit_fill  = exit_price  * (1 - slippage_bps / 10000)
```

### 20.3 同一根 K 同時碰停損與停利

若持倉後某根 15m K 同時滿足：

```text
low <= stop_loss
high >= take_profit
```

保守處理：

```text
先觸發 stop_loss
```

reason code：

```text
AMBIGUOUS_BAR_STOP_FIRST
```

### 20.4 出場優先順序

每根 15m K：

```text
1. stop_loss
2. take_profit
```

v1.1 無移動止盈，無反向訊號出場。

---

## 21. Config 範例

```yaml
strategy_id: Z3B-Prime
symbols:
  - BTCUSDT
  - ETHUSDT

timeframes:
  trend_tf: 1h
  entry_tf: 15m

swing:
  left_bars: 2
  right_bars: 2

center_detection:
  min_center_swings: 4
  min_center_bars: 5
  min_midline_crosses: 2
  use_edges: wick_extreme
  main_center_score: range_times_duration

macd:
  fast: 12
  slow: 26
  signal: 9

center_level_diagnostic:
  enabled: true
  zero_axis_source: [DIF, DEA]
  use_histogram: false
  hard_filter: false
  above_current_cross_count: 2

third_buy:
  pullback_low_must_hold_upper: true
  allow_wick_break_and_reclaim: false

entry_path:
  primary_video_only: true
  require_A_b_greater_than_a_before_bA: true
  allow_A_b_less_than_a_direct_entry: false
  require_bA_range_smaller_than_A: true

entry_confirmation:
  bullish_k_body_ratio_of_ba_range: 0.25
  bullish_k_requires_close_gt_open: true

execution:
  entry_mode: next_bar_open
  fee_rate: 0.0005
  slippage_bps: 0
  ambiguous_bar_policy: stop_first

position:
  side: long_only
  max_positions_per_symbol: 1
  allow_pyramiding: false
```

---

## 22. 輸出結果

### 22.1 Trade log 欄位

```text
trade_id
strategy_id
symbol
entry_time
entry_price
stop_loss
take_profit
exit_time
exit_price
exit_reason
pnl
pnl_pct
rr_planned
holding_bars

center_1h_start
center_1h_end
center_1h_upper
center_1h_lower
center_1h_score
center_1h_macd_diag

center_A_15m_start
center_A_15m_end
center_A_upper
center_A_lower
center_A_range
center_A_score
center_A_macd_diag
a_length
b_length

center_bA_15m_start
center_bA_15m_end
center_bA_upper
center_bA_lower
center_bA_range
center_bA_score
center_bA_macd_diag
b_a_length
b_b_length

iso_low_1_time
iso_low_1_price
iso_low_2_time
iso_low_2_price

bullish_k_time
bullish_k_open
bullish_k_high
bullish_k_low
bullish_k_close
bullish_k_body
bullish_k_required_body

reason_code
fallback_used
fallback_reason
```

### 22.2 Signal log 欄位

即使沒有開單，也必須記錄候選與拒絕原因。

```text
time
symbol
state
reason_code
message
related_center_id
related_swing_id
macd_diag
fallback_used
```

### 22.3 視覺標註

Codex / 工程實作應提供可選 chart annotation：

```text
1. 1H 主中樞上下沿。
2. 1H 向上離開點。
3. 1H 結構突破點。
4. 1H 回抽低點。
5. 15m 中樞 A。
6. a / b 段。
7. b-A。
8. b-a / b-b 段。
9. 兩次孤立低點。
10. 多頭趨勢 K。
11. Entry / SL / TP。
12. MACD 診斷標籤，但不得顯示為硬條件。
```

---

## 23. 建議專案結構

```text
z3b_prime/
  README.md
  config.example.yaml
  pyproject.toml
  data/
    loader.py
    resample.py
  indicators/
    macd.py
  market_structure/
    swings.py
    centers.py
    legs.py
  diagnostics/
    macd_zero_axis.py
  strategy/
    z3b_prime.py
    state_machine.py
    reason_codes.py
  backtest/
    engine.py
    broker.py
    metrics.py
  visualization/
    annotate.py
    plot.py
  tests/
    test_swings.py
    test_centers.py
    test_macd_diagnostic.py
    test_1h_third_buy.py
    test_ab_compare.py
    test_ba_compare.py
    test_isolated_lows.py
    test_bullish_trend_k.py
    test_no_lookahead.py
```

---

## 24. 核心資料類別

```python
from dataclasses import dataclass
from typing import Literal
import pandas as pd

@dataclass
class SwingPoint:
    symbol: str
    timeframe: str
    time: pd.Timestamp
    confirmed_time: pd.Timestamp
    kind: Literal["high", "low"]
    price: float
    bar_index: int

@dataclass
class Center:
    id: str
    symbol: str
    timeframe: str
    start_time: pd.Timestamp
    end_time: pd.Timestamp
    upper: float
    lower: float
    mid: float
    range: float
    duration_bars: int
    score: float
    macd_level_diag: Literal[
        "BELOW_CURRENT",
        "CURRENT_LIKE",
        "ABOVE_CURRENT_LIKE",
        "UNKNOWN"
    ]

@dataclass
class Leg:
    name: str
    start_time: pd.Timestamp
    end_time: pd.Timestamp
    start_price: float
    end_price: float
    direction: Literal["down", "up"]
    length: float

@dataclass
class TradeSignal:
    strategy_id: str
    symbol: str
    signal_time: pd.Timestamp
    entry_time: pd.Timestamp
    entry_price: float
    stop_loss: float
    take_profit: float
    rr: float
    reason_code: str
    metadata: dict
```

---

## 25. Pseudocode

```python
def run_strategy(symbol, bars_1h, bars_15m, config):
    bars_1h = add_macd(bars_1h, config.macd)
    bars_15m = add_macd(bars_15m, config.macd)

    swings_1h = detect_swings(bars_1h, config.swing)
    swings_15m = detect_swings(bars_15m, config.swing)

    centers_1h = detect_price_centers(bars_1h, swings_1h, config.center_detection)
    centers_15m = detect_price_centers(bars_15m, swings_15m, config.center_detection)

    # MACD diagnostics only; do not hard-filter by default.
    attach_macd_zero_axis_diagnostics(centers_1h, bars_1h, config)
    attach_macd_zero_axis_diagnostics(centers_15m, bars_15m, config)

    state = Z3BPrimeStateMachine(config)

    for t in bars_15m.closed_times:
        state.update_time(t)
        ctx_1h = latest_closed_1h_context(t, bars_1h)
        ctx_15m = latest_closed_15m_context(t, bars_15m)

        if state.name == "WAIT_1H_CENTER":
            center_1h = select_main_price_center(centers_1h, ctx_1h)
            if not center_1h:
                log("NO_1H_CENTER")
                continue
            state.center_1h = center_1h
            state.name = "WAIT_1H_UPWARD_LEAVE"

        if state.name == "WAIT_1H_UPWARD_LEAVE":
            if ctx_1h.close > state.center_1h.upper:
                state.name = "WAIT_1H_STRUCTURE_BREAK"

        if state.name == "WAIT_1H_STRUCTURE_BREAK":
            if broke_previous_1h_swing_high(ctx_1h, swings_1h):
                state.target_high_1h = find_target_high_1h(ctx_1h, swings_1h)
                state.name = "WAIT_1H_PULLBACK_3BUY"

        if state.name == "WAIT_1H_PULLBACK_3BUY":
            if pullback_low_broke_center_upper(ctx_1h, state.center_1h):
                log("PULLBACK_BROKE_CENTER_UPPER")
                state.reset()
                continue
            if potential_3buy_confirmed(ctx_1h, state.center_1h):
                state.pullback_segment = map_1h_pullback_to_15m(ctx_1h, bars_15m)
                state.name = "WAIT_15M_CENTER_A"

        if state.name == "WAIT_15M_CENTER_A":
            center_A = select_center_A_price_based(centers_15m, state.pullback_segment)
            if not center_A:
                log("NO_15M_CENTER_A")
                continue
            state.center_A = center_A
            state.name = "WAIT_15M_AB_COMPARE"

        if state.name == "WAIT_15M_AB_COMPARE":
            a_leg, b_leg = build_ab_legs(state.center_A, swings_15m)
            state.a_leg = a_leg
            state.b_leg = b_leg

            if b_leg.length > a_leg.length:
                log("B_GREATER_THAN_A_WAIT_BA")
                state.name = "WAIT_15M_BA_CENTER"
            elif b_leg.length < a_leg.length:
                log("A_B_LESS_THAN_A_CONCEPT_ONLY_NO_ENTRY")
                state.reset_to_wait_15m_center_A()
                continue
            else:
                log("B_EQUAL_A_NOT_CLEAR")
                continue

        if state.name == "WAIT_15M_BA_CENTER":
            bA = select_bA_price_center(centers_15m, state.b_leg)
            if not bA:
                log("NO_BA_CENTER")
                continue
            if bA.range >= state.center_A.range:
                log("NO_SMALLER_BA_CENTER")
                continue
            state.bA = bA
            state.name = "WAIT_15M_BA_BB_COMPARE"

        if state.name == "WAIT_15M_BA_BB_COMPARE":
            ba_leg, bb_leg = build_ba_bb_legs(state.bA, swings_15m)
            state.ba_leg = ba_leg
            state.bb_leg = bb_leg
            if bb_leg.length < ba_leg.length:
                state.name = "WAIT_15M_ISOLATED_LOWS"
            else:
                log("BB_NOT_LESS_THAN_BA")
                continue

        if state.name == "WAIT_15M_ISOLATED_LOWS":
            iso1, iso2 = find_isolated_lows(state.bA, swings_15m)
            if not iso2:
                continue
            if iso2.price < iso1.price:
                log("SECOND_LOW_BROKE_FIRST_LOW")
                state.reset_to_wait_15m_center_A()
                continue
            state.iso1 = iso1
            state.iso2 = iso2
            state.name = "WAIT_15M_BULLISH_TREND_K"

        if state.name == "WAIT_15M_BULLISH_TREND_K":
            k = latest_closed_15m_bar(ctx_15m)
            if is_bullish_trend_k(k, state.bA, config):
                signal = build_trade_signal(
                    k=k,
                    entry_price=next_bar_open(bars_15m, k),
                    stop_loss=k.low,
                    take_profit=state.target_high_1h,
                    metadata=state.metadata(),
                )
                if signal_is_valid(signal):
                    emit(signal)
                    state.name = "IN_POSITION"
                else:
                    log(signal.reason_code)
```

---

## 26. 單元測試要求

Codex 完成後至少建立以下測試：

```text
1. test_swing_confirmation_delay
2. test_no_lookahead_swing_not_available_before_confirmed_time
3. test_center_edges_use_wick_extremes
4. test_center_candidate_requires_alternating_swings
5. test_macd_zero_axis_diagnostic_does_not_block_trade_by_default
6. test_1h_upward_leave_requires_close_above_center_upper
7. test_1h_pullback_low_must_not_break_center_upper
8. test_ab_compare_b_greater_a_goes_to_bA_path
9. test_ab_compare_b_less_a_does_not_open_trade_v1_1
10. test_bA_must_be_smaller_than_A
11. test_bb_less_than_ba_allows_next_confirmation_state
12. test_second_low_must_not_break_first_low
13. test_bullish_trend_k_body_threshold
14. test_early_bullish_k_before_structure_complete_rejected
15. test_stop_loss_is_bullish_k_low
16. test_take_profit_is_1h_target_high
17. test_entry_uses_next_15m_open
18. test_ambiguous_bar_stop_first
19. test_reason_codes_are_logged_for_rejections
20. test_trade_log_contains_all_structure_fields
```

---

## 27. 驗收標準

模型完成後至少要能做到：

```text
1. 讀取任意標的 1H / 15m OHLCV。
2. 自動計算 MACD，但 MACD 預設只做診斷。
3. 自動識別 confirmed swing points。
4. 自動識別 price-based 中樞。
5. 自動找 1H 主中樞。
6. 自動判斷 1H 向上離開。
7. 自動判斷 1H 結構突破。
8. 自動判斷 1H 回抽不跌破中樞上沿。
9. 自動找 15m 中樞 A。
10. 自動比較 A 的 a / b。
11. 僅在 A 的 b > a 時進入 b-A 路徑。
12. 自動找 b-A，並確認 bA.range < A.range。
13. 自動比較 b-a / b-b。
14. 自動判斷兩次孤立低點不破。
15. 自動判斷多頭趨勢 K。
16. 自動產生 entry / SL / TP。
17. 自動回測 SL / TP。
18. 自動輸出 trade log / signal log。
19. 能產出標註圖，方便檢查每筆交易是否符合第一部影片語義。
20. 所有單元測試通過。
```

---

## 28. 給 Codex 的實作指令

請依照本文件實作 `Z3B-Prime` 量化模型。

核心要求：

```text
1. 第一部影片為主，第二部只作觀念輔助。
2. 不要自行增加新的入場路徑。
3. 不要把 MACD 零軸診斷變成硬性開單 / 拒單條件。
4. 不要把 b < a 直接做成開單條件。
5. 不要改停損與停利。
6. 必須使用狀態機。
7. 必須防止 lookahead bias。
8. 必須記錄 reason code。
9. 必須提供視覺標註輸出。
```

請輸出：

```text
1. Python package: z3b_prime
2. config.example.yaml
3. strategy implementation
4. backtest CLI
5. trade log CSV
6. signal log CSV
7. annotated chart examples
8. unit tests
9. README with usage instructions
```

優先順序：

```text
1. 策略語義正確。
2. 第一部影片優先。
3. 防止偷看未來資料。
4. 所有不開單原因可追蹤。
5. 圖上能檢查中樞、a/b、b-A、低點、K 線、Entry/SL/TP。
6. 最後才做速度優化。
```

---

## 29. README 命令範例

```bash
python -m z3b_prime.backtest \
  --config config.example.yaml \
  --data-dir ./data \
  --symbols BTCUSDT ETHUSDT \
  --start 2023-01-01 \
  --end 2026-01-01 \
  --out ./reports/z3b_prime
```

期望輸出：

```text
reports/z3b_prime/trades.csv
reports/z3b_prime/signals.csv
reports/z3b_prime/metrics.json
reports/z3b_prime/charts/*.png
```

---

## 30. v1.1 重要備註

這份規格的目標不是提高勝率，也不是最佳化參數，而是先把第一部影片的策略邏輯變成可重現、可檢查、可回測的模型。

第二部影片的價值是幫助理解中樞與 a/b 的語義，但不能讓模型脫離第一部影片的開單流程。

v1.1 的設計原則：

```text
寧可少開單，也不要亂把觀念影片延伸成額外交易邏輯。
```
