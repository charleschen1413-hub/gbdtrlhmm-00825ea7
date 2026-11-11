# 來源快照：`/workspace/ml_meta/reports/DIAG_TRADECOUNT_v1.md`

- **探索性、非獨立盲測；非官方驗收**
- 來源路徑：`/workspace/ml_meta/reports/DIAG_TRADECOUNT_v1.md`
- sha1：`18fe1963514dc3658619e16c0d8709bf009bb28a`
- 快照時間：2026-11-11 22:48（台北時間）
- 本頁只轉述來源文件已有的內容，不自行推論或加數字。

---

# 交易筆數流失診斷 v1（探索性、非官方結論）

撰寫：2026-11-11 22:31（台北時間）。只讀既有輸出，未重跑試驗、未重訓模型、未重算後三年驗收。不得稱獨立盲測。

## 結論先講

1. 六種 PCR 模式本身（1 分 K、全接受、無模型過濾）十年完成交易皆不足 300：A1／A1B＝175、A2／A2B＝189、A3／A3B＝16；PCR_ONLY 對照＝191（與 tick 基準證據相符）。沒有任何底層模式單獨達到十年 ≥300。
2. 六種底層模式的二考完成交易皆為 0。PCR_ONLY 在 2026-08-09 18:00 進場後持倉至資料終點 2026-09-28、不強制平倉，故 2026-08-15～09-28 二考窗內沒有已完成交易。底層模式單獨也無法滿足二考 ≥5。
3. 因此「十年 ≥300、二考 ≥5」的第一限制是底層 PCR 模式本身筆數不足（以及二考窗內未完成出場），不是特徵集。特徵只改變可算樣本數（F1 的 `n_finite` 等於該模式全部訊號；F2～F5 因缺值降至約三分之二），不改變上述十年交易上限。
4. 模型過濾是第二層流失：第一輪 60 格 rank-1 樣本接受率中位數僅 19.1%（最高 78.6%，無一格 ≥90%）；GBDT／邏輯迴歸 rank-1 幾乎都選了較嚴的進場門檻 0.6（GBDT 17／20、邏輯迴歸 17／20）。第一輪十年交易最多 275（仍 <300），中位數 107。
5. 少數格子靠更碎的進出把十年交易抬到超過底層（第一輪 13 格、第二輪 10 格交易比 >1）。只有第二輪兩格達到十年 ≥300 且二考 ≥5：A1B|F3|hmm＝371／5（交易比 2.12）、A2B|F4|hmm＝419／5（交易比 2.22），接受率約 57–59%，研究分級皆 Fail。另有 3 格模型完全不接受訊號（`n_take`＝0，十年 0 筆，紅線 4 停止判定／ValueError）。全接受的兩格 HMM（接受率 100%）十年交易正好等於底層 189，仍不足 300。

## 口徑與限制

- **底層訊號**：`features_v3/samples_all.csv` 中該 PCR 模式、該特徵集延遲（F1／F2／F3＝0 小時，F4＝6 小時，F5＝24 小時）的樣本。「十年訊號」＝`in_front7` 或 `in_back3`（以 `fill_dt` 落在前七年或後三年）。這是日頻訊號列，不是完成交易。
- **底層交易**：既有 `baselines/ledger_{模式}.csv`（1 分 K、該模式全接受、無 SMA3 過濾）。以 `metrics_v2.slice_trades`、出場交易日＝出場時戳＋6 小時後取曆日、閉區間，按 `freeze/windows_v2.json` 切十年／前七年／後三年／二考。缺資料日名單為空。這不是新回測，只是對既有帳本做窗口計數。
- **未找到、故未猜測的輸入**：各模式×延遲的 tick 全接受十年帳本不在既有輸出裡。僅 PCR_ONLY 有 tick 基準證據，十年 191、二考 0，與 1 分 K 帳本重切結果完全相同；其餘五模式的十年底層交易只能引用 1 分 K 帳本。F4／F5 延遲全接受的獨立交易帳本亦缺。
- **樣本接受率**：`n_take / n_finite`。`n_finite` 是該格特徵可算的全部樣本（含 2016-09-29 之前），不是十年子集；既有 metrics 沒有另存十年限定的 `n_take`，本診斷不重擬合，故不編造十年接受率。
- **交易比**：模型十年完成交易／該模式 1 分 K 底層十年完成交易。可比 1 大：模型把長持倉切成更多來回，不是底層機會變多。
- `n_signal_events` 是目標序列變點（含平倉到 0），不是接受筆數，不當作接受率分母。
- 本檔數字皆為探索性、非官方結論。官方路徑 51 個 FAIL 依 REVIEW8 不得當成已滿足紅線 4 全部條件的正式官方驗收。

## 底層 PCR 模式（1 分 K 全接受）

| 模式 | 帳本列數（含暖機） | 前七年 | 後三年 | 十年 | 二考 | 十年是否 ≥300 | 帳本 sha1 |
|---|---:|---:|---:|---:|---:|---|---|
| PCR_ONLY（對照，非六模式之一） | 309 | 124 | 67 | 191 | 0 | 否 | `9394899f4cd63292967edea9f207499ca388c4ab` |
| A1 | 285 | 108 | 67 | 175 | 0 | 否 | `04f57be45817814109500054f80016fc6bb8abb8` |
| A1B | 285 | 108 | 67 | 175 | 0 | 否 | `a85aa7671d7d47d1fce1076b82d739bd79d26cfd` |
| A2 | 300 | 122 | 67 | 189 | 0 | 否 | `e3a9b2f5958c2c7cb58b542da54837c1244f6182` |
| A2B | 300 | 122 | 67 | 189 | 0 | 否 | `2d960560a88d58eb8f7d843487e9d21d026e2ebb` |
| A3 | 19 | 16 | 0 | 16 | 0 | 否 | `46581255e37e1496751220fd8f912bc870f76fa1` |
| A3B | 19 | 16 | 0 | 16 | 0 | 否 | `48147c8750e5e44ec461facdbb566044d5153a9a` |

