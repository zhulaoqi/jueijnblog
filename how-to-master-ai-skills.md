# AI 工程的三条腿：两条有路标，一条在雾中

> RAG 有向量数据库和检索链的成熟范式，MCP 有 Anthropic 主导的开放协议和 5800+ 现成 Server——这两条路，照着走就行。但 Skill 不一样。它没有质量评审机制，没有统一的"好坏"标准，写一个 Markdown 就算创建了，至于 Agent 能不能正确激活、会不会吃掉半个上下文窗口、Token 账单月底会不会爆炸——全靠工程师自己摸索。
>
> 本文把 RAG 和 MCP 的"确定性"作为参照系，聚焦于 Skill 这个当前最模糊的环节——特别是上下文记忆管理和 Token 消耗控制这两个隐形地雷，试图为这片"无人区"画出第一张地图。

---

## 一、先看清楚地形：三条路的确定性差异

### 1.1 RAG——最成熟的路，闭着眼走

RAG（Retrieval-Augmented Generation）发展至今，已经形成了高度标准化的技术栈：

```
文档 → 切片 → Embedding → 向量数据库 → 检索 → Rerank → 注入上下文 → 生成
```

**为什么说 RAG "好办"：**

| 维度 | 现状 |
|------|------|
| 技术栈 | 成熟且确定：LangChain / LlamaIndex / Haystack 三大框架选一个 |
| 向量数据库 | Milvus / Pinecone / Weaviate / Qdrant，都有完善文档和基准测试 |
| 质量评估 | 有明确指标：Recall@K、MRR、Faithfulness、Answer Relevancy |
| 优化路径 | 清晰：切片策略 → Embedding 模型选择 → 检索算法 → Rerank → Prompt 工程 |
| 行业共识 | 大量论文、开源实现、生产案例可参考 |

RAG 的难点不在于"不知道怎么做"，而在于"做到多好"——这是优化问题，不是方向问题。

### 1.2 MCP——有协议就有路标

MCP（Model Context Protocol）由 Anthropic 发起，2025 年底捐赠给 Linux Foundation，2026 年 3 月已经是事实标准：

```
应用 → MCP Client → JSON-RPC 2.0 → MCP Server → 外部系统/API
```

**为什么说 MCP "好办"：**

| 维度 | 现状 |
|------|------|
| 协议规范 | 完整的 JSON-RPC 2.0 标准，有官方 Spec |
| SDK | 官方提供 TypeScript / Python SDK |
| 生态 | 97M+ 月下载量，5800+ 现成 Server，覆盖主流工具和服务 |
| 安全标准 | OAuth 2.1 + PKCE，有明确的权限模型 |
| 开发路径 | 定义 Tool Schema → 实现 Handler → 注册 Server，流程清晰 |
| 验证方式 | 工具调用是确定性的——调成功就是成功，报错就是报错 |

MCP Server 好不好，跑一次就知道——API 调通了、数据对了，就是好的。它的"质量"可以被客观验证。

### 1.3 Skill——雾中行走

然后看 Skill：

```
写一个 SKILL.md → 放进文件夹 → ……然后呢？
```

**Skill 为什么"不好办"：**

| 维度 | 现状 |
|------|------|
| 规范 | 有格式规范（agentskills.io），但没有**质量**规范 |
| 质量评估 | 没有 Recall@K 那样的客观指标，"好不好用"全凭主观感受 |
| 验证困难 | Agent 是否正确激活了？激活后行为是否符合预期？每次一样吗？ |
| 成本黑箱 | 一个 Skill 吃掉多少 Token？对上下文窗口的挤压有多大？不透明 |
| 副作用 | 一个 Skill 的 description 可能"抢走"其他 Skill 的触发机会 |
| 最佳实践 | 散落在博客、推文、个人经验中，没有体系化的方法论 |

**一句话总结这个差异：**

> **RAG 的质量可以测量，MCP 的质量可以验证，但 Skill 的质量只能"感觉"。**

这就是问题所在。

---

## 二、Skill 到底难在哪：两个隐形地雷

技术社区讨论 Skill 时往往聚焦于"怎么写 SKILL.md"，但真正让 Skill 难以把控的，是两个很少被讨论的底层问题。

### 2.1 地雷一：上下文记忆——Skill 在和谁抢空间？

