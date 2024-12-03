import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

# 创建日志目录
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)

    # 文件处理器
    log_file = os.path.join(
        LOG_DIR, 
        f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
    )
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)

    # 添加处理器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