核對：PCR_ONLY 十年 191、前七年 124、二考 0，與 `e2e_tick_v3/baseline_evidence.json` 及前七年基準表相符。A1／A2／A3 前七年 108／122／16 亦與 `baselines/front7_table.csv` 相符。A2／A2B 帳本列數恰好 300，但含暖機；十年完成交易是 189，不是 300。

十年訊號（delay 0／6 小時相同；delay 24 小時 A1／A2 系僅多 1 筆後三年）：A1／A1B＝2,205，A2／A2B＝2,508，A3／A3B＝223（後三年訊號 0）。A3／A3B 第一輪 30 格、第二輪 20 格皆無合格 rank-1，與後三年樣本為 0、前七年樣本只落在折 3 之後的既有結論相符。

## 第一輪 60 格 rank-1（另 30 格 A3／A3B 無合格 rank-1）

- 研究分級：A 10／B 4／Fail 43／紅線 4 停止判定／ValueError 3。官方路徑沿用同一批帳本：PASS 0／FAIL 51／紅線 4 停止判定／ValueError 9（與 official SUMMARY 及階段 A metrics 的十年／二考筆數逐格相符，0 筆不符）。
- 十年交易：最少 4、中位數 107、最多 275，**0 格 ≥300**。二考 ≥5 的 7 格皆研究 Fail。
- 樣本接受率：最少 0.55%（A2|F1|logistic，門檻 0.6）、中位數 19.1%、最多 78.6%（A1B|F3|rule_table，`mean_return_threshold=0.0`）。
- 選中門檻：GBDT 進場門檻 0.6 共 17 格、0.55 共 3 格（網格尚有 0.5，無 rank-1 選到 0.5）。邏輯迴歸 0.6 共 17 格、0.55 共 2 格、0.5 共 1 格。規則表 `mean_return_threshold` 為 0.0／0.001／0.0005 各 10／7／3 格，`min_cell_n` 全為 5。
- 十年交易最多的格是 A2B|F4|rule_table（275，交易比 1.46，二考 3，Fail），仍低於 300。

