# Z3B-Prime 中樞三買量化模型規格 v1.4 — 台股整股 / 零股執行版

**中文名**：Z3B-Prime 中樞三買模型  
**英文名**：Z3B-Prime Center Third-Buy Model  
**策略代號**：`Z3B-Prime`  
**模組 / repo 建議名稱**：`z3b_prime_tw_equity`  
**方向**：只做台股實股現貨多單（TWSE / TPEx cash equity long only）  
**主策略來源**：第一部影片  
**觀念輔助來源**：第二部影片  

---

## 0. v1.4 重要修正與台股執行版變更

使用者已確認兩個優先級：

```text
1. 前後兩部影片是不同內容；第一部是策略實作主體，第二部主要是中樞觀念教學。
2. 第一部影片中的停損不是放在後面的多頭趨勢 K，而是放在前面的金 K。
```

因此本版保留前版停損修正，並加入實股執行層。修正如下：

```text
1. 第一部影片 = 開單流程、停損、停利、15m 確認邏輯的最高優先來源。
2. 第二部影片 = 用來理解「中樞是多空平衡區」與「MACD DIF/DEA 零軸可輔助判斷中樞級別」。
3. 第二部不能反過來新增第一部沒有使用的開單路徑。
4. MACD 零軸判斷在 v1.4 預設為 diagnostic / advisory，不是硬性開單或拒單條件。
5. 原先文件中的 Z3B-MACD 名稱容易讓人誤解 MACD 是策略核心，因此改名為 Z3B-Prime。
6. 新增並強制定義 golden_k：兩次孤立低點不破後、第二個低點成立的最後一根 K。
7. 停損必須使用 golden_k.low；多頭趨勢 K 只負責確認入場，不負責決定停損。
```

v1.4 保留 v1.2 / v1.4 修正，並新增台股專用執行要求：

```text
1. 本模型只做實股現貨多單，不做合約、不做融資融券、不做空、不加槓桿。
2. 策略訊號層與實際下單執行層必須分離。
3. 回測與實盤都不得假設理想成交；必須考慮滑價、手續費、交易稅、買賣價差、跳空、交易時段、漲跌停、成交量不足、部分成交與訂單失敗。
4. 實股預設用 marketable limit order 進場，避免純市價單滑價無上限；若未在可接受價格內成交，取消交易，不追價。
5. 停損價位仍然是 golden_k.low；實際成交價可能因滑價、跳空或跌停而比 stop_loss 更差。
6. 停利價位仍然是 1H 趨勢週期前高；實盤建議用限價賣單或 OCO / bracket order 管理。
7. 若同時存在策略訊號與執行風險衝突，執行風控優先，寧可錯過，不可用理想價硬成交。
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

停損放前面的金 K 底部極值點；金 K 是兩次孤立低點不破後，第二個低點成立的最後一根 K。
多頭趨勢 K 只用來確認可以入場，不用來放停損。
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
11. 停損 = 前面的金 K 底部極值點。
12. 多頭趨勢 K = 後面漲上去的確認 K，只用來確認入場。
13. 停利 = 趨勢週期 1H 的前高。
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
3. 不能改掉第一部的停損、停利；停損錨定 golden_k.low。
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
package_name: z3b_prime_tw_equity
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
2. 不做合約。
3. 不做融資融券。
4. 不使用槓桿。
5. 不抄底。
6. 不做 1 買猜底。
7. 不使用均線交叉作為進出場。
8. 不使用 RSI / KD / 布林通道作為必要條件。
9. 不使用 MACD 金叉死叉作為進出場。
10. 不把 MACD 背離當成核心開單條件。
11. 不把停利改成固定盈虧比。
12. 不把停損改成 ATR 或固定百分比。
13. 不因為主中樞 A 的 b < a 就直接開多。
14. 不因為價格出現大陽線就直接開多；前面結構必須完整。
15. 不把台股整股與零股用同一套成交規則混在一起。
16. 不把零股當沖 / 同日沖銷視為預設可用。
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
| `entry_tf` | 15m | 交易週期：找回調內中樞 A、b-A、兩次低點不破、金 K 停損、多頭趨勢 K 入場確認 |

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

### 6.1 實股資料額外要求

實股資料不能只當成 24/7 連續市場處理。Codex 必須加入交易所與標的 metadata。

每個 symbol 至少需要：

```text
symbol
exchange
currency
regular_session_open
regular_session_close
timezone
lot_size
min_order_quantity
tick_size
supports_fractional_shares
has_price_limit
price_limit_rule_id
fee_profile_id
tax_profile_id
```

資料處理要求：

```text
1. 只在 regular trading session 內產生新訊號與下單，除非 config 明確允許盤前 / 盤後。
2. 15m / 1H K 線必須依交易所 session 切分，不得跨午休、收盤、隔夜硬接成連續 K。
3. 若市場有午休，午休前後不可合併成同一根 K。
4. 若訊號 K 收在當日最後一根 15m，entry_time 必須順延到下一個有效 regular session 的第一根 15m open。
5. 若遇到假日、休市、停牌、無成交量，不能開單。
6. 若歷史資料有除權息 / split adjustment，signal、SL、TP 必須使用同一價格尺度；不可用 adjusted signal 搭配 unadjusted execution。
7. 實盤交易必須使用 raw live price；若用 adjusted historical data 回測，需記錄 adjustment_mode。
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

### 8.1 v1.4 的定位

第二部影片提到 MACD DIF / DEA 與 0 軸可輔助判斷中樞級別。使用者已確認第二部是教觀念，因此 v1.4 將 MACD 設為：

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
center_level_diag 不得在 v1.4 預設模式下直接阻擋交易。
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
3. v1.4 不允許影線跌破後收回。
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

因此 v1.4 規則為：

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
b < a 只作為市場狀態註記，不作為 v1.4 開單條件。
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

## 15. 兩次孤立低點不破與金 K

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

v1.4 嚴格使用影線 low：

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

### 15.3 金 K / golden_k 定義

使用者修正：第一部影片的停損不是放在後面漲上去的多頭趨勢 K，而是放在前面的金 K。

`golden_k` 的工程定義：

```text
golden_k = iso_low_2 成立時的最後一根 15m K 線
```

語義：

```text
1. b-A 之後已經出現第一次孤立低點 iso_low_1。
2. 後面價格第二次回到低位，形成 iso_low_2。
3. iso_low_2 沒有跌破 iso_low_1。
4. 這個「第二次孤立低點不破」成立時的最後一根 K，就是 golden_k。
5. golden_k 在時間上必須早於後面的 bullish_trend_k。
```

若 `iso_low_2` 是單根 confirmed swing low：

```text
golden_k = iso_low_2 對應的 bar
```

若 `iso_low_2` 是多根 K 組成的低位停住區：

```text
golden_k = 該低位停住區內，確認「沒有再破底」的最後一根 K
```

金 K 的低點：

```text
golden_k_low = golden_k.low
```

停損必須使用：

```text
stop_loss = golden_k_low
```

不可使用：

```text
forbidden_stop_source = bullish_trend_k.low
```

原因：

```text
多頭趨勢 K 是後面拉上去的入場確認 K。
金 K 是前面兩次孤立低點不破後，用來放風險邊界的 K。
兩者角色不同。
```

---

## 16. 多頭趨勢 K

### 16.1 定義

第一部影片入場前要看到 15m 多頭趨勢 K / 光頭光腳大陽線。使用者指定可用 b-A 高低落差的 1/4 量化。

```text
bullish_trend_k =
    time > golden_k.close_time
AND close > open
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
7. 由第二個孤立低點確認 golden_k，並記錄 golden_k.low 作為停損。
8. 然後才等多頭趨勢 K。
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
11. golden_k 已確認，且 golden_k.low 作為 stop_loss。
12. golden_k 之後出現 15m 多頭趨勢 K。
```

注意：

```text
A 的 b_length < a_length 在 v1.4 不是開多條件。
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

注意：

```text
entry_trigger_bar = bullish_trend_k
risk_anchor_bar = golden_k
```

兩者不能混用。

### 17.3 停損

照第一部影片與使用者修正：

```text
stop_loss = golden_k.low
```

其中：

```text
golden_k = 兩次孤立低點不破後，第二個低點成立的最後一根 15m K
```

多頭趨勢 K 的 low 不用作停損。

```text
forbidden_stop_source = bullish_trend_k.low
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


## 18. 實股執行層（Spot Equity Execution Layer）

