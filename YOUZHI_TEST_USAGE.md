# 游资涨停专题问题集测试脚本使用说明

## 概述

本项目包含了完整的游资涨停专题问题集测试框架，用于评估AI智能体在游资涨停分析方面的能力。

## 测试脚本说明

### 1. 综合测试脚本 (`test_youzhi_zhangting_comprehensive.py`)

**功能特点：**
- 自动化测试所有303个问题
- LLM自主工具选择（不参考预期工具）
- 多轮对话支持（处理5步工具调用链）
- 智能评估和详细报告
- 性能监控和错误处理

**使用方法：**
```bash
# 测试所有问题
python test_youzhi_zhangting_comprehensive.py

# 限制测试问题数量
python test_youzhi_zhangting_comprehensive.py --max 10

# 过滤特定类型问题
python test_youzhi_zhangting_comprehensive.py --filter single  # 单轮问题
python test_youzhi_zhangting_comprehensive.py --filter multi   # 多轮问题
python test_youzhi_zhangting_comprehensive.py --filter basic   # 初级问题
python test_youzhi_zhangting_comprehensive.py --filter advanced # 高级问题

# 指定CSV文件路径
python test_youzhi_zhangting_comprehensive.py --csv path/to/your/csv
```

### 2. 模拟测试脚本 (`test_youzhi_mock.py`)

**功能特点：**
- 完全离线运行，无需API调用
- 智能模拟响应生成
- 快速验证测试框架功能
- 适合开发和调试

**使用方法：**
```bash
# 默认测试10个问题
python test_youzhi_mock.py

# 指定测试问题数量
python test_youzhi_mock.py --max 20

# 指定CSV文件
python test_youzhi_mock.py --csv archived_data/游资涨停专题问题集.csv --max 15
```

### 3. 简化测试脚本 (`test_youzhi_simple_run.py`)

**功能特点：**
- 轻量级测试框架
- 支持真实LLM调用和模拟模式
- 适合快速验证基础功能

**使用方法：**
```bash
# 设置环境变量（可选）
export OPENAI_API_KEY="your-api-key"
export OPENAI_MODEL="gpt-4"

# 运行测试
python test_youzhi_simple_run.py
```

## 环境配置

### 必需依赖

```bash
# 使用uv安装依赖
uv add langchain-openai langchain-core psutil

# 或使用pip
pip install -r requirements.txt
```

### 环境变量设置

```bash
# OpenAI配置（可选，不设置则使用模拟模式）
export OPENAI_API_KEY="your-openai-api-key"
export OPENAI_MODEL="gpt-4"  # 或其他模型
export OPENAI_BASE_URL="https://api.openai.com/v1"  # 自定义API端点

# MCP服务器配置（可选）
export MCP_SERVER_URL="http://localhost:8000"
```

## 问题集格式

CSV文件包含以下字段：
- `问题ID`: 唯一标识符
- `问题内容`: 具体问题描述
- `预期工具调用`: 期望的工具调用方式
- `难度等级`: 初级/中级/高级
- `应用场景`: 问题的应用场景
- `问题特性`: 具体明确/通用宽泛

## 测试报告

### 报告文件

测试完成后会在 `test_reports/` 目录下生成：

1. **详细JSON报告**: `*_test_*.json`
   - 包含所有测试结果的详细数据
   - 适合程序化分析

2. **简化文本报告**: `*_summary_*.txt`
   - 人类可读的摘要报告
   - 包含统计信息和分析

### 评估指标

- **成功率**: 测试通过的问题比例
- **响应时间**: 平均响应时间
- **综合得分**: 基于多维度评估的综合分数
  - 相关性得分 (0-100)
  - 完整性得分 (0-100)
  - 工具选择得分 (0-100)
  - 专业性得分 (0-100)

### 按难度统计

- 初级问题成功率
- 中级问题成功率
- 高级问题成功率

## 故障排除

### 常见问题

1. **CSV文件不存在**
   ```
   ❌ CSV文件不存在: archived_data/游资涨停专题问题集.csv
   ```
   **解决**: 确保CSV文件在正确位置，或使用 `--csv` 参数指定路径

2. **API Key错误**
   ```
   Error code: 401 - Incorrect API key provided
   ```
   **解决**: 设置正确的 `OPENAI_API_KEY` 环境变量，或使用模拟模式

3. **导入模块失败**
   ```
   ❌ 无法导入agent模块，请检查路径配置
   ```
   **解决**: 这是正常的，脚本会自动使用模拟配置

### 模拟模式

如果没有设置API Key或不想进行真实调用，所有脚本都支持模拟模式：
- 自动检测API Key是否可用
- 生成智能模拟响应
- 保持完整的测试流程

## 扩展和定制

### 添加新的评估指标

在 `evaluate_response` 方法中添加新的评估维度：

```python
def evaluate_response(self, question, response, tool_calls):
    evaluation = {
        'custom_score': self.calculate_custom_score(response),
        # ... 其他指标
    }
    return evaluation
```

### 自定义工具调用检测

修改 `extract_tool_calls` 方法来识别新的工具模式：

```python
def extract_tool_calls(self, response):
    # 添加新的工具名称模式
    tool_patterns = [
        'your_custom_tool',
        # ... 现有工具
    ]
    # ... 处理逻辑
```

### 自定义问题过滤

添加新的过滤选项：

```python
if question_filter == 'your_filter':
    questions = [q for q in questions if your_condition(q)]
```

## 最佳实践

1. **开发阶段**: 使用模拟测试脚本快速验证功能
2. **集成测试**: 使用综合测试脚本进行完整评估
3. **性能调优**: 通过限制问题数量进行迭代测试
4. **生产验证**: 使用真实API进行最终验证

## 联系和支持

如有问题或建议，请查看项目文档或提交Issue。 