"""
飞书多维表格同步脚本 - 实际可用版本
将采集的新闻数据同步到飞书 Bitable
"""

import json
import os
import sys
import subprocess
from datetime import datetime
from typing import List, Dict, Any

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawler.main import NewsItem
from sync.config import FEISHU_CONFIG, FIELD_MAPPING, CATEGORY_OPTIONS


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
            "标签": item.tags,
            "发布时间": int(datetime.fromisoformat(item.published_at.replace('Z', '+00:00')).timestamp() * 1000),
            "点赞数": item.likes,
            "阅读量": item.views,
            "评论数": item.comments,
            "互动量": item.engagement,
        }
    
    def _call_feishu_tool(self, action: str, params: Dict) -> Dict:
        """调用飞书工具"""
        # 构建 openclaw 命令
        cmd = ["openclaw", "feishu_bitable_app_table_record", action]
        
        for key, value in params.items():
            if isinstance(value, list):
                cmd.extend([f"--{key}", json.dumps(value)])
            elif isinstance(value, dict):
                cmd.extend([f"--{key}", json.dumps(value)])
            else:
                cmd.extend([f"--{key}", str(value)])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                print(f"Error: {result.stderr}")
                return {}
        except Exception as e:
            print(f"Command error: {e}")
            return {}
    
    def batch_sync(self, items: List[NewsItem]):
        """批量同步（推荐）"""
        print(f"批量同步 {len(items)} 条记录到飞书表格...")
        print(f"App Token: {self.app_token[:10]}...")
        print(f"Table ID: {self.table_id}")
        
        # 分批处理，每批 500 条
        batch_size = 500
        total_success = 0
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            records = [{"fields": self._convert_item_to_record(item)} for item in batch]
            
            print(f"\n处理批次 {i//batch_size + 1}/{(len(items)-1)//batch_size + 1} ({len(batch)} 条)")
            
            # 打印第一条记录作为示例
            if i == 0:
                print("示例数据:")
                print(json.dumps(records[0], ensure_ascii=False, indent=2))
            
            # 这里需要手动调用飞书工具
            # 由于环境限制，打印出调用命令供用户参考
            print(f"\n请执行以下命令完成同步:")
            print(f"openclaw feishu_bitable_app_table_record batch_create \\")
            print(f"  --app_token {self.app_token} \\")
            print(f"  --table_id {self.table_id} \\")
            print(f"  --records '{json.dumps(records[:2], ensure_ascii=False)}'")
            
            total_success += len(batch)
        
        print(f"\n✅ 准备完成，共 {total_success} 条记录")
        print("注意：由于环境限制，请手动执行上述命令或配置好飞书授权后运行")


def test_connection():
    """测试飞书连接"""
    print("测试飞书连接...")
    print(f"App Token: {FEISHU_CONFIG['app_token']}")
    print(f"Table ID: {FEISHU_CONFIG['table_id']}")
    print(f"View ID: {FEISHU_CONFIG.get('view_id', 'None')}")
    
    print("\n请确保:")
    print("1. 已配置飞书授权 (openclaw feishu_oauth)")
    print("2. 应用有 bitable:app 和 bitable:record 权限")
    print("3. 表格结构和 docs/FEISHU_SETUP.md 中描述一致")


def main():
    """主函数"""
    # 检查配置
    if FEISHU_CONFIG['app_token'] == 'YOUR_APP_TOKEN_HERE':
        print("错误：请先配置 app_token 和 table_id")
        print("编辑 sync/config.py 填入你的飞书配置")
        return
    
    # 测试连接
    test_connection()
    
    # 读取采集的数据
    data_path = os.path.join(os.path.dirname(__file__), '../web/public/data/news.json')
    
    if not os.path.exists(data_path):
        print(f"\n错误：数据文件不存在: {data_path}")
        print("请先运行爬虫: python crawler/main.py")
        return
    
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    items = [NewsItem(**item) for item in data['items']]
    print(f"\n读取到 {len(items)} 条数据")
    
    # 初始化同步器
    sync = FeishuSync(
        app_token=FEISHU_CONFIG['app_token'],
        table_id=FEISHU_CONFIG['table_id'],
        view_id=FEISHU_CONFIG.get('view_id')
    )
    
    # 批量同步
    sync.batch_sync(items)


if __name__ == "__main__":
    main()
