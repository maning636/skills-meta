# -*- coding: utf-8 -*-
"""推送前扫描：确认公开仓库里没有密钥 / 密码 / token。"""
import io
import os
import re
import sys

PATTERNS = [
    (r"ghp_[A-Za-z0-9]{20,}", "github PAT"),
    (r"gho_[A-Za-z0-9]{20,}", "github oauth token"),
    (r"ghu_[A-Za-z0-9]{20,}", "github user token"),
    (r"github_pat_[A-Za-z0-9_]{20,}", "github fine-grained PAT"),
    (r"sk-[A-Za-z0-9]{20,}", "openai-style key"),
    (r"AIza[0-9A-Za-z_\-]{30,}", "google api key"),
    (r"AKIA[0-9A-Z]{16}", "aws access key"),
    (r"(?i)(api[_-]?key|access[_-]?token|secret[_-]?key|client[_-]?secret)\s*[:=]\s*[\"']?[A-Za-z0-9_\-]{16,}", "key=value"),
    (r"(?i)(password|passwd|pwd)\s*[:=]\s*[\"']?[^\s\"']{6,}", "password="),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "private key"),
]

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv"}
TEXT_EXT = {".md", ".yaml", ".yml", ".json", ".jsonl", ".py", ".js", ".mjs", ".txt", ".ps1", ".sh", ".toml", ".cfg", ""}


def scan(root):
    hits = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext not in TEXT_EXT:
                continue
            p = os.path.join(dirpath, fn)
            try:
                if os.path.getsize(p) > 4 * 1024 * 1024:
                    continue
                t = io.open(p, encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            for pat, label in PATTERNS:
                for m in re.finditer(pat, t):
                    ln = t[:m.start()].count("\n") + 1
                    rel = os.path.relpath(p, root)
                    hits.append((rel, ln, label, m.group(0)[:40]))
    return hits


def main():
    total = 0
    for root in sys.argv[1:]:
        hits = scan(root)
        total += len(hits)
        if hits:
            print("⚠ %s" % root)
            for rel, ln, label, sample in hits[:30]:
                print("   %s:%d  [%s]  %s" % (rel, ln, label, sample))
        else:
            print("✅ %s  无密钥痕迹" % root)
    print()
    print("命中总数: %d" % total)
    sys.exit(1 if total else 0)


main()
