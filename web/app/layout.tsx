import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: '朝霞日报 | OpenClaw AI见闻',
  description: '每日精选能源与AI领域高质量资讯，3天内的热门内容聚合',
  keywords: 'AI,能源,科技日报,资讯,OpenClaw',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body className="antialiased">
        {children}
      </body>
    </html>
  )
}
