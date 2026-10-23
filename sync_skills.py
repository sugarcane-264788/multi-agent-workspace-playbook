#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把方法包里的 skills 同步到你的 agent 技能目录（或只核对）。目录用 AGENT_SKILLS_DIR 或 --dst 指定。

用法：
    python sync_skills.py                 # 同步（源 -> 目标），打印每个目录做了什么
    python sync_skills.py --check         # 只核对，不改任何文件；一致退出 0，有差异退出 1
    python sync_skills.py --dry-run       # 只打印将要做的，不写
    python sync_skills.py --src DIR --dst DIR   # 别的机器/别的路径

为什么有这个脚本：源目录改了以后要记得手动复制到目标，忘了就是"文档说改了、
本机没改"（与协作库里"快照落后"同一种病）。核对模式是用来放进收尾清单的。
"""
from __future__ import annotations

import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SRC = os.path.join(HERE, "skills")
DEFAULT_DST = os.environ.get("AGENT_SKILLS_DIR") or os.path.expanduser("~/.agent/skills")
SKIP = {"__pycache__", ".DS_Store"}


def walk(root):
    """返回 {相对路径: sha256}，只针对文件。"""
    out = {}
    if not os.path.isdir(root):
        return out
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP]
        for fn in filenames:
            if fn in SKIP:
                continue
            p = os.path.join(dirpath, fn)
            rel = os.path.relpath(p, root).replace("\\", "/")
            with open(p, "rb") as f:
                out[rel] = hashlib.sha256(f.read()).hexdigest()
    return out


def compare(src, dst, names=None):
    """只比"我们发的这几个 skill"：返回 (缺, 多, 不同) 三个相对路径列表。

    目标目录里通常还有别人的 skill（grill-me / teach 之类），那不算差异，
    本脚本不碰它们、也不判它们。
    """
    a, b = walk(src), walk(dst)
    if names is None:
        names = sorted(d for d in os.listdir(src) if os.path.isdir(os.path.join(src, d)) and d not in SKIP)
    mine = lambda k: k.split("/", 1)[0] in names
    ka = {k: v for k, v in a.items() if mine(k)}
    kb = {k: v for k, v in b.items() if mine(k)}
    missing = sorted(set(ka) - set(kb))
    extra = sorted(set(kb) - set(ka))
    differ = sorted(k for k in set(ka) & set(kb) if ka[k] != kb[k])
    return missing, extra, differ


def copy_missing(src, dst, dry=False):
    if dry:
        return
    os.makedirs(dst, exist_ok=True)
    for dirpath, dirnames, filenames in os.walk(src):
        dirnames[:] = [d for d in dirnames if d not in SKIP]
        for fn in filenames:
            if fn in SKIP:
                continue
            s = os.path.join(dirpath, fn)
            rel = os.path.relpath(s, src)
            d = os.path.join(dst, rel)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(s, d)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    src, dst = DEFAULT_SRC, DEFAULT_DST
    check = dry = False
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--check":
            check = True
        elif a == "--dry-run":
            dry = True
        elif a == "--src":
            i += 1
            src = argv[i]
        elif a == "--dst":
            i += 1
            dst = argv[i]
        elif a in ("-h", "--help"):
            print(__doc__)
            return 0
        else:
            print("未知参数：%s（-h 看用法）" % a)
            return 2
        i += 1

    if not os.path.isdir(src):
        print("[FAIL] 源目录不存在：%s" % src)
        return 2
    names = sorted(d for d in os.listdir(src) if os.path.isdir(os.path.join(src, d)) and d not in SKIP)
    if not names:
        print("[FAIL] 源目录里没有 skill：%s" % src)
        return 2

    missing, extra, differ = compare(src, dst, names)
    dirty = bool(missing or extra or differ)

    if check:
        print("[%s] 核对：源 %d 个 skill，目标 %s" % ("PASS" if not dirty else "FAIL", len(names), dst))
        for k in missing:
            print("       缺：%s" % k)
        for k in extra:
            print("       多（目标有源没有）：%s" % k)
        for k in differ:
            print("       不同：%s" % k)
        if dirty:
            print("       -> 跑 `python sync_skills.py` 同步；多出来的文件不会自动删，先人工确认")
            return 1
        print("       7/7 一致" if len(names) == 7 else "       %d/%d 一致" % (len(names), len(names)))
        return 0

    if not dirty:
        print("已是最新：%d 个 skill，源与 %s 一致" % (len(names), dst))
        return 0

    if dry:
        print("将同步（dry-run，不写盘）：")
        for k in missing:
            print("       + %s" % k)
        for k in differ:
            print("       ~ %s" % k)
        for k in extra:
            print("       ! 目标多出（不自动删）：%s" % k)
        return 0

    copy_missing(src, dst)
    missing2, extra2, differ2 = compare(src, dst, names)
    ok = not (missing2 or differ2)
    print("[%s] 同步完成：%d 个 skill 源 -> %s（缺/不同已复制，多出的不删）" % ("PASS" if ok else "FAIL", len(names), dst))
    for k in extra2:
        print("       目标多出（保留，人工确认）：%s" % k)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
