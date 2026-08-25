# Hermes 文章图示重绘设计

## 目标

重绘 `hermes-agent-kernel-architecture-and-development-guide.md` 引用的全部图示，使其适合技术文章内嵌阅读：文字清楚、关系可追踪、构图紧凑，并保持 diagram-design 的可访问性与连接器规范。

## 设计原则

- 使用 `doc-wide` 画布，SVG 逻辑宽度 1200px，PNG 以 2× 导出。
- 节点正文使用 16px，技术副标题使用 12px；不依赖读者放大图片。
- 每张图只表达一个核心结论，默认不显示图例。
- 架构关系使用正交连接线；同一边多个连接点必须分散。
- 过程图使用阶段分组、编号和主循环，不再使用整页等宽列表。
- 超过 9 个概念时，合并为阶段或区域，而不是堆叠更多节点。
- 每张图最多两个珊瑚色焦点，其余依靠层级、区域和线型表达。

## 图型分组

1. **架构图**：总体架构、Gateway、Canonical Model、MCP、子 Agent、安全边界。
2. **流程图 / Process**：消息守卫、运行链、工具调用、压缩、Cron、Skills。
3. **层级图 / Layer stack**：Runtime 能力、Prompt、Memory、模块边界、协议层。
4. **循环 / Tree**：核心闭环、Run 可观测结构。

## 交付物

- 重写 `hermes-agent-kernel-diagrams/generate_diagrams.py`。
- 重新生成文章引用的 HTML 与 PNG。
- 保持 Markdown 图片路径不变，避免修改正文结构。
- 使用 `self_check.py` 检查全部 HTML。
- 逐张读取 PNG 进行视觉抽查，重点检查断线、重叠、文字尺寸和留白。

## 验收标准

- 文章中不存在断裂或悬空的关系线。
- 图片在 1000px 左右显示宽度下仍可直接阅读节点文字。
- 无无意义图例、无大面积空白、无连续十个相同框的图。
- 内容与正文原始语义一致，不引入新的实现断言。
- 全部 HTML 通过 diagram-design 自检，全部 PNG 可正常解码。
