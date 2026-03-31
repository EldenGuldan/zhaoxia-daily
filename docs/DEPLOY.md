# 快速部署指南

## 1. Vercel 一键部署

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/zhaoxia-daily)

或者手动部署：

```bash
# 安装 Vercel CLI
npm i -g vercel

# 进入项目目录
cd zhaoxia-daily/web

# 登录 Vercel
vercel login

# 部署
vercel --prod
```

## 2. 配置自定义域名（可选）

在 Vercel Dashboard 中：
1. 进入项目设置
2. 点击「Domains」
3. 添加你的域名

## 3. 配置自动更新

### 方式一：GitHub Actions（推荐）

1. Fork 本项目到你的 GitHub 账号
2. 在仓库设置中添加 Secrets：
   - `X_BEARER_TOKEN`: 你的 X/Twitter API Token（可选）
3. GitHub Actions 会自动每天运行爬虫并更新数据

### 方式二：本地定时任务

```bash
# 编辑 crontab
crontab -e

# 添加定时任务（每天 8:30）
30 8 * * * cd /path/to/zhaoxia-daily && /usr/bin/python3 crawler/main.py >> /var/log/zhaoxia.log 2>&1
```

## 4. 配置飞书表格（可选）

1. 按照 `docs/FEISHU_SETUP.md` 创建多维表格
2. 复制 `app_token` 和 `table_id` 到 `sync/config.py`
3. 运行同步脚本

## 5. 自定义配置

编辑 `crawler/main.py` 添加/修改数据源：

```python
# 添加新的 RSS 源
RSS_SOURCES = [
    {"name": "你的来源", "url": "https://example.com/feed", "category": "tech"},
]
```

## 6. 更新网站内容

网站使用 `web/public/data/news.json` 作为数据源：

- 手动更新：运行 `python crawler/main.py`
- 自动更新：配置 GitHub Actions 后自动执行

更新后 Vercel 会自动重新部署（约 1-2 分钟）。

## 常见问题

### Q: 部署后没有数据显示？
A: 确保 `web/public/data/news.json` 文件存在且有内容。首次部署需要手动运行爬虫或等待定时任务执行。

### Q: 如何修改筛选标准？
A: 编辑 `crawler/main.py` 中的 `QualityFilter` 类：
```python
self.filter = QualityFilter(min_engagement=50, max_age_days=3)
```

### Q: 可以添加更多数据源吗？
A: 可以。继承 `BaseCrawler` 类并实现 `fetch` 方法即可。

## 项目文件结构

```
zhaoxia-daily/
├── web/                    # 前端代码
│   ├── app/               # Next.js 页面
│   ├── components/        # React 组件
│   ├── lib/               # 工具函数
│   └── public/data/       # 数据文件
├── crawler/               # 爬虫代码
│   ├── main.py            # 主程序
│   └── requirements.txt   # Python 依赖
├── sync/                  # 飞书同步
│   ├── feishu_sync.py
│   └── config.py
└── .github/workflows/     # GitHub Actions
    └── daily-update.yml
```

## 技术栈

- **前端**: Next.js 14 + React + TypeScript + Tailwind CSS
- **部署**: Vercel
- **爬虫**: Python + aiohttp + BeautifulSoup
- **数据存储**: JSON 静态文件 / 飞书多维表格

## 需要帮忙？

有问题可以查看：
- `README.md` - 详细文档
- `docs/FEISHU_SETUP.md` - 飞书配置指南
