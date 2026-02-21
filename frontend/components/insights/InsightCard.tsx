"use client";

import { useTranslations } from "next-intl";
import {
    TrendingUp,
    TrendingDown,
    AlertTriangle,
    FileText,
    GitMerge,
    Star
} from "lucide-react";
import {
    Card,
    CardContent,
    CardHeader,
    CardFooter
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export interface InsightData {
    id: number;
    type: "trend" | "anomaly" | "summary" | "correlation";
    title_en: string;
    title_fr: string;
    title_ar: string;
    content_en: string;
    content_fr: string;
    content_ar: string;
    importance_score: number;
    period: string;
    created_at: string;
    sector_name_en?: string;
    sector_name_fr?: string;
    sector_name_ar?: string;
}

interface InsightCardProps {
    insight: InsightData;
    locale: "en" | "fr" | "ar";
}

export function InsightCard({ insight, locale }: InsightCardProps) {
    const t = useTranslations("insights");

    // Resolve localized text
    const title = insight[`title_${locale}` as keyof InsightData] as string;
    const content = insight[`content_${locale}` as keyof InsightData] as string;
    const sectorName = insight[`sector_name_${locale}` as keyof InsightData] as string;

    // Determine icon and color based on type
    const getTypeConfig = () => {
        switch (insight.type) {
            case "trend":
                return {
                    icon: <TrendingUp className="h-5 w-5 text-blue-500" />,
                    bgColor: "bg-blue-50 dark:bg-blue-900/20",
                    borderColor: "border-blue-200 dark:border-blue-800",
                    badgeColor: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
                    label: t("types.trend")
                };
            case "anomaly":
                return {
                    icon: <AlertTriangle className="h-5 w-5 text-amber-500" />,
                    bgColor: "bg-amber-50 dark:bg-amber-900/20",
                    borderColor: "border-amber-200 dark:border-amber-800",
                    badgeColor: "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200",
                    label: t("types.anomaly")
                };
            case "correlation":
                return {
                    icon: <GitMerge className="h-5 w-5 text-purple-500" />,
                    bgColor: "bg-purple-50 dark:bg-purple-900/20",
                    borderColor: "border-purple-200 dark:border-purple-800",
                    badgeColor: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
                    label: t("types.correlation")
                };
            case "summary":
            default:
                return {
                    icon: <FileText className="h-5 w-5 text-emerald-500" />,
                    bgColor: "bg-emerald-50 dark:bg-emerald-900/20",
                    borderColor: "border-emerald-200 dark:border-emerald-800",
                    badgeColor: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200",
                    label: t("types.summary")
                };
        }
    };

    const config = getTypeConfig();

    // Format date
    const date = new Date(insight.created_at).toLocaleDateString(
        locale === "ar" ? "ar-DZ" : locale === "fr" ? "fr-FR" : "en-US",
        { month: "short", day: "numeric", year: "numeric" }
    );

    return (
        <Card className={`overflow-hidden transition-all hover:shadow-md ${config.borderColor}`}>
            <CardHeader className={`pb-3 ${config.bgColor}`}>
                <div className="flex justify-between items-start gap-4">
                    <div className="flex items-center gap-2">
                        <div className="p-2 bg-background rounded-full shadow-sm">
                            {config.icon}
                        </div>
                        <div>
                            <div className="flex items-center gap-2">
                                <Badge variant="secondary" className={`font-medium ${config.badgeColor} hover:${config.badgeColor}`}>
                                    {config.label}
                                </Badge>
                                {sectorName && (
                                    <Badge variant="outline" className="text-xs text-muted-foreground border-muted-foreground/30">
                                        {sectorName}
                                    </Badge>
                                )}
                            </div>
                        </div>
                    </div>
                    <div className="flex items-center gap-1 bg-background/50 backdrop-blur-sm px-2 py-1 rounded-md text-sm font-medium">
                        <Star className="h-3.5 w-3.5 text-yellow-500 fill-yellow-500" />
                        <span>{insight.importance_score.toFixed(1)}</span>
                    </div>
                </div>
                <h3 className="text-lg font-semibold mt-3 text-foreground tracking-tight">
                    {title}
                </h3>
            </CardHeader>

            <CardContent className="pt-4">
                <p className="text-muted-foreground leading-relaxed">
                    {content}
                </p>
            </CardContent>

            <CardFooter className="pt-0 pb-4 text-xs text-muted-foreground flex justify-between">
                <span>{date}</span>
                {insight.period && (
                    <span className="font-medium bg-muted px-2 py-0.5 rounded-full">
                        {insight.period}
                    </span>
                )}
            </CardFooter>
        </Card>
    );
}
