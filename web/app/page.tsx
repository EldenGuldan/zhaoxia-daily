import { NewsItem, ViewMode } from '../lib/types'
import { getNewsData } from '../lib/data'
import NewsContent from './NewsContent'

export default function Home() {
  // 在服务端获取数据
  const data: NewsItem[] = getNewsData()

  return <NewsContent initialData={data} />
}
