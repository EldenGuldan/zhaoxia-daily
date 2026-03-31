"""
飞书多维表格同步脚本
将采集的新闻数据同步到飞书 Bitable
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawler.main import NewsItem
from sync.config import FEISHU_CONFIG, FIELD_MAPPING, CATEGORY_OPTIONS


class FeishuSync:
    """飞书表格同步器"""
    
    def __init__(self, app_token: str, table_id: str):
        self.app_token = app_token
        self.table_id = table_id
    
    def _convert_item_to_record(self, item: NewsItem) -> Dict[str, Any]:
        """将 NewsItem 转换为飞书记录格式"""
        # 类别映射
        category_display = CATEGORY_OPTIONS.get(item.category, item.category)
        
        return {
            "标题": item.title,
            "摘要": item.summary,
            "链接": {
                "text": "阅读原文",
                "link": item.url
            },
            "来源": item.source,
            "来源类型": item.source_type,
            "类别": category_display,
            "发布时间": int(datetime.fromisoformat(item.published_at.replace('Z', '+00:00')).timestamp() * 1000),
            "点赞数": item.likes,
            "阅读量": item.views,
            "评论数": item.comments,
            "互动量": item.engagement,
        }
    
    def sync(self, items: List[NewsItem]):
        """同步数据到飞书表格"""
        print(f"准备同步 {len(items)} 条记录到飞书表格...")
        
        # 这里调用飞书 API 进行同步
        # 由于需要用户授权，这里提供伪代码模板
        
        for item in items:
            record = self._convert_item_to_record(item)
            print(f"同步: {item.title[:30]}...")
            # TODO: 调用 feishu_bitable_app_table_record.create 或 batch_create
        
        print("同步完成！")
    
    def batch_sync(self, items: List[NewsItem]):
        """批量同步（推荐）"""
        print(f"批量同步 {len(items)} 条记录...")
        
        # 分批处理，每批 500 条
        batch_size = 500
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            records = [self._convert_item_to_record(item) for item in batch]
            
            # TODO: 调用 feishu_bitable_app_table_record.batch_create
            print(f"已处理批次 {i//batch_size + 1}/{(len(items)-1)//batch_size + 1}")


def main():
    """主函数"""
    # 读取采集的数据
    data_path = os.path.join(os.path.dirname(__file__), '../web/public/data/news.json')
    
    if not os.path.exists(data_path):
        print(f"数据文件不存在: {data_path}")
        print("请先运行爬虫: python crawler/main.py")
        return
    
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    items = [NewsItem(**item) for item in data['items']]
    
    # 初始化同步器
    sync = FeishuSync(
        app_token=FEISHU_CONFIG['app_token'],
        table_id=FEISHU_CONFIG['table_id']
    )
    
    # 批量同步
    sync.batch_sync(items)


if __name__ == "__main__":
    main()
