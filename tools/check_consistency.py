# -*- coding: utf-8 -*-
"""自洽检查：跨文档扫描过期数字。

规则：
  * 下面 CHECKS 里列的都是**已经过时**的写法，出现即视为漂移。
  * 标了【历史】的行、以及 git log 里的提交行属于**历史沿革**，不算漂移。
"""
import io
import os
import re
import sys

CHECKS = [
    (r"D:\agent-skills\README.md", [
        (r"\b213\b", "213"), (r"\b22 个领域", "22 域"), (r"50\.5 MB", "50.5MB"),
        (r"12\.09 MB", "12.09MB"), (r"4,969", "4969"), (r"1,565", "1565"),
        (r"Anthropic 166", "166"), (r"HumanLayer 3 个", "HL3"),
        (r"\b186\b", "186"), (r"1,475", "1475"), (r"11\.8 MB", "11.8MB"),
        (r"7,407", "7407"), (r"1,924", "1924"), (r"heygen", "heygen"),
        (r"hyperframes", "hyperframes"), (r"slidecraft", "slidecraft"),
        (r"canva-creator", "canva"), (r"data-visualization", "dataviz"),
        (r"\bcreate-viz\b", "create-viz"), (r"build-dashboard", "dashboard"),
    ]),
    (r"D:\agent-skills\FETCH.md", [
        (r"\b213\b", "213"), (r"\b235\b", "235"), (r"50\.5 MB", "50.5MB"),
        (r"12\.8 MB", "12.8MB"), (r"~1,750", "1750"), (r"59 行", "59行"),
        (r"~1,922 tokens", "1922"),
        (r"\b186\b", "186"), (r"1,475", "1475"), (r"11\.8 MB", "11.8MB"),
        (r"7,407", "7407"), (r"1,924", "1924"), (r"heygen", "heygen"),
        (r"hyperframes", "hyperframes"), (r"slidecraft", "slidecraft"),
        (r"canva-creator", "canva"), (r"data-visualization", "dataviz"),
        (r"\bcreate-viz\b", "create-viz"), (r"build-dashboard", "dashboard"),
    ]),
    (r"D:\agent-skills\INDEX.md", [
        (r"\b213\b", "213"), (r"\b235\b", "235"), (r"\b463\b", "463"),
        (r"\b186\b", "186"), (r"heygen", "heygen"), (r"hyperframes", "hyperframes"),
        (r"slidecraft", "slidecraft"), (r"canva-creator", "canva"),
        (r"data-visualization", "dataviz"), (r"\bcreate-viz\b", "create-viz"),
        (r"build-dashboard", "dashboard"),
    ]),
    (r"D:\agent-skills\NOTICE", [
        (r"合计 166 个", "166"), (r"合计 157 个", "157"), (r"共 154 个技能", "154"),
        (r"\b186\b", "186"), (r"heygen", "heygen"), (r"hyperframes", "hyperframes"),
    ]),
    (r"D:\agent-skills\catalog.yaml", [
        (r"\b213\b", "213"), (r"\b186\b", "186"), (r"hyperframes", "hyperframes"),
        (r"slidecraft", "slidecraft"), (r"canva-creator", "canva"),
        (r"data-visualization", "dataviz"), (r"\bcreate-viz\b", "create-viz"),
        (r"build-dashboard", "dashboard"),
    ]),
    (r"D:\agent-skills\AGENT.md", [
        (r"\b186\b", "186"), (r"hyperframes", "hyperframes"),
    ]),
    (r"D:\opc-playbook\README.md", [
        (r"\b27 个技能", "27技能"), (r"\b27 个技能正文", "27正文"),
        (r"\b29 个技能", "29技能"), (r"\b29 技能", "29技能"),
    ]),
    (r"D:\opc-playbook\AGENT.md", [
        (r"\b27 个技能", "27技能"), (r"\b29 个技能", "29技能"),
    ]),
    (r"D:\opc-playbook\INDEX.md", [
        (r"\b27 个技能", "27技能"), (r"\b29 个技能", "29技能"),
    ]),
    (r"D:\研究\库体系\01-我还缺什么库-怎么建.md", [
        (r"213 条", "213条"), (r"\b213 个技能\b", "213技能"),
        (r"\b29 技能", "29技能"),
        (r"\b186\b", "186"), (r"\b20 域\b", "20域"),
    ]),
    (r"D:\研究\库体系\03-库体系总图.md", [
        (r"22 域 / 213 技能", "213"), (r"\b213\b", "213"),
        (r"\b29 技能", "29技能"),
        (r"\b186\b", "186"), (r"\b20 域\b", "20域"),
        (r"hyperframes-video", "hyperframes-video"), (r"heygen", "heygen"),
    ]),
    (r"D:\skills-meta\catalog.yaml", [
        (r"\b213\b", "213"), (r"22 个域", "22域"), (r"27 技能", "27技能"),
        (r"\b29 技能", "29技能"),
        (r"\b186\b", "186"), (r"\b20 域\b", "20域"),
        (r"hyperframes-video", "hyperframes-video"),
    ]),
    (r"D:\skills-meta\README.md", [
        (r"\b213\b", "213"), (r"22 个域", "22域"), (r"27 技能", "27技能"),
        (r"\b29 技能", "29技能"),
        (r"\b186\b", "186"), (r"\b20 域\b", "20域"),
        (r"hyperframes-video", "hyperframes-video"),
    ]),
    (r"D:\skills-meta\AGENT.md", [
        (r"hyperframes-video", "hyperframes-video"),
    ]),
]

HIST_MARKERS = ("【历史】", "（历史）")
GIT_LOG_RE = re.compile(r"^\s*[0-9a-f]{7,}\s")
# 例外：NOTICE / 03 文档的「已移除内容」记录里要能出现这些名字
ALLOW_FILES = {
    r"D:\agent-skills\NOTICE": ("heygen", "hyperframes"),
    r"D:\研究\库体系\03-库体系总图.md": ("hyperframes-video",),
}


def is_historical(line):
    if any(m in line for m in HIST_MARKERS):
        return True
    return bool(GIT_LOG_RE.match(line))


bad = 0
for path, pats in CHECKS:
    if not os.path.isfile(path):
        print("!! 缺文件", path)
        bad += 1
        continue
    t = io.open(path, encoding="utf-8").read()
    lines = t.split("\n")
    allow = ALLOW_FILES.get(path, ())
    hits = []
    for pat, label in pats:
        for m in re.finditer(pat, t):
            line_no = t[:m.start()].count("\n") + 1
            src = lines[line_no - 1] if line_no - 1 < len(lines) else ""
            if is_historical(src):
                continue
            if label in allow:
                continue
            hits.append("第 %d 行  %s" % (line_no, label))
    if hits:
        print("⚠ %s" % path)
        for h in hits[:8]:
            print("    %s" % h)
        bad += 1
    else:
        print("✅ %s" % path)
print()
print("过期项所在文件: %d" % bad)
sys.exit(1 if bad else 0)