本節是 v1.4 的核心新增內容。策略訊號仍完全來自 Z3B-Prime；本節只處理「訊號成立後，實股如何買賣、如何回測成交、如何避免理想成交假設」。

### 18.1 執行層總原則

```text
signal_layer  = 判斷是否符合第一部影片的 Z3B-Prime 開多條件。
execution_layer = 判斷能否在實股市場合理成交、成交價格、數量、費用、滑價、風控與出場。
```

硬規則：

```text
1. 實股版本只允許 long cash equity。
2. 不允許 futures、perpetual swap、CFD、option、warrant、margin long、short selling。
3. 不允許因為訊號漂亮就忽略成交限制。
4. 不允許回測用理想 entry / stop / target 價格直接成交。
5. 所有成交必須經過 broker / execution simulator。
6. 每次拒單、未成交、部分成交、跳空、滑價、費用都要記錄 reason_code 與欄位。
```

### 18.2 實股預設交易模式

```yaml
instrument_type: spot_equity
position_side: long_only
leverage: 1.0
allow_margin: false
allow_short: false
allow_fractional_shares: false
allow_pyramiding: false
max_positions_per_symbol: 1
```

### 18.3 交易時段規則

```text
1. 只在 regular_session 下單、成交與觸發新進場。
2. 不使用盤前 / 盤後價格判斷入場，除非 config.allow_extended_hours = true。
3. 持倉可隔夜，但必須接受隔夜跳空風險。
4. 若 bullish_trend_k 收盤後已無下一根 regular 15m K，entry_time = 下一交易日 regular session 第一根 15m open。
5. 若下一交易日開盤跳空太高導致 entry_fill >= take_profit，拒絕開單。
6. 若下一交易日開盤跳空太低導致 entry_fill <= stop_loss，拒絕開單。
```

reason codes：

```text
MARKET_CLOSED_NO_ENTRY
NEXT_SESSION_ENTRY_DELAYED
ENTRY_GAP_ABOVE_TP_REJECTED
ENTRY_GAP_BELOW_STOP_REJECTED
SYMBOL_HALTED_OR_NO_VOLUME
```

### 18.4 預設進場單型：Marketable Limit Buy

不要讓 Codex 寫成「訊號成立後直接用理想價格買入」。實股第一版預設使用 marketable limit order，而不是無上限純市價單。

訊號產生：

```text
signal_time = bullish_trend_k.close_time
planned_entry_time = next valid 15m regular-session bar open
reference_entry_price = next_bar.open
```

買入限價：

```text
entry_limit_price = reference_entry_price * (1 + max_entry_slippage_bps / 10000)
```

回測成交模型：

```text
if next_bar.open > entry_limit_price:
    no fill
    reason_code = ENTRY_LIMIT_NOT_FILLED
else:
    entry_fill = min(
        next_bar.open * (1 + entry_slippage_bps / 10000),
        entry_limit_price
    )
```

實盤語義：

```text
1. 在 planned_entry_time 送出 buy limit，價格為 entry_limit_price。
2. 若未成交或只部分成交，依 partial fill policy 處理。
3. 預設不追價；若 entry order 未在 entry_order_timeout_bars 內成交，取消本次交易。
```

預設：

```yaml
entry_order_type: marketable_limit
entry_order_timeout_bars: 1
entry_slippage_bps: 5
max_entry_slippage_bps: 20
chase_if_not_filled: false
```

### 18.5 純市價單限制

只有在 config 明確允許時才能使用 market order。

```yaml
allow_pure_market_order: false
```

若啟用：

```text
entry_fill = next_bar.open * (1 + entry_slippage_bps / 10000)
```

但仍要經過：

```text
1. 最大可接受滑價檢查。
2. entry_fill < take_profit。
3. entry_fill > stop_loss。
4. liquidity filter。
5. position sizing。
```

### 18.6 持倉數量與資金風控

實股不能只說「開一個多單」。必須計算買幾股 / 幾張。

風險預算：

```text
risk_budget_cash = account_equity * risk_per_trade_pct
```

預估最壞停損成交：

```text
stop_exit_assumed = stop_loss * (1 - stop_slippage_bps / 10000)
```

如果使用跳空風險緩衝：

```text
stop_exit_worst_case = stop_loss * (1 - (stop_slippage_bps + gap_risk_buffer_bps) / 10000)
```

單股風險：

```text
risk_per_share = entry_fill - stop_exit_worst_case
```

股數：

```text
raw_qty_by_risk = floor(risk_budget_cash / risk_per_share)
raw_qty_by_cash = floor(available_cash / (entry_fill * (1 + buy_fee_bps / 10000)))
raw_qty = min(raw_qty_by_risk, raw_qty_by_cash)
```

依市場單位取整：

```text
qty = floor_to_lot_size(raw_qty, lot_size)
```

拒單：

```text
if risk_per_share <= 0: INVALID_RISK_PER_SHARE
if qty < min_order_quantity: ORDER_QTY_BELOW_MINIMUM
if estimated_order_value < min_order_value: ORDER_VALUE_BELOW_MINIMUM
if estimated_order_value > available_cash: INSUFFICIENT_CASH
```

預設：

```yaml
position_sizing:
  method: risk_percent
  risk_per_trade_pct: 0.005
  max_cash_per_trade_pct: 0.20
  min_order_value: 0
  round_to_lot_size: true
```

### 18.7 流動性與成交量過濾

為避免回測買到實盤根本難成交的小股票，必須加入 liquidity filter。

```yaml
liquidity_filter:
  enabled: true
  min_avg_volume_20: 100000
  min_avg_turnover_20: 0
  max_order_participation_pct: 0.01
  require_nonzero_volume_on_entry_bar: true
```

規則：

```text
1. 若 entry bar volume = 0，拒單。
2. 若 qty > entry_bar.volume * max_order_participation_pct，則依 config 決定 reduce_qty 或 reject。
3. 預設 reduce_qty = true；若 reduce 後低於 min_order_quantity，拒單。
4. 若有 bid/ask/spread 資料，可加入 max_spread_bps；沒有 L1/L2 資料時不得假裝知道 spread。
```

reason codes：

```text
ENTRY_BAR_ZERO_VOLUME
LIQUIDITY_FILTER_FAILED
ORDER_EXCEEDS_VOLUME_PARTICIPATION
ORDER_REDUCED_BY_VOLUME_CAP
```

### 18.8 手續費、交易稅與成本

所有績效必須扣成本。

```yaml
costs:
  buy_fee_bps: 0
  sell_fee_bps: 0
  sell_tax_bps: 0
  min_fee_per_order: 0
  currency: account_currency
```

買入成本：

```text
buy_fee = max(entry_fill * qty * buy_fee_bps / 10000, min_fee_per_order)
```

賣出成本：

```text
sell_fee = max(exit_fill * qty * sell_fee_bps / 10000, min_fee_per_order)
sell_tax = exit_fill * qty * sell_tax_bps / 10000
```

淨損益：

```text
gross_pnl = (exit_fill - entry_fill) * qty
net_pnl = gross_pnl - buy_fee - sell_fee - sell_tax
```

注意：

```text
1. 不要在策略程式硬寫某市場稅率；用 config / fee profile。
2. 若回測多市場，費用與交易稅必須按 exchange / symbol profile 套用。
3. 若有最低手續費，必須納入，否則小金額交易績效會被高估。
```

### 18.9 停損執行：Golden K Low 是觸發價，不保證成交價

策略停損價位仍然是：

```text
stop_loss_level = golden_k.low
```

但實際出場價要分情況：

#### 18.9.1 盤中正常觸發

若持倉後某根 15m K：

```text
low <= stop_loss_level
```

回測停損成交：

```text
stop_exit_fill = stop_loss_level * (1 - stop_slippage_bps / 10000)
```

#### 18.9.2 隔夜 / 跨 session 跳空跌破停損

若下一個 regular session 開盤：

```text
open < stop_loss_level
```

不得用 stop_loss_level 當成交價，必須用：

```text
gap_stop_exit_fill = open * (1 - stop_slippage_bps / 10000)
```

reason code：

```text
STOP_GAP_THROUGH_FILLED_AT_OPEN
```

#### 18.9.3 跌停 / 停牌 / 無法成交

若市場有漲跌停或標的停牌，且 stop 被觸發但不能成交：

```text
exit_status = BLOCKED
reason_code = STOP_TRIGGERED_BUT_NOT_EXECUTABLE
```

處理方式：