| 格 | trial_id | 底層十年訊號 | 底層十年交易 | n_finite | n_take | 樣本接受率 | 模型十年交易 | 二考交易 | 交易比 | 選中門檻／參數 | 研究分級 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| A1|F1|gbdt | v3_A1_F1_gbdt_00051 | 2205 | 175 | 3295 | 234 | 7.1% | 100 | 0 | 0.571 | threshold=0.6; max_depth=2; learning_rate=0.05; max_iter=100; min_samples_leaf=50; seed=42 | Fail |
| A1|F1|logistic | v3_A1_F1_logistic_00018 | 2205 | 175 | 3295 | 22 | 0.7% | 4 | 0 | 0.023 | threshold=0.6; C=0.1; class_weight=none; max_iter=5000; seed=42; standardize=True | 紅線 4 停止判定／ValueError |
| A1|F1|rule_table | v3_A1_F1_rule_table_00001 | 2205 | 175 | 3295 | 1631 | 49.5% | 88 | 0 | 0.503 | mean_return_threshold=0.0; min_cell_n=5 | Fail |
| A1|F2|gbdt | v3_A1_F2_gbdt_00207 | 2205 | 175 | 2226 | 116 | 5.2% | 61 | 0 | 0.349 | threshold=0.6; max_depth=2; learning_rate=0.1; max_iter=50; min_samples_leaf=20; seed=42 | A |
| A1|F2|logistic | v3_A1_F2_logistic_00175 | 2205 | 175 | 2226 | 823 | 37.0% | 107 | 0 | 0.611 | threshold=0.5; C=10.0; class_weight=none; max_iter=5000; seed=42; standardize=True | A |
| A1|F2|rule_table | v3_A1_F2_rule_table_00148 | 2205 | 175 | 2226 | 1112 | 50.0% | 88 | 0 | 0.503 | mean_return_threshold=0.0; min_cell_n=5 | Fail |
| A1|F3|gbdt | v3_A1_F3_gbdt_00372 | 2205 | 175 | 2226 | 145 | 6.5% | 74 | 0 | 0.423 | threshold=0.6; max_depth=3; learning_rate=0.05; max_iter=50; min_samples_leaf=20; seed=42 | 紅線 4 停止判定／ValueError |
| A1|F3|logistic | v3_A1_F3_logistic_00323 | 2205 | 175 | 2226 | 415 | 18.6% | 161 | 0 | 0.920 | threshold=0.55; C=10.0; class_weight=none; max_iter=5000; seed=42; standardize=True | A |
| A1|F3|rule_table | v3_A1_F3_rule_table_00297 | 2205 | 175 | 2226 | 477 | 21.4% | 178 | 0 | 1.017 | mean_return_threshold=0.001; min_cell_n=5 | Fail |
| A1|F4|gbdt | v3_A1_F4_gbdt_00501 | 2205 | 175 | 2226 | 150 | 6.7% | 88 | 0 | 0.503 | threshold=0.6; max_depth=2; learning_rate=0.1; max_iter=50; min_samples_leaf=20; seed=42 | A |
| A1|F4|logistic | v3_A1_F4_logistic_00456 | 2205 | 175 | 2226 | 82 | 3.7% | 51 | 0 | 0.291 | threshold=0.6; C=0.01; class_weight=balanced; max_iter=5000; seed=42; standardize=True | Fail |
| A1|F4|rule_table | v3_A1_F4_rule_table_00443 | 2205 | 175 | 2226 | 249 | 11.2% | 100 | 0 | 0.571 | mean_return_threshold=0.0005; min_cell_n=5 | Fail |
| A1|F5|gbdt | v3_A1_F5_gbdt_00651 | 2206 | 175 | 2226 | 218 | 9.8% | 88 | 0 | 0.503 | threshold=0.6; max_depth=2; learning_rate=0.1; max_iter=50; min_samples_leaf=50; seed=42 | A |
| A1|F5|logistic | v3_A1_F5_logistic_00621 | 2206 | 175 | 2226 | 574 | 25.8% | 133 | 0 | 0.760 | threshold=0.6; C=10.0; class_weight=balanced; max_iter=5000; seed=42; standardize=True | Fail |
| A1|F5|rule_table | v3_A1_F5_rule_table_00591 | 2206 | 175 | 2226 | 568 | 25.5% | 121 | 0 | 0.691 | mean_return_threshold=0.001; min_cell_n=5 | Fail |
| A1B|F1|gbdt | v3_A1B_F1_gbdt_00777 | 2205 | 175 | 3295 | 572 | 17.4% | 133 | 3 | 0.760 | threshold=0.6; max_depth=2; learning_rate=0.05; max_iter=50; min_samples_leaf=20; seed=42 | B |
| A1B|F1|logistic | v3_A1B_F1_logistic_00765 | 2205 | 175 | 3295 | 339 | 10.3% | 33 | 0 | 0.189 | threshold=0.6; C=10.0; class_weight=none; max_iter=5000; seed=42; standardize=True | Fail |
| A1B|F1|rule_table | v3_A1B_F1_rule_table_00736 | 2205 | 175 | 3295 | 1655 | 50.2% | 87 | 0 | 0.497 | mean_return_threshold=0.0; min_cell_n=5 | Fail |
| A1B|F2|gbdt | v3_A1B_F2_gbdt_00927 | 2205 | 175 | 2226 | 461 | 20.7% | 126 | 5 | 0.720 | threshold=0.6; max_depth=2; learning_rate=0.05; max_iter=50; min_samples_leaf=50; seed=42 | Fail |
| A1B|F2|logistic | v3_A1B_F2_logistic_00894 | 2205 | 175 | 2226 | 392 | 17.6% | 88 | 5 | 0.503 | threshold=0.6; C=0.01; class_weight=none; max_iter=5000; seed=42; standardize=True | Fail |
| A1B|F2|rule_table | v3_A1B_F2_rule_table_00883 | 2205 | 175 | 2226 | 1114 | 50.0% | 87 | 0 | 0.497 | mean_return_threshold=0.0; min_cell_n=5 | Fail |
| A1B|F3|gbdt | v3_A1B_F3_gbdt_01113 | 2205 | 175 | 2226 | 955 | 42.9% | 248 | 2 | 1.417 | threshold=0.6; max_depth=3; learning_rate=0.05; max_iter=100; min_samples_leaf=20; seed=42 | Fail |
| A1B|F3|logistic | v3_A1B_F3_logistic_01044 | 2205 | 175 | 2226 | 268 | 12.0% | 108 | 5 | 0.617 | threshold=0.6; C=0.01; class_weight=balanced; max_iter=5000; seed=42; standardize=True | Fail |
| A1B|F3|rule_table | v3_A1B_F3_rule_table_01030 | 2205 | 175 | 2226 | 1749 | 78.6% | 274 | 0 | 1.566 | mean_return_threshold=0.0; min_cell_n=5 | Fail |
| A1B|F4|gbdt | v3_A1B_F4_gbdt_01263 | 2205 | 175 | 2226 | 365 | 16.4% | 170 | 3 | 0.971 | threshold=0.6; max_depth=3; learning_rate=0.05; max_iter=100; min_samples_leaf=50; seed=42 | Fail |
| A1B|F4|logistic | v3_A1B_F4_logistic_01200 | 2205 | 175 | 2226 | 372 | 16.7% | 190 | 8 | 1.086 | threshold=0.6; C=1.0; class_weight=none; max_iter=5000; seed=42; standardize=True | Fail |
| A1B|F4|rule_table | v3_A1B_F4_rule_table_01179 | 2205 | 175 | 2226 | 553 | 24.8% | 195 | 3 | 1.114 | mean_return_threshold=0.001; min_cell_n=5 | Fail |
| A1B|F5|gbdt | v3_A1B_F5_gbdt_01383 | 2206 | 175 | 2226 | 645 | 29.0% | 184 | 4 | 1.051 | threshold=0.6; max_depth=2; learning_rate=0.1; max_iter=50; min_samples_leaf=20; seed=42 | Fail |
| A1B|F5|logistic | v3_A1B_F5_logistic_01335 | 2206 | 175 | 2226 | 577 | 25.9% | 99 | 3 | 0.566 | threshold=0.6; C=0.01; class_weight=none; max_iter=5000; seed=42; standardize=True | A |
| A1B|F5|rule_table | v3_A1B_F5_rule_table_01326 | 2206 | 175 | 2226 | 767 | 34.5% | 135 | 3 | 0.771 | mean_return_threshold=0.001; min_cell_n=5 | Fail |
| A2|F1|gbdt | v3_A2_F1_gbdt_01514 | 2508 | 189 | 3649 | 831 | 22.8% | 218 | 0 | 1.153 | threshold=0.55; max_depth=2; learning_rate=0.05; max_iter=50; min_samples_leaf=50; seed=42 | Fail |
| A2|F1|logistic | v3_A2_F1_logistic_01488 | 2508 | 189 | 3649 | 20 | 0.5% | 4 | 0 | 0.021 | threshold=0.6; C=0.1; class_weight=none; max_iter=5000; seed=42; standardize=True | 紅線 4 停止判定／ValueError |
| A2|F1|rule_table | v3_A2_F1_rule_table_01471 | 2508 | 189 | 3649 | 1844 | 50.5% | 95 | 0 | 0.503 | mean_return_threshold=0.0; min_cell_n=5 | Fail |
| A2|F2|gbdt | v3_A2_F2_gbdt_01658 | 2508 | 189 | 2529 | 247 | 9.8% | 118 | 0 | 0.624 | threshold=0.55; max_depth=2; learning_rate=0.05; max_iter=50; min_samples_leaf=20; seed=42 | A |
| A2|F2|logistic | v3_A2_F2_logistic_01632 | 2508 | 189 | 2529 | 64 | 2.5% | 30 | 0 | 0.159 | threshold=0.6; C=0.01; class_weight=balanced; max_iter=5000; seed=42; standardize=True | A |
| A2|F2|rule_table | v3_A2_F2_rule_table_01618 | 2508 | 189 | 2529 | 1335 | 52.8% | 104 | 0 | 0.550 | mean_return_threshold=0.0; min_cell_n=5 | Fail |
| A2|F3|gbdt | v3_A2_F3_gbdt_01823 | 2508 | 189 | 2529 | 394 | 15.6% | 166 | 0 | 0.878 | threshold=0.55; max_depth=2; learning_rate=0.1; max_iter=50; min_samples_leaf=20; seed=42 | A |
| A2|F3|logistic | v3_A2_F3_logistic_01785 | 2508 | 189 | 2529 | 148 | 5.9% | 94 | 0 | 0.497 | threshold=0.6; C=0.1; class_weight=balanced; max_iter=5000; seed=42; standardize=True | A |
| A2|F3|rule_table | v3_A2_F3_rule_table_01767 | 2508 | 189 | 2529 | 531 | 21.0% | 198 | 0 | 1.048 | mean_return_threshold=0.001; min_cell_n=5 | Fail |
| A2|F4|gbdt | v3_A2_F4_gbdt_02046 | 2508 | 189 | 2529 | 362 | 14.3% | 207 | 2 | 1.095 | threshold=0.6; max_depth=4; learning_rate=0.1; max_iter=50; min_samples_leaf=50; seed=42 | Fail |
| A2|F4|logistic | v3_A2_F4_logistic_01926 | 2508 | 189 | 2529 | 82 | 3.2% | 52 | 0 | 0.275 | threshold=0.6; C=0.01; class_weight=balanced; max_iter=5000; seed=42; standardize=True | B |
| A2|F4|rule_table | v3_A2_F4_rule_table_01913 | 2508 | 189 | 2529 | 531 | 21.0% | 198 | 0 | 1.048 | mean_return_threshold=0.0005; min_cell_n=5 | Fail |
| A2|F5|gbdt | v3_A2_F5_gbdt_02121 | 2509 | 189 | 2529 | 174 | 6.9% | 85 | 0 | 0.450 | threshold=0.6; max_depth=2; learning_rate=0.1; max_iter=50; min_samples_leaf=50; seed=42 | Fail |
| A2|F5|logistic | v3_A2_F5_logistic_02090 | 2509 | 189 | 2529 | 758 | 30.0% | 105 | 0 | 0.556 | threshold=0.55; C=10.0; class_weight=balanced; max_iter=5000; seed=42; standardize=True | B |
| A2|F5|rule_table | v3_A2_F5_rule_table_02061 | 2509 | 189 | 2529 | 365 | 14.4% | 107 | 0 | 0.566 | mean_return_threshold=0.001; min_cell_n=5 | Fail |
| A2B|F1|gbdt | v3_A2B_F1_gbdt_02256 | 2508 | 189 | 3649 | 717 | 19.6% | 187 | 4 | 0.989 | threshold=0.6; max_depth=2; learning_rate=0.05; max_iter=100; min_samples_leaf=50; seed=42 | Fail |
| A2B|F1|logistic | v3_A2B_F1_logistic_02235 | 2508 | 189 | 3649 | 283 | 7.8% | 49 | 0 | 0.259 | threshold=0.6; C=10.0; class_weight=none; max_iter=5000; seed=42; standardize=True | Fail |
| A2B|F1|rule_table | v3_A2B_F1_rule_table_02206 | 2508 | 189 | 3649 | 1805 | 49.5% | 94 | 0 | 0.497 | mean_return_threshold=0.0; min_cell_n=5 | Fail |
| A2B|F2|gbdt | v3_A2B_F2_gbdt_02397 | 2508 | 189 | 2529 | 295 | 11.7% | 163 | 3 | 0.862 | threshold=0.6; max_depth=2; learning_rate=0.05; max_iter=50; min_samples_leaf=50; seed=42 | B |
| A2B|F2|logistic | v3_A2B_F2_logistic_02373 | 2508 | 189 | 2529 | 321 | 12.7% | 81 | 5 | 0.429 | threshold=0.6; C=0.1; class_weight=balanced; max_iter=5000; seed=42; standardize=True | Fail |
| A2B|F2|rule_table | v3_A2B_F2_rule_table_02353 | 2508 | 189 | 2529 | 1194 | 47.2% | 88 | 0 | 0.466 | mean_return_threshold=0.0; min_cell_n=5 | Fail |
| A2B|F3|gbdt | v3_A2B_F3_gbdt_02598 | 2508 | 189 | 2529 | 615 | 24.3% | 251 | 7 | 1.328 | threshold=0.6; max_depth=3; learning_rate=0.1; max_iter=50; min_samples_leaf=50; seed=42 | Fail |
| A2B|F3|logistic | v3_A2B_F3_logistic_02520 | 2508 | 189 | 2529 | 375 | 14.8% | 185 | 5 | 0.979 | threshold=0.6; C=0.1; class_weight=balanced; max_iter=5000; seed=42; standardize=True | Fail |
| A2B|F3|rule_table | v3_A2B_F3_rule_table_02500 | 2508 | 189 | 2529 | 1633 | 64.6% | 219 | 0 | 1.159 | mean_return_threshold=0.0; min_cell_n=5 | Fail |
| A2B|F4|gbdt | v3_A2B_F4_gbdt_02733 | 2508 | 189 | 2529 | 271 | 10.7% | 134 | 0 | 0.709 | threshold=0.6; max_depth=3; learning_rate=0.05; max_iter=100; min_samples_leaf=50; seed=42 | Fail |
| A2B|F4|logistic | v3_A2B_F4_logistic_02658 | 2508 | 189 | 2529 | 116 | 4.6% | 76 | 1 | 0.402 | threshold=0.6; C=0.01; class_weight=none; max_iter=5000; seed=42; standardize=True | Fail |
| A2B|F4|rule_table | v3_A2B_F4_rule_table_02648 | 2508 | 189 | 2529 | 1231 | 48.7% | 275 | 3 | 1.455 | mean_return_threshold=0.0005; min_cell_n=5 | Fail |
| A2B|F5|gbdt | v3_A2B_F5_gbdt_02835 | 2509 | 189 | 2529 | 538 | 21.3% | 107 | 0 | 0.566 | threshold=0.6; max_depth=2; learning_rate=0.05; max_iter=50; min_samples_leaf=20; seed=42 | Fail |
| A2B|F5|logistic | v3_A2B_F5_logistic_02805 | 2509 | 189 | 2529 | 615 | 24.3% | 114 | 0 | 0.603 | threshold=0.6; C=0.01; class_weight=none; max_iter=5000; seed=42; standardize=True | Fail |
| A2B|F5|rule_table | v3_A2B_F5_rule_table_02796 | 2509 | 189 | 2529 | 859 | 34.0% | 150 | 3 | 0.794 | mean_return_threshold=0.001; min_cell_n=5 | Fail |
| A3|F1|gbdt | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3|F1|logistic | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3|F1|rule_table | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3|F2|gbdt | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3|F2|logistic | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3|F2|rule_table | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3|F3|gbdt | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3|F3|logistic | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3|F3|rule_table | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3|F4|gbdt | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3|F4|logistic | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3|F4|rule_table | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3|F5|gbdt | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3|F5|logistic | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3|F5|rule_table | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3B|F1|gbdt | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3B|F1|logistic | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3B|F1|rule_table | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3B|F2|gbdt | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3B|F2|logistic | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3B|F2|rule_table | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3B|F3|gbdt | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3B|F3|logistic | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3B|F3|rule_table | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3B|F4|gbdt | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3B|F4|logistic | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3B|F4|rule_table | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3B|F5|gbdt | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3B|F5|logistic | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3B|F5|rule_table | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |

