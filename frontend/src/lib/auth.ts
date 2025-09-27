"use client"
import { useCallback, useEffect, useRef, useState } from "react"
import { useRouter } from "next/navigation"
import { refreshToken, me, type MeResponse } from "./api"

const TOKEN_KEY = "token"
const USER_KEY = "user"
const LAST_ACTIVITY_KEY = "last_activity"
const INACTIVITY_TIMEOUT = 2 * 60 * 60 * 1000 // 2小时（毫秒）
const REFRESH_THRESHOLD = 30 * 60 * 1000 // 30分钟前开始刷新令牌

export function useAuth() {
  const [user, setUser] = useState<MeResponse | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()
  const refreshTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const logoutTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  // 更新最后活动时间
  const updateLastActivity = useCallback(() => {
    const now = Date.now()
    localStorage.setItem(LAST_ACTIVITY_KEY, now.toString())
    
    // 清除现有的登出定时器
    if (logoutTimeoutRef.current) {
      clearTimeout(logoutTimeoutRef.current)
    }
    
    // 设置新的登出定时器
    logoutTimeoutRef.current = setTimeout(() => {
      logout()
    }, INACTIVITY_TIMEOUT)
  }, [])

  // 登出函数
  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    localStorage.removeItem(LAST_ACTIVITY_KEY)
    setUser(null)
    setToken(null)
    
    // 清除所有定时器
    if (refreshTimeoutRef.current) {
      clearTimeout(refreshTimeoutRef.current)
    }
    if (logoutTimeoutRef.current) {
      clearTimeout(logoutTimeoutRef.current)
    }
    
    router.push("/login")
  }, [router])

  // 刷新令牌
  const refreshAuthToken = useCallback(async () => {
    if (!token) return false
    
    try {
      const response = await refreshToken(token)
      const newToken = response.access_token
      localStorage.setItem(TOKEN_KEY, newToken)
      setToken(newToken)
      
      // 验证新令牌并获取用户信息
      const userInfo = await me(newToken)
      localStorage.setItem(USER_KEY, JSON.stringify(userInfo))
      setUser(userInfo)
      
      return true
    } catch (error) {
      console.error("Token refresh failed:", error)
      logout()
      return false
    }
  }, [token, logout])

  // 设置令牌刷新定时器
  const scheduleTokenRefresh = useCallback(() => {
    if (!token) return
    
    // 清除现有定时器
    if (refreshTimeoutRef.current) {
      clearTimeout(refreshTimeoutRef.current)
    }
    
    // 计算刷新时间（令牌过期前30分钟）
    const refreshTime = REFRESH_THRESHOLD
    refreshTimeoutRef.current = setTimeout(() => {
      refreshAuthToken()
    }, refreshTime)
  }, [token, refreshAuthToken])

  // 检查令牌是否即将过期
  const isTokenExpiringSoon = useCallback((token: string): boolean => {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      const exp = payload.exp * 1000 // 转换为毫秒
      const now = Date.now()
      return (exp - now) < REFRESH_THRESHOLD
    } catch {
      return true // 如果解析失败，认为需要刷新
    }
  }, [])

  // 初始化认证状态
  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem(TOKEN_KEY)
      const storedUser = localStorage.getItem(USER_KEY)
      const lastActivity = localStorage.getItem(LAST_ACTIVITY_KEY)
      
      if (!storedToken || !storedUser) {
        setIsLoading(false)
        return
      }
      
      // 检查是否超过2小时无活动
      if (lastActivity) {
        const lastActivityTime = parseInt(lastActivity)
        const now = Date.now()
        if (now - lastActivityTime > INACTIVITY_TIMEOUT) {
          logout()
          return
        }
      }
      
      // 检查令牌是否即将过期
      if (isTokenExpiringSoon(storedToken)) {
        try {
          const response = await refreshToken(storedToken)
          const newToken = response.access_token
          localStorage.setItem(TOKEN_KEY, newToken)
          setToken(newToken)
          
          const userInfo = await me(newToken)
          localStorage.setItem(USER_KEY, JSON.stringify(userInfo))
          setUser(userInfo)
        } catch (error) {
          console.error("Initial token refresh failed:", error)
          logout()
          return
        }
      } else {
        setToken(storedToken)
        setUser(JSON.parse(storedUser))
      }
      
      setIsLoading(false)
    }
    
    initAuth()
  }, [logout, isTokenExpiringSoon])

  // 设置定时器
  useEffect(() => {
    if (token) {
      scheduleTokenRefresh()
      updateLastActivity()
    }
    
    return () => {
      if (refreshTimeoutRef.current) {
        clearTimeout(refreshTimeoutRef.current)
      }
      if (logoutTimeoutRef.current) {
        clearTimeout(logoutTimeoutRef.current)
      }
    }
  }, [token, scheduleTokenRefresh, updateLastActivity])

  // 监听用户活动
  useEffect(() => {
    const handleActivity = () => {
      updateLastActivity()
    }
    
    // 监听各种用户活动
    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click']
    
    events.forEach(event => {
      document.addEventListener(event, handleActivity, true)
    })
    
    return () => {
      events.forEach(event => {
        document.removeEventListener(event, handleActivity, true)
      })
    }
  }, [updateLastActivity])

  return {
    user,
    token,
    isLoading,
    logout,
    refreshAuthToken
  }
}