LLM 的上下文窗口是一个**零和博弈的竞技场**。每次对话中，以下内容都在争夺同一块有限的空间：

```
┌──────────────────────────────────────────────────────────┐
│                上下文窗口（例：128K tokens）                │
│                                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │  System Prompt + Rules    ~2K-5K tokens           │    │
│  ├──────────────────────────────────────────────────┤    │
│  │  已激活的 Skill 内容      ~2K-5K tokens / 每个     │ ←  │
│  ├──────────────────────────────────────────────────┤    │
│  │  Skill 发现索引           ~100 tokens × Skill 数   │    │
│  ├──────────────────────────────────────────────────┤    │
│  │  MCP Tool Schemas         ~200 tokens × Tool 数    │    │
│  ├──────────────────────────────────────────────────┤    │
│  │  对话历史（记忆）          随对话增长               │ ←  │
│  ├──────────────────────────────────────────────────┤    │
│  │  RAG 检索结果             ~1K-5K tokens            │    │
│  ├──────────────────────────────────────────────────┤    │
│  │  当前任务上下文（代码等）   变化很大                 │    │
│  ├──────────────────────────────────────────────────┤    │
│  │  模型输出空间              需要预留                 │    │
│  └──────────────────────────────────────────────────┘    │
│                                                          │
│  标 ← 的部分就是 Skill 直接影响的区域                      │
└──────────────────────────────────────────────────────────┘
```

**问题的本质**：Skill 的内容在"激活"阶段被注入上下文，它和对话历史、RAG 结果、其他 Skill 共享同一个上下文窗口。每多加载一个 Skill，留给"真正干活"的空间就少一块。

**这带来三个具体问题**：

**问题 1：Skill 越多，每个 Skill 的效果越差**

```
场景：你有 200 个 Skill

仅 Skill 发现索引：200 × 100 tokens = 20,000 tokens
假设同时激活 3 个：  3 × 4000 tokens  = 12,000 tokens
合计 Skill 占用：                       32,000 tokens

128K 窗口中，25% 被 Skill 基础设施吃掉了
留给对话历史 + 任务上下文 + 输出的只剩 96K
```

这还没算 System Prompt、Rules、MCP Schemas。在实际生产环境中，**真正留给"干活"的上下文可能只有窗口的 50-60%**。

**问题 2：长对话中 Skill 和记忆互相挤压**

```
对话第 1 轮：上下文充裕
├── Skill 正常加载、正常执行 ✅
└── 对话历史很短，空间富余

对话第 20 轮：上下文紧张
├── 对话历史已膨胀到 40K+ tokens
├── Skill 内容被"挤到"上下文的边缘
├── 模型对 Skill 指令的遵循度开始下降 ⚠️
└── 可能出现"忘记"Skill 约束的行为 ❌

对话第 50 轮：上下文溢出
├── 早期对话被截断
├── Skill 可能被部分丢弃
└── Agent 行为变得不可预测 ❌❌
```

这就是为什么同一个 Skill 在短对话中表现完美，在长对话中突然"失忆"——**不是 Skill 变差了，是它被对话历史挤出了模型的注意力范围。**

**问题 3："大海捞针"——Skill 在上下文中的位置影响效果**

LLM 对上下文信息的注意力分布是不均匀的。研究表明：

```
注意力强度
  ▲
  │ ████                                    ████
  │ ████                                    ████
  │ ████                                    ████
  │ ████                                    ████
  │ ████  ██                            ██  ████
  │ ████  ████                        ████  ████
  │ ████  ████  ████████████████████  ████  ████
  └──────────────────────────────────────────────▶
   开头              中间                    末尾

   模型对开头和末尾的信息记忆最牢
   中间段落容易被"遗忘"
```

如果你的 Skill 内容恰好被加载到上下文的中间位置，它的约束力会大打折扣——Agent 可能读到了但"不太在意"。

### 2.2 地雷二：Token 消耗——一笔算不清的账

RAG 的成本好算：检索 Top-5 段落，每段约 500 tokens，每次请求额外消耗 ~2500 input tokens。

MCP 的成本好算：Tool Schema 一次加载，每次调用的参数和结果 token 数基本稳定。

**但 Skill 的成本是"叠加的、隐性的、不可预测的"。**