```text
1. 持倉保持 open。
2. 下一個可成交 regular session 繼續嘗試出場。
3. 風險報告必須標記 blocked_exit = true。
4. 不得假裝已在 stop_loss_level 成交。
```

### 18.10 停損單型預設

回測預設：

```yaml
stop_order_type: simulated_stop_market
```

語義：

```text
1. stop_loss_level 是觸發價。
2. 觸發後以 market sell 語義出場。
3. 成交價可能比 stop_loss_level 更差。
```

不建議第一版使用 stop-limit 作為預設，因為 stop-limit 可以控制價格，但可能不成交。若之後要支援：

```yaml
stop_order_type: stop_limit
stop_limit_offset_bps: 20
```

但必須加：

```text
1. STOP_LIMIT_NOT_FILLED
2. 持倉延續風險
3. 後續補救規則
```

### 18.11 停利執行：1H 前高限價賣出

策略停利價位：

```text
take_profit_level = target_high_1h
```

回測：

```text
if high >= take_profit_level:
    take_profit_fill = take_profit_level
```

實盤建議：

```text
1. entry 成交後，掛 sell limit at take_profit_level。
2. 若 broker 支援 OCO / bracket order，entry 成交後同時建立 stop-loss sell 與 take-profit sell。
3. 若不支援 OCO，策略 engine 必須監控；任一出場成交後立即取消另一個出場單。
```

注意：

```text
1. 限價停利可能部分成交。
2. 若 high 只刺到 target 一點點，OHLC 回測仍會假設成交；進階版可加入 target_fill_probability 或 volume check。
3. 第一版保持簡化：高點觸及 target 即視為限價成交，但必須扣 sell fee / tax。
```

### 18.12 OCO / Bracket Order 規則

若 broker 支援：

```text
after entry_fill:
    place OCO:
        stop_loss_sell: stop_loss_level, qty
        take_profit_sell_limit: take_profit_level, qty
```

若 broker 不支援：

```text
engine monitors bars/ticks:
    if stop triggered first:
        market sell / simulated stop-market
        cancel take-profit order
    elif take_profit filled first:
        sell limit filled
        cancel stop order
```

### 18.13 同一根 K 同時碰停損與停利

OHLC 無法知道同一根 15m 內先碰哪邊。保守處理：

```text
if low <= stop_loss_level and high >= take_profit_level:
    exit_reason = AMBIGUOUS_BAR_STOP_FIRST
    exit_fill = stop_loss_level * (1 - stop_slippage_bps / 10000)
```

### 18.14 部分成交處理

預設回測可採 full fill，但不能讓實盤程式忽略 partial fill。

```yaml
partial_fill_policy:
  backtest_assume_full_fill_if_volume_ok: true
  live_allow_partial_fill: true
  min_fill_ratio: 1.0
  cancel_if_partial_below_min_ratio: true
```

實盤：

```text
1. 若 entry partial fill < min_fill_ratio，取消剩餘數量，並視設定決定是否保留小倉位。
2. 若保留小倉位，SL / TP 數量必須等於實際成交數量。
3. 不可對未成交數量掛出場單。
```

### 18.15 企業行為與停牌

```text
1. 持倉期間若發生 split / reverse split，qty、entry、SL、TP 必須同步調整。
2. 現金股息不應直接改變技術停損價，但績效報告應可記錄 dividend_cash_flow。
3. 停牌期間不得假設可出場。
4. 復牌跳空要按 gap rule 處理。
```

### 18.16 實股執行 reason codes

```text
MARKET_CLOSED_NO_ENTRY
NEXT_SESSION_ENTRY_DELAYED
ENTRY_LIMIT_NOT_FILLED
ENTRY_ORDER_TIMEOUT_CANCELLED
ENTRY_GAP_ABOVE_TP_REJECTED
ENTRY_GAP_BELOW_STOP_REJECTED
SYMBOL_HALTED_OR_NO_VOLUME
TRADING_SUSPENDED
PRICE_LIMIT_BLOCKED_ENTRY
PRICE_LIMIT_BLOCKED_EXIT
INVALID_RISK_PER_SHARE
ORDER_QTY_BELOW_MINIMUM
ORDER_VALUE_BELOW_MINIMUM
INSUFFICIENT_CASH
ENTRY_BAR_ZERO_VOLUME
LIQUIDITY_FILTER_FAILED
ORDER_EXCEEDS_VOLUME_PARTICIPATION
ORDER_REDUCED_BY_VOLUME_CAP
PARTIAL_FILL_BELOW_MIN_RATIO
STOP_GAP_THROUGH_FILLED_AT_OPEN
STOP_TRIGGERED_BUT_NOT_EXECUTABLE
STOP_LIMIT_NOT_FILLED
TAKE_PROFIT_LIMIT_FILLED
TAKE_PROFIT_PARTIAL_FILL
CORPORATE_ACTION_ADJUSTED_POSITION
```

---


## 18T. 台股專用執行層（TWSE / TPEx Cash Equity）

本節覆蓋 v1.4 台股實戰下單與回測成交規則。Codex 實作時必須先通過本節，再處理任何 live order。

### 18T.1 台股市場範圍

預設市場：

```yaml
market_scope:
  country: Taiwan
  timezone: Asia/Taipei
  currency: TWD
  exchanges_allowed: [TWSE, TPEX]
  product_allowed_default: common_stock
  allow_etf: optional_by_config
  allow_warrant: false
  allow_futures: false
  allow_options: false
  allow_margin: false
  allow_short: false
  leverage: 1.0
```

預設只跑：

```text
1. 上市普通股 TWSE common stocks。
2. 上櫃普通股 TPEx common stocks。
3. ETF 可選，但必須使用 ETF tax / tick / lot profile，不可混用普通股稅率。
```

預設排除：

```text
1. 權證。
2. 期貨。
3. 選擇權。
4. 融資融券。
5. 當沖放空。
6. 處置股 / 全額交割股 / 變更交易方法股票，除非 config 明確允許且資料源可標記。
7. 新上市前五日無漲跌幅限制股票，除非 config.allow_no_price_limit_symbols = true。
```

### 18T.2 台股交易時段與 K 線切分

台股 regular session：

```text
09:00 - 13:30 Asia/Taipei
```

regular trading orders 可從 08:30 輸入，但策略訊號與回測進場只用 regular session 成交資料。

15m K 線切分：

```text
09:00-09:15
09:15-09:30
...
13:15-13:30
```

1H K 線切分：

```text
09:00-10:00
10:00-11:00
11:00-12:00
12:00-13:00
13:00-13:30  # short_session_bar = true
```

實作要求：

```text
1. 不得把台股 K 線接成 24/7 連續市場。
2. 不得把隔夜缺口補成平滑走勢。
3. 13:00-13:30 的 1H short bar 必須標記 short_session_bar=true。
4. 若 bullish_trend_k 出現在 13:15-13:30，entry_time = 下一個交易日 09:00，而不是當天盤後。
5. 預設不使用 after-hours fixed-price trading 與 after-hours odd-lot trading 進出場。
```

### 18T.3 整股與零股版本總表

| 項目 | 整股版 `tw_round_lot` | 零股版 `tw_odd_lot` |
|---|---:|---:|
| 單位 | 1 張 = 1,000 股 | 1 - 999 股 |
| qty rounding | 取 1,000 股整數倍 | 取 1 股整數，預設單筆上限 999 股 |
| 交易時段 | regular session 09:00-13:30 | intraday odd-lot 09:00-13:30 |
| 盤中撮合 | regular continuous / call auction rules | first match 09:10, then call auction every 5 sec |
| 下單型態 | 預設 marketable limit | limit only / marketable limit approximation |
| 當沖 / 同日沖銷 | 可用但需帳戶與標的符合資格 | 預設不可作 day trading offset |
| 停損執行 | stop trigger 後送賣單；需考慮跌停 / 跳空 | 同日停損不可預設可執行；預設 next-day executable only |
| 交易稅 | 普通股賣出 0.3%；符合現股當沖條件之賣出 0.15% 至 2027-12-31 | 普通股賣出預設 0.3%；不套用現股當沖 0.15% |
| 最適用途 | 策略正式回測與實盤優先版本 | 小資金測試 / 分批建倉；需保守處理同日出場 |

### 18T.4 整股版：`tw_round_lot`

整股版是 Z3B-Prime 台股主版本。

```yaml
execution_profile: tw_round_lot
lot_size_shares: 1000
min_order_quantity_shares: 1000
quantity_unit_name: lot
quantity_unit_shares: 1000
rounding_rule: floor_to_1000_shares
allow_odd_lot_remainder: false
```

