# MCP Java 系统教程实施计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 交付一篇以 MCP `2026-07-28` 正式规范为主线、准确说明 Java SDK 代际差异，并配有 6 张高质量协议图示的 Java 系统教程。

**Architecture:** 正文按“现代协议内核 → Java 生态实现现状 → 迁移与生产化”展开。`2026-07-28` 内容通过正式规范、Schema 和 Java 线级消息代码验证；官方 Java SDK 与 Spring AI 示例按其真实的 `2025-11-25` 协议基线编译和运行。所有验证工程、抓包和中间数据仅放在临时目录，仓库只保留 Markdown、HTML 图源和 PNG。

**Tech Stack:** MCP Specification `2026-07-28`、Java 21、Maven、Jackson、MCP Java SDK 2.0.x、Spring Boot 4.x、Spring AI 2.0.x、JSON Schema、diagram-design、HTML/SVG、Playwright/Chromium。

**Design spec:** `docs/superpowers/specs/2026-08-25-mcp-java-tutorial-design.md`

---

## 文件结构

**创建：**

- `mcp-java-core-principles-and-development-guide.md`：教程正文、Java 代码、JSON-RPC 消息、引用与版本说明。
- `mcp-java-tutorial-diagrams/01-runtime-and-trust-boundaries.html`
- `mcp-java-tutorial-diagrams/01-runtime-and-trust-boundaries.png`
- `mcp-java-tutorial-diagrams/02-stateless-request-patterns.html`
- `mcp-java-tutorial-diagrams/02-stateless-request-patterns.png`
- `mcp-java-tutorial-diagrams/03-discovery-and-version-selection.html`
- `mcp-java-tutorial-diagrams/03-discovery-and-version-selection.png`
- `mcp-java-tutorial-diagrams/04-features-mrtr-and-subscriptions.html`
- `mcp-java-tutorial-diagrams/04-features-mrtr-and-subscriptions.png`
- `mcp-java-tutorial-diagrams/05-transport-bindings.html`
- `mcp-java-tutorial-diagrams/05-transport-bindings.png`
- `mcp-java-tutorial-diagrams/06-java-version-gap.html`
- `mcp-java-tutorial-diagrams/06-java-version-gap.png`

**只在临时目录创建：**

- `/tmp/mcp-java-tutorial-verification/modern-wire/`：`2026-07-28` 消息与 Schema 校验。
- `/tmp/mcp-java-tutorial-verification/java-sdk/`：官方 Java SDK 编译和端到端验证。
- `/tmp/mcp-java-tutorial-verification/spring-ai/`：Spring AI 编译、启动和传输验证。
- `/tmp/mcp-java-tutorial-verification/logs/`：标准化线级日志。

**不修改：**

- `hermes-agent-kernel-architecture-and-development-guide.md`
- `hermes-agent-kernel-diagrams/`
- `skill-mcp-rag-future-of-ai-integration.md`

**Git 约束：** 不提交或推送；只有用户明确要求时才执行 Git 提交。

---

## Chunk 1：资料基线与现代协议正文

### Task 1：锁定一手资料、版本和文章骨架

**Files:**
- Create: `mcp-java-core-principles-and-development-guide.md`
- Reference: `docs/superpowers/specs/2026-08-25-mcp-java-tutorial-design.md`

- [ ] **Step 1：建立官方资料清单**

从 `https://modelcontextprotocol.io/llms.txt` 定位并核验以下正式页面：

- `specification/2026-07-28`
- `specification/2026-07-28/changelog`
- `specification/2026-07-28/basic`
- `specification/2026-07-28/basic/versioning`
- `specification/2026-07-28/basic/patterns/mrtr`
- `specification/2026-07-28/basic/patterns/subscriptions`
- `specification/2026-07-28/basic/transports/stdio`
- `specification/2026-07-28/basic/transports/streamable-http`
- `specification/2026-07-28/server/discover`
- Tools、Resources、Prompts、Elicitation、Caching、Cancellation、Authorization
- Deprecated registry、Tasks extension、官方 Schema

为每个版本敏感结论记录：

- 版本化深链和章节锚点。
- TypeScript Schema 对应类型或字段。
- 生成的 JSON Schema `$defs` 名称。
- 原始 MUST / SHOULD / MAY 级别。
- 核验日期。

