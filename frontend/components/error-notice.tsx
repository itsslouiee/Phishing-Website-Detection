import { CircleAlert, RefreshCw } from 'lucide-react'
import { Button } from './ui/button'

export function ErrorNotice({
  title,
  message,
  onRetry,
}: {
  title: string
  message: string
  onRetry?: () => void
}) {
  return (
    <div role="alert" className="flex flex-col gap-4 rounded-2xl border border-danger/25 bg-danger/[0.06] p-5 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex items-start gap-3">
        <CircleAlert className="mt-0.5 size-5 shrink-0 text-danger" aria-hidden="true" />
        <div>
          <p className="text-sm font-semibold text-ink">{title}</p>
          <p className="mt-1 text-sm leading-6 text-ink-2">{message}</p>
        </div>
      </div>
      {onRetry && (
        <Button variant="ghost" onClick={onRetry} className="h-10 shrink-0">
          <RefreshCw className="size-4" aria-hidden="true" />
          Try again
        </Button>
      )}
    </div>
  )
}
