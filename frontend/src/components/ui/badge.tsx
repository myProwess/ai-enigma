import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default: "border-transparent bg-primary text-primary-foreground hover:bg-primary/80",
        secondary: "border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80",
        destructive: "border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/80",
        outline: "text-foreground",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

// Dynamic category color mapping — extend freely as needed
const categoryColors: Record<string, string> = {
  Technology: "border-transparent bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300 hover:bg-blue-200 dark:hover:bg-blue-900/60",
  Business: "border-transparent bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300 hover:bg-green-200 dark:hover:bg-green-900/60",
  Sports: "border-transparent bg-orange-100 text-orange-800 dark:bg-orange-900/40 dark:text-orange-300 hover:bg-orange-200 dark:hover:bg-orange-900/60",
  Politics: "border-transparent bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300 hover:bg-purple-200 dark:hover:bg-purple-900/60",
  Science: "border-transparent bg-teal-100 text-teal-800 dark:bg-teal-900/40 dark:text-teal-300 hover:bg-teal-200 dark:hover:bg-teal-900/60",
  Health: "border-transparent bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300 hover:bg-red-200 dark:hover:bg-red-900/60",
  Entertainment: "border-transparent bg-pink-100 text-pink-800 dark:bg-pink-900/40 dark:text-pink-300 hover:bg-pink-200 dark:hover:bg-pink-900/60",
}

// Fallback for any unknown category
const defaultCategoryColor = "border-transparent bg-slate-100 text-slate-800 dark:bg-slate-900/40 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-900/60"

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
  VariantProps<typeof badgeVariants> {
  category?: string | null;
}

function Badge({ className, variant, category, ...props }: BadgeProps) {
  const categoryClass = category
    ? categoryColors[category] || defaultCategoryColor
    : undefined;

  return (
    <div
      className={cn(
        badgeVariants({ variant: categoryClass ? null : variant }),
        categoryClass,
        className,
      )}
      {...props}
    />
  )
}

export { Badge, badgeVariants }
