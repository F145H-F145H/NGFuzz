#!/usr/bin/env python3
"""
logger.py - 轻量级可复用日志系统
支持：
    logger(DEBUG, "xxx")
    Logger.DEBUG("xxx")

特性：
    - 默认输出到 stdout (彩色)
    - 写入 latest.log (覆盖旧文件, 无颜色)
    - 默认等级 DEBUG
    - 所有日志都会显示来源文件 + 行号
    - 可设置 stacklevel 控制调用堆栈深度
"""

import sys
import time
import inspect

# 日志等级
DEBUG = 10
INFO = 20
WARNING = 30
ERROR = 40

LEVEL_NAMES = {
    DEBUG: "DEBUG",
    INFO: "INFO",
    WARNING: "WARNING",
    ERROR: "ERROR"
}

# ANSI 颜色
COLORS = {
    DEBUG: "\033[94m",   # 蓝色
    INFO: "\033[92m",    # 绿色
    WARNING: "\033[93m", # 黄色
    ERROR: "\033[91m",   # 红色
}
RESET = "\033[0m"

class Logger:
    _log_file = "latest.log"
    _level = DEBUG
    _fp = None

    @classmethod
    def config(cls, file: str = "latest.log", level: int = DEBUG):
        """统一配置接口"""
        cls._log_file = file
        cls._level = level
        if cls._fp:
            cls._fp.close()
            cls._fp = None  # 下次写入时重新打开

    @classmethod
    def setLevel(cls, lvl: int):
        cls._level = lvl

    @classmethod
    def _ensure_file(cls):
        if cls._fp is None:
            cls._fp = open(cls._log_file, "w", encoding="utf-8")

    @classmethod
    def _write(cls, lvl: int, msg: str, stacklevel: int = 3):
        """真正的日志输出实现"""
        if lvl < cls._level:
            return
        cls._ensure_file()
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        # 获取调用日志的文件名 + 行号
        frame = inspect.stack()[stacklevel - 1]
        filename = frame.filename.split("/")[-1]
        lineno = frame.lineno

        base_line = f"[{now}] {LEVEL_NAMES[lvl]} ({filename}:{lineno}): {msg}\n"

        # 文件写入（无颜色）
        cls._fp.write(base_line)
        cls._fp.flush()

        # 终端输出（有颜色）
        color = COLORS.get(lvl, "")
        sys.stdout.write(f"{color}{base_line}{RESET}")

    # 快捷接口
    @classmethod
    def DEBUG(cls, msg: str, stacklevel: int = 3): cls._write(DEBUG, msg, stacklevel)
    @classmethod
    def INFO(cls, msg: str, stacklevel: int = 3): cls._write(INFO, msg, stacklevel)
    @classmethod
    def WARNING(cls, msg: str, stacklevel: int = 3): cls._write(WARNING, msg, stacklevel)
    @classmethod
    def ERROR(cls, msg: str, stacklevel: int = 3): cls._write(ERROR, msg, stacklevel)

# 函数式接口
def logger(level: int, msg: str, stacklevel: int = 3):
    Logger._write(level, msg, stacklevel)
