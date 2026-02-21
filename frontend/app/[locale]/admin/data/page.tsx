"use client";

import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { Database, FolderTree, BarChart2, Globe } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function AdminDataPage() {
    const tCommon = useTranslations("common");

    return (
        <div className="max-w-7xl mx-auto p-6 space-y-8 mt-6">
            <div>
                <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
                    <Database className="h-8 w-8 text-primary" /> Data Management
                </h1>
                <p className="text-muted-foreground mt-1">
                    Manage taxonomy, geographic entities, and core platform metrics.
                </p>
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <FolderTree className="h-5 w-5 text-blue-500" />
                            Sectors
                        </CardTitle>
                        <CardDescription>Manage industry sectors and their definitions.</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <p className="text-sm text-muted-foreground">Add new sectors or modify existing ones. Changes immediately reflect across the platform.</p>
                    </CardContent>
                    <CardFooter>
                        <Button variant="outline" className="w-full" asChild>
                            <Link href="/admin/data/sectors">Manage Sectors</Link>
                        </Button>
                    </CardFooter>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <BarChart2 className="h-5 w-5 text-indigo-500" />
                            Indicators & Metrics
                        </CardTitle>
                        <CardDescription>Configure data indicators and their formatting.</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <p className="text-sm text-muted-foreground">Set up KPI definitions, units of measurement, and default visualizations.</p>
                    </CardContent>
                    <CardFooter>
                        <Button variant="outline" className="w-full">Manage Indicators</Button>
                    </CardFooter>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Globe className="h-5 w-5 text-emerald-500" />
                            Geographic Data
                        </CardTitle>
                        <CardDescription>Manage Wilayas and regions.</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <p className="text-sm text-muted-foreground">Update regional boundaries, names, and general localized metadata.</p>
                    </CardContent>
                    <CardFooter>
                        <Button variant="outline" className="w-full">Manage Regions</Button>
                    </CardFooter>
                </Card>
            </div>
        </div>
    );
}
