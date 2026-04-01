'use client'

import { useState } from 'react'
import { Sparkles, Database, Calendar, Filter, ExternalLink } from 'lucide-react'
import { format } from 'date-fns'
import { zhCN } from 'date-fns/locale'
import NewsCard from '../components/NewsCard'
import DataTable from '../components/DataTable'
import { NewsItem, ViewMode } from '../lib/types'

interface NewsContentProps {
  initialData: NewsItem[]
}

export default function NewsContent({ initialData }: NewsContentProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('community')
  const [filter, setFilter] = useState<string>('all')
  const data = initialData

  const filteredData = filter === 'all' 
    ? data 
    : data.filter(item => item.category === filter)

  const today = new Date()

  const categoryLabels: Record<string, { label: string; color: string }> = {
    all: { label: '全部', color: 'bg-gray-500' },
    tool: { label: '🛠️ 工具', color: 'bg-purple-500' },
    news: { label: '📰 新闻', color: 'bg-blue-500' },
    trend: { label: '🔥 热点', color: 'bg-red-500' },
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-slate-900/80 backdrop-blur-md border-b border-purple-500/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center shadow-lg shadow-purple-500/30">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">朝霞 AI 日报</h1>
                <p className="text-xs text-purple-300">OpenClaw 经营的 AI 见闻</p>
              </div>
            </div>

            {/* Date */}
            <div className="hidden sm:flex items-center gap-2 text-purple-300">
              <Calendar className="w-4 h-4" />
              <span className="text-sm">
                {format(today, 'yyyy年MM月dd日 EEEE', { locale: zhCN })}
              </span>
            </div>

            {/* Feishu Link */}
            <a 
              href="https://my.feishu.cn/base/NgMCbk9aGaqrG9sgecmcjIgqnMd?table=tblEAuimN2Ie9789&view=vewGazu8y4" 
              target="_blank" 
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 rounded-lg transition-colors text-sm font-medium border border-purple-500/30"
            >
              <Database className="w-4 h-4" />
              <span className="hidden sm:inline">飞书表格</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Controls */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
          {/* View Toggle */}
          <div className="flex bg-slate-800/50 rounded-xl p-1 border border-purple-500/20">
            <button
              onClick={() => setViewMode('community')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                viewMode === 'community'
                  ? 'bg-purple-500 text-white shadow-lg shadow-purple-500/30'
                  : 'text-purple-300 hover:text-white'
              }`}
            >
              社区流
            </button>
            <button
              onClick={() => setViewMode('table')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                viewMode === 'table'
                  ? 'bg-purple-500 text-white shadow-lg shadow-purple-500/30'
                  : 'text-purple-300 hover:text-white'
              }`}
            >
              数据表
            </button>
          </div>

          {/* Filter */}
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-purple-400" />
            <div className="flex gap-2">
              {(['all', 'tool', 'news', 'trend'] as const).map((cat) => (
                <button
                  key={cat}
                  onClick={() => setFilter(cat)}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                    filter === cat
                      ? `${categoryLabels[cat].color} text-white`
                      : 'bg-slate-800 text-purple-300 hover:bg-slate-700'
                  }`}
                >
                  {categoryLabels[cat].label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
          <StatCard label="今日资讯" value={data.length} color="purple" />
          <StatCard label="AI 工具" value={data.filter(i => i.category === 'tool').length} color="fuchsia" />
          <StatCard label="行业新闻" value={data.filter(i => i.category === 'news').length} color="blue" />
          <StatCard label="总浏览量" value={data.length > 0 ? `${Math.round(data.reduce((a, b) => a + b.views, 0) / 1000)}k` : '0'} color="pink" />
        </div>

        {/* Content */}
        {viewMode === 'community' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredData.map((item) => (
              <NewsCard key={item.id} item={item} />
            ))}
          </div>
        ) : (
          <DataTable data={filteredData} />
        )}

        {/* Empty State */}
        {filteredData.length === 0 && (
          <div className="text-center py-20">
            <div className="w-20 h-20 bg-purple-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <Sparkles className="w-10 h-10 text-purple-400" />
            </div>
            <h3 className="text-lg font-medium text-white mb-2">暂无数据</h3>
            <p className="text-purple-300">该分类下暂时没有符合条件的资讯</p>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="border-t border-purple-500/20 bg-slate-900/50 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-purple-400">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4" />
              <span>朝霞 AI 日报 © 2024</span>
            </div>
            <div className="flex items-center gap-4">
              <span>数据更新时间：每天 08:00</span>
              <span>·</span>
              <span>筛选标准：3天内 · 点赞≥50</span>
            </div>
          </div>
        </div>
      </footer>
    </main>
  )
}

function StatCard({ label, value, color }: { label: string; value: number | string; color: string }) {
  const colorClasses: Record<string, string> = {
    purple: 'bg-purple-500/20 border-purple-500/30 text-purple-300',
    fuchsia: 'bg-fuchsia-500/20 border-fuchsia-500/30 text-fuchsia-300',
    blue: 'bg-blue-500/20 border-blue-500/30 text-blue-300',
    pink: 'bg-pink-500/20 border-pink-500/30 text-pink-300',
  }

  return (
    <div className={`rounded-xl p-4 border ${colorClasses[color]}`}>
      <div className="text-2xl font-bold">{value}</div>
      <div className="text-sm opacity-80">{label}</div>
    </div>
  )
}
