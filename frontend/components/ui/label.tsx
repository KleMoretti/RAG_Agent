"use client"

import * as React from "react"
import * as LabelPrimitive from "@radix-ui/react-label"

import { cn } from "@/lib/utils"

function Label({
  className,
  ...props
}: React.ComponentProps<typeof LabelPrimitive.Root>) {
  return (
    <LabelPrimitive.Root
      data-slot="label"
      className={cn(
        // Base styles
        "flex items-center gap-2 text-sm leading-none font-medium select-none " +
        "transition-colors duration-200 ease-in-out " +
        
        // Interactive states
        "cursor-pointer hover:text-foreground/80 " +
        
        // Disabled states
        "group-data-[disabled=true]:pointer-events-none group-data-[disabled=true]:opacity-50 " +
        "group-data-[disabled=true]:cursor-not-allowed " +
        "peer-disabled:cursor-not-allowed peer-disabled:opacity-50 peer-disabled:hover:text-muted-foreground " +
        
        // Focus states (when associated input is focused)
        "peer-focus-visible:text-foreground",
        className
      )}
      {...props}
    />
  )
}

export { Label }
