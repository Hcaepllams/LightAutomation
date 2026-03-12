#!/bin/bash
# Desktop Light Automation - 启动脚本
# 用法: ./scripts/run.sh

set -e

# 获取脚本所在目录
cd "$(dirname "$0")/.."

# 检查 Python3
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3"
    echo "   请安装 Python 3.9 或更高版本"
    exit 1
fi

# 检查 Python 版本
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.9"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then 
    echo "❌ 错误: Python 版本过低 ($PYTHON_VERSION)"
    echo "   需要 Python $REQUIRED_VERSION 或更高版本"
    exit 1
fi

# 创建必要的目录
mkdir -p logs

# 检查配置文件
if [ ! -f "config.json" ]; then
    echo "⚠️  配置文件不存在，正在创建默认配置..."
    echo '{
  "pc": {
    "ip": "192.168.1.100",
    "ping_interval_sec": 30,
    "online_threshold": 3,
    "offline_threshold": 5
  },
  "shortcuts": {
    "arrive": "到家",
    "leave": "离开"
  },
  "logging": {
    "level": "INFO",
    "max_days": 7
  }
}' > config.json
    echo "✅ 已创建默认配置: config.json"
    echo "⚠️  请编辑 config.json 设置正确的 IP 地址后再运行！"
    exit 1
fi

echo "🚀 启动 Desktop Light Automation..."
echo "   按 Ctrl+C 停止"
echo ""

# 运行监控脚本
exec python3 src/monitor.py "$@"
