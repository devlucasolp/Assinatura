export default function Loading() {
  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-6">
        <div className="h-7 w-32 bg-zinc-100 dark:bg-zinc-800 rounded animate-pulse mb-2" />
        <div className="h-4 w-48 bg-zinc-100 dark:bg-zinc-800 rounded animate-pulse" />
      </div>
      <div className="flex flex-col gap-2">
        {[1, 2, 3].map(i => (
          <div key={i} className="h-20 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-100 dark:border-zinc-800 animate-pulse" />
        ))}
      </div>
    </div>
  )
}