**隐性成本一：发现阶段的"税"**

每次对话，Agent 都要扫描所有 Skill 的 description 来决定激活哪个。这是一笔"固定税"：

```
Skill 数量    发现阶段成本        年化成本（按 100 次/天算）
10 个         ~1,000 tokens      ≈ $27/年
50 个         ~5,000 tokens      ≈ $137/年
200 个        ~20,000 tokens     ≈ $547/年
500 个        ~50,000 tokens     ≈ $1,369/年
```

Skill 越多，即使一个都没被激活，你也在付"浏览菜单"的钱。

**隐性成本二：激活阶段的"尺寸税"**

同样功能的 Skill，写法不同，成本差距巨大：

```
精简版 SKILL.md：~150 行，约 2,000 tokens
├── 每次激活成本：$0.005（GPT-4o input）
├── 每天 100 次：$0.50
└── 每月：$15

冗余版 SKILL.md：~600 行，约 8,000 tokens
├── 每次激活成本：$0.020
├── 每天 100 次：$2.00
└── 每月：$60

同一个 Skill，冗余写法一年多花 $540
如果你有 20 个这样的 Skill：一年多花 $10,800
```

**隐性成本三：挤压效应的间接成本**

这是最难算的一笔账——Skill 占了上下文空间，导致：
- 对话历史被截断 → 用户需要重复说明需求 → 额外 token 消耗
- 模型对 Skill 指令遵循度下降 → 输出质量下降 → 人工检查成本上升
- Agent 需要更多轮对话完成任务 → 每轮都重复消耗 Skill tokens

**这些间接成本无法被直接测量，但它们是真实存在的。**

### 2.3 为什么 RAG 和 MCP 不存在这个问题

| 维度 | RAG | MCP | Skill |
|------|-----|-----|-------|
| 加载时机 | 按需检索，只在需要时 | Tool Schema 一次加载 | 发现阶段永远消耗 + 激活阶段按需 |
| 成本可预测性 | 高（检索 Top-K，K 固定） | 高（Schema 大小固定） | 低（取决于写法和激活数量） |
| 质量可测量性 | 高（Recall/MRR/Faithfulness） | 高（调用成功/失败） | 低（主观判断） |
| 对上下文的影响 | 可控（只注入相关片段） | 可控（Schema 固定大小） | 不可控（取决于 Skill 内容长度） |
| 冗余惩罚 | 低（检索算法过滤） | 无（精确调用） | 高（写多少加载多少） |

**结论**：RAG 和 MCP 的成本是"确定性"的——你能提前算出来；Skill 的成本是"概率性"的——取决于写了多少、写得多长、激活了几个、对话进行到第几轮。

---

## 三、既然这么难，Skill 的正确打开方式是什么

### 3.1 首先接受一个现实

> **Skill 的质量，在当前阶段，本质上是一个"工程审美"问题，而非"工程规范"问题。**

RAG 可以跑 benchmark，MCP 可以跑集成测试，但 Skill——你只能写完之后让 Agent 跑一遍，然后凭经验判断"这个行为对不对"。

这不是你的问题，是行业现状。agentskills.io 提供了格式规范（YAML frontmatter 怎么写、文件夹结构怎么放），但它**没有也无法提供质量规范**——因为 Skill 的"好坏"取决于：

1. Agent 是否在该激活时激活了（受 description 影响）
2. 激活后行为是否符合预期（受指令影响）
3. 消耗的 Token 是否值得（受写法影响）
4. 在多 Skill 共存时是否互相干扰（受生态影响）

这四个维度，每一个都带有主观性和上下文依赖性。

### 3.2 我们能做到的：建立自己的质量标尺

既然行业没给标准，我们就自己建。以下是一个可落地的质量评估框架：

#### 第一把尺：description 质量（决定 Skill 的"生死"）

```
好的 description 必须包含三要素：
  WHAT ——做什么
  WHEN ——什么时候用（触发条件）
  NOT  ——什么时候不用（排除条件）

自测方法：
  把你的 description 混进 50 个其他 Skill 的 description 中
  读一遍，问自己：3 秒内能判断"这个 Skill 该在什么场景激活"吗？
  不能 → 重写
```

**反面教材 vs 正面教材**：

