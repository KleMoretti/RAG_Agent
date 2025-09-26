"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { register, login, me } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [hints, setHints] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      router.replace("/chat");
    }
  }, [router]);

  function validateInputs(): string | null {
    const messages: string[] = [];
    const usernameOk = /^[A-Za-z0-9_]{4,20}$/.test(username);
    if (!usernameOk) messages.push("用户名需为4-20位字母、数字或下划线");
    const passwordLenOk = password.length >= 8 && password.length <= 64;
    if (!passwordLenOk) messages.push("密码长度需为8-64位");
    const hasLetter = /[A-Za-z]/.test(password);
    const hasNumber = /\d/.test(password);
    if (!(hasLetter && hasNumber)) messages.push("密码需包含字母和数字");
    return messages.length ? messages.join("；") : null;
  }

  async function onSubmit() {
    setLoading(true);
    setError(null);
    const clientError = validateInputs();
    setHints(clientError);
    if (clientError) {
      setLoading(false);
      return;
    }
    try {
      await register(username, password);
      const t = await login(username, password);
      localStorage.setItem("token", t.access_token);
      const info = await me(t.access_token);
      localStorage.setItem("user", JSON.stringify(info));
      router.replace("/chat");
    } catch (e: any) {
      setError(e?.message || "注册失败");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-sm space-y-4">
        <h1 className="text-xl font-semibold">注册</h1>
        <div className="space-y-2">
          <Input placeholder="用户名" value={username} onChange={(e) => setUsername(e.target.value)} />
          <Input placeholder="密码" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
        {hints && <div className="text-amber-600 text-sm">{hints}</div>}
        {error && <div className="text-red-500 text-sm">{error}</div>}
        <Button onClick={() => void onSubmit()} disabled={loading} className="w-full">
          {loading ? "提交中..." : "注册并登录"}
        </Button>
        <div className="text-sm text-center">
          已有账号？ <a className="underline" href="/login">去登录</a>
        </div>
      </div>
    </div>
  );
}


