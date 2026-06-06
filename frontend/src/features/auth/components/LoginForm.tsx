import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { Eye, EyeOff, AlertCircle, Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { useI18nStore } from "@/lib/i18n/store";
import { useAuthStore } from "@/features/auth/store";
import { Alert, AlertDescription } from "@/components/ui/alert";

import { login } from "../api";

const LoginSchema = z.object({
  email: z.string().email("Email tidak valid"),
  password: z.string().min(1, "Password wajib diisi"),
});

type LoginValues = z.infer<typeof LoginSchema>;

export function LoginForm({ onSuccess }: { onSuccess: (role: string) => void }) {
  const t = useI18nStore((s) => s.t);
  const [serverError, setServerError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const rememberMe = useAuthStore((s) => s.rememberMe);
  const setRememberMe = useAuthStore((s) => s.setRememberMe);
  const form = useForm<LoginValues>({
    resolver: zodResolver(LoginSchema),
    defaultValues: { email: "", password: "" },
  });

  async function onSubmit(values: LoginValues) {
    setServerError(null);
    try {
      const { role } = await login(values);
      onSuccess(role);
    } catch (err) {
      setServerError(err instanceof Error ? err.message : "Login failed");
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} noValidate className="space-y-4">
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>{t("Email", "Email")}</FormLabel>
              <FormControl>
                <Input type="email" inputMode="email" autoComplete="username" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>{t("Kata sandi", "Password")}</FormLabel>
              <div className="relative">
                <FormControl>
                  <Input
                    type={showPassword ? "text" : "password"}
                    autoComplete="current-password"
                    className="pr-10"
                    {...field}
                  />
                </FormControl>
                <button
                  type="button"
                  tabIndex={-1}
                  onClick={() => setShowPassword((v) => !v)}
                  className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-muted-foreground hover:text-foreground cursor-pointer"
                  aria-label={
                    showPassword
                      ? t("Sembunyikan sandi", "Hide password")
                      : t("Tampilkan sandi", "Show password")
                  }
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
              <FormMessage />
            </FormItem>
          )}
        />
        <div className="flex items-center gap-2">
          <Checkbox
            id="remember-me"
            checked={rememberMe}
            onCheckedChange={(checked) => setRememberMe(checked === true)}
          />
          <label htmlFor="remember-me" className="text-sm text-muted-foreground cursor-pointer">
            {t("Ingat saya", "Remember me")}
          </label>
        </div>
        {serverError && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{serverError}</AlertDescription>
          </Alert>
        )}
        <Button
          type="submit"
          disabled={form.formState.isSubmitting}
          className="w-full cursor-pointer"
        >
          {form.formState.isSubmitting ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              {t("Memuat...", "Signing in...")}
            </>
          ) : (
            t("Masuk", "Sign in")
          )}
        </Button>
      </form>
      <p className="text-center text-sm text-muted-foreground">
        <a
          href="#"
          className="text-primary underline-offset-4 hover:underline pointer-events-none opacity-50"
        >
          {t("Lupa kata sandi?", "Forgot password?")}
        </a>
      </p>
    </Form>
  );
}
