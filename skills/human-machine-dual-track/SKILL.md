---
name: human-machine-dual-track
description: 人读 md、机读薄快照：先 schema、生成物不手改、doctor 对账。
---
> English: Markdown for humans, thin ASCII JSON snapshots for machines: schema first, never hand-edit generated files, reconcile with a doctor.

# 人读一份，机读一份

版本：2026-10-23（v2：补验收与故障判读）

## 什么时候用

- 用户想让 AI "少读文件"，问能不能把文档全转 JSON。
- 状态文件与文件系统/名册不一致（未读数、会话数对不上）。
- 有"多人/多会话读同一份状态"的需求，需要一个可校验的薄缓存。

## 什么时候别用

- 长文档要给人读（规范、说明书、教学材料）：转 JSON 只会丢掉可读性。
- 只有两三个数字：写在 README 里就行，别为一个数字建生成器。
- 团队里没人维护生成器：JSON 会先烂掉，比不做还糟。

## 核心判断

**只把"薄状态"转 JSON**（会话清单、未读计数、游标、任务字段——字段固定、机器天天比较）；长文档保持 markdown。

```
人读面（权威）                 机器面（缓存）
00-规范\*.md ───生成器───▶ _machine\*.json
名册.md ─────────────────▶ sessions.json
信箱目录 ────────────────▶ mailbox.json
        ◀── read_state.py 只吐几行（主会话不整读 JSON）
```

## 落地五步

1. **先写 `schema.json`**：键名 `^[a-z][a-z0-9_]*$`、类型、枚举、pattern、必填、`additionalProperties: false`。
2. **再写生成器**：从权威来源读 → 输出纯 ASCII + `indent=2` + `"schema": 1`。
3. **生成前后都校验**：校验器带 `--selftest`（好样本 + 几个坏样本）。
4. **写 `read_state.py`**：`--sessions` / `--mailbox` / `--me` / `--codes` / `--doctor`，只吐几行。
5. **对账**：`--doctor` 比较快照与盘上/名册/游标，不一致 `[DRIFT]` 退 1。

## 四条铁律

- **生成物不手改**（手改会被下一次覆盖）。
- **快照不是新真相**（真相在 markdown/文件系统/信箱目录）。
- **快照随手更新**：日常命令跑完顺手刷新；受限档位写不进就静默跳过。
- **机器面纯 ASCII**：中文留在正文；文件名也 ASCII。

## 例子（真输出）

```
$ python 工具/kb/read_state.py --doctor
[PASS] 机器层对账：24 个会话、7 个信箱箱、合计未读 122，与名册/盘上一致
```

```
[DRIFT] 快照 未读=87，盘上=92 → 有人刚发信，快照没跟上
```

schema 片段：

```json
{"sessions": {"required": ["sid", "state", "last_active"],
              "properties": {"state": {"enum": ["active", "archived"]},
                             "last_active": {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}\\+08:00$"}}}}
```

## 验收

- `schema_check --selftest`：好样本 PASS + 3 个坏样本分别被抓出（未知键/枚举越界/pattern 不符）。
- 生成物：`json.loads` 通过、无 BOM、`nonascii=0`。
- `--doctor` PASS；手动改快照一个数字 → doctor 必须报 DRIFT（证明对账有效）。
- `json_lint` 进自检后，故意把键名写成 `camelCase` → 报红。

## 常见故障

| 症状 | 根因 | 做法 |
|---|---|---|
| `[DRIFT]` 反复出现 | 日常命令没同步快照 | 命令跑完顺手生成 |
| 某箱未读恒为 0 | 游标被写成 JSON，读的地方按字符串比 | 兼容 `{"last": ...}` |
| schema 校验永远不过 | 字段名含中文/大写 | 键名小写下划线、值 ASCII |
| lint 判自己不合规 | schema.json 里的关键字也被当业务字段查 | 给 schema 文件开豁免 |
