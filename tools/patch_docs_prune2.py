# -*- coding: utf-8 -*-
"""03 文档：agent-skills 瘦身后的数字与状态。"""
import io
import os
import sys

P = os.path.join(r"D:\研究\库体系", "03-库体系总图.md")

pairs = [
    ("> `agent-skills` 本地实盘【历史】(463→235→213) → 现状 186 技能 / 20 域、",
     "> `agent-skills` 本地实盘【历史】(463→235→213) → 现状 176 技能 / 19 域、"),
    ("**已落地**：agent-skills 186 技能 / opc-playbook 30 技能",
     "**已落地**：agent-skills 176 技能（19 域，已剔除 HyperFrames 与制图类）/ opc-playbook 30 技能"),
    ("最终 186 技能 / 20 域。**", "最终 176 技能 / 19 域。**"),
    ("【历史】最终构成：Anthropic 157 + heygen 5 + 本机自研 24 = 186。",
     "【历史】最终构成：Anthropic 153 + 本机自研 23 = 176。"),
    ("│  agent-skills     公共 MIT   186 skill / 20 域   ← 已精简 ✅        │",
     "│  agent-skills     公共 MIT   176 skill / 19 域   ← 已精简 ✅        │"),
    ("别把 186 全塞进去。", "别把 176 全塞进去。"),
    ("| `agent-skills` | 186 个通用岗位技能（公共 MIT 素材） |",
     "| `agent-skills` | 176 个通用岗位技能（公共 MIT 素材） |"),
    ("### agent-skills（分支 `chore/prune-20261031` 已推；**main 已 fast-forward 到 `975eff9`**）",
     "### agent-skills（**main 已到 `2287b3c`**：剔除 HyperFrames 域与制图类技能，收敛到 Anthropic 技能集）"),
    ("  eeeebd5  refactor(lib):  OPC + growth-ops 迁出成独立库 → 20 域 / 186 技能",
     "  eeeebd5  refactor(lib):  OPC + growth-ops 迁出成独立库 → 20 域 / 186 技能\n"
     "  2287b3c  refactor(prune): 移除 hyperframes 域与制图类技能 → 19 域 / 176 技能 / 3.2 MB"),
    ("**最终：20 域 / 186 技能 / 1,475 文件 / 11.8 MB / L0 7.4 KB ≈ 1,924 tokens**",
     "**最终：19 域 / 176 技能 / 490 文件 / 3.2 MB / L0 7.1 KB ≈ 1,881 tokens**"),
    ("| `agent-skills` | https://github.com/maning636/agent-skills | public | `975eff9` | 20 域 / 186 技能 / 11.8 MB / L0 7,407 B ≈ 1,924 tok |",
     "| `agent-skills` | https://github.com/maning636/agent-skills | public | `2287b3c` | 19 域 / 176 技能 / 3.2 MB / L0 7,240 B ≈ 1,881 tok |"),
]

t = io.open(P, encoding="utf-8").read()
for old, new in pairs:
    if old not in t:
        print("MISS :: %r" % old[:80]); sys.exit(1)
    t = t.replace(old, new, 1)
io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("OK 03-库体系总图.md (%d edits)" % len(pairs))
