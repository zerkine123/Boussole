"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import AdminTopBar from "@/components/admin/AdminTopBar";
import { useLocale } from "next-intl";

import { API_BASE_URL } from "@/lib/api";

interface AdminLayoutProps {
    children: React.ReactNode;
}

export default function AdminLayout({ children }: AdminLayoutProps) {
    const router = useRouter();
    const pathname = usePathname();
    const locale = useLocale();
    const [isAuthorized, setIsAuthorized] = useState<boolean | null>(null);

    useEffect(() => {
        const verifyAdmin = async () => {
            const token = localStorage.getItem("access_token");
            if (!token) {
                router.push("/login");
                return;
            }

            try {
                const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });

                if (response.ok) {
                    const userData = await response.json();
                    if (userData.is_superuser) {
                        setIsAuthorized(true);
                    } else {
                        // Not an admin, redirect to normal dashboard
                        router.push(`/${locale}/dashboard`);
                    }
                } else {
                    // Invalid token
                    localStorage.removeItem("access_token");
                    router.push("/login");
                }
            } catch (error) {
                console.error("Admin verification failed:", error);
                router.push("/login");
            }
        };

        verifyAdmin();
    }, [pathname, router, locale]);

    if (isAuthorized === null) {
        return (
            <div className="min-h-screen bg-slate-50 flex items-center justify-center">
                <div className="flex flex-col items-center gap-4">
                    <div className="h-8 w-8 rounded-full border-4 border-slate-200 border-t-red-500 animate-spin" />
                    <p className="text-slate-500 font-medium">Verifying admin access...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-50">
            {/* Top Navigation Bar for Admin */}
            <AdminTopBar />

            {/* Page Content */}
            <main className="min-h-[calc(100vh-4.5rem)]">
                {children}
            </main>
        </div>
    );
}
