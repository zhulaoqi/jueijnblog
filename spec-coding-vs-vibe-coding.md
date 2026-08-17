# Spec Coding vs Vibe Coding：AI 编程的两条路线，你选哪条？

> 2025 年 2 月，Andrej Karpathy 一条推文让 "Vibe Coding" 火遍全球。一年后，"Spec-Driven Development" 成为工程圈的新共识。两种范式之争的背后，是 AI 编程工业化进程中最核心的问题：**速度和质量，如何兼得？**

## 一个真实的故事

周一，团队用 Cursor 的 Agent 模式花 3 小时搭完了一个内部管理后台的原型，老板很满意，说"下周上线"。

周五，你打开代码发现：

- 认证模块的逻辑散落在 6 个文件里，没人说得清中间件的调用顺序
- 有 3 处几乎一样的数据校验逻辑，但参数微妙不同
- 改一个表单字段，3 个页面同时崩溃
- 没有一行测试

你加了两天班修补，改好一个 Bug，冒出三个新的。最终不得不重写整个认证流程。

这不是个例。GitClear 对 2.11 亿行代码的研究显示：AI 工具普及后，**重构活动下降约 60%，代码复制粘贴率上升 48%**，复制粘贴行数在 2024 年首次超过重构行数。

问题不在 AI 不够聪明——**在于我们使用 AI 的方式。**

## 两种范式的定义

### Vibe Coding：凭感觉写代码

2025 年 2 月，OpenAI 联合创始人、前特斯拉 AI 总监 Andrej Karpathy 在 X 上写道：

> "There's a new kind of coding I call **vibe coding**, where you fully give in to the vibes, embrace exponentials, and forget that the code even exists."

他描述的工作流是：**你说需求，AI 写代码，你看效果，再说调整，循环往复**——全程不需要逐行审查代码。

这条推文获得超过 450 万次浏览，"Vibe Coding" 被 Merriam-Webster 收录，并当选 Collins 词典 2025 年度词汇。

**核心工作流：**

```
描述需求（自然语言） → AI 生成代码 → 运行查看效果 → 反馈调整 → 循环迭代
```

**关键特征：**

- 不写规格文档，直接对话
- 不逐行审查 AI 生成的代码
- 开发者从"代码编写者"变为"意图表达者"
- 速度极快，适合探索和原型

### Spec Coding（Spec-Driven Development）：先写规格再写代码

Spec-Driven Development 是 AI 编程的结构化方法论。核心思想来自一篇提交至 AIWare 2026 的 arXiv 论文：

> "The specification is the primary artifact, and code is entirely derived from it."（规格说明书是首要产物，代码完全从中派生。）

**核心工作流：**

```
定义规格（What & Why） → 技术方案设计（How） → 拆分任务 → AI 逐任务实现 → 验证对齐
```

**关键特征：**

- 规格文档是唯一的事实来源（Single Source of Truth）
- AI 在明确的约束下生成代码，而非自由发挥
- 每个变更都可追溯到具体的规格条目
- 前期投入大，但长期收益高

## 在 Claude Code 和 Cursor 中的实践

理论说完，我们落到实际工具上。以下是两种范式在 Claude Code 和 Cursor 中的具体工作方式。

### Vibe Coding 实践

#### 在 Cursor 中

Cursor 天然是 Vibe Coding 的最佳载体。它的 Composer Agent 模式让你可以用自然语言驱动整个开发过程：

```
你在 Composer 中输入：
"帮我创建一个用户管理模块，支持 CRUD 操作，用 Element Plus 的表格组件，
 要有搜索、分页、新增和编辑的弹窗"

Cursor Agent 会：
1. 创建路由文件
2. 生成页面组件（表格 + 搜索 + 弹窗）
3. 创建 API 请求函数
4. 添加 Pinia store
5. 注册路由

你查看效果，继续输入：
"搜索要支持按角色筛选，表格加上批量删除功能"

Agent 继续修改，如此迭代...
```

**优势：** 多文件编辑能力强，可视化 IDE 体验流畅，模型可切换（Claude/GPT/Gemini），`.cursorrules` 提供项目级上下文。

**局限：** 随着对话变长，上下文可能被截断（实际可用约 70K-120K token）；对大型仓库的深层理解不如终端工具。

#### 在 Claude Code 中

Claude Code 的终端原生体验同样支持快速迭代：

