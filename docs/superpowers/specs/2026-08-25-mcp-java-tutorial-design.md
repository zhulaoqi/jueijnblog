# MCP Java 系统教程设计

## 1. 目标

编写一篇面向有 Spring Boot 经验、初次系统学习 MCP 的 Java 后端工程师的长篇教程。教程以 `2026-07-28` 正式规范为协议主线，以 Java 代码为验证手段，使读者能够准确理解 MCP 的参与方、消息模式、逐请求能力声明、核心功能、传输方式、兼容边界和生产约束。

截至 2026-08-25，官方 MCP Java SDK `2.0.1` 仍实现 `2025-11-25` 规范。教程必须正面说明这一代际差异：

- 使用 `2026-07-28` 规范、Schema 和 Java 线级消息代码讲解当前协议。
- 使用官方 Java SDK 与 Spring AI MCP 讲解 Java 生态当前可运行的 `2025-11-25` 实现。
- 通过版本迁移章节明确两代协议的差异，绝不把旧 SDK 行为描述为当前规范。

拟定成稿：

- 文件：`mcp-java-core-principles-and-development-guide.md`
- 规模：约 1.5 万至 2.5 万字
- 写法：协议内核优先、单一案例贯穿
- 代码路线：Java 线级消息解释当前规范，官方 Java SDK 解释现有类型映射，Spring AI MCP 展示工程化接入

## 2. 读者与前置知识

目标读者具备：

- Java 基础和 Maven 使用经验
- Spring Boot 基础
- HTTP、JSON 和异步调用的基本概念

正文会在使用处解释 JSON-RPC、SSE、逐请求元数据和能力声明，不要求读者预先接触过 Agent 或 MCP。

## 3. 内容边界

### 3.1 必须覆盖

- MCP 解决的问题及其与 Agent 框架、REST API、函数调用的边界
- Host、MCP Client、MCP Server、Transport 的职责和信任边界
- JSON-RPC 2.0 请求、响应、通知、错误和标识符
- `server/discover`、逐请求协议版本与能力声明、`UnsupportedProtocolVersionError`
- Request/Response、MRTR、Subscribe/Notify 三种消息模式
- 所有成功结果的 `resultType`，以及 `InputRequiredResult`、`inputRequests`、`inputResponses`、`requestState`
- Tools、Resources、Prompts 三类 Server Features
- Elicitation，以及已经弃用但仍处于兼容窗口的 Roots、Sampling
- Logging 作为已弃用的 Server Utility，而不是 Client Feature
- 进度、取消、分页、补全、`subscriptions/listen`、`ttlMs` 和 `cacheScope`
- stdio 与 Streamable HTTP，包括标准头部、请求作用域 SSE、终止和重试边界
- 无协议级 Session、无 Server 主动 JSON-RPC Request、无 SSE 恢复的现代语义
- 协议无状态与实现无状态的区别：Server 可以持久化业务状态，但必须通过显式句柄、Tasks ID 或授权主体关联请求，不能依赖隐式连接状态
- Tasks 扩展的定位和最小流程，不把它误写成核心协议
- `2026-07-28` 与 `2025-11-25` 的版本迁移和兼容探测
- 官方 Java SDK 的协议类型与同步、异步 API 映射
- Spring AI MCP 的自动配置方式及其隐藏的协议细节
- HTTP Authorization 的资源元数据发现、授权服务器发现、PKCE、客户端注册选择和 Token 边界，以及 stdio 从环境获取凭据的边界
- 输入校验、超时、背压、幂等、审计和可观测性
- 调试、版本兼容、能力降级和常见错误定位

### 3.2 不作为主线

- 不把教程写成 Spring Boot 配置手册
- 不系统讲解 LLM、RAG 或 Agent 框架
- 不把某个客户端产品的私有行为写成 MCP 标准
- 不保留独立示例工程
- 不使用大量互不相关的小案例
- 不实现完整 OAuth Authorization Server
- 不实现 Token 签发、账户系统或完整 OAuth Provider
- 不实现自定义传输、完整 Tasks 扩展或全量客户端兼容矩阵
- 不用 Java SDK 旧 API 模拟不存在的 `2026-07-28` 支持

## 4. 叙事方案

采用“协议内核优先、案例贯穿”的结构：

