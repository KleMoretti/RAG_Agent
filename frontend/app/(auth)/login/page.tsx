"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { loginSchema, type LoginFormData } from "@/lib/validations/auth";
import { useAuthStore } from "@/store/authStore";
import { authApi } from "@/lib/api/auth";
import { ROUTES } from "@/lib/constants";
import { useTranslation } from "@/lib/hooks/useTranslation";
import { LanguageSwitcher } from "@/components/shared/LanguageSwitcher";
import { Loader2 } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const t = useTranslation();
  const [isLoading, setIsLoading] = React.useState(false);
  const [errorMessage, setErrorMessage] = React.useState("");
  const login = useAuthStore((state) => state.login);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      username: "",
      password: "",
      rememberMe: false,
    },
  });

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true);
    setErrorMessage("");

    try {
      // Step 1: Login to get access token
      const loginResponse = await authApi.login({
        username: data.username,
        password: data.password,
      });

      // Step 2: Fetch user data using the token directly
      const user = await authApi.getMeWithToken(loginResponse.access_token);

      // Step 3: Complete login process
      login(user, loginResponse.access_token);

      // Also store token in cookie for middleware authentication
      document.cookie = `auth_token=${loginResponse.access_token}; path=/; max-age=${
        60 * 60 * 24 * 7
      }`; // 7 days

      // Redirect to dashboard
      router.push(ROUTES.DASHBOARD);
    } catch (error: unknown) {
      console.error("Login failed:", error);

      // Handle network errors with helpful message
      if (error instanceof Error && error.message.includes("Network")) {
        setErrorMessage(t.errors.networkError);
      } else {
        setErrorMessage(
          error instanceof Error ? error.message : t.errors.loginFailedMessage
        );
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background to-secondary dark:from-background dark:to-card p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <div className="flex justify-end mb-2">
            <LanguageSwitcher />
          </div>
          <CardTitle className="text-2xl font-semibold text-center">
            {t.auth.loginTitle}
          </CardTitle>
          <CardDescription className="text-center font-normal">
            {t.auth.loginSubtitle}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {errorMessage && (
            <Alert variant="destructive" className="mb-4">
              <AlertDescription>{errorMessage}</AlertDescription>
            </Alert>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="username">{t.auth.username}</Label>
              <Input
                id="username"
                placeholder={t.auth.username}
                {...register("username")}
                disabled={isLoading}
              />
              {errors.username && (
                <p className="text-sm text-destructive">
                  {errors.username.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">{t.auth.password}</Label>
              <Input
                id="password"
                type="password"
                placeholder={t.auth.password}
                {...register("password")}
                disabled={isLoading}
              />
              {errors.password && (
                <p className="text-sm text-destructive">
                  {errors.password.message}
                </p>
              )}
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Checkbox id="rememberMe" {...register("rememberMe")} />
                <Label
                  htmlFor="rememberMe"
                  className="text-sm font-normal cursor-pointer"
                >
                  {t.auth.rememberMe}
                </Label>
              </div>
              <Link href="#" className="text-sm text-primary hover:underline">
                {t.auth.forgotPassword}
              </Link>
            </div>

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4" />
                  {t.auth.signInProgress}
                </>
              ) : (
                t.auth.signIn
              )}
            </Button>
          </form>
        </CardContent>
        <CardFooter className="flex flex-col space-y-2">
          <div className="text-sm text-center text-muted-foreground">
            {t.auth.noAccount}{" "}
            <Link
              href={ROUTES.REGISTER}
              className="text-primary hover:underline"
            >
              {t.auth.registerNow}
            </Link>
          </div>
          <div className="text-xs text-center text-muted-foreground">
            {t.auth.demoCredentials}
          </div>
        </CardFooter>
      </Card>
    </div>
  );
}