股數計算：

```python
raw_qty = min(raw_qty_by_risk, raw_qty_by_cash)
qty_shares = floor(raw_qty / 1000) * 1000
qty_lots = qty_shares / 1000
```

拒單條件：

```text
if qty_shares < 1000:
    reject ROUND_LOT_QTY_BELOW_ONE_LOT
```

整股版不拆成零股補尾數：

```text
若 raw_qty = 2,350 股，整股版只買 2,000 股，不買剩餘 350 股。
```

### 18T.5 零股版：`tw_odd_lot`

零股版是獨立執行模式，不是整股版的尾數補單。它適合資金較小或想降低單筆資金門檻，但回測與實盤必須更保守。

```yaml
execution_profile: tw_odd_lot
lot_size_shares: 1
min_order_quantity_shares: 1
max_order_quantity_shares: 999
quantity_unit_name: share
rounding_rule: floor_to_1_share
allow_round_lot_conversion: false
```

股數計算：

```python
raw_qty = min(raw_qty_by_risk, raw_qty_by_cash)
qty_shares = floor(raw_qty)
qty_shares = min(qty_shares, 999)
```

拒單條件：

```text
if qty_shares < 1:
    reject ODD_LOT_QTY_BELOW_ONE_SHARE
```

零股版不可自動變成整股：

```text
若 raw_qty = 1,200 股，零股版預設最多買 999 股，不自動買成 1 張。
```

### 18T.6 零股撮合與回測成交模型

零股盤中交易不是 regular continuous trading。intraday odd-lot：

```text
1. 委託時間 09:00-13:30。
2. 第一盤撮合 09:10。
3. 之後每 5 秒集合競價撮合一次。
4. 委託限當日有效，未成交不帶入盤後零股。
5. 限價單，預設不使用純市價單。
```

因為多數歷史資料只有 15m OHLC，不會有每 5 秒零股委託簿，回測必須標註 fill_model。

預設保守模型：

```yaml
odd_lot_fill_model: conservative_15m_proxy
odd_lot_requires_intraday_odd_lot_volume: true
odd_lot_entry_order_type: limit
odd_lot_match_delay_seconds: 5
odd_lot_first_match_time: '09:10:00'
```

回測近似：

```python
match_time = next_odd_lot_match_time(planned_entry_time)
match_bar = bar_containing(match_time)

if match_bar.volume == 0:
    reject ODD_LOT_ENTRY_BAR_ZERO_VOLUME
elif match_bar.low <= entry_limit_price:
    entry_fill = min(entry_limit_price, max(match_bar.open, match_bar.low))
else:
    reject ODD_LOT_LIMIT_NOT_FILLED
```

注意：

```text
1. 這只是 15m OHLC 近似，不代表真實零股委託簿成交。
2. 若資料源能提供零股成交明細，必須優先使用零股成交明細。
3. 若沒有零股 volume，不能把 regular volume 當成零股 volume 直接使用；只能在報告標記 proxy_fill=true。
```

### 18T.7 同日出場、現股當沖與零股限制

Z3B-Prime 是 15m 入場確認模型，停損 / 停利可能在入場同一天被觸發。因此台股版必須處理同日出場權限。

整股版：

```yaml
round_lot_same_day_exit:
  require_day_trading_permission: true
  require_symbol_day_trading_eligible: true
  if_not_available: reject_entry
```

若帳戶或標的不支援同日沖銷：

```text
策略不能假裝 same-day stop / take-profit 可執行。
預設直接拒絕該筆進場，reason_code = SAME_DAY_EXIT_NOT_AVAILABLE_FOR_RISK_CONTROL。
```

零股版：

```yaml
odd_lot_same_day_exit:
  default_supported: false
  same_day_stop_take_profit: not_assumed_executable
  live_policy: reject_entry_or_next_day_risk_only
  backtest_policy: conservative_next_day_exit_only
```

零股版回測分兩種：

```text
1. live_valid_conservative：同日 SL/TP 不視為可成交；若同日觸發，標記 UNEXECUTABLE_SAME_DAY_ODD_LOT_EXIT，隔日按 gap rule 處理。
2. research_signal_only：允許同日 SL/TP 以 OHLC 模擬，只用來研究訊號品質，不可用作實盤績效。
```

預設必須使用：

```yaml
odd_lot_backtest_mode: live_valid_conservative
```

### 18T.8 台股交易稅與手續費 profile

普通股成本規則：

```text
1. 券商手續費買進、賣出都要計算；實際費率與最低手續費依券商而定。
2. 普通股證券交易稅只在賣出時收。
3. 普通股一般賣出稅率預設 0.3%。
4. 符合現股當沖規定的上市 / 上櫃普通股，同日等量沖銷賣出稅率可用 0.15%，期限依現行法規至 2027-12-31。
5. 零股預設不套用 0.15% 現股當沖稅率，使用 0.3%。
```

普通股 profile：

```yaml
fee_tax_profiles:
  tw_common_stock_default:
    commission_bps_before_discount: 14.25
    commission_discount: 1.0
    min_commission_twd: 0   # 依券商設定；不能硬寫
    buy_commission_applies: true
    sell_commission_applies: true
    sell_tax_bps: 30.0
    sell_tax_bps_day_trade_round_lot: 15.0
    day_trade_tax_reduction_valid_until: '2027-12-31'
    odd_lot_uses_day_trade_tax_reduction: false
```

手續費函數：

```python
commission_bps = commission_bps_before_discount * commission_discount
buy_fee  = max(floor_or_round(entry_fill * qty * commission_bps / 10000), min_commission_twd)
sell_fee = max(floor_or_round(exit_fill * qty * commission_bps / 10000), min_commission_twd)
```

交易稅函數：

```python
if product_type == 'common_stock':
    if execution_profile == 'tw_round_lot' and is_qualified_day_trade:
        sell_tax_bps = 15.0
    else:
        sell_tax_bps = 30.0
elif product_type == 'etf':
    sell_tax_bps = symbol_tax_profile.etf_sell_tax_bps
else:
    sell_tax_bps = symbol_tax_profile.sell_tax_bps

sell_tax = exit_fill * qty * sell_tax_bps / 10000
```

### 18T.9 台股 tick size 與價格四捨五入

所有 limit price、TP、SL trigger、price limit 都必須落在合法 tick。

實作要求：

```text
1. 優先從交易所 / 券商 / 資料商取得 symbol 當日 tick table。
2. 若使用內建台股普通股 tick table，必須集中在 tw_tick_size(price) 並有單元測試。
3. 不得把小數價格直接送單。
```

台股普通股 tick table：

```python
def tw_stock_tick_size(price: float) -> float:
    if price < 10:
        return 0.01
    if price < 50:
        return 0.05
    if price < 100:
        return 0.10
    if price < 500:
        return 0.50
    if price < 1000:
        return 1.00
    return 5.00
```

價格方向：

```python
entry_limit_buy  = ceil_to_tick(raw_entry_limit)
take_profit_sell = floor_to_tick(raw_take_profit)
stop_trigger     = floor_to_tick(raw_stop_loss)
stop_limit_sell  = floor_to_tick(raw_stop_limit)  # only if stop-limit is explicitly enabled
```

### 18T.10 漲跌停與停牌處理

每日漲跌幅限制預設：

```yaml
price_limit:
  enabled: true
  default_limit_pct: 0.10
  use_exchange_limit_price_if_available: true
  reject_no_price_limit_new_listing: true
```

實作要求：

```text
1. 優先使用資料源提供的 limit_up_price / limit_down_price。
2. 若沒有，依交易所規則與 tick table 計算，並標記 limit_price_derived=true。
3. 新上市前五日無漲跌幅限制的普通股，預設不交易。
4. 停牌 / 暫停交易 / 處置延長撮合，預設不開新倉。
```

進場：

```text
若 entry_limit_buy > limit_up_price，必須裁到 limit_up_price 或拒單。
若開盤漲停且沒有可成交量，reason_code = PRICE_LIMIT_BLOCKED_ENTRY。
```

停損：

```text
若 stop 被觸發但股價跌停且無法成交，不能假裝在 stop_loss 成交。
position remains open
reason_code = PRICE_LIMIT_BLOCKED_EXIT
```

停損成交價下限：

```python
stop_exit_fill = max(limit_down_price, stop_loss_level * (1 - stop_slippage_bps / 10000))
```

