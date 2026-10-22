export function Loading({ label = 'Loading…' }: { label?: string }) {
  return (
    <div className="status" role="status" aria-live="polite">
      <span className="spinner" aria-hidden="true" /> {label}
    </div>
  )
}

export function ErrorBox({ message }: { message: string }) {
  return (
    <div className="status status-error" role="alert">
      {message}
    </div>
  )
}