Expected: TypeScript Schema 作为事实源，生成的 JSON Schema 用于自动验证；每个规范结论都可以复现其来源。

- [ ] **Step 2：锁定 Java 生态版本矩阵**

核验：

- MCP Java SDK 最新稳定版本、发布日期、Maven 坐标、JDK 要求和实现的协议版本。
- Spring AI 最新稳定版本、Spring Boot 要求、传递的 Java SDK 版本和 MCP 传输模块。
- Spring AI `STATELESS` 的部署含义，确认它不代表 `2026-07-28` 协议支持。

截至计划编写日的待验证基线是：

- 直接 Java SDK：`2.0.1`，协议 `2025-11-25`。
- Spring AI：`2.0.1`，支持 Spring Boot 4.0/4.1，其 MCP 模块传递 Java SDK `2.0.0`。
- Spring AI 工程不得强制覆盖其管理的 Java SDK 到 `2.0.1`，除非官方兼容说明和测试证明可行。

Expected: 得到“规范版本 / SDK 版本 / Spring AI 版本 / 传递 SDK / 能力差异 / 核验日期”矩阵；任何冲突以源码、release、effective POM 和完整 dependency tree 为准。

- [ ] **Step 3：建立临时目录所有权和 Git 基线**

Run:

```bash
if [ -e /tmp/mcp-java-tutorial-verification ]; then
  echo "temporary directory already exists; refusing to claim ownership" >&2
  exit 1
fi
mkdir /tmp/mcp-java-tutorial-verification
touch /tmp/mcp-java-tutorial-verification/.owned-by-mcp-java-tutorial-plan
git status --short > /tmp/mcp-java-tutorial-verification/git-status.before
```

Expected: 已存在同名目录时停止，不写标记也不接管；新建成功后所有临时产物都位于带任务所有权标记的目录，最终可区分用户原有变更和本任务新增文件。

- [ ] **Step 4：创建文章骨架**

在 `mcp-java-core-principles-and-development-guide.md` 写入：

- 标题、导语和版本警告。
- 设计规格中的 15 个一级章节。
- 每章的结论句、待填代码位和正式资料链接。
- 文首版本矩阵，以及“规范行为 / SDK 行为 / Spring AI 行为”标记约定。

Expected: 文章结构完整，尚未出现把旧初始化流程称为当前协议的内容。

- [ ] **Step 5：执行结构检查**

Run:

```bash
rg -n '^## ' mcp-java-core-principles-and-development-guide.md
rg -n '2026-07-28|2025-11-25|Java SDK|Spring AI' mcp-java-core-principles-and-development-guide.md
```

Expected: 15 个主章节齐全；两个协议版本及 Java 代际差异在正文开头明确出现。

### Task 2：撰写 MCP `2026-07-28` 协议内核

**Files:**
- Modify: `mcp-java-core-principles-and-development-guide.md`
- Temporary: `/tmp/mcp-java-tutorial-verification/modern-wire/`

- [ ] **Step 1：撰写系统边界与基础消息**

覆盖：

- Host、Client、Server、Transport 的职责和信任边界。
- JSON-RPC Request、Response、Notification、Error 和 ID。
- `_meta.io.modelcontextprotocol/protocolVersion`
- `_meta.io.modelcontextprotocol/clientCapabilities`
- `_meta.io.modelcontextprotocol/clientInfo`
- 结果 `_meta.io.modelcontextprotocol/serverInfo`
- `resultType: complete | input_required`

明确 `protocolVersion` 和 `clientCapabilities` 是 MUST；`clientInfo` 和结果中的 `serverInfo` 是 SHOULD。缺少两个必填 `_meta` 字段返回 `-32602`；缺少 `clientInfo` 仍是合法请求。扩展可在双方声明支持后增加新的 `resultType`。

Expected: 不把 MCP Client 与 Host 混为一个进程角色，不引入协议级 Session，也不把 SHOULD 写成 MUST。

- [ ] **Step 2：撰写发现、版本选择与兼容探测**

依次解释：

1. Client 可先调用 `server/discover`。
2. Server 必须实现 `server/discover`。
3. Client 也可直接发送业务 RPC。
4. 每个请求独立声明版本和能力。
5. 版本不支持时返回 `UnsupportedProtocolVersionError`。
6. stdio 与 HTTP 如何探测旧 `initialize` 时代实现。

