#!/usr/bin/env python3
"""Replace ```text diagram blocks in Hermes guide with diagram links or code blocks."""
import re
from pathlib import Path

MD = Path(__file__).parent.parent / "hermes-agent-kernel-architecture-and-development-guide.md"
DIAG = "./hermes-agent-kernel-diagrams"

# Sequential replacements for each ```text block in the document.
REPLACEMENTS = [
    # §0
    ("figure", "01-runtime-stack.html", "Agent Runtime 能力叠加"),
    # §1
    ("figure", "02-overall-architecture.html", "一个内核，多个入口"),
    # §2.1
    ("figure", "17-gateway-components.html", "Gateway 组成模块"),
    # §2.2
    ("figure", "03-gateway-bus.html", "入站 MessageEvent 规范化"),
    # §2.3 session key
    ("code", "agent:main:{platform}:{chat_type}:{chat_id}"),
    ("code", "agent:main:telegram:private:123456789"),
    # §2.4
    ("figure", "04-two-level-guards.html", "两级消息守卫"),
    # §2.5
    ("figure", "05-delivery-router.html", "出站投递总线"),
    # §2.6
    ("figure", "06-callback-bus.html", "AIAgent 回调事件总线"),
    # §3.2
    ("figure", "07-run-conversation.html", "run_conversation 单轮分发链"),
    # §3.3 canonical
    ("figure", "08-canonical-model.html", "Canonical Model 规范内部模型"),
    # §3.4
    ("figure", "18-provider-resolution.html", "Provider 分发解析"),
    # §3.5
    ("figure", "09-tool-dispatch.html", "工具调用分发链"),
    # §4.1
    ("figure", "19-prompt-layers.html", "Prompt 组装顺序"),
    # context priority
    ("code", ".hermes.md / HERMES.md\n  > AGENTS.md\n  > CLAUDE.md\n  > .cursorrules / .cursor/rules"),
    # frozen snapshot
    ("quote", "稳定前缀冻结 · 动态召回按需加载 · 摘要与原文并存"),
    # §5.2
    ("figure", "10-dual-compression.html", "双层上下文压缩"),
    # placeholder
    ("code", "[Old tool output cleared to save context space]"),
    # boundaries
    ("code", "[头部固定区] [中间摘要区] [尾部逐字保留区]"),
    # summary template
    ("code", "Goal\nConstraints & Preferences\nProgress (Done / In Progress / Blocked)\nKey Decisions\nRelevant Files\nNext Steps\nCritical Context"),
    # iterative
    ("code", "旧摘要 + 新的中间历史 → 新摘要"),
    # cache breakpoints - §5.7
    ("code", "系统 Prompt · 工具定义 · MEMORY 块 · 历史前缀（最多 4 个 Anthropic 缓存断点）"),
    # §6.1 tool four parts
    ("code", "name · description · input_schema · handler"),
    # schema path - duplicate of tool dispatch
    ("figure", "09-tool-dispatch.html", "模型只看 Schema，运行时执行 handler"),
    # §6.8
    ("figure", "20-tool-search.html", "Tool Search 渐进式披露"),
    # §7.1
    ("figure", "12-mcp-architecture.html", "MCP 三方角色"),
    # §7.2 primitives
    ("code", "Tools（可调用） · Resources（可读取） · Prompts（可复用模板）"),
    # §7.4 registration
    ("code", "mcp_servers 配置 → MCP Session → tools/list → 过滤 → 前缀 → ToolRegistry"),
    ("code", "mcp_<server_name>_<tool_name>"),
    ("code", "mcp_github_create_issue"),
    # §7.5
    ("code", "notifications/tools/list_changed → 重新 tools/list → 更新 Registry"),
    # §7.7 sampling
    ("code", "MCP Server ── sampling/createMessage ──> Hermes Client ──> 模型 ──> 返回"),
    # §7.9
    ("figure", "13-protocol-compare.html", "MCP · ACP · A2A 区分"),
    # §8.1
    ("code", "传统：IDE 嵌入 Agent 逻辑\nACP：IDE 通过 JSON-RPC 驱动独立 Agent 进程"),
    ("code", "session/new → prompt → session/update（流式）→ 完成"),
    # §8.2 bridge
    ("code", "ACP 异步 JSON-RPC ↔ AIAgent 同步编排（桥接层排队/回调）"),
    # §9.3
    ("code", "~/.hermes/state.db"),
    ("code", "sessions · messages · messages_fts · messages_fts_trigram · state_meta · schema_version"),
    # §9.4
    ("code", "事实记忆：用户用 PostgreSQL\n程序性记忆：如何安全迁移这套 PostgreSQL"),
    ("figure", "25-skills-disclosure.html", "Skills 渐进式披露"),
    # §9.5
    ("figure", "14-memory-layers.html", "记忆与技能分层"),
    # §10
    ("figure", "21-subagent-delegation.html", "子 Agent 委派"),
    # §11
    ("figure", "22-cron-tick.html", "Cron 触发流程"),
    # §12
    ("code", "Agent 的命令 = 当前操作系统用户的权限"),
    ("figure", "24-security-sandbox.html", "安全隔离边界"),
    # §13
    ("figure", "23-observability-run.html", "Run 可观测结构"),
    # §14.3
    ("code", "Hermes：模型决定下一步，流程灵活\nLangGraph：图定义状态转移，流程可控"),
    # §16.1 split list
    ("code", "AgentRuntime\nRunStateMachine\nContextManager\nToolExecutor\nProviderRouter\nSessionRepository\nEventBus\nPolicyEngine"),
    # §17 directory / module boundaries
    ("figure_code", "15-module-boundaries.html", "自研 Agent 内核模块边界",
     "agent_runtime/\n├── runtime.py          # Run 状态机\n├── events.py           # 统一事件协议\n├── messages.py         # Canonical Message\n├── providers/\n├── context/\n├── tools/\n├── state/\n├── agents/\n├── protocols/\n└── observability/"),
    # §19.6
    ("figure", "26-protocol-interop.html", "协议互操作全景"),
    # §20
    ("figure", "27-final-loop.html", "Hermes 核心闭环"),
]


