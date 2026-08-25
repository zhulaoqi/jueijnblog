#!/usr/bin/env python3
"""Generate the 27 doc-wide Hermes architecture diagrams as accessible HTML/SVG."""

from __future__ import annotations

from pathlib import Path

from primitives import (
    ACCENT,
    INK,
    MUTED,
    PAPER,
    RULE,
    arrow_label,
    bus,
    caption,
    connector,
    diamond,
    layer_band,
    node,
    stack,
    stage_header,
    wrap,
    zone,
)

OUT = Path(__file__).resolve().parent


def diagram_01_runtime_stack() -> str:
    slug = "runtime-stack"
    body = stack(
        [
            caption(92, 72, "能力从底层约束向上组合"),
            connector(slug, [(72, 500), (72, 96)], style="accent"),
            layer_band(160, 60, 960, 80, "L5", "交互与自治", "多端路由 · Cron · 子 Agent"),
            layer_band(160, 148, 960, 80, "L4", "上下文系统", "Prompt · 压缩 · Memory · Skills"),
            layer_band(160, 236, 960, 80, "L3", "执行与状态", "工具调用 · 审批 · Session 持久化", focal=True),
            layer_band(160, 324, 960, 80, "L2", "模型运行时", "Provider 解析 · 故障转移 · 缓存"),
            layer_band(160, 412, 960, 80, "L1", "安全与资源边界", "沙箱 · 权限 · 中断 · 可观测性"),
        ]
    )
    return wrap(
        slug,
        "Layer Stack · Hermes",
        "Agent Runtime 能力叠加",
        "Hermes Agent Runtime 由安全资源、模型运行时、执行状态、上下文系统和交互自治五层能力组合。",
        560,
        body,
    )


def diagram_02_overall_architecture() -> str:
    slug = "overall-architecture"
    zones = zone(40, 40, 1120, 144, "入口与适配") + zone(40, 220, 1120, 300, "共享 Agent Runtime")
    edges = stack(
        [
            connector(slug, [(200, 156), (200, 196), (516, 196), (516, 260)]),
            connector(slug, [(520, 156), (520, 212), (600, 212), (600, 260)], style="accent"),
            connector(slug, [(840, 156), (840, 196), (684, 196), (684, 260)]),
            connector(slug, [(516, 352), (516, 380), (260, 380), (260, 420)]),
            connector(slug, [(600, 352), (600, 396), (580, 396), (580, 420)]),
            connector(slug, [(684, 352), (684, 380), (900, 380), (900, 420)]),
        ]
    )
    nodes = stack(
        [
            node(80, 76, 240, 80, "ENTRY", "多端入口", "CLI · IM · IDE"),
            node(400, 76, 240, 80, "ADAPTER", "协议适配", "Gateway · ACP · API"),
            node(720, 76, 240, 80, "SCHED", "主动触发", "Cron · Background"),
            node(460, 260, 280, 92, "CORE", "AIAgent", "推理 → 工具 → 反馈", kind="focal"),
            node(140, 420, 240, 76, "EXEC", "Tool / MCP", "真实世界副作用"),
            node(460, 420, 240, 76, "MODEL", "Provider Runtime", "厂商与 API 差异"),
            node(780, 420, 240, 76, "STATE", "Session / Memory", "连续性与可恢复", kind="store"),
        ]
    )
    return wrap(
        slug,
        "Architecture · Hermes",
        "一个内核，多个入口",
        "多个入口通过协议适配汇入同一个 AIAgent，并共享工具、Provider 与状态运行时。",
        560,
        zones + edges + nodes,
    )


def diagram_03_gateway_bus() -> str:
    slug = "gateway-bus"
    zones = zone(40, 36, 1120, 140, "平台适配器") + zone(40, 208, 1120, 144, "Canonical Event") + zone(40, 388, 1120, 132, "Gateway 协调")
    edges = stack(
        [
            connector(slug, [(180, 140), (180, 228)], style="link"),
            connector(slug, [(460, 140), (460, 228)], style="link"),
            connector(slug, [(740, 140), (740, 228)], style="link"),
            connector(slug, [(1020, 140), (1020, 228)], style="link"),
            connector(slug, [(180, 320), (180, 420)]),
            connector(slug, [(460, 320), (460, 420)]),
            connector(slug, [(740, 320), (740, 420)]),
            connector(slug, [(1020, 320), (1020, 420)]),
        ]
    )
    nodes = stack(
        [
            node(80, 72, 200, 68, "PLATFORM", "Telegram / Slack", "raw event", kind="external"),
            node(360, 72, 200, 68, "PLATFORM", "Discord / Email", "raw event", kind="external"),
            node(640, 72, 200, 68, "PLATFORM", "ACP / TUI", "JSON-RPC", kind="external"),
            node(920, 72, 200, 68, "PLATFORM", "HTTP / Cron", "request · tick", kind="external"),
            node(80, 228, 1040, 92, "EVENT", "MessageEvent", "统一会话、发送者、内容与投递目标", kind="focal"),
            node(80, 420, 200, 72, "ROUTE", "Session Router", "定位会话"),
            node(360, 420, 200, 72, "LIFE", "Lifecycle", "创建 · 中断"),
            node(640, 420, 200, 72, "CALLBACK", "Event Bridge", "进度 · 审批"),
            node(920, 420, 200, 72, "DELIVERY", "Delivery", "多端出站"),
        ]
    )
    return wrap(
        slug,
        "Architecture · Gateway",
        "多端输入规范化为统一 MessageEvent",
        "四组平台适配器独立接入 MessageEvent，再由会话、生命周期、回调和投递模块协调。",
        560,
        zones + edges + nodes,
    )