但若無成交量 / 停牌 / 跌停鎖死：

```text
exit_status = BLOCKED
blocked_exit = true
```

### 18T.11 台股 settlement / cash ledger

台股 settlement 是 T+2。策略雖然是 15m 訊號，但資金帳必須能處理交割。

```yaml
settlement:
  cycle: T+2
  require_cash_available_at_order_time: true
  track_settled_cash: true
  track_unsettled_cash: true
  sell_proceeds_available_policy: after_settlement
```

回測 ledger：

```text
on buy fill:
    available_cash -= buy_amount + buy_fee
    position_qty += qty
    settlement_payable_T_plus_2 += buy_amount + buy_fee

on sell fill:
    position_qty -= qty
    unsettled_receivable += sell_amount - sell_fee - sell_tax
    settled_cash increases on T+2
```

如果 broker 允許使用未交割款作為買進額度，必須用 config 顯式啟用：

```yaml
allow_unsettled_cash_reuse: false
```

### 18T.12 台股 entry / SL / TP 實盤流程

整股版 live flow：

```text
1. 15m bullish_trend_k 收盤，訊號成立。
2. 檢查帳戶是否可同日出場；若不行，拒絕進場。
3. 下一個 valid regular 15m bar open 準備進場。
4. 用 marketable limit buy，價格 = open * (1 + max_entry_slippage_bps / 10000)，再 ceil_to_tick。
5. 成交後，建立 stop monitor 與 take-profit limit。
6. stop_loss_level = golden_k.low，非 bullish_trend_k.low。
7. take_profit_level = 1H 前高。
8. 任一出場成交後取消另一個出場。
```

零股版 live flow：

```text
1. 15m bullish_trend_k 收盤，訊號成立。
2. 檢查 odd_lot_same_day_exit policy。
3. 若 live_valid_conservative 且無法同日出場，預設拒絕當日進場，或只允許 next_day_risk 模式。
4. 使用 intraday odd-lot limit order。
5. 由於零股為集合競價，成交不保證；未成交不追價。
6. 停損 / 停利若同日觸發，預設只記錄風險事件，不在 live_valid_conservative 回測中視為成交。
```

### 18T.13 台股 reason codes 新增

```text
TW_MARKET_NOT_SUPPORTED
TW_PRODUCT_NOT_ALLOWED
TW_NEW_LISTING_NO_PRICE_LIMIT_REJECTED
TW_DISPOSITION_SECURITY_REJECTED
TW_ALTERED_TRADING_METHOD_REJECTED
TW_HALTED_OR_SUSPENDED
TW_SHORT_SESSION_1H_BAR
TW_NEXT_DAY_ENTRY_AFTER_CLOSE
TW_PRICE_NOT_ON_VALID_TICK
TW_LIMIT_PRICE_DERIVED
TW_LIMIT_UP_ENTRY_BLOCKED
TW_LIMIT_DOWN_EXIT_BLOCKED
TW_SETTLED_CASH_INSUFFICIENT
TW_UNSETTLED_CASH_REUSE_DISABLED
ROUND_LOT_QTY_BELOW_ONE_LOT
ROUND_LOT_REMAINDER_DROPPED
ROUND_LOT_DAY_TRADE_PERMISSION_MISSING
ROUND_LOT_SYMBOL_NOT_DAY_TRADE_ELIGIBLE
SAME_DAY_EXIT_NOT_AVAILABLE_FOR_RISK_CONTROL
ODD_LOT_QTY_BELOW_ONE_SHARE
ODD_LOT_QTY_CAPPED_AT_999
ODD_LOT_LIMIT_ONLY
ODD_LOT_FIRST_MATCH_NOT_REACHED
ODD_LOT_ENTRY_BAR_ZERO_VOLUME
ODD_LOT_LIMIT_NOT_FILLED
ODD_LOT_PROXY_FILL_USED
ODD_LOT_INTRADAY_VOLUME_MISSING
ODD_LOT_SAME_DAY_EXIT_NOT_ASSUMED
UNEXECUTABLE_SAME_DAY_ODD_LOT_EXIT
ODD_LOT_AFTER_HOURS_NOT_USED
DAY_TRADE_TAX_REDUCTION_APPLIED
DAY_TRADE_TAX_REDUCTION_NOT_APPLIED
```

### 18T.14 台股版本選擇規則

預設推薦：

```text
正式績效回測與未來實盤優先使用 tw_round_lot。
零股版可做小資金測試，但報告必須獨立，不可和整股績效混算。
```

績效報告必須分開：

```text
1. Z3B-Prime tw_round_lot performance
2. Z3B-Prime tw_odd_lot live_valid_conservative performance
3. Z3B-Prime tw_odd_lot research_signal_only performance, if enabled
```

不得把 `research_signal_only` 當成可實盤績效。

## 19. 狀態機

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
    -> WAIT_15M_ISOLATED_LOWS_AND_GOLDEN_K
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
| `WAIT_15M_ISOLATED_LOWS_AND_GOLDEN_K` | 等第二低點確認不破，並確定第二低點形成的金 K | 第二低點破第一低點則失效；金 K 無法定位則等待或失效 |
| `WAIT_15M_BULLISH_TREND_K` | 金 K 後等多頭趨勢 K | 未出現則等待 |
| `IN_POSITION` | 管理 SL / TP | 觸發 SL 或 TP 出場 |
| `TRADE_CLOSED` | 記錄交易 | 回到等待下一候選 |

---

## 20. Reason codes

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
NO_GOLDEN_K_FOR_SECOND_LOW
GOLDEN_K_CONFIRMED
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


## 21. 實股回測規則

### 21.1 持倉限制

```yaml
position:
  instrument_type: spot_equity
  side: long_only
  leverage: 1.0
  allow_margin: false
  allow_short: false
  max_positions_per_symbol: 1
  allow_pyramiding: false
```

### 21.2 回測 broker 必須模擬的項目

```text
1. next valid regular-session bar open 進場。
2. marketable limit entry，不是理想市價。
3. entry_slippage_bps / stop_slippage_bps。
4. 手續費、交易稅、最低手續費。
5. 資金是否足夠。
6. lot size / tick size / min order quantity。
7. 交易時段與隔夜跳空。
8. 漲跌停 / 停牌 / 無量 K。
9. 成交量參與率上限。
10. 同 K 同時碰 SL / TP 的 stop_first 保守規則。
```

### 21.3 進場回測

```text
reference_entry_price = next_regular_15m_bar.open
entry_limit_price = reference_entry_price * (1 + max_entry_slippage_bps / 10000)
```

```text
if next_regular_15m_bar.open > entry_limit_price:
    reject ENTRY_LIMIT_NOT_FILLED
else:
    entry_fill = min(
        next_regular_15m_bar.open * (1 + entry_slippage_bps / 10000),
        entry_limit_price
    )
```

進場後檢查：

```text
if entry_fill <= stop_loss: reject INVALID_RISK_ENTRY_LE_STOP
if entry_fill >= take_profit: reject INVALID_TARGET_LE_ENTRY
```

### 21.4 停損回測

```text
if session_open < stop_loss:
    exit_fill = session_open * (1 - stop_slippage_bps / 10000)
    exit_reason = STOP_GAP_THROUGH_FILLED_AT_OPEN
elif low <= stop_loss:
    exit_fill = stop_loss * (1 - stop_slippage_bps / 10000)
    exit_reason = STOP_LOSS_HIT
```

若 stop 被觸發但市場不可成交：

```text
exit_status = BLOCKED
exit_reason = STOP_TRIGGERED_BUT_NOT_EXECUTABLE
position remains open
```

### 21.5 停利回測

```text
if high >= take_profit:
    exit_fill = take_profit
    exit_reason = TAKE_PROFIT_HIT
```

### 21.6 出場優先順序

每根 15m K：

```text
1. 若開盤跳空低於 stop_loss，先按 gap stop 出場。
2. 若同一根 K 同時 high >= TP 且 low <= SL，保守算 stop first。
3. 一般盤中先檢查 stop_loss，再檢查 take_profit。
```

### 21.7 成本與淨損益

```text
buy_fee = max(entry_fill * qty * buy_fee_bps / 10000, min_fee_per_order)
sell_fee = max(exit_fill * qty * sell_fee_bps / 10000, min_fee_per_order)
sell_tax = exit_fill * qty * sell_tax_bps / 10000

gross_pnl = (exit_fill - entry_fill) * qty
net_pnl = gross_pnl - buy_fee - sell_fee - sell_tax
```