Expected: `server/discover` 被描述为 Server 必须实现、Client 可选调用，而不是强制握手。

- [ ] **Step 3：撰写三种消息模式**

分别给出完整线级消息：

- Request/Response：`tools/list` 或 `resources/read`。
- MRTR：首次 `tools/call` → Server 在 `InputRequiredResult.inputRequests` 中嵌入 `ElicitRequest` → Client 产生对应 `ElicitResult` → 使用新 ID、`inputResponses` 和原样 `requestState` 重试原 `tools/call`。
- Subscribe/Notify：`subscriptions/listen` → acknowledged → `notifications/resources/updated` → 取消或流终止。

Expected:

- Server 不主动发送 JSON-RPC Request。
- MRTR 重试 ID 与首次请求不同。
- 只有 `tools/call`、`resources/read`、`prompts/get` 可以返回 `InputRequiredResult`。
- `inputRequests` 与 `requestState` 至少存在一个。
- `requestState` 原样回传；当其影响授权、资源访问或业务逻辑时必须提供完整性保护，只有篡改最多导致请求失败时才可省略。为防重放，Server 应校验授权主体、过期时间和原请求绑定。
- Client 必须逐请求声明所需 Elicitation/Sampling/Roots 能力，否则 Server 返回 `MissingRequiredClientCapabilityError`（`-32021`）。
- Server 必须声明 `resources.subscribe: true` 才能提供资源订阅；acknowledged 返回实际接受的过滤条件，先于同一 subscriptionId 的业务通知；subscriptionId 等于 listen 请求 ID，且每条通知携带该 ID。
- Server 不发送未订阅的通知；断线后 Client 重新发送 `subscriptions/listen`；Server 优雅结束时返回 `SubscriptionsListenResult`。

- [ ] **Step 4：撰写 Server Features 与 Client Features**

覆盖：

- Tools：发现、输入/输出 Schema、结构化内容、错误与 annotations 的不可信边界。
- Resources：URI、模板、读取、内容类型、更新通知。
- Prompts：用户选择的消息模板，不是可执行工具。
- Elicitation：Form 与 URL 两种模式及敏感信息边界。
- Roots、Sampling：保留兼容语义，但明确 Deprecated 状态和迁移方向；在现代协议中只能作为 MRTR 的嵌入请求，不能画成或写成 Server 主动 JSON-RPC Request。
- Logging：保留兼容语义，但明确其 Server Utility 分类、Deprecated 状态和迁移方向。

Tool Schema 需注明 JSON Schema 2020-12、`$ref` 解析资源边界和默认禁止任意联网解析；存在 `outputSchema` 时验证 `structuredContent`。Logging 分类为 Server Utility，并明确现代协议已移除 `logging/setLevel`，改用逐请求 `_meta.io.modelcontextprotocol/logLevel`；`notifications/message` 只能出现在对应请求流。Elicitation 不代替 Authorization。

- [ ] **Step 5：撰写缓存、取消、进度与 Tasks 扩展**

明确：

- `server/discover`、`tools/list`、`prompts/list`、`resources/list`、`resources/templates/list`、`resources/read` 的完整结果必须同时包含 `ttlMs >= 0` 与 `cacheScope: public | private`。
- `input_required` 和带 `inputResponses`/`requestState` 的重试不可缓存。
- 变更通知使相关缓存失效。
- stdio 使用 `notifications/cancelled`，HTTP 关闭响应流。
- Progress token、`notifications/progress` 的请求作用域和终止规则。
- Pagination 的 cursor 不透明性、稳定 cursor 和终止条件。
- Completion 的参数、候选限制和能力前提。
- Tasks 属于 `io.modelcontextprotocol/tasks` 扩展，不属于核心；最小流程为 `CreateTaskResult`、`tasks/get`、`tasks/update`、`tasks/cancel`。

Expected: 不把旧 `tasks/result`、旧资源订阅 RPC 或 HTTP GET 流写成现代主线。

- [ ] **Step 6：撰写两种传输**

stdio 必须说明：

- 单行 UTF-8 JSON-RPC 帧。
- `stdout` 只承载协议消息，日志写 `stderr`。
- 子进程生命周期和取消。

Streamable HTTP 必须说明：

