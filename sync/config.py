# 飞书同步配置

FEISHU_CONFIG = {
    "app_token": "YOUR_APP_TOKEN_HERE",
    "table_id": "YOUR_TABLE_ID_HERE",
    "view_id": None,
}

# 字段映射
FIELD_MAPPING = {
    "标题": "title",
    "摘要": "summary",
    "链接": "url",
    "来源": "source",
    "来源类型": "source_type",
    "类别": "category",
    "标签": "tags",
    "发布时间": "published_at",
    "点赞数": "likes",
    "阅读量": "views",
    "评论数": "comments",
    "互动量": "engagement",
}

# 类别选项映射
CATEGORY_OPTIONS = {
    "tool": "🛠️ AI工具",
    "news": "📰 行业新闻",
    "trend": "🔥 热点话题",
}
