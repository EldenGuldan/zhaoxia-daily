"""
朝霞日报 - AI 资讯 RSS 订阅采集器
使用 RSS 订阅获取新闻，而非网页爬虫
"""

import os
import json
import asyncio
import aiohttp
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class NewsItem:
    id: str
    title: str
    summary: str
    url: str
    source: str
    source_type: str
    category: str  # 'tool' | 'news' | 'trend'
    tags: List[str]
    published_at: str
    likes: int
    views: int
    comments: int


class QualityFilter:
    """质量过滤器"""
    
    def __init__(self, min_engagement: int = 10, max_age_days: int = 7):
        self.min_engagement = min_engagement
        self.max_age_days = max_age_days
    
    def is_valid(self, item: NewsItem) -> bool:
        try:
            pub_date = datetime.fromisoformat(item.published_at.replace('Z', '+00:00').replace('+00:00', ''))
            cutoff = datetime.now() - timedelta(days=self.max_age_days)
            if pub_date < cutoff:
                return False
        except:
            pass
        return True


# ============ RSS 订阅源配置 ============

RSS_SOURCES = [
    # AI 研究论文
    {
        "name": "arXiv AI",
        "url": "http://export.arxiv.org/api/query?search_query=cat:cs.AI+OR+cat:cs.CL+OR+cat:cs.LG&sortBy=submittedDate&sortOrder=descending&max_results=10",
        "category": "news",
        "source_type": "学术论文",
        "tags": ["AI论文", "研究"]
    },
    # 中文 AI 媒体
    {
        "name": "机器之心",
        "url": "https://www.jiqizhixin.com/rss",
        "category": "news",
        "source_type": "中文媒体",
        "tags": ["AI新闻", "中文"]
    },
    {
        "name": "量子位",
        "url": "https://www.qbitai.com/feed",
        "category": "news",
        "source_type": "中文媒体",
        "tags": ["AI新闻", "中文"]
    },
    # 国际科技媒体
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "category": "news",
        "source_type": "科技媒体",
        "tags": ["AI新闻", "科技"]
    },
    {
        "name": "MIT Technology Review",
        "url": "https://www.technologyreview.com/feed/",
        "category": "news",
        "source_type": "科技媒体",
        "tags": ["科技", "研究"]
    },
    {
        "name": "Wired AI",
        "url": "https://www.wired.com/tag/artificial-intelligence/feed/",
        "category": "news",
        "source_type": "科技媒体",
        "tags": ["AI新闻", "科技趋势"]
    },
    {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/category/ai/feed/",
        "category": "news",
        "source_type": "科技媒体",
        "tags": ["AI新闻", "创投"]
    },
    # AI 公司官方博客
    {
        "name": "OpenAI Blog",
        "url": "https://openai.com/blog/rss.xml",
        "category": "news",
        "source_type": "官方博客",
        "tags": ["OpenAI", "大模型"]
    },
    {
        "name": "Google AI Blog",
        "url": "http://ai.googleblog.com/feeds/posts/default",
        "category": "news",
        "source_type": "官方博客",
        "tags": ["Google", "AI研究"]
    },
    {
        "name": "Anthropic News",
        "url": "https://www.anthropic.com/news/rss.xml",
        "category": "news",
        "source_type": "官方博客",
        "tags": ["Claude", "Anthropic"]
    },
    # 开发者社区
    {
        "name": "Hacker News",
        "url": "https://hnrss.org/newest?q=ai+OR+llm+OR+openai+OR+claude",
        "category": "trend",
        "source_type": "开发者社区",
        "tags": ["开发者", "技术"]
    },
    {
        "name": "Dev.to AI",
        "url": "https://dev.to/feed/tag/ai",
        "category": "news",
        "source_type": "开发者社区",
        "tags": ["开发者", "AI应用"]
    },
    # Product Hunt (少量)
    {
        "name": "Product Hunt",
        "url": "https://www.producthunt.com/feed",
        "category": "tool",
        "source_type": "产品发布",
        "tags": ["AI产品"]
    },
]


