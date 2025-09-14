#!/usr/bin/env python3
"""
gdb_controller_mvp.py - MVP版 GDB 控制器 (增强版 process_output)
功能：
1. 初始化 GDB
2. 设置断点
3. 运行程序并监控状态
4. 获取调用栈 (并格式化)
5. 基于 payload 类型自动识别并处理 (backtrace / breakpoint / signal ...)
"""

import sys
import os
from io import StringIO
from typing import Optional, List, Dict, Any
from enum import Enum
from pprint import pprint

from pygdbmi.gdbcontroller import GdbController

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))
from logger import logger, Logger, DEBUG, INFO, WARNING

respio = StringIO()

class ProgramStatus(Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    EXITED = "exited"
    CRASHED = "crashed"
    UNKNOWN = "unknown"

def format_stack_trace(stack: List[Dict[str, Any]]) -> str:
    """Format stack into arrow chain style: main -> funA -> funB -> ..."""
    # gdb/mi 给出的 stack level=0 是当前帧，level 最大的是 main
    # 我们翻转顺序，让 main 在最前，当前帧在最后
    stack_reversed = stack[::-1]
    return " ->\n".join(f"{frame['func']}:{frame['addr']}" for frame in stack_reversed)

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

    # -----------------
    # 核心改造：process_output
    # -----------------
    def process_output(self, resp, action: str = ""):
        # 原始输出存到日志
        respio.seek(0)
        respio.truncate(0)
        pprint(resp, respio)
        if action:
            logger(INFO, f"{action}", stacklevel=4)
        logger(DEBUG, "Message from pygdbmi:\n" + respio.getvalue(), stacklevel=4)

        # 标准化成 list
        msgs = resp if isinstance(resp, list) else [resp]

        results = []
        for msg in msgs:
            payload = msg.get("payload")
            mtype = msg.get("type")
            message = msg.get("message")

            # --- 调用栈 ---
            if isinstance(payload, dict) and "stack" in payload:
                stack = payload["stack"]
                self.call_stack = stack
                formatted = format_stack_trace(stack)
                logger(INFO, "Call stack:\n" + formatted, stacklevel=4)
                results.append({"kind": "backtrace", "frames": stack})

            # --- 断点 ---
            elif isinstance(payload, dict) and ("bkpt" in payload or "number" in payload):
                logger(INFO, f"Breakpoint info: {payload}", stacklevel=4)
                results.append({"kind": "breakpoint", "payload": payload})

            # --- 信号/崩溃 ---
            elif isinstance(payload, dict) and ("signal-name" in payload or "reason" in payload):
                sig = payload.get("signal-name") or payload.get("reason")
                self.status = ProgramStatus.CRASHED
                self.signal = sig
                logger(WARNING, f"Program crashed: {sig}", stacklevel=4)
                results.append({"kind": "signal", "signal": sig})

            # --- result:done 等通用消息 ---
            elif mtype == "result" and message in ("done", "running", "connected"):
                logger(INFO, f"GDB result: {message}", stacklevel=4)
                results.append({"kind": "result", "message": message})

            else:
                # 默认回退：原始打印
                results.append({"kind": "generic", "msg": msg})

        return results

    # -----------------
    # 业务函数
    # -----------------
    def set_breakpoint(self, location: str) -> bool:
        resp = self.gdb.write(f"-break-insert {location}")
        return self.process_output(resp, f"Setting breakpoint at {location}")

    def run(self, args: str = "") -> ProgramStatus:
        if args:
            resp = self.gdb.write(f"set args {args}")
            self.process_output(resp, f"Setting args: {args}")
        
        resp = self.gdb.write("-exec-run")
        self.process_output(resp, f"Running program")

        self.status = ProgramStatus.RUNNING
        return self.status

    def get_stack_trace(self) -> List[Dict[str, Any]]:
        resp = self.gdb.write("-stack-list-frames")
        result = self.process_output(resp, f"Fetching call stack")
        return self.call_stack

    def close(self):
        logger(INFO, "Exiting gdb_controller!")
        self.gdb.exit()

# -----------------
# Demo
# -----------------
if __name__ == "__main__":
    logger(INFO, "Now Running test demo")
    Logger.setLevel(DEBUG)
    gdb = GDBController(target_binary="targets/crashme")
    gdb.set_breakpoint("funC")
    gdb.run("test_argument")
    gdb.get_stack_trace()
    gdb.close()