```yaml
# ❌ 差——只说了 WHAT，Agent 不知道何时该激活
description: Processes PDF files

# ❌ 差——太泛，和其他 Skill 区分不开
description: A useful tool for developers

# ✅ 好——WHAT + WHEN + NOT + 关键词
description: >
  Extract text and tables from PDF files, fill forms,
  merge documents. Use when working with PDF files or
  when user mentions PDFs, forms, or document extraction.
  NOT for image-only PDFs requiring OCR.
```

#### 第二把尺：Token 效率（决定 Skill 的"性价比"）

**500 行红线**：SKILL.md 超过 500 行会可测量地降低 Agent 执行质量。不是建议，是经过验证的阈值。

**每段自检**：对文档中的每一段，问——"如果删掉这段，Agent 还能正确执行吗？" 如果能，删。

**常见冗余 vs 精简写法**：

| 冗余写法 | 精简写法 | Token 节省 |
|---------|---------|-----------|
| "This skill should be used when the user wants to" | "Use when" | ~70% |
| "The purpose of this skill is to help you" | 直接写功能 | ~75% |
| 三段话解释 HTTP 协议是什么 | 删掉（AI 知道） | 100% |
| 列举 8 个可选库不给推荐 | 给一个默认 + 两个备选 | ~60% |

**核心纪律：不要教 AI 它已经知道的事。只写你公司/你项目特有的知识。**

#### 第三把尺：激活准确率（决定 Skill 的"可靠性"）

```
测试方法：

准备 10 个"应该激活"的 Prompt：
  "帮我写个 commit message"
  "review 一下这段代码"
  "部署到 staging 环境"
  ...

准备 10 个"不应该激活"的 Prompt：
  "帮我画个架构图"
  "解释一下 TCP 三次握手"
  "今天天气怎么样"
  ...

跑 20 次，记录：
  正确激活数 / 应激活数 = 触发率（目标 >90%）
  错误激活数 / 不应激活数 = 误触率（目标 <5%）
```

#### 第四把尺：执行一致性（决定 Skill 的"可信度"）

```
测试方法：

用同一个 Prompt 触发同一个 Skill 5 次
比较 5 次输出：
  结构是否一致？（格式、章节、标题）
  关键步骤是否一致？（顺序、命令、约束）
  约束是否被遵守？（每次都遵守 vs 时遵时违）

一致性 < 80% → Skill 指令太模糊，需要加约束
一致性 > 95% → 达到生产质量
```

### 3.3 上下文管理的实操策略

既然上下文空间是零和博弈，就需要有策略地管理 Skill 对上下文的占用：

**策略一：渐进式披露——用文件引用换上下文空间**

```
❌ 全部塞进 SKILL.md（8000 tokens）

✅ 分层存放（主文件 2000 tokens）

my-skill/
├── SKILL.md              # 核心指令（<200 行）
│     └── "详细 API 文档见 references/api.md"
│     └── "示例见 examples/"
├── references/
│   └── api.md            # Agent 只在需要时读取
└── examples/
    └── good-output.md    # Agent 只在需要时读取
```

核心技巧：SKILL.md 中用链接引用子文件，Agent 只在执行到相关步骤时才按需读取——脚本执行更是 **0 额外 token**。

**策略二：控制 Skill 总数**

```
项目级 Skill 建议：    ≤ 20 个
全局 Skill 建议：      ≤ 10 个
合计发现阶段成本：     ≤ 3,000 tokens（可接受）

如果超过 30 个 Skill → 问自己：
  有没有可以合并的？
  有没有几乎不被激活的？（删掉）
  有没有应该降级为 Rule 的？（约束类指令）
```

**策略三：短 description，长正文**

这是一个反直觉的写法：description 要尽可能短（因为它被所有 Skill 共同支付），正文可以适当长（因为只有被激活的 Skill 才支付正文成本）。

```yaml
# ❌ description 太长——每次对话都要支付这 200 tokens
description: >
  This skill is designed to help engineers who are working on
  PostgreSQL database migrations. It generates migration scripts
  with proper up and down migrations, handles transactions,
  supports concurrent index creation, and follows best practices
  for zero-downtime deployments. Use when you need to create,
  modify, or remove database tables, columns, indexes, or
  constraints in a PostgreSQL database...

# ✅ description 精简——每次只支付 40 tokens
description: >
  Generate PostgreSQL migration scripts (up/down).
  Use when creating, altering, or dropping tables/columns/indexes.
```

