"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { login, me } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      // already logged in
      router.replace("/chat");
    }
  }, [router]);

  async function onSubmit() {
    setLoading(true);
    setError(null);
    try {
      const t = await login(username, password);
      localStorage.setItem("token", t.access_token);
      const info = await me(t.access_token);
      localStorage.setItem("user", JSON.stringify(info));
      router.replace("/chat");
    } catch (e: any) {
      setError(e?.message || "登录失败");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-sm space-y-4">
        <h1 className="text-xl font-semibold">登录</h1>
        <div className="space-y-2">
          <Input placeholder="用户名" value={username} onChange={(e) => setUsername(e.target.value)} />
          <Input placeholder="密码" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
        {error && <div className="text-red-500 text-sm">{error}</div>}
        <Button onClick={() => void onSubmit()} disabled={loading} className="w-full">
          {loading ? "登录中..." : "登录"}
        </Button>
      </div>
    </div>
  );
}


