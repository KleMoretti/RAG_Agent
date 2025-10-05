import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { STORAGE_KEYS, THEME_MODES } from '../lib/constants';

/**
 * Language type
 */
export type Language = 'zh-CN' | 'en-US';

/**
 * Theme mode type
 */
type ThemeMode = typeof THEME_MODES[keyof typeof THEME_MODES];

/**
 * UI store state
 */
interface UIState {
  theme: ThemeMode;
  sidebarCollapsed: boolean;
  language: Language;
  isDemoMode: boolean;
}

/**
 * UI store actions
 */
interface UIActions {
  setTheme: (theme: ThemeMode) => void;
  toggleTheme: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  toggleSidebar: () => void;
  setLanguage: (language: Language) => void;
  setDemoMode: (enabled: boolean) => void;
}

/**
 * Combined UI store type
 */
type UIStore = UIState & UIActions;

/**
 * UI state management store using Zustand
 * Handles theme, sidebar, language, and demo mode
 */
export const useUIStore = create<UIStore>()(
  persist(
    (set, get) => ({
      // Initial state - Chinese as default language
      theme: THEME_MODES.LIGHT,
      sidebarCollapsed: false,
      language: 'zh-CN',
      isDemoMode: true,

      // Actions
      setTheme: (theme) => set({ theme }),

      toggleTheme: () => {
        const currentTheme = get().theme;
        const newTheme =
          currentTheme === THEME_MODES.LIGHT
            ? THEME_MODES.DARK
            : THEME_MODES.LIGHT;
        set({ theme: newTheme });
      },

      setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),

      toggleSidebar: () => set({ sidebarCollapsed: !get().sidebarCollapsed }),

      setLanguage: (language) => set({ language }),

      setDemoMode: (enabled) => set({ isDemoMode: enabled }),
    }),
    {
      name: STORAGE_KEYS.THEME,
      partialize: (state) => ({
        theme: state.theme,
        language: state.language,
        sidebarCollapsed: state.sidebarCollapsed,
      }),
    }
  )
);
