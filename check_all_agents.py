#!/usr/bin/env python3
"""
检查数据库中所有 Agent
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.api.db import get_db
from src.api.models import Agent

def main():
    try:
        db = next(get_db())
        agents = db.query(Agent).all()
        print(f'数据库中有 {len(agents)} 个 Agent:')
        
        for agent in agents:
            print(f'ID: {agent.id}, Name: {agent.name}, Display: {agent.display_name}, Type: {agent.agent_type}')
            
    except Exception as e:
        print(f'检查 Agent 时出错: {e}')

if __name__ == "__main__":
    main()