class RSSCrawler:
    """通用 RSS 订阅采集器"""
    
    async def fetch_source(self, session: aiohttp.ClientSession, source: Dict) -> List[NewsItem]:
        """获取单个 RSS 源"""
        items = []
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; ZhaoxiaDaily/1.0)"
            }
            async with session.get(source["url"], headers=headers, timeout=15) as resp:
                if resp.status == 200:
                    content = await resp.text()
                    feed = feedparser.parse(content)
                    
                    for entry in feed.entries[:8]:  # 每个源取前8条
                        # 提取摘要
                        summary = entry.get('summary', entry.get('description', ''))
                        # 清理 HTML 标签
                        import re
                        clean_summary = re.sub(r'<[^>]+>', '', summary)[:200]
                        
                        # 判断是否是 AI 相关内容
                        title_lower = entry.title.lower()
                        summary_lower = clean_summary.lower()
                        if not any(kw in title_lower or kw in summary_lower for kw in 
                                  ['ai', 'artificial intelligence', 'machine learning', 'llm', 'gpt', 
                                   'neural', 'deep learning', 'chatgpt', 'claude', 'openai', 'model']):
                            continue
                        
                        # 生成 ID
                        entry_id = entry.get('id', entry.get('link', ''))
                        item_id = f"rss_{hash(entry_id) % 10000000000}"
                        
                        # 发布时间
                        pub_date = entry.get('published', datetime.now().isoformat())
                        
                        item = NewsItem(
                            id=item_id,
                            title=entry.title,
                            summary=clean_summary or entry.title,
                            url=entry.link,
                            source=source["name"],
                            source_type=source["source_type"],
                            category=source["category"],
                            tags=source["tags"],
                            published_at=pub_date,
                            likes=50,
                            views=500,
                            comments=10
                        )
                        items.append(item)
                        
        except Exception as e:
            print(f"{source['name']} RSS error: {e}")
        
        return items


class NewsAggregator:
    """新闻聚合器"""
    
    def __init__(self):
        self.rss_crawler = RSSCrawler()
        self.filter = QualityFilter(min_engagement=10, max_age_days=7)
    
    async def collect(self) -> List[NewsItem]:
        """采集所有 RSS 源"""
        all_items = []
        
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.rss_crawler.fetch_source(session, source) 
                for source in RSS_SOURCES
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, list):
                    all_items.extend(result)
                else:
                    print(f"RSS error: {result}")
        
        # 应用时间过滤
        valid_items = [item for item in all_items if self.filter.is_valid(item)]
        
        # 去重
        seen_urls = set()
        unique_items = []
        for item in valid_items:
            if item.url not in seen_urls:
                seen_urls.add(item.url)
                unique_items.append(item)
        
        # 按浏览量排序，取前20条
        unique_items.sort(key=lambda x: x.views, reverse=True)
        
        return unique_items[:20]  # 只保留20条浏览量最多的
    
    def save(self, items: List[NewsItem], output_path: str):
        """保存到 JSON"""
        data = {
            "updated_at": datetime.now().isoformat(),
            "count": len(items),
            "items": [asdict(item) for item in items]
        }
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"Saved {len(items)} items to {output_path}")
        
        # 统计
        sources = {}
        for item in items:
            src = item.source
            sources[src] = sources.get(src, 0) + 1
        print("Source distribution:")
        for src, count in sorted(sources.items(), key=lambda x: -x[1]):
            print(f"  - {src}: {count}")


async def main():
    aggregator = NewsAggregator()
    items = await aggregator.collect()
    
    output_path = os.path.join(os.path.dirname(__file__), '../web/public/data/news.json')
    aggregator.save(items, output_path)
    return items


if __name__ == "__main__":
    asyncio.run(main())
