export function SectionHeading({
  eyebrow,
  title,
  titleId,
  description,
}: {
  eyebrow: string
  title: string
  titleId: string
  description: string
}) {
  return (
    <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-lilac">{eyebrow}</p>
        <h2 id={titleId} className="mt-3 text-3xl font-semibold tracking-[-0.03em] sm:text-4xl">
          {title}
        </h2>
      </div>
      <p className="max-w-md text-sm leading-6 text-ink-2">{description}</p>
    </div>
  )
}
