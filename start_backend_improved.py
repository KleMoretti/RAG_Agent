#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
改进的后端启动脚本，增加错误处理和超时配置
"""

import uvicorn
import logging
import sys
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('backend.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """启动后端服务器"""
    try:
        logger.info("正在启动后端服务器...")
        
        # 检查main.py是否存在
        main_file = Path(__file__).parent / "main.py"
        if not main_file.exists():
            logger.error(f"main.py 文件不存在: {main_file}")
            sys.exit(1)
        
        # 启动uvicorn服务器，增加超时和错误处理配置
        uvicorn.run(
            "main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            reload_dirs=[str(Path(__file__).parent)],
            log_level="info",
            access_log=True,
            # 增加超时配置
            timeout_keep_alive=30,
            timeout_graceful_shutdown=10,
            # 工作进程配置
            workers=1,
            # 移除请求限制以避免频繁重启
            # limit_max_requests=1000,  # 注释掉，避免worker频繁重启
            limit_concurrency=200,  # 增加并发限制
        )
        
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭服务器...")
    except Exception as e:
        logger.error(f"启动服务器时发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()