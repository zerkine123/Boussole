"use client";

import React, { useState, useEffect } from "react";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    BarChart,
    Bar,
    Legend
} from "recharts";
import { AlertCircle, Calculator, TrendingUp, DollarSign } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { api } from "@/lib/api";

interface SimulationMetrics {
    initial_investment: number;
    total_profit_3yr: number;
    roi_percent: number;
    break_even_month: number | string;
    net_margin_percent: number;
}

interface CashFlowMonth {
    month: number;
    year: number;
    revenue: number;
    expenses: number;
    net_income: number;
    balance: number;
}

interface SimulationResponse {
    projection: CashFlowMonth[];
    metrics: SimulationMetrics;
}

export function FinancialSimulatorWidget() {
    // State for inputs
    const [investment, setInvestment] = useState(2000000); // 2M DZD
    const [rent, setRent] = useState(80000); // 80k DZD
    const [staff, setStaff] = useState(120000); // 120k DZD
    const [utilities, setUtilities] = useState(20000);
    const [unitCost, setUnitCost] = useState(80); // DZD
    const [unitPrice, setUnitPrice] = useState(250); // DZD
    const [dailySales, setDailySales] = useState(80); // Cups/Units

    // State for results
    const [results, setResults] = useState<SimulationResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const calculate = async () => {
        setLoading(true);
        setError(null);
        try {
            const fixedCosts = rent + staff + utilities;

            const payload = {
                initial_investment: investment,
                monthly_fixed_costs: fixedCosts,
                unit_cost: unitCost,
                unit_price: unitPrice,
                daily_sales: dailySales,
                growth_rate_annual: 0.10,
                years: 3
            };

            const data: SimulationResponse = await api.simulateFinancials(payload);
            setResults(data);
        } catch (err) {
            console.error("Simulation error:", err);
            setError("Failed to calculate simulation. Please check inputs.");
        } finally {
            setLoading(false);
        }
    };

    // Initial calculation
    useEffect(() => {
        calculate();
    }, []); // Run once on mount

    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Input Panel */}
            <Card className="lg:col-span-1">
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Calculator className="h-5 w-5 text-primary" />
                        Simulator Inputs
                    </CardTitle>
                    <CardDescription>Adjust variables to forecast viability</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">

                    <div className="space-y-2">
                        <Label>Initial Investment (DZD)</Label>
                        <Input
                            type="number"
                            value={investment}
                            onChange={(e) => setInvestment(Number(e.target.value))}
                        />
                        <input
                            type="range"
                            min="500000"
                            max="10000000"
                            step="100000"
                            value={investment}
                            onChange={(e) => setInvestment(Number(e.target.value))}
                            className="w-full h-2 bg-secondary rounded-lg appearance-none cursor-pointer accent-primary"
                        />
                    </div>

                    <div className="space-y-2">
                        <Label>Monthly Fixed Costs (Rent + Staff + Utils)</Label>
                        <div className="grid grid-cols-3 gap-2">
                            <div>
                                <span className="text-xs text-muted-foreground">Rent</span>
                                <Input type="number" value={rent} onChange={(e) => setRent(Number(e.target.value))} />
                            </div>
                            <div>
                                <span className="text-xs text-muted-foreground">Staff</span>
                                <Input type="number" value={staff} onChange={(e) => setStaff(Number(e.target.value))} />
                            </div>
                            <div>
                                <span className="text-xs text-muted-foreground">Utils</span>
                                <Input type="number" value={utilities} onChange={(e) => setUtilities(Number(e.target.value))} />
                            </div>
                        </div>
                        <p className="text-xs text-right font-medium text-muted-foreground">
                            Total: {(rent + staff + utilities).toLocaleString()} DZD/mo
                        </p>
                    </div>

                    <div className="space-y-2">
                        <Label>Revenue Model</Label>
                        <div className="grid grid-cols-2 gap-2">
                            <div>
                                <span className="text-xs text-muted-foreground">Unit Price</span>
                                <Input type="number" value={unitPrice} onChange={(e) => setUnitPrice(Number(e.target.value))} />
                            </div>
                            <div>
                                <span className="text-xs text-muted-foreground">Unit Cost</span>
                                <Input type="number" value={unitCost} onChange={(e) => setUnitCost(Number(e.target.value))} />
                            </div>
                        </div>
                    </div>

                    <div className="space-y-2">
                        <Label>Daily Sales Volume (Year 1)</Label>
                        <Input
                            type="number"
                            value={dailySales}
                            onChange={(e) => setDailySales(Number(e.target.value))}
                        />
                        <input
                            type="range"
                            min="10"
                            max="500"
                            step="5"
                            value={dailySales}
                            onChange={(e) => setDailySales(Number(e.target.value))}
                            className="w-full h-2 bg-secondary rounded-lg appearance-none cursor-pointer accent-primary"
                        />
                    </div>

                    <Button onClick={calculate} className="w-full" disabled={loading}>
                        {loading ? "Calculating..." : "Update Projection"}
                    </Button>

                </CardContent>
            </Card>

            {/* Results Panel */}
            <div className="lg:col-span-2 space-y-6">

                {/* KPI Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Card>
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm font-medium">Break-Even Point</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold flex items-center gap-2">
                                {results?.metrics.break_even_month === "Not reached" ? (
                                    <span className="text-destructive">Not Reached</span>
                                ) : (
                                    <>
                                        {results?.metrics.break_even_month} <span className="text-sm font-normal text-muted-foreground">months</span>
                                    </>
                                )}
                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm font-medium">3-Year ROI</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className={`text-2xl font-bold ${(results?.metrics.roi_percent || 0) > 0 ? "text-green-600" : "text-red-600"
                                }`}>
                                {results?.metrics.roi_percent}%
                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm font-medium">Net Margin</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">
                                {results?.metrics.net_margin_percent}%
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Charts */}
                <Card className="h-[400px]">
                    <CardHeader>
                        <CardTitle>Cash Flow Projection (Cumulative)</CardTitle>
                        <CardDescription>Estimated balance over 3 years</CardDescription>
                    </CardHeader>
                    <CardContent className="h-[320px]">
                        {results ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={results.projection}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                    <XAxis dataKey="month" label={{ value: 'Months', position: 'insideBottom', offset: -5 }} />
                                    <YAxis tickFormatter={(value) => `${(value / 1000000).toFixed(1)}M`} />
                                    <Tooltip
                                        formatter={(value: number) => [`${value.toLocaleString()} DZD`, "Balance"]}
                                        labelFormatter={(label) => `Month ${label}`}
                                    />
                                    <Legend />
                                    <Line
                                        type="monotone"
                                        dataKey="balance"
                                        stroke="#2563eb"
                                        strokeWidth={2}
                                        dot={false}
                                        name="Cumulative Balance"
                                    />
                                    {/* Zero line */}
                                    <Line type="monotone" dataKey={() => 0} stroke="#666" strokeDasharray="3 3" strokeWidth={1} dot={false} name="Break-even Line" />
                                </LineChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="flex items-center justify-center h-full text-muted-foreground">
                                No data generated (Click Update)
                            </div>
                        )}
                    </CardContent>
                </Card>

            </div>
        </div>
    );
}
