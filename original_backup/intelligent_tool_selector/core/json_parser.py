"""
JSON解析核心模块
JSON Parser Core Module

提供增强的JSON解析功能，能够处理各种格式问题和干扰标签
"""

import json
import re
from typing import Dict, Any, Optional


class JSONParser:
    """增强的JSON解析器"""
    
    @staticmethod
    def extract_json_from_response(response_text: str) -> Dict[str, Any]:
        """
        从模型响应中提取JSON，处理各种格式问题
        
        Args:
            response_text: 模型的原始响应文本
            
        Returns:
            解析后的JSON字典，如果解析失败返回空字典
        """
        parser = JSONParser()
        
        # 方法1: 移除<think>标签及其内容
        cleaned_text = parser._remove_think_tags(response_text)
        
        # 方法2: 查找JSON代码块
        json_content = parser._extract_json_from_code_block(cleaned_text)
        if json_content:
            try:
                return json.loads(json_content)
            except json.JSONDecodeError:
                pass
        
        # 方法3: 直接查找JSON对象
        json_content = parser._extract_json_object(cleaned_text)
        if json_content:
            try:
                return json.loads(json_content)
            except json.JSONDecodeError:
                pass
        
        # 方法4: 尝试修复常见的JSON格式问题
        json_content = parser._fix_common_json_issues(cleaned_text)
        if json_content:
            try:
                return json.loads(json_content)
            except json.JSONDecodeError:
                pass
        
        return {}
    
    def _remove_think_tags(self, text: str) -> str:
        """移除<think>标签及其内容"""
        # 移除<think>...</think>内容
        pattern = r'<think>.*?</think>'
        cleaned = re.sub(pattern, '', text, flags=re.DOTALL)
        return cleaned.strip()
    
    def _extract_json_from_code_block(self, text: str) -> str:
        """从```json代码块中提取JSON"""
        # 查找```json ... ```格式
        pattern = r'```json\s*(.*?)\s*```'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # 查找``` ... ```格式（可能没有明确指定json）
        pattern = r'```\s*(.*?)\s*```'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            content = match.group(1).strip()
            # 检查是否看起来像JSON
            if content.startswith('{') and content.endswith('}'):
                return content
        
        return ""
    
    def _extract_json_object(self, text: str) -> str:
        """直接提取JSON对象"""
        # 查找第一个{到最后一个}之间的内容
        start_pos = text.find('{')
        end_pos = text.rfind('}')
        
        if start_pos >= 0 and end_pos > start_pos:
            return text[start_pos:end_pos + 1]
        
        return ""
    
    def _fix_common_json_issues(self, text: str) -> str:
        """修复常见的JSON格式问题"""
        # 提取可能的JSON部分
        json_content = self._extract_json_object(text)
        if not json_content:
            return ""
        
        # 修复常见问题
        fixed_content = json_content
        
        # 1. 修复单引号为双引号
        fixed_content = re.sub(r"'([^']*)':", r'"\1":', fixed_content)
        fixed_content = re.sub(r":\s*'([^']*)'", r': "\1"', fixed_content)
        
        # 2. 修复尾随逗号
        fixed_content = re.sub(r',\s*}', '}', fixed_content)
        fixed_content = re.sub(r',\s*]', ']', fixed_content)
        
        # 3. 修复缺失的逗号（简单情况）
        fixed_content = re.sub(r'"\s*\n\s*"', '",\n  "', fixed_content)
        
        # 4. 移除注释
        fixed_content = re.sub(r'//.*', '', fixed_content)
        
        return fixed_content
    
    @staticmethod
    def validate_json_structure(json_data: Dict[str, Any]) -> bool:
        """
        验证JSON数据结构是否符合预期
        
        Args:
            json_data: 待验证的JSON数据
            
        Returns:
            是否符合预期结构
        """
        required_sections = ['analysis', 'tool_selection', 'parameter_mapping']
        
        for section in required_sections:
            if section not in json_data:
                return False
        
        # 验证tool_selection结构
        tool_selection = json_data.get('tool_selection', {})
        if 'primary_tool' not in tool_selection:
            return False
        
        primary_tool = tool_selection['primary_tool']
        required_tool_fields = ['name', 'reason', 'confidence']
        
        for field in required_tool_fields:
            if field not in primary_tool:
                return False
        
        return True 