### 21.8 不允許的回測簡化

```text
1. 不可用 bullish_trend_k.close 當 entry_fill。
2. 不可用 next_bar.open 無滑價成交，除非 slippage_bps 明確設為 0 並在報告標示。
3. 不可用 stop_loss 理想價成交，遇跳空必須用 open。
4. 不可忽略費用 / 稅。
5. 不可忽略交易時段。
6. 不可在無量 K 成交。
7. 不可在跌停不可賣時假裝停損成交。
```

---


## 22. Config 範例：實股版

```yaml
strategy_id: Z3B-Prime
package_name: z3b_prime_tw_equity

symbols:
  - 2330.TW
  - 0050.TW

instrument:
  type: spot_equity
  long_only: true
  allow_futures: false
  allow_margin: false
  allow_short: false
  leverage: 1.0

market:
  default_timezone: Asia/Taipei
  use_regular_session_only: true
  allow_extended_hours: false
  enforce_exchange_calendar: true
  delay_entry_to_next_session_if_needed: true

symbol_metadata:
  default_lot_size: 1000
  default_min_order_quantity: 1000
  default_tick_size: null
  supports_fractional_shares: false
  has_price_limit: auto

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
  bullish_k_must_be_after_golden_k: true

risk_anchor:
  stop_loss_source: golden_k_low
  forbid_bullish_k_low_as_stop: true

execution:
  mode: spot_equity_backtest
  entry_mode: next_regular_bar_open
  entry_order_type: marketable_limit
  allow_pure_market_order: false
  entry_order_timeout_bars: 1
  entry_slippage_bps: 5
  max_entry_slippage_bps: 20
  stop_order_type: simulated_stop_market
  stop_slippage_bps: 10
  take_profit_order_type: limit
  ambiguous_bar_policy: stop_first
  chase_if_not_filled: false

position_sizing:
  method: risk_percent
  risk_per_trade_pct: 0.005
  max_cash_per_trade_pct: 0.20
  min_order_value: 0
  round_to_lot_size: true

liquidity_filter:
  enabled: true
  min_avg_volume_20: 100000
  min_avg_turnover_20: 0
  max_order_participation_pct: 0.01
  require_nonzero_volume_on_entry_bar: true
  reduce_qty_if_exceeds_volume_cap: true

costs:
  buy_fee_bps: 0
  sell_fee_bps: 0
  sell_tax_bps: 0
  min_fee_per_order: 0
  use_symbol_fee_profile: true

corporate_actions:
  adjustment_mode: consistent_ohlc_adjustment
  adjust_position_on_split: true
  track_dividends_in_pnl: false

position:
  side: long_only
  max_positions_per_symbol: 1
  allow_pyramiding: false
```

---

## 23. 輸出結果

### 22.1 Trade log 欄位

```text
trade_id
strategy_id
symbol
entry_time
entry_price
entry_fill
entry_order_type
entry_limit_price
entry_slippage_bps
qty
order_value
stop_loss
take_profit
exit_time
exit_price
exit_fill
exit_order_type
exit_reason
buy_fee
sell_fee
sell_tax
gross_pnl
net_pnl
pnl_pct
rr_planned
holding_bars
execution_status
partial_fill_ratio
blocked_exit

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

golden_k_time
golden_k_open
golden_k_high
golden_k_low
golden_k_close
stop_loss_source

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
10. 金 K：停損錨點。
11. 多頭趨勢 K：入場確認。
12. Entry / SL / TP。
13. MACD 診斷標籤，但不得顯示為硬條件。
```

---

## 24. 建議專案結構

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
  execution/
    broker_sim.py
    equity_orders.py
    order_types.py
    sizing.py
    costs.py
    calendars.py
    liquidity.py
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

## 25. 核心資料類別

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
class EquityExecutionPlan:
    symbol: str
    signal_time: pd.Timestamp
    planned_entry_time: pd.Timestamp
    reference_entry_price: float
    entry_order_type: str
    entry_limit_price: float
    stop_loss_level: float
    take_profit_level: float
    qty: int
    estimated_buy_fee: float
    estimated_risk_cash: float
    reason_code: str

@dataclass
class EquityFill:
    order_id: str
    symbol: str
    side: Literal["buy", "sell"]
    time: pd.Timestamp
    requested_qty: int
    filled_qty: int
    fill_price: float
    fee: float
    tax: float
    status: Literal["filled", "partial", "cancelled", "blocked"]
    reason_code: str

@dataclass
class TradeSignal:
    strategy_id: str
    symbol: str
    signal_time: pd.Timestamp
    golden_k_time: pd.Timestamp
    golden_k_low: float
    bullish_k_time: pd.Timestamp
    entry_time: pd.Timestamp
    entry_price: float
    stop_loss: float
    take_profit: float
    rr: float
    reason_code: str
    metadata: dict
```

---

## 26. Pseudocode

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
                state.name = "WAIT_15M_ISOLATED_LOWS_AND_GOLDEN_K"
            else:
                log("BB_NOT_LESS_THAN_BA")
                continue

        if state.name == "WAIT_15M_ISOLATED_LOWS_AND_GOLDEN_K":
            iso1, iso2 = find_isolated_lows(state.bA, swings_15m)
            if not iso2:
                continue
            if iso2.price < iso1.price:
                log("SECOND_LOW_BROKE_FIRST_LOW")
                state.reset_to_wait_15m_center_A()
                continue
            golden_k = resolve_golden_k_from_iso_low_2(iso2, bars_15m, config)
            if not golden_k:
                log("NO_GOLDEN_K_FOR_SECOND_LOW")
                continue
            state.iso1 = iso1
            state.iso2 = iso2
            state.golden_k = golden_k
            state.stop_loss = golden_k.low
            log("GOLDEN_K_CONFIRMED")
            state.name = "WAIT_15M_BULLISH_TREND_K"

        if state.name == "WAIT_15M_BULLISH_TREND_K":
            k = latest_closed_15m_bar(ctx_15m)
            if k.time <= state.golden_k.time:
                continue
            if is_bullish_trend_k(k, state.bA, config):
                signal = build_trade_signal(
                    bullish_k=k,
                    golden_k=state.golden_k,
                    entry_price=next_bar_open(bars_15m, k),
                    stop_loss=state.golden_k.low,
                    take_profit=state.target_high_1h,
                    metadata=state.metadata(),
                )
                if signal_is_valid(signal):
                    emit(signal)
                    state.name = "IN_POSITION"
                else:
                    log(signal.reason_code)
```



### 26.1 Execution pseudocode extension

```python
def handle_valid_z3b_signal(signal, bars_15m, account, symbol_meta, config):
    plan = build_equity_execution_plan(
        signal=signal,
        account=account,
        symbol_meta=symbol_meta,
        config=config,
    )

    if not plan.is_valid:
        log(plan.reason_code)
        return None

    entry_fill = broker_sim.try_enter_long_marketable_limit(
        plan=plan,
        next_bar=get_next_regular_15m_bar(signal.bullish_k_time),
        config=config,
    )

    if not entry_fill or entry_fill.status not in ["filled", "partial"]:
        log(entry_fill.reason_code if entry_fill else "ENTRY_LIMIT_NOT_FILLED")
        return None

    position = open_equity_position_from_fill(signal, plan, entry_fill)

    # After entry, create OCO intent if supported, otherwise monitor bars.
    position.stop_loss_level = signal.stop_loss  # golden_k.low
    position.take_profit_level = signal.take_profit

    return position


def manage_open_equity_position(position, bar, session_state, config):
    if session_state.halted or session_state.no_sell_execution:
        if bar.low <= position.stop_loss_level:
            position.blocked_exit = True
            log("STOP_TRIGGERED_BUT_NOT_EXECUTABLE")
        return position

    if bar.open < position.stop_loss_level:
        exit_fill = bar.open * (1 - config.execution.stop_slippage_bps / 10000)
        close_position(position, exit_fill, "STOP_GAP_THROUGH_FILLED_AT_OPEN")
        return None

    if bar.low <= position.stop_loss_level and bar.high >= position.take_profit_level:
        exit_fill = position.stop_loss_level * (1 - config.execution.stop_slippage_bps / 10000)
        close_position(position, exit_fill, "AMBIGUOUS_BAR_STOP_FIRST")
        return None

    if bar.low <= position.stop_loss_level:
        exit_fill = position.stop_loss_level * (1 - config.execution.stop_slippage_bps / 10000)
        close_position(position, exit_fill, "STOP_LOSS_HIT")
        return None

    if bar.high >= position.take_profit_level:
        close_position(position, position.take_profit_level, "TAKE_PROFIT_HIT")
        return None

    return position
```