**策略四：在长对话中主动"提醒"**

如果你的工作流会产生长对话（20+ 轮），在关键步骤前主动提及 Skill 名称，帮助 Agent "回忆"：

```
用户第 25 轮：
"按照 release-workflow 的流程，开始发布 v2.3.0"
  ↑ 显式提及 Skill 名称，强化 Agent 对该 Skill 的注意力
```

---

## 四、动手：从第一个 Skill 到生产级

### 4.1 你的第一个 Skill（15 分钟）

```
mkdir -p .cursor/skills/git-commit-helper
```

创建 `.cursor/skills/git-commit-helper/SKILL.md`：

````markdown
---
name: git-commit-helper
description: >
  Generate conventional commit messages from staged changes.
  Use when committing, writing commit messages, or reviewing
  staged changes. NOT for git operations like merge or rebase.
---

# Git Commit Message Generator

## Format

```
<type>(<scope>): <subject>

<body>
```

## Types

| Type | When |
|------|------|
| feat | New feature |
| fix | Bug fix |
| refactor | Code restructure, no behavior change |
| docs | Documentation only |
| test | Adding or fixing tests |
| chore | Build, deps, config |

## Process

1. Run `git diff --cached`
2. Analyze change nature → pick type
3. Identify scope (module/component name)
4. Write subject: imperative mood, max 72 chars, no period
5. Add body only if change is non-trivial (explain WHY, not WHAT)
````

验证方式：
- 输入 `/git-commit-helper` → 显式激活
- 输入 "帮我写个 commit message" → 隐式触发
- 输入 "帮我做 git rebase" → 不应激活（检查 NOT 条件）

### 4.2 五种 Skill 编写模式

| 模式 | 适用场景 | 核心特征 |
|------|---------|---------|
| **步骤清单** | 有明确先后顺序的操作 | 1→2→3 线性流程 |
| **条件分支** | 需要根据情况走不同路径 | if/else 决策树 |
| **模板输出** | 输出格式有严格要求 | 提供精确模板 |
| **正反示例** | 质量依赖"品味" | Good vs Bad 对照 |
| **反馈循环** | 质量关键、需自我验证 | 做→验→改→再验 |

**最有效的实战策略：去抄标杆。** 你本地就有生产级 Skill 可以参考：

- `~/.cursor/skills-cursor/create-skill/SKILL.md` —— Cursor 官方的"元 Skill"
- superpowers 插件的 `systematic-debugging/SKILL.md` —— 297 行，四阶段流程，硬门禁设计
- superpowers 插件的 `brainstorming/SKILL.md` —— 复杂流程编排，带 Checklist 和退出条件

### 4.3 七个必须避开的坑

从大量真实 Skill 审查中提炼：

| # | 反模式 | 后果 | 修复 |
|---|-------|------|------|
| 1 | description 只写了"做什么"，没写"什么时候用" | Skill 永远不被自动触发 | 加 "Use when..." |
| 2 | 一个 Skill 覆盖整个领域（"万能 Skill"） | 上下文浪费 + 激活误判 | 拆成多个聚焦 Skill |
| 3 | 教 AI 它已经知道的事（解释 HTTP、JSON……） | 浪费 30-50% 上下文 | 只写项目特有知识 |
| 4 | 空标题（有 ## 没内容） | 浪费 Token + 迷惑 Agent | 有内容就写，没内容就删 |
| 5 | 列一堆选项不给推荐 | Agent 每次选不同的 | 给默认选择 + 逃生通道 |
| 6 | 引用不存在的文件 | Agent 报错或幻觉 | 只引用真实存在的文件 |
| 7 | SKILL.md 超过 500 行 | 可测量地降低执行质量 | 主文件精简，详细内容放子文件 |

---

## 五、Skill vs Rule：什么时候用哪个

这是很多人混淆的点，一个判断标准讲清楚：

