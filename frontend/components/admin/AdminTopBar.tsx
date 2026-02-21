"use client";

import { usePathname } from "next/navigation";
import { useLocale, useTranslations } from "next-intl";
import Link from "next/link";
import {
    LayoutDashboard,
    Database,
    Users,
    Compass,
    Bell,
    ChevronDown,
    Menu,
    X,
    Settings,
    LogOut,
    Shield,
    BrainCircuit
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

const adminNavItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard, href: "/admin" },
    { id: "users", label: "Users", icon: Users, href: "/admin/users" },
    { id: "data", label: "Data Management", icon: Database, href: "/admin/data" },
    { id: "ai", label: "AI Config", icon: BrainCircuit, href: "/admin/ai" },
];

export default function AdminTopBar() {
    const pathname = usePathname();
    const locale = useLocale();
    const tCommon = useTranslations("common");
    const tNav = useTranslations("nav");
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const menuRef = useRef<HTMLDivElement>(null);

    const isActive = (href: string) => {
        if (href === "/admin") {
            return pathname === `/${locale}/admin`;
        }
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
            <div className="bg-slate-900/95 backdrop-blur-md border-b border-white/10 shadow-sm transition-all duration-300">
                <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-16 lg:h-[72px]">

                        {/* Left: Logo + Brand */}
                        <div className="flex items-center gap-3">
                            <div className="h-9 w-9 rounded-xl bg-red-500/20 backdrop-blur-sm flex items-center justify-center border border-red-500/30 shadow-inner">
                                <Shield className="h-5 w-5 text-red-400" />
                            </div>
                            <Link href={`/${locale}/admin`} className="flex flex-col">
                                <span className="text-lg font-bold text-white tracking-tight leading-tight">
                                    {tCommon("appName")} Admin
                                </span>
                                <span className="text-[10px] text-red-300/80 font-medium tracking-widest uppercase hidden sm:block">
                                    Control Panel
                                </span>
                            </Link>
                        </div>

                        {/* Center: Desktop Navigation */}
                        <nav className="hidden md:flex items-center gap-1">
                            {adminNavItems.map((item) => {
                                const Icon = item.icon;
                                const active = isActive(item.href);
                                return (
                                    <Link
                                        key={item.id}
                                        href={`/${locale}${item.href}`}
                                        className={cn(
                                            "relative flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 group",
                                            active
                                                ? "text-slate-900 bg-white shadow-sm"
                                                : "text-white/80 hover:text-white hover:bg-white/10"
                                        )}
                                    >
                                        <Icon className="h-4 w-4" />
                                        <span>{item.label}</span>
                                    </Link>
                                );
                            })}
                        </nav>

                        {/* Right: Actions */}
                        <div className="flex items-center gap-2 sm:gap-3">
                            <Link href={`/${locale}/dashboard`} className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium text-white/80 hover:text-white hover:bg-white/10 transition-colors border border-white/20">
                                <Compass className="h-4 w-4" />
                                <span>Exit Admin</span>
                            </Link>

                            {/* User Avatar — desktop */}
                            <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                    <button className="hidden sm:flex items-center gap-2.5 pl-3 pr-2 py-1.5 rounded-full hover:bg-white/10 transition-colors border border-transparent hover:border-white/10 outline-none">
                                        <div className="h-8 w-8 rounded-full bg-red-500 text-white flex items-center justify-center text-xs font-bold shadow-sm">
                                            A
                                        </div>
                                        <div className="hidden lg:block text-left">
                                            <div className="text-sm font-medium text-white leading-tight">
                                                Superuser
                                            </div>
                                        </div>
                                        <ChevronDown className="h-3.5 w-3.5 text-white/70 hidden lg:block" />
                                    </button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end" className="w-56">
                                    <DropdownMenuLabel>Admin Profile</DropdownMenuLabel>
                                    <DropdownMenuSeparator />
                                    <Link href={`/${locale}/dashboard`}>
                                        <DropdownMenuItem className="cursor-pointer">
                                            <Compass className="mr-2 h-4 w-4" />
                                            <span>Return to App</span>
                                        </DropdownMenuItem>
                                    </Link>
                                    <DropdownMenuSeparator />
                                    <Link href="/login">
                                        <DropdownMenuItem className="cursor-pointer text-red-600 focus:text-red-600">
                                            <LogOut className="mr-2 h-4 w-4" />
                                            <span>{tNav("logout")}</span>
                                        </DropdownMenuItem>
                                    </Link>
                                </DropdownMenuContent>
                            </DropdownMenu>

                            {/* Mobile menu toggle */}
                            <button
                                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                                className="md:hidden p-2 rounded-lg text-white/80 hover:text-white hover:bg-white/10 transition-colors"
                            >
                                {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Mobile Navigation Menu */}
            <div
                className={cn(
                    "md:hidden overflow-hidden transition-all duration-300 ease-in-out bg-slate-800/95 backdrop-blur-md border-t border-white/5",
                    mobileMenuOpen ? "max-h-[400px] opacity-100" : "max-h-0 opacity-0"
                )}
            >
                <div className="px-4 py-3 space-y-1">
                    {/* Mobile Nav Links */}
                    {adminNavItems.map((item) => {
                        const Icon = item.icon;
                        const active = isActive(item.href);
                        return (
                            <Link
                                key={item.id}
                                href={`/${locale}${item.href}`}
                                className={cn(
                                    "flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200",
                                    active
                                        ? "text-slate-900 bg-white shadow-sm"
                                        : "text-white/80 hover:text-white hover:bg-white/10"
                                )}
                            >
                                <Icon className="h-5 w-5" />
                                <span>{item.label}</span>
                            </Link>
                        );
                    })}

                    {/* Mobile User Info */}
                    <div className="border-t border-white/5 pt-3 mt-2 space-y-1">
                        <Link href={`/${locale}/dashboard`} className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium text-white/80 hover:text-white hover:bg-white/10 transition-all">
                            <Compass className="h-5 w-5" />
                            <span>Return to App</span>
                        </Link>
                        <Link href="/login" className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium text-red-400 hover:text-red-300 hover:bg-white/10 transition-all">
                            <LogOut className="h-5 w-5" />
                            <span>{tNav("logout")}</span>
                        </Link>
                    </div>
                </div>
            </div>
        </header>
    );
}
