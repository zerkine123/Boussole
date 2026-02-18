"use client";

import { useState, useRef, useEffect } from "react";
import { useTranslations } from "next-intl";
import { useLocale } from "next-intl";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import {
  MessageCircle,
  Send,
  X,
  Minimize2,
  Maximize2,
  FileText,
  Download,
  Sparkles,
  Loader2,
  CheckCircle2,
  AlertCircle,
} from "lucide-react";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  sources?: Source[];
  exportable?: boolean;
}

interface Source {
  id: string;
  title: string;
  url?: string;
  type: "document" | "data" | "metric";
  relevance: number;
}

interface AIResponse {
  answer: string;
  sources: Source[];
  data?: any[];
}

export default function AIAssistant() {
  const t = useTranslations("aiAssistant");
  const locale = useLocale();
  const isRTL = locale === "ar";

  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen && !isMinimized && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen, isMinimized]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setError("");
    setIsLoading(true);

    try {
      // Call backend RAG API
      const response = await fetch("/api/v1/rag/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: userMessage.content,
          locale: locale,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to get AI response");
      }

      const data: AIResponse = await response.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.answer,
        timestamp: new Date(),
        sources: data.sources,
        exportable: data.data && data.data.length > 0,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error("AI query error:", err);
      setError(err instanceof Error ? err.message : "Failed to get response");

      // Add error message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: t("error.message"),
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExport = async (message: Message) => {
    if (!message.sources || message.sources.length === 0) return;

    try {
      // Export to Excel
      const filename = `boussole-ai-export-${new Date().toISOString().split("T")[0]}.xlsx`;

      // In production, this would call backend API to generate Excel file
      console.log("Exporting to Excel:", filename);

      alert(`${t("export.success")}: ${filename}`);
    } catch (err) {
      console.error("Export error:", err);
      alert(t("export.error"));
    }
  };

  const getSuggestedQueries = () => [
    t("suggestions.compareWilayas"),
    t("suggestions.trendAnalysis"),
    t("suggestions.sectorOverview"),
    t("suggestions.forecast"),
  ];

  const formatTimestamp = (date: Date) => {
    return new Intl.DateTimeFormat(locale, {
      hour: "2-digit",
      minute: "2-digit",
    }).format(date);
  };

  const getSourceIcon = (type: Source["type"]) => {
    switch (type) {
      case "document":
        return <FileText className="h-4 w-4" />;
      case "data":
        return <Sparkles className="h-4 w-4" />;
      case "metric":
        return <CheckCircle2 className="h-4 w-4" />;
      default:
        return <FileText className="h-4 w-4" />;
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 z-50 bg-blue-600 hover:bg-blue-700 text-white rounded-full p-4 shadow-lg transition-all hover:scale-110"
        title={t("open")}
      >
        <MessageCircle className="h-6 w-6" />
      </button>
    );
  }

  return (
    <div
      className={`fixed bottom-6 right-6 z-50 transition-all ${isRTL ? "left-6 right-auto" : ""}`}
    >
      <Card
        className={`shadow-2xl ${isMinimized ? "w-80" : "w-96 h-[600px]"} flex flex-col`}
      >
        {/* Header */}
        <CardHeader className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5" />
              <CardTitle className="text-lg">{t("title")}</CardTitle>
            </div>
            <div className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-white hover:bg-white/20"
                onClick={() => setIsMinimized(!isMinimized)}
              >
                {isMinimized ? (
                  <Maximize2 className="h-4 w-4" />
                ) : (
                  <Minimize2 className="h-4 w-4" />
                )}
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-white hover:bg-white/20"
                onClick={() => setIsOpen(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>

        {!isMinimized && (
          <>
            {/* Messages */}
            <CardContent className="flex-1 p-4 overflow-hidden">
              <ScrollArea className="h-[420px]" ref={scrollRef}>
                <div className="space-y-4">
                  {messages.length === 0 && (
                    <div className="text-center py-8">
                      <Sparkles className="h-12 w-12 mx-auto mb-4 text-blue-600" />
                      <h3 className="text-lg font-semibold mb-2">
                        {t("welcome.title")}
                      </h3>
                      <p className="text-sm text-muted-foreground mb-6">
                        {t("welcome.subtitle")}
                      </p>

                      {/* Suggested Queries */}
                      <div className="space-y-2">
                        <p className="text-xs text-muted-foreground mb-2">
                          {t("suggestions.title")}
                        </p>
                        {getSuggestedQueries().map((query, index) => (
                          <Button
                            key={index}
                            variant="outline"
                            size="sm"
                            className="w-full text-left justify-start text-sm"
                            onClick={() => setInput(query)}
                          >
                            {query}
                          </Button>
                        ))}
                      </div>
                    </div>
                  )}

                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
                    >
                      <div
                        className={`max-w-[80%] rounded-lg p-3 ${
                          message.role === "user"
                            ? "bg-blue-600 text-white"
                            : "bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                        }`}
                      >
                        <p className="text-sm whitespace-pre-wrap">
                          {message.content}
                        </p>

                        {/* Sources */}
                        {message.sources && message.sources.length > 0 && (
                          <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                            <p className="text-xs text-muted-foreground mb-2">
                              {t("sources")}
                            </p>
                            <div className="flex flex-wrap gap-1">
                              {message.sources.map((source) => (
                                <Badge
                                  key={source.id}
                                  variant="outline"
                                  className="text-xs flex items-center gap-1"
                                >
                                  {getSourceIcon(source.type)}
                                  {source.title}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Export Button */}
                        {message.exportable && (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="mt-2 w-full justify-start"
                            onClick={() => handleExport(message)}
                          >
                            <Download className="h-4 w-4 mr-2" />
                            {t("export.button")}
                          </Button>
                        )}

                        {/* Timestamp */}
                        <p className="text-xs mt-2 opacity-70">
                          {formatTimestamp(message.timestamp)}
                        </p>
                      </div>
                    </div>
                  ))}

                  {/* Loading State */}
                  {isLoading && (
                    <div className="flex justify-start">
                      <div className="bg-gray-100 dark:bg-gray-800 rounded-lg p-3">
                        <div className="flex items-center gap-2">
                          <Loader2 className="h-4 w-4 animate-spin" />
                          <p className="text-sm text-muted-foreground">
                            {t("loading")}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Error State */}
                  {error && (
                    <div className="flex justify-start">
                      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3">
                        <div className="flex items-start gap-2">
                          <AlertCircle className="h-4 w-4 text-red-600 mt-0.5" />
                          <div>
                            <p className="text-sm text-red-800 dark:text-red-200">
                              {error}
                            </p>
                            <Button
                              variant="link"
                              size="sm"
                              className="h-auto p-0 text-red-600 dark:text-red-400"
                              onClick={() => setError("")}
                            >
                              {t("error.dismiss")}
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </ScrollArea>
            </CardContent>

            {/* Input */}
            <div className="p-4 border-t">
              <form onSubmit={handleSubmit} className="flex gap-2">
                <Input
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder={t("input.placeholder")}
                  disabled={isLoading}
                  className="flex-1"
                />
                <Button
                  type="submit"
                  disabled={isLoading || !input.trim()}
                  size="icon"
                >
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </Button>
              </form>
              <p className="text-xs text-muted-foreground mt-2">
                {t("input.disclaimer")}
              </p>
            </div>
          </>
        )}
      </Card>
    </div>
  );
}
