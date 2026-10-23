---
name: session-handoff
description: 新会话接手：三十秒清单 + 真会话演练，卡住=无才算过。
---
> English: Cold-start a brand-new session in 30 seconds; verify it with a real rehearsal where 'stuck = none' is the pass bar.

# 会话接手（handoff）

版本：2026-10-23（v1：从本项目三次实测提炼）

## 什么时候用

- 用户要开新会话接手、换线、交接工作。
- 你（新会话）刚进来，不知道自己是谁、该干什么。
- 改过接手文档，需要**验证**新会话是否真能跑通。

## 什么时候别用

- 还是同一个会话在连续干活：不需要接手语，直接干。
- 只是问一个事实（"名册里我 id 是几"）：直接查，别走全套。
- 库还没建好（连索引/名册都没有）：先搭骨架，再写接手语。

## 接手语：照抄能跑（按顺序，每步有"看到什么算正常"）

```markdown
# 接手语（三十秒）

0.0 先判我是什么档位
  python -c "import os,tempfile;p=os.path.join(tempfile.gettempdir(),'__t.txt');open(p,'w').write('x');print('TEMP 可写');os.remove(p)"
  再用 write 工具试写一次工作区（别用 shell 建文件：受限档位里建了删不掉）。
  - 能写工作区 = 全权档位：后文全跑得通。
  - 只能写 TEMP = 受限档位：见 delegate/受限清单；写库的活要交给全权会话。

0.1 全库体检
  python ..\工具\kb\kb_check.py
  - 全 PASS / 「结果：全部通过」= 正常。
  - 红了：先看 00-规范\09 的「假 FAIL 判读」，别急着修（可能是另一条线在收尾）。

0.2 收信
  python ..\工具\mailbox\mailbox.py digest --for <你的箱>
  - 读自己的箱＝收信，会推进游标，正常。

0.3 认自己
  python ..\工具\kb\read_state.py --me <会话 id 或角色名>
  - 报「（未登记）」＝正常，不是错。

0.4 读三份（只读）
  README.md（路由）→ 00-规范\04（硬规矩）→ 40-协作\_模板\接手交接.md

0.5 接活
  改动前先写计划卡（见 card-ledger-workflow）；卡外改动先问。

0.6 收尾
  台账 → verify --card → kb_index → publish → status --json → kb_check → --doctor
```

## 演练：怎么证明接手语真的能用

```bash
# 1. 起一个真·新会话，只给它接手语
agent CLI --headless --json "<接手语全文>"
# 2. 需要这些环境
#    DEEPSEEK_API_KEY（从自己的配置/桥读，别硬编码）
#    AGENT_HOME=<agent-home>
#    cwd = 工作区根
# 3. stdout 每行一个 JSON：{"type":"session"} 拿会话 id，{"type":"final"} 拿最终文本
```

判定标准只有一句：**新会话报告里「卡住的地方」= 无**。否则把它卡的那一步抄回接手语改掉，再跑。

演练会话用完要回收（见 `delegate-and-reclaim`）。

## 例子（真演练报告的骨架）

```
0.0 档位：受限（TEMP 可写，写 <workspace> 报 PermissionError: [Errno 13]）
0.1 体检：13/13 PASS（提示：桥会话已归档=侧栏隐藏）
0.2 收信：kb 箱无新消息
0.3 身份：（未登记）→ 正常；信箱 kb
0.5 不写卡（只读演练）
卡住的地方：无
```

## 验收

- 新会话照接手语自己跑完 0.0→0.6，报告"卡住=无"。
- 报告里每一步都有**实际输出**，不是"读完了"。
- 受限档位的新会话没试图写库（或写了但按兜底路径交付）。

## 常见坑

- 接手语写成散文 → 新会话读完还是不知道先干什么。
- 每一步不给"看到什么算正常" → 新会话把正常现象当故障。
- 改完文档不演练 → 等于没改。
- 演练会话不回收 → 活跃列表越积越多。
