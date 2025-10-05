import * as React from "react"

import { cn } from "@/lib/utils"

function Input({ className, type, ...props }: React.ComponentProps<"input">) {
  return (
    <input
      type={type}
      data-slot="input"
      className={cn(
        // Base styles
        "file:text-foreground placeholder:text-muted-foreground selection:bg-primary selection:text-primary-foreground " +
        "dark:bg-input/30 border-input h-9 w-full min-w-0 rounded-md border bg-transparent px-3 py-1 text-base shadow-xs " +
        "transition-all duration-200 ease-in-out outline-none " +
        "file:inline-flex file:h-7 file:border-0 file:bg-transparent file:text-sm file:font-medium " +
        
        // Hover states
        "hover:border-input/80 hover:shadow-sm " +
        
        // Focus states
        "focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] focus-visible:shadow-md " +
        
        // Error states
        "aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive " +
        "aria-invalid:focus-visible:ring-destructive/30 aria-invalid:focus-visible:border-destructive " +
        
        // Disabled states
        "disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 " +
        "disabled:bg-muted/50 disabled:border-border/50 disabled:shadow-none " +
        
        // Dark mode enhancements
        "dark:hover:border-input/60 dark:focus-visible:border-ring " +
        
        // Placeholder enhancements
        "placeholder:transition-colors placeholder:duration-200 " +
        "focus:placeholder:text-muted-foreground/60 " +
        
        // Text size responsive
        "md:text-sm",
        className
      )}
      {...props}
    />
  )
}

export { Input }
