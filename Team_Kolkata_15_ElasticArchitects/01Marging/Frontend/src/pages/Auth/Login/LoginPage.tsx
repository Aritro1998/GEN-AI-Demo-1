"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardHeader, CardContent, CardTitle } from "@/components/ui/card";
import { LoginBackground } from "@/components/Background/LoginBackground";
import { Particles } from "@/components/Background/Particles";
import { Parallax } from "@/components/Background/Parallex";
import { Link } from "react-router-dom";
import useUserStore from "@/store/useUserStore";
import { useState } from "react";
// import { FutureBackground } from "@/components/FutureBackground";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const { login } = useUserStore();

  const handleLogin = () => {
    login(email,password)
  };

  return (
    <div className="relative min-h-screen w-full bg-background text-white flex items-center justify-center overflow-hidden">
      {/* Fullscreen Spline background */}
      <LoginBackground />

      {/* Subtle floating particles */}
      <Particles />

      {/* Parallax card */}
      <Parallax>
        <Card
          className="
          relative z-10 w-[360px] p-6
          backdrop-blur-xl bg-white/5
          border border-white/10 rounded-xl
          shadow-[0_0_60px_rgba(0,0,0,0.4)]
          transition-all duration-500
        "
        >
          <CardHeader>
            <CardTitle className="text-center text-2xl font-light tracking-wide text-white/90">
              Welcome Back
            </CardTitle>
          </CardHeader>

          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label className="text-[var(--muted-foreground)]">Email</Label>
              <Input
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                type="email"
                placeholder="you@example.com"
                className="
        bg-[var(--muted)]
        border border-[var(--border)]
        text-[var(--foreground)]
        placeholder:text-[var(--muted-foreground)]
        glow-focus
      "
              />
            </div>

            <div className="space-y-2">
              <Label className="text-[var(--muted-foreground)]">Password</Label>
              <Input
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                type="password"
                placeholder="••••••••"
                className="
        bg-[var(--muted)]
        border border-[var(--border)]
        text-[var(--foreground)]
        placeholder:text-[var(--muted-foreground)]
        glow-focus
      "
              />
            </div>

            {/* Remember Me + Forgot Password */}
            <div className="flex items-center justify-between">
              {/* Remember me */}
              <label className="flex items-center gap-2 text-[var(--muted-foreground)] text-sm select-none">
                <input
                  type="checkbox"
                  className="
          w-4 h-4 rounded-sm border-[var(--border)]
          bg-[var(--muted)]
          checked:bg-[var(--primary)]
          checked:border-[var(--primary)]
          cursor-pointer
        "
                />
                Remember me
              </label>

              {/* Forgot Password */}
              <a
                href="/forgot-password"
                className="
        text-sm text-[var(--primary)]
        hover:underline hover:text-[color-mix(in_oklch,var(--primary)_90%,var(--secondary))]
        transition
      "
              >
                Forgot password?
              </a>
            </div>

            <Button
              className="
      w-full
      bg-[var(--primary)]
      text-[var(--primary-foreground)]
      hover:bg-[color-mix(in_oklch,var(--primary)_85%,var(--secondary))]
      transition-all duration-300
    "
              onClick={handleLogin}
            >
              Login
            </Button>
          </CardContent>
        </Card>
      </Parallax>
    </div>
  );
}
