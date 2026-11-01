# -*- coding: utf-8 -*-
"""agent-skills 瘦身后（19 域 / 176 技能），同步 skills-meta：删 hyperframes-video 组合，
清掉组合里指向已删技能的引用，pin 切到 main，更新文档数字。"""
import io
import os
import sys

ROOT = r"D:\skills-meta"


def patch(rel, pairs, must=True):
    p = os.path.join(ROOT, rel)
    t = io.open(p, encoding="utf-8").read()
    for old, new in pairs:
        if old not in t:
            print("MISS  %s :: %r" % (rel, old[:70]))
            if must:
                sys.exit(1)
            continue
        t = t.replace(old, new, 1)
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)
    print("OK    %s (%d edits)" % (rel, len(pairs)))


# 1. 删除 hyperframes-video 组合
comp = os.path.join(ROOT, "compositions", "hyperframes-video.yaml")
if os.path.exists(comp):
    os.remove(comp)
    print("OK    删除 compositions/hyperframes-video.yaml")

# 2. 清掉组合里指向已删技能的引用
patch("compositions/business-ops.yaml", [
    ("      - agent-toolkit/slidecraft\n", ""),
])
patch("compositions/one-person-company.yaml", [
    ("      - data/build-dashboard\n", ""),
    ("      - data/create-viz\n", ""),
])

# 3. pin 切到 main（main 已含精简后的库）
patch("pin", [
    ("agent-skills@chore/prune-20261031", "agent-skills@main"),
])

# 4. catalog.yaml 数字
patch("catalog.yaml", [
    ("note: 20 域 / 186 技能。CRM、现金流、竞品、合同、招聘、财务、客服、数据、企业搜索等企业职能。",
     "note: 19 域 / 176 技能。CRM、现金流、竞品、合同、招聘、财务、客服、数据、企业搜索等企业职能。"),
])

# 5. README / AGENT
patch("README.md", [
    ("我们有 5 个库、20+ 个插件、186 + 27 个技能。如果没有统一索引：",
     "我们有 5 个库、20+ 个插件、176 + 30 个技能。如果没有统一索引："),
    ("│  └─ hyperframes-video.yaml\n", ""),
    ("| `hyperframes-video` | 视频管线：动效、网页转视频、素材与发布 | agent-skills(hyperframes) |\n", ""),
])
patch("AGENT.md", [
    ("| 做视频：动效、网页转视频、素材、发布 | `hyperframes-video` |\n", ""),
])
print("ALL DONE")
