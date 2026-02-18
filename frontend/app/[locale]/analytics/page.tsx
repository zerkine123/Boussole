"use client";

import { useTranslations } from "next-intl";
import DashboardLayout from "@/components/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { BarChart3, TrendingUp, Users, Activity } from "lucide-react";

export default function AnalyticsPage() {
    const t = useTranslations("common"); // Using common for now as analytics namespace might be missing

    return (
        <DashboardLayout>
            <div className="bg-primary relative overflow-hidden shadow-sm mb-8">
                <div className="absolute inset-0">
                    <div className="absolute top-[10%] left-[5%] w-72 h-72 bg-white/10 rounded-full blur-3xl" />
                    <div className="absolute top-[20%] right-[10%] w-56 h-56 bg-accent/20 rounded-full blur-3xl" />
                </div>
                <div className="relative px-4 sm:px-8 py-12">
                    <div className="max-w-3xl">
                        <h1 className="text-3xl font-bold text-white mb-2 shadow-sm">
                            Analytics Overview
                        </h1>
                        <p className="text-white/80 text-lg">
                            Deep dive into market trends and performance metrics.
                        </p>
                    </div>
                </div>
            </div>

            <div className="px-4 sm:px-8 space-y-8">
                {/* Placeholder Content */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <Card className="hover:shadow-md transition-all duration-300">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Total Views</CardTitle>
                            <Users className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">12,345</div>
                            <p className="text-xs text-muted-foreground">+18% from last month</p>
                        </CardContent>
                    </Card>
                    <Card className="hover:shadow-md transition-all duration-300">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Active Sessions</CardTitle>
                            <Activity className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">+573</div>
                            <p className="text-xs text-muted-foreground">+201 since last hour</p>
                        </CardContent>
                    </Card>
                    <Card className="hover:shadow-md transition-all duration-300">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Conversion Rate</CardTitle>
                            <TrendingUp className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">2.4%</div>
                            <p className="text-xs text-muted-foreground">+4% from last week</p>
                        </CardContent>
                    </Card>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <Card className="min-h-[300px] flex items-center justify-center border-dashed">
                        <div className="text-center text-muted-foreground">
                            <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
                            <h3 className="text-lg font-medium">Traffic Sources</h3>
                            <p className="text-sm">Chart coming soon...</p>
                        </div>
                    </Card>
                    <Card className="min-h-[300px] flex items-center justify-center border-dashed">
                        <div className="text-center text-muted-foreground">
                            <Activity className="h-12 w-12 mx-auto mb-4 opacity-50" />
                            <h3 className="text-lg font-medium">User Engagement</h3>
                            <p className="text-sm">Chart coming soon...</p>
                        </div>
                    </Card>
                </div>
            </div>
        </DashboardLayout>
    );
}
