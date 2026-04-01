"""
朝霞日报 - AI 资讯采集器
数据源：AI 工具官网、AI 社区、科技媒体、社交媒体
过滤：3天内 + 点赞/阅读量 > 50
"""

import os
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
import feedparser
from bs4 import BeautifulSoup


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
    engagement: int


class QualityFilter:
    """质量过滤器：3天内 + 互动量 > 50"""
    
    def __init__(self, min_engagement: int = 50, max_age_days: int = 3):
        self.min_engagement = min_engagement
        self.max_age_days = max_age_days
    
    def is_valid(self, item: NewsItem) -> bool:
        # 检查互动量
        if item.engagement < self.min_engagement:
            return False
        
        # 检查时间
        try:
            pub_date = datetime.fromisoformat(item.published_at.replace('Z', '+00:00'))
            cutoff = datetime.now(pub_date.tzinfo) - timedelta(days=self.max_age_days)
            if pub_date < cutoff:
                return False
        except:
            return False
        
        return True


# ============ AI 数据源配置 ============

AI_TOOLS_SOURCES = [
    # AI 绘画
    {"name": "Midjourney", "url": "https://www.midjourney.com", "category": "tool", "tags": ["AI绘画"]},
    {"name": "Stable Diffusion", "url": "https://stability.ai", "category": "tool", "tags": ["AI绘画", "开源"]},
    {"name": "DALL-E", "url": "https://openai.com/dall-e-3", "category": "tool", "tags": ["AI绘画", "OpenAI"]},
    
    # AI 对话/大模型
    {"name": "ChatGPT", "url": "https://openai.com/blog", "category": "tool", "tags": ["大模型", "对话"]},
    {"name": "Claude", "url": "https://www.anthropic.com/news", "category": "tool", "tags": ["大模型", "对话"]},
    {"name": "Gemini", "url": "https://blog.google/technology/ai/", "category": "tool", "tags": ["大模型", "Google"]},
    {"name": "通义千问", "url": "https://qwenlm.github.io", "category": "tool", "tags": ["大模型", "阿里", "开源"]},
    {"name": "文心一言", "url": "https://yiyan.baidu.com", "category": "tool", "tags": ["大模型", "百度"]},
    {"name": "智谱AI", "url": "https://chatglm.cn", "category": "tool", "tags": ["大模型", "智谱"]},
    
    # AI 编程
    {"name": "GitHub Copilot", "url": "https://github.blog", "category": "tool", "tags": ["AI编程"]},
    {"name": "Cursor", "url": "https://cursor.sh/blog", "category": "tool", "tags": ["AI编程", "编辑器"]},
    {"name": "Codeium", "url": "https://codeium.com/blog", "category": "tool", "tags": ["AI编程"]},
    
    # AI 视频
    {"name": "Runway", "url": "https://runwayml.com/blog", "category": "tool", "tags": ["视频生成"]},
    {"name": "Pika", "url": "https://pika.art", "category": "tool", "tags": ["视频生成"]},
    {"name": "Sora", "url": "https://openai.com/sora", "category": "tool", "tags": ["视频生成", "OpenAI"]},
    
    # AI 音乐/音频
    {"name": "Suno", "url": "https://www.suno.ai", "category": "tool", "tags": ["AI音乐"]},
    {"name": "Udio", "url": "https://www.udio.com", "category": "tool", "tags": ["AI音乐"]},
    {"name": "ElevenLabs", "url": "https://elevenlabs.io", "category": "tool", "tags": ["AI语音"]},
    
    # AI 搜索/知识
    {"name": "Perplexity", "url": "https://www.perplexity.ai", "category": "tool", "tags": ["AI搜索", "知识管理"]},
    {"name": "Devv", "url": "https://devv.ai", "category": "tool", "tags": ["AI搜索", "开发者"]},
    
    # AI 应用构建
    {"name": "Coze", "url": "https://www.coze.com", "category": "tool", "tags": ["Agent", "Bot"]},
    {"name": "Dify", "url": "https://dify.ai", "category": "tool", "tags": ["LLM应用", "开源"]},
    {"name": "Flowise", "url": "https://flowiseai.com", "category": "tool", "tags": ["LLM应用", "开源"]},
]

AI_NEWS_SOURCES = [
    # 中文科技媒体
    {"name": "36氪 AI", "rss": "https://36kr.com/feed", "category": "news", "tags": ["AI新闻"]},
    {"name": "机器之心", "rss": "https://www.jiqizhixin.com/rss", "category": "news", "tags": ["AI媒体"]},
    {"name": "量子位", "rss": "https://www.qbitai.com/rss", "category": "news", "tags": ["AI媒体"]},
    
    # 英文科技媒体
    {"name": "TechCrunch AI", "rss": "https://techcrunch.com/category/artificial-intelligence/feed/", "category": "news", "tags": ["AI新闻"]},
    {"name": "The Verge AI", "rss": "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml", "category": "news", "tags": ["AI新闻"]},
    {"name": "VentureBeat AI", "rss": "https://venturebeat.com/category/ai/feed/", "category": "news", "tags": ["AI新闻"]},
]

