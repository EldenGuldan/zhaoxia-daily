export interface NewsItem {
  id: string
  title: string
  summary: string
  url: string
  source: string
  source_type: string
  category: 'tool' | 'news' | 'trend'
  tags: string[]
  publishedAt: string
  likes: number
  views: number
  comments: number
}

export type ViewMode = 'community' | 'table'

export interface SourceConfig {
  name: string
  type: 'rss' | 'api' | 'scrape'
  url: string
  category: string
  enabled: boolean
}
