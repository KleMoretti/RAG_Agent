#!/usr/bin/env python3
"""
检查用户表数据
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.api.db import get_db
from src.api.models import User

def main():
    try:
        db = next(get_db())
        users = db.query(User).all()
        print(f'用户表中有 {len(users)} 个用户')
        
        if users:
            for user in users:
                print(f'用户 ID: {user.id}, 用户名: {user.username}')
        else:
            print('用户表为空，需要先创建用户')
            
    except Exception as e:
        print(f'检查用户表时出错: {e}')

if __name__ == "__main__":
    main()