def diagram_04_two_level_guards() -> str:
    slug = "two-level-guards"
    zones = zone(32, 48, 496, 484, "Adapter Guard") + zone(548, 48, 620, 484, "Gateway Guard")
    edges = stack(
        [
            connector(slug, [(216, 320), (280, 320)], style="accent"),
            connector(slug, [(340, 260), (340, 136), (472, 136)]),
            connector(slug, [(576, 176), (576, 220), (620, 220), (620, 252)]),
            connector(slug, [(400, 320), (536, 320)]),
            connector(slug, [(704, 320), (760, 320)]),
            connector(slug, [(820, 260), (820, 184), (976, 184)]),
            connector(slug, [(820, 380), (820, 420), (976, 420)]),
            connector(slug, [(620, 388), (620, 468)]),
        ]
    )
    labels = stack(
        [
            arrow_label(408, 128, "是"),
            arrow_label(468, 312, "否"),
            arrow_label(900, 176, "是"),
            arrow_label(900, 412, "否"),
            arrow_label(628, 440, "未运行", anchor="start"),
        ]
    )
    nodes = stack(
        [
            node(48, 280, 168, 80, "EVENT", "新消息", "same session"),
            diamond(340, 320, 120, 120, "活跃会话？", focal=True),
            node(472, 96, 208, 80, "QUEUE", "Pending Queue", "set interrupt"),
            diamond(620, 320, 168, 136, "Agent 运行中？"),
            diamond(820, 320, 120, 120, "特殊命令？"),
            node(976, 144, 168, 80, "CMD", "/stop /approve", "允许穿透"),
            node(976, 380, 168, 80, "INT", "中断当前推理", "普通消息 steer"),
            node(512, 468, 216, 72, "NEW", "创建 AIAgent", "无并发写入"),
        ]
    )
    return wrap(
        slug,
        "Flowchart · Gateway",
        "两级消息守卫",
        "Adapter 先拦截同会话竞态，Gateway 再区分运行状态、特殊命令和普通中断语义。",
        572,
        zones + edges + labels + nodes,
    )


def diagram_05_delivery_router() -> str:
    slug = "delivery-router"
    edges = stack(
        [
            connector(slug, [(600, 128), (600, 200)], style="accent"),
            connector(slug, [(508, 292), (508, 340), (180, 340), (180, 400)]),
            connector(slug, [(568, 292), (568, 356), (460, 356), (460, 400)]),
            connector(slug, [(632, 292), (632, 356), (740, 356), (740, 400)]),
            connector(slug, [(692, 292), (692, 340), (1020, 340), (1020, 400)]),
        ]
    )
    nodes = stack(
        [
            node(460, 48, 280, 80, "OUTPUT", "AIAgent 输出", "text · artifact · event", kind="focal"),
            node(420, 200, 360, 92, "ROUTER", "Delivery Router", "解析 delivery_target"),
            node(60, 400, 240, 76, "ORIGIN", "当前会话", "origin chat"),
            node(340, 400, 240, 76, "CHANNEL", "IM / Thread", "指定 channel"),
            node(620, 400, 240, 76, "ASYNC", "Cron / 后台任务", "不污染聊天历史"),
            node(900, 400, 240, 76, "SINK", "Email / Local", "外部投递", kind="external"),
        ]
    )
    return wrap(
        slug,
        "Data Flow · Gateway",
        "出站投递总线",
        "Delivery Router 将统一 Agent 输出独立路由到当前会话、IM 线程、后台任务或外部目标。",
        520,
        edges + nodes,
    )


def diagram_06_callback_bus() -> str:
    slug = "callback-bus"
    edges = stack(
        [
            connector(slug, [(600, 132), (600, 204)], style="accent"),
            connector(slug, [(468, 296), (468, 348), (180, 348), (180, 404)]),
            connector(slug, [(556, 296), (556, 364), (460, 364), (460, 404)]),
            connector(slug, [(644, 296), (644, 364), (740, 364), (740, 404)]),
            connector(slug, [(732, 296), (732, 348), (1020, 348), (1020, 404)]),
        ]
    )
    nodes = stack(
        [
            node(440, 48, 320, 84, "CORE", "AIAgent", "唯一执行事件源", kind="focal"),
            node(360, 204, 480, 92, "CALLBACK", "Callback Event Stream", "tool · thinking · token · approval"),
            node(60, 404, 240, 76, "HOST", "CLI", "spinner · token"),
            node(340, 404, 240, 76, "HOST", "Gateway", "进度 · 审批"),
            node(620, 404, 240, 76, "HOST", "ACP / IDE", "session/update"),
            node(900, 404, 240, 76, "HOST", "TUI RPC", "tool.start"),
        ]
    )
    return wrap(
        slug,
        "Architecture · Events",
        "AIAgent 回调事件总线",
        "同一 AIAgent 回调流被 CLI、Gateway、ACP 和 TUI 宿主独立消费。",
        520,
        edges + nodes,
    )


def diagram_07_run_conversation() -> str:
    slug = "run-conversation"
    zones = stack(
        [
            zone(32, 48, 248, 424, "01 准备"),
            zone(304, 48, 248, 424, "02 解析"),
            zone(576, 48, 360, 424, "03 执行循环"),
            zone(960, 48, 208, 424, "04 提交"),
        ]
    )
    edges = stack(
        [
            connector(slug, [(248, 260), (336, 260)]),
            connector(slug, [(520, 260), (568, 260), (568, 224), (620, 224)]),
            connector(slug, [(680, 268), (680, 304), (664, 304), (664, 332)]),
            connector(slug, [(736, 372), (768, 372)]),
            connector(slug, [(840, 332), (840, 296), (840, 268)]),
            connector(slug, [(900, 224), (996, 224)]),
        ]
    )
    nodes = stack(
        [
            stage_header(52, 84, "1", "准备"),
            stage_header(324, 84, "2", "解析"),
            stage_header(596, 84, "3", "执行循环"),
            stage_header(980, 84, "4", "提交"),
            node(64, 212, 184, 96, "SETUP", "会话准备", ["task/session", "追加用户消息"]),
            node(336, 212, 184, 96, "CONTEXT", "解析上下文", ["Prompt · 压缩", "Provider · 格式"]),
            node(620, 180, 280, 88, "MODEL", "模型输出解析", "决策 · 可中断调用", kind="focal"),
            node(592, 332, 144, 80, "TOOL", "工具执行", "dispatch · hook"),
            node(768, 332, 144, 80, "RESULT", "Tool Result", "role=tool", kind="store"),
            node(996, 180, 148, 88, "COMMIT", "提交", ["持久化", "Memory · 返回"], kind="store"),
        ]
    )
    return wrap(
        slug,
        "Process · Agent Loop",
        "run_conversation：四阶段单轮分发",
        "单轮运行依次完成准备、解析、模型与工具循环、持久化提交，其中工具结果明确回到模型。",
        520,
        zones + edges + nodes,
    )


