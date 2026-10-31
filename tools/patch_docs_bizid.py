# -*- coding: utf-8 -*-
"""把 03 总图 / 01 文档同步到最新状态（共享业务 ID 落地 + opc-playbook 30 技能）。"""
import io
import os
import sys

DOCS = r"D:\研究\库体系"
META = r"D:\skills-meta"

def patch(path, pairs):
    with io.open(path, "r", encoding="utf-8") as f:
        t = f.read()
    for old, new in pairs:
        if old not in t:
            print("MISS  %s :: %r" % (path, old[:70]))
            sys.exit(1)
        t = t.replace(old, new, 1)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(t)
    print("OK    %s (%d edits)" % (path, len(pairs)))

patch(os.path.join(DOCS, "03-库体系总图.md"), [
    ("> `agent-skills` 本地实盘（463→235→213）、`plan-to-goal`、`workbuddy-runbook`",
     "> `agent-skills` 本地实盘【历史】(463→235→213) → 现状 186 技能 / 20 域、`plan-to-goal`、`workbuddy-runbook`"),
    ("**已落地**：agent-skills 186 技能 / opc-playbook 29 技能 / skills-meta 元库 + 5 组合 / Loader --composition / 第一个真实工作区 / 插件共存规则",
     "**已落地**：agent-skills 186 技能 / opc-playbook 30 技能 / skills-meta 元库 + 5 组合 / Loader --composition / 第一个真实工作区 / 插件共存规则 / **共享业务 ID**"),
    ("**净删 22 个 → agent-skills 从 235 落到 213 技能 / 22 域 / 12.09 MB / 1,565 文件。**",
     "**净删 22 个 → agent-skills 从 235 落到 213 技能 / 22 域 / 12.09 MB / 1,565 文件。【历史】复审一阶段的数字；最终 186 技能 / 20 域。**"),
    ("> agent-skills 的来源构成变为：**Anthropic 166 + heygen 5 + 本机自研 42 = 213**。",
     "> agent-skills 的来源构成变为：**Anthropic 166 + heygen 5 + 本机自研 42 = 213**。【历史】最终构成：Anthropic 157 + heygen 5 + 本机自研 24 = 186。"),
    ("| **P3** | ⑩ OPC / idea / engineering 三层用**同一个业务 ID** 跑通一次真实任务 | 验证联动 | ⑧⑨ | ⬜ **未做**：ID 字段已定义，尚未在两个状态机脚本里真正串起来 |",
     "| **P3** | ⑩ OPC / idea / engineering 三层用**同一个业务 ID** 跑通一次真实任务 | 验证联动 | ⑧⑨ | ✅ **已完成**：`opc/opc-business-registry` 分配器 + `idea-to-cash` state v2（`biz_id` + `layers` 指针） |"),
    ("""### opc-playbook（新建独立库，本地已提交，**未推 GitHub**）

```
  e852712  feat(opc-playbook): 从 agent-skills 迁出 OPC 经营层与通用增长方法（27 技能）
  19897ee  feat(opc):         补齐指标字典与实验设计（→ 29 技能）
```

**最终：2 组 / 29 技能 / `skills/<name>/SKILL.md` 形态 / L0 6.1 KB ≈ 1.6k tokens**""",
     """### opc-playbook（新建独立库，本地已提交，**未推 GitHub**）

```
  e852712  feat(opc-playbook): 从 agent-skills 迁出 OPC 经营层与通用增长方法（27 技能）
  19897ee  feat(opc):         补齐指标字典与实验设计（→ 29 技能）
  (新)     feat(bizid):      共享业务 ID 注册表 + state v2（→ 30 技能）
```

**最终：2 组 / 30 技能 / `skills/<name>/SKILL.md` 形态 / L0 6.3 KB ≈ 1.8k tokens**"""),
])

patch(os.path.join(DOCS, "01-我还缺什么库-怎么建.md"), [
    ("| **技能库** | `opc-playbook` | `D:\\opc-playbook\\` | **2 组 / 29 技能** / L0 6.1 KB ≈ 1.6k tok |",
     "| **技能库** | `opc-playbook` | `D:\\opc-playbook\\` | **2 组 / 30 技能** / L0 6.3 KB ≈ 1.8k tok |"),
])
print("ALL DONE")
