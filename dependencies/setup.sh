#!/usr/bin/env bash
set -e
DEPS_DIR="$(dirname "$0")"

GHIDRA_VERSION=11.4.2
GHIDRA_DATE=20250826
GHIDRA_URL="https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_${GHIDRA_VERSION}_build/ghidra_${GHIDRA_VERSION}_PUBLIC_${GHIDRA_DATE}.zip"

usage() {
    echo "用法: $0 [all|ghidra|gdb|afl|clean]"
    echo "  all     安装全部依赖 (默认)"
    echo "  ghidra  单独安装 Ghidra"
    echo "  gdb     检查/安装 GDB"
    echo "  afl     单独安装 AFL++"
    echo "  clean   删除已下载依赖"
}

install_ghidra() {
    if [ ! -d "$DEPS_DIR/ghidra" ]; then
        echo "[+] 下载 Ghidra ${GHIDRA_VERSION}"
        wget -O "$DEPS_DIR/ghidra.zip" "$GHIDRA_URL"
        unzip -q "$DEPS_DIR/ghidra.zip" -d "$DEPS_DIR/"
        mv "$DEPS_DIR/ghidra_${GHIDRA_VERSION}_PUBLIC" "$DEPS_DIR/ghidra"
        rm "$DEPS_DIR/ghidra.zip"
    else
        echo "[*] Ghidra 已存在，跳过下载"
    fi
}

install_gdb() {
    if ! command -v gdb &>/dev/null; then
        echo "[!] 未检测到 gdb，请手动安装 (sudo apt install gdb)"
    else
        echo "[*] 已检测到 gdb: $(gdb --version | head -n1)"
    fi
}

install_afl() {
    if [ ! -d "$DEPS_DIR/aflplusplus" ]; then
        echo "[+] 克隆并编译 AFL++"
        git clone https://github.com/AFLplusplus/AFLplusplus.git "$DEPS_DIR/aflplusplus"
        cd "$DEPS_DIR/aflplusplus"
        make source-only   # 避免编译 nyx 等耗时部分
    else
        echo "[*] AFL++ 已存在，跳过克隆"
    fi
}

clean_all() {
    echo "[*] 清理依赖..."
    rm -rf "$DEPS_DIR/ghidra" "$DEPS_DIR/aflplusplus"
    echo "[✓] 清理完成"
}

# ===========================
# 主逻辑
# ===========================
ACTION="${1:-all}"

case "$ACTION" in
    all)
        echo "[*] 开始准备外部依赖..."
        install_ghidra
        install_gdb
        install_afl
        echo "[✓] 外部依赖准备完成"
        ;;
    ghidra) install_ghidra ;;
    gdb)    install_gdb ;;
    afl)    install_afl ;;
    clean)  clean_all ;;
    *) usage; exit 1 ;;
esac
