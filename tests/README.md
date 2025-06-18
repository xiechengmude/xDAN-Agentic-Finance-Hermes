# 多轮智能体测试套件

本目录包含用于测试和评估xDAN多轮智能体性能的脚本。

## 文件说明

- `test_multi_turn_agent.py` - 多轮智能体测试脚本
- `evaluate_test_results.py` - 测试结果统计评估脚本
- `test_results/` - 测试结果存储目录
- `analysis_reports/` - 分析报告存储目录

## 使用方法

### 1. 环境准备

首先确保已安装所需依赖：

```bash
pip install pandas matplotlib seaborn langfuse
```

### 2. 配置Langfuse（可选）

在`.env`文件中配置Langfuse参数：

```env
# Langfuse配置
LANGFUSE_PUBLIC_KEY=your_public_key_here
LANGFUSE_SECRET_KEY=your_secret_key_here
LANGFUSE_HOST=https://cloud.langfuse.com
```

如果不配置Langfuse，测试仍可正常运行，但不会有观测数据。

### 3. 运行测试

```bash
# 运行多轮智能体测试
python tests/test_multi_turn_agent.py

# 可以通过修改代码中的参数来控制测试数量
# max_cases=5  # 测试前5个用例
```

### 4. 分析结果

测试完成后，运行评估脚本：

```bash
# 分析最新的测试结果
python tests/evaluate_test_results.py
```

## 测试指标

### 核心指标

1. **成功率** - 测试用例的通过率
2. **工具覆盖率** - 实际使用的工具与预期工具的匹配度
3. **执行时间** - 每个测试用例的执行时间
4. **轮数准确性** - 实际执行轮数是否在预期范围内

### 成功判定标准

测试用例被判定为成功需要满足：
- 执行没有出错
- 工具覆盖率 >= 50%
- 执行轮数在预期范围内

## 测试数据格式

测试使用CSV格式的问题集，包含以下字段：
- 问题编号
- 问题类别
- 具体问题
- 涉及工具（逗号分隔）
- 预期轮数（如"3-4"表示3到4轮）
- 难度等级
- 应用场景

## 输出文件

### 测试结果

保存在 `test_results/multi_turn_test_results_YYYYMMDD_HHMMSS.json`

包含每个测试用例的详细信息：
- 测试ID和问题
- 成功状态
- 实际使用的工具列表
- 执行时间
- 错误信息（如果有）
- Langfuse追踪ID（如果启用）

### 分析报告

保存在 `test_results/analysis_reports/analysis_report_YYYYMMDD_HHMMSS/`

包含：
- `detailed_report.md` - 详细的文本报告
- `tool_usage_analysis.png` - 工具使用分析图表
- `performance_analysis.png` - 性能分析图表

## Langfuse集成

如果配置了Langfuse，可以在Langfuse平台查看：
- 每个测试用例的完整执行追踪
- 工具调用的详细信息
- LLM生成的输入输出
- 性能指标和错误信息

## 常见问题

### Q: 测试失败率很高怎么办？

检查：
1. MCP服务器是否正常运行
2. 模型服务是否可用
3. 网络连接是否稳定

### Q: 如何调整测试参数？

在 `test_multi_turn_agent.py` 中可以调整：
- `max_cases` - 测试用例数量
- `asyncio.sleep(2)` - 测试间隔时间
- 成功判定的阈值（如工具覆盖率）

### Q: 如何添加新的测试用例？

直接编辑CSV文件，按照格式添加新的测试用例即可。

## 扩展开发

### 添加新的评估指标

在 `evaluate_test_results.py` 中的 `generate_report` 方法中添加新的分析函数。

### 自定义测试流程

继承 `MultiTurnAgentTester` 类并重写相关方法。

### 集成到CI/CD

可以在CI/CD流程中运行测试脚本，并根据成功率决定是否通过。