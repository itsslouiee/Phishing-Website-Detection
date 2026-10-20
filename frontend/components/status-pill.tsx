export function StatusPill({ children, tone = 'violet' }: { children: React.ReactNode; tone?: 'violet' | 'green' | 'red' }) {
  const styles = {
    violet: 'border-violet-400/20 bg-violet-400/10 text-violet-200',
    green: 'border-emerald-400/20 bg-emerald-400/10 text-emerald-300',
    red: 'border-red-400/20 bg-red-400/10 text-red-300',
  }
  return (
    <span className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-[11px] font-medium tracking-[0.12em] uppercase ${styles[tone]}`}>
      <span className="size-1.5 rounded-full bg-current" aria-hidden />
      {children}
    </span>
  )
}
