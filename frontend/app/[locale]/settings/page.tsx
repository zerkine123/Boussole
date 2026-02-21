"use client";

import { useTranslations } from "next-intl";
import { useTheme } from "next-themes";
import { useRouter, usePathname } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Settings, Globe, Moon, Bell, Shield } from "lucide-react";

export default function SettingsPage() {
    const t = useTranslations("common");
    const { theme, setTheme } = useTheme();
    const router = useRouter();
    const pathname = usePathname();

    // Extract current locale from pathname (e.g. /en/settings -> en)
    const currentLocale = pathname.split('/')[1] || 'en';

    const handleLanguageChange = (newLocale: string) => {
        // Replace the locale in the URL
        const newPathname = pathname.replace(`/${currentLocale}`, `/${newLocale}`);
        router.push(newPathname);
    };

    return (
        <div className="max-w-4xl mx-auto p-6 mt-6 space-y-6">
            <div>
                <h1 className="text-3xl font-bold tracking-tight">Account Settings</h1>
                <p className="text-muted-foreground mt-1">
                    Manage your platform preferences and configurations.
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                {/* Application Preferences */}
                <Card>
                    <CardHeader>
                        <CardTitle className="text-xl flex items-center gap-2">
                            <Settings className="h-5 w-5 text-primary" /> Application
                        </CardTitle>
                        <CardDescription>Customize how the platform looks and feels.</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">

                        {/* Theme Toggle */}
                        <div className="flex items-center justify-between">
                            <div className="space-y-0.5">
                                <Label className="flex items-center gap-2">
                                    <Moon className="h-4 w-4 text-muted-foreground" /> Dark Mode
                                </Label>
                                <p className="text-sm text-muted-foreground">
                                    Switch between light and dark themes.
                                </p>
                            </div>
                            <Switch
                                checked={theme === "dark"}
                                onCheckedChange={(checked) => setTheme(checked ? "dark" : "light")}
                            />
                        </div>

                        {/* Language Selection */}
                        <div className="flex items-center justify-between">
                            <div className="space-y-0.5">
                                <Label className="flex items-center gap-2">
                                    <Globe className="h-4 w-4 text-muted-foreground" /> Language
                                </Label>
                                <p className="text-sm text-muted-foreground">
                                    Select your preferred language.
                                </p>
                            </div>
                            <Select value={currentLocale} onValueChange={handleLanguageChange}>
                                <SelectTrigger className="w-[120px]">
                                    <SelectValue placeholder="Select Language" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="en">English</SelectItem>
                                    <SelectItem value="fr">Français</SelectItem>
                                    <SelectItem value="ar">العربية</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>

                    </CardContent>
                </Card>

                {/* Notifications */}
                <Card>
                    <CardHeader>
                        <CardTitle className="text-xl flex items-center gap-2">
                            <Bell className="h-5 w-5 text-primary" /> Notifications
                        </CardTitle>
                        <CardDescription>Choose what updates you want to receive.</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="flex items-center justify-between">
                            <div className="space-y-0.5">
                                <Label>Platform Updates</Label>
                                <p className="text-sm text-muted-foreground">
                                    Receive news about new features and data points.
                                </p>
                            </div>
                            <Switch defaultChecked />
                        </div>
                        <div className="flex items-center justify-between">
                            <div className="space-y-0.5">
                                <Label>Data Alerts</Label>
                                <p className="text-sm text-muted-foreground">
                                    Get notified when watched sectors are updated.
                                </p>
                            </div>
                            <Switch defaultChecked />
                        </div>
                        <div className="flex items-center justify-between">
                            <div className="space-y-0.5">
                                <Label>Marketing Emails</Label>
                                <p className="text-sm text-muted-foreground">
                                    Receive promotional offers and newsletters.
                                </p>
                            </div>
                            <Switch />
                        </div>
                    </CardContent>
                </Card>

                {/* Security (Placeholder) */}
                <Card className="md:col-span-2">
                    <CardHeader>
                        <CardTitle className="text-xl flex items-center gap-2">
                            <Shield className="h-5 w-5 text-destructive" /> Security & Privacy
                        </CardTitle>
                        <CardDescription>Manage your account security and data.</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <p className="text-sm text-muted-foreground">
                            Account security features like password changes and 2FA are currently managed by your organization administrator. For emergency freezes, please contact support.
                        </p>
                    </CardContent>
                    <CardFooter className="flex justify-end border-t pt-4">
                        <Button variant="outline" className="text-destructive hover:bg-destructive/10">
                            Request Account Deletion
                        </Button>
                    </CardFooter>
                </Card>

            </div>
        </div>
    );
}