AI_COMMUNITIES = [
    {"name": "WaytoAGI", "url": "https://waytoagi.com", "category": "news", "tags": ["AI社区"]},
    {"name": "Hugging Face", "url": "https://huggingface.co", "category": "news", "tags": ["开源社区"]},
    {"name": "Reddit r/LocalLLaMA", "url": "https://www.reddit.com/r/LocalLLaMA", "category": "trend", "tags": ["开源模型", "社区热点"]},
    {"name": "Reddit r/MachineLearning", "url": "https://www.reddit.com/r/MachineLearning", "category": "news", "tags": ["机器学习"]},
    {"name": "Product Hunt", "url": "https://www.producthunt.com", "category": "tool", "tags": ["AI产品", "新品发布"]},
]


class WaytoAGICrawler:
    """WaytoAGI 社区热门采集"""
    
    API_URL = "https://waytoagi.com/api/feed"
    
    async def fetch(self, session: aiohttp.ClientSession) -> List[NewsItem]:
        items = []
        
        try:
            async with session.get(self.API_URL, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for post in data.get('posts', []):
                        likes = post.get('likes', 0)
                        views = post.get('views', 0)
                        comments = post.get('comments', 0)
                        engagement = likes + comments
                        
                        # 质量过滤
                        if engagement < 50:
                            continue
                        
                        item = NewsItem(
                            id=f"waytoagi_{post.get('id')}",
                            title=post.get('title', ''),
                            summary=post.get('summary', '')[:200],
                            url=post.get('url', ''),
                            source="WaytoAGI",
                            source_type="AI社区",
                            category="trend" if engagement > 200 else "news",
                            tags=["AI社区"] + post.get('tags', []),
                            published_at=post.get('created_at', datetime.now().isoformat()),
                            likes=likes,
                            views=views,
                            comments=comments,
                            engagement=engagement
                        )
                        items.append(item)
        except Exception as e:
            print(f"WaytoAGI fetch error: {e}")
        
        return items


class HuggingFaceCrawler:
    """Hugging Face 热门模型/项目采集"""
    
    TRENDING_URL = "https://huggingface.co/api/trending"
    
    async def fetch(self, session: aiohttp.ClientSession) -> List[NewsItem]:
        items = []
        
        try:
            async with session.get(self.TRENDING_URL, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for model in data.get('items', [])[:10]:
                        # HF 没有直接的点赞数据，用 downloads 估算
                        downloads = model.get('downloads', 0)
                        likes = model.get('likes', 0)
                        engagement = likes + downloads // 100
                        
                        if engagement < 50:
                            continue
                        
                        item = NewsItem(
                            id=f"hf_{model.get('id', '').replace('/', '_')}",
                            title=f"🤗 {model.get('modelId', '')}",
                            summary=model.get('description', '暂无描述')[:200],
                            url=f"https://huggingface.co/{model.get('modelId')}",
                            source="Hugging Face",
                            source_type="开源社区",
                            category="tool",
                            tags=["开源模型", "Hugging Face"] + model.get('tags', []),
                            published_at=datetime.now().isoformat(),
                            likes=likes,
                            views=downloads,
                            comments=0,
                            engagement=engagement
                        )
                        items.append(item)
        except Exception as e:
            print(f"HuggingFace fetch error: {e}")
        
        return items


class ProductHuntCrawler:
    """Product Hunt 热门 AI 产品采集"""
    
    API_URL = "https://www.producthunt.com/feed"
    
    async def fetch(self, session: aiohttp.ClientSession) -> List[NewsItem]:
        items = []
        
        try:
            async with session.get(self.API_URL, timeout=10) as resp:
                content = await resp.text()
                feed = feedparser.parse(content)
                
                for entry in feed.entries[:15]:
                    # 只保留 AI 相关产品
                    title_lower = entry.title.lower()
                    summary_lower = entry.get('summary', '').lower()
                    if not any(kw in title_lower or kw in summary_lower for kw in 
                              ['ai', 'gpt', 'llm', 'machine learning', 'neural', 'openai', 'claude']):
                        continue
                    
                    # 获取正确的链接 - 使用 entry.id 通常是完整帖子链接
                    # 或者从链接中提取 slug 构建正确链接
                    url = entry.get('id', entry.link)
                    # 如果 id 不是 URL，使用 link 并转换为 posts 链接
                    if not url.startswith('http'):
                        # 从 link 中提取产品名构建帖子链接
                        url = entry.link
                        # Product Hunt 的链接通常是 /products/{name}，需要改为 /posts/{name}
                        if '/products/' in url:
                            url = url.replace('/products/', '/posts/')
                    
                    # 从 summary 中提取实际的产品 URL（如果有）
                    soup = BeautifulSoup(entry.get('summary', ''), 'html.parser')
                    links = soup.find_all('a')
                    product_url = None
                    for link in links:
                        href = link.get('href', '')
                        if 'utm_campaign=producthunt' in href or '/products/' in href:
                            product_url = href
                            break
                    
                    # 使用找到的直接链接，否则使用 RSS 链接
                    final_url = product_url if product_url else url
                    
                    item = NewsItem(
                        id=f"ph_{hash(entry.link) % 10000000000}",
                        title=entry.title,
                        summary=entry.get('summary', '')[:200],
                        url=final_url,
                        source="Product Hunt",
                        source_type="产品发布",
                        category="tool",
                        tags=["AI产品", "新品"],
                        published_at=datetime.now().isoformat(),
                        likes=100,
                        views=1000,
                        comments=20,
                        engagement=120
                    )
                    items.append(item)
        except Exception as e:
            print(f"ProductHunt fetch error: {e}")
        
        return items


class XWebScraper:
    """X (Twitter) AI 话题采集 - 需要 API Key"""
    
    def __init__(self, bearer_token: str = None):
        self.bearer_token = bearer_token or os.getenv('X_BEARER_TOKEN')
    
    async def fetch(self, session: aiohttp.ClientSession) -> List[NewsItem]:
        items = []
        
        if not self.bearer_token:
            print("X_BEARER_TOKEN not set, skipping X/Twitter")
            return items
        
        # AI 热门话题关键词
        keywords = [
            "Claude 3.5", "GPT-5", "Sora", "Midjourney", "Stable Diffusion",
            "AI编程", "AI绘画", "大模型", "开源模型", "AI视频"
        ]
        
        headers = {
            "Authorization": f"Bearer {self.bearer_token}"
        }
        
        for keyword in keywords:
            try:
                url = f"https://api.twitter.com/2/tweets/search/recent?query={keyword}&tweet.fields=public_metrics,created_at&max_results=10"
                async with session.get(url, headers=headers, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for tweet in data.get('data', []):
                            metrics = tweet.get('public_metrics', {})
                            likes = metrics.get('like_count', 0)
                            
                            # 只保留高互动推文
                            if likes < 50:
                                continue
                            
                            # 判断类别
                            category = "trend" if likes > 500 else "news"
                            
                            item = NewsItem(
                                id=f"x_{tweet['id']}",
                                title=tweet.get('text', '')[:100],
                                summary=tweet.get('text', ''),
                                url=f"https://x.com/i/web/status/{tweet['id']}",
                                source="X",
                                source_type="社交媒体",
                                category=category,
                                tags=["社交媒体", keyword],
                                published_at=tweet.get('created_at', datetime.now().isoformat()),
                                likes=likes,
                                views=metrics.get('impression_count', 0),
                                comments=metrics.get('reply_count', 0),
                                engagement=likes + metrics.get('retweet_count', 0)
                            )
                            items.append(item)
            except Exception as e:
                print(f"X fetch error {keyword}: {e}")
                continue
        
        return items


class NewsAggregator:
    """AI 资讯聚合器"""
    
    def __init__(self):
        self.crawlers = [
            WaytoAGICrawler(),
            HuggingFaceCrawler(),
            ProductHuntCrawler(),
            XWebScraper(),
        ]
        self.filter = QualityFilter(min_engagement=50, max_age_days=3)
    
    async def collect(self) -> List[NewsItem]:
        """采集所有源的数据"""
        all_items = []
        
        async with aiohttp.ClientSession() as session:
            tasks = [crawler.fetch(session) for crawler in self.crawlers]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, list):
                    all_items.extend(result)
                else:
                    print(f"Crawler error: {result}")
        
        # 应用质量过滤
        valid_items = [item for item in all_items if self.filter.is_valid(item)]
        
        # 去重
        seen_urls = set()
        unique_items = []
        for item in valid_items:
            if item.url not in seen_urls:
                seen_urls.add(item.url)
                unique_items.append(item)
        
        # 按互动量排序
        unique_items.sort(key=lambda x: x.engagement, reverse=True)
        
        return unique_items
    
    def save(self, items: List[NewsItem], output_path: str):
        """保存到 JSON 文件"""
        data = {
            "updated_at": datetime.now().isoformat(),
            "count": len(items),
            "items": [asdict(item) for item in items]
        }
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"Saved {len(items)} AI items to {output_path}")
        
        # 打印分类统计
        tools = len([i for i in items if i.category == 'tool'])
        news = len([i for i in items if i.category == 'news'])
        trends = len([i for i in items if i.category == 'trend'])
        print(f"  - AI工具: {tools}")
        print(f"  - 行业新闻: {news}")
        print(f"  - 热点话题: {trends}")


async def main():
    """主函数"""
    aggregator = NewsAggregator()
    items = await aggregator.collect()
    
    output_path = os.path.join(os.path.dirname(__file__), '../web/public/data/news.json')
    aggregator.save(items, output_path)
    
    return items


if __name__ == "__main__":
    asyncio.run(main())
