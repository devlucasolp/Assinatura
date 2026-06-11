import { cn } from '@/lib/cn'
import { type TextareaHTMLAttributes, forwardRef } from 'react'

type Props = TextareaHTMLAttributes<HTMLTextAreaElement> & { error?: string }

export const Textarea = forwardRef<HTMLTextAreaElement, Props>(
  ({ error, className, ...props }, ref) => (
    <div className="flex flex-col gap-1">
      <textarea
        ref={ref}
        className={cn(
          'w-full rounded-lg border bg-white px-3.5 py-2.5 text-sm text-zinc-900 placeholder:text-zinc-400 transition-all resize-y leading-relaxed',
          'focus:outline-none focus:ring-2 focus:ring-violet-500/25 focus:border-violet-400',
          'dark:bg-zinc-950 dark:text-zinc-100 dark:placeholder:text-zinc-600',
          error
            ? 'border-red-400 dark:border-red-600'
            : 'border-zinc-200 dark:border-zinc-800 hover:border-zinc-300 dark:hover:border-zinc-700',
          className,
        )}
        {...props}
      />
      {error && <p className="text-xs text-red-500 dark:text-red-400">{error}</p>}
    </div>
  )
)
Textarea.displayName = 'Textarea'
