import { NewsItem } from '../lib/types'
import { format } from 'date-fns'
import { zhCN } from 'date-fns/locale'
import { ExternalLink, ThumbsUp, Eye, MessageCircle, Tag } from 'lucide-react'

interface NewsCardProps {
  item: NewsItem
}

export default function NewsCard({ item }: NewsCardProps) {
  const categoryConfig: Record<string, { label: string; className: string; icon: string }> = {
    tool: { 
      label: '🛠️ AI 工具', 
      className: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
      icon: '🛠️'
    },
    news: { 
      label: '📰 行业新闻', 
      className: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
      icon: '📰'
    },
    trend: { 
      label: '🔥 热点话题', 
      className: 'bg-red-500/20 text-red-300 border-red-500/30',
      icon: '🔥'
    },
  }

  const config = categoryConfig[item.category]

  return (
    <article className="group bg-slate-800/50 rounded-2xl border border-purple-500/20 overflow-hidden hover:border-purple-500/50 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-purple-500/10">
      <div className="p-5">
        {/* Header */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border ${config.className}`}>
            {config.label}
          </span>
          <span className="text-xs text-slate-400 flex-shrink-0">
            {format(new Date(item.publishedAt), 'MM-dd HH:mm', { locale: zhCN })}
          </span>
        </div>

        {/* Title */}
        <h3 className="font-semibold text-white mb-2 line-clamp-2 leading-snug group-hover:text-purple-300 transition-colors">
          {item.title}
        </h3>

        {/* Tags */}
        {item.tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-3">
            {item.tags.map((tag, idx) => (
              <span key={idx} className="inline-flex items-center gap-1 px-2 py-0.5 bg-slate-700/50 text-slate-400 rounded text-xs">
                <Tag className="w-3 h-3" />
                {tag}
              </span>
            ))}
          </div>
        )}

        {/* Summary */}
        <p className="text-sm text-slate-400 mb-4 line-clamp-3 leading-relaxed">
          {item.summary}
        </p>

        {/* Source & Engagement */}
        <div className="flex items-center justify-between pt-3 border-t border-slate-700/50">
          <div className="flex items-center gap-1.5 text-xs text-slate-500">
            <span className="font-medium text-slate-300">{item.source}</span>
            <span>·</span>
            <span>{item.source_type}</span>
          </div>

          <div className="flex items-center gap-3 text-xs text-slate-500">
            <span className="flex items-center gap-1">
              <Eye className="w-3.5 h-3.5" />
              {item.views >= 10000 ? `${(item.views / 10000).toFixed(1)}w` : item.views}
            </span>
            <span className="flex items-center gap-1">
              <ThumbsUp className="w-3.5 h-3.5" />
              {item.likes}
            </span>
            {item.comments > 0 && (
              <span className="flex items-center gap-1">
                <MessageCircle className="w-3.5 h-3.5" />
                {item.comments}
              </span>
            )}
          </div>
        </div>

        {/* Link */}
        <a
          href={item.url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-4 flex items-center justify-center gap-2 w-full py-2 bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 rounded-lg text-sm font-medium transition-colors border border-purple-500/30"
        >
          <span>阅读原文</span>
          <ExternalLink className="w-4 h-4" />
        </a>
      </div>
    </article>
  )
}
