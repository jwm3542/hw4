import { Fragment, ReactNode } from 'react'

// Tiny, safe Markdown for chat replies: **bold**, *italic*, and "- " bullet lists.
// Renders React elements only (no innerHTML), so model output can't inject HTML.
function inline(text: string): ReactNode[] {
  return text.split(/(\*\*[^*]+\*\*|\*[^*]+\*)/g).map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**') && part.length > 4) return <strong key={i}>{part.slice(2, -2)}</strong>
    if (part.startsWith('*') && part.endsWith('*') && part.length > 2) return <em key={i}>{part.slice(1, -1)}</em>
    return <Fragment key={i}>{part}</Fragment>
  })
}

export default function Markdown({ text }: { text: string }) {
  const blocks: ReactNode[] = []
  let bullets: string[] = []
  const flush = () => {
    if (bullets.length) {
      blocks.push(
        <ul key={`ul${blocks.length}`}>
          {bullets.map((b, i) => (
            <li key={i}>{inline(b)}</li>
          ))}
        </ul>,
      )
      bullets = []
    }
  }
  for (const line of text.split('\n')) {
    const m = line.match(/^\s*[-*•]\s+(.*)$/)
    if (m) {
      bullets.push(m[1])
      continue
    }
    flush()
    if (line.trim()) blocks.push(<p key={`p${blocks.length}`}>{inline(line)}</p>)
  }
  flush()
  return <>{blocks}</>
}
