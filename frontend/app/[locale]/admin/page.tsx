"use client";

import { useTranslations } from "next-intl";
import { Users, Database, Activity, ShieldAlert } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function AdminPage() {
    const tCommon = useTranslations("common");
    const pathname = usePathname();
    const basePath = pathname.split('/admin')[0];

    return (
        <div className="max-w-7xl mx-auto p-6 space-y-8 mt-6">
            <div className="flex flex-col gap-2">
                <h1 className="text-3xl font-bold tracking-tight text-slate-900">Admin Dashboard</h1>
                <p className="text-muted-foreground text-sm">
                    Manage users, configure settings, and monitor the platform.
                </p>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card className="hover:border-primary/50 transition-colors">
                    <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                        <CardTitle className="text-sm font-medium">Total Users</CardTitle>
                        <Users className="w-4 h-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">Manage users</div>
                        <p className="text-xs text-muted-foreground mt-1">
                            <Link href={`${basePath}/admin/users`} className="text-primary hover:underline">View all users →</Link>
                        </p>
                    </CardContent>
                </Card>

                <Card className="hover:border-primary/50 transition-colors">
                    <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                        <CardTitle className="text-sm font-medium">Data Entities</CardTitle>
                        <Database className="w-4 h-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">Manage sectors</div>
                        <p className="text-xs text-muted-foreground mt-1">
                            <Link href={`${basePath}/admin/data`} className="text-primary hover:underline">Go to data section →</Link>
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0 opacity-50">
                        <CardTitle className="text-sm font-medium">System Health</CardTitle>
                        <Activity className="w-4 h-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent className="opacity-50">
                        <div className="text-2xl font-bold">Normal</div>
                        <p className="text-xs text-muted-foreground mt-1">
                            All services running smoothly
                        </p>
                    </CardContent>
                </Card>

                <Card className="border-red-200 bg-red-50/50">
                    <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                        <CardTitle className="text-sm font-medium text-red-800">Security Logs</CardTitle>
                        <ShieldAlert className="w-4 h-4 text-red-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-red-900">0 Alerts</div>
                        <p className="text-xs text-red-600/80 mt-1">
                            No recent security events
                        </p>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
