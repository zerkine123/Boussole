"use client";

import { useTranslations } from "next-intl";
import { useState, useEffect } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import { api } from "@/lib/api";
import { InsightCard, InsightData } from "@/components/insights/InsightCard";
import { useLocale } from "next-intl";
import { Loader2, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function InsightsPage() {
    const t = useTranslations("insights");
    const locale = useLocale() as "en" | "fr" | "ar";

    const [insights, setInsights] = useState<InsightData[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isGenerating, setIsGenerating] = useState(false);

    const fetchInsights = async () => {
        setIsLoading(true);
        try {
            const token = localStorage.getItem('access_token');
            if (!token) return;

            const response = await api.getInsights(token, { limit: 20 });
            if (response && Array.isArray(response)) {
                setInsights(response);
            }
        } catch (error) {
            console.error("Failed to fetch insights:", error);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchInsights();
    }, []);

    const handleGenerate = async () => {
        setIsGenerating(true);
        try {
            const token = localStorage.getItem('access_token');
            if (!token) return;

            // We trigger a generation for a primary sector, e.g. "agriculture"
            // In a real app, you might have a modal to select the sector to analyze.
            await api.generateInsights(token, {
                sector_slug: "agriculture",
                period_end: new Date().getFullYear().toString()
            });

            // Refresh list
            await fetchInsights();
        } catch (error) {
            console.error("Failed to generate insights:", error);
        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <DashboardLayout>
            <div className="bg-primary relative overflow-hidden shadow-sm">
                <div className="absolute inset-0">
                    <div className="absolute top-[10%] left-[5%] w-72 h-72 bg-white/10 rounded-full blur-3xl" />
                    <div className="absolute top-[20%] right-[10%] w-56 h-56 bg-accent/20 rounded-full blur-3xl" />
                </div>
                <div className="relative px-4 sm:px-8 py-10 sm:py-14">
                    <div className="max-w-2xl mx-auto text-center">
                        <h1 className="text-2xl sm:text-3xl font-bold text-white mb-2 shadow-sm">
                            {t("title")}
                        </h1>
                        <p className="text-sm sm:text-base text-white/80 mb-6">
                            {t("description")}
                        </p>
                        <Button
                            onClick={handleGenerate}
                            className="bg-white text-primary hover:bg-white/90 font-semibold"
                            disabled={isGenerating}
                        >
                            {isGenerating ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    {t("generating")}
                                </>
                            ) : (
                                <>
                                    <RefreshCw className="mr-2 h-4 w-4" />
                                    {t("generate")}
                                </>
                            )}
                        </Button>
                    </div>
                </div>
            </div>

            <div className="px-4 sm:px-8 py-8">
                {isLoading ? (
                    <div className="flex justify-center items-center h-64">
                        <Loader2 className="h-8 w-8 animate-spin text-primary" />
                    </div>
                ) : insights.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {insights.map((insight) => (
                            <InsightCard key={insight.id} insight={insight} locale={locale} />
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-20 bg-muted/30 rounded-2xl border border-dashed border-muted-foreground/30">
                        <p className="text-muted-foreground">{t("noInsights")}</p>
                    </div>
                )}
            </div>
        </DashboardLayout>
    );
}
