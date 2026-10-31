#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
扫描本机已安装的 Agent 插件，生成 libraries/plugins/<name>.yaml。

插件清单是 skills-meta 的一等公民：composition 可以直接组合插件，
Loader 按「插件优先、我们兜底」的规则解析。

用法:
  python tools/scan_plugins.py                # 扫描并生成清单
  python tools/scan_plugins.py --json         # 只打印扫描结果
  python tools/scan_plugins.py --refresh-agent-skills   # 同时刷新 agent-skills 的 plugin_overlap.json

扫描位置（按优先级）:
  1. $CLAUDE_PLUGIN_ROOT
  2. ~/.claude/plugins
  3. ~/.agents/plugins
  4. ./.claude/plugins      （当前项目）
  5. ~/.agents/skills        （扁平技能目录，也当插件看待）
"""
import argparse
import datetime
import json
import os
import re
import sys

try:
    import yaml
except ImportError:
    yaml = None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "libraries", "plugins")
TODAY = datetime.date.today().isoformat()


def candidate_roots():
    """插件可能装在这些地方。"""
    roots = []
    env = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if env:
        roots.append(env)
    home = os.path.expanduser("~")
    roots += [
        os.path.join(home, ".claude", "plugins"),
        os.path.join(home, ".claude", "plugins", "marketplaces"),
        os.path.join(home, ".kimi-code", "plugins", "managed"),
        os.path.join(home, ".agents", "plugins"),
        os.path.join(home, ".agents", "skills"),
        os.path.join(home, ".skills-manager", "skills"),
        os.path.join(os.getcwd(), ".claude", "plugins"),
    ]
    # Claude Code 记录的 marketplace 安装位置
    mp = os.path.join(home, ".claude", "plugins", "known_marketplaces.json")
    if os.path.isfile(mp):
        try:
            with open(mp, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            for _name, info in (data or {}).items():
                loc = (info or {}).get("installLocation")
                if loc:
                    roots.append(loc)
        except Exception:
            pass
    seen, out = set(), []
    for r in roots:
        r = os.path.abspath(os.path.expanduser(r))
        if r not in seen and os.path.isdir(r):
            seen.add(r)
            out.append(r)
    return out


def plugin_of_dir(d):
    """一个目录算不算插件？返回 (name, skills[], version) 或 None。"""
    skills_dir = os.path.join(d, "skills")
    if not os.path.isdir(skills_dir):
        return None
    names = []
    for e in sorted(os.listdir(skills_dir)):
        p = os.path.join(skills_dir, e)
        if os.path.isdir(p) and os.path.isfile(os.path.join(p, "SKILL.md")):
            names.append(e)
    if not names:
        return None
    version = "unknown"
    for mf in (".claude-plugin/plugin.json", "plugin.json", "package.json"):
        p = os.path.join(d, mf)
        if os.path.isfile(p):
            try:
                with open(p, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                version = str(data.get("version", "unknown"))
                break
            except Exception:
                pass
    return {"name": os.path.basename(d), "skills": names, "version": version}


def scan():
    found = []
    for root in candidate_roots():
        for e in sorted(os.listdir(root)):
            d = os.path.join(root, e)
            if not os.path.isdir(d):
                continue
            info = plugin_of_dir(d)
            if info:
                info["root"] = root
                found.append(info)
                continue
            # 二级：root/<marketplace>/<plugin>
            for e2 in sorted(os.listdir(d)):
                d2 = os.path.join(d, e2)
                if not os.path.isdir(d2):
                    continue
                info = plugin_of_dir(d2)
                if info:
                    info["name"] = "%s/%s" % (e, e2)
                    info["root"] = d
                    found.append(info)
    # 同名插件按「版本最新」保留一份
    best = {}
    for p in found:
        k = p["name"]
        if k not in best or p["version"] > best[k]["version"]:
            best[k] = p
    return sorted(best.values(), key=lambda x: x["name"])


def write_manifests(plugins):
    os.makedirs(OUT_DIR, exist_ok=True)
    written = []
    for p in plugins:
        safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", p["name"])
        out = {
            "name": p["name"],
            "namespace": "plugin:%s" % p["name"],
            "type": "plugin",
            "version": p["version"],
            "updated": TODAY,
            "source": "local",
            "root": p.get("root", ""),
            "priority": "first",
            "authority": "process",
            "skills": p["skills"],
        }
        path = os.path.join(OUT_DIR, "%s.yaml" % safe)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            yaml.safe_dump(out, fh, allow_unicode=True, sort_keys=False,
                           default_flow_style=False, width=100)
        written.append(path)
    return written


def refresh_agent_skills(plugins):
    """把插件能力清单回写到 agent-skills/tools/plugin_overlap.json。"""
    path = r"D:\agent-skills\tools\plugin_overlap.json"
    if not os.path.isfile(path):
        print("找不到 %s，跳过" % path, file=sys.stderr)
        return False
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    for p in plugins:
        entry = None
        for e in data.get("plugins", []):
            if e.get("name") == p["name"]:
                entry = e
                break
        if entry is None:
            entry = {"name": p["name"], "namespace": "plugin:%s" % p["name"],
                     "source": "local", "status": "detected", "skills": []}
            data.setdefault("plugins", []).append(entry)
        entry["skills"] = p["skills"]
        entry["status"] = "detected"
        entry["version"] = p["version"]
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    print("已刷新 %s" % path)
    return True


def main():
    ap = argparse.ArgumentParser(description="扫描本机已安装插件")
    ap.add_argument("--json", action="store_true", help="只打印 JSON")
    ap.add_argument("--refresh-agent-skills", action="store_true",
                    help="同时刷新 agent-skills 的 plugin_overlap.json")
    a = ap.parse_args()

    plugins = scan()
    if a.json:
        print(json.dumps(plugins, ensure_ascii=False, indent=2))
        return 0

    if not plugins:
        print("没有扫描到任何插件。")
        print("扫描位置:")
        for r in candidate_roots():
            print("  %s" % r)
        print()
        print("如果插件装在别处，设 $CLAUDE_PLUGIN_ROOT 后重跑。")
        return 0

    print("扫描到 %d 个插件：\n" % len(plugins))
    for p in plugins:
        print("  %-28s %-18s %d 个技能" % (p["name"], p["version"], len(p["skills"])))
        print("      %s" % ", ".join(p["skills"][:12]) + (" ..." if len(p["skills"]) > 12 else ""))
    print()
    written = write_manifests(plugins)
    for w in written:
        print("已生成 %s" % w)
    if a.refresh_agent_skills:
        refresh_agent_skills(plugins)
    return 0


if __name__ == "__main__":
    sys.exit(main())
