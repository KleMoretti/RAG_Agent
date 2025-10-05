"use client"

import * as React from "react"
import * as CheckboxPrimitive from "@radix-ui/react-checkbox"
import { CheckIcon } from "lucide-react"

import { cn } from "@/lib/utils"

function Checkbox({
  className,
  ...props
}: React.ComponentProps<typeof CheckboxPrimitive.Root>) {
  return (
    <CheckboxPrimitive.Root
      data-slot="checkbox"
      className={cn(
        // Base styles
        "peer border-input dark:bg-input/30 size-4 shrink-0 rounded-[4px] border shadow-xs " +
        "transition-all duration-200 ease-in-out outline-none " +
        
        // Checked states
        "data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground " +
        "dark:data-[state=checked]:bg-primary data-[state=checked]:border-primary " +
        "data-[state=checked]:shadow-sm " +
        
        // Hover states
        "hover:border-input/80 hover:shadow-sm " +
        "data-[state=checked]:hover:bg-primary/90 data-[state=checked]:hover:border-primary/90 " +
        
        // Focus states
        "focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] " +
        "data-[state=checked]:focus-visible:ring-primary/30 " +
        
        // Error states
        "aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive " +
        
        // Disabled states
        "disabled:cursor-not-allowed disabled:opacity-50 " +
        "disabled:bg-muted/50 disabled:border-border/50 disabled:shadow-none " +
        "data-[state=checked]:disabled:bg-primary/50 data-[state=checked]:disabled:border-primary/50",
        className
      )}
      {...props}
    >
      <CheckboxPrimitive.Indicator
        data-slot="checkbox-indicator"
        className="flex items-center justify-center text-current transition-all duration-150 ease-in-out"
      >
        <CheckIcon className="size-3.5" />
      </CheckboxPrimitive.Indicator>
    </CheckboxPrimitive.Root>
  )
}

export { Checkbox }