```bash
# 直接在终端中描述需求
claude "帮我实现一个 WebSocket 实时通知系统，
       支持消息推送、在线状态和未读计数"

# Claude Code 会自主：读文件、编辑代码、运行测试、修复错误
# 你看到效果后继续对话
claude "加上消息持久化，用 Redis 存储最近 100 条"
```

**优势：** 200K 可靠上下文窗口（1M Beta），token 效率是 Cursor 的 5.5 倍，Agent Teams（多智能体协作）。

**局限：** 纯终端界面，学习曲线陡峭，不适合视觉化开发场景。

### Spec Coding 实践

#### 在 Claude Code 中

Claude Code 的 `CLAUDE.md` 机制是 Spec Coding 的天然基础设施。它是**持久化的项目记忆**，每次对话自动加载：

```markdown
# CLAUDE.md（项目根目录）

## 架构原则
- Clean Architecture 四层分离
- 依赖方向：外层 → 内层，内层不知道外层存在
- 新增路由只做参数提取和响应格式化，业务逻辑放 service

## 安全约束
- 敏感数据必须 AES 加密存储
- API Key 使用 SHA-256 哈希存储，禁止明文
- 每个请求必须经过完整认证链

## 代码风格
- 无分号、单引号、100字符行宽
- 必须使用 Prettier 格式化
```

结合 Spec 工作流工具（如 `claude-code-spec-workflow`），完整流程是：

```
Step 1: 写规格文档
────────────────
claude "基于以下需求写一份技术规格文档：
       - 功能：多账户调度器
       - 支持粘性会话、并发控制、529 过载保护
       - 需要和现有的 accountService 集成"

→ 产出：spec.md（需求定义 + 接口契约 + 数据模型 + 边界条件）

Step 2: 评审规格
────────────────
人工审查 spec.md，确认架构决策和边界条件

Step 3: 拆分任务
────────────────
claude "根据 spec.md 拆分为可独立实现的开发任务，
       每个任务包含：输入、输出、测试标准"

→ 产出：tasks.md（5-8 个原子任务）

Step 4: 逐任务实现
────────────────
claude "实现任务 1：创建 SchedulerBase 基类，
       严格按照 spec.md 中的接口定义"

Step 5: 验证对齐
────────────────
claude "对比 spec.md 和当前实现，检查是否有偏离"
```

研究表明，使用 `CLAUDE.md` 配置的结构化开发，相比随意对话的方式，**缺陷率降低 1.7 倍，安全漏洞减少 2.74 倍**。

#### 在 Cursor 中

Cursor 通过 `.cursor/rules/` 目录实现类似的规格约束：

```markdown
<!-- .cursor/rules/architecture.mdc -->
---
description: 架构规范
globs: src/**/*.{js,ts,vue}
---

## 分层架构
- routes/ 只做参数提取和响应格式化
- services/ 处理业务逻辑
- models/ 定义数据模型
- utils/ 放工具函数

## 命名约定
- Service 文件用 camelCase + Service 后缀
- Route 文件用 camelCase + Routes 后缀
- 测试文件和源文件同名 + .test.js

## 禁止
- 禁止在 route 中直接操作数据库
- 禁止在 service 中直接返回 HTTP 响应
```

Cursor 还支持通过 Plan Mode 先做方案设计，再切换到 Agent Mode 执行：

```
Plan Mode：
"分析当前认证系统的架构，设计新的多因子认证方案，
 给出文件变更清单和影响范围评估"

→ 产出方案文档，人工确认

Agent Mode：
"按照上述方案，开始实现第一步：创建 MFA service"
```

## 深度对比分析

### 维度一：适用场景

| 场景 | Vibe Coding | Spec Coding | 推荐 |
|------|:-----------:|:-----------:|:----:|
| 周末个人项目 | ★★★★★ | ★★☆☆☆ | Vibe |
| Hackathon / Demo | ★★★★★ | ★☆☆☆☆ | Vibe |
| 学习新技术框架 | ★★★★☆ | ★★☆☆☆ | Vibe |
| MVP 原型验证 | ★★★★★ | ★★★☆☆ | Vibe |
| 内部工具 / 脚本 | ★★★★☆ | ★★★☆☆ | Vibe |
| 生产系统新功能 | ★★☆☆☆ | ★★★★★ | Spec |
| 多人协作项目 | ★★☆☆☆ | ★★★★★ | Spec |
| 企业级系统 | ★☆☆☆☆ | ★★★★★ | Spec |
| 合规 / 审计要求 | ★☆☆☆☆ | ★★★★★ | Spec |
| 长期维护系统（>3个月） | ★☆☆☆☆ | ★★★★★ | Spec |

