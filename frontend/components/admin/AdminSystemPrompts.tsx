"use client";

import { useState, useEffect } from "react";
import { format } from "date-fns";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { History } from "lucide-react";

interface SystemPrompt {
    id: number;
    name: string;
    content: string;
    description: string;
    version: number;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export function AdminSystemPrompts() {
    const [prompts, setPrompts] = useState<SystemPrompt[]>([]);
    const [loading, setLoading] = useState(true);
    const [editingPrompt, setEditingPrompt] = useState<SystemPrompt | null>(null);
    const [editContent, setEditContent] = useState("");

    const fetchPrompts = async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem("access_token");
            const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
            const res = await fetch(`${baseUrl}/api/v1/admin/ai/prompts`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                setPrompts(data);
            }
        } catch (error) {
            console.error("Failed to fetch system prompts:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchPrompts();
    }, []);

    const handleEdit = (prompt: SystemPrompt) => {
        setEditingPrompt(prompt);
        setEditContent(prompt.content);
    };

    const handleSave = async () => {
        if (!editingPrompt) return;

        try {
            const token = localStorage.getItem("access_token");
            const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
            const res = await fetch(`${baseUrl}/api/v1/admin/ai/prompts`, {
                method: "POST", // We create a new version
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify({
                    name: editingPrompt.name,
                    content: editContent,
                    description: editingPrompt.description,
                    is_active: true
                })
            });

            if (res.ok) {
                setEditingPrompt(null);
                fetchPrompts();
            } else {
                const err = await res.json();
                alert(`Error: ${err.detail}`);
            }
        } catch (e) {
            console.error(e);
        }
    };

    return (
        <div className="space-y-4">
            <h2 className="text-xl font-semibold">System Prompt Configuration</h2>
            <p className="text-muted-foreground text-sm mb-6">
                <strong>System Prompts</strong> act as the "brain instructions" for different AI agents in the platform.
                For example, <code>intent_parser</code> controls how the Search Bar categorizes user requests, while <code>ai_assistant</code> controls the personality and knowledge base of the Chatbot. Editing these allows you to tweak the AI's behavior without deploying new code. Saving a prompt creates a new version automatically.
            </p>

            <div className="grid gap-6">
                {loading ? (
                    <div className="text-center p-8 text-muted-foreground">Loading prompts...</div>
                ) : prompts.length === 0 ? (
                    <div className="text-center p-8 text-muted-foreground border rounded-md">
                        No custom system prompts configured yet. Using codebase defaults.
                    </div>
                ) : (
                    prompts.map((prompt) => (
                        <Card key={prompt.id} className="border-primary/20">
                            <CardHeader className="pb-3">
                                <div className="flex justify-between items-start">
                                    <div>
                                        <CardTitle className="flex items-center gap-2">
                                            {prompt.name}
                                            <Badge variant={prompt.is_active ? "secondary" : "outline"}>
                                                v{prompt.version}
                                            </Badge>
                                        </CardTitle>
                                        <CardDescription className="mt-1">{prompt.description || 'Core LLM Instructions'}</CardDescription>
                                    </div>
                                    <div className="text-xs text-muted-foreground flex items-center gap-1">
                                        <History className="h-3 w-3" /> Updated {format(new Date(prompt.created_at), 'MMM d, yyyy HH:mm')}
                                    </div>
                                </div>
                            </CardHeader>
                            <CardContent>
                                {editingPrompt?.id === prompt.id ? (
                                    <Textarea
                                        className="min-h-[300px] font-mono text-sm leading-relaxed"
                                        value={editContent}
                                        onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setEditContent(e.target.value)}
                                    />
                                ) : (
                                    <div className="bg-slate-50 dark:bg-slate-900 rounded-md p-4 text-sm font-mono whitespace-pre-wrap text-slate-700 dark:text-slate-300 border h-64 overflow-y-auto">
                                        {prompt.content}
                                    </div>
                                )}
                            </CardContent>
                            <CardFooter className="flex justify-end gap-2 border-t pt-4">
                                {editingPrompt?.id === prompt.id ? (
                                    <>
                                        <Button variant="outline" onClick={() => setEditingPrompt(null)}>Cancel</Button>
                                        <Button onClick={handleSave}>Save New Version</Button>
                                    </>
                                ) : (
                                    <Button variant="outline" onClick={() => handleEdit(prompt)}>
                                        Edit Prompt
                                    </Button>
                                )}
                            </CardFooter>
                        </Card>
                    ))
                )}
            </div>

            {!loading && (
                <div className="flex justify-center gap-4 mt-8 pt-4 border-t">
                    {!prompts.find(p => p.name === 'intent_parser') && (
                        <Button variant="secondary" onClick={async () => {
                            const token = localStorage.getItem("access_token");
                            const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
                            await fetch(`${baseUrl}/api/v1/admin/ai/prompts`, {
                                method: "POST",
                                headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
                                body: JSON.stringify({
                                    name: "intent_parser",
                                    content: `You are Boussole's AI Intent Parser... (Replace with codebase system prompt or type your own)`,
                                    description: "Core parsing intelligence instructions",
                                    is_active: true
                                })
                            });
                            fetchPrompts();
                        }}>
                            Initialize Intent Parser
                        </Button>
                    )}
                    {!prompts.find(p => p.name === 'ai_assistant') && (
                        <Button variant="secondary" onClick={async () => {
                            const token = localStorage.getItem("access_token");
                            const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
                            await fetch(`${baseUrl}/api/v1/admin/ai/prompts`, {
                                method: "POST",
                                headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
                                body: JSON.stringify({
                                    name: "ai_assistant",
                                    content: `You are Boussole AI, the intelligent assistant for the Boussole platform — an Algerian Data Analytics SaaS.

Your role:
- Help users understand Algerian market data, economic trends, and business statistics.
- Answer questions about sectors: Agriculture, Energy, Manufacturing, Services, Tourism, Innovation, Consulting.
- Provide context about Algeria's 58 Wilayas and their economic profiles.
- Help interpret data from the Data Explorer.

Guidelines:
- Be concise but informative.
- Use data and numbers when possible.
- Respond in the same language the user writes in.
- Format responses with markdown when helpful.`,
                                    description: "Personality and knowledge base for the Chatbot",
                                    is_active: true
                                })
                            });
                            fetchPrompts();
                        }}>
                            Initialize AI Assistant
                        </Button>
                    )}
                </div>
            )}
        </div>
    );
}
