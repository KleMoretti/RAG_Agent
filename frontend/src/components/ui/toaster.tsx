"use client";
import * as React from "react";
import * as Toast from "@radix-ui/react-toast";

export function Toaster() {
  return (
    <Toast.Provider swipeDirection="right">
      <Toast.Viewport className="fixed bottom-0 right-0 z-50 m-4 w-96 max-w-[100vw] space-y-2" />
    </Toast.Provider>
  );
}
