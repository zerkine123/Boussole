"use client";

import { useState, useEffect } from "react";
import { format } from "date-fns";
import {
    Table, TableBody, TableCell, TableHead, TableHeader, TableRow
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";

interface StaticIntent {
    id: number;
    keyword: string;
    mapped_intent: Record<string, any>;
    is_active: boolean;
    created_at: string;
}

export function AdminStaticIntents() {
    const [intents, setIntents] = useState<StaticIntent[]>([]);
    const [loading, setLoading] = useState(true);

    const [newKeyword, setNewKeyword] = useState("");
    const [newJson, setNewJson] = useState("{\n  \"sector\": \"general\"\n}");

    const fetchIntents = async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem("access_token");
            const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
            const res = await fetch(`${baseUrl}/api/v1/admin/ai/static`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                setIntents(data);
            }
        } catch (error) {
            console.error("Failed to fetch static intents:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchIntents();
    }, []);

    const handleCreate = async () => {
        try {
            const token = localStorage.getItem("access_token");
            const mapped_intent = JSON.parse(newJson);
            const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
            const res = await fetch(`${baseUrl}/api/v1/admin/ai/static`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify({
                    keyword: newKeyword.toLowerCase().trim(),
                    mapped_intent,
                    is_active: true
                })
            });

            if (res.ok) {
                setNewKeyword("");
                setNewJson("{\n  \"sector\": \"general\"\n}");
                fetchIntents();
            } else {
                const err = await res.json();
                alert(`Error: ${err.detail}`);
            }
        } catch (e) {
            alert("Invalid JSON format");
        }
    };

    const handleDelete = async (id: number) => {
        if (!confirm("Delete this static intent mapping?")) return;
        try {
            const token = localStorage.getItem("access_token");
            const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
            const res = await fetch(`${baseUrl}/api/v1/admin/ai/static/${id}`, {
                method: "DELETE",
                headers: { Authorization: `Bearer ${token}` }
            });
            if (res.ok) fetchIntents();
        } catch (e) {
            console.error(e);
        }
    }

    return (
        <div className="space-y-4">
            <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold">Static Intent Caching</h2>

                <Dialog>
                    <DialogTrigger asChild>
                        <Button>Add Static Mapping</Button>
                    </DialogTrigger>
                    <DialogContent>
                        <DialogHeader>
                            <DialogTitle>Map Keyword to Intent</DialogTitle>
                        </DialogHeader>
                        <div className="space-y-4 mt-4">
                            <div>
                                <label className="text-sm font-medium">Trigger Keyword (exact match)</label>
                                <Input
                                    value={newKeyword}
                                    onChange={(e) => setNewKeyword(e.target.value)}
                                    placeholder="e.g. bakery in algiers"
                                />
                            </div>
                            <div>
                                <label className="text-sm font-medium">Mapped BusinessIntent JSON</label>
                                <Textarea
                                    className="font-mono h-48"
                                    value={newJson}
                                    onChange={(e) => setNewJson(e.target.value)}
                                />
                            </div>
                            <Button onClick={handleCreate} className="w-full">Save Mapping</Button>
                        </div>
                    </DialogContent>
                </Dialog>
            </div>

            <div className="border rounded-md bg-white">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Keyword</TableHead>
                            <TableHead>Status</TableHead>
                            <TableHead>Mapped Intent</TableHead>
                            <TableHead>Created</TableHead>
                            <TableHead className="text-right">Action</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {intents.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={5} className="text-center h-24 text-muted-foreground">
                                    {loading ? "Loading..." : "No static intents configured yet."}
                                </TableCell>
                            </TableRow>
                        ) : (
                            intents.map((intent) => (
                                <TableRow key={intent.id}>
                                    <TableCell className="font-medium text-primary">
                                        "{intent.keyword}"
                                    </TableCell>
                                    <TableCell>
                                        <Badge variant={intent.is_active ? "secondary" : "destructive"}>
                                            {intent.is_active ? "Active" : "Inactive"}
                                        </Badge>
                                    </TableCell>
                                    <TableCell className="max-w-xs truncate text-xs font-mono text-slate-500">
                                        {JSON.stringify(intent.mapped_intent)}
                                    </TableCell>
                                    <TableCell className="whitespace-nowrap text-sm text-muted-foreground">
                                        {format(new Date(intent.created_at), 'MMM d, yyyy')}
                                    </TableCell>
                                    <TableCell className="text-right">
                                        <Button variant="ghost" className="text-destructive h-8 px-2" onClick={() => handleDelete(intent.id)}>
                                            Delete
                                        </Button>
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
