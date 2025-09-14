#!/usr/bin/env python3
"""
gdb_controller_mvp.py - MVP版 GDB 控制器
只保留最小可用功能：
1. 初始化 GDB
2. 设置断点
3. 运行程序并监控状态
4. 获取调用栈
"""

import sys
import os
from io import StringIO
from typing import Optional, List, Dict, Any
from enum import Enum

from pygdbmi.gdbcontroller import GdbController
# from pygdbmi import gdbmiparser
from pprint import pprint

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))
from logger import logger, Logger, DEBUG, INFO

respio = StringIO()

class ProgramStatus(Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    EXITED = "exited"
    CRASHED = "crashed"
    UNKNOWN = "unknown"

class GDBController:
    def __init__(self, gdb_path="gdb", target_binary: Optional[str] = None):
        self.gdb = GdbController([gdb_path, "--nx", "--quiet", "--interpreter=mi3"])
        self.target_binary = target_binary
        self.status = ProgramStatus.UNKNOWN
        self.signal = None
        self.exit_code = None
        self.call_stack: List[Dict[str, Any]] = []

        if self.target_binary:
            if not os.path.exists(self.target_binary):
                raise FileNotFoundError(f"目标文件不存在: {self.target_binary}")
            self.gdb.write(f"file {self.target_binary}")
        
        # 禁用自动下载调试信息
        self.gdb.write("set debuginfod enabled off")

    def set_breakpoint(self, location: str) -> bool:
        resp = self.gdb.write(f"-break-insert {location}")
        pprint(resp,respio)
        logger(INFO,f"Setting breakpoint to {location}")
        logger(DEBUG,"Message from pygdbmi:\n" + respio.getvalue())

    def run(self, args: str = "") -> ProgramStatus:
        if args:
            resp = self.gdb.write(f"set args: {args}")
            pprint(resp,respio)
            logger(INFO,f"Setting args {args}")
            logger(DEBUG,"Message from pygdbmi:\n" + respio.getvalue())
        
        resp = self.gdb.write("-exec-run")
        pprint(resp,respio)
        logger(INFO,f"Now starting running program")
        logger(DEBUG,"Message from pygdbmi:\n" + respio.getvalue())

    def get_stack_trace(self) -> List[Dict[str, Any]]:
        # to be done
        print()

    def close(self):
        logger(INFO,"Exiting gdb_controller!")
        self.gdb.exit()

if __name__ == "__main__":
    logger(INFO, "Now Running test demo")
    Logger.setLevel(DEBUG)
    gdb = GDBController(target_binary="targets/crashme")
    gdb.set_breakpoint("main")
    gdb.run("test_argument")
    gdb.get_stack_trace()
    gdb.close()
