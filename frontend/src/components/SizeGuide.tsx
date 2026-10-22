import { useRef } from 'react'

// General unisex sizing reference (typical for campus fleece and tees). Not store data; labeled as a guide.
const ROWS = [
  ['XS', '31–33', '34–36', '27'],
  ['S', '34–36', '36–38', '28'],
  ['M', '38–40', '39–41', '29'],
  ['L', '42–44', '42–44', '30'],
  ['XL', '46–48', '45–47', '31'],
  ['XXL', '50–52', '48–50', '32'],
]

export default function SizeGuide() {
  const ref = useRef<HTMLDialogElement>(null)
  return (
    <>
      <button type="button" className="link-btn" onClick={() => ref.current?.showModal()}>
        📏 Size guide
      </button>
      <dialog ref={ref} className="size-guide" aria-labelledby="size-guide-title" onClick={e => e.target === ref.current && ref.current?.close()}>
        <div className="size-guide-inner">
          <div className="section-head">
            <h2 id="size-guide-title">Size guide</h2>
            <button className="chat-close size-guide-close" onClick={() => ref.current?.close()} aria-label="Close size guide">
              ×
            </button>
          </div>
          <p className="muted">Unisex fit, in inches. Between sizes? Size up for a relaxed fit, or for hoodies over layers.</p>
          <table className="stock-table size-table">
            <thead>
              <tr>
                <th scope="col">Size</th>
                <th scope="col">Chest</th>
                <th scope="col">Waist</th>
                <th scope="col">Body length</th>
              </tr>
            </thead>
            <tbody>
              {ROWS.map(r => (
                <tr key={r[0]}>
                  {r.map((c, i) => (i === 0 ? <th key={i} scope="row">{c}</th> : <td key={i}>{c}</td>))}
                </tr>
              ))}
            </tbody>
          </table>
          <p className="muted small">
            General guide only; fit varies by brand. Questions? Call (475) 301-4205. Unworn items with tags can be returned within 30 days.
          </p>
        </div>
      </dialog>
    </>
  )
}
