"use client";

import { useState, useEffect } from "react";
import { useTranslations } from "next-intl";
import {
    Table, TableBody, TableCell, TableHead, TableHeader, TableRow
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { DatabaseZap } from "lucide-react";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { API_BASE_URL as baseUrl } from "@/lib/api";

interface AIProviderConfig {
    id: number;
    provider_name: string;
    api_key: string;
    api_base_url: string | null;
    model_name: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export default function AdminAIProviders() {
    const [providers, setProviders] = useState<AIProviderConfig[]>([]);
    const [loading, setLoading] = useState(true);
    const [isAddOpen, setIsAddOpen] = useState(false);

    // Form state
    const [providerName, setProviderName] = useState("groq");
    const [apiKey, setApiKey] = useState("");
    const [modelName, setModelName] = useState("");
    const [apiBaseUrl, setApiBaseUrl] = useState("");
    const [isActive, setIsActive] = useState(false);

    // Edit state
    const [editingProvider, setEditingProvider] = useState<AIProviderConfig | null>(null);
    const [isEditOpen, setIsEditOpen] = useState(false);

    // Testing state
    const [testResult, setTestResult] = useState<{ success: boolean; message: string; response?: string } | null>(null);
    const [isTesting, setIsTesting] = useState(false);

    const handleTestConnection = async (isEdit: boolean = false) => {
        setIsTesting(true);
        setTestResult(null);
        try {
            const token = localStorage.getItem("access_token");

            const payload = isEdit && editingProvider ? {
                provider_name: editingProvider.provider_name,
                api_key: editingProvider.api_key,
                api_base_url: editingProvider.api_base_url || null,
                model_name: editingProvider.model_name,
                is_active: false
            } : {
                provider_name: providerName,
                api_key: apiKey,
                api_base_url: apiBaseUrl || null,
                model_name: modelName,
                is_active: false
            };

            const res = await fetch(`${baseUrl}/api/v1/admin/ai/providers/test`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            const data = await res.json();
            if (res.ok) {
                setTestResult({
                    success: true,
                    message: "Connection successful!",
                    response: data.response
                });
            } else {
                setTestResult({
                    success: false,
                    message: data.detail || "Connection failed"
                });
            }
        } catch (error: any) {
            setTestResult({
                success: false,
                message: error.message || "An unexpected error occurred"
            });
        } finally {
            setIsTesting(false);
        }
    };

    const fetchProviders = async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem("access_token");
            const res = await fetch(`${baseUrl}/api/v1/admin/ai/providers`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                setProviders(data);
            }
        } catch (error) {
            console.error("Failed to fetch AI providers:", error);
        } finally {
            setLoading(false);
        }
    };

    const [isSeeding, setIsSeeding] = useState(false);
    const [seedMessage, setSeedMessage] = useState<string | null>(null);

    const handleSeed = async () => {
        if (!confirm("This will clear all current metrics and re-seed the database with ~85k representative data rows. Proceed?")) return;
        setIsSeeding(true);
        setSeedMessage(null);
        try {
            const token = localStorage.getItem("access_token");
            const res = await fetch(`${baseUrl}/api/v1/admin/seed-metrics`, {
                method: "POST",
                headers: { Authorization: `Bearer ${token}` }
            });
            const data = await res.json();
            if (res.ok) {
                setSeedMessage(data.message || "Seeding complete!");
            } else {
                setSeedMessage(`Error: ${data.detail || "Seeding failed"}`);
            }
        } catch (error: any) {
            setSeedMessage(`Error: ${error.message}`);
        } finally {
            setIsSeeding(false);
        }
    };

    useEffect(() => {
        fetchProviders();
    }, []);

    const handleCreate = async () => {
        try {
            const token = localStorage.getItem("access_token");

            const payload = {
                provider_name: providerName,
                api_key: apiKey,
                api_base_url: apiBaseUrl || null,
                model_name: modelName,
                is_active: isActive
            };

            const res = await fetch(`${baseUrl}/api/v1/admin/ai/providers`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });
            if (res.ok) {
                setIsAddOpen(false);
                fetchProviders();
                // Reset form
                setProviderName("groq");
                setApiKey("");
                setModelName("");
                setApiBaseUrl("");
            } else {
                alert("Failed to create provider config");
            }
        } catch (error) {
            console.error(error);
        }
    };

    const handleUpdate = async () => {
        if (!editingProvider) return;
        try {
            const token = localStorage.getItem("access_token");

            const payload = {
                model_name: editingProvider.model_name,
                api_key: editingProvider.api_key,
                api_base_url: editingProvider.api_base_url,
                is_active: editingProvider.is_active
            };

            const res = await fetch(`${baseUrl}/api/v1/admin/ai/providers/${editingProvider.id}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                setIsEditOpen(false);
                fetchProviders();
            } else {
                alert("Failed to update provider config");
            }
        } catch (error) {
            console.error(error);
        }
    };

    const handleDelete = async (id: number) => {
        if (!confirm("Are you sure you want to delete this provider configuration?")) return;
        try {
            const token = localStorage.getItem("access_token");
            const res = await fetch(`${baseUrl}/api/v1/admin/ai/providers/${id}`, {
                method: "DELETE",
                headers: { Authorization: `Bearer ${token}` }
            });
            if (res.ok) {
                fetchProviders();
            }
        } catch (error) {
            console.error("Failed to delete", error);
        }
    };

    const handleActivate = async (id: number) => {
        try {
            const token = localStorage.getItem("access_token");

            const res = await fetch(`${baseUrl}/api/v1/admin/ai/providers/${id}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify({ is_active: true })
            });

            if (res.ok) {
                fetchProviders();
            }
        } catch (error) {
            console.error(error);
        }
    };

    return (
        <div className="space-y-6">
            <Card className="border-emerald-200 bg-emerald-50/30">
                <CardHeader className="pb-3">
                    <CardTitle className="text-lg flex items-center gap-2">
                        <DatabaseZap className="h-5 w-5 text-emerald-600" />
                        Database Infrastructure
                    </CardTitle>
                    <CardDescription>
                        Populate your platform with representative market data. This is required for the Dashboard and Data Explorer to function correctly.
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="flex items-center gap-4">
                        <Button
                            onClick={handleSeed}
                            disabled={isSeeding}
                            className="bg-emerald-600 hover:bg-emerald-700 text-white"
                        >
                            {isSeeding ? "Seeding Database..." : "Seed Database (85k rows)"}
                        </Button>
                        {seedMessage && (
                            <p className={`text-sm font-medium ${seedMessage.includes("Error") ? "text-red-600" : "text-emerald-700"}`}>
                                {seedMessage}
                            </p>
                        )}
                    </div>
                </CardContent>
            </Card>

            <div className="space-y-4">
                <div className="flex justify-between items-center">
                    <h2 className="text-xl font-semibold">LLM Providers</h2>
                    <div className="space-x-2">
                        <Button variant="outline" size="sm" onClick={fetchProviders} disabled={loading}>
                            Refresh
                        </Button>
                        <Dialog open={isAddOpen} onOpenChange={setIsAddOpen}>
                            <DialogTrigger asChild>
                                <Button size="sm">Add Provider Config</Button>
                            </DialogTrigger>
                            <DialogContent>
                                <DialogHeader>
                                    <DialogTitle>Add New Provider Configuration</DialogTitle>
                                </DialogHeader>
                                <div className="space-y-4 py-4">
                                    <div className="space-y-2">
                                        <Label>Provider</Label>
                                        <select
                                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background"
                                            value={providerName}
                                            onChange={(e) => setProviderName(e.target.value)}
                                        >
                                            <option value="groq">Groq</option>
                                            <option value="openai">OpenAI</option>
                                            <option value="azure">Azure / Microsoft Foundry</option>
                                            <option value="gemini">Google Gemini</option>
                                            <option value="anthropic">Anthropic Claude</option>
                                        </select>
                                    </div>
                                    <div className="space-y-2">
                                        <Label>API Key</Label>
                                        <Input
                                            type="password"
                                            placeholder="sk-..."
                                            value={apiKey}
                                            onChange={e => setApiKey(e.target.value)}
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <Label>Model Name</Label>
                                        <Input
                                            placeholder="mixtral-8x7b-32768, gpt-4o, etc."
                                            value={modelName}
                                            onChange={e => setModelName(e.target.value)}
                                        />
                                        <p className="text-xs text-muted-foreground">For Azure, use your Deployment Name here.</p>
                                    </div>
                                    {providerName === "azure" && (
                                        <div className="space-y-2">
                                            <Label>Azure Endpoint Base URL</Label>
                                            <Input
                                                placeholder="https://YOUR_RESOURCE_NAME.openai.azure.com/"
                                                value={apiBaseUrl}
                                                onChange={e => setApiBaseUrl(e.target.value)}
                                            />
                                        </div>
                                    )}
                                    <div className="flex items-center space-x-2 pt-2">
                                        <input
                                            type="checkbox"
                                            id="active-check"
                                            checked={isActive}
                                            onChange={e => setIsActive(e.target.checked)}
                                            className="h-4 w-4 rounded border-gray-300"
                                        />
                                        <Label htmlFor="active-check">Set as Active Global Provider</Label>
                                    </div>

                                    {testResult && !isEditOpen && (
                                        <div className={`p-3 rounded-md text-sm ${testResult.success ? "bg-green-50 text-green-900 border border-green-200" : "bg-red-50 text-red-900 border border-red-200"}`}>
                                            <p className="font-semibold">{testResult.message}</p>
                                            {testResult.response && <p className="mt-1 text-xs opacity-80">AI Response: "{testResult.response}"</p>}
                                        </div>
                                    )}

                                    <div className="flex gap-2">
                                        <Button variant="secondary" className="w-1/3" onClick={() => handleTestConnection(false)} disabled={isTesting || !apiKey || !modelName}>
                                            {isTesting ? "Testing..." : "Test"}
                                        </Button>
                                        <Button className="w-2/3" onClick={handleCreate}>Save Configuration</Button>
                                    </div>
                                </div>
                            </DialogContent>
                        </Dialog>
                    </div>
                </div>

                {/* Edit Dialog */}
                <Dialog open={isEditOpen} onOpenChange={setIsEditOpen}>
                    <DialogContent>
                        <DialogHeader>
                            <DialogTitle>Edit Provider: {editingProvider?.provider_name}</DialogTitle>
                        </DialogHeader>
                        {editingProvider && (
                            <div className="space-y-4 py-4">
                                <div className="space-y-2">
                                    <Label>API Key</Label>
                                    <Input
                                        type="password"
                                        value={editingProvider.api_key}
                                        onChange={e => setEditingProvider({ ...editingProvider, api_key: e.target.value })}
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label>Model Name</Label>
                                    <Input
                                        value={editingProvider.model_name}
                                        onChange={e => setEditingProvider({ ...editingProvider, model_name: e.target.value })}
                                    />
                                </div>
                                {editingProvider.provider_name === "azure" && (
                                    <div className="space-y-2">
                                        <Label>Azure Endpoint Base URL</Label>
                                        <Input
                                            value={editingProvider.api_base_url || ""}
                                            onChange={e => setEditingProvider({ ...editingProvider, api_base_url: e.target.value })}
                                        />
                                    </div>
                                )}

                                {testResult && isEditOpen && (
                                    <div className={`p-3 rounded-md text-sm ${testResult.success ? "bg-green-50 text-green-900 border border-green-200" : "bg-red-50 text-red-900 border border-red-200"}`}>
                                        <p className="font-semibold">{testResult.message}</p>
                                        {testResult.response && <p className="mt-1 text-xs opacity-80">AI Response: "{testResult.response}"</p>}
                                    </div>
                                )}

                                <div className="flex gap-2">
                                    <Button variant="secondary" className="w-1/3" onClick={() => handleTestConnection(true)} disabled={isTesting || !editingProvider.api_key || !editingProvider.model_name}>
                                        {isTesting ? "Testing..." : "Test"}
                                    </Button>
                                    <Button className="w-2/3" onClick={handleUpdate}>Update Configuration</Button>
                                </div>
                            </div>
                        )}
                    </DialogContent>
                </Dialog>

                <div className="border rounded-md bg-white">
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Provider</TableHead>
                                <TableHead>Model</TableHead>
                                <TableHead>API Key</TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead className="text-right">Actions</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {providers.length === 0 ? (
                                <TableRow>
                                    <TableCell colSpan={5} className="text-center h-24 text-muted-foreground">
                                        {loading ? "Loading..." : "No provider configurations found in database. Using .env defaults."}
                                    </TableCell>
                                </TableRow>
                            ) : (
                                providers.map((provider) => (
                                    <TableRow key={provider.id}>
                                        <TableCell className="font-medium capitalize">
                                            {provider.provider_name}
                                        </TableCell>
                                        <TableCell>
                                            <Badge variant="secondary">{provider.model_name}</Badge>
                                        </TableCell>
                                        <TableCell className="text-muted-foreground text-sm font-mono tracking-wider">
                                            {provider.api_key ? `••••••••${provider.api_key.slice(-4)}` : 'None'}
                                        </TableCell>
                                        <TableCell>
                                            {provider.is_active ? (
                                                <Badge className="bg-green-600">Active</Badge>
                                            ) : (
                                                <Badge variant="secondary">Inactive</Badge>
                                            )}
                                        </TableCell>
                                        <TableCell className="text-right space-x-2">
                                            {!provider.is_active && (
                                                <Button variant="outline" size="sm" onClick={() => handleActivate(provider.id)}>
                                                    Activate
                                                </Button>
                                            )}
                                            <Button variant="ghost" size="sm" onClick={() => {
                                                setEditingProvider(provider);
                                                setIsEditOpen(true);
                                            }}>
                                                Edit
                                            </Button>
                                            <Button variant="ghost" size="sm" className="text-destructive hover:text-destructive" onClick={() => handleDelete(provider.id)}>
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
        </div>
    );
}
