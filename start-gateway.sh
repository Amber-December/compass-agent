#!/bin/bash
# Compass Multi-Agent Gateway 启动脚本
# 多 Agent 隔离架构

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 项目级 OpenClaw 状态目录
export OPENCLAW_STATE_DIR="$PROJECT_DIR/.openclaw"
export OPENCLAW_CONFIG_PATH="$PROJECT_DIR/.openclaw/openclaw.json"

echo "🦞 Starting Compass Multi-Agent Gateway..."
echo "Project dir: $PROJECT_DIR"
echo "State dir:   $OPENCLAW_STATE_DIR"
echo ""

# 检查 Agent 配置
echo "📋 Configured Agents:"
for agent_dir in "$OPENCLAW_STATE_DIR"/agents/*/; do
    if [ -d "$agent_dir" ]; then
        agent_name=$(basename "$agent_dir")
        echo "  - $agent_name"
    fi
done
echo ""

# 停止可能存在的其他 gateway
openclaw gateway stop 2>/dev/null || true

# 前台运行
echo "🚀 Gateway starting..."
exec openclaw gateway run --verbose
