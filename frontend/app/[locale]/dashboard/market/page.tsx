"use client";

import { useTranslations } from "next-intl";
import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { useLocale } from "next-intl";
import Link from "next/link";
import {
    Loader2,
    ArrowLeft,
    ExternalLink,
    MapPin,
    Search,
    ShoppingBag,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import DashboardLayout from "@/components/DashboardLayout";

interface OuedknissResult {
    id: string;
    title: string;
    price: number | null;
    priceUnit: string;
    oldPrice: number | null;
    imageUrl: string | null;
    url: string;
    location: string;
    description: string;
    store: string | null;
}

export default function MarketPage() {
    const t = useTranslations("market");
    const locale = useLocale();
    const searchParams = useSearchParams();
    const query = searchParams.get("q") || "";

    const [results, setResults] = useState<OuedknissResult[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState("");
    const [total, setTotal] = useState(0);

    useEffect(() => {
        if (query.trim()) {
            fetchResults(query);
        }
    }, [query]);

    const fetchResults = async (q: string) => {
        setIsLoading(true);
        setError("");
        try {
            const res = await fetch(
                `/api/scrape/ouedkniss?q=${encodeURIComponent(q)}&count=24`
            );
            const data = await res.json();
            if (!res.ok) {
                setError(data.error || t("error"));
                return;
            }
            setResults(data.results || []);
            setTotal(data.total || 0);
        } catch {
            setError(t("error"));
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <DashboardLayout>
            {/* Header */}
            <div className="bg-[#30364F] relative overflow-hidden">
                <div className="absolute inset-0">
                    <div className="absolute top-[10%] left-[5%] w-72 h-72 bg-white/5 rounded-full blur-3xl" />
                    <div className="absolute top-[20%] right-[10%] w-56 h-56 bg-[#E1D9BC]/8 rounded-full blur-3xl" />
                </div>
                <div className="relative px-4 sm:px-8 py-8 sm:py-10">
                    <div className="max-w-6xl mx-auto">
                        <Link
                            href={`/${locale}/dashboard`}
                            className="inline-flex items-center gap-2 text-sm text-[#ACBAC4] hover:text-[#F0F0DB] transition-colors mb-4"
                        >
                            <ArrowLeft className="h-4 w-4" />
                            {t("backToDashboard")}
                        </Link>
                        <div className="flex items-center gap-3 mb-2">
                            <div className="h-10 w-10 rounded-xl bg-orange-500/20 flex items-center justify-center">
                                <ShoppingBag className="h-5 w-5 text-orange-300" />
                            </div>
                            <div>
                                <h1 className="text-xl sm:text-2xl font-bold text-[#F0F0DB]">
                                    {t("title")}
                                </h1>
                                <p className="text-sm text-[#ACBAC4]">
                                    {t("subtitle")}
                                </p>
                            </div>
                        </div>
                        {query && (
                            <div className="mt-3 flex items-center gap-2">
                                <Search className="h-4 w-4 text-[#ACBAC4]" />
                                <span className="text-[#E1D9BC] font-medium">&quot;{query}&quot;</span>
                                <span className="text-[#ACBAC4] text-sm">
                                    · {total} {t("results")}
                                </span>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Results */}
            <div className="px-4 sm:px-8 py-8 max-w-6xl mx-auto">
                {isLoading ? (
                    <div className="flex flex-col items-center justify-center gap-4 py-20">
                        <Loader2 className="h-8 w-8 animate-spin text-[#30364F]" />
                        <p className="text-muted-foreground">{t("loading")}</p>
                    </div>
                ) : error ? (
                    <div className="text-center py-16">
                        <p className="text-destructive mb-4">{error}</p>
                        <button
                            onClick={() => fetchResults(query)}
                            className="px-4 py-2 rounded-lg bg-[#30364F] text-[#F0F0DB] text-sm font-medium hover:bg-[#30364F]/90 transition-colors"
                        >
                            {t("retry")}
                        </button>
                    </div>
                ) : results.length > 0 ? (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                        {results.map((result) => (
                            <MarketResultCard key={result.id} result={result} />
                        ))}
                    </div>
                ) : query ? (
                    <div className="text-center py-20">
                        <div className="h-16 w-16 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-4">
                            <Search className="h-7 w-7 text-gray-400" />
                        </div>
                        <p className="text-lg font-medium text-foreground mb-1">{t("noResults")}</p>
                        <p className="text-sm text-muted-foreground">
                            {t("noResultsHint")}
                        </p>
                    </div>
                ) : null}
            </div>
        </DashboardLayout>
    );
}

function MarketResultCard({ result }: { result: OuedknissResult }) {
    return (
        <a
            href={result.url}
            target="_blank"
            rel="noopener noreferrer"
            className="group block"
        >
            <Card className="overflow-hidden hover:shadow-lg transition-all duration-300 hover:-translate-y-1 h-full">
                {/* Image */}
                {result.imageUrl ? (
                    <div className="relative h-44 w-full overflow-hidden bg-gray-100">
                        <img
                            src={result.imageUrl}
                            alt={result.title}
                            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                            loading="lazy"
                        />
                    </div>
                ) : (
                    <div className="h-44 w-full bg-gray-100 flex items-center justify-center">
                        <ShoppingBag className="h-10 w-10 text-gray-300" />
                    </div>
                )}
                <CardContent className="p-4">
                    <h3 className="text-sm font-medium text-foreground line-clamp-2 mb-2 group-hover:text-[#30364F] transition-colors min-h-[2.5rem]">
                        {result.title}
                    </h3>

                    {/* Price */}
                    {result.price !== null && (
                        <div className="flex items-baseline gap-2 mb-2">
                            <span className="text-lg font-bold text-[#30364F]">
                                {result.price.toLocaleString()} {result.priceUnit}
                            </span>
                            {result.oldPrice && result.oldPrice > 0 && (
                                <span className="text-xs text-muted-foreground line-through">
                                    {result.oldPrice.toLocaleString()} {result.priceUnit}
                                </span>
                            )}
                        </div>
                    )}

                    {/* Footer */}
                    <div className="flex items-center justify-between pt-2 border-t border-border/50">
                        {result.location && (
                            <div className="flex items-center gap-1 text-xs text-muted-foreground">
                                <MapPin className="h-3 w-3" />
                                <span className="truncate max-w-[140px]">{result.location}</span>
                            </div>
                        )}
                        <ExternalLink className="h-3.5 w-3.5 text-muted-foreground/50 group-hover:text-[#30364F] transition-colors shrink-0" />
                    </div>
                </CardContent>
            </Card>
        </a>
    );
}
