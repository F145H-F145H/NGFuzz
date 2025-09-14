#!/usr/bin/env python3
import argparse
import os
import sys
from utils.config_parser import Config
# from fuzz_engine.fuzz import Fuzzer


def prepare(config):
    print("========== [准备阶段] ==========")
    target = config.get("target_binary")
    output_dir = config.get("output_dir", "./output")

    # 检查目标程序
    if not os.path.exists(target):
        print(f"[!] 目标程序不存在: {target}")
        sys.exit(1)

    # 管理输出目录
    os.makedirs(output_dir, exist_ok=True)
    print(f"[*] 输出目录: {output_dir}")

    # 测试 GDB 是否可用
    gdb_bin = config.get("gdb_addr", "gdb")
    print(f"[*] GDB 使用: {gdb_bin}")

    # 如果需要，可以测试 remote gdbserver
    remote = config.get("remote_gdbserver")
    if remote:
        print(f"[*] 配置为远程调试: {remote}")
    else:
        print("[*] 配置为本地调试")

    # 目标信息总结
    print(f"[*] 目标程序: {target}")
    print(f"[*] 入口断点: {config.get('entry_point', 'main')}")
    print("================================")
    return target, output_dir

def run_fuzz(config, target):
    print("========== [Fuzz阶段] ==========")
    #fuzzer = Fuzzer(target)
    #fuzzer.run()
    #fuzzer.close()
    print("================================")
    # 模拟一些反馈统计
    result = {
        "coverage": "N/A",   # TODO: 根据触发的断点数计算
        "hit_breakpoints": 1,
        "crashes": 0
    }
    return result

def conclude(result, output_dir):
    print("========== [结语阶段] ==========")
    print(f"[*] Fuzz 完成，结果保存至: {output_dir}")
    print(f"[*] 覆盖率: {result['coverage']}")
    print(f"[*] 命中断点数: {result['hit_breakpoints']}")
    print(f"[*] 崩溃次数: {result['crashes']}")
    print("================================")

def main():
    parser = argparse.ArgumentParser(description="NGFuzz Launcher")
    parser.add_argument("--config", "-c", required=True, help="配置文件路径 (.cfg)")
    args = parser.parse_args()

    config = Config(args.config)

    target, output_dir = prepare(config)
    result = run_fuzz(config, target)
    conclude(result, output_dir)

if __name__ == "__main__":
    main()
