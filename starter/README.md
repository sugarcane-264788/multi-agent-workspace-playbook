# starter：十五分钟能跑起来的最小一套

这里只放"跑得动"的最小件。为什么这样做、为什么那样取舍，看上层 `01-设计全景.md` 与 `04-落地清单.md`；本目录不放长文，免得你还要挑哪些该读。

## 五件东西

| 文件 | 干什么 |
|---|---|
| `mailbox_min.py` | 80 行信箱：写信、数未读、读信、推进游标；带 `--selftest` |
| `card-template.md` | 改动前的计划卡模板（含 `- 文件：` 清单与 verify 块） |
| `boot-template.md` | 新会话开工语（认自己→三分钟读完→拿任务） |
| `closeout.sh` | 收尾七连的空壳，每步注释写着该填什么 |
| 本文件 | 顺序与验收 |

## 顺序（照着敲）

```bash
# 1. 先确认信箱能跑（不碰任何东西，只读）
python mailbox_min.py --selftest
# 期望最后一行：selftest=PASS（依次未读：2/2/3/0，a 箱信数 0）

# 2. 建你自己的箱：一个"人"一个箱，别共用
python mailbox_min.py send --to worker --from boss --text "第一件事：把 X 的版本号核一遍"
python mailbox_min.py status
# 期望：boss 未读 0 / worker 未读 1

# 3. 以 worker 的身份收信（会推进游标）
python mailbox_min.py digest --for worker
python mailbox_min.py status
# 期望：worker 未读 0

# 4. 只读地看一眼但不推进游标（演练/审计时用）
python mailbox_min.py send --to worker --from boss --text "第二件：不要动文件"
python mailbox_min.py digest --for worker --peek
python mailbox_min.py status
# 期望：worker 未读 1 —— --peek 不推进

# 5. 抄一张卡：把要改的文件列进 "本卡文件"，命令写进 verify 块
#    然后照 closeout.sh 的七步走一遍（前几步现在可能是空的，先留痕）
```

## 验收（做到算过）

- `--selftest` 打 `selftest=PASS`。
- `status` 的"未读"会随 `digest` 增减，`--peek` 不推进。
- 你能说出**为什么一件事只放一个箱**：同一箱两个使用者共用一份游标，谁先读谁推进，另一人静默丢信（这是真实事故，不是假想）。
- 你的第一张卡有：日期主题、范围、不做什么、`- 文件：` 清单、verify 命令块、回滚。

## 故意没做的

- 锁与并发合并（两个人同时写信真会撞名字——真需要时加 `O_EXCL` 或时间戳加随机后缀）。
- 播报/索引/台账/自检脚本——`04-落地清单.md` 里有取舍说明，先跑最小件再长。
- 中文/ASCII 命名规则、JSON 快照——那是第二周的事，别在第一天做。
