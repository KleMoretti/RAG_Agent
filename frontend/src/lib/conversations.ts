"use client"
import { useCallback, useEffect, useMemo, useState } from "react"

export type Conversation = {
  id: string
  title: string
  createdAt: number
  updatedAt: number
}

const LS_LIST = "rag_conversations"
const LS_CURRENT = "rag_current_conversation"

function readList(): Conversation[] {
  try {
    const raw = localStorage.getItem(LS_LIST)
    if (!raw) return []
    const arr = JSON.parse(raw) as Conversation[]
    return Array.isArray(arr) ? arr : []
  } catch {
    return []
  }
}

function writeList(list: Conversation[]) {
  localStorage.setItem(LS_LIST, JSON.stringify(list))
}

export function useConversations() {
  const [list, setList] = useState<Conversation[]>([])
  const [currentId, setCurrentId] = useState<string | null>(null)

  // init from storage
  useEffect(() => {
    const l = readList()
    setList(l)
    const cid = localStorage.getItem(LS_CURRENT)
    setCurrentId(cid || (l[0]?.id ?? null))
  }, [])

  const current = useMemo(() => list.find((c) => c.id === currentId) || null, [list, currentId])

  const select = useCallback((id: string) => {
    setCurrentId(id)
    localStorage.setItem(LS_CURRENT, id)
  }, [])

  const create = useCallback((title = "新会话") => {
    const id = `c_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 6)}`
    const now = Date.now()
    const conv: Conversation = { id, title, createdAt: now, updatedAt: now }
    setList((prev) => {
      const next = [conv, ...prev]
      writeList(next)
      return next
    })
    setCurrentId(id)
    localStorage.setItem(LS_CURRENT, id)
    return id
  }, [])

  const rename = useCallback((id: string, title: string) => {
    setList((prev) => {
      const next = prev.map((c) => (c.id === id ? { ...c, title, updatedAt: Date.now() } : c))
      writeList(next)
      return next
    })
  }, [])

  const remove = useCallback((id: string) => {
    setList((prev) => {
      const next = prev.filter((c) => c.id !== id)
      writeList(next)
      // update current selection
      if (id === currentId) {
        const fallback = next[0]?.id || null
        setCurrentId(fallback)
        if (fallback) localStorage.setItem(LS_CURRENT, fallback)
        else localStorage.removeItem(LS_CURRENT)
      }
      return next
    })
  }, [currentId])

  return { list, current, currentId, select, create, rename, remove }
}