1. 先建立 MCP 的系统边界和运行时心智模型。
2. 再从线上消息解释现代协议的无状态逐请求模型。
3. 接着拆解普通请求、MRTR 和订阅通知三种交互模式。
4. 使用同一案例贯通 Server Features、Client Features 和两种传输。
5. 再解释官方 Java SDK 与 Spring AI 当前为何仍呈现旧初始化和 Session 语义。
6. 最后给出迁移、生产化和调试方法。

每段核心代码之前先说明它对应的协议版本、线上消息、状态变化和能力前提，避免框架 API 掩盖协议语义。

## 5. 章节结构

1. **MCP 解决什么问题**：定义、非目标及与常见集成方式的区别。
2. **运行时全景**：Host、Client、Server、Transport、请求作用域和信任边界。
3. **协议基础**：JSON-RPC、`_meta`、`resultType`、错误对象和方法命名。
4. **现代版本协商**：`server/discover`、逐请求版本与能力声明、失败与重试。
5. **三种消息模式**：Request/Response、MRTR、Subscribe/Notify。
6. **Server Features**：Tools、Resources、Prompts 的语义、发现、缓存与使用。
7. **Client Features**：以 Elicitation 为主线，解释 MRTR；Roots、Sampling 放入弃用兼容说明。
8. **横切机制与扩展**：进度、取消、分页、补全、订阅、已弃用的 Logging，以及 Tasks 扩展边界。
9. **传输层**：stdio、Streamable HTTP、标准头部、请求作用域 SSE、终止与重试。
10. **Java 版本现实**：`2026-07-28` 规范与 Java SDK `2025-11-25` 基线对照矩阵，并区分协议无状态和 Spring AI `STATELESS` 部署模式。
11. **官方 Java SDK 实战**：在明确旧协议语义的前提下讲 Server/Client、同步/异步和两种传输。
12. **Spring AI MCP 实战**：自动配置、注解或回调适配及其隐藏的协议细节。
13. **迁移与兼容**：初始化、Session、Server 主动请求和旧订阅如何迁移到现代模型。
14. **生产化与调试**：安全、可靠性、可观测性、Inspector、线级日志和能力降级。
15. **内核总结**：现代请求端到端时序、开发检查清单和协议对象速查。

## 6. 贯通案例

案例为“研发知识库 MCP”，包含：

- Resource：`kb://documents/{id}`，用于解释资源 URI、模板、内容类型、缓存和订阅。
- Tool：`search_documents`，用于解释工具发现、JSON Schema 输入、结构化结果、错误和取消。
- Prompt：`incident_analysis`，用于解释 Prompt 是用户可选择的消息模板，而不是可执行 Tool。
- MRTR：`search_documents` 在执行高成本检索前，通过包含 `elicitation/create` 的 `InputRequiredResult` 收集“检索理由和用户确认”等非敏感输入；Client 以新 JSON-RPC ID、`inputResponses` 和原 `requestState` 重试。Form Elicitation 不收集密码或 Token，也不代替 MCP Authorization；需要在交互中收集第三方凭据时必须使用 URL Elicitation，不能经由 MCP Client 传给 Server，预配置或环境提供的凭据不在此限制内。
- 订阅：Server 声明 `resources.subscribe`；Client 通过 `subscriptions/listen` 订阅指定资源更新；acknowledged 返回实际接受的过滤条件，且必须先于 `notifications/resources/updated`；每条通知携带匹配的 `_meta.io.modelcontextprotocol/subscriptionId`。
- Transport：stdio 展示换行帧、取消和子进程退出；Streamable HTTP 展示 POST-only、标准头部、无 `Mcp-Session-Id` 和请求作用域 SSE。

当前协议的线级消息使用 Java 21 `HttpClient`、Jackson 数据结构或最小消息编解码代码表达，并通过 `2026-07-28` Schema 校验。官方 Java SDK 与 Spring AI 的可运行案例单独标记为 `2025-11-25` 语义。Roots、Sampling 只用于迁移说明，不作为新实现推荐路径。

## 7. 配图设计

使用 `diagram-design` 生成 6 张图：

1. MCP 生态与信任边界全景图
2. 现代 MCP 逐请求元数据与三种消息模式
3. `server/discover`、版本选择、请求与版本重试流程
4. Tools / Resources / Prompts、Elicitation MRTR 与订阅交互图
5. stdio 与 Streamable HTTP 的帧、流和终止对比图
6. `2026-07-28` 规范、Java SDK、Spring AI 与迁移边界图

每张图只承担一个核心结论。协议字段、消息样例和 Java 类型不塞入图片，而使用正文代码块或短列表表达。交付时保留可编辑 HTML 和文章引用的 PNG。

