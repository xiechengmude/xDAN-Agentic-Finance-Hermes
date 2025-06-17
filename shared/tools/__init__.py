"""
工具模块
Tools Module

包含各种工具信息和工具管理功能
"""

import os
import csv
from typing import Dict, List, Any, Optional

def load_tools_info(csv_file: str = "xdan_finance_tools_info.csv") -> List[Dict[str, Any]]:
    """
    从CSV文件加载工具信息
    
    Args:
        csv_file: CSV文件名
        
    Returns:
        工具信息列表
    """
    tools_info = []
    csv_path = os.path.join(os.path.dirname(__file__), csv_file)
    
    if not os.path.exists(csv_path):
        print(f"⚠️ 工具信息文件不存在: {csv_path}")
        return tools_info
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                tools_info.append(dict(row))
    except Exception as e:
        print(f"❌ 读取工具信息文件失败: {e}")
    
    return tools_info

def get_tool_by_name(tool_name: str, tools_info: Optional[List[Dict[str, Any]]] = None) -> Optional[Dict[str, Any]]:
    """
    根据工具名称获取工具信息
    
    Args:
        tool_name: 工具名称
        tools_info: 工具信息列表，如果为None则自动加载
        
    Returns:
        工具信息字典或None
    """
    if tools_info is None:
        tools_info = load_tools_info()
    
    for tool in tools_info:
        if tool.get('name') == tool_name or tool.get('tool_name') == tool_name:
            return tool
    
    return None

def search_tools(keyword: str, tools_info: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """
    搜索包含关键词的工具
    
    Args:
        keyword: 搜索关键词
        tools_info: 工具信息列表，如果为None则自动加载
        
    Returns:
        匹配的工具列表
    """
    if tools_info is None:
        tools_info = load_tools_info()
    
    matching_tools = []
    keyword_lower = keyword.lower()
    
    for tool in tools_info:
        # 在工具名称和描述中搜索
        name = tool.get('name', '').lower()
        description = tool.get('description', '').lower()
        
        if keyword_lower in name or keyword_lower in description:
            matching_tools.append(tool)
    
    return matching_tools

__all__ = ["load_tools_info", "get_tool_by_name", "search_tools"] 