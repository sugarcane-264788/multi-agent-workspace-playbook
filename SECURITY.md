# 安全与隐私

## 这个仓库里有什么

只有方法文档、模板和两个纯标准库脚本（`starter/mailbox_min.py`、`sync_skills.py`、`scrub_check.py`）。
**没有任何** API key、token、训练/教学数据、真实人名、真实会话编号、绝对路径。

## 发布前自检

```
python scrub_check.py
```

它会扫描本目录所有 `.md/.py/.json/.sh`，命中下列任一形态就非零退出并打印行号：

- 绝对路径（`X:\...`、`/home/...`）
- 32 位以上 uuid 或 `session-<uuid>` 形态的真实会话编号
- 内部业务名清单（写在脚本里的 `INTERNAL_WORDS` 常量）
- 疑似凭据（`sk-`、`ghp_`、`Authorization:` 后跟长串）

维护者改完文档、**push 之前**跑一次；也可以挂到 CI。

## 报告问题

如果你在这里看到不该公开的东西，请开 issue 或在仓库的 Security 页留言，我会立刻删除。
