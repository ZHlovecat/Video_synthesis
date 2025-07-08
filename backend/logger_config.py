"""
日志配置模块
提供统一的日志管理和格式化
"""

import logging
import sys
from datetime import datetime
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器"""
    
    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',    # 青色
        'INFO': '\033[32m',     # 绿色
        'WARNING': '\033[33m',  # 黄色
        'ERROR': '\033[31m',    # 红色
        'CRITICAL': '\033[35m', # 紫色
    }
    RESET = '\033[0m'
    
    def format(self, record):
        # 添加颜色
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        
        # 格式化时间
        record.asctime = datetime.now().strftime('%H:%M:%S')
        
        return super().format(record)


class ModuleLogger:
    """模块化日志管理器"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.module_name = name
        
    def _log_with_module(self, level: int, message: str, **kwargs):
        """带模块名的日志记录"""
        formatted_message = f"[{self.module_name}] {message}"
        self.logger.log(level, formatted_message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        self._log_with_module(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        self._log_with_module(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log_with_module(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._log_with_module(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        self._log_with_module(logging.CRITICAL, message, **kwargs)


def setup_logging(level: str = 'INFO') -> None:
    """设置全局日志配置"""
    
    # 清除现有的处理器
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 设置日志级别
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # 设置格式化器
    formatter = ColoredFormatter(
        fmt='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # 配置根日志器
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # 禁用Flask的默认日志
    logging.getLogger('werkzeug').setLevel(logging.WARNING)


def get_module_logger(module_name: str) -> ModuleLogger:
    """获取模块日志器"""
    return ModuleLogger(module_name)


# 预定义的模块日志器
class AppLoggers:
    """应用日志器集合"""
    
    SYSTEM = get_module_logger("系统")
    API = get_module_logger("API")
    UPLOAD = get_module_logger("上传")
    COMPOSE = get_module_logger("合成")
    DOWNLOAD = get_module_logger("下载")
    PREVIEW = get_module_logger("预览")
    FILES = get_module_logger("文件")
    ERROR = get_module_logger("错误")


def log_request_info(endpoint: str, method: str, **kwargs):
    """记录请求信息"""
    extra_info = " | ".join([f"{k}={v}" for k, v in kwargs.items() if v is not None])
    message = f"{method} {endpoint}"
    if extra_info:
        message += f" | {extra_info}"
    AppLoggers.API.info(message)


def log_response_info(endpoint: str, status_code: int, message: str = None):
    """记录响应信息"""
    status_text = "成功" if 200 <= status_code < 300 else "失败"
    log_message = f"{endpoint} | {status_code} {status_text}"
    if message:
        log_message += f" | {message}"
    
    if 200 <= status_code < 300:
        AppLoggers.API.info(log_message)
    elif 400 <= status_code < 500:
        AppLoggers.API.warning(log_message)
    else:
        AppLoggers.API.error(log_message)


def log_file_operation(operation: str, filename: str, success: bool = True, details: str = None):
    """记录文件操作"""
    status = "成功" if success else "失败"
    message = f"{operation} | {filename} | {status}"
    if details:
        message += f" | {details}"
    
    logger = AppLoggers.FILES
    if success:
        logger.info(message)
    else:
        logger.error(message)


def log_video_processing(operation: str, details: str, success: bool = True):
    """记录视频处理操作"""
    status = "成功" if success else "失败"
    message = f"{operation} | {status} | {details}"
    
    logger = AppLoggers.COMPOSE
    if success:
        logger.info(message)
    else:
        logger.error(message)


def log_system_info(message: str):
    """记录系统信息"""
    AppLoggers.SYSTEM.info(message)


def log_error(module: str, error: Exception, context: str = None):
    """记录错误信息"""
    message = f"{module}"
    if context:
        message += f" | {context}"
    message += f" | {type(error).__name__}: {str(error)}"
    AppLoggers.ERROR.error(message)