def diagram_08_canonical_model() -> str:
    slug = "canonical-model"
    zones = zone(32, 48, 304, 448, "外部输入协议") + zone(412, 48, 376, 448, "内部规范模型") + zone(864, 48, 304, 448, "Provider API")
    edges = stack(
        [
            connector(slug, [(296, 144), (368, 144), (368, 244), (460, 244)], style="link"),
            connector(slug, [(296, 272), (388, 272), (388, 288), (460, 288)], style="link"),
            connector(slug, [(296, 400), (368, 400), (368, 332), (460, 332)], style="link"),
            connector(slug, [(740, 244), (832, 244), (832, 144), (904, 144)]),
            connector(slug, [(740, 288), (812, 288), (812, 272), (904, 272)]),
            connector(slug, [(740, 332), (832, 332), (832, 400), (904, 400)]),
        ]
    )
    nodes = stack(
        [
            node(72, 104, 224, 80, "HOST", "Gateway / CLI", "MessageEvent", kind="external"),
            node(72, 232, 224, 80, "HOST", "ACP / IDE", "JSON-RPC", kind="external"),
            node(72, 360, 224, 80, "HOST", "HTTP / SDK", "request", kind="external"),
            node(460, 196, 280, 184, "CANON", "Canonical Message", ["system · user", "assistant · tool"], kind="focal"),
            node(904, 104, 224, 80, "API", "Chat Completions", "OpenAI"),
            node(904, 232, 224, 80, "API", "Responses", "Codex"),
            node(904, 360, 224, 80, "API", "Messages", "Anthropic"),
        ]
    )
    return wrap(
        slug,
        "Architecture · Messages",
        "Canonical Model：协议边缘适配，内核保持统一",
        "三类宿主协议通过独立端口汇入 Canonical Message，再由三个独立端口适配到不同 Provider API。",
        544,
        zones + edges + nodes,
    )


def diagram_09_tool_dispatch() -> str:
    slug = "tool-dispatch"
    edges = stack(
        [
            connector(slug, [(232, 148), (320, 148)], style="accent"),
            connector(slug, [(520, 148), (608, 148)]),
            connector(slug, [(708, 196), (708, 248)]),
            connector(slug, [(808, 148), (888, 148)]),
            connector(slug, [(808, 296), (888, 296)]),
            connector(slug, [(1088, 148), (1144, 148), (1144, 488), (584, 488), (584, 476)]),
            connector(slug, [(988, 336), (988, 376), (656, 376), (656, 400)]),
            connector(slug, [(520, 436), (336, 436), (336, 188)], dashed=True),
        ]
    )
    labels = arrow_label(848, 140, "STATE") + arrow_label(848, 288, "REGISTRY")
    nodes = stack(
        [
            node(48, 108, 184, 80, "MODEL", "tool_call", "name + arguments", kind="focal"),
            node(320, 108, 200, 80, "AGENT", "_invoke_tool", "校验与上下文"),
            diamond(708, 148, 200, 96, "内核特判？"),
            node(608, 248, 200, 96, "REGISTRY", "Registry + Hooks", "pre · dispatch · post"),
            node(888, 108, 200, 80, "STATE", "Agent-state Tool", "显式上下文"),
            node(888, 256, 200, 80, "HANDLER", "Tool Handler", "执行副作用"),
            node(520, 400, 200, 76, "RESULT", "role=tool", "回灌 messages", kind="store"),
        ]
    )
    return wrap(
        slug,
        "Flowchart · Tools",
        "工具调用分发链",
        "模型调用意图经 AIAgent 校验后进入内核特判或 Registry 与 Hooks，执行结果再回灌消息历史。",
        520,
        edges + labels + nodes,
    )


def diagram_10_dual_compression() -> str:
    slug = "dual-compression"
    zones = zone(32, 48, 488, 432, "Gateway Session Hygiene") + zone(544, 48, 624, 432, "AIAgent Active Context")
    edges = stack(
        [
            connector(slug, [(208, 268), (240, 268)]),
            connector(slug, [(300, 208), (300, 136), (384, 136)]),
            connector(slug, [(484, 176), (484, 232), (576, 232)]),
            connector(slug, [(360, 268), (540, 268)]),
            connector(slug, [(600, 208), (600, 136), (760, 136)], style="accent"),
            connector(slug, [(1000, 136), (1040, 136), (1040, 228)]),
            connector(slug, [(660, 268), (920, 268)]),
        ]
    )
    labels = stack(
        [
            arrow_label(308, 184, ">85%", anchor="start"),
            arrow_label(448, 260, "≤85%"),
            arrow_label(680, 128, ">50%"),
            arrow_label(792, 260, "≤50%"),
        ]
    )
    nodes = stack(
        [
            node(48, 228, 160, 80, "IN", "入站消息", "跨轮会话"),
            diamond(300, 268, 120, 120, "超过 85%？"),
            node(384, 96, 200, 80, "SAFETY", "Gateway 清理", "会话安全网"),
            diamond(600, 268, 120, 120, "超过 50%？"),
            node(760, 96, 240, 80, "COMPRESS", "ContextCompressor", "主动压缩", kind="focal"),
            node(920, 228, 240, 80, "MODEL", "进入模型", "保留执行余量", kind="store"),
        ]
    )
    return wrap(
        slug,
        "Flowchart · Context",
        "双层上下文压缩",
        "Gateway 以 85% 阈值兜底异常长会话，AIAgent 以 50% 阈值主动压缩并为后续执行留出空间。",
        524,
        zones + edges + labels + nodes,
    )


