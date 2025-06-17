
  🏗️ 核心架构分布

  1. 双重API架构

  - 标准适配器API (api/fastapi_app.py) - 基于现有xDAN后端的LangGraph兼容层
  - 原生LangGraph API (api/fastapi_app_langgraph_native.py) - 使用官方LangGraph和MCP SDK的全新实现

  2. 智能工具选择系统 (intelligent_tool_selector/)

  - 单轮选择器 - 基于LLM的智能工具选择
  - 多轮选择器 - 复杂查询的任务规划和分解
  - 并行执行器 - 基于依赖分析的并行优化，性能提升40-60%

  3. 适配器层 (adapters/)

  - xDAN适配器 - 将现有后端转换为LangGraph事件流
  - 原生MCP适配器 - 纯LangGraph实现
  - 事件映射器 - 格式转换和事件处理

  4. MCP工具生态

  - 138+金融工具 - 覆盖股票、基金、宏观经济数据
  - 智能参数映射 - 自动参数推断和验证
  - 工具管理器 - MCP客户端连接和工具缓存

  🔄 数据流架构

  用户查询 → FastAPI → 适配器 → 多轮选择器 → MCP工具 → 结果整合 → 前端

  🎯 架构优势

  - 灵活性 - 双架构支持不同场景需求
  - 智能化 - LLM驱动的任务规划和工具选择
  - 高性能 - 并行执行和依赖优化
  - 生产就绪 - 完整的Docker部署和健康监控

  这个架构设计允许项目既保持向后兼容，又能利用最新的LangGraph特性，是一个非常成熟的企业级智能代理系统。
