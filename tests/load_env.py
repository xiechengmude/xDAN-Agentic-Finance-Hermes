"""
加载.env文件的辅助模块
"""

import os
from pathlib import Path

def load_dotenv():
    """手动加载.env文件"""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # 处理包含等号的行
                    if '=' in line:
                        key, value = line.split('=', 1)
                        # 去除引号
                        value = value.strip('"').strip("'")
                        os.environ[key] = value

# 自动加载
load_dotenv()