"use client";

import TopBar from "@/components/TopBar";

interface DashboardLayoutProps {
    children: React.ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
    return (
        <div className="min-h-screen bg-background">
            {/* Top Navigation Bar */}
            <TopBar />

            {/* Page Content — full width */}
            <main className="min-h-[calc(100vh-4.5rem)]">
                {children}
            </main>
        </div>
    );
}
