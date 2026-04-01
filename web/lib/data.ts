import { NewsItem } from './types'

// 在构建时静态导入数据
let newsData: NewsItem[] = []

try {
  // 尝试动态导入数据文件
  const data = require('../public/data/news.json')
  newsData = data.items || []
} catch (e) {
  // 如果文件不存在，使用空数组
  newsData = []
}

export function getNewsData(): NewsItem[] {
  return newsData
}

export function getNewsById(id: string): NewsItem | undefined {
  return newsData.find(item => item.id === id)
}

export function getNewsByCategory(category: string): NewsItem[] {
  if (category === 'all') return newsData
  return newsData.filter(item => item.category === category)
}
