#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""最小信箱：一件事只放一个箱，写信/数未读/读信。

    python mailbox_min.py send --to b --from a --text "一句话"
    python mailbox_min.py status
    python mailbox_min.py digest --for b [--peek]
    python mailbox_min.py --selftest

默认根目录是 ./_minibox（可用 --root 或环境变量 MAILBOX_ROOT 改）。
它只做三件事，故意不做锁、不做合并、不做播报——那些等你真需要了再加。
"""
import argparse
import os
import sys
import tempfile
import time

ROOT = os.environ.get("MAILBOX_ROOT") or os.path.join(os.getcwd(), "_minibox")


def boxes(root):
    d = os.path.join(root, "boxes")
    return sorted(n for n in os.listdir(d)) if os.path.isdir(d) else []


def letters(root, box):
    d = os.path.join(root, "boxes", box)
    return sorted(f for f in os.listdir(d) if f.endswith(".md")) if os.path.isdir(d) else []


def cursor(root, box):
    p = os.path.join(root, "cursors", box)
    try:
        with open(p, encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return ""


def set_cursor(root, box, name):
    d = os.path.join(root, "cursors")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, box), "w", encoding="utf-8", newline="\n") as f:
        f.write(name + "\n")


def unread(root, box):
    c = cursor(root, box)
    return [f for f in letters(root, box) if f > c]


def send(root, to, frm, text):
    d = os.path.join(root, "boxes", to)
    os.makedirs(d, exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    name = "%s-from-%s.md" % (ts, frm)
    body = "发件人：%s\n收件人：%s\n时间：%s\n\n%s\n" % (frm, to, ts, text.strip())
    with open(os.path.join(d, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(body)
    return name


def digest(root, box, peek):
    c = cursor(root, box)
    new = unread(root, box)
    if not new:
        print("（%s 箱没有新消息；游标：%s）" % (box, c or "空"))
        return
    print("--- %s 箱 %d 封（游标：%s）" % (box, len(new), c or "空"))
    for n in new:
        with open(os.path.join(root, "boxes", box, n), encoding="utf-8") as f:
            t = f.read()
        print("\n### %s\n%s" % (n, t[t.find("\n\n") + 2:].strip() if "\n\n" in t else t.strip()))
    if peek:
        print("\n（--peek：游标没动，下次还会读到这 %d 封）" % len(new))
    else:
        set_cursor(root, box, new[-1])
        print("\n（已推进游标到 %s）" % new[-1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    s = sub.add_parser("send")
    s.add_argument("--to", required=True)
    s.add_argument("--from", dest="frm", default="main")
    s.add_argument("--text", required=True)
    sub.add_parser("status")
    d = sub.add_parser("digest")
    d.add_argument("--for", dest="box", required=True)
    d.add_argument("--peek", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        tmp = tempfile.mkdtemp(prefix="minibox-")
        send(tmp, "b", "a", "第一封")
        time.sleep(1.1)  # 文件名按秒排序，睡一下保证名字不同
        send(tmp, "b", "a", "第二封")
        n1 = len(unread(tmp, "b"))
        digest(tmp, "b", peek=True)
        n2 = len(unread(tmp, "b"))
        time.sleep(1.1)
        send(tmp, "b", "a", "第三封")
        n3 = len(unread(tmp, "b"))
        digest(tmp, "b", peek=False)
        n4 = len(unread(tmp, "b"))
        ok = (n1 == 2 and n2 == 2 and n3 == 3 and n4 == 0 and letters(tmp, "a") == [])
        print("selftest=%s（依次未读：%d/%d/%d/%d，a 箱信数 %d）"
              % ("PASS" if ok else "FAIL", n1, n2, n3, n4, len(letters(tmp, "a"))))
        return 0 if ok else 1

    if a.cmd == "send":
        print("已投递 -> %s 箱 [%s]" % (a.to, send(a.root, a.to, a.frm, a.text)))
    elif a.cmd == "status":
        for b in boxes(a.root):
            print("%-8s 未读 %d / 共 %d" % (b, len(unread(a.root, b)), len(letters(a.root, b))))
        print("合计未读 %d" % sum(len(unread(a.root, b)) for b in boxes(a.root)))
    elif a.cmd == "digest":
        digest(a.root, a.box, a.peek)
    else:
        ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
