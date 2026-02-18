"use client";

import { useTranslations } from "next-intl";
import DashboardLayout from "@/components/DashboardLayout";
import { Card } from "@/components/ui/card";
import { Bot, Send, User, Sparkles, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState, useRef, useEffect } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ChatMessage {
    role: "user" | "assistant";
    content: string;
    timestamp: Date;
}

const SUGGESTED_PROMPTS = [
    "What are the key economic sectors in Algeria?",
    "Tell me about startups in Algiers",
    "How many business entities are registered in Algeria?",
    "What is the agriculture growth rate?",
    "Compare Oran and Constantine economies",
    "How many incubators exist in Algeria?",
];

export default function RagPage() {
    const t = useTranslations("common");

    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [inputValue, setInputValue] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [hasStarted, setHasStarted] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    // Auto-scroll to bottom when messages change
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, isLoading]);

    // Focus input when chat starts
    useEffect(() => {
        if (hasStarted) {
            inputRef.current?.focus();
        }
    }, [hasStarted]);

    const sendMessage = async (content: string) => {
        if (!content.trim() || isLoading) return;

        const userMessage: ChatMessage = {
            role: "user",
            content: content.trim(),
            timestamp: new Date(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setInputValue("");
        setIsLoading(true);

        try {
            // Build history (excluding the current message)
            const history = messages.map((m) => ({
                role: m.role,
                content: m.content,
            }));

            const response = await fetch(`${API_BASE_URL}/api/v1/chat/completion`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: content.trim(),
                    history,
                }),
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }

            const data = await response.json();

            const assistantMessage: ChatMessage = {
                role: "assistant",
                content: data.reply,
                timestamp: new Date(),
            };

            setMessages((prev) => [...prev, assistantMessage]);
        } catch (error) {
            console.error("Chat error:", error);
            const errorMessage: ChatMessage = {
                role: "assistant",
                content:
                    "I'm sorry, I encountered an error. Please check that the backend server is running and try again.",
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        sendMessage(inputValue);
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage(inputValue);
        }
    };

    const startConversation = () => {
        setHasStarted(true);
    };

    const clearChat = () => {
        setMessages([]);
        setHasStarted(false);
    };

    // Format markdown-like responses (basic bold, lists)
    const formatContent = (text: string) => {
        // Split into lines for processing
        const lines = text.split("\n");
        return lines.map((line, i) => {
            // Bold text
            let formatted = line.replace(
                /\*\*(.*?)\*\*/g,
                '<strong class="font-semibold">$1</strong>'
            );
            // Bullet points
            if (formatted.startsWith("- ") || formatted.startsWith("* ")) {
                formatted = `<span class="ml-2">•</span> ${formatted.slice(2)}`;
            }
            // Numbered lists
            const numMatch = formatted.match(/^(\d+)\.\s/);
            if (numMatch) {
                formatted = `<span class="font-medium text-primary">${numMatch[1]}.</span> ${formatted.slice(numMatch[0].length)}`;
            }
            return (
                <span key={i}>
                    <span dangerouslySetInnerHTML={{ __html: formatted }} />
                    {i < lines.length - 1 && <br />}
                </span>
            );
        });
    };

    return (
        <DashboardLayout>
            {/* Banner Header */}
            <div className="banner-gradient relative overflow-hidden">
                <div className="absolute inset-0">
                    <div className="absolute top-[10%] left-[5%] w-72 h-72 bg-white/10 rounded-full blur-3xl" />
                    <div className="absolute top-[20%] right-[10%] w-56 h-56 bg-accent/20 rounded-full blur-3xl" />
                </div>
                <div className="relative px-4 sm:px-8 py-8">
                    <div className="flex items-center justify-between max-w-4xl mx-auto">
                        <div>
                            <p className="text-sm text-white/70 mb-1">🤖 AI / Assistant</p>
                            <h1 className="text-2xl font-bold text-white">
                                Boussole AI Assistant
                            </h1>
                            <p className="text-white/70 text-sm mt-1">
                                Ask questions about Algerian market data and economics
                            </p>
                        </div>
                        {hasStarted && messages.length > 0 && (
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={clearChat}
                                className="bg-white/10 border-white/20 text-white hover:bg-white/20"
                            >
                                <Trash2 className="h-4 w-4 mr-1.5" />
                                New Chat
                            </Button>
                        )}
                    </div>
                </div>
            </div>

            {/* Chat Area */}
            <div className="px-4 sm:px-8 py-6 max-w-4xl mx-auto">
                {!hasStarted ? (
                    /* Welcome Screen */
                    <Card className="min-h-[500px] flex flex-col items-center justify-center p-8 text-center space-y-8">
                        <div className="h-20 w-20 rounded-full bg-gradient-to-br from-primary/20 to-emerald-500/20 flex items-center justify-center animate-pulse">
                            <Bot className="h-10 w-10 text-primary" />
                        </div>
                        <div className="space-y-3">
                            <h2 className="text-2xl font-bold">Chat with Boussole AI</h2>
                            <p className="text-muted-foreground max-w-md mx-auto">
                                I can help you explore Algerian market data, understand economic
                                trends, and find relevant statistics across all 58 Wilayas.
                            </p>
                        </div>

                        {/* Suggested Prompts */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg w-full">
                            {SUGGESTED_PROMPTS.slice(0, 4).map((prompt, i) => (
                                <button
                                    key={i}
                                    onClick={() => {
                                        setHasStarted(true);
                                        setTimeout(() => sendMessage(prompt), 100);
                                    }}
                                    className="text-left p-3 rounded-xl border border-gray-200 hover:border-primary/40 hover:bg-primary/5 transition-all text-sm text-muted-foreground hover:text-foreground group"
                                >
                                    <Sparkles className="h-3.5 w-3.5 text-primary/50 group-hover:text-primary inline mr-1.5" />
                                    {prompt}
                                </button>
                            ))}
                        </div>

                        <Button
                            size="lg"
                            className="rounded-full px-8 bg-gradient-to-r from-primary to-emerald-600 hover:from-primary/90 hover:to-emerald-600/90 shadow-lg"
                            onClick={startConversation}
                        >
                            <Bot className="h-5 w-5 mr-2" />
                            Start Conversation
                        </Button>
                    </Card>
                ) : (
                    /* Chat Interface */
                    <Card className="flex flex-col" style={{ height: "calc(100vh - 280px)", minHeight: "500px" }}>
                        {/* Messages Area */}
                        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
                            {messages.length === 0 && (
                                <div className="text-center py-12 space-y-4">
                                    <Bot className="h-8 w-8 text-primary/40 mx-auto" />
                                    <p className="text-sm text-muted-foreground">
                                        Send a message to start the conversation
                                    </p>
                                    {/* Quick suggestions */}
                                    <div className="flex flex-wrap justify-center gap-2 max-w-md mx-auto">
                                        {SUGGESTED_PROMPTS.map((prompt, i) => (
                                            <button
                                                key={i}
                                                onClick={() => sendMessage(prompt)}
                                                className="text-xs px-3 py-1.5 rounded-full border border-gray-200 hover:border-primary/40 hover:bg-primary/5 transition-all text-muted-foreground hover:text-foreground"
                                            >
                                                {prompt}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {messages.map((msg, i) => (
                                <div
                                    key={i}
                                    className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"} animate-fade-in`}
                                >
                                    {msg.role === "assistant" && (
                                        <div className="flex-shrink-0 h-8 w-8 rounded-full bg-gradient-to-br from-primary/20 to-emerald-500/20 flex items-center justify-center mt-1">
                                            <Bot className="h-4 w-4 text-primary" />
                                        </div>
                                    )}
                                    <div
                                        className={`max-w-[80%] rounded-2xl px-4 py-3 ${msg.role === "user"
                                                ? "bg-primary text-white rounded-br-md"
                                                : "bg-gray-100 text-foreground rounded-bl-md"
                                            }`}
                                    >
                                        <div className="text-sm leading-relaxed whitespace-pre-wrap">
                                            {msg.role === "assistant"
                                                ? formatContent(msg.content)
                                                : msg.content}
                                        </div>
                                        <div
                                            className={`text-[10px] mt-1.5 ${msg.role === "user" ? "text-white/60" : "text-muted-foreground/60"
                                                }`}
                                        >
                                            {msg.timestamp.toLocaleTimeString([], {
                                                hour: "2-digit",
                                                minute: "2-digit",
                                            })}
                                        </div>
                                    </div>
                                    {msg.role === "user" && (
                                        <div className="flex-shrink-0 h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center mt-1">
                                            <User className="h-4 w-4 text-primary" />
                                        </div>
                                    )}
                                </div>
                            ))}

                            {/* Typing indicator */}
                            {isLoading && (
                                <div className="flex gap-3 animate-fade-in">
                                    <div className="flex-shrink-0 h-8 w-8 rounded-full bg-gradient-to-br from-primary/20 to-emerald-500/20 flex items-center justify-center">
                                        <Bot className="h-4 w-4 text-primary" />
                                    </div>
                                    <div className="bg-gray-100 rounded-2xl rounded-bl-md px-4 py-3">
                                        <div className="flex gap-1.5 items-center h-5">
                                            <div className="w-2 h-2 rounded-full bg-primary/40 animate-bounce" style={{ animationDelay: "0ms" }} />
                                            <div className="w-2 h-2 rounded-full bg-primary/40 animate-bounce" style={{ animationDelay: "150ms" }} />
                                            <div className="w-2 h-2 rounded-full bg-primary/40 animate-bounce" style={{ animationDelay: "300ms" }} />
                                        </div>
                                    </div>
                                </div>
                            )}

                            <div ref={messagesEndRef} />
                        </div>

                        {/* Input Area */}
                        <div className="border-t border-gray-100 p-4">
                            <form onSubmit={handleSubmit} className="flex gap-3">
                                <input
                                    ref={inputRef}
                                    type="text"
                                    value={inputValue}
                                    onChange={(e) => setInputValue(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                    placeholder="Ask about Algerian market data..."
                                    disabled={isLoading}
                                    className="flex-1 h-11 px-4 text-sm bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50 transition-all disabled:opacity-50"
                                />
                                <Button
                                    type="submit"
                                    disabled={!inputValue.trim() || isLoading}
                                    className="h-11 w-11 rounded-xl bg-gradient-to-r from-primary to-emerald-600 hover:from-primary/90 hover:to-emerald-600/90 p-0"
                                >
                                    <Send className="h-4 w-4" />
                                </Button>
                            </form>
                            <p className="text-[10px] text-muted-foreground/50 text-center mt-2">
                                Powered by Gemini AI · Responses may not always be accurate
                            </p>
                        </div>
                    </Card>
                )}
            </div>
        </DashboardLayout>
    );
}