## 第二輪 60 格（40 格有 rank-1；20 格 A3／A3B 無合格 rank-1）

- 研究分級（有 rank-1 的 40 格）：A 2／B 0／Fail 23／紅線 4 停止判定／ValueError 15。
- 十年交易：最少 0、中位數 131、最多 419；**2 格 ≥300**（見結論第 5 點），皆 Fail。二考 ≥5 共 4 格，皆 Fail。
- 樣本接受率中位數：HMM 50.0%、RL 16.7%。HMM 有 2 格接受率 100%（A2B|F3|hmm、A2B|F5|hmm），十年交易＝底層 189。RL／HMM 各有格子 `n_take`＝0：A1B|F3|rl、A2|F1|rl、A2|F5|hmm（十年 0 筆，停止判定）。
- 選中參數：達到 ≥300 的兩格都是 HMM `n_states=3`、`mean_return_threshold=0.0`、`min_state_n=10`。其餘 HMM rank-1 以 `n_states=4`（11 格）或 `2`（7 格）為主。RL 進場門檻 0.0005 與 0.001 各 8 格、0.0 共 4 格。

| 格 | trial_id | 底層十年訊號 | 底層十年交易 | n_finite | n_take | 樣本接受率 | 模型十年交易 | 二考交易 | 交易比 | 選中門檻／參數 | 研究分級 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| A1|F1|hmm | v4_A1_F1_hmm_00001 | 2205 | 175 | 3295 | 1641 | 49.8% | 88 | 0 | 0.503 | mean_return_threshold=0.0; min_state_n=10; n_states=2; covariance_type=diag; n_iter_max=200; tol=0.0001; seed=42 | Fail |
| A1|F1|rl | v4_A1_F1_rl_00044 | 2205 | 175 | 3295 | 8 | 0.2% | 1 | 0 | 0.006 | threshold=0.0005; alpha=0.1; epsilon=0.05; l2=0.0; n_epochs=1; min_updates=30; seed=42 | 紅線 4 停止判定／ValueError |
| A1|F2|hmm | v4_A1_F2_hmm_00067 | 2205 | 175 | 2226 | 454 | 20.4% | 40 | 0 | 0.229 | mean_return_threshold=0.0; min_state_n=10; n_states=4; covariance_type=diag; n_iter_max=200; tol=0.0001; seed=42 | 紅線 4 停止判定／ValueError |
| A1|F2|rl | v4_A1_F2_rl_00083 | 2205 | 175 | 2226 | 2 | 0.1% | 2 | 0 | 0.011 | threshold=0.0005; alpha=0.01; epsilon=0.1; l2=1.0; n_epochs=1; min_updates=30; seed=42 | 紅線 4 停止判定／ValueError |
| A1|F3|hmm | v4_A1_F3_hmm_00122 | 2205 | 175 | 2226 | 483 | 21.7% | 191 | 3 | 1.091 | mean_return_threshold=0.0005; min_state_n=10; n_states=4; covariance_type=diag; n_iter_max=200; tol=0.0001; seed=42 | Fail |
| A1|F3|rl | v4_A1_F3_rl_00158 | 2205 | 175 | 2226 | 802 | 36.0% | 114 | 0 | 0.651 | threshold=0.0005; alpha=0.1; epsilon=0.1; l2=0.0; n_epochs=1; min_updates=30; seed=42 | 紅線 4 停止判定／ValueError |
| A1|F4|hmm | v4_A1_F4_hmm_00176 | 2205 | 175 | 2226 | 483 | 21.7% | 191 | 3 | 1.091 | mean_return_threshold=0.0005; min_state_n=10; n_states=4; covariance_type=diag; n_iter_max=200; tol=0.0001; seed=42 | Fail |
| A1|F4|rl | v4_A1_F4_rl_00195 | 2205 | 175 | 2226 | 450 | 20.2% | 139 | 0 | 0.794 | threshold=0.001; alpha=0.05; epsilon=0.05; l2=0.0; n_epochs=1; min_updates=30; seed=42 | Fail |
| A1|F5|hmm | v4_A1_F5_hmm_00229 | 2206 | 175 | 2226 | 483 | 21.7% | 191 | 3 | 1.091 | mean_return_threshold=0.0; min_state_n=10; n_states=4; covariance_type=diag; n_iter_max=200; tol=0.0001; seed=42 | Fail |
| A1|F5|rl | v4_A1_F5_rl_00243 | 2206 | 175 | 2226 | 392 | 17.6% | 147 | 0 | 0.840 | threshold=0.001; alpha=0.01; epsilon=0.1; l2=0.0; n_epochs=1; min_updates=30; seed=42 | 紅線 4 停止判定／ValueError |
| A1B|F1|hmm | v4_A1B_F1_hmm_00271 | 2205 | 175 | 3295 | 1654 | 50.2% | 87 | 0 | 0.497 | mean_return_threshold=0.0; min_state_n=10; n_states=2; covariance_type=diag; n_iter_max=200; tol=0.0001; seed=42 | Fail |
| A1B|F1|rl | v4_A1B_F1_rl_00322 | 2205 | 175 | 3295 | 155 | 4.7% | 52 | 0 | 0.297 | threshold=0.0; alpha=0.1; epsilon=0.1; l2=1.0; n_epochs=1; min_updates=30; seed=42 | Fail |
| A1B|F2|hmm | v4_A1B_F2_hmm_00337 | 2205 | 175 | 2226 | 1772 | 79.6% | 135 | 0 | 0.771 | mean_return_threshold=0.0; min_state_n=10; n_states=4; covariance_type=diag; n_iter_max=200; tol=0.0001; seed=42 | Fail |
| A1B|F2|rl | v4_A1B_F2_rl_00362 | 2205 | 175 | 2226 | 760 | 34.1% | 183 | 0 | 1.046 | threshold=0.0005; alpha=0.05; epsilon=0.1; l2=0.0; n_epochs=1; min_updates=30; seed=42 | A |
| A1B|F3|hmm | v4_A1B_F3_hmm_00385 | 2205 | 175 | 2226 | 1278 | 57.4% | 371 | 5 | 2.120 | mean_return_threshold=0.0; min_state_n=10; n_states=3; covariance_type=diag; n_iter_max=200; tol=0.0001; seed=42 | Fail |
| A1B|F3|rl | v4_A1B_F3_rl_00419 | 2205 | 175 | 2226 | 0 | 0.0% | 0 | 0 | 0.000 | threshold=0.0005; alpha=0.05; epsilon=0.1; l2=1.0; n_epochs=1; min_updates=30; seed=42 | 紅線 4 停止判定／ValueError |
| A1B|F4|hmm | v4_A1B_F4_hmm_00445 | 2205 | 175 | 2226 | 1743 | 78.3% | 289 | 3 | 1.651 | mean_return_threshold=0.0; min_state_n=10; n_states=4; covariance_type=diag; n_iter_max=200; tol=0.0001; seed=42 | Fail |
| A1B|F4|rl | v4_A1B_F4_rl_00469 | 2205 | 175 | 2226 | 353 | 15.9% | 77 | 0 | 0.440 | threshold=0.0; alpha=0.05; epsilon=0.1; l2=0.0; n_epochs=1; min_updates=30; seed=42 | Fail |
| A1B|F5|hmm | v4_A1B_F5_hmm_00499 | 2206 | 175 | 2226 | 1743 | 78.3% | 289 | 3 | 1.651 | mean_return_threshold=0.0; min_state_n=10; n_states=4; covariance_type=diag; n_iter_max=200; tol=0.0001; seed=42 | Fail |
| A1B|F5|rl | v4_A1B_F5_rl_00525 | 2206 | 175 | 2226 | 590 | 26.5% | 127 | 0 | 0.726 | threshold=0.001; alpha=0.05; epsilon=0.1; l2=0.0; n_epochs=1; min_updates=30; seed=42 | 紅線 4 停止判定／ValueError |
| A2|F1|hmm | v4_A2_F1_hmm_00541 | 2508 | 189 | 3649 | 1845 | 50.6% | 95 | 0 | 0.503 | mean_return_threshold=0.0; min_state_n=10; n_states=2; covariance_type=diag; n_iter_max=200; tol=0.0001; seed=42 | Fail |
| A2|F1|rl | v4_A2_F1_rl_00579 | 2508 | 189 | 3649 | 0 | 0.0% | 0 | 0 | 0.000 | threshold=0.001; alpha=0.05; epsilon=0.1; l2=0.0; n_epochs=1; min_updates=30; seed=42 | 紅線 4 停止判定／ValueError |
| A2|F2|hmm | v4_A2_F2_hmm_00608 | 2508 | 189 | 2529 | 454 | 18.0% | 40 | 0 | 0.212 | mean_return_threshold=0.0005; min_state_n=10; n_states=4; covariance_type=diag; n_iter_max=200; tol=0.0001; seed=42 | 紅線 4 停止判定／ValueError |
| A2|F2|rl | v4_A2_F2_rl_00624 | 2508 | 189 | 2529 | 82 | 3.2% | 67 | 0 | 0.354 | threshold=0.001; alpha=0.01; epsilon=0.1; l2=1.0; n_epochs=1; min_updates=30; seed=42 | A |
| A2|F3|hmm | v4_A2_F3_hmm_00662 | 2508 | 189 | 2529 | 521 | 20.6% | 211 | 3 | 1.116 | mean_return_threshold=0.0005; min_state_n=10; n_states=4; covariance_type=diag; n_iter_max=200; tol=0.0001; seed=42 | Fail |
| A2|F3|rl | v4_A2_F3_rl_00677 | 2508 | 189 | 2529 | 208 | 8.2% | 110 | 5 | 0.582 | threshold=0.0005; alpha=0.01; epsilon=0.1; l2=1.0; n_epochs=1; min_updates=30; seed=42 | Fail |
| A2|F4|hmm | v4_A2_F4_hmm_00716 | 2508 | 189 | 2529 | 521 | 20.6% | 211 | 3 | 1.116 | mean_return_threshold=0.0005; min_state_n=10; n_states=4; covariance_type=diag; n_iter_max=200; tol=0.0001; seed=42 | Fail |
| A2|F4|rl | v4_A2_F4_rl_00746 | 2508 | 189 | 2529 | 838 | 33.1% | 142 | 0 | 0.751 | threshold=0.0005; alpha=0.1; epsilon=0.05; l2=0.0; n_epochs=1; min_updates=30; seed=42 | Fail |
| A2|F5|hmm | v4_A2_F5_hmm_00757 | 2509 | 189 | 2529 | 0 | 0.0% | 0 | 0 | 0.000 | mean_return_threshold=0.0; min_state_n=10; n_states=2; covariance_type=diag; n_iter_max=200; tol=0.0001; seed=42 | 紅線 4 停止判定／ValueError |
| A2|F5|rl | v4_A2_F5_rl_00809 | 2509 | 189 | 2529 | 748 | 29.6% | 174 | 0 | 0.921 | threshold=0.0005; alpha=0.1; epsilon=0.1; l2=1.0; n_epochs=1; min_updates=30; seed=42 | 紅線 4 停止判定／ValueError |
| A2B|F1|hmm | v4_A2B_F1_hmm_00811 | 2508 | 189 | 3649 | 1804 | 49.4% | 94 | 0 | 0.497 | mean_return_threshold=0.0; min_state_n=10; n_states=2; covariance_type=diag; n_iter_max=200; tol=0.0001; seed=42 | Fail |
| A2B|F1|rl | v4_A2B_F1_rl_00859 | 2508 | 189 | 3649 | 464 | 12.7% | 173 | 9 | 0.915 | threshold=0.0; alpha=0.1; epsilon=0.1; l2=0.0; n_epochs=1; min_updates=30; seed=42 | Fail |
| A2B|F2|hmm | v4_A2B_F2_hmm_00880 | 2508 | 189 | 2529 | 1827 | 72.2% | 135 | 0 | 0.714 | mean_return_threshold=0.0; min_state_n=30; n_states=4; covariance_type=diag; n_iter_max=200; tol=0.0001; seed=42 | Fail |
| A2B|F2|rl | v4_A2B_F2_rl_00900 | 2508 | 189 | 2529 | 526 | 20.8% | 67 | 0 | 0.354 | threshold=0.001; alpha=0.05; epsilon=0.05; l2=1.0; n_epochs=1; min_updates=30; seed=42 | 紅線 4 停止判定／ValueError |
| A2B|F3|hmm | v4_A2B_F3_hmm_00919 | 2508 | 189 | 2529 | 2529 | 100.0% | 189 | 0 | 1.000 | mean_return_threshold=0.0; min_state_n=10; n_states=2; covariance_type=diag; n_iter_max=200; tol=0.0001; seed=42 | Fail |
| A2B|F3|rl | v4_A2B_F3_rl_00957 | 2508 | 189 | 2529 | 929 | 36.7% | 95 | 0 | 0.503 | threshold=0.001; alpha=0.05; epsilon=0.1; l2=0.0; n_epochs=1; min_updates=30; seed=42 | 紅線 4 停止判定／ValueError |
| A2B|F4|hmm | v4_A2B_F4_hmm_00979 | 2508 | 189 | 2529 | 1482 | 58.6% | 419 | 5 | 2.217 | mean_return_threshold=0.0; min_state_n=10; n_states=3; covariance_type=diag; n_iter_max=200; tol=0.0001; seed=42 | Fail |
| A2B|F4|rl | v4_A2B_F4_rl_01021 | 2508 | 189 | 2529 | 853 | 33.7% | 136 | 0 | 0.720 | threshold=0.0; alpha=0.1; epsilon=0.1; l2=0.0; n_epochs=1; min_updates=30; seed=42 | 紅線 4 停止判定／ValueError |
| A2B|F5|hmm | v4_A2B_F5_hmm_01027 | 2509 | 189 | 2529 | 2529 | 100.0% | 189 | 0 | 1.000 | mean_return_threshold=0.0; min_state_n=10; n_states=2; covariance_type=diag; n_iter_max=200; tol=0.0001; seed=42 | Fail |
| A2B|F5|rl | v4_A2B_F5_rl_01056 | 2509 | 189 | 2529 | 166 | 6.6% | 59 | 0 | 0.312 | threshold=0.001; alpha=0.01; epsilon=0.1; l2=1.0; n_epochs=1; min_updates=30; seed=42 | 紅線 4 停止判定／ValueError |
| A3|F1|hmm | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3|F1|rl | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3|F2|hmm | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3|F2|rl | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3|F3|hmm | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3|F3|rl | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3|F4|hmm | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3|F4|rl | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3|F5|hmm | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3|F5|rl | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3B|F1|hmm | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3B|F1|rl | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3B|F2|hmm | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3B|F2|rl | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3B|F3|hmm | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3B|F3|rl | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3B|F4|hmm | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3B|F4|rl | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3B|F5|hmm | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |
| A3B|F5|rl | — | 223 | 16 | — | — | — | — | — | — | — | 無合格 rank-1 |

