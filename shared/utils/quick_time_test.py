#!/usr/bin/env python3
"""
快速测试时间感知功能
"""

import asyncio
from system_prompt import generate_system_prompt, get_current_time_info

async def test_time_awareness():
    """测试时间感知功能"""
    
    print("🕐 时间感知功能测试")
    print("=" * 50)
    
    # 测试时间信息获取
    print("📅 当前时间信息:")
    time_info = get_current_time_info()
    for key, value in time_info.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 50)
    
    # 测试系统提示生成
    print("📝 生成带时间的系统提示:")
    prompt = generate_system_prompt(include_time=True)
    
    # 显示系统提示的前500个字符
    print("系统提示预览:")
    print("-" * 30)
    print(prompt[:800] + "..." if len(prompt) > 800 else prompt)
    print("-" * 30)
    
    print(f"\n✅ 系统提示总长度: {len(prompt)} 字符")
    
    # 测试选定的问题
    test_query = "如何分析今日涨停股的游资集中度和投资价值？"
    print(f"\n🧪 测试查询: {test_query}")
    
    # 分析查询中的时间关键词
    time_keywords = ['今日', '今天', '昨天', '上周', '本月', '最近']
    found_keywords = [kw for kw in time_keywords if kw in test_query]
    
    if found_keywords:
        print(f"⏰ 发现时间关键词: {found_keywords}")
        print("✅ 该查询需要时间感知处理")
    else:
        print("ℹ️ 该查询不包含明显的时间关键词")
    
    print("\n🎯 预期Agent行为:")
    print("1. 识别'今日'关键词")
    print(f"2. 将'今日'解析为当前日期: {time_info['current_date']}")
    print("3. 在工具调用中使用正确的日期参数")
    print("4. 按照预期的5步工具调用链执行")
    
    return True

if __name__ == "__main__":
    asyncio.run(test_time_awareness()) 