- 单一 MCP endpoint、POST-only。
- `MCP-Protocol-Version`、`Mcp-Method`、适用时的 `Mcp-Name`。
- `Accept: application/json, text/event-stream` 与正确 `Content-Type`。
- Notification 的成功响应是 `202 Accepted`。
- Body 是元数据事实来源，Header 必须匹配 Body。
- Header/Body 不一致使用 `HeaderMismatchError`（`-32020`）。
- `Mcp-Name` 的适用方法和 Base64 sentinel 编码；非 ASCII、控制字符、首尾空白或本身匹配 sentinel 模式的 ASCII 值都必须编码。
- JSON 响应或请求作用域 SSE。
- 无 `Mcp-Session-Id`、无 `Last-Event-ID` 恢复。
- 流中断后以新请求 ID 重发。

- [ ] **Step 7：创建现代消息验证夹具**

在临时目录保存文章中的每个 JSON 消息。固定官方 `2026-07-28` Schema 的下载 URL、Git commit SHA 和 SHA-256；为每个 fixture 建立 `文件 → #/$defs/<具体类型> → PASS/FAIL` 清单，禁止直接把消息对 Schema 根对象校验。

另写序列语义断言，覆盖 JSON Schema 无法验证的规则：

- MRTR 重试 ID 变化和 `requestState` 原样回传。
- `InputRequiredResult` 的 `inputRequests` 与 `requestState` 至少存在一个。
- subscriptionId 等于 listen 请求 ID。
- acknowledged 时序和过滤范围。
- Header 与 Body 一致。
- `input_required` 只出现在允许的方法。

Run:

```bash
cd /tmp/mcp-java-tutorial-verification/modern-wire
./validate-all.sh
```

Expected: 正例全部 PASS，负例全部按预期 FAIL。负例至少覆盖：缺少 `resultType`、分别缺少两个 MUST `_meta` 字段、保留 SHOULD 缺失合法例、旧 ID 重试、篡改/过期 `requestState`、未声明 Client 能力、不支持的方法返回 `input_required`、错误 subscriptionId、通知越权和 HeaderMismatch。

- [ ] **Step 8：审查现代协议章节**

由独立审查者逐条检查规范引用、MUST/SHOULD/MAY、方法名、字段路径和弃用状态。

Expected: 输出 `✅ Approved`；发现问题时修正文稿和夹具后重新审查。

---

## Chunk 2：Java 实现、迁移与生产化

### Task 3：验证并撰写官方 MCP Java SDK 实战

**Files:**
- Modify: `mcp-java-core-principles-and-development-guide.md`
- Temporary: `/tmp/mcp-java-tutorial-verification/java-sdk/`

- [ ] **Step 1：生成临时 Maven 工程**

使用已核验的最新稳定 MCP Java SDK 版本，JDK 21，创建：

- STDIO Server/Client 模块，使用 `ProcessBuilder` 管理 Server 子进程。
- JDK HTTP Client 与 `HttpServletStreamableServerTransportProvider` 模块，使用嵌入式 Servlet 容器和随机端口。
- 研发知识库领域对象。
- `kb://documents/{id}` Resource。
- `search_documents` Tool。
- `incident_analysis` Prompt。
- 同步 Server/Client 最短路径。
- 异步 Server/Client 示例。

所有进程与 HTTP 测试必须有启动就绪检测、硬超时、finally 清理和残留进程断言。

Expected: `pom.xml` 只使用真实发布坐标，effective POM 与依赖树显示直接 Java SDK `2.0.1` 或重新核验后的实际稳定版本。

- [ ] **Step 2：先写协议基线断言**

测试必须断言 Java SDK 实际使用 `2025-11-25` 初始化语义，并在测试名和日志中标注 `legacy_protocol_baseline`。

Run:

```bash
cd /tmp/mcp-java-tutorial-verification/java-sdk
mvn -q test
```

Expected: 基线断言通过；若 SDK 已更新到 `2026-07-28`，暂停并回到 Task 1 重做版本矩阵和章节设计，不沿用旧假设。

- [ ] **Step 3：验证 stdio**

启动本地 Server 子进程，验证：

- 初始化与能力协商符合 SDK 的 `2025-11-25` 语义。
- 列出并调用 Tool。
- 列出并读取 Resource。
- 获取 Prompt。
- 协议输出与 `stderr` 日志隔离。
- 在途请求通过 `notifications/cancelled` 取消。
- stdin EOF 后 Server 退出。
- Client 退出后 Server 正常终止。