## 輸入雜湊

| 檔案 | 說明 | sha1 |
|---|---|---|
| `/workspace/ml_meta/official_v1/SUMMARY.csv` | 官方路徑彙整 CSV | `8bc42da2e7be0a3bcc114e052f230a4013d6f977` |
| `/workspace/ml_meta/official_v1/SUMMARY.md` | 官方路徑彙整 MD | `c094f151c8a8d41f5dc6258a0b3ed7d775d496f8` |
| `/workspace/ml_meta/round1_run/stageA/summary.csv` | 第一輪階段 A 彙整 | `14734b4a7ec57b8f34461a2152b646298e23ddd2` |
| `/workspace/ml_meta/round2_run/stageA_v2/summary.csv` | 第二輪階段 A（v2）彙整 | `c1dc06cf3ff44d91d537251809974b43b3cf947f` |
| `/workspace/ml_meta/round2_run/SUMMARY_v1.md` | 第二輪結果彙整 | `a973aec97b0e27477032e411ae2d10619f87523b` |
| `/workspace/ml_meta/features_v3/samples_all.csv` | 特徵樣本（底層訊號筆數） | `013ff1e333248561f76e38a3f3f1b876e33e13f5` |
| `/workspace/ml_meta/freeze/windows_v2.json` | 官方窗口 | `6672824bd0fb5ec953d95957fbed6425555a44da` |
| `/workspace/ml_meta/baselines/front7_table.csv` | 前七年基準表（核對 front7 筆數） | `77f853026b1699e2924cfce0b8e1295c57fe92d7` |
| `/workspace/ml_meta/baselines/front7_baselines.json` | 前七年基準 JSON | `ca02fc4df9d0d3cf8025a8bbf4eb1c5ba16adf0a` |
| `/workspace/ml_meta/baselines/ledger_PCR_ONLY.csv` | PCR_ONLY 1 分 K 帳本 | `9394899f4cd63292967edea9f207499ca388c4ab` |
| `/workspace/ml_meta/baselines/ledger_A1.csv` | A1 1 分 K 帳本 | `04f57be45817814109500054f80016fc6bb8abb8` |
| `/workspace/ml_meta/baselines/ledger_A1B.csv` | A1B 1 分 K 帳本 | `a85aa7671d7d47d1fce1076b82d739bd79d26cfd` |
| `/workspace/ml_meta/baselines/ledger_A2.csv` | A2 1 分 K 帳本 | `e3a9b2f5958c2c7cb58b542da54837c1244f6182` |
| `/workspace/ml_meta/baselines/ledger_A2B.csv` | A2B 1 分 K 帳本 | `2d960560a88d58eb8f7d843487e9d21d026e2ebb` |
| `/workspace/ml_meta/baselines/ledger_A3.csv` | A3 1 分 K 帳本 | `46581255e37e1496751220fd8f912bc870f76fa1` |
| `/workspace/ml_meta/baselines/ledger_A3B.csv` | A3B 1 分 K 帳本 | `48147c8750e5e44ec461facdbb566044d5153a9a` |
| `/workspace/ml_meta/e2e_tick_v3/baseline_evidence.json` | PCR_ONLY tick 基準證據（核對十年 191／二考 0） | `d572cd05aa13000ffbc30bca87c0c6b7dc837873` |
| 第一輪／第二輪階段 A metrics JSON 共 150 份 | 每格 `n_take`、十年／二考、參數、研究分級 | 逐檔 sha1 見同目錄 CSV 的 `metrics_sha1` 欄 |

完整逐格欄位（含 `metrics_sha1`、官方結論、底層帳本 sha1）見同目錄 `DIAG_TRADECOUNT_v1.csv`。
