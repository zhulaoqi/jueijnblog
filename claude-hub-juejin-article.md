# Claude HUD：给你的 Claude Code 装一块「仪表盘」

> 用 Claude Code 写代码时，你是否经历过这些场景：上下文用了多少？还剩多少额度？当前跑了几个子 Agent？任务完成到哪一步了？——Claude HUD 让这一切一目了然。

## 为什么需要 Claude HUD？

如果你已经在用 Claude Code 进行日常开发，你一定对以下体验不陌生：

- 写着写着对话突然被截断，才发现**上下文窗口已经用完**
- 不知道当前会话的**速率限额还剩多少**，只能等 429 报错才反应过来
- Claude 在后台跑了好几个子 Agent，你完全不知道**它们在干什么、跑了多久**
- 让 Claude 执行一个多步骤任务，但看不到**进度到哪一步了**

这些问题的本质是：**Claude Code 的运行状态对用户来说是个黑盒。**

[Claude HUD](https://github.com/jarrodwatts/claude-hud) 就是为了解决这个问题而生的——它是一个 Claude Code 插件，在终端输入框下方实时展示会话状态，让你对 Claude 的一举一动了然于胸。

## Claude HUD 是什么？

Claude HUD 是由开发者 [Jarrod Watts](https://x.com/jarrodwatts) 开源的 Claude Code 状态栏插件。它利用 Claude Code 原生的 statusline API，每约 **300ms** 刷新一次，在终端底部渲染出一块信息面板。

```
┌──────────────────────────────────────────────────────────────┐
│ [Opus 4.6 | Max] │ my-project git:(main*)                    │
│ Context █████░░░░░ 45% │ Usage ██░░░░░░░░ 25% (1h30m / 5h)  │
│ ◐ Edit: auth.ts | ✓ Read ×3 | ✓ Grep ×2                     │
│ ◐ explore [haiku]: Finding auth code (2m 15s)                │
│ ▸ Fix authentication bug (2/5)                               │
└──────────────────────────────────────────────────────────────┘
```

**不需要 tmux，不需要额外窗口，不需要手动查询**——打开 Claude Code 就能看到。

### 技术原理

```
Claude Code (每 ~300ms)
        ↓ stdin (JSON)
   Claude HUD 插件
        ↓ 解析原生 token 数据 + transcript JSONL
        ↓ stdout
   终端状态栏渲染（最多 4 行）
```

关键点：

- 读取的是 Claude Code **原生 token 计数**，不是估算值
- 通过解析 transcript JSONL 文件获取工具调用、Agent、Todo 状态
- 零外部依赖，不启动额外进程

## 核心功能

### 1. 上下文用量可视化

这是最实用的功能。一根颜色渐变的进度条实时展示上下文窗口消耗：

- **绿色**：用量健康，放心继续
- **黄色**：开始吃紧，考虑精简对话
- **红色**：即将耗尽，建议开新会话

支持显示格式可选：百分比、已用 token 数、剩余 token 数。对于 1M context 的长会话也完美支持。

### 2. 速率限额追踪

如果你是 Claude **Pro / Max / Team** 订阅用户，HUD 会展示当前的速率消耗情况：

- 小时级用量的可视化进度条
- 可选显示 7 天用量百分比
- 避免在关键时刻撞上限额

> 注意：API 按量付费用户不显示此项（因为没有限额概念），AWS Bedrock 用户同理。

### 3. 工具活动实时追踪

当 Claude 在执行 Read、Edit、Grep、Bash 等工具调用时，HUD 会实时显示：

```
◐ Edit: src/auth.ts | ✓ Read ×3 | ✓ Grep ×2
```

- `◐` 表示正在执行
- `✓` 表示已完成（附执行次数）

你不再需要盯着日志猜 Claude 在干什么。

### 4. 子 Agent 状态监控

Claude Code 的一大能力是派发子 Agent 并行处理任务。HUD 会追踪每个 Agent：

```
◐ explore [haiku]: Finding auth code (2m 15s)
◐ general-purpose [sonnet]: Running tests (45s)
```

显示内容包括：Agent 类型、使用的模型、当前任务描述、已运行时间。

### 5. Todo 进度展示

当 Claude 创建了任务列表（TaskCreate/TaskUpdate），HUD 会显示整体进度：

```
▸ Fix authentication bug (2/5)
```

让你清楚知道多步骤任务推进到了哪里。

### 6. Git 状态集成

状态栏上直接显示当前 Git 分支及工作区状态：

- `main*` — 有未提交的变更
- `↑2 ↓1` — 领先远程 2 个提交，落后 1 个
- `!3 +1 ✘1 ?2` — 3 个修改、1 个新增、1 个删除、2 个未追踪

### 7. 会话元信息

一行展示当前会话的关键信息：

- 当前模型名（Opus / Sonnet / Haiku）
- 订阅类型（Max / Pro / API / Bedrock）
- 项目路径（可配置显示层级）
- 会话时长
- Token 速度
- 配置统计（CLAUDE.md 数量、rules 数量、MCP 数量、hooks 数量）

## 安装教程

### 前置要求

| 依赖 | 版本 |
|------|------|
| Claude Code | >= v1.0.80 |
| Node.js | >= 18（或 Bun） |

### 三步安装

**第一步：添加插件市场源**

在 Claude Code 中输入：

```
/plugin marketplace add jarrodwatts/claude-hud
```

**第二步：安装插件**

```
/plugin install claude-hud
```

**第三步：配置状态栏**

```
/claude-hud:setup
```

这一步会自动将 statusline 配置写入 `~/.claude/settings.json`，后续插件更新也会自动生效，无需重新 setup。

安装完成后，重启 Claude Code 即可看到效果。

> **Linux 用户注意**：如果安装时遇到 cross-device 错误，需要先设置 `TMPDIR=~/.cache/tmp`。

## 配置指南

安装后运行 `/claude-hud:configure` 可进入交互式配置，支持实时预览效果。

### 三种预设模式

| 预设 | 内容 | 适用场景 |
|------|------|----------|
| **Full** | 全部功能开启（工具、Agent、Todo、Git、用量、时长） | 重度用户，想要完整信息 |
| **Essential** | 活动行 + Git 状态 | 日常开发，信息够用又不杂乱 |
| **Minimal** | 仅模型名 + 上下文进度条 | 屏幕空间有限，只看关键指标 |

### 关键配置项

**布局控制**：

```jsonc
{
  "lineLayout": "expanded",   // "expanded"（多行）或 "compact"（单行）
  "pathLevels": 2,             // 项目路径显示层级（1-3）
  "elementOrder": ["model", "context", "usage"]  // 元素排列顺序
}
```

**功能开关**：

| 配置项 | 说明 | 默认 |
|--------|------|------|
| `showTools` | 显示工具活动行 | 关 |
| `showAgents` | 显示子 Agent 状态 | 关 |
| `showTodos` | 显示 Todo 进度 | 关 |
| `gitStatus.enabled` | 显示 Git 状态 | 开 |
| `gitStatus.dirty` | 脏标记（*） | 开 |
| `gitStatus.aheadBehind` | 领先/落后远程 | 关 |
| `gitStatus.fileStats` | 文件变更统计 | 关 |

**颜色自定义**：

支持自定义上下文进度条、用量进度条、警告状态、临界状态的颜色：

```
可选颜色：red / green / yellow / magenta / cyan / brightBlue / brightMagenta
```

**用量 API 缓存**：

```jsonc
{
  "usageSuccessTTL": 60,    // 成功响应缓存时间（秒）
  "usageFailureTTL": 15     // 失败响应缓存时间（秒）
}
```

## 优势亮点

### 与"盲飞"模式对比

| 场景 | 没有 HUD | 有 HUD |
|------|----------|--------|
| 上下文快用完了 | 对话突然截断，一脸懵 | 看到进度条变红，主动开新会话 |
| 速率限额耗尽 | 429 报错才知道 | 提前看到用量接近上限 |
| Claude 在跑子 Agent | 只能干等，不知道在干嘛 | 实时看到每个 Agent 在做什么 |
| 多步骤任务 | 不知道进行到第几步 | Todo 进度条清晰展示 |
| Git 状态 | 需要手动 `git status` | 抬头就能看到 |

### 核心优势总结

1. **零侵入**：纯 statusline 实现，不影响 Claude Code 的任何功能
2. **零延迟感知**：~300ms 刷新频率，状态近乎实时
3. **原生数据**：token 计数来自 Claude Code 原生 API，不是估算
4. **高度可定制**：3 种预设 + 完整的精细配置，满足不同偏好
5. **零外部依赖**：不需要 tmux、不需要额外进程、不需要后台服务
6. **自动更新**：插件更新后无需重新配置

## 适用人群

| 角色 | 为什么需要 |
|------|------------|
| **Claude Code 重度用户** | 每天长时间使用，需要随时掌握会话状态，避免上下文浪费 |
| **Max/Pro 订阅用户** | 有限额限制，需要实时了解用量消耗，合理分配使用节奏 |
| **多 Agent 工作流使用者** | 经常派发子 Agent 并行任务，需要监控每个 Agent 的运行状态 |
| **团队技术负责人** | 推荐给团队成员使用，统一开发体验 |
| **效率导向的开发者** | 不想在黑盒中等待，想要对 AI 工具有完整的掌控感 |

## 常见问题

**Q：安装后看不到状态栏？**
确认已执行 `/claude-hud:setup`，然后重启 Claude Code。

**Q：配置修改后没生效？**
检查 JSON 语法是否正确。语法错误时会静默回退到默认配置。可以用 `/claude-hud:configure` 重新配置。

**Q：看不到用量数据？**
用量追踪仅支持 Pro/Max/Team 订阅用户的 OAuth 登录方式。API Key 用户（按量付费）和 Bedrock 用户不显示此数据。

**Q：看不到工具/Agent/Todo 行？**
这三行默认关闭，需要在配置中手动开启 `showTools`、`showAgents`、`showTodos`。

**Q：用量 API 响应慢？**
可以增大 `CLAUDE_HUD_USAGE_TIMEOUT_MS` 环境变量的值。如果使用代理，确保设置了 `HTTPS_PROXY` 或 `HTTP_PROXY`。

## 项目状态

- **GitHub Stars**：5.9k+
- **开源协议**：MIT
- **作者**：[Jarrod Watts](https://x.com/jarrodwatts)
- **要求**：Claude Code v1.0.80+ / Node.js 18+
- **项目地址**：[github.com/jarrodwatts/claude-hud](https://github.com/jarrodwatts/claude-hud)

## 写在最后

Claude Code 已经足够强大，但再强大的工具，如果运行状态对用户不透明，用起来总会有种"不踏实"的感觉。Claude HUD 做的事情很简单——把 Claude Code 的运行状态从黑盒变成白盒，让你在每一个 ~300ms 都知道它在干什么、用了多少、还剩多少。

三条命令，一分钟安装。如果你每天都在用 Claude Code，没有理由不试试。

---

*如果这篇文章对你有帮助，欢迎点赞收藏。有使用心得或问题，欢迎评论区交流。*