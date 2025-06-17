# 游资涨停专题问题集测试指南

## 概述

这是一个专门为游资涨停专题问题集设计的完整测试脚本，能够：

1. **自动化测试所有303个问题**
2. **LLM自主工具选择**（不依赖预期工具调用）
3. **多轮对话支持**（处理复杂的5步工具调用链）
4. **智能评估和详细报告**
5. **性能监控和错误处理**

## 文件说明

### 核心文件

- `test_youzhi_zhangting_comprehensive.py` - 主测试脚本
- `run_youzhi_test.py` - 快速启动脚本
- `YOUZHI_ZHANGTING_TEST_GUIDE.md` - 使用指南（本文件）

### 输出文件

- `test_logs/` - 测试日志目录
- `test_reports/` - 测试报告目录

## 快速开始

### 1. 环境检查

确保已安装必要的依赖：

```bash
# 检查Python环境
python --version  # 需要Python 3.11+

# 检查依赖包
pip list | grep -E "(langchain|openai|asyncio)"
```

### 2. 文件准备

确保游资涨停专题问题集CSV文件在正确位置：

```
langraph-stack/backend/
├── archived_data/
│   └── 游资涨停专题问题集.csv  # 确保这个文件存在
├── test_youzhi_zhangting_comprehensive.py
└── run_youzhi_test.py
```

### 3. 快速测试

使用快速启动脚本进行初步验证：

```bash
python run_youzhi_test.py
```

选择测试模式：
- `1` - 快速测试（前3个问题）
- `2` - 典型问题测试
- `3` - 退出

## 详细使用

### 完整测试

运行所有303个问题的完整测试：

```bash
python test_youzhi_zhangting_comprehensive.py
```

### 限制测试数量

只测试前N个问题：

```bash
python test_youzhi_zhangting_comprehensive.py --max 10
```

### 自定义CSV文件

使用自定义的CSV文件：

```bash
python test_youzhi_zhangting_comprehensive.py --csv path/to/your/questions.csv
```

### 组合参数

```bash
python test_youzhi_zhangting_comprehensive.py --csv custom.csv --max 20
```

## 测试评估标准

### 评估维度

1. **相关性得分** (0-100)
   - 检查响应中是否包含游资、涨停等关键词
   - 权重：游资、涨停、龙虎榜、打板、连板、炸板

2. **完整性得分** (0-100)
   - 响应长度评估
   - 是否包含分析和建议

3. **工具选择得分** (0-100)
   - 是否检测到工具调用
   - 工具调用数量的合理性

4. **专业性得分** (0-100)
   - 专业术语使用情况
   - 权重：基本面、技术面、资金流、市场情绪、风险控制

5. **综合得分**
   - 上述四个维度的平均分

### 工具调用检测

系统会自动检测以下工具的调用：

- `get_hm_detail` - 游资明细
- `get_hm_list` - 游资列表  
- `get_kpl_list` - 涨跌停列表
- `get_kpl_concept` - 涨跌停概念
- `get_top_list` - 龙虎榜
- `get_limit_step` - 连板股
- `get_limit_cpt_list` - 涨停概念统计
- `moneyflow` - 资金流向
- `get_stock_basic_info` - 股票基本信息
- `get_daily` - 日线数据
- `get_stk_auction` - 集合竞价
- 其他相关工具...

## 测试报告

### 报告文件

测试完成后会生成：

1. **详细JSON报告**
   - 文件：`test_reports/youzhi_zhangting_test_YYYYMMDD_HHMMSS.json`
   - 包含每个问题的详细测试结果

2. **简化文本报告**
   - 文件：`test_reports/youzhi_zhangting_summary_YYYYMMDD_HHMMSS.txt`
   - 包含总体统计和摘要

3. **测试日志**
   - 文件：`test_logs/youzhi_test_YYYYMMDD_HHMMSS.log`
   - 包含详细的执行日志

### 报告内容

```json
{
  "test_summary": {
    "total_time": 1234.56,
    "total_questions": 303,
    "successful_tests": 290,
    "failed_tests": 13,
    "success_rate": 95.7,
    "avg_response_time": 2.1,
    "avg_overall_score": 78.5,
    "total_tool_calls": 456
  },
  "detailed_results": [...]
}
```

## 问题集结构

### CSV文件格式

```csv
问题ID,工具名称,用户类型,问题内容,预期工具调用,难度等级,应用场景,问题特性
YZ001,get_hm_detail,ToC,今天有哪些知名游资在操作涨停股？,get_hm_detail(),初级,游资涨停监控,具体明确
YZM001,多工具调用,ToC,深度分析问题...,工具调用链,高级,综合分析,复杂多轮
```

### 问题类型

1. **单轮问题** (YZ001-YZ050)
   - 问题ID以"YZ"开头
   - 通常需要1-2个工具调用
   - 难度：初级、中级

2. **多轮问题** (YZM001-YZM050)  
   - 问题ID以"YZM"开头
   - 需要3-5个工具调用链
   - 难度：中级、高级

## 性能基准

### 预期性能指标

- **成功率**: ≥ 80%
- **平均响应时间**: ≤ 3秒
- **平均综合得分**: ≥ 70分
- **工具调用检测率**: ≥ 60%

### 性能优化

1. **并发控制**: 避免请求过快，设置1秒间隔
2. **超时设置**: LLM调用超时时间适中
3. **错误恢复**: 单个问题失败不影响整体测试
4. **内存管理**: 大量问题测试时的内存控制

## 故障排除

### 常见问题

1. **CSV文件不存在**
   ```
   ❌ CSV文件不存在: ../../archived_data/游资涨停专题问题集.csv
   ```
   解决：确保CSV文件在正确路径

2. **Agent初始化失败**
   ```
   ❌ Agent组件初始化失败: ...
   ```
   解决：检查环境变量和MCP服务器连接

3. **导入错误**
   ```
   ModuleNotFoundError: No module named 'agent'
   ```
   解决：确保在正确目录运行，检查Python路径

4. **权限错误**
   ```
   PermissionError: [Errno 13] Permission denied
   ```
   解决：检查文件和目录权限

### 调试模式

启用详细日志：

```python
# 在代码中修改日志级别
logging.basicConfig(level=logging.DEBUG)
```

## 扩展功能

### 自定义评估标准

可以修改 `evaluate_response` 方法来调整评估标准：

```python
def evaluate_response(self, question, response, tool_calls):
    # 自定义评估逻辑
    pass
```

### 添加新工具检测

在 `extract_tool_calls` 方法中添加新的工具名称：

```python
tool_patterns = [
    'get_hm_detail',
    'your_new_tool',  # 添加新工具
    # ...
]
```

### 自定义报告格式

可以修改 `generate_report` 方法来自定义报告格式。

## 最佳实践

1. **分批测试**: 对于大量问题，建议分批测试
2. **监控资源**: 注意CPU和内存使用情况
3. **定期备份**: 保存重要的测试报告
4. **版本控制**: 记录不同版本的测试结果
5. **持续改进**: 根据测试结果优化Agent性能

## 联系支持

如果遇到问题，请检查：

1. 环境配置是否正确
2. CSV文件格式是否符合要求
3. 网络连接是否正常
4. 日志文件中的详细错误信息

---

**版本**: 1.0  
**更新日期**: 2024-12-17  
**兼容性**: Python 3.11+, LangChain 0.1+ 