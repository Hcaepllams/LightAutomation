#!/bin/bash
# Desktop Light Automation - macOS 开机自启安装脚本
# 用法：./scripts/install-service.sh

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

PLIST_NAME="com.lightautomation.monitor.plist"
PLIST_SOURCE="$SCRIPT_DIR/$PLIST_NAME"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"

echo "🔧 安装 Desktop Light Automation 开机自启服务..."
echo ""

# 检查配置文件
if [ ! -f "$PROJECT_DIR/config.json" ]; then
    echo "❌ 错误：config.json 不存在"
    echo "   请先复制 config.example.json 为 config.json 并修改配置"
    echo ""
    echo "   cp $PROJECT_DIR/config.example.json $PROJECT_DIR/config.json"
    echo "   编辑 $PROJECT_DIR/config.json"
    exit 1
fi

# 创建日志目录
mkdir -p "$PROJECT_DIR/logs"

# 替换 plist 中的占位符
echo "📝 生成 launchd 配置文件..."
cat "$PLIST_SOURCE" | sed "s|\$(PROJECT_DIR)|$PROJECT_DIR|g" > "$PLIST_DEST"

# 卸载旧服务（如果存在）
if launchctl list | grep -q "$PLIST_NAME"; then
    echo "🔄 卸载旧服务..."
    launchctl unload "$PLIST_DEST" 2>/dev/null || true
fi

# 加载新服务
echo "🚀 加载服务..."
launchctl load "$PLIST_DEST"

echo ""
echo "✅ 安装完成！"
echo ""
echo "服务状态："
launchctl list | grep "$PLIST_NAME" || echo "❌ 服务未运行"
echo ""
echo "管理命令："
echo "  查看状态：launchctl list | grep $PLIST_NAME"
echo "  重启服务：launchctl unload $PLIST_DEST && launchctl load $PLIST_DEST"
echo "  卸载服务：launchctl unload $PLIST_DEST && rm $PLIST_DEST"
echo ""
echo "日志位置："
echo "  $PROJECT_DIR/logs/monitor.log"
echo "  $PROJECT_DIR/logs/launchd.out.log"
echo "  $PROJECT_DIR/logs/launchd.err.log"