```
你想让 AI...

├── "一直记住某个规矩"
│     没有步骤，只是约束/偏好
│     例：必须用 const、组件必须函数式、不准用 eval
│     └── → Rule（.cursor/rules/xxx.mdc）
│           alwaysApply: true 或 globs: **/*.ts
│           每次对话都加载，确定性
│
└── "在特定场景下按特定流程做事"
      有明确步骤，按需触发
      例：部署流程、代码审查、数据库迁移
      └── → Skill（.cursor/skills/xxx/SKILL.md）
            Agent 自动判断是否激活
            只在需要时加载

简化判断：有"步骤"的用 Skill，没"步骤"的用 Rule
```

| 技术特性 | Rule (.mdc) | Skill (SKILL.md) |
|---------|-------------|-------------------|
| 加载方式 | 配置驱动（确定性） | Agent 判断（智能） |
| Token 消耗 | 每次对话都消耗（alwaysApply） | 只在激活时消耗 |
| 跨平台 | Cursor 专属 | 开放标准（Cursor/Claude/Codex） |
| 适合内容 | 约束、规范、禁止项 | 流程、操作、多步骤任务 |
| 推荐长度 | < 50 行 | < 500 行 |

---

## 六、Skill 质量评分框架

行业没有给我们标准，我们自己建。以下评分表可直接用于团队内部的 Skill 质量审查：

| 维度 | 权重 | 5 分（优秀） | 3 分（合格） | 1 分（不合格） |
|------|------|-------------|-------------|---------------|
| **description 质量** | 25% | WHAT + WHEN + NOT + 关键词 | 有 WHAT 和 WHEN | 只有模糊描述 |
| **激活准确率** | 20% | 正确激活 >90%，误触 <5% | 正确 >70% | 正确 <50% |
| **Token 效率** | 20% | <200 行，无冗余 | <500 行 | >500 行或大量废话 |
| **步骤清晰度** | 15% | 无歧义，有约束，有退出条件 | 可理解但有模糊 | 含糊或缺失 |
| **执行一致性** | 10% | 5 次执行 >95% 一致 | >80% | <60% |
| **错误处理** | 10% | 有明确异常路径和边界 | 提到了错误处理 | 未考虑异常 |

**评分示例**：

```
Skill: systematic-debugging（superpowers 内置）

description:    5/5 — 明确 WHEN（"any bug, test failure, unexpected behavior"）
激活准确率:     5/5 — 遇到 bug 稳定触发
Token 效率:     4/5 — ~300 行，内容密度高
步骤清晰度:     5/5 — 四阶段流程 + 硬门禁 + 退出条件
执行一致性:     5/5 — "NO FIXES WITHOUT ROOT CAUSE" 确保行为一致
错误处理:       5/5 — "修 3 次还没好 → 停下质疑架构"

总分: 4.85/5 — 生产级标杆
```

---

## 七、结语：确定性的归确定性，模糊的用方法论

回到开头的类比：

**RAG** —— 一条铺好的公路。有路标、有限速、有导航。你只需要开好车。

**MCP** —— 一条有标准的铁轨。有协议、有 SDK、有生态。你只需要造好车厢。

**Skill** —— 一片有方向但没有路的原野。有大致的方向（agentskills.io），有先行者的脚印（superpowers、ClawHub），但没有路标，没有限速牌，甚至没有"你走对了"的确认。

这就是 2026 年 3 月的现实。

但"没有路标"不等于"没有方法"。本文试图提供的就是在这片原野上行走的方法论：

1. **承认模糊性** —— Skill 的质量无法像 RAG 那样用 Recall@K 度量，这不是你的问题
2. **建立自己的尺子** —— 用 description 质量 / 激活准确率 / Token 效率 / 一致性四维度评估
3. **敬畏上下文** —— 每一行 Skill 都在跟对话记忆和任务上下文抢空间，写少就是写好
4. **抄标杆起步** —— 不要从零开始，从 superpowers 和 Cursor 内置 Skill 抄结构
5. **测了才算数** —— 写完不是终点，跑 5 次看一致性、看激活率，用数据替代感觉

Skill 的门槛确实低——会写 Markdown 就能创建。

**但写出一个在上下文紧张时仍然稳定工作、Token 消耗合理、不干扰其他 Skill 的生产级 Skill——这需要的不是 Markdown 技巧，而是对 LLM 运行时机制的深刻理解。**

这篇文档，就是这个理解的起点。

---

*本文系 AI 工程实践探索，欢迎交流指正。*

*最后更新：2026 年 3 月*