def diagram_11_compression_phases() -> str:
    slug = "compression-phases"
    edges = stack(
        [
            connector(slug, [(280, 276), (328, 276)]),
            connector(slug, [(560, 276), (608, 276)]),
            connector(slug, [(840, 276), (888, 276)]),
        ]
    )
    nodes = stack(
        [
            stage_header(48, 80, "1", "机械清理"),
            stage_header(328, 80, "2", "确定边界"),
            stage_header(608, 80, "3", "结构摘要"),
            stage_header(888, 80, "4", "重组修复"),
            node(48, 180, 232, 192, "CLEAN", "旧工具输出", ["保护区外替换", "可重新获取优先"]),
            node(328, 180, 232, 192, "BOUND", "三段边界", ["固定头部 · 摘要中段", "逐字尾部 · 调用成组"]),
            node(608, 180, 232, 192, "SUMMARY", "状态移交单", ["Goal · Progress", "Decisions · Next Steps"], kind="focal"),
            node(888, 180, 232, 192, "REPAIR", "合法消息序列", ["保留头尾 · 插入摘要", "修复孤立 Tool Result"]),
        ]
    )
    return wrap(
        slug,
        "Process · Context",
        "四阶段上下文压缩算法",
        "压缩依次执行旧输出清理、保留边界确定、结构化摘要和消息合法性重组。",
        440,
        edges + nodes,
    )


def diagram_12_mcp_architecture() -> str:
    slug = "mcp-architecture"
    zones = zone(32, 36, 1136, 140, "Host") + zone(32, 204, 1136, 144, "Host 内 1:1 Client") + zone(32, 380, 1136, 140, "External MCP Server")
    edges = stack(
        [
            connector(slug, [(536, 144), (536, 184), (180, 184), (180, 232)], style="link"),
            connector(slug, [(600, 144), (600, 232)], style="link"),
            connector(slug, [(664, 144), (664, 184), (1020, 184), (1020, 232)], style="link"),
            connector(slug, [(180, 312), (180, 408)], style="link"),
            connector(slug, [(600, 312), (600, 408)], style="link"),
            connector(slug, [(1020, 312), (1020, 408)], style="link"),
        ]
    )
    nodes = stack(
        [
            node(480, 72, 240, 72, "HOST", "Hermes Host", "Agent application", kind="focal"),
            node(60, 232, 240, 80, "CLIENT 1", "GitHub Client", "独立 JSON-RPC"),
            node(480, 232, 240, 80, "CLIENT 2", "Database Client", "独立 JSON-RPC"),
            node(900, 232, 240, 80, "CLIENT 3", "Browser Client", "独立 JSON-RPC"),
            node(60, 408, 240, 80, "SERVER 1", "GitHub Server", "tools · resources", kind="store"),
            node(480, 408, 240, 80, "SERVER 2", "Database Server", "tools · resources", kind="store"),
            node(900, 408, 240, 80, "SERVER 3", "Browser Server", "tools · resources", kind="store"),
        ]
    )
    return wrap(
        slug,
        "Architecture · MCP",
        "MCP 三方角色与 1:1 Client 连接",
        "Hermes Host 维护三个独立 MCP Client，每个 Client 只连接对应的一个 MCP Server。",
        556,
        zones + edges + nodes,
    )


def diagram_13_protocol_compare() -> str:
    slug = "protocol-compare"
    body = stack(
        [
            caption(100, 60, "交互双方"),
            caption(1100, 60, "协议职责", anchor="end"),
            layer_band(100, 88, 1000, 112, "MCP", "Agent ↔ Tool", "发现并调用工具、资源与 Prompt", focal=True),
            layer_band(100, 216, 1000, 112, "ACP", "IDE ↔ Agent", "会话、流式进度、权限与取消"),
            layer_band(100, 344, 1000, 112, "A2A", "Agent ↔ Agent", "任务、消息、Artifact 与远程协作"),
        ]
    )
    return wrap(
        slug,
        "Layer Stack · Protocols",
        "MCP、ACP、A2A：三种协议解决三种边界",
        "MCP 面向工具调用，ACP 面向 IDE 驱动 Agent，A2A 面向远程 Agent 协作。",
        520,
        body,
    )


def diagram_14_memory_layers() -> str:
    slug = "memory-layers"
    body = stack(
        [
            caption(92, 68, "参与推理频率 ↑"),
            connector(slug, [(72, 492), (72, 92)], style="accent"),
            layer_band(160, 60, 960, 80, "L5", "工作记忆", "当前 Prompt · 最近消息 · 工具结果"),
            layer_band(160, 148, 960, 80, "L4", "整理记忆", "MEMORY.md · USER.md · 有界可读", focal=True),
            layer_band(160, 236, 960, 80, "L3", "情节历史", "SQLite Session · FTS5 · 原文可审计"),
            layer_band(160, 324, 960, 80, "L2", "历史检索", "session_search · 按需召回"),
            layer_band(160, 412, 960, 80, "L1", "程序性技能", "Skills · 可复用的“怎么做”"),
        ]
    )
    return wrap(
        slug,
        "Layer Stack · Memory",
        "会话、记忆、检索与技能分层",
        "Hermes 将工作上下文、整理记忆、会话历史、历史检索和程序性技能分为五层。",
        560,
        body,
    )


