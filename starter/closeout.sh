#!/usr/bin/env bash
# 收尾七连（照顺序跑，别跳；每步后面写着"为什么这个位置"）
# 用法：填好下面的变量，然后 bash closeout.sh
set -u

KA="<卡名，例如 2026-10-23-M19-P2三件>"
DIR_K="<卡所在目录，例如 /srv/kb/40-协作/_计划卡>"
TOOL="<工具目录，例如 /srv/kb/工具>"
KB="<库根，例如 /srv/kb/协作库>"
BOX="<你的箱，例如 kb>"
PY=python

echo "== 0/7 先确认卡里的 - 文件： 清单已记进台账（每个改过的文件都要 add）"
$PY "$TOOL/kb/ledger.py" add --path "<相对库根的路径>" --action edit --note "$KA"

echo "== 1/7 台账比对 + 卡内 verify 命令（这一步最便宜，先跑，省得改完才发现缺文件）"
$PY "$TOOL/kb/verify.py" --card "40-协作\\_计划卡\\${KA}.md"

echo "== 2/7 重建索引（改了任何 .md 都要跑，否则自检第 12 项落后）"
$PY "$TOOL/kb/kb_index.py"

echo "== 3/7 播报（改了共用格/规范就必须播，否则自检第 8 项红；投给别人不投自己）"
$PY "$TOOL/mailbox/mailbox.py" publish --scope all --from "$BOX" \
  --title "<标题：一句话说变了什么>" \
  --text "一、变了什么：<...>
二、为什么：<...>
三、对看到这条消息的会话：<要她做什么，没有就写没有>
四、另外：<...>"

echo "== 4/7 快照跟上（播报会改信箱，不跑这一步 --doctor 必漂移）"
$PY "$TOOL/mailbox/mailbox.py" status --json >/dev/null
$PY "$TOOL/kb/session_registry.py" --json >/dev/null

echo "== 5/7 自检（前面几步漏了哪步，这里会告诉你是哪一项）"
$PY "$TOOL/kb/kb_check.py"

echo "== 6/7 机器层与盘上对账（红=快照没跟上，不是数据坏了）"
$PY "$TOOL/kb/read_state.py" --doctor

echo "== 7/7 回报：已做+证据 / 正在做 / 还剩 / 要你决定的"
echo "   别把计划当结果、别报没跑过的命令；verify 的原始输出要贴出来。"
