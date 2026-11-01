# -*- coding: utf-8 -*-
"""agent-skills 瘦身后，同步 01 / 03 文档的数字与状态。"""
import io
import os
import re
import sys

DOCS = r"D:\研究\库体系"


def patch(rel, pairs):
    p = os.path.join(DOCS, rel)
    t = io.open(p, encoding="utf-8").read()
    for old, new in pairs:
        if old not in t:
            print("MISS  %s :: %r" % (rel, old[:80]))
            sys.exit(1)
        t = t.replace(old, new, 1)
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)
    print("OK    %s (%d edits)" % (rel, len(pairs)))


patch("01-我还缺什么库-怎么建.md", [
    ("**20 域 / 186 技能** / 12.0 MB / L0 7.4 KB ≈ 1,922 tok",
     "**19 域 / 176 技能** / 3.2 MB / L0 7.1 KB ≈ 1,881 tok"),
    ("# ... 共 186 条", "# ... 共 176 条"),
    ("- [x] 顶层 catalog 条目数 == 186", "- [x] 顶层 catalog 条目数 == 176"),
    ("`catalog.yaml` 186 条、path 全存在、脚本幂等", "`catalog.yaml` 176 条、path 全存在、脚本幂等"),
])

patch("03-库体系总图.md", [
    ("**已落地**：agent-skills 186 技能 / opc-playbook 30 技能",
     "**已落地**：agent-skills 176 技能（19 域，已剔除 HyperFrames 与制图类）/ opc-playbook 30 技能"),
    ("| `agent-skills` | 技能库 | 186 技能 / 20 域 |",
     "| `agent-skills` | 技能库 | 176 技能 / 19 域 |"),
    ("| `agent-skills` | https://github.com/maning636/agent-skills | `975eff9` | 20 域 / 186 技能 / 11.8 MB / L0 7,407 B ≈ 1,924 tok |",
     "| `agent-skills` | https://github.com/maning636/agent-skills | `2287b3c` | 19 域 / 176 技能 / 3.2 MB / L0 7,240 B ≈ 1,881 tok |"),
])
print("ALL DONE")
