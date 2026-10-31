# -*- coding: utf-8 -*-
"""三库已推 GitHub，同步 03 总图的落地状态。"""
import io
import os
import sys

DOCS = r"D:\研究\库体系"


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
    ("## 附：本次对 `agent-skills` 的实际改动（已提交，未推 main）",
     "## 附：本次对 `agent-skills` 的实际改动（**已推 GitHub main**）"),
    ("### agent-skills（分支 `chore/prune-20261031`，本地已提交，**未推 main**）",
     "### agent-skills（分支 `chore/prune-20261031` 已推；**main 已 fast-forward 到 `975eff9`**）\n\n"
     "🔗 https://github.com/maning636/agent-skills  （public）"),
    ("### opc-playbook（新建独立库，本地已提交，**未推 GitHub**）",
     "### opc-playbook（新建独立库，**已推 GitHub**）\n\n"
     "🔗 https://github.com/maning636/opc-playbook  （public）"),
    ("### skills-meta（新建元库，本地已提交，**未推 GitHub**）",
     "### skills-meta（新建元库，**已推 GitHub**）\n\n"
     "🔗 https://github.com/maning636/skills-meta  （public）"),
    ("""### 工作区

`D:\\work\\hyperframes\\` —— AGENTS.md / skills/hyperframes-release / scripts/verify_project.py / 素材/ / 产出/ / 台账.md""",
     """### 工作区

`D:\\work\\hyperframes\\` —— AGENTS.md / skills/hyperframes-release / scripts/verify_project.py / 素材/ / 产出/ / 台账.md

---

## 附：三库 GitHub 现状（2026-10-31）

| 库 | GitHub | 可见性 | main HEAD | 内容 |
|---|---|---|---|---|
| `agent-skills` | https://github.com/maning636/agent-skills | public | `975eff9` | 20 域 / 186 技能 / 11.8 MB / L0 7,407 B ≈ 1,924 tok |
| `opc-playbook` | https://github.com/maning636/opc-playbook | public | `506e618` | 2 组 / 30 技能 / L0 6,048 B ≈ 1,572 tok |
| `skills-meta` | https://github.com/maning636/skills-meta | public | `97aba05` | 5 库登记 / 5 composition / pin / lock / Loader / 插件扫描器 |

三个库**全部 public**，外部专家可直接 clone / 提 issue 反馈意见。
`engineering-standard` 保持不动（CC BY-NC-SA 4.0，远端 `main` 未变）。"""),
])
print("ALL DONE")
