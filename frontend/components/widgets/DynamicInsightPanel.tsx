"use client";

import { Card, CardHeader, CardContent, CardTitle } from "@/components/ui/card";
import { Lightbulb, TrendingUp, AlertTriangle, Info } from "lucide-react";

export function DynamicInsightPanel({ title, text, insight_text, sentiment, type }: any) {
    // Support both naming conventions from the AI schema
    const displayText = text || insight_text || "No insight available for this query.";
    const displayType = sentiment || type || "info";
    let Icon = Info;
    let colorClass = "text-blue-500 bg-blue-50";
    let borderClass = "border-blue-200";

    switch (displayType) {
        case "opportunity":
        case "positive":
            Icon = Lightbulb;
            colorClass = "text-amber-500 bg-amber-50 dark:bg-amber-900/20";
            borderClass = "border-amber-200 dark:border-amber-800";
            break;
        case "trend":
            Icon = TrendingUp;
            colorClass = "text-emerald-500 bg-emerald-50 dark:bg-emerald-900/20";
            borderClass = "border-emerald-200 dark:border-emerald-800";
            break;
        case "risk":
        case "warning":
        case "negative":
            Icon = AlertTriangle;
            colorClass = "text-red-500 bg-red-50 dark:bg-red-900/20";
            borderClass = "border-red-200 dark:border-red-800";
            break;
        case "info":
        default:
            Icon = Info;
            colorClass = "text-blue-500 bg-blue-50 dark:bg-blue-900/20";
            borderClass = "border-blue-200 dark:border-blue-800";
            break;
    }

    return (
        <Card className={`h-full border-l-4 ${borderClass}`}>
            <CardHeader className="pb-2 flex flex-row items-center gap-3">
                <div className={`p-2 rounded-full ${colorClass}`}>
                    <Icon className="h-5 w-5" />
                </div>
                <CardTitle className="text-sm font-semibold m-0 leading-none">
                    {title || "AI Insight"}
                </CardTitle>
            </CardHeader>
            <CardContent>
                <p className="text-sm text-foreground/80 leading-relaxed">
                    {displayText}
                </p>
            </CardContent>
        </Card>
    );
}
