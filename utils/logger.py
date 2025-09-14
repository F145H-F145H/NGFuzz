#!/usr/bin/env python3
"""
logger.py - 轻量级可复用日志系统
支持：
    logger(DEBUG, "xxx")
    Logger.DEBUG("xxx")

特性：
    - 默认输出到 stdout
    - 写入 latest.log (覆盖旧文件)
    - 默认等级 DEBUG
    - 所有日志都会显示来源文件 + 行号
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
    def _write(cls, lvl: int, msg: str):
        if lvl < cls._level:
            return
        cls._ensure_file()
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        # 获取调用日志的文件名 + 行号
        frame = inspect.stack()[2]
        filename = frame.filename.split("/")[-1]
        lineno = frame.lineno

        line = f"[{now}] {LEVEL_NAMES[lvl]} ({filename}:{lineno}): {msg}\n"

        cls._fp.write(line)
        cls._fp.flush()
        sys.stdout.write(line)

    # 快捷接口
    @classmethod
    def DEBUG(cls, msg: str): cls._write(DEBUG, msg)
    @classmethod
    def INFO(cls, msg: str): cls._write(INFO, msg)
    @classmethod
    def WARNING(cls, msg: str): cls._write(WARNING, msg)
    @classmethod
    def ERROR(cls, msg: str): cls._write(ERROR, msg)

# 函数式接口
def logger(level: int, msg: str):
    Logger._write(level, msg)
