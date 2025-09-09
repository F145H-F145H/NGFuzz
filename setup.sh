#!/usr/bin/env bash
set -e

usage() {
    echo "用法: $0 [--no-deps|--deps-only]"
    echo "  (默认)       安装 Python 依赖 + 所有外部依赖"
    echo "  --no-deps    只安装 Python 依赖"
    echo "  --deps-only  只安装外部依赖"
}

# =========================
# 1. 参数解析
# =========================
MODE="all"
if [ $# -gt 0 ]; then
    case "$1" in
        --no-deps) MODE="no-deps" ;;
        --deps-only) MODE="deps-only" ;;
        -h|--help) usage; exit 0 ;;
        *) echo "[!] 未知参数: $1"; usage; exit 1 ;;
    esac
fi

echo "[*] NGFuzz 安装脚本启动 (模式: $MODE)"

# =========================
# 2. Python 依赖
# =========================
if [ "$MODE" = "all" ] || [ "$MODE" = "no-deps" ]; then
    echo "[+] 处理 Python 依赖..."
    echo "[*] 安装 Python 包..."
    pip install -r requirements.txt
fi

# =========================
# 3. 外部依赖
# =========================
if [ "$MODE" = "all" ] || [ "$MODE" = "deps-only" ]; then
    echo "[+] 检查并安装外部依赖..."
    bash "$(dirname "$0")/dependencies/setup.sh" all
fi

echo "[✓] NGFuzz 环境准备完成"