def diagram_15_module_boundaries() -> str:
    slug = "module-boundaries"
    zones = stack(
        [
            zone(32, 40, 260, 460, "Edge"),
            zone(316, 40, 340, 460, "Runtime Core"),
            zone(680, 40, 488, 284, "Capabilities"),
            zone(680, 348, 488, 152, "State & Observe"),
        ]
    )
    edges = stack(
        [
            connector(slug, [(252, 156), (364, 156)], style="link"),
            connector(slug, [(252, 388), (332, 388), (332, 244), (364, 244)], style="link"),
            connector(slug, [(604, 200), (720, 200)], style="accent"),
            connector(slug, [(604, 232), (688, 232), (688, 284), (720, 284)]),
            connector(slug, [(444, 292), (444, 348), (812, 348), (812, 372)]),
            connector(slug, [(524, 292), (524, 332), (1036, 332), (1036, 372)]),
        ]
    )
    nodes = stack(
        [
            node(72, 112, 180, 88, "ENTRY", "Entry Adapters", "Gateway · ACP · API"),
            node(72, 344, 180, 88, "EVENT", "Canonical Events", "messages.py"),
            node(364, 132, 240, 160, "CORE", "runtime.py", ["Run 状态机", "只依赖接口"], kind="focal"),
            node(720, 112, 184, 88, "CONTEXT", "Context Engine", "prompt · compress"),
            node(944, 112, 184, 88, "PROVIDER", "Providers", "model APIs"),
            node(720, 240, 184, 88, "TOOLS", "Tools / MCP", "capability"),
            node(720, 372, 184, 88, "STATE", "State Store", "session · memory", kind="store"),
            node(944, 372, 184, 88, "TRACE", "Observability", "events · cost", kind="store"),
        ]
    )
    return wrap(
        slug,
        "Architecture · Kernel",
        "自研 Agent 内核模块边界",
        "运行时核心只依赖消息、上下文、Provider、工具、状态与可观测接口，不直接依赖外部实现。",
        540,
        zones + edges + nodes,
    )


def diagram_16_summary_loop() -> str:
    slug = "summary-loop"
    edges = stack(
        [
            connector(slug, [(600, 112), (1000, 112), (1000, 168)]),
            connector(slug, [(1000, 248), (1000, 292)]),
            connector(slug, [(1000, 372), (1000, 520), (600, 520), (600, 492)]),
            connector(slug, [(480, 452), (200, 452), (200, 372)]),
            connector(slug, [(200, 292), (200, 248)]),
            connector(slug, [(200, 168), (200, 112), (480, 112)], style="accent"),
            connector(slug, [(880, 332), (720, 332)], dashed=True),
            connector(slug, [(600, 412), (600, 348)], dashed=True),
        ]
    )
    nodes = stack(
        [
            node(480, 72, 240, 80, "INPUT", "用户输入", "goal · context"),
            node(880, 168, 240, 80, "ROUTE", "Gateway 路由", "session"),
            node(880, 292, 240, 80, "DECIDE", "模型 / 工具", "decision loop", kind="focal"),
            node(480, 412, 240, 80, "PERSIST", "状态持久化", "session · memory", kind="store"),
            node(80, 292, 240, 80, "DELIVER", "多端投递", "output"),
            node(80, 168, 240, 80, "FEEDBACK", "环境反馈", "next turn"),
            node(480, 252, 240, 96, "HUB", "共享 Run State", "每轮累积", kind="dark"),
        ]
    )
    return wrap(
        slug,
        "Loop · Hermes",
        "Hermes 核心运行闭环",
        "输入沿路由、模型工具、持久化、投递和反馈循环推进，并将执行状态写回中心 Run State。",
        572,
        edges + nodes,
    )


def diagram_17_gateway_components() -> str:
    slug = "gateway-components"
    edges = stack(
        [
            connector(slug, [(480, 264), (348, 264), (348, 144), (280, 144)]),
            connector(slug, [(480, 288), (320, 288), (320, 392), (280, 392)]),
            connector(slug, [(720, 264), (852, 264), (852, 144), (920, 144)]),
            connector(slug, [(720, 288), (880, 288), (880, 392), (920, 392)]),
            connector(slug, [(600, 328), (600, 432)]),
        ]
    )
    nodes = stack(
        [
            node(480, 232, 240, 96, "GATEWAY", "GatewayRunner", "会话协调器", kind="focal"),
            node(64, 104, 216, 80, "ADAPTER", "Adapter Bus", "平台规范化"),
            node(64, 352, 216, 80, "SESSION", "Session Router", "会话定位"),
            node(920, 104, 216, 80, "LIFECYCLE", "Lifecycle", "创建 · 中断"),
            node(920, 352, 216, 80, "CALLBACK", "Event Bridge", "进度 · 审批"),
            node(480, 432, 240, 80, "DELIVERY", "Delivery Router", "出站目标"),
        ]
    )
    return wrap(
        slug,
        "Architecture · Gateway",
        "Gateway：适配、路由与生命周期协调",
        "GatewayRunner 将 Adapter Bus、Session Router、Lifecycle、Callback Bridge 和 Delivery Router 组合为多端协调层。",
        548,
        edges + nodes,
    )


def diagram_18_provider_resolution() -> str:
    slug = "provider-resolution"
    edges = stack(
        [
            connector(slug, [(288, 268), (400, 268)], style="accent"),
            connector(slug, [(680, 244), (760, 244), (760, 136), (872, 136)]),
            connector(slug, [(680, 268), (872, 268)]),
            connector(slug, [(680, 292), (760, 292), (760, 400), (872, 400)]),
        ]
    )
    nodes = stack(
        [
            node(48, 188, 240, 160, "INPUT", "配置优先级", ["1 运行时参数", "2 config · 3 env", "4 默认 / 自动识别"]),
            node(400, 212, 280, 112, "RUNTIME", "Provider Runtime", "解析 provider + model", kind="focal"),
            node(872, 96, 240, 80, "MODE", "api_mode", "chat · responses"),
            node(872, 228, 240, 80, "AUTH", "credentials", "key · token"),
            node(872, 360, 240, 80, "ENDPOINT", "endpoint", "base_url · headers"),
        ]
    )
    return wrap(
        slug,
        "Flowchart · Provider",
        "Provider 分发解析",
        "Provider Runtime 按明确优先级解析配置，并分别产出 API 模式、凭据和端点元数据。",
        496,
        edges + nodes,
    )


