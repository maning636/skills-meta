# -*- coding: utf-8 -*-
"""自洽检查：跨文档扫描过期数字。"""
import io
import os
import re
import sys

CHECKS = [
    (r"D:\agent-skills\README.md", [
        (r"\b213\b", "213"), (r"\b22 个领域", "22 域"), (r"50\.5 MB", "50.5MB"),
        (r"12\.09 MB", "12.09MB"), (r"4,969", "4969"), (r"1,565", "1565"),
        (r"Anthropic 166", "166"), (r"HumanLayer 3 个", "HL3"),
    ]),
    (r"D:\agent-skills\FETCH.md", [
        (r"\b213\b", "213"), (r"\b235\b", "235"), (r"50\.5 MB", "50.5MB"),
        (r"12\.8 MB", "12.8MB"), (r"~1,750", "1750"), (r"59 行", "59行"),
        (r"~1,922 tokens", "1922"),
    ]),
    (r"D:\agent-skills\INDEX.md", [
        (r"\b213\b", "213"), (r"\b235\b", "235"), (r"\b463\b", "463"),
    ]),
    (r"D:\agent-skills\NOTICE", [
        (r"合计 166 个", "166"), (r"共 154 个技能", "154+3"),
    ]),
    (r"D:\agent-skills\catalog.yaml", [
        (r"\b213\b", "213"),
    ]),
    (r"D:\opc-playbook\README.md", [
        (r"\b27 个技能", "27技能"), (r"\b27 个技能正文", "27正文"),
    ]),
    (r"D:\opc-playbook\AGENT.md", [
        (r"\b27 个技能", "27技能"),
    ]),
    (r"D:\opc-playbook\INDEX.md", [
        (r"\b27 个技能", "27技能"),
    ]),
    (r"D:\研究\库体系\01-我还缺什么库-怎么建.md", [
        (r"213 条", "213条"), (r"\b213 个技能\b", "213技能"),
    ]),
    (r"D:\研究\库体系\03-库体系总图.md", [
        (r"22 域 / 213 技能", "213"), (r"\b213\b", "213"),
    ]),
    (r"D:\skills-meta\catalog.yaml", [
        (r"\b213\b", "213"), (r"22 个域", "22域"), (r"27 技能", "27技能"),
    ]),
    (r"D:\skills-meta\README.md", [
        (r"\b213\b", "213"), (r"22 个域", "22域"), (r"27 技能", "27技能"),
    ]),
]

bad = 0
for path, pats in CHECKS:
    if not os.path.isfile(path):
        print("!! 缺文件", path)
        bad += 1
        continue
    t = io.open(path, encoding="utf-8").read()
    hits = []
    for pat, label in pats:
        for m in re.finditer(pat, t):
            line = t[:m.start()].count("\n") + 1
            hits.append("第 %d 行  %s" % (line, label))
    if hits:
        print("⚠ %s" % path)
        for h in hits[:8]:
            print("    %s" % h)
        bad += 1
    else:
        print("✅ %s" % path)
print()
print("过期项所在文件: %d" % bad)