---

## 27. 單元測試要求

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
9. test_ab_compare_b_less_a_does_not_open_trade_v1_2
10. test_bA_must_be_smaller_than_A
11. test_bb_less_than_ba_allows_next_confirmation_state
12. test_second_low_must_not_break_first_low
13. test_bullish_trend_k_body_threshold
14. test_early_bullish_k_before_structure_complete_rejected
15. test_golden_k_is_resolved_from_second_isolated_low
16. test_golden_k_must_precede_bullish_trend_k
17. test_stop_loss_is_golden_k_low
18. test_stop_loss_is_not_bullish_k_low
19. test_take_profit_is_1h_target_high
20. test_entry_uses_next_15m_open
21. test_ambiguous_bar_stop_first
22. test_reason_codes_are_logged_for_rejections
23. test_trade_log_contains_all_structure_fields
24. test_equity_entry_uses_marketable_limit_not_ideal_fill
25. test_entry_limit_not_filled_when_open_above_limit
26. test_entry_rejected_when_market_closed
27. test_entry_delayed_to_next_regular_session
28. test_position_size_uses_risk_budget_and_lot_size
29. test_insufficient_cash_rejects_order
30. test_liquidity_volume_cap_reduces_or_rejects_qty
31. test_stop_gap_through_fills_at_open_not_stop_price
32. test_stop_triggered_but_not_executable_keeps_position_open
33. test_take_profit_limit_fill_at_target
34. test_costs_and_taxes_reduce_net_pnl
35. test_no_futures_no_margin_no_short_modes_allowed
36. test_partial_fill_updates_exit_qty_only_for_filled_qty
```

---

## 28. 驗收標準

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
15. 自動解析 golden_k，並使用 golden_k.low 作為停損。
16. 自動判斷 golden_k 之後的多頭趨勢 K。
16. 自動產生 entry / SL / TP。
17. 自動回測 SL / TP。
18. 自動輸出 trade log / signal log。
19. 能產出標註圖，方便檢查每筆交易是否符合第一部影片語義。
20. 所有單元測試通過。
21. 實股執行層能模擬 marketable limit entry、stop-market exit、limit TP、滑價、費用、交易稅、跳空、交易時段、成交量限制。
22. trade log 必須同時包含策略結構欄位與實際成交欄位。
23. 報告必須分開顯示 gross_pnl 與 net_pnl。
```

---

## 29. 給 Codex 的實作指令

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
1. Python package: z3b_prime_equity
2. config.example.yaml
3. strategy implementation
4. spot equity execution simulator
5. backtest CLI
6. trade log CSV with execution fields
7. signal log CSV
8. annotated chart examples
9. unit tests, including execution tests
10. README with usage instructions
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

## 30. README 命令範例

```bash
python -m z3b_prime_equity.backtest \
  --config config.example.yaml \
  --data-dir ./data \
  --symbols 2330.TW 0050.TW AAPL \
  --start 2023-01-01 \
  --end 2026-01-01 \
  --out ./reports/z3b_prime_equity
```

期望輸出：

```text
reports/z3b_prime_equity/trades.csv
reports/z3b_prime_equity/signals.csv
reports/z3b_prime_equity/orders.csv
reports/z3b_prime_equity/fills.csv
reports/z3b_prime_equity/metrics.json
reports/z3b_prime_equity/charts/*.png
```

---

## 31. v1.4 重要備註

這份規格的目標不是提高勝率，也不是最佳化參數，而是先把第一部影片的策略邏輯變成可重現、可檢查、可回測的模型。

第二部影片的價值是幫助理解中樞與 a/b 的語義，但不能讓模型脫離第一部影片的開單流程。

v1.4 的設計原則：

```text
寧可少開單，也不要亂把觀念影片延伸成額外交易邏輯；停損必須錨定金 K，而不是後面的多頭趨勢 K。
```


---

## 32. 外部執行風險參考來源（只用於訂單風險觀念）

以下來源只支援「實股執行層」的市場訂單風險觀念，不是 Z3B-Prime 策略來源：

```text
1. SEC Investor.gov, Types of Orders:
   market order 通常保證執行，但不保證執行價格。
   https://www.investor.gov/introduction-investing/investing-basics/how-stock-markets-work/types-orders

2. SEC Investor.gov, Investor Bulletin: Understanding Order Types:
   stop price 是觸發價，不是保證成交價；stop order 觸發後可能以偏離 stop price 的價格成交。
   https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins-14

3. SEC Investor.gov, Stop, Stop-Limit, and Trailing Stop Orders:
   stop-limit 可控制價格，但可能不成交。
   https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins-15

4. FINRA, Order Types:
   stop orders 可用於風險控管，但需要理解 stop 與 stop-limit 的差異。
   https://www.finra.org/investors/investing/investment-products/stocks/order-types
```

工程要求：不得因為加入這些外部執行風險來源，就改變第一部影片的策略訊號邏輯。


## 33. 台股整股版 Config：`tw_round_lot`

```yaml
strategy_id: Z3B-Prime
package_name: z3b_prime_tw_equity
execution_profile: tw_round_lot

market_scope:
  country: Taiwan
  timezone: Asia/Taipei
  currency: TWD
  exchanges_allowed: [TWSE, TPEX]
  product_allowed_default: common_stock
  allow_etf: false
  allow_warrant: false
  allow_futures: false
  allow_options: false
  allow_margin: false
  allow_short: false
  leverage: 1.0

symbols:
  - 2330.TW
  - 2317.TW
  - 2454.TW

sessions:
  regular:
    open: '09:00:00'
    close: '13:30:00'
    timezone: Asia/Taipei
  order_entry_start: '08:30:00'
  use_after_hours_fixed_price: false
  use_after_hours_odd_lot: false
  entry_after_last_15m_bar: next_trading_day_09_00

bar_construction:
  entry_tf: 15m
  trend_tf: 1h
  trend_tf_session_local: true
  include_short_final_1h_bar: true
  short_final_1h_bar: '13:00-13:30'
  do_not_bridge_overnight: true

quantity:
  lot_size_shares: 1000
  min_order_quantity_shares: 1000
  round_to_lot_size: true
  allow_odd_lot_remainder: false

execution:
  entry_order_type: marketable_limit
  allow_pure_market_order: false
  entry_order_timeout_bars: 1
  entry_slippage_bps: 5
  max_entry_slippage_bps: 20
  price_rounding:
    entry_limit_buy: ceil_to_tick
    take_profit_sell: floor_to_tick
    stop_trigger: floor_to_tick
  chase_if_not_filled: false

same_day_exit:
  require_day_trading_permission: true
  require_symbol_day_trading_eligible: true
  if_not_available: reject_entry

risk_anchor:
  stop_loss_source: golden_k_low
  forbid_bullish_k_low_as_stop: true

exit:
  stop_order_type: broker_or_engine_simulated_stop_market
  stop_slippage_bps: 10
  take_profit_order_type: sell_limit
  ambiguous_bar_policy: stop_first
  gap_stop_policy: fill_at_open_minus_slippage
  price_limit_blocked_exit_policy: keep_position_open_and_flag

position_sizing:
  method: risk_percent
  risk_per_trade_pct: 0.005
  max_cash_per_trade_pct: 0.20
  min_order_value_twd: 0

liquidity_filter:
  enabled: true
  min_avg_volume_20_shares: 100000
  max_order_participation_pct: 0.01
  require_nonzero_volume_on_entry_bar: true
  reduce_qty_if_exceeds_volume_cap: true

fees_and_taxes:
  profile: tw_common_stock_default
  commission_bps_before_discount: 14.25
  commission_discount: 1.0
  min_commission_twd: 0
  sell_tax_bps: 30.0
  sell_tax_bps_day_trade_round_lot: 15.0
  day_trade_tax_reduction_valid_until: '2027-12-31'
  apply_day_trade_tax_reduction_if_qualified: true

settlement:
  cycle: T+2
  require_cash_available_at_order_time: true
  track_settled_cash: true
  track_unsettled_cash: true
  allow_unsettled_cash_reuse: false

price_limit:
  enabled: true
  default_limit_pct: 0.10
  use_exchange_limit_price_if_available: true
  reject_no_price_limit_new_listing: true

reporting:
  separate_round_lot_and_odd_lot_performance: true
  log_all_rejected_signals: true
```