## 8. 准确性策略

资料优先级：

1. 对应版本的 MCP 正式规范与官方 JSON Schema
2. 官方 MCP Java SDK 源码、发布说明和 Javadoc
3. Spring AI 官方参考文档与源码
4. 官方示例
5. 其他网络资料仅用于交叉验证

用户提供的 `/docs/2026-07-28/` 对应 `2026-07-28` 正式规范文档。文章分别记录：

- 正式规范版本
- 每个请求声明的 `protocolVersion`
- 官方 Java SDK 依赖版本
- Java SDK 实现的规范基线
- Spring AI 依赖版本
- Spring AI 传递依赖的 Java SDK 版本与规范基线
- 资料核验日期

规范中的 MUST、SHOULD、MAY 按原意表述。所有版本敏感结论必须区分“`2026-07-28` 协议规定”“`2025-11-25` Java SDK 行为”“Spring AI 封装行为”。正文开头和 Java 实战章节前各放置一次版本矩阵，防止读者跨版本套用。矩阵单列“协议无状态”和“框架部署模式”：Spring AI 的 `STATELESS` 只描述服务端部署状态策略，不代表它已实现 `2026-07-28` 逐请求协议。

## 9. 代码与消息设计

- Java 代码以 Maven 依赖和可复制片段呈现。
- 每段 Java 代码必须标明协议版本；示例中的方法名、能力声明、请求 ID、响应和错误保持前后一致。
- `2026-07-28` 消息示例必须包含逐请求 `_meta`，成功结果必须包含 `resultType`。
- 关键 Java API 旁给出对应 JSON-RPC 方法或消息。
- 同步 API 用于展示最短路径，异步 API 用于解释生产环境中的并发、取消和背压。
- 在临时目录建立验证工程，编译并运行代码，但不把验证工程保留在仓库。
- 使用官方 Java SDK 分别验证一次 `2025-11-25` stdio 和 Streamable HTTP 端到端交互。
- 使用官方 `2026-07-28` Schema 校验全部现代协议消息。标准化线级日志只保存在临时目录，关键片段嵌入文章，验收后与临时工程一并删除。
- 当前 Java SDK 无法覆盖的现代能力明确记录为“SDK 尚未实现”，不以“实验性”代替。

## 10. 验收标准

- 读者可以描述现代 MCP 从 `server/discover` 或直接请求，到逐请求版本选择、MRTR/订阅和传输终止的完整流程。
- 读者能解释为什么 `2026-07-28` 没有协议级 Session，也没有 Server 主动 JSON-RPC Request。
- 读者不会把“协议无状态”误解为 Server 不得保存任何业务状态，也不会把 Spring AI `STATELESS` 当作现代协议支持证明。
- 读者能区分 Tools、Resources、Prompts、Elicitation 和 Tasks 扩展。
- 关键协议结论可追溯到正式规范。
- 不把正式规范版本、Java SDK 版本和 Spring AI 版本混为一谈。
- 代码使用真实发布 API，并经过编译或最小运行验证。
- 所有现代消息样例通过 `2026-07-28` 官方 Schema 校验。
- MRTR 示例验证新请求 ID、`inputResponses` 和 `requestState`；订阅示例验证 acknowledged 必须先于更新通知。
- 订阅示例验证 Server 能力声明、accepted filter、所有通知的 subscriptionId、断线后重新发送 `subscriptions/listen`，并区分 stdio 取消通知与 HTTP 关闭响应流。
- HTTP 示例验证 `MCP-Protocol-Version`、`Mcp-Method`、适用时的 `Mcp-Name`，且不出现 `Mcp-Session-Id`。
- stdio 示例验证单行帧、`stderr` 隔离、取消和进程退出。
- `server/discover`、`tools/list`、`prompts/list`、`resources/list`、`resources/templates/list` 和 `resources/read` 的完整结果包含合法的 `ttlMs` 与 `cacheScope`；`input_required` 及携带 `inputResponses`/`requestState` 的重试结果不得缓存；变更通知使相关缓存失效。
- 弃用能力、实验性能力和版本差异有醒目标注。
- 6 张图与正文语义一致，在文章常见显示宽度下可直接阅读。
- 文末列出一手资料、版本和核验日期。

## 11. 交付物

- `mcp-java-core-principles-and-development-guide.md`
- MCP 教程配图目录中的 6 个 HTML 文件
- 对应的 6 个 PNG 文件

不创建或保留独立 Maven 示例工程。