def render(kind: str, arg1: str, title: str = "") -> str:
    if kind == "figure":
        path, title = arg1, title or arg1
        return (
            f"> **图：{title}**  \n"
            f"> [查看交互式架构图]({DIAG}/{path})"
        )
    if kind == "code":
        return f"```\n{arg1}\n```"
    if kind == "quote":
        return f"> {arg1}"
    raise ValueError(kind)


def main():
    text = MD.read_text(encoding="utf-8")
    parts = re.split(r"```text\n", text)
    if len(parts) - 1 != len(REPLACEMENTS):
        raise SystemExit(
            f"Block count mismatch: found {len(parts)-1} text blocks, "
            f"have {len(REPLACEMENTS)} replacements"
        )
    out = [parts[0]]
    for i, block_tail in enumerate(parts[1:]):
        content, rest = block_tail.split("```", 1)
        repl = REPLACEMENTS[i]
        if repl[0] == "figure":
            new = render("figure", repl[1], repl[2])
        elif repl[0] == "code":
            new = render("code", repl[1])
        elif repl[0] == "quote":
            new = render("quote", repl[1])
        elif repl[0] == "figure_code":
            new = (
                f"> **图：{repl[2]}**  \n"
                f"> [查看交互式架构图]({DIAG}/{repl[1]})\n\n"
                f"```\n{repl[3]}\n```"
            )
        else:
            raise ValueError(repl)
        out.append(new + rest)
    MD.write_text("".join(out), encoding="utf-8")
    print(f"Updated {MD} — replaced {len(REPLACEMENTS)} text blocks")


if __name__ == "__main__":
    main()
