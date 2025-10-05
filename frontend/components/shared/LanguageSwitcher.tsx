"use client";

import { Button } from "@/components/ui/button";
import { useUIStore } from "@/store/uiStore";

export function LanguageSwitcher() {
  const { language, setLanguage } = useUIStore();

  const toggleLanguage = () => {
    setLanguage(language === "zh-CN" ? "en-US" : "zh-CN");
  };

  return (
    <Button variant="outline" size="sm" onClick={toggleLanguage}>
      {language === "zh-CN" ? "中文" : "EN"}
    </Button>
  );
}
