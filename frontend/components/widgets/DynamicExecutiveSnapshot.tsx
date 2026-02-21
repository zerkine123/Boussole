"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Sparkles, TrendingUp, TrendingDown, Minus } from "lucide-react";

export function DynamicExecutiveSnapshot({ title, summary_text, key_metrics = [] }: any) {
    return (
        <Card className="h-full bg-gradient-to-br from-indigo-900 to-slate-900 text-white border-0 overflow-hidden relative">
            <div className="absolute top-0 right-0 p-8 opacity-10 pointer-events-none">
                <Sparkles className="w-48 h-48" />
            </div>

            <CardContent className="p-6 sm:p-8 flex flex-col h-full relative z-10">
                <div className="flex items-center gap-3 mb-4">
                    <div className="p-2 bg-white/10 rounded-lg shrink-0">
                        <Sparkles className="h-5 w-5 text-indigo-300" />
                    </div>
                    <h2 className="text-xl font-bold tracking-tight text-white/90">
                        {title || "Executive Snapshot"}
                    </h2>
                </div>

                <p className="text-indigo-100/80 leading-relaxed text-sm lg:text-base max-w-3xl mb-8 flex-grow">
                    {summary_text || "AI is synthesizing the latest intelligence..."}
                </p>

                {key_metrics && key_metrics.length > 0 && (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-auto">
                        {key_metrics.map((metric: any, i: number) => (
                            <div key={i} className="flex flex-col gap-1 p-4 rounded-xl bg-white/5 border border-white/10 backdrop-blur-md">
                                <span className="text-xs font-medium text-indigo-200/70 uppercase tracking-wider">{metric.label}</span>
                                <div className="flex items-baseline gap-2">
                                    <span className="text-xl md:text-2xl font-bold text-white">{metric.value}</span>
                                    {metric.trend === 'up' && <TrendingUp className="h-4 w-4 text-emerald-400" />}
                                    {metric.trend === 'down' && <TrendingDown className="h-4 w-4 text-red-400" />}
                                    {metric.trend === 'none' && <Minus className="h-4 w-4 text-slate-400" />}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
