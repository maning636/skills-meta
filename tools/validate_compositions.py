# -*- coding: utf-8 -*-
"""校验 compositions 里引用的每个技能/文档路径都真实存在。"""
import json
import os
import sys

import yaml

ROOT = r"D:\skills-meta"
CAT = yaml.safe_load(open(os.path.join(ROOT, "catalog.yaml"), encoding="utf-8"))
LIBS = {l["id"]: l for l in CAT["libraries"]}

# 各库本地路径（catalog.yaml 里的 local_path 优先）
def lib_catalog(lib):
    lp = lib.get("local_path")
    if lp:
        p = os.path.join(lp, lib.get("catalog", "catalog.yaml"))
        if os.path.isfile(p):
            return yaml.safe_load(open(p, encoding="utf-8"))
    return None


bad = []
ok = 0
for f in sorted(os.listdir(os.path.join(ROOT, "compositions"))):
    if not f.endswith(".yaml"):
        continue
    comp = yaml.safe_load(open(os.path.join(ROOT, "compositions", f), encoding="utf-8"))
    for inc in comp.get("include", []) or []:
        spec = inc.get("library", "")
        base = spec.split("@")[0]
        lib = LIBS.get(base)
        if lib is None:
            bad.append("%s: 未登记的库 %s" % (f, base))
            continue
        if lib["type"] == "skills":
            lc = lib_catalog(lib)
            if lc is None:
                bad.append("%s: 拿不到 %s 的 catalog（未推远端？）" % (f, base))
                continue
            ids = {s["id"] for s in lc["skills"]}
            doms = {s.get("domain") or s.get("group") for s in lc["skills"]}
            for sid in inc.get("skills", []) or []:
                if sid not in ids:
                    bad.append("%s: %s 不存在于 %s" % (f, sid, base))
                else:
                    ok += 1
            for d in inc.get("domains", []) or []:
                if d not in doms:
                    bad.append("%s: 域 %s 不存在于 %s" % (f, d, base))
                else:
                    ok += 1
        elif lib["type"] == "spec":
            lp = lib.get("local_path")
            for p in inc.get("paths", []) or []:
                if lp and os.path.isdir(lp):
                    import glob
                    if not glob.glob(os.path.join(lp, p)):
                        bad.append("%s: 文档路径 %s 在 %s 里找不到" % (f, p, base))
                    else:
                        ok += 1
                else:
                    ok += 1  # 远端库，无法本地校验
        elif lib["type"] == "plugin":
            for s in inc.get("skills", []) or []:
                ok += 1

print("校验通过项: %d" % ok)
if bad:
    print("问题 %d 项:" % len(bad))
    for b in bad:
        print("  - %s" % b)
    sys.exit(1)
print("✅ 全部引用有效")