### 维度二：效率曲线

两种方法的效率不是线性的，而是随时间呈现截然不同的曲线：

```
开发效率
  ^
  |      Vibe Coding
  |     /‾‾‾‾‾\
  |    /        \
  |   /          \  ← "三个月之墙"
  |  /            \___________  ← 技术债务拖累
  | /
  |/    Spec Coding
  |        ___________________  ← 稳定高效
  |       /
  |      /  ← 前期投入期
  |     /
  |____/
  +──────────────────────────→ 时间
       1月   3月   6月   12月
```

Codebridge 研究记录了 Vibe Coding 项目的典型衰减模式：

| 阶段 | 时间线 | 特征 |
|------|--------|------|
| 兴奋期 | 第 1-3 月 | 快速交付，速度惊人 |
| 平台期 | 第 4-9 月 | 集成问题浮现，修一个崩三个 |
| 衰退期 | 第 10-15 月 | 新功能需要大量调试旧代码 |
| 停滞期 | 第 16-18 月 | 交付停止，团队无人理解系统全貌 |

### 维度三：团队协作

| 方面 | Vibe Coding | Spec Coding |
|------|-------------|-------------|
| 知识载体 | 聊天记录 + 生成的代码 | 版本化的规格文档 |
| 新人上手 | 需要考古聊天历史和逆向工程代码 | 阅读规格文档即可理解 |
| 变更追溯 | 几乎不可能 | 每个变更关联规格条目 |
| 并行开发 | 容易产生冲突和不一致 | 基于规格分工，边界清晰 |
| Code Review | 审查 AI 生成的大段代码 | 审查是否符合规格的小段变更 |

GitHub 的 Spec-Driven Development 文档一针见血：

> "Instead of reviewing thousand-line code dumps, you review focused changes that solve specific problems."
> （不再审查上千行的代码倾泻，而是审查解决具体问题的聚焦变更。）

### 维度四：代码质量

CMU 对 Cursor 使用的研究发现，AI 工具采用后**代码复杂度增加约 41%，静态分析告警增加 30%**。这些技术债务会逐步蚕食未来的开发速度。

Towards AI 的研究更直接：**代码重复率最高增加了 8 倍**，因为"模型生成自包含的代码片段，而不是发现和复用已有的抽象"。

Spec Coding 通过规格约束直接对抗这个问题——AI 在有明确上下文和架构约束的情况下，生成的代码质量显著更高。

## 实战：同一需求的两种实现路径

假设需求是：**为系统添加 API 限流功能，支持按用户、按模型的细粒度控制**。

### 路径一：Vibe Coding

```
开发者：帮我加一个 API 限流功能，支持按用户和模型限制

AI：好的，我来实现...
    [生成 rateLimiter.js — 200 行]
    [修改 auth.js 中间件 — 添加限流检查]
    [修改 3 个路由文件]

开发者：还要支持不同用户不同限额

AI：好的，我来修改...
    [重写 rateLimiter.js 的大部分逻辑]
    [新增 userQuota.js]
    [修改 Redis 存储结构]

开发者：之前的按模型限制好像不工作了

AI：让我看看... 确实，在重构时遗漏了，我来修复...
    [再次修改 rateLimiter.js]
    [patch auth.js]

...反复 5-6 轮后，功能基本可用，但：
- 限流逻辑散布在 4 个文件中
- 有 2 处重复的计数逻辑
- 没有测试
- 没人能解释为什么 Redis Key 的结构是这样的
```

### 路径二：Spec Coding

```
Step 1 — 规格定义：

## 限流系统规格

### 目标
为 API 请求添加多维度限流，保护上游服务不被滥用。

### 功能要求
- FR-1: 按 API Key 限流（全局 RPM/RPD）
- FR-2: 按模型限流（每个模型独立额度）
- FR-3: 按用户自定义额度（管理员可配置）
- FR-4: 超限返回 429 + Retry-After 头
- FR-5: 限流数据实时可查（管理接口）

### 技术约束
- 使用 Redis Sorted Set 实现滑动窗口
- 与现有 auth 中间件集成，不改变认证流程
- 单次 Redis 往返完成检查（Lua 脚本）

### 接口定义
- checkRateLimit(apiKey, model) → { allowed, remaining, resetAt }
- getUserQuota(apiKey) → { rpm, rpd, modelLimits }
- setUserQuota(apiKey, quota) → void

### 数据模型
- Redis Key: `rl:{apiKey}:{window}` (全局)
- Redis Key: `rl:{apiKey}:{model}:{window}` (模型级)

────────────────────────────────────
Step 2 — 人工评审 spec，确认方案

Step 3 — 拆分为 4 个任务：
  Task 1: 实现 Redis 滑动窗口限流核心
  Task 2: 创建 rateLimitService（FR-1, FR-2）
  Task 3: 集成 auth 中间件（FR-4）
  Task 4: 管理接口（FR-3, FR-5）

Step 4 — 逐任务实现 + 验证对齐

结果：
- 限流逻辑集中在 1 个 service 文件
- 每个 FR 都有对应的测试
- Redis Key 设计有文档记录和决策理由
- 新人看 spec 即可理解系统设计
```