Expected: 端到端测试通过，并生成脱敏线级日志。

- [ ] **Step 4：验证 Streamable HTTP**

验证：

- 直接 Java SDK 的 Servlet Streamable HTTP Provider、JDK HTTP Client、实际 endpoint 和随机端口。
- `2025-11-25` 的初始化、Session 和 SSE 行为。
- Tool、Resource、Prompt 可完整调用。
- POST、GET、DELETE、`MCP-Session-Id`、JSON 与 SSE 两类响应。
- 显式 `notifications/cancelled`、Session 终止、错误 HTTP 状态映射和超时后取消。

Expected: 端到端测试通过且确实覆盖 SSE 响应路径；日志与现代 `2026-07-28` 的“关闭响应流即取消、无 Session”语义放在相邻小节对比，不能共用断言。

- [ ] **Step 5：把已验证代码写入文章**

每段代码前标注：

```text
实现基线：MCP Java SDK <已核验版本>
协议语义：2025-11-25
与当前规范的差异：<一句话>
```

Expected: 读者不会因代码可运行而误认为它实现了 `2026-07-28`。

### Task 4：验证并撰写 Spring AI MCP 实战

**Files:**
- Modify: `mcp-java-core-principles-and-development-guide.md`
- Temporary: `/tmp/mcp-java-tutorial-verification/spring-ai/`

- [ ] **Step 1：创建 Spring AI 临时工程**

使用核验后的稳定 Spring AI BOM 和兼容 Spring Boot 版本，复用同一研发知识库领域逻辑，分别配置：

- MCP Server starter。
- MCP Client starter。
- 注解或 callback 形式的 Tool、Resource、Prompt。
- 独立测试 profile 或模块下的 stdio、WebMVC HTTP 和 WebFlux HTTP Server/Client。
- 随机端口、启动就绪检测、超时和子进程清理。

- [ ] **Step 2：检查真实依赖树**

Run:

```bash
cd /tmp/mcp-java-tutorial-verification/spring-ai
mvn -q help:effective-pom > effective-pom.xml
mvn -q dependency:tree > dependency-tree.txt
rg 'spring-ai|modelcontextprotocol|mcp' dependency-tree.txt
```

Expected: 默认预期为 Spring AI `2.0.1` 管理 Java SDK `2.0.0`；若实际不同，先更新版本矩阵。不得为了与直接 SDK 工程对齐而强制覆盖传递 SDK。

- [ ] **Step 3：编译并运行最小验证**

Run:

```bash
cd /tmp/mcp-java-tutorial-verification/spring-ai
mvn -q test
```

Expected: ApplicationContext、Tool/Resource/Prompt 注册、Client 调用和传输测试全部通过。

- [ ] **Step 4：撰写框架映射**

解释：

- 自动配置创建了哪些 Client、Server、Transport 和 Provider。
- 注解或 callback 如何映射到 SDK 类型。
- Spring AI `STATELESS` 只表示框架部署模式。
- WebMVC/WebFlux Transport 所属模块和发布节奏。
- 框架默认值、配置项和协议标准之间的边界。

Expected: 不把 Spring 属性名、注解或安全扩展称为 MCP 标准字段。

### Task 5：完成迁移、Authorization、生产化与总结

**Files:**
- Modify: `mcp-java-core-principles-and-development-guide.md`

- [ ] **Step 1：写两代协议迁移表**

至少覆盖：

- `initialize` 与 `notifications/initialized` → 逐请求 `_meta`
- Session → 显式业务句柄；句柄只是普通应用参数，不是新的协议 Session
- Server 主动 Request → MRTR
- `resources/subscribe` / HTTP GET → `subscriptions/listen`
- SSE 恢复 → 新 ID 重发；对可能重复的副作用使用幂等键或业务去重
- 核心 Tasks → Tasks 扩展
- Roots → 工具参数、Resource URI 或 Server 配置
- Sampling → Server 直接集成模型 Provider
- Logging → `stderr` 或 OpenTelemetry

明确：现代 MRTR、`subscriptions/listen`、无 Session 和现代请求复盘只由线级夹具与规范 Schema 验证，不作为旧 Java SDK 或 Spring AI 的端到端测试目标。

