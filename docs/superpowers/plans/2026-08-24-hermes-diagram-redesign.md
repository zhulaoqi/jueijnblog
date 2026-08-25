# Hermes Diagram Redesign Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 Hermes 长文引用的全部图示重绘为适合文章内嵌阅读的高质量 HTML/SVG 与 PNG。

**Architecture:** 使用一个声明式 Python 生成器提供画布、节点、区域、正交连接线和文本原语；每张图使用独立构图函数，不再复用单一“框列表”模板。生成 HTML 后通过本地 Chrome 截取 SVG，并保持 Markdown 路径不变。

**Tech Stack:** Python 3、内联 HTML/SVG/CSS、diagram-design `self_check.py`、本地 Google Chrome headless。

---

## Chunk 1: 生成系统与核心图

### Task 1: 重建绘图原语

**Files:**
- Modify: `hermes-agent-kernel-diagrams/generate_diagrams.py`

- [ ] 将默认画布改为 1200px `doc-wide`。
- [ ] 提供 16px 节点、12px副标题、区域标题、阶段卡片和正交路径原语。
- [ ] 删除全局默认图例，只有颜色语义不能从图中直接理解时才添加。
- [ ] 为连接器提供独立端口和标签遮罩。

### Task 2: 重绘架构类图

**Files:**
- Modify: `hermes-agent-kernel-diagrams/generate_diagrams.py`

- [ ] 重绘总体架构、Gateway 总线、Canonical Model、MCP。
- [ ] 重绘 Delivery、Callback、Provider、Tool Search。
- [ ] 检查 fan-in/fan-out 端口、线条连续性和区域层级。

## Chunk 2: 流程、层级与循环图

### Task 3: 重绘流程类图

**Files:**
- Modify: `hermes-agent-kernel-diagrams/generate_diagrams.py`

- [ ] 将 `run_conversation` 合并为四个阶段，而不是十个相同框。
- [ ] 重绘消息守卫、工具调用、双层压缩、四阶段压缩、Skills、Cron。
- [ ] 明确分支、回路、正常路径和安全网。

### Task 4: 重绘层级与总结类图

**Files:**
- Modify: `hermes-agent-kernel-diagrams/generate_diagrams.py`

- [ ] 重绘 Runtime 能力、Prompt、Memory、模块边界、协议互操作。
- [ ] 重绘子 Agent、可观测树、安全边界和最终闭环。
- [ ] 合并重复语义，控制每图节点和箭头预算。

## Chunk 3: 导出与质量门禁

### Task 5: 生成并验证 HTML

**Files:**
- Regenerate: `hermes-agent-kernel-diagrams/*.html`

- [ ] 运行生成器，确认目标文件全部生成。
- [ ] 对每个 HTML 运行 diagram-design `self_check.py`。
- [ ] 搜索对角线、缺失标题与重复裸 ID。

### Task 6: 导出 PNG 并视觉抽查

**Files:**
- Modify: `hermes-agent-kernel-diagrams/export_png.py`
- Regenerate: `hermes-agent-kernel-diagrams/*.png`

- [ ] 使用本地 Chrome 以 2× 截取 SVG。
- [ ] 核对图片数量、尺寸和解码结果。
- [ ] 逐图检查至少架构、流程、层级、循环各两张。
- [ ] 确认 Markdown 中全部图片路径有效。
