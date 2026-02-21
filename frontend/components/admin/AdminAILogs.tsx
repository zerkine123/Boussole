"use client";

import { useState, useEffect } from "react";
import { format } from "date-fns";
import {
    Table, TableBody, TableCell, TableHead, TableHeader, TableRow
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { API_BASE_URL as baseUrl } from "@/lib/api";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

interface IntentLog {
    id: number;
    query: string;
    provider: string;
    model_name: string;
    latency_ms: number | null;
    confidence: number | null;
    parsed_intent: Record<string, any>;
    is_accurate: boolean | null;
    feedback_notes: string | null;
    created_at: string;
}

export default function AdminAILogs() {
    const [logs, setLogs] = useState<IntentLog[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchLogs = async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem("access_token");
            const res = await fetch(`${baseUrl}/api/v1/admin/ai/audits`, {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            if (res.ok) {
                const data = await res.json();
                setLogs(data);
            }
        } catch (error) {
            console.error("Failed to fetch intent logs:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchLogs();
    }, []);

    return (
        <div className="space-y-4">
            <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold">Parser Audit Log</h2>
                <Button variant="outline" size="sm" onClick={fetchLogs} disabled={loading}>
                    {loading ? "Refreshing..." : "Refresh"}
                </Button>
            </div>

            <div className="border rounded-md bg-white">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Time</TableHead>
                            <TableHead>Query</TableHead>
                            <TableHead>Provider/Model</TableHead>
                            <TableHead>Performance</TableHead>
                            <TableHead>Confidence</TableHead>
                            <TableHead className="text-right">Action</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {logs.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={6} className="text-center h-24 text-muted-foreground">
                                    {loading ? "Loading logs..." : "No LLM interactions logged yet."}
                                </TableCell>
                            </TableRow>
                        ) : (
                            logs.map((log) => (
                                <TableRow key={log.id}>
                                    <TableCell className="whitespace-nowrap text-sm text-muted-foreground">
                                        {format(new Date(log.created_at), 'MMM d, HH:mm:ss')}
                                    </TableCell>
                                    <TableCell className="max-w-xs truncate font-medium">
                                        "{log.query}"
                                    </TableCell>
                                    <TableCell>
                                        <div className="flex flex-col">
                                            <span className="capitalize">{log.provider}</span>
                                            <span className="text-xs text-muted-foreground">{log.model_name}</span>
                                        </div>
                                    </TableCell>
                                    <TableCell>
                                        {log.latency_ms ? (
                                            <Badge variant="secondary" className={log.latency_ms > 2000 ? "text-amber-600 bg-amber-100" : ""}>
                                                {Math.round(log.latency_ms)}ms
                                            </Badge>
                                        ) : "-"}
                                    </TableCell>
                                    <TableCell>
                                        {log.confidence ? (
                                            <span className={log.confidence < 0.5 ? "text-destructive font-medium" : ""}>
                                                {(log.confidence * 100).toFixed(0)}%
                                            </span>
                                        ) : "-"}
                                    </TableCell>
                                    <TableCell className="text-right">
                                        <Dialog>
                                            <DialogTrigger asChild>
                                                <Button variant="ghost" size="sm">View JSON</Button>
                                            </DialogTrigger>
                                            <DialogContent className="max-w-2xl">
                                                <DialogHeader>
                                                    <DialogTitle>Parsed Intent Details</DialogTitle>
                                                </DialogHeader>
                                                <div className="bg-slate-950 text-slate-50 p-4 rounded-md overflow-auto max-h-[60vh]">
                                                    <pre className="text-sm">
                                                        {JSON.stringify(log.parsed_intent, null, 2)}
                                                    </pre>
                                                </div>
                                            </DialogContent>
                                        </Dialog>
                                    </TableCell>
                                </TableRow>
                            ))
                        )}
                    </TableBody>
                </Table>
            </div>
        </div>
    );
}
