#!/usr/bin/env python3
"""
飞书多维表格同步脚本 - 使用 openclaw 工具
将采集的新闻数据同步到飞书 Bitable
"""

import json
import os
import sys
import subprocess
from datetime import datetime
from typing import List, Dict, Any

# 飞书配置
FEISHU_CONFIG = {
    "app_token": "NgMCbk9aGaqrG9sgecmcjIgqnMd",
    "table_id": "tblEAuimN2Ie9789",
    "view_id": "vewGazu8y4",
}

# 类别选项映射
CATEGORY_OPTIONS = {
    "tool": "🛠️ AI工具",
    "news": "📰 行业新闻",
    "trend": "🔥 热点话题",
}

# 来源类型映射（标准化）
SOURCE_TYPE_MAP = {
    "官方博客": "官方博客",
    "开源社区": "开源社区",
    "开源项目": "开源社区",
    "产品发布": "产品发布",
    "社交媒体": "社交媒体",
    "科技媒体": "科技媒体",
    "AI社区": "AI社区",
    "企业新闻": "官方博客",
}


class NewsItem:
    """新闻数据项"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', '')
        self.title = kwargs.get('title', '')
        self.summary = kwargs.get('summary', '')
        self.url = kwargs.get('url', '')
        self.source = kwargs.get('source', '')
        self.source_type = kwargs.get('source_type', 'AI社区')
        self.category = kwargs.get('category', 'tool')
        self.tags = kwargs.get('tags', [])
        self.published_at = kwargs.get('published_at', '')
        self.likes = kwargs.get('likes', 0)
        self.views = kwargs.get('views', 0)
        self.comments = kwargs.get('comments', 0)
        self.engagement = kwargs.get('engagement', 0)


class FeishuSync:
    """飞书表格同步器"""
    
    def __init__(self, app_token: str, table_id: str, view_id: str = None):
        self.app_token = app_token
        self.table_id = table_id
        self.view_id = view_id
    
    def _convert_item_to_record(self, item: NewsItem) -> Dict[str, Any]:
        """将 NewsItem 转换为飞书记录格式"""
        # 类别映射
        category_display = CATEGORY_OPTIONS.get(item.category, item.category)
        
        # 来源类型标准化
        source_type = SOURCE_TYPE_MAP.get(item.source_type, "AI社区")
        
        # 标签过滤（只保留预定义的标签）
        valid_tags = ["大模型", "AI绘画", "AI编程", "视频生成", "AI音乐", 
                      "AI搜索", "开源模型", "Agent", "新品发布", "社区热点"]
        filtered_tags = [tag for tag in item.tags if tag in valid_tags]
        
        # 转换时间戳（毫秒）
        try:
            published_at = item.published_at.replace('Z', '+00:00') if 'Z' in item.published_at else item.published_at
            timestamp_ms = int(datetime.fromisoformat(published_at).timestamp() * 1000)
        except:
            timestamp_ms = int(datetime.now().timestamp() * 1000)
        
        return {
            "标题": item.title,
            "摘要": item.summary,
            "链接": {
                "text": "阅读原文",
                "link": item.url
            },
            "来源": item.source,
            "来源类型": source_type,
            "类别": category_display,
            "标签": filtered_tags,
            "发布时间": timestamp_ms,
            "点赞数": item.likes,
            "阅读量": item.views,
            "评论数": item.comments,
        }
    
    def batch_sync(self, items: List[NewsItem]):
        """批量同步"""
        if not items:
            print("没有数据需要同步")
            return 0
        
        print(f"批量同步 {len(items)} 条记录到飞书表格...")
        print(f"App Token: {self.app_token[:10]}...")
        print(f"Table ID: {self.table_id}")
        
        # 分批处理，每批 500 条（API 限制）
        batch_size = 500
        total_success = 0
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            records = [{"fields": self._convert_item_to_record(item)} for item in batch]
            
            print(f"\n处理批次 {i//batch_size + 1}/{(len(items)-1)//batch_size + 1} ({len(batch)} 条)")
            
            # 调用 openclaw 工具批量创建
            result = self._batch_create_records(records)
            if result:
                total_success += len(batch)
                print(f"✅ 成功同步 {len(batch)} 条")
            else:
                print(f"❌ 批次失败")
        
        return total_success
    
    def _batch_create_records(self, records: List[Dict]) -> bool:
        """使用 openclaw 工具批量创建记录"""
        try:
            cmd = [
                "openclaw", "feishu_bitable_app_table_record", "batch_create",
                "--app_token", self.app_token,
                "--table_id", self.table_id,
                "--records", json.dumps(records)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return True
            else:
                print(f"API Error: {result.stderr[:500]}")
                return False
        except Exception as e:
            print(f"Command error: {e}")
            return False


def sync_to_feishu(data_path: str = None):
    """主函数：同步数据到飞书"""
    print("=" * 50)
    print("开始同步到飞书多维表格")
    print("=" * 50)
    
    # 初始化同步器
    sync = FeishuSync(
        app_token=FEISHU_CONFIG['app_token'],
        table_id=FEISHU_CONFIG['table_id'],
        view_id=FEISHU_CONFIG.get('view_id')
    )
    
    # 读取数据文件
    if data_path is None:
        data_path = os.path.join(os.path.dirname(__file__), '../web/public/data/news.json')
    
    if not os.path.exists(data_path):
        print(f"❌ 错误：数据文件不存在: {data_path}")
        print("请先运行爬虫: cd crawler && python main.py")
        return 0
    
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 转换数据
    items = []
    for item_data in data.get('items', []):
        try:
            item = NewsItem(**item_data)
            items.append(item)
        except Exception as e:
            print(f"跳过无效数据: {e}")
    
    print(f"\n读取到 {len(items)} 条有效数据")
    
    # 执行同步
    success_count = sync.batch_sync(items)
    
    print(f"\n{'=' * 50}")
    print(f"同步完成: {success_count}/{len(items)} 条成功")
    print(f"{'=' * 50}")
    
    return success_count


if __name__ == "__main__":
    # 支持命令行参数指定数据文件
    data_file = sys.argv[1] if len(sys.argv) > 1 else None
    sync_to_feishu(data_file)
