import { NewsItem } from '@/lib/types'
import { format } from 'date-fns'
import { zhCN } from 'date-fns/locale'
import { ExternalLink, Tag } from 'lucide-react'

interface DataTableProps {
  data: NewsItem[]
}

export default function DataTable({ data }: DataTableProps) {
  const categoryLabels: Record<string, { label: string; className: string }> = {
    tool: { label: '🛠️ AI 工具', className: 'text-purple-300' },
    news: { label: '📰 行业新闻', className: 'text-blue-300' },
    trend: { label: '🔥 热点话题', className: 'text-red-300' },
  }

  return (
    <div className="bg-slate-800/50 rounded-2xl border border-purple-500/20 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-slate-900/80">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-semibold text-purple-300 uppercase tracking-wider">类别</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-purple-300 uppercase tracking-wider">标题</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-purple-300 uppercase tracking-wider">标签</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-purple-300 uppercase tracking-wider">来源</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-purple-300 uppercase tracking-wider">时间</th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-purple-300 uppercase tracking-wider">互动</th>
              <th className="px-4 py-3 text-center text-xs font-semibold text-purple-300 uppercase tracking-wider">链接</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-purple-500/10">
            {data.map((item) => (
              <tr key={item.id} className="hover:bg-purple-500/5 transition-colors">
                <td className="px-4 py-3 whitespace-nowrap">
                  <span className={`text-sm font-medium ${categoryLabels[item.category].className}`}>
                    {categoryLabels[item.category].label}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="max-w-md">
                    <p className="text-sm font-medium text-white line-clamp-2" title={item.title}>
                      {item.title}
                    </p>
                    <p className="text-xs text-slate-500 mt-1 line-clamp-1">{item.summary}</p>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="flex flex-wrap gap-1">
                    {item.tags.slice(0, 3).map((tag, idx) => (
                      <span key={idx} className="inline-flex items-center gap-1 px-2 py-0.5 bg-slate-700 text-slate-400 rounded text-xs">
                        <Tag className="w-3 h-3" />
                        {tag}
                      </span>
                    ))}
                  </div>
                </td>
                <td className="px-4 py-3 whitespace-nowrap">
                  <div className="text-sm text-slate-300">{item.source}</div>
                  <div className="text-xs text-slate-500">{item.source_type}</div>
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-slate-400">
                  {format(new Date(item.publishedAt), 'MM-dd HH:mm', { locale: zhCN })}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-right text-sm">
                  <div className="flex flex-col gap-1">
                    <span className="text-slate-400">👁 {item.views >= 10000 ? `${(item.views / 10000).toFixed(1)}w` : item.views}</span>
                    <span className="text-purple-400 font-medium">👍 {item.likes}</span>
                  </div>
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-center">
                  <a
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-purple-400 hover:text-purple-300 text-sm font-medium"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