## 混合策略：工程实践中的最优解

非此即彼是伪命题。**成熟的工程团队应该在同一个项目中灵活切换两种模式。**

### Explore → Formalize → Implement 循环

```
┌─────────────────────────────────────────────────────────┐
│                    混合工作流                              │
│                                                         │
│  ┌──────────┐    触发条件     ┌──────────────┐          │
│  │          │  ──────────→  │              │           │
│  │  Vibe    │               │    Spec      │           │
│  │  Coding  │  ←──────────  │    Coding    │           │
│  │ (探索)   │    新需求/      │  (生产)      │           │
│  └──────────┘    技术调研     └──────────────┘          │
│       ↓                           ↓                     │
│   快速原型                    生产代码                    │
│   概念验证                    可维护系统                  │
│   技术选型                    团队协作                    │
└─────────────────────────────────────────────────────────┘
```

### 何时从 Vibe 切换到 Spec？

Scalable Path 的指南提供了 4 个明确信号：

1. **生产意图出现**：用户或业务流程将依赖这个系统
2. **团队扩展**：不止一个人需要理解代码
3. **回归模式**：新功能频繁破坏已有功能
4. **上下文漂移**：AI 修一个 Bug 却引入三个新 Bug

当这些信号出现时，意味着**不协调的成本已超过编写和维护规格文档的成本**。

### 工具侧的实践组合

#### Claude Code 混合工作流

```bash
# Phase 1: Vibe — 快速探索技术方案
claude "调研 WebSocket 和 SSE 两种方案用于实时通知的优劣，
       分别写一个最小 demo"

# 评估后决定用 SSE

# Phase 2: Spec — 正式化
claude "基于 SSE 方案，写一份实时通知系统的技术规格，
       包含接口定义、数据模型、错误处理策略、
       和现有系统的集成点"

# 人工评审 spec

# Phase 3: Implement — 按规格实现
claude "根据 spec.md 实现任务 1：SSE 连接管理器"
```

#### Cursor 混合工作流

```
Plan Mode（Spec 阶段）：
→ "分析现有认证架构，设计 OAuth 2.0 集成方案"
→ 产出方案文档，人工确认

Agent Mode（Vibe 阶段 — 实现细节探索）：
→ "先试一下 Google OAuth 的接入流程，做个 spike"
→ 快速验证可行性

Agent Mode（Spec 阶段 — 正式实现）：
→ "按照方案文档，实现 Step 1：OAuth Service"
→ 遵循规格的结构化实现
```

## Claude Code vs Cursor：工具选型建议

| 维度 | Claude Code | Cursor |
|------|-------------|--------|
| **交互方式** | 终端原生，命令行对话 | VS Code IDE，可视化 |
| **上下文容量** | 200K 可靠 / 1M Beta | 70K-120K（内部截断后） |
| **Token 效率** | 基准（1x） | ~5.5x 消耗 |
| **Spec 支持** | `CLAUDE.md` 自动加载 | `.cursor/rules/` glob 匹配 |
| **多智能体** | Agent Teams（研究预览） | Cloud Agents（隔离 VM） |
| **Vibe 体验** | 终端流畅但无可视化 | IDE 内 Composer 体验优秀 |
| **Spec 体验** | CLAUDE.md + 工作流工具成熟 | Plan Mode + Rules 体系完善 |
| **适合场景** | 大型仓库、复杂重构、终端爱好者 | 全栈开发、前端项目、IDE 偏好者 |
| **价格** | ~$100/月（Max）或 API 按量 | ~$20/月（Pro） |

**选型建议：**

- **纯 Vibe Coding 场景**（原型、Demo、个人项目）→ **Cursor**，可视化体验更好，成本更低
- **纯 Spec Coding 场景**（企业系统、大型项目）→ **Claude Code**，上下文更大，适合复杂规格驱动
- **混合场景**（大多数专业开发）→ **两者配合使用**——Cursor 做前端和可视化交互，Claude Code 做后端和架构级变更

