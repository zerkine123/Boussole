"use client";

import { useState, useEffect } from "react";
import { useTranslations } from "next-intl";
import { User, Mail, Shield, CheckCircle2, UserCircle, Calendar, CreditCard } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import api from "@/lib/api";

interface UserProfile {
    id: number;
    email: string;
    first_name: string;
    last_name: string;
    phone_number: string | null;
    is_active: boolean;
    is_superuser: boolean;
    subscription_plan: string;
    subscription_status: string;
    created_at: string;
}

export default function ProfilePage() {
    const t = useTranslations("common");
    const [profile, setProfile] = useState<UserProfile | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const token = localStorage.getItem("access_token");
                if (!token) {
                    setLoading(false);
                    return;
                }

                // Using the api client
                const data = await api.getMe(token) as UserProfile;
                setProfile(data);
            } catch (error) {
                console.error("Failed to fetch profile:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchProfile();
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[50vh]">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
        );
    }

    if (!profile) {
        return (
            <div className="max-w-4xl mx-auto p-6 mt-6">
                <Card>
                    <CardContent className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                        <UserCircle className="h-12 w-12 mb-4" />
                        <p>Unable to load profile information. Please verify you are logged in.</p>
                    </CardContent>
                </Card>
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto p-6 mt-6 space-y-6">
            <div>
                <h1 className="text-3xl font-bold tracking-tight">Your Profile</h1>
                <p className="text-muted-foreground mt-1">
                    Manage your personal information and subscription details.
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card className="md:col-span-2">
                    <CardHeader>
                        <CardTitle className="text-xl flex items-center gap-2">
                            <User className="h-5 w-5 text-primary" /> Personal Information
                        </CardTitle>
                        <CardDescription>Your basic account details.</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="flex items-center gap-4 p-4 border rounded-lg bg-slate-50/50 dark:bg-slate-900/50">
                            <div className="h-16 w-16 bg-primary/10 rounded-full flex items-center justify-center">
                                <span className="text-2xl font-bold text-primary">
                                    {(profile.first_name?.[0] || profile.email[0]).toUpperCase()}
                                </span>
                            </div>
                            <div>
                                <h3 className="font-semibold text-lg">{profile.first_name} {profile.last_name}</h3>
                                <p className="text-sm text-muted-foreground">{profile.is_superuser ? 'Administrator' : 'General User'}</p>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div className="space-y-1">
                                <label className="text-xs font-medium text-muted-foreground flex items-center gap-1.5 hover:text-foreground transition-colors">
                                    <Mail className="h-3.5 w-3.5" /> Email Address
                                </label>
                                <p className="text-sm font-medium">{profile.email}</p>
                            </div>

                            <div className="space-y-1">
                                <label className="text-xs font-medium text-muted-foreground flex items-center gap-1.5 hover:text-foreground transition-colors">
                                    <Shield className="h-3.5 w-3.5" /> Account Role
                                </label>
                                <div className="flex items-center gap-2">
                                    <Badge variant={profile.is_superuser ? "default" : "secondary"}>
                                        {profile.is_superuser ? "Admin" : "User"}
                                    </Badge>
                                </div>
                            </div>

                            <div className="space-y-1">
                                <label className="text-xs font-medium text-muted-foreground flex items-center gap-1.5 hover:text-foreground transition-colors">
                                    <CheckCircle2 className="h-3.5 w-3.5" /> Account Status
                                </label>
                                <div className="flex items-center gap-2">
                                    <Badge variant={profile.is_active ? "default" : "destructive"} className={profile.is_active ? "bg-green-100 text-green-800 hover:bg-green-100" : ""}>
                                        {profile.is_active ? "Active" : "Inactive"}
                                    </Badge>
                                </div>
                            </div>

                            <div className="space-y-1">
                                <label className="text-xs font-medium text-muted-foreground flex items-center gap-1.5 hover:text-foreground transition-colors">
                                    <Calendar className="h-3.5 w-3.5" /> Member Since
                                </label>
                                <p className="text-sm font-medium">
                                    {new Date(profile.created_at).toLocaleDateString(undefined, {
                                        year: 'numeric',
                                        month: 'long',
                                        day: 'numeric'
                                    })}
                                </p>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle className="text-xl flex items-center gap-2">
                            <CreditCard className="h-5 w-5 text-primary" /> Subscription
                        </CardTitle>
                        <CardDescription>Your current plan.</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="flex flex-col items-center p-6 border rounded-lg bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
                            <Badge variant="outline" className="mb-4 uppercase tracking-wider text-xs font-bold px-3 py-1">
                                {profile.subscription_status}
                            </Badge>
                            <h3 className="text-2xl font-bold text-center capitalize">
                                {profile.subscription_plan} Plan
                            </h3>
                            <p className="text-center text-sm text-muted-foreground mt-2">
                                {profile.subscription_plan === 'free'
                                    ? 'Basic access to application features.'
                                    : 'Full access to premium analytics and insights.'}
                            </p>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
