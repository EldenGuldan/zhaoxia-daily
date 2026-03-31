# 朝霞 AI 日报 (Zhaoxia AI Daily)

> OpenClaw 经营的 AI 见闻资讯站

由小龙虾自动运营的每日精选 AI 领域高质量资讯——**工具**、**新闻**、**热点**。

## 筛选标准

- **时效性**：3 天内发布的内容
- **质量门槛**：点赞/评论/转发总和 > 50
- **去重机制**：同一 URL 仅保留一条

## 内容分类

| 分类 | 说明 | 示例 |
|------|------|------|
| 🛠️ **AI 工具** | 新发布的 AI 产品、工具更新 | Claude 3.5、Midjourney V7 |
| 📰 **行业新闻** | 公司动态、融资、政策 | OpenAI 训练 GPT-5、Cursor 融资 |
| 🔥 **热点话题** | 社交媒体热门讨论 | Sora 安全漏洞、Copilot 涨价 |

## 数据源

| 来源 | 类型 | 内容 |
|------|------|------|
| WaytoAGI | AI 社区 | 中文 AI 社区热门讨论 |
| Hugging Face | 开源社区 | 热门开源模型 |
| Product Hunt | 产品发布 | 新发布的 AI 产品 |
| X/Twitter | 社交媒体 | AI 话题热门推文 |

## 项目结构

```
zhaoxia-daily/
├── web/              # Next.js 前端 (部署到 Vercel)
│   ├── app/          # App Router
│   ├── components/   # React 组件
│   ├── lib/          # 类型定义和工具
│   └── public/data/  # 静态数据文件
├── crawler/          # Python 数据采集器
│   ├── main.py       # 主爬虫脚本
│   └── requirements.txt
├── sync/             # 飞书同步
│   ├── feishu_sync.py
│   └── config.py
└── .github/workflows/# GitHub Actions 自动更新
```

## 快速部署

### 1. GitHub + Vercel（推荐）

```bash
# 1. Fork 本项目

# 2. 推送到你的 GitHub
cd zhaoxia-daily
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/zhaoxia-daily.git
git push -u origin main

# 3. 在 Vercel 导入项目
# 访问 https://vercel.com/new，选择 GitHub 仓库导入
```

### 2. 配置自动更新

在 GitHub 仓库设置中添加 Secrets（可选）：
- `X_BEARER_TOKEN`: X/Twitter API Token

GitHub Actions 会每天自动运行爬虫并更新数据。

## 飞书表格同步

创建多维表格，字段如下：

| 字段 | 类型 | 说明 |
|------|------|------|
| 标题 | 文本 | |
| 摘要 | 文本 | |
| 链接 | 超链接 | |
| 来源 | 文本 | |
| 来源类型 | 单选 | 官方博客/开源社区/产品发布/社交媒体/科技媒体/AI社区 |
| 类别 | 单选 | 🛠️ AI工具 / 📰 行业新闻 / 🔥 热点话题 |
| 标签 | 多选 | 大模型/AI绘画/AI编程/视频生成/... |
| 发布时间 | 日期 | |
| 点赞数 | 数字 | |
| 阅读量 | 数字 | |
| 评论数 | 数字 | |
| 互动量 | 数字 | |

详见 `docs/FEISHU_SETUP.md`

## 技术栈

- **前端**: Next.js 14 + TypeScript + Tailwind CSS
- **部署**: Vercel
- **爬虫**: Python + aiohttp
- **数据**: JSON 静态文件 / 飞书多维表格

## 自定义配置

编辑 `crawler/main.py` 添加数据源：

```python
AI_TOOLS_SOURCES = [
    {"name": "你的工具", "url": "https://example.com", "category": "tool", "tags": ["标签"]},
]
```

## License

MIT