## 未来发展趋势

### 趋势一：Living Specs（活文档）将成为标准

AWS Kiro（2025 年 11 月 GA，超过 25 万开发者使用）已经验证了"活文档"概念——规格文档随代码实现自动更新，而不是写完就过时。Augment Code 的 Intent 产品更进一步，让多个 AI Agent 同时读写同一份规格文档。

**预测：** 2026-2027 年，`CLAUDE.md` 和 `.cursor/rules/` 将进化为双向同步的活文档，规格 ↔ 代码自动保持一致。

### 趋势二：AI Agent 编排将替代单次对话

Claude Code 的 Agent Teams 和 Cursor 的 Cloud Agents 标志着 AI 编程正从"一问一答"演进为"多角色协作"：

```
未来的 Spec Coding 工作流：

Coordinator Agent（规格守护者）
    ├── Implementor Agent 1（实现模块 A）
    ├── Implementor Agent 2（实现模块 B）
    ├── Test Agent（编写和运行测试）
    └── Verifier Agent（检查规格对齐度）

所有 Agent 共享同一份 Living Spec，独立工作，协调交付。
```

**预测：** 到 2027 年，Spec Coding 将从"人写规格 → AI 实现"进化为"人审批规格 → 多 AI 协作实现 → AI 自验证"，人类的角色进一步后移到架构决策和最终审批。

### 趋势三：Vibe Coding 不会消失，而会下沉

Vibe Coding 不会被 Spec Coding 取代。它会成为开发流程中的一个阶段——**探索阶段的默认模式**：

- 技术选型时 Vibe Coding 做 spike
- 新需求分析时 Vibe Coding 做原型
- 确定方案后切换到 Spec Coding 做正式实现

就像我们不会消灭草稿纸，但也不会用草稿纸画施工图。

### 趋势四：工程师的核心技能正在转移

| 过去 | 现在 | 未来 |
|------|------|------|
| 写代码的能力 | 和 AI 对话的能力 | 写规格的能力 |
| 熟悉语法 | 熟悉 prompt | 熟悉系统设计 |
| Debug 能力 | 评估 AI 输出的能力 | 架构决策能力 |
| 代码 Review | AI 输出 Review | 规格 Review |

Thoughtworks 的分析精辟地总结了这一点：

> "Understanding a system used to come naturally through hands-on work. Now, teams need new habits to retain that understanding. **Context has become a skill, not a byproduct.**"
> （理解系统曾经是动手写代码的自然副产物。现在，团队需要新的习惯来保持这种理解。上下文管理已经从副产品变成了一项核心技能。）

### 趋势五：Spec 即代码、代码即 Spec

随着 AI 能力提升，Spec 和代码之间的边界将越来越模糊。未来的规格文档本身可能就是可执行的：

```markdown
## 用户认证

### 约束
- 密码必须 >= 8 字符，包含大小写字母和数字
- 登录失败 5 次后锁定账户 30 分钟
- JWT Token 有效期 24 小时，支持 Refresh

### 接口
POST /auth/login  { email, password } → { token, refreshToken }
POST /auth/refresh { refreshToken } → { token }

### 测试场景
- 正确凭据 → 200 + token
- 错误密码 → 401
- 锁定账户 → 423 + retryAfter
```

当 AI 能力达到一定水平，这样的规格文档直接就能生成完整的实现、测试和文档——**规格即代码、代码即规格**。

## 写在最后

Y Combinator W25 批次中 25% 的创业公司代码是 95% AI 生成的，它们创下了 YC 历史上最快的增长记录。但 YC 的时间尺度是"几个月到 Series A"，而生产系统的时间尺度是"数年的持续运营"。

**Vibe Coding 让你跑得快，Spec Coding 让你跑得远。**

聪明的工程师不选边站，而是在对的时间用对的工具：

- **探索时**用 Vibe，让想法快速落地
- **建设时**用 Spec，让系统经得住考验
- **始终**保持对 AI 输出的工程判断力

AI 不会取代工程师——但**会用 Spec Coding 的工程师，会取代只会 Vibe Coding 的工程师**。

---

*本文基于 Claude Code 和 Cursor 的实际工程实践撰写。文中引用的研究数据来自 GitClear（211M 行代码分析）、CMU（Cursor 采用研究）、Augment Code、GitHub、AWS Kiro、Thoughtworks 等公开来源。*
