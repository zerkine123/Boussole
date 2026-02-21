"use client";

import { useState, useEffect } from "react";
import { useTranslations } from "next-intl";
import { BrainCircuit, Activity, DatabaseZap, Text } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import AdminAILogs from "@/components/admin/AdminAILogs";
import AdminStaticIntents from "@/components/admin/AdminStaticIntents";
import AdminSystemPrompts from "@/components/admin/AdminSystemPrompts";
import AdminAIProviders from "@/components/admin/AdminAIProviders";
import { Settings } from "lucide-react";

export default function AdminAIPage() {
    const tCommon = useTranslations("common");

    // We'll manage active tab state to facilitate focused rendering
    const [activeTab, setActiveTab] = useState("logs");

    return (
        <div className="max-w-7xl mx-auto p-6 space-y-6 mt-6">
            <div>
                <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
                    <BrainCircuit className="h-8 w-8 text-primary" /> AI & Intent Intelligence
                </h1>
                <p className="text-muted-foreground mt-1">
                    Manage the AI Intent Router, review parsed logs, bypass the LLM with static maps, and tweak prompts.
                </p>
            </div>

            <Tabs defaultValue="logs" value={activeTab} onValueChange={setActiveTab} className="w-full">
                <TabsList className="grid w-full grid-cols-3 mb-8">
                    <TabsTrigger value="logs" className="flex items-center gap-2">
                        <Activity className="h-4 w-4" /> Audit Logs
                    </TabsTrigger>
                    <TabsTrigger value="static" className="flex items-center gap-2">
                        <DatabaseZap className="h-4 w-4" /> Static Cache
                    </TabsTrigger>
                    <TabsTrigger value="prompts" className="flex items-center gap-2">
                        <Text className="h-4 w-4" /> System Prompts
                    </TabsTrigger>
                    <TabsTrigger value="providers" className="flex items-center gap-2">
                        <Settings className="h-4 w-4" /> AI Providers
                    </TabsTrigger>
                </TabsList>

                <TabsContent value="logs" className="space-y-4">
                    <AdminAILogs />
                </TabsContent>

                <TabsContent value="static" className="space-y-4">
                    <AdminStaticIntents />
                </TabsContent>

                <TabsContent value="prompts" className="space-y-4">
                    <AdminSystemPrompts />
                </TabsContent>

                <TabsContent value="providers" className="space-y-4">
                    <AdminAIProviders />
                </TabsContent>
            </Tabs>
        </div>
    );
}
