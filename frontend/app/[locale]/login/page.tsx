"use client";

import { useTranslations } from "next-intl";
import { Link, useRouter } from "@/i18n/navigation";
import { Button } from "@/components/ui/button";
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Compass, Loader2 } from "lucide-react";
import { useState } from "react";

export default function LoginPage() {
    const t = useTranslations("auth.login");
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(false);
    const [formData, setFormData] = useState({
        email: "",
        password: "",
    });

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);

        try {
            const loginBody = new URLSearchParams();
            loginBody.append('username', formData.email);
            loginBody.append('password', formData.password);

            const res = await fetch("/api/v1/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: loginBody,
            });

            if (!res.ok) {
                throw new Error("Invalid credentials");
            }

            const data = await res.json();
            localStorage.setItem("access_token", data.access_token);
            localStorage.setItem("refresh_token", data.refresh_token);

            router.push("/dashboard");
        } catch (err) {
            console.error(err);
            alert("Login failed: Invalid email or password");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex">
            {/* Left: Nature-inspired visual */}
            <div className="hidden lg:flex lg:w-1/2 banner-gradient relative overflow-hidden">
                {/* Decorative elements */}
                <div className="absolute inset-0">
                    <div className="absolute top-[20%] left-[15%] w-72 h-72 bg-white/5 rounded-full blur-3xl" />
                    <div className="absolute bottom-[20%] right-[10%] w-56 h-56 bg-white/8 rounded-full blur-3xl" />
                    <div className="absolute top-[60%] left-[40%] w-40 h-40 bg-white/5 rounded-full blur-2xl" />
                </div>

                <div className="relative z-10 flex flex-col justify-center px-16">
                    <div className="flex items-center gap-3 mb-8">
                        <div className="h-12 w-12 rounded-2xl bg-white/20 backdrop-blur-sm flex items-center justify-center">
                            <Compass className="h-7 w-7 text-white" />
                        </div>
                        <span className="text-2xl font-bold text-white">Boussole</span>
                    </div>
                    <h2 className="text-4xl font-bold text-white mb-4 leading-tight">
                        Algeria&apos;s Economic<br />Data Platform
                    </h2>
                    <p className="text-lg text-white/70 leading-relaxed max-w-md">
                        Explore comprehensive economic insights across 48 wilayas, powered by AI analytics and real-time data.
                    </p>
                </div>
            </div>

            {/* Right: Login Form */}
            <div className="flex-1 flex items-center justify-center bg-[#f5f6f8] px-6">
                <div className="w-full max-w-md">
                    {/* Mobile logo */}
                    <div className="flex items-center gap-2.5 mb-8 lg:hidden">
                        <div className="h-9 w-9 rounded-xl bg-primary flex items-center justify-center">
                            <Compass className="h-5 w-5 text-white" />
                        </div>
                        <span className="text-lg font-bold text-foreground">Boussole</span>
                    </div>

                    <Card className="border-gray-200/80 shadow-sm">
                        <CardHeader className="space-y-2 pb-4">
                            <CardTitle className="text-2xl font-bold">
                                {t("title")}
                            </CardTitle>
                            <CardDescription>
                                Enter your credentials to access your account
                            </CardDescription>
                        </CardHeader>
                        <form onSubmit={handleSubmit}>
                            <CardContent className="space-y-4 pt-2">
                                <div className="space-y-2">
                                    <Label htmlFor="email" className="text-sm font-medium">
                                        {t("email")}
                                    </Label>
                                    <Input
                                        id="email"
                                        type="email"
                                        placeholder="m@example.com"
                                        required
                                        value={formData.email}
                                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                    />
                                </div>
                                <div className="space-y-2">
                                    <div className="flex items-center justify-between">
                                        <Label htmlFor="password" className="text-sm font-medium">
                                            {t("password")}
                                        </Label>
                                        <Link
                                            href="/forgot-password"
                                            className="text-xs text-primary hover:text-primary/80 transition-colors"
                                        >
                                            {t("forgot")}
                                        </Link>
                                    </div>
                                    <Input
                                        id="password"
                                        type="password"
                                        required
                                        value={formData.password}
                                        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                    />
                                </div>
                            </CardContent>
                            <CardFooter className="flex flex-col gap-4 pt-2">
                                <Button className="w-full" size="lg" type="submit" disabled={isLoading}>
                                    {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                                    {t("button")}
                                </Button>
                                <div className="text-center text-sm text-muted-foreground">
                                    {t("noAccount")}{" "}
                                    <Link
                                        href="/register"
                                        className="text-primary font-medium hover:text-primary/80 transition-colors"
                                    >
                                        {t("signUp")}
                                    </Link>
                                </div>
                            </CardFooter>
                        </form>
                    </Card>
                </div>
            </div>
        </div>
    );
}
