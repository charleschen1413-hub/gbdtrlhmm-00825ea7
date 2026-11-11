# 來源快照：`/workspace/ml_meta/round1_run/stageA/summary.csv`

- **探索性、非獨立盲測；非官方驗收**
- 來源路徑：`/workspace/ml_meta/round1_run/stageA/summary.csv`
- sha1：`14734b4a7ec57b8f34461a2152b646298e23ddd2`
- 快照時間：2026-11-11 22:48（台北時間）
- 本頁只轉述來源文件已有的內容，不自行推論或加數字。

---

| cell | trial_id | skip | n_completed | front7_n | back3_n | research_grade | ledger_sha1 | sec |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1B\|F1\|rule_table | v3_A1B_F1_rule_table_00736 | False | 142.0 | 54.0 | 33.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | b04ee2cdc277d252f874d42f6c3e7cf17da53e2c | 0.8168160689965589 |
| A1B\|F2\|rule_table | v3_A1B_F2_rule_table_00883 | False | 87.0 | 54.0 | 33.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | 5a804cbe24ff45f48399766713f5d69c7762c975 | 0.4325233470008243 |
| A1B\|F1\|logistic | v3_A1B_F1_logistic_00765 | False | 50.0 | 16.0 | 17.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | 548c7175ef40c7095f0b92547bbe00597f87414f | 1.351768437998544 |
| A1B\|F2\|logistic | v3_A1B_F2_logistic_00894 | False | 88.0 | 20.0 | 68.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | 33ad39d4f3db6436f5583e63a0441b7ece0bed60 | 3.233896892001212 |
| A1B\|F1\|gbdt | v3_A1B_F1_gbdt_00777 | False | 206.0 | 81.0 | 52.0 | {'research_tier': 'B', 'reason': 'not A, but trim_pf>1.03 and mc95<48000', 'judgment_stopped': False} | fb0de94a20148d26730b7fc9bcf2b1f97c85a89c | 5.467844667000463 |
| A1B\|F2\|gbdt | v3_A1B_F2_gbdt_00927 | False | 126.0 | 85.0 | 41.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | f7051b0237c9fe732f36516a0fd21c5b74c984d5 | 3.901511746000324 |
| A1B\|F3\|logistic | v3_A1B_F3_logistic_01044 | False | 108.0 | 38.0 | 70.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | c416470e5971c10a8e2bee03475547b9c6386eeb | 5.041924243996618 |
| A1B\|F3\|rule_table | v3_A1B_F3_rule_table_01030 | False | 277.0 | 173.0 | 101.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | 9053e86e58d02f7db0ab39853ac7e450f5ec4be9 | 8.845024797003134 |
| A1B\|F4\|rule_table | v3_A1B_F4_rule_table_01179 | False | 197.0 | 125.0 | 70.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | 8a5bc2f6d8ad634fd3ce70d0270e0c3a0aff8068 | 3.0414340179995634 |
| A1B\|F4\|logistic | v3_A1B_F4_logistic_01200 | False | 190.0 | 113.0 | 77.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | afa86b4a6e6340818506bc89e647a9cf6714e817 | 3.50793104100012 |
| A1B\|F3\|gbdt | v3_A1B_F3_gbdt_01113 | False | 250.0 | 147.0 | 101.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | 2053afe5cd209dafe97630df8aa22995281f3327 | 3.7982762640021974 |
| A1B\|F5\|logistic | v3_A1B_F5_logistic_01335 | False | 99.0 | 68.0 | 31.0 | {'research_tier': 'A', 'reason': 'trim_pf>1.10 and mc95<35000', 'judgment_stopped': False} | 85f2326404a2aaa81ac8be96502a8698430a95cc | 1.1548829479943379 |
| A1B\|F5\|rule_table | v3_A1B_F5_rule_table_01326 | False | 135.0 | 87.0 | 48.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | 10c951c25d76f419d678d88cae8863f4bf5c7cfb | 1.2492995889988379 |
| A1\|F1\|logistic | v3_A1_F1_logistic_00018 | False | 4.0 | 4.0 | 0.0 | {'research_tier': None, 'reason': '紅線 4 停止判定／ValueError：後三年 Trim PF 或 MC95 不是有限值，不可記為研究 Fail', 'judgment_stopped': True, 'value_error': 'back3 Trim PF or MC95 is not a finite value; stop research-tier judgment (not a strategy Fail)'} | 92d12d4d712c08ed7c55bd7ceebdefc614d4091c | 0.13827278599637793 |
| A1\|F1\|rule_table | v3_A1_F1_rule_table_00001 | False | 144.0 | 54.0 | 34.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | 9485a3a5a6aef2080d61a08eac0c8b7f302eca4d | 0.37150817799556535 |
| A1\|F2\|rule_table | v3_A1_F2_rule_table_00148 | False | 88.0 | 54.0 | 34.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | 40f28bfa575f9fa08722b338b15e00d796b9b806 | 0.2593555670027854 |
| A1\|F3\|rule_table | v3_A1_F3_rule_table_00297 | False | 181.0 | 122.0 | 56.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | 11425393697184673f9c99c606497d32d9b35fa1 | 0.2793608139982098 |
| A1B\|F4\|gbdt | v3_A1B_F4_gbdt_01263 | False | 171.0 | 116.0 | 54.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | 89ee30b5466fbf83220789a3c5b7b6d3774e5ce0 | 2.2143533950002166 |
| A1\|F2\|logistic | v3_A1_F2_logistic_00175 | False | 107.0 | 66.0 | 41.0 | {'research_tier': 'A', 'reason': 'trim_pf>1.10 and mc95<35000', 'judgment_stopped': False} | dfdcda7a8c35231b87af5ee8a0a461c78817a094 | 1.651805877998413 |
| A1B\|F5\|gbdt | v3_A1B_F5_gbdt_01383 | False | 185.0 | 119.0 | 65.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | c90814ed777c1d16d00ea825e0e4f68211a571fb | 2.6443379030024516 |
| A1\|F4\|rule_table | v3_A1_F4_rule_table_00443 | False | 102.0 | 72.0 | 28.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | 4a7f6ae07fb97e7975ed889a9bccbb5951c5e7f6 | 2.80198557300173 |
| A1\|F3\|logistic | v3_A1_F3_logistic_00323 | False | 165.0 | 148.0 | 13.0 | {'research_tier': 'A', 'reason': 'trim_pf>1.10 and mc95<35000', 'judgment_stopped': False} | 2fede0aa646d5c8a6ab19ab514b9c3821c19bfa3 | 4.489292200996715 |
| A1\|F5\|rule_table | v3_A1_F5_rule_table_00591 | False | 122.0 | 80.0 | 41.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | 84785cd7328d072ecbfa7fb35689626984eae546 | 3.409320471000683 |
| A1\|F1\|gbdt | v3_A1_F1_gbdt_00051 | False | 157.0 | 64.0 | 36.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | 5dd868346adff3e4ac349fb619d9eea2c576212f | 3.515104557001905 |
| A2B\|F1\|rule_table | v3_A2B_F1_rule_table_02206 | False | 150.0 | 61.0 | 33.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | c221820d7a697a3a9d976ced63f16f45be115637 | 0.3064272800038452 |
| A1\|F4\|logistic | v3_A1_F4_logistic_00456 | False | 51.0 | 30.0 | 21.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | f51a61c3fc4eede63428bcbbf9f6d4019a3bbee1 | 1.476259380004194 |
| A2B\|F2\|rule_table | v3_A2B_F2_rule_table_02353 | False | 88.0 | 55.0 | 33.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | 50d26147a0cb6b2cd73b2b2a49052dc1223c93d6 | 0.3432292539946502 |
| A1\|F2\|gbdt | v3_A1_F2_gbdt_00207 | False | 62.0 | 57.0 | 4.0 | {'research_tier': 'A', 'reason': 'trim_pf>1.10 and mc95<35000', 'judgment_stopped': False} | ac6bf93a3e6e8e87b0679bec5d5319abc1107ccf | 0.6828372089948971 |
| A1\|F3\|gbdt | v3_A1_F3_gbdt_00372 | False | 75.0 | 73.0 | 1.0 | {'research_tier': None, 'reason': '紅線 4 停止判定／ValueError：後三年 Trim PF 或 MC95 不是有限值，不可記為研究 Fail', 'judgment_stopped': True, 'value_error': 'back3 Trim PF or MC95 is not a finite value; stop research-tier judgment (not a strategy Fail)'} | 9f572f8c2be5c4bc2f7d95fd8a7bf1ab6ed501bd | 1.9322422960030963 |
| A1\|F5\|logistic | v3_A1_F5_logistic_00621 | False | 136.0 | 86.0 | 47.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | 13a942a29d248843eb0b98093599829c2f40bb97 | 2.5326040020008804 |
| A2B\|F3\|rule_table | v3_A2B_F3_rule_table_02500 | False | 221.0 | 147.0 | 72.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | 339b435bc3d2196765cabdfe78d3a5db8941b447 | 2.4541045229998417 |
| A2B\|F1\|logistic | v3_A2B_F1_logistic_02235 | False | 63.0 | 24.0 | 25.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | 4ab47b86b5f1fc1e16a067dd37e793756dc1a0e0 | 0.5403295880023506 |
| A2B\|F2\|logistic | v3_A2B_F2_logistic_02373 | False | 81.0 | 13.0 | 68.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | f9eb39f31da1ae204c38b6ff467c449ad52e7d46 | 0.5496031069997116 |
| A1\|F4\|gbdt | v3_A1_F4_gbdt_00501 | False | 90.0 | 79.0 | 9.0 | {'research_tier': 'A', 'reason': 'trim_pf>1.10 and mc95<35000', 'judgment_stopped': False} | 78039d90d68e796be544605db89131ec49bc3069 | 1.6520548280022922 |
| A2B\|F4\|rule_table | v3_A2B_F4_rule_table_02648 | False | 277.0 | 188.0 | 87.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | ffed38ca16d64e8c1fe42c9c7351164431536e6d | 2.286115470000368 |
| A1\|F5\|gbdt | v3_A1_F5_gbdt_00651 | False | 93.0 | 80.0 | 8.0 | {'research_tier': 'A', 'reason': 'trim_pf>1.10 and mc95<35000', 'judgment_stopped': False} | 22c4a430a31b68280e79c7dc052fbd4a95903fcb | 1.1857265850048861 |
| A2B\|F3\|logistic | v3_A2B_F3_logistic_02520 | False | 185.0 | 93.0 | 92.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | 5e6f9d950bce72cb813671184fb5b93630c46b89 | 1.478498322001542 |
| A2B\|F5\|rule_table | v3_A2B_F5_rule_table_02796 | False | 150.0 | 102.0 | 48.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | 51f2eeed175b7e8c867a655df4acc0bb6d5fe952 | 0.5026239069993608 |
| A2\|F1\|rule_table | v3_A2_F1_rule_table_01471 | False | 150.0 | 61.0 | 34.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | fa10395361673276f8d6c7a6c9e1061cfb00b55d | 0.26864027800183976 |
| A2B\|F4\|logistic | v3_A2B_F4_logistic_02658 | False | 76.0 | 40.0 | 36.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | 1f8d9a951ef53a6fb967b1c418573eedf6e3f08b | 0.5882317909999983 |
| A2\|F2\|rule_table | v3_A2_F2_rule_table_01618 | False | 104.0 | 70.0 | 34.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | 0fbc891082528d1728f8298ff838d2d50243dfbe | 0.2597032539997599 |
| A2\|F3\|rule_table | v3_A2_F3_rule_table_01767 | False | 201.0 | 142.0 | 56.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | 221230e7453e21b07f90f00c7307a3cabc97c67f | 0.8699981770041632 |
| A2B\|F5\|logistic | v3_A2B_F5_logistic_02805 | False | 114.0 | 84.0 | 30.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | 1aab8f68adc014e487350672dce8c7849f942534 | 1.0807037519989535 |
| A2B\|F1\|gbdt | v3_A2B_F1_gbdt_02256 | False | 280.0 | 116.0 | 71.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | a407e17b15b83ca113c61524a71c26107995d9bf | 1.852350054999988 |
| A2\|F1\|logistic | v3_A2_F1_logistic_01488 | False | 4.0 | 4.0 | 0.0 | {'research_tier': None, 'reason': '紅線 4 停止判定／ValueError：後三年 Trim PF 或 MC95 不是有限值，不可記為研究 Fail', 'judgment_stopped': True, 'value_error': 'back3 Trim PF or MC95 is not a finite value; stop research-tier judgment (not a strategy Fail)'} | cef40032e31ef97053e335a43b0f48d34555843a | 0.11173758399672806 |
| A2B\|F2\|gbdt | v3_A2B_F2_gbdt_02397 | False | 163.0 | 97.0 | 66.0 | {'research_tier': 'B', 'reason': 'not A, but trim_pf>1.03 and mc95<48000', 'judgment_stopped': False} | 93d120ffa214ccf91b69b3d429616a8439dffd76 | 0.5441338259988697 |
| A2\|F2\|logistic | v3_A2_F2_logistic_01632 | False | 30.0 | 23.0 | 7.0 | {'research_tier': 'A', 'reason': 'trim_pf>1.10 and mc95<35000', 'judgment_stopped': False} | f17bdf90c54219b79de1804d41fb6dbb30761bb9 | 0.5886034400027711 |
| A2\|F4\|rule_table | v3_A2_F4_rule_table_01913 | False | 201.0 | 142.0 | 56.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | ac05f31daad252a831e990de631c5fa9113ef395 | 0.8069858419985394 |
| A2\|F5\|rule_table | v3_A2_F5_rule_table_02061 | False | 108.0 | 70.0 | 37.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | 1cde007f2317f705127dcc0f155991d8f86d12ca | 0.5185036529946956 |
| A3B\|F1\|rule_table |  | True |  |  |  |  |  | 0.0001145979986176826 |
| A3B\|F2\|rule_table |  | True |  |  |  |  |  | 0.00019591699674492702 |
| A3B\|F3\|rule_table |  | True |  |  |  |  |  | 0.0001929499994730577 |
| A3B\|F4\|rule_table |  | True |  |  |  |  |  | 0.00012456599506549537 |
| A3B\|F5\|rule_table |  | True |  |  |  |  |  | 0.0003367749959579669 |
| A3\|F1\|rule_table |  | True |  |  |  |  |  | 9.296999633079395e-05 |
| A3\|F2\|rule_table |  | True |  |  |  |  |  | 0.00010248400212731212 |
| A3\|F3\|rule_table |  | True |  |  |  |  |  | 9.29689995246008e-05 |
| A3\|F4\|rule_table |  | True |  |  |  |  |  | 0.00012356699880911037 |
| A3\|F5\|rule_table |  | True |  |  |  |  |  | 9.686699922895059e-05 |
| A2\|F3\|logistic | v3_A2_F3_logistic_01785 | False | 95.0 | 82.0 | 12.0 | {'research_tier': 'A', 'reason': 'trim_pf>1.10 and mc95<35000', 'judgment_stopped': False} | 3c12643fd5fd85cd90c0f95a28a2dbcb1d0192f7 | 0.7902967749978416 |
| A2B\|F3\|gbdt | v3_A2B_F3_gbdt_02598 | False | 252.0 | 155.0 | 96.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | ad7a341de674c9bbc2b3a3dcc96b274b3619e57d | 1.2902694439981133 |
| A2\|F4\|logistic | v3_A2_F4_logistic_01926 | False | 52.0 | 38.0 | 14.0 | {'research_tier': 'B', 'reason': 'not A, but trim_pf>1.03 and mc95<48000', 'judgment_stopped': False} | d697014f15390af145f74682f868c6b3d99dc031 | 0.5509180680019199 |
| A2\|F5\|logistic | v3_A2_F5_logistic_02090 | False | 107.0 | 90.0 | 15.0 | {'research_tier': 'B', 'reason': 'not A, but trim_pf>1.03 and mc95<48000', 'judgment_stopped': False} | f0ca8f6785e84c239762e9cf87cc247d4da447cf | 0.7859819210061687 |
| A3B\|F1\|logistic |  | True |  |  |  |  |  | 0.00021075500262668356 |
| A3B\|F2\|logistic |  | True |  |  |  |  |  | 0.0001091860031010583 |
| A3B\|F3\|logistic |  | True |  |  |  |  |  | 0.00010067399853141978 |
| A3B\|F4\|logistic |  | True |  |  |  |  |  | 0.00010891900456044823 |
| A3B\|F5\|logistic |  | True |  |  |  |  |  | 0.00014091200137045234 |
| A3\|F1\|logistic |  | True |  |  |  |  |  | 0.00010681800631573424 |
| A3\|F2\|logistic |  | True |  |  |  |  |  | 9.397200483363122e-05 |
| A3\|F3\|logistic |  | True |  |  |  |  |  | 8.791800064500421e-05 |
| A3\|F4\|logistic |  | True |  |  |  |  |  | 0.00012154400610597804 |
| A3\|F5\|logistic |  | True |  |  |  |  |  | 0.00011163299495819956 |
| A2B\|F4\|gbdt | v3_A2B_F4_gbdt_02733 | False | 135.0 | 106.0 | 28.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | 77dfed0e6077d666379ae0f28f604a7d1def721b | 1.1707876049986226 |
| A2B\|F5\|gbdt | v3_A2B_F5_gbdt_02835 | False | 107.0 | 100.0 | 7.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | 13bc391100651ce888f19acbb6b97fda5f8a6e4b | 0.4749523629943724 |
| A2\|F1\|gbdt | v3_A2_F1_gbdt_01514 | False | 320.0 | 145.0 | 73.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | 20975aaf203aace12cc06cb767561372eabacf49 | 0.849021342000924 |
| A2\|F2\|gbdt | v3_A2_F2_gbdt_01658 | False | 120.0 | 109.0 | 9.0 | {'research_tier': 'A', 'reason': 'trim_pf>1.10 and mc95<35000', 'judgment_stopped': False} | 7fdffa321673ad14c0abfa6f8744ae89edf690d3 | 0.39769029000308365 |
| A2\|F3\|gbdt | v3_A2_F3_gbdt_01823 | False | 169.0 | 157.0 | 9.0 | {'research_tier': 'A', 'reason': 'trim_pf>1.10 and mc95<35000', 'judgment_stopped': False} | d55b304e92cfc97d2f8dbd38e32e1b0eb7684ef2 | 0.32253442000364885 |
| A2\|F4\|gbdt | v3_A2_F4_gbdt_02046 | False | 212.0 | 161.0 | 46.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | d484ed0a46fb40ceda540e1a6a26feb40528c3ac | 1.479255373000342 |
| A2\|F5\|gbdt | v3_A2_F5_gbdt_02121 | False | 90.0 | 75.0 | 10.0 | {'research_tier': 'Fail', 'reason': 'neither A nor B', 'judgment_stopped': False} | 0733376abe6a22b10be7e175d5465329e04e60f4 | 0.38360308299888857 |
| A3B\|F1\|gbdt |  | True |  |  |  |  |  | 0.00017349299741908908 |
| A3B\|F2\|gbdt |  | True |  |  |  |  |  | 0.00010304099851055071 |
| A3B\|F3\|gbdt |  | True |  |  |  |  |  | 9.894500544760376e-05 |
| A3B\|F4\|gbdt |  | True |  |  |  |  |  | 9.433300147065893e-05 |
| A3B\|F5\|gbdt |  | True |  |  |  |  |  | 8.782799704931676e-05 |
| A3\|F1\|gbdt |  | True |  |  |  |  |  | 0.00010670999472495168 |
| A3\|F2\|gbdt |  | True |  |  |  |  |  | 0.00010644800204318017 |
| A3\|F3\|gbdt |  | True |  |  |  |  |  | 7.884200022090226e-05 |
| A3\|F4\|gbdt |  | True |  |  |  |  |  | 8.651900134282187e-05 |
| A3\|F5\|gbdt |  | True |  |  |  |  |  | 8.40639986563474e-05 |
