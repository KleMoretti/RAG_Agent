"use client";
import { useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

export type ReasoningStep = {
  thought?: string;
  tool_name?: string | null;
  tool_input?: string | null;
  result?: string | null;
};

export function ReasoningPanel({
  steps,
  defaultOpen = false,
}: {
  steps: ReasoningStep[];
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);
  if (!steps || steps.length === 0) return null;
  return (
    <Card className="mt-3">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-base">Reasoning</CardTitle>
        <button
          onClick={() => setOpen((s) => !s)}
          className="text-sm text-gray-500"
        >
          {open ? (
            <span className="inline-flex items-center gap-1">
              <ChevronDown className="h-4 w-4" /> 收起
            </span>
          ) : (
            <span className="inline-flex items-center gap-1">
              <ChevronRight className="h-4 w-4" /> 展开
            </span>
          )}
        </button>
      </CardHeader>
      {open && (
        <CardContent>
          <div className="space-y-3">
            {steps.map((s, i) => (
              <div key={i} className="text-sm">
                <div className="font-medium">{s.thought || "(no thought)"}</div>
                {(s.tool_name || s.tool_input) && (
                  <div className="text-xs text-gray-500">
                    {s.tool_name ? `Tool: ${s.tool_name}` : null}
                    {s.tool_input ? ` | Input: ${s.tool_input}` : null}
                  </div>
                )}
                {i < steps.length - 1 && <Separator className="my-2" />}
              </div>
            ))}
          </div>
        </CardContent>
      )}
    </Card>
  );
}
