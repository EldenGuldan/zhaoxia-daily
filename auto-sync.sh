#!/bin/bash
# 朝霞日报自动同步脚本
# 每天自动采集数据并同步到飞书表格

set -e

# 设置飞书 Token（从 openclaw 配置中读取）
export FEISHU_ACCESS_TOKEN="${FEISHU_ACCESS_TOKEN:-}"

echo "=========================================="
echo "开始执行朝霞日报自动同步"
echo "时间: $(date)"
echo "=========================================="

# 进入项目目录
cd /root/.openclaw/workspace/zhaoxia-daily

# 步骤1: 运行爬虫采集数据
echo ""
echo "[1/3] 采集最新数据..."
cd crawler
python3 main.py 2>&1 | tee /tmp/crawler.log || {
    echo "⚠️ 爬虫执行失败，使用现有数据继续"
}
cd ..

# 检查数据文件是否存在
if [ ! -f "web/public/data/news.json" ]; then
    echo "❌ 错误: 数据文件不存在"
    exit 1
fi

DATA_COUNT=$(python3 -c "import json; print(len(json.load(open('web/public/data/news.json'))['items']))")
echo "✅ 采集完成: $DATA_COUNT 条数据"

# 步骤2: 同步到飞书表格
echo ""
echo "[2/3] 同步到飞书表格..."
cd sync
python3 feishu_sync.py 2>&1 | tee /tmp/sync.log || {
    echo "❌ 同步失败"
    exit 1
}
cd ..

# 步骤3: 可选 - 重新部署网站（如果数据更新）
echo ""
echo "[3/3] 检查是否需要重新部署..."
if command -v git &> /dev/null; then
    if [ -n "$(git status --porcelain web/public/data/news.json 2>/dev/null)" ]; then
        echo "数据已更新，提交并推送..."
        git add web/public/data/news.json
        git commit -m "auto: update news data $(date +%Y-%m-%d)"
        git push
        echo "✅ 已推送到 GitHub，Vercel 将自动重新部署"
    else
        echo "数据无变化，跳过部署"
    fi
else
    echo "git 不可用，跳过部署步骤"
fi

echo ""
echo "=========================================="
echo "同步任务完成: $(date)"
echo "=========================================="
