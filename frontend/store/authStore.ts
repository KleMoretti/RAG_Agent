import { create } from "zustand";
import { persist } from "zustand/middleware";
import { User } from "../lib/types/user";
import { STORAGE_KEYS } from "../lib/constants";
import { useChatStore } from "./chatStore";

/**
 * Authentication store state
 */
interface AuthState {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    isLoading: boolean;
}

/**
 * Authentication store actions
 */
interface AuthActions {
    setUser: (user: User | null) => void;
    setToken: (token: string | null) => void;
    setLoading: (loading: boolean) => void;
    login: (user: User, token: string) => void;
    logout: () => void;
}

/**
 * Combined auth store type
 */
type AuthStore = AuthState & AuthActions;

/**
 * Authentication store using Zustand
 * Persisted to localStorage for session persistence
 */
export const useAuthStore = create<AuthStore>()(
    persist(
        (set) => ({
            // Initial state
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,

            // Actions
            setUser: (user) =>
                set({
                    user,
                    isAuthenticated: !!user,
                }),

            setToken: (token) => set({ token }),

            setLoading: (loading) => set({ isLoading: loading }),

            login: (user, token) => {
                // 设置用户 ID 到 localStorage 以便 chatStore 使用
                if (typeof localStorage !== "undefined") {
                    localStorage.setItem("user-id", user.id.toString());
                }

                // 清除旧用户的聊天数据
                const chatStore = useChatStore.getState();
                chatStore.clearUserData();
                chatStore.setCurrentUser(user.id);

                set({
                    user,
                    token,
                    isAuthenticated: true,
                    isLoading: false,
                });
            },

            logout: () => {
                // Clear cookie
                if (typeof document !== "undefined") {
                    document.cookie =
                        "auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
                }

                // 清除用户 ID
                if (typeof localStorage !== "undefined") {
                    localStorage.removeItem("user-id");
                }

                // 清除聊天数据
                const chatStore = useChatStore.getState();
                chatStore.clearUserData();
                chatStore.setCurrentUser(null);

                set({
                    user: null,
                    token: null,
                    isAuthenticated: false,
                    isLoading: false,
                });
            },
        }),
        {
            name: STORAGE_KEYS.USER,
            partialize: (state) => ({
                user: state.user,
                token: state.token,
                isAuthenticated: state.isAuthenticated,
            }),
        },
    ),
);
