#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
skills-meta Loader —— 解析 composition，输出「库@tag + 技能 id 列表」。

用法:
  python tools/resolve.py --list                    # 列出所有 composition
  python tools/resolve.py one-person-company       # 解析并打印完整清单
  python tools/resolve.py one-person-company --inject   # 只输出注入上下文的内容
  python tools/resolve.py one-person-company --lock      # 解析并写入 lock.jsonl
  python tools/resolve.py one-person-company --check     # 与上次 lock 对比，报告差异

规则（来自 agent-workspace-spec 08 篇）:
  * 先读 catalog.yaml -> 按 pin 拉取各库 -> 只把 name/description 注入上下文
  * 缓存放在 ~/.agent-skills-cache/<库名>@<tag>/，一键可清
  * 执行时打印本次使用的 composition / 库@tag / 技能 id 列表
  * 生产用的 composition 固定 tag，不固定 main
  * 插件优先于我们的技能；冲突看 catalog 的 superseded_by
"""
import argparse
import datetime
import json
import os
import re
import sys
import urllib.request

try:
    import yaml
except ImportError:
    yaml = None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG = os.path.join(ROOT, "catalog.yaml")
PIN = os.path.join(ROOT, "pin")
COMPOSITIONS = os.path.join(ROOT, "compositions")
LOCK = os.path.join(ROOT, "lock.jsonl")
PLUGIN_DIR = os.path.join(ROOT, "libraries", "plugins")
CACHE = os.path.join(os.path.expanduser("~"), ".agent-skills-cache")


# --------------------------------------------------------------- 基础读取
def load_yaml(path):
    with open(path, "r", encoding="utf-8") as fh:
        if yaml is None:
            raise RuntimeError("需要 PyYAML：pip install pyyaml")
        return yaml.safe_load(fh)


def read_pin():
    pins = {}
    if not os.path.isfile(PIN):
        return pins
    for line in open(PIN, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        for sep in ("@", "="):
            if sep in line:
                k, _, v = line.partition(sep)
                pins[k.strip()] = v.strip()
                break
    return pins


def fetch_text(url, timeout=25):
    req = urllib.request.Request(url, headers={
        "User-Agent": "skills-meta-resolve/1.0", "Accept": "text/plain, */*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def library_catalog(lib):
    """拿到某库的 catalog.yaml（本地优先，其次网络）。"""
    local = lib.get("local_path")
    if local:
        p = os.path.join(local, lib.get("catalog", "catalog.yaml"))
        if os.path.isfile(p):
            return load_yaml(p), "local:" + p
    base = lib.get("raw_base")
    if base:
        try:
            txt = fetch_text(base + lib.get("catalog", "catalog.yaml"))
            return yaml.safe_load(txt) if yaml else None, "remote:" + base
        except Exception as e:
            print("  ! %s 的 catalog 拉取失败 (%s)" % (lib.get("id"), e), file=sys.stderr)
    return None, None


def plugin_manifest(name):
    """插件能力清单（由 scan_plugins.py 生成）。"""
    p = os.path.join(PLUGIN_DIR, "%s.yaml" % name)
    if os.path.isfile(p):
        return load_yaml(p)
    return None


# --------------------------------------------------------------- 解析
def resolve(name, offline=False):
    cpath = os.path.join(COMPOSITIONS, "%s.yaml" % name)
    if not os.path.isfile(cpath):
        return None, "未知 composition: %s" % name
    comp = load_yaml(cpath)
    cat = load_yaml(CATALOG)
    libs = {l["id"]: l for l in cat.get("libraries", [])}
    pins = read_pin()
    cr = cat.get("conflict_resolution", {})

    plan = {"composition": name, "description": comp.get("description", ""),
            "entries": [], "never_delegate": cr.get("never_delegate", [])}

    for inc in comp.get("include", []) or []:
        spec = inc.get("library", "")
        base, _, want = spec.partition("@")
        lib = libs.get(base)
        if lib is None:
            plan["entries"].append({"library": base, "tag": want or "?", "error": "未在 catalog.yaml 登记"})
            continue
        tag = want or pins.get(base, "") or lib.get("default_tag", "main")
        entry = {"library": base, "tag": tag, "type": lib.get("type"),
                 "authority": lib.get("authority", "domain"),
                 "priority": lib.get("priority", "normal"),
                 "label": lib.get("label", base), "skills": [], "paths": []}

        if lib.get("type") == "skills":
            lc, where = library_catalog(lib)
            if lc is None:
                entry["error"] = "拿不到 catalog.yaml"
            else:
                want_domains = set(inc.get("domains", []) or [])
                want_skills = set(inc.get("skills", []) or [])
                by_id = {s["id"]: s for s in lc.get("skills", [])}
                for sid, s in by_id.items():
                    dom = s.get("domain") or s.get("group") or ""
                    hit = (sid in want_skills) or (dom in want_domains and not want_skills) \
                          or (dom in want_domains and sid in want_skills)
                    if want_domains and dom in want_domains:
                        hit = True
                    if not hit:
                        continue
                    entry["skills"].append({
                        "id": sid, "name": s.get("name", sid),
                        "description": s.get("description", ""),
                        "path": s.get("path", ""),
                        "authority": s.get("authority", "primary"),
                        "superseded_by": s.get("superseded_by"),
                    })
                entry["source"] = where

        elif lib.get("type") == "spec":
            entry["paths"] = list(inc.get("paths", []) or [])

        elif lib.get("type") == "plugin":
            pm = plugin_manifest(base.split(":", 1)[1]) if ":" in base else None
            names = list(inc.get("skills", []) or [])
            if pm and pm.get("skills"):
                entry["plugin_skills"] = names or pm.get("skills", [])
                entry["plugin_version"] = pm.get("version", "?")
            else:
                entry["plugin_skills"] = names
                entry["plugin_version"] = "未扫描（跑 tools/scan_plugins.py 刷新）"
            entry["skills"] = [{"id": "%s/%s" % (base, n), "name": n,
                                "description": "插件技能", "path": "", "authority": "plugin"}
                               for n in entry["plugin_skills"]]

        plan["entries"].append(entry)
    return plan, None


# --------------------------------------------------------------- 输出
def print_plan(plan, inject=False):
    print("本次使用：composition=%s" % plan["composition"])
    if plan.get("description"):
        print("  说明: %s" % plan["description"])
    print()
    total = 0
    for e in plan["entries"]:
        if e.get("error"):
            print("  ! %s — %s" % (e["library"], e["error"]))
            continue
        head = "  库 %s@%s" % (e["library"], e["tag"])
        if e.get("priority") == "first":
            head += "   [插件：优先于我们的技能]"
        print(head)
        if e.get("type") == "spec":
            for p in e.get("paths", []):
                print("      文档 %s" % p)
            continue
        for s in e.get("skills", []):
            total += 1
            mark = ""
            if s.get("superseded_by"):
                mark = "  ← 让位给 %s" % s["superseded_by"]
            elif s.get("authority") == "fallback":
                mark = "  ← 仅插件缺失时用"
            if inject:
                print("      %s: %s" % (s["name"], s["description"]))
            else:
                print("      %-42s %s%s" % (s["id"], s["name"], mark))
    print()
    print("  技能数: %d" % total)
    if plan.get("never_delegate"):
        print("  不可委托给插件: " + "、".join(plan["never_delegate"]))
    return total


def write_lock(plan):
    rec = {
        "ts": datetime.datetime.now().isoformat(timespec="seconds"),
        "composition": plan["composition"],
        "libraries": [{"library": e["library"], "tag": e["tag"],
                       "skills": [s["id"] for s in e.get("skills", [])],
                       "paths": e.get("paths", [])}
                      for e in plan["entries"] if not e.get("error")],
    }
    with open(LOCK, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print("已写入 %s" % LOCK)
    return rec


def check(plan):
    if not os.path.isfile(LOCK):
        print("没有 lock.jsonl，无法比对。")
        return 1
    last = None
    for line in open(LOCK, encoding="utf-8"):
        line = line.strip()
        if line:
            last = json.loads(line)
    if last is None:
        print("lock.jsonl 为空。")
        return 1
    cur = {e["library"]: (e["tag"], sorted(s["id"] for s in e.get("skills", [])))
           for e in plan["entries"] if not e.get("error")}
    old = {e["library"]: (e["tag"], sorted(e.get("skills", [])))
           for e in last.get("libraries", [])}
    diffs = 0
    for lib in sorted(set(cur) | set(old)):
        if lib not in old:
            print("  + 新增库 %s@%s（%d 技能）" % (lib, cur[lib][0], len(cur[lib][1])))
            diffs += 1
        elif lib not in cur:
            print("  - 移除库 %s@%s" % (lib, old[lib][0]))
            diffs += 1
        else:
            ot, osk = old[lib]
            ct, csk = cur[lib]
            if ot != ct:
                print("  ~ %s 版本变了: %s -> %s" % (lib, ot, ct))
                diffs += 1
            added = [s for s in csk if s not in osk]
            removed = [s for s in osk if s not in csk]
            for s in added:
                print("    + %s" % s)
            for s in removed:
                print("    - %s" % s)
            diffs += len(added) + len(removed)
    print()
    print("差异 %d 处。" % diffs if diffs else "与上次解析一致。")
    return 0


def main():
    ap = argparse.ArgumentParser(description="skills-meta Loader")
    ap.add_argument("composition", nargs="?", help="composition 名")
    ap.add_argument("--list", action="store_true", help="列出所有 composition")
    ap.add_argument("--inject", action="store_true", help="只输出注入上下文的内容")
    ap.add_argument("--lock", action="store_true", help="写入 lock.jsonl")
    ap.add_argument("--check", action="store_true", help="与上次 lock 比对")
    ap.add_argument("--cache-dir", action="store_true", help="打印缓存目录")
    a = ap.parse_args()

    if a.cache_dir:
        print(CACHE)
        return 0
    if a.list:
        print("# compositions")
        for f in sorted(os.listdir(COMPOSITIONS)):
            if not f.endswith(".yaml"):
                continue
            c = load_yaml(os.path.join(COMPOSITIONS, f))
            print("  %-24s %s" % (c.get("name", f[:-5]), c.get("description", "")))
        return 0
    if not a.composition:
        ap.print_help()
        return 2

    plan, err = resolve(a.composition)
    if err:
        print(err, file=sys.stderr)
        return 1
    print_plan(plan, inject=a.inject)
    if a.lock:
        write_lock(plan)
    if a.check:
        check(plan)
    return 0


if __name__ == "__main__":
    sys.exit(main())
