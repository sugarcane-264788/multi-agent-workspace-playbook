#!/usr/bin/env python3
"""发布前自检：确认包里没有绝对路径、真实会话编号、内部业务名、疑似凭据。

用法：
  python scrub_check.py          # 扫描本目录（跳过自身）
  python scrub_check.py DIR      # 扫描指定目录
退出码：0=干净；1=命中（打印文件:行号）。
"""
import os
import re
import sys

SELF = os.path.basename(os.path.abspath(__file__))
EXTS = ('.md', '.py', '.json', '.sh', '.txt', '.yml', '.yaml')

# 换成你自己的内部词：团队名、产品内部代号、真实课程名……
INTERNAL_WORDS = [
    'USTB', '锐格', 'zhy34532', 'D:\\DSH', 'AI-Workspace',
]

PATTERNS = [
    (re.compile(r'[A-Za-z]:\\\\?[A-Za-z]'), 'Windows 绝对路径'),
    (re.compile(r'(?<![<\w ])/(home|Users|srv|opt)/[A-Za-z]'), 'POSIX 绝对路径'),
    (re.compile(r'session-[0-9a-f]{8}-[0-9a-f-]{27}'), '真实会话编号'),
    (re.compile(r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b'), 'uuid'),
    (re.compile(r'sk-[A-Za-z0-9]{16,}'), '疑似 API key'),
    (re.compile(r'gh[pousr]_[A-Za-z0-9]{20,}'), '疑似 GitHub token'),
    (re.compile(r'(?i)authorization\s*[:=]\s*\S{20,}'), '疑似 Authorization 头'),
]


def scan(root):
    hits = []
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in ('.git', '__pycache__')]
        for fn in files:
            if not fn.endswith(EXTS) or fn == SELF:
                continue
            p = os.path.join(dirpath, fn)
            try:
                text = open(p, encoding='utf-8').read()
            except UnicodeDecodeError:
                continue
            for i, line in enumerate(text.splitlines(), 1):
                for pat, why in PATTERNS:
                    if pat.search(line):
                        hits.append((p, i, why, line.strip()[:90]))
                for w in INTERNAL_WORDS:
                    if w in line:
                        hits.append((p, i, '内部词 %r' % w, line.strip()[:90]))
    return hits


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
    hits = scan(root)
    if not hits:
        print('[PASS] 干净：没有绝对路径、真实编号、内部词、疑似凭据')
        return 0
    print('[FAIL] %d 处命中，发布前必须处理：' % len(hits))
    for p, i, why, line in hits:
        print('  %s:%d  [%s]\n      %s' % (os.path.relpath(p, root), i, why, line))
    return 1


if __name__ == '__main__':
    sys.exit(main())
