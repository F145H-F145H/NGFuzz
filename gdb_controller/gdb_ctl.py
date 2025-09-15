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
            message = msg.get("message")
            payload = msg.get("payload")
            msg_type = msg.get("type")
            
            # 处理程序状态变化
            if msg_type == "notify":

                if message == "stopped":
                    self.status = ProgramStatus.STOPPED
                    if payload and "reason" in payload:
                        reason = payload["reason"]
                        if reason == "breakpoint-hit":
                            logger(WARNING, f"Program stopped at breakpoint: {reason}", stacklevel=4)
                        elif reason == "signal-received":
                            self.status = ProgramStatus.CRASHED
                            signal_name = payload.get("signal-name", "unknown")
                            self.signal = signal_name
                            logger(WARNING, f"Program crashed with signal: {signal_name}", stacklevel=4)
                            self.get_stack_trace()
                        else:
                            logger(INFO, f"Program stopped: {reason}", stacklevel=4)
                    
                    # 记录断点信息
                    if payload and "bkptno" in payload:
                        logger(INFO, f"Breakpoint number: {payload['bkptno']}", stacklevel=4)
                
                elif message == "running":
                    self.status = ProgramStatus.RUNNING
                    logger(INFO, "Program is running", stacklevel=4)
                
                elif message == "thread-created":
                    logger(DEBUG, f"Thread created: {payload}", stacklevel=4)
                
                elif message == "thread-group-started":
                    logger(DEBUG, f"Thread group started: {payload}", stacklevel=4)
            
            # 处理命令执行结果
            elif msg_type == "result":
                if message == "done":
                    if payload and "bkpt" in payload:
                        self.breakpoint_info = payload["bkpt"]
                        logger(INFO, f"Breakpoint info: {self.breakpoint_info}", stacklevel=4)
                        results.append(self.breakpoint_info)
                    elif payload and "stack" in payload:
                        self.call_stack = payload["stack"]
                        formatted_stack = format_stack_trace(self.call_stack)
                        logger(INFO, f"Call stack:\n{formatted_stack}", stacklevel=4)
                        results.append(self.call_stack)
                    else:
                        logger(INFO, f"GDB result: {message}", stacklevel=4)
                        results.append(message)
                
                elif message == "running":
                    self.status = ProgramStatus.RUNNING
                    logger(INFO, "Program started running", stacklevel=4)
                    results.append(message)
            
            # 处理控制台输出
            elif msg_type == "console":
                if payload and "exited" in payload:
                    self.status = ProgramStatus.EXITED
                    logger(INFO, "Program exited normally", stacklevel=4)
                elif payload and "terminated" in payload:
                    self.status = ProgramStatus.CRASHED
                    logger(WARNING, "Program terminated unexpectedly", stacklevel=4)
            
            # 处理日志信息
            elif msg_type == "log":
                if payload and "exited" in payload:
                    self.status = ProgramStatus.EXITED
                    logger(INFO, "Program exited normally", stacklevel=4)
        
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
        self.process_output(resp, f"Fetching call stack")
        return self.call_stack
    
    def continue_exec(self) -> ProgramStatus:
        """继续执行程序，直到下一个断点或程序结束"""
        resp = self.gdb.write("-exec-continue")
        self.process_output(resp, "Continuing program execution")
        return self.status

    def close(self):
        logger(INFO, "Exiting gdb_controller!")
        self.gdb.exit()

# -----------------
# Demo
# -----------------
if __name__ == "__main__":
    logger(INFO, "Now Running test demo")
    Logger.setLevel(INFO)
    gdb = GDBController(target_binary="targets/crashme")
    gdb.set_breakpoint("funC")
    gdb.run("test_arg")
    gdb.get_stack_trace()
    gdb.continue_exec()
    gdb.close()