def diagram_19_prompt_layers() -> str:
    slug = "prompt-layers"
    body = stack(
        [
            zone(132, 40, 1036, 220, "稳定前缀 · 适合缓存"),
            zone(132, 280, 1036, 244, "易变上下文 · 每轮更新"),
            layer_band(160, 72, 960, 72, "01", "身份与行为边界", "SOUL · 系统规则", focal=True),
            layer_band(160, 152, 960, 72, "02", "工具规范", "核心 Schema · 使用约束"),
            layer_band(160, 296, 960, 64, "03", "整理记忆", "MEMORY · USER 快照"),
            layer_band(160, 368, 960, 64, "04", "Skills 索引", "name + description"),
            layer_band(160, 440, 960, 64, "05", "项目与会话上下文", "project · time · session"),
        ]
    )
    return wrap(
        slug,
        "Layer Stack · Prompt",
        "Prompt 组装：稳定前缀与易变上下文分离",
        "系统 Prompt 将身份与工具规范放入稳定前缀，把记忆、Skills、项目和会话信息放入易变上下文。",
        560,
        body,
    )


def diagram_20_tool_search() -> str:
    slug = "tool-search"
    zones = zone(264, 40, 760, 152, "Schema Discovery") + zone(264, 328, 912, 152, "Tool Execution")
    edges = stack(
        [
            connector(slug, [(240, 252), (256, 252), (256, 128), (280, 128)]),
            connector(slug, [(480, 128), (520, 128)]),
            connector(slug, [(720, 128), (760, 128)], style="link"),
            connector(slug, [(240, 308), (256, 308), (256, 400), (280, 400)]),
            connector(slug, [(480, 400), (520, 400)]),
            connector(slug, [(720, 400), (760, 400)], style="link"),
            connector(slug, [(960, 400), (1000, 400)], style="link"),
            connector(slug, [(1080, 440), (1080, 504), (140, 504), (140, 336)], style="link", dashed=True),
        ]
    )
    nodes = stack(
        [
            node(40, 224, 200, 112, "AGENT", "AIAgent / Model", "两条独立路径", kind="focal"),
            node(280, 88, 200, 80, "SEARCH", "tool_search", "按关键词发现"),
            node(520, 88, 200, 80, "DESCRIBE", "tool_describe", "按需读取 Schema"),
            node(760, 88, 240, 80, "CATALOG", "MCP / Plugin Catalog", "工具 Schema 索引", kind="store"),
            node(280, 360, 200, 80, "CALL", "tool_call", "提交调用参数"),
            node(520, 360, 200, 80, "REGISTRY", "Tool Registry", "解析并分发"),
            node(760, 360, 200, 80, "EXTERNAL", "External Tool", "执行真实副作用"),
            node(1000, 360, 160, 80, "RESULT", "Tool Result", "返回模型上下文", kind="store"),
        ]
    )
    return wrap(
        slug,
        "Process · Tools",
        "Tool Search：Schema 发现与工具执行分流",
        "AIAgent 一条路径通过 search、describe 查询 Catalog Schema，另一条路径经 tool_call、Registry 与外部工具执行，并把 Tool Result 返回模型。",
        560,
        zones + edges + nodes,
    )


def diagram_21_subagent_delegation() -> str:
    slug = "subagent-delegation"
    edges = stack(
        [
            connector(slug, [(600, 136), (600, 188)], style="accent", arrow=False),
            bus(180, 1020, 188),
            connector(slug, [(180, 188), (180, 232)]),
            connector(slug, [(600, 188), (600, 232)]),
            connector(slug, [(1020, 188), (1020, 232)]),
            connector(slug, [(180, 320), (180, 368), (520, 368), (520, 420)]),
            connector(slug, [(600, 320), (600, 420)]),
            connector(slug, [(1020, 320), (1020, 368), (680, 368), (680, 420)]),
        ]
    )
    nodes = stack(
        [
            node(480, 48, 240, 88, "PARENT", "Parent Agent", "goal + bounded context", kind="focal"),
            node(60, 232, 240, 88, "WORKER", "研究文档", "独立 Context"),
            node(480, 232, 240, 88, "WORKER", "检查代码", "独立 Terminal"),
            node(900, 232, 240, 88, "WORKER", "运行测试", "收窄工具权限"),
            node(480, 420, 240, 88, "MERGE", "Summary Merge", "只回传最终摘要", kind="store"),
        ]
    )
    return wrap(
        slug,
        "Tree · Delegation",
        "子 Agent 委派：隔离执行，摘要回传",
        "Parent Agent 将目标分发给三个隔离 Worker，并仅把各自最终摘要汇入父上下文。",
        552,
        edges + nodes,
    )


