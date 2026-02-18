"use client";

import { usePathname } from "next/navigation";
import { useLocale, useTranslations } from "next-intl";
import Link from "next/link";
import {
    LayoutDashboard,
    Database,
    BarChart3,
    MessageSquare,
    Compass,
    Search,
    Bell,
    ChevronDown,
    Menu,
    X,
    User,
    Settings,
    LogOut,
} from "lucide-react";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useState, useEffect, useRef } from "react";
import { cn } from "@/lib/utils";

const navItems = [
    { id: "dashboard", icon: LayoutDashboard, href: "/dashboard" },
    { id: "data", icon: Database, href: "/data" },
    { id: "analytics", icon: BarChart3, href: "/analytics" },
    { id: "rag", icon: MessageSquare, href: "/rag" },
];

export default function TopBar() {
    const pathname = usePathname();
    const locale = useLocale();
    const t = useTranslations("nav");
    const tCommon = useTranslations("common");
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const menuRef = useRef<HTMLDivElement>(null);

    const isActive = (href: string) => {
        return pathname.includes(href);
    };

    // Close mobile menu when clicking outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
                setMobileMenuOpen(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    // Close mobile menu on route change
    useEffect(() => {
        setMobileMenuOpen(false);
    }, [pathname]);

    return (
        <header className="sticky top-0 z-50" ref={menuRef}>
            {/* Main bar */}
            <div className="bg-primary/95 backdrop-blur-md border-b border-white/10 shadow-sm transition-all duration-300">
                <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-16 lg:h-[72px]">

                        {/* Left: Logo + Brand */}
                        <div className="flex items-center gap-3">
                            <div className="h-9 w-9 rounded-xl bg-white/10 backdrop-blur-sm flex items-center justify-center border border-white/20 shadow-inner">
                                <Compass className="h-5 w-5 text-white" />
                            </div>
                            <Link href={`/${locale}`} className="flex flex-col">
                                <span className="text-lg font-bold text-white tracking-tight leading-tight">
                                    {tCommon("appName")}
                                </span>
                                <span className="text-[10px] text-white/70 font-medium tracking-widest uppercase hidden sm:block">
                                    Data Analytics
                                </span>
                            </Link>
                        </div>

                        {/* Center: Desktop Navigation */}
                        <nav className="hidden md:flex items-center gap-1">
                            {navItems.map((item) => {
                                const Icon = item.icon;
                                const active = isActive(item.href);
                                return (
                                    <Link
                                        key={item.id}
                                        href={`/${locale}${item.href}`}
                                        className={cn(
                                            "relative flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 group",
                                            active
                                                ? "text-primary bg-white shadow-sm"
                                                : "text-white/80 hover:text-white hover:bg-white/10"
                                        )}
                                    >
                                        <Icon className="h-4 w-4" />
                                        <span>{t(item.id)}</span>
                                        {/* Active indicator bar - removed for pill style */}
                                    </Link>
                                );
                            })}
                        </nav>

                        {/* Right: Actions */}
                        <div className="flex items-center gap-2 sm:gap-3">
                            {/* Notifications */}
                            <button className="relative p-2 rounded-full text-white/80 hover:text-white hover:bg-white/10 transition-colors">
                                <Bell className="h-5 w-5" />
                                <span className="absolute top-1.5 right-1.5 h-2 w-2 bg-red-400 rounded-full ring-2 ring-primary" />
                            </button>

                            {/* User Avatar — desktop */}
                            <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                    <button className="hidden sm:flex items-center gap-2.5 pl-3 pr-2 py-1.5 rounded-full hover:bg-white/10 transition-colors border border-transparent hover:border-white/10 outline-none">
                                        <div className="h-8 w-8 rounded-full bg-white text-primary flex items-center justify-center text-xs font-bold shadow-sm">
                                            U
                                        </div>
                                        <div className="hidden lg:block text-left">
                                            <div className="text-sm font-medium text-white leading-tight">
                                                User
                                            </div>
                                            <div className="text-[11px] text-white/70 leading-tight">
                                                Admin
                                            </div>
                                        </div>
                                        <ChevronDown className="h-3.5 w-3.5 text-white/70 hidden lg:block" />
                                    </button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end" className="w-56">
                                    <DropdownMenuLabel>{t("profile")}</DropdownMenuLabel>
                                    <DropdownMenuSeparator />
                                    <Link href="/profile">
                                        <DropdownMenuItem className="cursor-pointer">
                                            <User className="mr-2 h-4 w-4" />
                                            <span>{t("profile")}</span>
                                        </DropdownMenuItem>
                                    </Link>
                                    <Link href="/settings">
                                        <DropdownMenuItem className="cursor-pointer">
                                            <Settings className="mr-2 h-4 w-4" />
                                            <span>{t("settings")}</span>
                                        </DropdownMenuItem>
                                    </Link>
                                    <DropdownMenuSeparator />
                                    <Link href="/login">
                                        <DropdownMenuItem className="cursor-pointer text-red-600 focus:text-red-600">
                                            <LogOut className="mr-2 h-4 w-4" />
                                            <span>{t("logout")}</span>
                                        </DropdownMenuItem>
                                    </Link>
                                </DropdownMenuContent>
                            </DropdownMenu>

                            {/* Mobile menu toggle */}
                            <button
                                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                                className="md:hidden p-2 rounded-lg text-[#ACBAC4] hover:text-[#F7F8FA] hover:bg-white/5 transition-colors"
                                aria-label="Toggle menu"
                            >
                                {mobileMenuOpen ? (
                                    <X className="h-5 w-5" />
                                ) : (
                                    <Menu className="h-5 w-5" />
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Mobile Navigation Menu */}
            <div
                className={cn(
                    "md:hidden overflow-hidden transition-all duration-300 ease-in-out bg-[#30364F]/95 backdrop-blur-md border-t border-white/5",
                    mobileMenuOpen ? "max-h-[400px] opacity-100" : "max-h-0 opacity-0"
                )}
            >
                <div className="px-4 py-3 space-y-1">
                    {/* Mobile Nav Links */}
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        const active = isActive(item.href);
                        return (
                            <Link
                                key={item.id}
                                href={`/${locale}${item.href}`}
                                className={cn(
                                    "flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200",
                                    active
                                        ? "text-primary bg-white shadow-sm"
                                        : "text-white/80 hover:text-white hover:bg-white/10"
                                )}
                            >
                                <Icon className="h-5 w-5" />
                                <span>{t(item.id)}</span>
                            </Link>
                        );
                    })}

                    {/* Mobile User Info */}
                    <div className="border-t border-white/5 pt-3 mt-2 space-y-1">
                        <div className="flex items-center gap-3 px-4 py-2 mb-2">
                            <div className="h-9 w-9 rounded-full bg-gradient-to-br from-[#E1D9BC] to-[#ACBAC4] flex items-center justify-center text-[#30364F] text-sm font-bold">
                                U
                            </div>
                            <div>
                                <div className="text-sm font-medium text-[#F7F8FA]">User</div>
                                <div className="text-xs text-[#ACBAC4]">Admin</div>
                            </div>
                        </div>

                        <Link href="/profile" className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium text-white/80 hover:text-white hover:bg-white/10 transition-all">
                            <User className="h-5 w-5" />
                            <span>{t("profile")}</span>
                        </Link>
                        <Link href="/settings" className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium text-white/80 hover:text-white hover:bg-white/10 transition-all">
                            <Settings className="h-5 w-5" />
                            <span>{t("settings")}</span>
                        </Link>
                        <Link href="/login" className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium text-red-400 hover:text-red-300 hover:bg-white/10 transition-all">
                            <LogOut className="h-5 w-5" />
                            <span>{t("logout")}</span>
                        </Link>
                    </div>
                </div>
            </div>
        </header>
    );
}
