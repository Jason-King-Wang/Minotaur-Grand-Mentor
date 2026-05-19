# 使用者口述三買規則與原公式對照

## 對照結論

本次以使用者口述規則為主，取代原本較泛化的 1H 三買 gate 與 15m direct path。

## 1H 規則

| 使用者口述 | 原模型狀態 | 本次修改 |
|---|---|---|
| 1H 先下跌，跌破/離開時的中樞是第一個中樞 | 原模型只找任意 1H 中樞，沒有明確定義第一中樞序列 | 改為要求中樞必須位於某次 1H 破高之後的回撤/下跌段，且中樞形成後要被 1H 向下有效跌破 |
| 漲回來不能高於第一中樞最高點，此高點稱為前高點 | 原模型用 center.upper 判斷向上離開，沒有前高點概念 | 新增 previous_high：第一個在中樞後且不高於 center.box_high 的 1H swing high |
| 前高後再次下跌，再反轉上來突破前高 | 原模型只找向上離開與結構突破 | 新增 pullback_low_before_breakout 與 breakout_high，必須先跌後漲破 previous_high |
| 突破前高後再下跌的低點才是三買 | 原模型把「向上離開後第一個回抽不回中樞」當三買 | 新增 third_buy_low：breakout_high 後第一個 1H swing low |
| 到「突破前高後的這個高點」才切 15m | 原模型從 1H pullback index 開始切 15m | 改為從 breakout_high.time 開始找 15m A / b-A |

## 15m 規則

| 使用者口述 | 原模型狀態 | 本次修改 |
|---|---|---|
| 15m 才開始有中樞 A | 原模型可抓到與 1H 回抽段重疊的 A | 改為 A 必須從 1H breakout_high 之後開始 |
| a 是最後高點進入中樞 A 反彈的小回撤 | 原模型 build_ab_legs 大致相似，但未檢查真下跌 | 新增 down_leg 合法性，a 必須真的下跌且 length > 0 |
| b 是中樞 A 向下突破到金 K 底的持續下跌，且 b 要比 a 長 | 原模型有 b>a 走 b-A，但也允許 b<a direct path | 移除 direct path，只允許 b>a，b 長度以 b_start_high 到 b-b 金 K 低點計 |
| b 尾段要有 b-A | 原模型找 A 後任意 b-A 候選，範圍偏寬 | b-A 必須在 A 後、b_start_high 後才可用 |
| b-a 是 b 開始到 b-A 前面 | 原模型 b-a 以 b-A 前 swing 組合，未綁定 b 起點 | 新增 build_ba_bb_legs_from_b_start，b-a 從 b_start_high 到 b-A 前低點 |
| b-b 是 b-A 內部最高點到結束 | 原模型類似，但未要求新低不破 | b-b 從 b-A 內部最高點到 b-A 後第一個低點 |
| b-b < b-a | 原模型已有 bb_less_than_ba | 保留 |
| b-b 低點不能比 b-a 低點更低 | 原模型只有 generic 兩低不破 | 改為明確比較 bb_leg.end_price >= ba_leg.end_price |
| b-b 以金 K 為終結，後面出現大長漲線入場 | 原模型用 golden_k + bullish trend K | 暫時沿用目前「多頭趨勢 K 線」量化定義，後續可調 |

## 尚未納入的缺口

1. 使用者沒有定義止盈，本次仍保留原模型的 1H 目標高點停利回測層，否則無法產出五大績效指標。
2. 「大長漲線 / 多頭趨勢 K 線」暫時沿用原工程定義：大實體、上影線短、收盤位置高、必要時收過局部壓力。
3. Stop 已確認為金 K 底部極值點，即金 K low。

## 本次對「斷掉」的工程定義

```text
center_high = center.box_high
center_low  = center.box_low

斷掉 = 中樞 confirmed / end_index 之後，
        先出現 1H close < center_low，
        且後面有 confirmed swing low < center_low。
```

前高點只從這個向下斷掉之後才開始找。