---

## 34. 台股零股版 Config：`tw_odd_lot`

```yaml
strategy_id: Z3B-Prime
package_name: z3b_prime_tw_equity
execution_profile: tw_odd_lot

market_scope:
  country: Taiwan
  timezone: Asia/Taipei
  currency: TWD
  exchanges_allowed: [TWSE, TPEX]
  product_allowed_default: common_stock
  allow_etf: false
  allow_warrant: false
  allow_futures: false
  allow_options: false
  allow_margin: false
  allow_short: false
  leverage: 1.0

symbols:
  - 2330.TW
  - 2317.TW
  - 2454.TW

sessions:
  intraday_odd_lot:
    order_start: '09:00:00'
    order_end: '13:30:00'
    first_match: '09:10:00'
    match_interval_seconds: 5
    timezone: Asia/Taipei
  use_after_hours_odd_lot: false
  after_hours_odd_lot:
    order_start: '13:40:00'
    order_end: '14:30:00'
    match_once_after: '14:30:00'
  entry_after_last_15m_bar: next_trading_day_09_00

bar_construction:
  entry_tf: 15m
  trend_tf: 1h
  trend_tf_session_local: true
  include_short_final_1h_bar: true
  short_final_1h_bar: '13:00-13:30'
  do_not_bridge_overnight: true

quantity:
  lot_size_shares: 1
  min_order_quantity_shares: 1
  max_order_quantity_shares: 999
  round_to_lot_size: true
  cap_qty_at_999: true
  allow_round_lot_conversion: false

execution:
  entry_order_type: odd_lot_limit
  allow_pure_market_order: false
  entry_order_timeout_bars: 1
  entry_slippage_bps: 10
  max_entry_slippage_bps: 30
  odd_lot_fill_model: conservative_15m_proxy
  odd_lot_requires_intraday_odd_lot_volume: true
  proxy_fill_allowed_if_odd_lot_volume_missing: false
  chase_if_not_filled: false

same_day_exit:
  default_supported: false
  live_policy: reject_entry_or_next_day_risk_only
  backtest_policy: live_valid_conservative
  research_signal_only_mode_allowed: true
  research_signal_only_must_be_reported_separately: true

risk_anchor:
  stop_loss_source: golden_k_low
  forbid_bullish_k_low_as_stop: true

exit:
  stop_order_type: broker_or_engine_simulated_stop_market_when_executable
  stop_slippage_bps: 20
  take_profit_order_type: odd_lot_sell_limit
  same_day_sl_tp_fill_allowed: false
  next_day_gap_rule_if_same_day_triggered: true
  ambiguous_bar_policy: stop_first
  price_limit_blocked_exit_policy: keep_position_open_and_flag

position_sizing:
  method: risk_percent
  risk_per_trade_pct: 0.003
  max_cash_per_trade_pct: 0.05
  min_order_value_twd: 0

liquidity_filter:
  enabled: true
  require_nonzero_volume_on_entry_bar: true
  require_odd_lot_volume_if_available: true
  max_order_participation_pct: 0.005
  reduce_qty_if_exceeds_volume_cap: true

fees_and_taxes:
  profile: tw_common_stock_odd_lot_default
  commission_bps_before_discount: 14.25
  commission_discount: 1.0
  min_commission_twd: 0
  sell_tax_bps: 30.0
  apply_day_trade_tax_reduction_if_qualified: false
  odd_lot_uses_day_trade_tax_reduction: false

settlement:
  cycle: T+2
  require_cash_available_at_order_time: true
  track_settled_cash: true
  track_unsettled_cash: true
  allow_unsettled_cash_reuse: false

price_limit:
  enabled: true
  default_limit_pct: 0.10
  use_exchange_limit_price_if_available: true
  reject_no_price_limit_new_listing: true

reporting:
  separate_round_lot_and_odd_lot_performance: true
  tag_as_odd_lot: true
  log_proxy_fills: true
  log_all_rejected_signals: true
```

---

## 35. 台股單元測試與驗收要求

Codex 必須為台股執行層新增測試。

### 31.1 整股版測試

```text
1. raw_qty = 2350 -> qty = 2000，reason_code 包含 ROUND_LOT_REMAINDER_DROPPED。
2. raw_qty = 999 -> reject ROUND_LOT_QTY_BELOW_ONE_LOT。
3. signal at 13:15-13:30 -> entry_time next trading day 09:00。
4. entry_limit_buy 必須 ceil_to_tick。
5. take_profit_sell 必須 floor_to_tick。
6. stop_loss_source 必須 golden_k.low，不得使用 bullish_trend_k.low。
7. 帳戶無當沖權限且可能需要同日出場 -> reject SAME_DAY_EXIT_NOT_AVAILABLE_FOR_RISK_CONTROL。
8. 賣出普通股稅率：非當沖 0.3%，符合整股當沖條件 0.15%。
```

### 31.2 零股版測試

```text
1. raw_qty = 0.8 -> reject ODD_LOT_QTY_BELOW_ONE_SHARE。
2. raw_qty = 235 -> qty = 235。
3. raw_qty = 1200 -> qty = 999，reason_code ODD_LOT_QTY_CAPPED_AT_999。
4. planned_entry_time = 09:02 -> first executable match >= 09:10。
5. planned_entry_time = 10:15:00 -> next match = 10:15:05 or next legal match tick。
6. 未成交零股 intraday order 不得帶到盤後零股。
7. live_valid_conservative 下，同日 SL/TP 觸發不得視為成交，必須標記 UNEXECUTABLE_SAME_DAY_ODD_LOT_EXIT。
8. 零股賣出普通股稅率預設 0.3%，不得套用 0.15% 現股當沖稅率。
```

### 31.3 台股市場規則測試

```text
1. session-aware 1H 最後一根為 13:00-13:30 short bar。
2. 不能跨隔夜 resample 成連續 1H。
3. 無成交量 K 不得成交。
4. 跌停鎖死觸發 stop 時，不能假裝 stop_loss 成交。
5. 停牌期間不能開倉或平倉。
6. 新上市前五日無漲跌幅限制股票預設拒絕。
7. T+2 ledger 正確更新 settled_cash / unsettled_cash。
```

---

## 36. 台股資料與法規來源備註

本文件的台股執行層依 2026-05-17 可查之公開資料校準。Codex 不需要在策略程式內寫入 web citation，但 README 應列出資料來源與版本日期。

Source URLs:

```text
TWSE 2025 Guide to Investing in Taiwan:
https://www.twse.com.tw/en/about/company/guide.html

TWSE Odd-Lot Trading Regulations:
https://twse-regulation.twse.com.tw/m/EN/LawContent.aspx?FID=FL007115

TPEx Intraday Odd-Lot Trading:
https://www.tpex.org.tw/en-us/mainboard/trading/rules/odd-lot.html

TWSE Day Trading:
https://www.twse.com.tw/en/products/system/day-trading.html

Ministry of Finance - Securities Transaction Tax Act:
https://law-out.mof.gov.tw/EngLawContent.aspx?id=20707

TWSE Fund and Securities Settlement Operation:
https://www.twse.com.tw/en/clearing/clearing/operations.html

TWSE Features of Clearing and Settlement Operations:
https://www.twse.com.tw/en/clearing/clearing/features.html

TWSE Operating Rules:
https://twse-regulation.twse.com.tw/m/en/LawContent.aspx?FID=FL007304

FSC press release on intraday odd-lot matching interval:
https://www.fsc.gov.tw/en/home.jsp?dataserno=202402200001&dtable=News&id=54&mcustomize=multimessage_view.jsp&parentpath=0
```

若交易所規則、券商 API、手續費折扣或稅率更新，必須更新：

```text
1. market calendar
2. tick table
3. lot / odd-lot rules
4. tax profile
5. day-trade eligibility rules
6. broker order support matrix
```


---

## 37. v1.4 結論給 Codex

```text
Z3B-Prime v1.4 的策略訊號仍以第一部影片為主。
第二部影片只作中樞概念輔助，不新增開單路徑。
停損必須是 golden_k.low，不是 bullish_trend_k.low。
台股執行層必須拆成 tw_round_lot 與 tw_odd_lot 兩個 profile。
整股版是正式主版本；零股版必須保守處理同日出場與集合競價成交。
所有績效必須扣手續費、交易稅、滑價，並處理 T+2、漲跌停、跳空、停牌、成交量不足與部分成交。
```