- [ ] **Step 2：写 Authorization 边界**

只覆盖：

- `401 + WWW-Authenticate` 和 well-known 两种 HTTP Protected Resource Metadata 发现方式。
- Authorization Server Metadata。
- Authorization Server `issuer` 严格验证和 mix-up 防护。
- PKCE；`resource` 同时进入 Authorization Request 与 Token Request。
- Server 验证 Token audience/resource。
- 禁止 Token passthrough；访问上游 API 使用独立 Token。
- Client ID Metadata Documents、预注册、已弃用动态注册的选择顺序。
- Client 凭据按 issuer 隔离，不能跨 Authorization Server 复用。
- stdio 从受控环境获取凭据。
- stdio SHOULD NOT 套用 HTTP OAuth 流。
- Form Elicitation 不承载密码或 Token。

不实现完整 Authorization Server、Token 签发或账户系统。

- [ ] **Step 3：写生产化与调试**

覆盖：

- Schema 校验、工具输入验证、资源 URI 校验。
- 超时、取消、重试、幂等、背压和显式状态句柄。
- Streamable HTTP `Origin` 校验，非法 Origin 返回 403；本地服务默认绑定 `127.0.0.1`。
- 请求体、消息、结构化结果和流的大小上限。
- Spring AI HTTP starter 默认不提供认证时会暴露全部 Tool/Resource/Prompt，生产环境必须显式配置认证与授权。
- Tool descriptions/annotations 不可信。
- 用户同意、最小权限、审计和敏感信息脱敏。
- OpenTelemetry `_meta` 传播、结构化日志和指标。
- Inspector、线级日志、Schema 错误和版本错误定位。

安全修复归属必须按实际依赖版本说明：不得把直接 Java SDK `2.0.1` 的 bounded-read 等修复错误归因于 Spring AI 当前传递的 Java SDK `2.0.0`。

- [ ] **Step 4：完成总结与参考资料**

加入：

- 一次现代请求的端到端复盘。
- Java 开发检查清单。
- 协议对象速查。
- 正式规范、Schema、Java SDK、Spring AI 和扩展的一手链接。
- 版本与资料核验日期。

- [ ] **Step 5：执行正文一致性检查**

Run:

```bash
rg -n 'initialize|Mcp-Session-Id|resources/subscribe|sampling/createMessage|roots/list|logging/setLevel' mcp-java-core-principles-and-development-guide.md
rg -n '2026-07-28|2025-11-25|Deprecated|SDK 尚未实现' mcp-java-core-principles-and-development-guide.md
```

Expected: 每个旧概念都位于明确的旧协议、迁移或弃用语境；版本敏感代码均有基线标记。

- [ ] **Step 6：独立技术审查**

审查者按设计规格逐项检查：

- 现代协议事实和版本边界。
- Java 代码与真实依赖版本。
- Spring AI 与标准协议的边界。
- Authorization 和 Elicitation 安全边界。
- 引用可追溯性。

Expected: 输出 `✅ Approved`；问题修复后重复审查。

---

## Chunk 3：diagram-design 配图与最终验收

### Task 6：创建并导出 6 张协议图

**Files:**
- Create: `mcp-java-tutorial-diagrams/*.html`
- Create: `mcp-java-tutorial-diagrams/*.png`
- Modify: `mcp-java-core-principles-and-development-guide.md`

- [ ] **Step 1：确认图形方案**

使用 `diagram-design`，统一采用：

- Format：`html+png`
- Size：`doc-inline`（viewBox `960×600`，PNG @2 为 `1920×1200`）
- Detail：`balanced`
- Audience：`engineer`
- Variant：minimal light、static
- 风格：沿用仓库现有 Hermes 技术文章图示的编辑设计语言
- 密度：4/10，单图不超过 9 个主节点、12 条箭头、2 个珊瑚焦点

具体类型：

