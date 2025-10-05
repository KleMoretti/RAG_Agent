import { useUIStore } from '@/store/uiStore';
import { translations } from '../i18n';

/**
 * Hook to get translations based on current language
 */
export function useTranslation() {
  const language = useUIStore((state) => state.language);
  return translations[language];
}
