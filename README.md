# skills-meta

> **多库元库（组合总线）** —— 把「我们有哪些库、这次任务该用哪几个、谁说了算」写成配置，
> 而不是靠 Agent 临场发挥。
>
> 依据：`agent-workspace-spec/08 篇` 的分发层设计。

---

## 它解决什么

我们有 5 个库、20+ 个插件、186 + 27 个技能。如果没有统一索引：

- Agent 不知道该去哪个库找，会在一个库里硬找
- 同一个能力在插件和我们的库里各有一份，不知道**谁权威**
- 库版本会漂移，不同任务加载到不同版本的技能

`skills-meta` 把这三点变成**配置**：

| 问题 | 机制 |
|---|---|
| 有哪些库 | `catalog.yaml` |
| 这次用哪几个 | `compositions/*.yaml` |
| 用哪个版本 | `pin` |
| 上次用了什么 | `lock.jsonl` |
| 插件和我们的技能冲突谁赢 | `conflict_resolution` + 各库 `catalog.yaml` 的 `superseded_by` |

---

## 目录结构

```
skills-meta/
├─ catalog.yaml            库登记表（id / type / url / local_path / authority）
├─ pin                     版本锁定（<库>@<tag>）
├─ lock.jsonl              解析流水（每次 resolve 记一条）
├─ compositions/           组合定义
│  ├─ one-person-company.yaml
│  ├─ business-ops.yaml
│  ├─ product-delivery.yaml
│  ├─ daily-coding.yaml
│  └─ hyperframes-video.yaml
├─ libraries/
│  └─ plugins/             插件清单（scan_plugins.py 生成）
└─ tools/
   ├─ resolve.py           Loader：解析 composition
   └─ scan_plugins.py      扫描本机已装插件
```

---

## 五种库

`catalog.yaml` 里 `type` 决定这个库怎么被用：

| type | 例子 | 怎么用 |
|---|---|---|
| `skills` | `agent-skills`、`opc-playbook` | 读它的 `catalog.yaml`，按 domain/skill 展开 |
| `spec` | `engineering-standard`、`design-skills-playbook`、`agent-workspace-spec` | 按 `paths` 列出的文档路径读 |
| `plugin` | `plugin:superpowers` | 读 `libraries/plugins/<name>.yaml` 的技能清单 |

---

## 用法

```bash
# 列出所有组合
python tools/resolve.py --list

# 解析一个组合：打印「库@tag + 技能 id 列表」
python tools/resolve.py one-person-company

# 只输出「要注入上下文的内容」（name: description）
python tools/resolve.py one-person-company --inject

# 解析并记一条流水
python tools/resolve.py one-person-company --lock

# 与上次解析比对（库版本变了 / 技能增减了）
python tools/resolve.py one-person-company --check

# 扫描本机插件并刷新清单
python tools/scan_plugins.py --refresh-agent-skills
```

`agent-skills` 侧也有一个薄封装：

```bash
python D:\agent-skills\tools\fetch.py --composition one-person-company
python D:\agent-skills\tools\fetch.py --pin-list
python D:\agent-skills\tools\fetch.py --cache-clear
```

---

## 五个组合

| 组合 | 用途 | 主库 |
|---|---|---|
| `one-person-company` | 一人公司经营主线：经营判断 + 增长 + 最小企业职能 | opc-playbook + agent-skills |
| `business-ops` | 企业职能事务：CRM、现金流、合同、招聘、运营、客服、财务、数据 | agent-skills |
| `product-delivery` | 需求澄清 → 设计 → 开发 → 复核 → 发布 | 三本规范库 + agent-skills |
| `daily-coding` | 日常写码：调试、代码理解、本机工具 | engineering-standard + superpowers |
| `hyperframes-video` | 视频管线：动效、网页转视频、素材与发布 | agent-skills(hyperframes) |

---

## 插件共存规则

写死在 `catalog.yaml` 的 `conflict_resolution` 里：

```yaml
conflict_resolution:
  order: [plugin, skills, spec]      # 冲突时先看插件
  key_field: superseded_by            # 冲突看这个字段
  fallback_field: fallback
  never_delegate:                     # 这八类永远不交给插件
    - 商业判断 / 经营层
    - OPC 经营层阶段机
    - idea-to-cash 产品层阶段机
    - 价值主张与商业模式
    - 设计令牌与设计评审
    - 企业运营（CRM / 现金流 / 竞品 / 销售漏斗）
    - 指标口径与实验设计
    - 交付发布与合规
```

**插件里有相近能力时（如 `positioning-statement`、`tam-sam-som-calculator`、
`business-health-diagnostic`），只能当「阶段内可引用的工具」，不能当「判断依据」。**
判断依据永远来自 `opc-playbook` 与 `agent-skills`。

本机实测扫描到 25 个插件目录，其中真正重叠的 4 个：

| 插件 | 技能数 | 与我们的关系 |
|---|---:|---|
| `superpowers` | 15 | 通用工艺，**插件主导**；我们的 `engineering/debug` 降为 fallback |
| `Product-Manager-Skills` | 46 | 通用 PM 工艺 + SaaS 指标，**插件主导**；不替代 OPC 经营层 |
| `plugin-dev` | 7 | Claude Code 侧插件/命令/Agent 开发，**插件主导**；与我们的 cowork 侧不冲突 |
| `skill-creator` | 1 | 写技能，**插件主导**；我们的 `agent-toolkit/optimize-skill-md` 降为 fallback |

---

## 版本锁定规则

- `pin` 固定**库的版本**，不固定技能列表（技能列表在 composition 里写死）
- **生产用的组合固定 tag，不固定 main。** 本地库尚未发版打 tag，暂固定分支；
  发版后改回 `vX.Y.Z`
- `lock.jsonl` 记录每次解析的「库@tag + 技能 id 列表」，用 `--check` 比对差异
  → 库升级了哪些技能变了，一眼可见

---

## 缓存

按 08 篇规范，缓存放在短路径：

```
~/.agent-skills-cache/<库名>@<tag>/
```

一键清理：`python D:\agent-skills\tools\fetch.py --cache-clear`