1. `01-runtime-and-trust-boundaries`：普通 Architecture zones，不套用 Secure paved road；≤7 节点、≤8 路径；展示 Host / Client / Server / Transport 和信任边界。
2. `02-stateless-request-patterns`：Nested；≤7 节点、≤6 路径；只展示“JSON-RPC Request 包含逐请求 `_meta`，结果由普通完成或 MRTR 组成，订阅是长请求流”的包含关系；Features 移回正文。
3. `03-discovery-and-version-selection`：Flowchart；≤8 节点、≤10 转移；展示 Client 可选 discover、可直接业务请求、版本错误和双时代回退。Server 实现 discover 是 MUST，Client 调用是 MAY。
4. `04-features-mrtr-and-subscriptions`：Sequence；Client、User、Server 三条 lifeline，消息清单固定为：首次 `tools/call`、`InputRequiredResult`、用户输入、带新 ID 的重试、完成结果、`subscriptions/listen`、acknowledged、资源更新、`resources/read`、读取结果。最多 10 条消息、1 个 opt fragment；不再单独画普通 Tool 调用和取消细节。顶部使用不占消息预算的分类标识列出 Tools / Resources / Prompts，并明确 Prompt 是消息模板而非可执行 Tool。
5. `05-transport-bindings`：Architecture；左右各≤4 节点；对比 stdio 的单行帧/取消通知/EOF 与 Streamable HTTP 的 POST/请求流/关闭取消。
6. `06-java-version-gap`：Layer stack；4–5 层；自上而下为应用代码 → Spring AI → Java SDK → `2025-11-25` 协议栈，`2026-07-28` 作为外部迁移目标，不得画成当前 Java 支持层。

绘制前分别读取对应 `type-*.md` 并判断是否需要语义模式；这 6 张图默认不套用强制语义模式。每图先写一句核心结论、节点/箭头预算和明确删减项，超预算立即拆减而不是缩小字体。

- [ ] **Step 2：逐图生成自包含 HTML**

每个 HTML 必须：

- 使用 inline SVG 和 CSS。
- `<svg role="img">`，首个子元素为带前缀 ID 的 `<title>`，随后是 `<desc>`。
- 采用 4px 网格。
- 所有非共轴连接使用圆角正交路径。
- 箭头标签带遮罩并与线保持 6–10px。
- 不使用阴影、渐变、对角线或浮动图例。

- [ ] **Step 3：运行 diagram-design 自检**

对每个文件运行：

```bash
python3 /Users/zhujinqi/.claude/plugins/cache/diagram-design/diagram-design/2.3.5/skills/diagram-design/scripts/self_check.py mcp-java-tutorial-diagrams/<file>.html
python3 /Users/zhujinqi/.claude/plugins/cache/diagram-design/diagram-design/2.3.5/scripts/verify-geometry.py mcp-java-tutorial-diagrams/<file>.html
python3 /Users/zhujinqi/.claude/plugins/cache/diagram-design/diagram-design/2.3.5/scripts/lint-skin.py mcp-java-tutorial-diagrams/<file>.html
```

Expected: 6 个 HTML 通过工具能够覆盖的无障碍、单文件安全、皮肤和几何检查。断线、连接重叠、4px 网格和语义正确性仍必须在下一步人工检查，不能由 self_check 的通过代替。

- [ ] **Step 4：导出 PNG**

先运行：

```bash
python3 -c "import playwright"
python3 -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); b=p.chromium.launch(); b.close(); p.stop()"
```

若失败，停止导出并提示用户执行：

```bash
pip install playwright
playwright install chromium
```

不得自动安装。若通过，以 `diagram-design/references/export.md` 的导出器为基础创建 `/tmp/mcp-java-tutorial-verification/export_diagram.py`，并扩展为显式等待 `document.fonts.ready`、读取 `getComputedStyle` 断言 Geist/Instrument Serif 生效后再截图。逐个运行：

```bash
python3 /tmp/mcp-java-tutorial-verification/export_diagram.py \
  mcp-java-tutorial-diagrams/<file>.html \
  mcp-java-tutorial-diagrams/<file>.png \
  2
```

导出器必须等待 `document.fonts.ready`、断言 Geist/Instrument Serif 已加载，并只截图首个 `<svg>`。

Expected: 每个 HTML 旁存在同名 `1920×1200` PNG。`omit_background=True` 只移除浏览器背景；SVG 自带的 paper 背景矩形仍会保留，不能声称 PNG 完全透明。

- [ ] **Step 5：逐图视觉审查**

逐张读取 PNG，检查：