def diagram_22_cron_tick() -> str:
    slug = "cron-tick"
    edges = stack(
        [
            connector(slug, [(240, 264), (280, 264)]),
            connector(slug, [(464, 264), (504, 264)]),
            connector(slug, [(704, 264), (744, 264)]),
            connector(slug, [(928, 264), (968, 264)]),
        ]
    )
    nodes = stack(
        [
            stage_header(48, 88, "1", "触发"),
            stage_header(280, 88, "2", "装载"),
            stage_header(504, 88, "3", "执行"),
            stage_header(744, 88, "4", "投递"),
            stage_header(968, 88, "5", "提交"),
            node(48, 200, 192, 128, "TICK", "Tick + 文件锁", ["防重复触发", "跨进程互斥"]),
            node(280, 200, 184, 128, "JOB", "加载 Job", ["Prompt · Schedule", "Skills · Target"]),
            node(504, 200, 200, 128, "AGENT", "Fresh AIAgent", ["新 Session", "禁用 cronjob"], kind="focal"),
            node(744, 200, 184, 128, "DELIVER", "投递结果", ["目标独立", "不污染聊天"]),
            node(968, 200, 184, 128, "STATE", "原子更新", ["status", "next_run"], kind="store"),
        ]
    )
    return wrap(
        slug,
        "Process · Cron",
        "Cron 调度的是一次完整 Agent Run",
        "Cron 触发后先加锁并加载任务，再创建新 AIAgent、投递结果并原子更新下一次运行状态。",
        408,
        edges + nodes,
    )


def diagram_23_observability_run() -> str:
    slug = "observability-run"
    zones = zone(32, 196, 704, 264, "Hermes 当前记录") + zone(760, 196, 408, 264, "成熟系统扩展")
    edges = stack(
        [
            connector(slug, [(560, 132), (560, 168), (384, 168), (384, 232)], arrow=False),
            connector(slug, [(640, 132), (640, 168), (972, 168), (972, 232)], arrow=False),
            bus(152, 616, 232),
            bus(872, 1072, 232),
            connector(slug, [(152, 232), (152, 268)]),
            connector(slug, [(384, 232), (384, 268)]),
            connector(slug, [(616, 232), (616, 268)]),
            connector(slug, [(872, 232), (872, 268)], dashed=True),
            connector(slug, [(1072, 232), (1072, 268)], dashed=True),
        ]
    )
    nodes = stack(
        [
            node(440, 48, 320, 84, "RUN", "Agent Run", "当前记录 + 扩展建议", kind="focal"),
            node(48, 268, 208, 144, "CURRENT", "Session / Message", "会话 · 消息"),
            node(280, 268, 208, 144, "CURRENT", "Tool Call / Error", "调用 · 结果 · 错误"),
            node(512, 268, 208, 144, "CURRENT", "Usage / Lineage", ["Token · Cache", "Provider · Cost", "父子 Session 血缘"]),
            node(784, 268, 176, 144, "EXT", "Control Spans", ["Approval · Retry", "Compression"], kind="optional"),
            node(984, 268, 176, 144, "EXT", "Trace Fidelity", ["Trace / Span", "hash / replay"], kind="optional"),
        ]
    )
    return wrap(
        slug,
        "Tree · Observability",
        "Run 是 Agent 可观测性的根对象",
        "Hermes 当前记录会话、消息、工具错误、用量成本与父子血缘；更细的控制 Span 和可重放标识属于成熟系统扩展。",
        500,
        zones + edges + nodes,
    )


def diagram_24_security_sandbox() -> str:
    slug = "security-sandbox"
    zones = zone(32, 48, 532, 436, "Terminal-only Isolation") + zone(588, 48, 580, 436, "Whole-process Sandbox")
    edges = stack(
        [
            connector(slug, [(160, 164), (160, 236)]),
            connector(slug, [(284, 304), (380, 304)]),
            connector(slug, [(720, 164), (720, 236)]),
            connector(slug, [(844, 304), (940, 304)]),
        ]
    )
    nodes = stack(
        [
            node(72, 96, 176, 68, "INPUT", "不可信输入", "web · mail · MCP", kind="external"),
            node(72, 236, 212, 136, "HOST", "Hermes Host", ["凭据 · Plugin", "MCP · Code Exec"]),
            node(380, 256, 152, 96, "DOCKER", "Terminal", "仅命令隔离", kind="optional"),
            node(632, 96, 176, 68, "INPUT", "不可信输入", "same threat", kind="external"),
            node(632, 236, 212, 136, "SANDBOX", "Hermes 进程树", ["Agent · MCP", "Plugin · Terminal"], kind="focal"),
            node(940, 256, 196, 96, "BOUNDARY", "OS 隔离边界", "Container / VM", kind="security"),
        ]
    )
    notes = caption(296, 404, "宿主扩展仍暴露") + caption(884, 404, "完整进程树受限")
    return wrap(
        slug,
        "Architecture · Security",
        "Terminal 隔离不等于整个 Agent 隔离",
        "只隔离 Terminal 仍让 MCP、Plugin 和凭据留在宿主；更强边界是隔离完整 Hermes 进程树。",
        528,
        zones + edges + nodes + notes,
    )


def diagram_25_skills_disclosure() -> str:
    slug = "skills-disclosure"
    edges = stack(
        [
            connector(slug, [(240, 268), (320, 268)]),
            connector(slug, [(380, 208), (380, 136), (560, 136)]),
            connector(slug, [(380, 328), (380, 380)]),
            connector(slug, [(760, 136), (840, 136)]),
            connector(slug, [(960, 176), (960, 320)]),
        ]
    )
    labels = arrow_label(500, 128, "相关") + arrow_label(388, 352, "不相关", anchor="start")
    nodes = stack(
        [
            node(40, 220, 200, 96, "INDEX", "Skills 索引", "name + description"),
            diamond(380, 268, 120, 120, "任务相关？"),
            node(560, 96, 200, 80, "VIEW", "skill_view", "加载完整 SKILL.md", kind="focal"),
            node(840, 96, 240, 80, "APPLY", "按 Skill 执行", "程序性上下文"),
            node(280, 380, 200, 80, "END", "跳过加载", "保持上下文精简"),
            node(840, 320, 240, 96, "MAINTAIN", "skill_manage", ["完成后沉淀", "创建 · Patch · 归档"], kind="store"),
        ]
    )
    return wrap(
        slug,
        "Flowchart · Skills",
        "Skills 渐进式披露",
        "系统 Prompt 只暴露 Skills 索引，模型判断相关后才读取完整内容，并可在执行后管理 Skill。",
        480,
        edges + labels + nodes,
    )


