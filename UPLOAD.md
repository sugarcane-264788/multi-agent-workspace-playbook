# 怎么把它放上 GitHub（不装任何软件）

1. 打开 https://github.com ，注册/登录。
2. 右上角 `+` → `New repository`：
   - `Repository name`：`multi-agent-workspace-playbook`
   - 可见性：先选 `Private`（跑通再改 `Public`：仓库页 `Settings` → 最下面 `Change visibility`）
   - 不要勾 `Add a README file`（我们自带 README）
   - `Create repository`
3. 新仓库页面点 `uploading an existing file`（或 `Add file` → `Upload files`）。
4. 把**本文件所在目录里的全部内容**拖进浏览器窗口：
   - 注意是**里面的文件和文件夹**（`README.md`、`LICENSE`、`skills/`、`starter/`、`evals/` …），不要把整个外层文件夹拖进去。
   - 拖完等进度条走完，底部 `Commit changes`。
5. 回到仓库首页确认能看到 `README.md` 的内容。
6. 要公开时：`Settings` → 拉到底 `Danger Zone` → `Change repository visibility` → `Make public`。
7. 隐私建议：`Settings` → `Emails` → 勾 `Keep my email addresses private`；`Settings` → `Public profile` 可以不填真名。

## 以后要改内容

- 网页上直接点文件 → 铅笔图标 → 改 → `Commit changes`（每次提交都会留历史）。
- 或者把仓库 `Download ZIP` 下来改，再拖回去覆盖。
- 想用命令行（可选，需装 Git for Windows）：`git clone <仓库地址>`，改完 `git add -A && git commit -m "说明" && git push`。