- 文章宽度下文字可直接阅读。
- 没有断线、共线路径、未桥接交叉和错误箭头方向。
- 没有节点文字溢出、标签遮挡或大面积无意义留白。
- 图 3 明确 Server 必须实现 discover、Client 可选调用并可直接业务请求。
- 图 4 不出现 Server 主动 JSON-RPC Request；MRTR 使用新 ID、`inputResponses`、`requestState`；acknowledged 先于带正确 subscriptionId 的通知。
- 图 5 的 HTTP 是 POST-only，Header/Body 一致，不出现 Session 或 Last-Event-ID。
- 图 6 明确 SDK 为 `2025-11-25`，Spring AI `STATELESS` 不表示支持 `2026-07-28`。
- 单图只表达一个核心结论。

Expected: 6 张图全部通过；任何失败先修改 HTML，再重新自检和导出。

- [ ] **Step 6：插入 Markdown**

按对应章节插入：

```markdown
![<准确的中文替代文本>](./mcp-java-tutorial-diagrams/<file>.png)
```

Expected: 6 个引用唯一、路径有效、替代文本描述图的结论而不是“如下图”。

### Task 7：最终验证与交付

**Files:**
- Verify: `mcp-java-core-principles-and-development-guide.md`
- Verify: `mcp-java-tutorial-diagrams/*.html`
- Verify: `mcp-java-tutorial-diagrams/*.png`

- [ ] **Step 1：检查 Markdown 和资源完整性**

Run:

```bash
rg -n '^!\[' mcp-java-core-principles-and-development-guide.md
rg -n 'TODO|TBD|待补|占位' mcp-java-core-principles-and-development-guide.md mcp-java-tutorial-diagrams
```

再使用临时 Python 脚本解析 Markdown 图片语法，断言引用数量为 6、路径唯一、目标存在，并断言目录中恰有 6 个 HTML 和 6 个 PNG。不能仅根据 `rg` 输出人工猜测数量。

Expected: 正好 6 个唯一且存在的本地图片引用；不存在占位文本。

- [ ] **Step 2：重新运行所有临时验证**

Run:

```bash
set -euo pipefail
cd /tmp/mcp-java-tutorial-verification/modern-wire && ./validate-all.sh
cd /tmp/mcp-java-tutorial-verification/java-sdk && mvn -q test
cd /tmp/mcp-java-tutorial-verification/spring-ai && mvn -q test
```

Expected: Schema、Java SDK、Spring AI 验证全部通过。

- [ ] **Step 3：检查文件与图片格式**

Run:

```bash
file mcp-java-tutorial-diagrams/*.png
sips -g pixelWidth -g pixelHeight mcp-java-tutorial-diagrams/*.png
```

Expected: 6 个文件均为有效 PNG，尺寸均为 `1920×1200`。

- [ ] **Step 4：执行最终规格审查**

使用独立审查者对照：

- `docs/superpowers/specs/2026-08-25-mcp-java-tutorial-design.md`
- `docs/superpowers/plans/2026-08-25-mcp-java-tutorial.md`

检查内容完整性、事实准确性、代码真实性、版本边界、图文一致性和引用质量。

Expected: 输出 `✅ Approved`。

- [ ] **Step 5：确认 Git 变更边界**

Run:

```bash
git status --short
git diff -- mcp-java-core-principles-and-development-guide.md docs/superpowers/specs/2026-08-25-mcp-java-tutorial-design.md docs/superpowers/plans/2026-08-25-mcp-java-tutorial.md
```

将最终状态与 `/tmp/mcp-java-tutorial-verification/git-status.before` 对比，并单独读取未跟踪的文章和 12 个图示文件；`git diff` 不用于证明未跟踪文件内容。

Expected: 用户原有 `.idea`、`__pycache__` 等状态保持不变；本任务只新增文章、6 个 HTML、6 个 PNG、设计和计划文件。

- [ ] **Step 6：清理临时产物**

先断言 `/tmp/mcp-java-tutorial-verification/.owned-by-mcp-java-tutorial-plan` 存在；不存在则停止并报告，不执行递归删除。存在时才删除该任务专属目录。不得删除或改动仓库中的用户文件。

- [ ] **Step 7：交付说明**

报告：

- 文章和配图路径。
- 实际锁定的规范、Java SDK、Spring AI、JDK 版本。
- 三组验证命令的结果。
- `2026-07-28` 与 Java 生态 `2025-11-25` 的关键限制。
- 未执行 Git commit 或 push。