def diagram_26_protocol_interop() -> str:
    slug = "protocol-interop"
    edges = stack(
        [
            connector(slug, [(480, 252), (360, 252), (360, 136), (288, 136)], style="link"),
            connector(slug, [(480, 300), (360, 300), (360, 420), (288, 420)], style="link"),
            connector(slug, [(720, 252), (840, 252), (840, 136), (912, 136)], style="link"),
            connector(slug, [(720, 300), (840, 300), (840, 420), (912, 420)], style="link", dashed=True),
        ]
    )
    labels = stack(
        [
            arrow_label(368, 220, "ACP", anchor="start"),
            arrow_label(368, 388, "HTTP / SSE", anchor="start"),
            arrow_label(832, 220, "MCP", anchor="end"),
            arrow_label(832, 388, "A2A · 演进方向", anchor="end"),
        ]
    )
    nodes = stack(
        [
            node(480, 220, 240, 112, "CORE", "AIAgent Runtime", "统一内部 API", kind="focal"),
            node(48, 96, 240, 80, "IDE", "IDE / Editor", "驱动 Agent", kind="external"),
            node(48, 380, 240, 80, "APP", "Web / CI / SDK", "嵌入服务", kind="external"),
            node(912, 96, 240, 80, "TOOL", "Tool / Resource", "外部能力", kind="external"),
            node(912, 380, 240, 80, "FUTURE", "Remote Agent", "未来任务与 Artifact", kind="optional"),
        ]
    )
    return wrap(
        slug,
        "Architecture · Protocols",
        "协议互操作全景",
        "当前 AIAgent Runtime 通过 ACP、HTTP/SSE 和 MCP 连接 IDE、应用与工具；A2A 连接远程 Agent 属演进方向。",
        520,
        edges + labels + nodes,
    )


def diagram_27_final_loop() -> str:
    slug = "final-loop"
    edges = stack(
        [
            connector(slug, [(280, 112), (360, 112)]),
            connector(slug, [(560, 112), (640, 112)]),
            connector(slug, [(840, 112), (1000, 112), (1000, 196)]),
            connector(slug, [(1000, 276), (1000, 340)]),
            connector(slug, [(880, 368), (800, 368), (800, 380), (720, 380)]),
            connector(slug, [(480, 380), (320, 380)]),
            connector(slug, [(80, 380), (40, 380), (40, 112), (80, 112)], style="accent"),
            connector(slug, [(960, 340), (960, 316), (760, 316), (760, 268), (720, 268)], dashed=True),
            connector(slug, [(600, 340), (600, 300)], dashed=True),
        ]
    )
    nodes = stack(
        [
            node(80, 72, 200, 80, "INPUT", "多端输入", "CLI · IM · IDE"),
            node(360, 72, 200, 80, "SESSION", "会话路由", "identity · task"),
            node(640, 72, 200, 80, "CONTEXT", "Prompt / Context", "memory · skills"),
            node(880, 196, 240, 80, "MODEL", "Provider / 模型", "下一步决策", kind="focal"),
            node(880, 340, 240, 80, "TOOL", "Tool / MCP", "执行与结果"),
            node(480, 340, 240, 80, "STATE", "压缩 / 持久化", "session · memory · trajectory", kind="store"),
            node(80, 340, 240, 80, "OUTPUT", "多端输出", "delivery target"),
            node(480, 220, 240, 80, "HUB", "Session / Memory", "trajectory · approval", kind="dark"),
        ]
    )
    return wrap(
        slug,
        "Loop · Hermes",
        "Hermes Agent Runtime 核心闭环",
        "多端输入经会话、上下文、模型和工具推进，结果写入 Session、Memory 与轨迹并投递，再由新反馈启动下一轮。",
        472,
        edges + nodes,
    )


DIAGRAMS = [
    ("01-runtime-stack.html", diagram_01_runtime_stack),
    ("02-overall-architecture.html", diagram_02_overall_architecture),
    ("03-gateway-bus.html", diagram_03_gateway_bus),
    ("04-two-level-guards.html", diagram_04_two_level_guards),
    ("05-delivery-router.html", diagram_05_delivery_router),
    ("06-callback-bus.html", diagram_06_callback_bus),
    ("07-run-conversation.html", diagram_07_run_conversation),
    ("08-canonical-model.html", diagram_08_canonical_model),
    ("09-tool-dispatch.html", diagram_09_tool_dispatch),
    ("10-dual-compression.html", diagram_10_dual_compression),
    ("11-compression-phases.html", diagram_11_compression_phases),
    ("12-mcp-architecture.html", diagram_12_mcp_architecture),
    ("13-protocol-compare.html", diagram_13_protocol_compare),
    ("14-memory-layers.html", diagram_14_memory_layers),
    ("15-module-boundaries.html", diagram_15_module_boundaries),
    ("16-summary-loop.html", diagram_16_summary_loop),
    ("17-gateway-components.html", diagram_17_gateway_components),
    ("18-provider-resolution.html", diagram_18_provider_resolution),
    ("19-prompt-layers.html", diagram_19_prompt_layers),
    ("20-tool-search.html", diagram_20_tool_search),
    ("21-subagent-delegation.html", diagram_21_subagent_delegation),
    ("22-cron-tick.html", diagram_22_cron_tick),
    ("23-observability-run.html", diagram_23_observability_run),
    ("24-security-sandbox.html", diagram_24_security_sandbox),
    ("25-skills-disclosure.html", diagram_25_skills_disclosure),
    ("26-protocol-interop.html", diagram_26_protocol_interop),
    ("27-final-loop.html", diagram_27_final_loop),
]


def main() -> None:
    for filename, factory in DIAGRAMS:
        path = OUT / filename
        path.write_text(factory(), encoding="utf-8")
        print(f"written {path.name}")


if __name__ == "__main__":
    main()
