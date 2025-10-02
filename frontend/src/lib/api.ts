export type ChatRequest = { message: string; session_id?: string | null }
export type ReasoningStep = { thought?: string; tool_name?: string | null; tool_input?: string | null }
export type ChatResponse = { response: string; reasoning_steps?: ReasoningStep[] }

export type FileUploadResponse = {
  success: boolean
  message: string
  file_id?: string | null
  file_name?: string | null
  file_size?: number | null
  content_type?: string | null
  chunks?: Array<{
    content: string
    type: string
    length: number
  }> | null
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000"

export type TokenResponse = { access_token: string; token_type: string }
export type MeResponse = { 
  id: number; 
  username: string; 
  role: string; 
  is_active: boolean;
  can_upload: boolean;
  can_download: boolean;
  can_chat: boolean;
}
export type RegisterResponse = { id: number; username: string }

export async function login(username: string, password: string): Promise<TokenResponse> {
  const res = await fetch(`${API_BASE}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  })
  if (!res.ok) throw new Error(`Login error: ${res.status}`)
  return res.json()
}

export async function register(username: string, password: string): Promise<RegisterResponse> {
  const res = await fetch(`${API_BASE}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  })
  if (!res.ok) {
    try {
      const data = await res.json()
      // FastAPI validation errors shape: { detail: [{ msg, loc, type }, ...] }
      if (data?.detail) {
        const messages = Array.isArray(data.detail)
          ? data.detail.map((d: any) => d?.msg).filter(Boolean)
          : [String(data.detail)]
        throw new Error(messages.join("; ") || `Register error: ${res.status}`)
      }
      if (data?.message) throw new Error(String(data.message))
    } catch (_) {
      // ignore JSON parse errors, fall through to generic
    }
    throw new Error(`Register error: ${res.status}`)
  }
  return res.json()
}

export async function me(token: string): Promise<MeResponse> {
  const res = await fetch(`${API_BASE}/api/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) throw new Error(`Me error: ${res.status}`)
  return res.json()
}

export async function refreshToken(token: string): Promise<TokenResponse> {
  const res = await fetch(`${API_BASE}/api/auth/refresh`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) throw new Error(`Refresh token error: ${res.status}`)
  return res.json()
}

export async function chat(req: ChatRequest): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  })
  if (!res.ok) {
    throw new Error(`Chat API error: ${res.status}`)
  }
  return res.json()
}

export async function uploadFile(file: File): Promise<FileUploadResponse> {
  const formData = new FormData()
  formData.append('file', file)
  
  const res = await fetch(`${API_BASE}/api/upload`, {
    method: "POST",
    body: formData,
  })
  if (!res.ok) {
    throw new Error(`Upload API error: ${res.status}`)
  }
  return res.json()
}
export type User = {
  id: number;
  username: string;
  role: string;
  is_active: boolean;
  can_upload: boolean;
  can_download: boolean;
  can_chat: boolean;
  created_at: string;
  updated_at: string;
  last_login: string | null;
  created_by: number | null;
  notes: string | null;
}

export type UserListResponse = {
  users: User[];
  total: number;
  page: number;
  page_size: number;
}

export type FileInfo = {
  file_name: string;
  file_size: number;
  upload_time: string;
  uploader: string | null;
  file_path: string;
}

export type FileListResponse = {
  files: FileInfo[];
  total: number;
  page: number;
  page_size: number;
}

export type SystemStats = {
  users: {
    total: number;
    active: number;
    admins: number;
    regular: number;
  };
  files: {
    count: number;
    total_size: number;
    total_size_mb: number;
  };
}

export async function getUsers(token: string, page = 1, pageSize = 10, search = ""): Promise<UserListResponse> {
  const params = new URLSearchParams({
    page: page.toString(),
    page_size: pageSize.toString(),
    ...(search && { search }),
  });
  
  const res = await fetch(`${API_BASE}/api/admin/users?${params}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`Get users error: ${res.status}`);
  return res.json();
}

export async function createUser(token: string, userData: {
  username: string;
  password: string;
  role?: string;
  can_upload?: boolean;
  can_download?: boolean;
  can_chat?: boolean;
  notes?: string;
}): Promise<User> {
  const res = await fetch(`${API_BASE}/api/admin/users`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(userData),
  });
  if (!res.ok) throw new Error(`Create user error: ${res.status}`);
  return res.json();
}

export async function updateUser(token: string, userId: number, userData: {
  username?: string;
  role?: string;
  is_active?: boolean;
  can_upload?: boolean;
  can_download?: boolean;
  can_chat?: boolean;
  notes?: string;
}): Promise<User> {
  const res = await fetch(`${API_BASE}/api/admin/users/${userId}`, {
    method: "PUT",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(userData),
  });
  if (!res.ok) throw new Error(`Update user error: ${res.status}`);
  return res.json();
}

export async function deleteUser(token: string, userId: number): Promise<void> {
  const res = await fetch(`${API_BASE}/api/admin/users/${userId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`Delete user error: ${res.status}`);
}

export async function getFiles(token: string, page = 1, pageSize = 10, search = ""): Promise<FileListResponse> {
  const params = new URLSearchParams({
    page: page.toString(),
    page_size: pageSize.toString(),
    ...(search && { search }),
  });
  
  const res = await fetch(`${API_BASE}/api/admin/files?${params}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`Get files error: ${res.status}`);
  return res.json();
}

export async function deleteFile(token: string, fileName: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/admin/files/${fileName}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`Delete file error: ${res.status}`);
}

export async function getSystemStats(token: string): Promise<SystemStats> {
  const res = await fetch(`${API_BASE}/api/admin/stats`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`Get stats error: ${res.status}`);
  return res.json();
}

// 用户更改密码
export async function changePassword(token: string, oldPassword: string, newPassword: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/auth/change-password`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      old_password: oldPassword,
      new_password: newPassword,
    }),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || `Change password error: ${res.status}`);
  }
}

// 管理员重置用户密码
export async function resetUserPassword(token: string, userId: number, newPassword: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/admin/users/${userId}/reset-password`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      new_password: newPassword,
    }),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || `Reset password error: ${res.status}`);
  }
}