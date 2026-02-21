"use client";

import { useState, useEffect } from "react";
import { FolderTree, Plus, MoreHorizontal, Pencil, Trash2, ArrowLeft } from "lucide-react";
import { Link } from "@/i18n/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import api from "@/lib/api";

interface Sector {
    id: number;
    name_en: string;
    name_ar: string;
    name_fr: string;
    slug: string;
    description: string | null;
    is_active: boolean;
    icon: string;
}

export default function AdminSectorsPage() {
    const [sectors, setSectors] = useState<Sector[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const [editingSector, setEditingSector] = useState<Sector | null>(null);
    const [formData, setFormData] = useState({
        name_en: "",
        name_ar: "",
        name_fr: "",
        slug: "",
        icon: "Briefcase",
        description: "",
        is_active: true
    });

    const fetchSectors = async () => {
        setIsLoading(true);
        try {
            const token = localStorage.getItem("access_token");
            if (!token) return;
            const data = await api.getSectors(token);
            setSectors(data as Sector[]);
        } catch (error) {
            console.error("Error fetching sectors:", error);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchSectors();
    }, []);

    const handleOpenDialog = (sector?: Sector) => {
        if (sector) {
            setEditingSector(sector);
            setFormData({
                name_en: sector.name_en,
                name_ar: sector.name_ar,
                name_fr: sector.name_fr,
                slug: sector.slug,
                icon: sector.icon || "Briefcase",
                description: sector.description || "",
                is_active: sector.is_active
            });
        } else {
            setEditingSector(null);
            setFormData({
                name_en: "",
                name_ar: "",
                name_fr: "",
                slug: "",
                icon: "Briefcase",
                description: "",
                is_active: true
            });
        }
        setIsDialogOpen(true);
    };

    const handleSave = async () => {
        try {
            const token = localStorage.getItem("access_token");
            if (!token) return;

            if (editingSector) {
                await api.updateSector(token, editingSector.slug, formData);
            } else {
                await api.createSector(token, formData);
            }

            setIsDialogOpen(false);
            fetchSectors();
        } catch (error) {
            console.error("Error saving sector:", error);
            alert("Failed to save sector. Make sure the slug is unique.");
        }
    };

    const handleDelete = async (slug: string) => {
        if (!confirm("Are you sure you want to delete this sector? This may affect data linked to it.")) return;

        try {
            const token = localStorage.getItem("access_token");
            if (!token) return;
            await api.deleteSector(token, slug);
            fetchSectors();
        } catch (error) {
            console.error("Error deleting sector:", error);
            alert("Failed to delete sector.");
        }
    };

    return (
        <div className="max-w-7xl mx-auto p-6 space-y-8 mt-6">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <div className="flex items-center gap-2 mb-2 text-sm text-muted-foreground">
                        <Link href="/admin/data" className="hover:text-foreground flex items-center gap-1">
                            <ArrowLeft className="h-4 w-4" /> Back to Data Management
                        </Link>
                    </div>
                    <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
                        <FolderTree className="h-8 w-8 text-blue-500" /> Manage Sectors
                    </h1>
                </div>

                <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                    <DialogTrigger asChild>
                        <Button onClick={() => handleOpenDialog()} className="bg-primary hover:bg-primary/90">
                            <Plus className="h-4 w-4 mr-2" /> Add Sector
                        </Button>
                    </DialogTrigger>
                    <DialogContent className="sm:max-w-[425px]">
                        <DialogHeader>
                            <DialogTitle>{editingSector ? 'Edit Sector' : 'Create New Sector'}</DialogTitle>
                            <DialogDescription>
                                Defines an industry category available platform-wide.
                            </DialogDescription>
                        </DialogHeader>
                        <div className="grid gap-4 py-4">
                            <div className="grid grid-cols-4 items-center gap-4">
                                <Label htmlFor="name" className="text-right">Name (EN)</Label>
                                <Input id="name" value={formData.name_en} onChange={(e) => setFormData({ ...formData, name_en: e.target.value })} className="col-span-3" />
                            </div>
                            <div className="grid grid-cols-4 items-center gap-4">
                                <Label htmlFor="name_ar" className="text-right">Name (AR)</Label>
                                <Input id="name_ar" value={formData.name_ar} onChange={(e) => setFormData({ ...formData, name_ar: e.target.value })} className="col-span-3 text-right" dir="rtl" />
                            </div>
                            <div className="grid grid-cols-4 items-center gap-4">
                                <Label htmlFor="name_fr" className="text-right">Name (FR)</Label>
                                <Input id="name_fr" value={formData.name_fr} onChange={(e) => setFormData({ ...formData, name_fr: e.target.value })} className="col-span-3" />
                            </div>
                            <div className="grid grid-cols-4 items-center gap-4">
                                <Label htmlFor="slug" className="text-right">Slug URL</Label>
                                <Input id="slug" value={formData.slug} onChange={(e) => setFormData({ ...formData, slug: e.target.value })} className="col-span-3 font-mono text-sm" placeholder="e.g. agriculture" />
                            </div>
                            <div className="grid grid-cols-4 items-center gap-4">
                                <Label htmlFor="icon" className="text-right">Lucide Icon</Label>
                                <Input id="icon" value={formData.icon} onChange={(e) => setFormData({ ...formData, icon: e.target.value })} className="col-span-3" placeholder="e.g. Activity, Briefcase" />
                            </div>
                        </div>
                        <DialogFooter>
                            <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>Cancel</Button>
                            <Button type="button" onClick={handleSave}>Save changes</Button>
                        </DialogFooter>
                    </DialogContent>
                </Dialog>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Platform Sectors</CardTitle>
                    <CardDescription>
                        All industry sectors currently available for analysis.
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="rounded-md border">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>English</TableHead>
                                    <TableHead>Arabic</TableHead>
                                    <TableHead>French</TableHead>
                                    <TableHead>URL Slug</TableHead>
                                    <TableHead>Status</TableHead>
                                    <TableHead className="text-right">Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {isLoading ? (
                                    <TableRow>
                                        <TableCell colSpan={6} className="text-center py-8">
                                            Loading sectors...
                                        </TableCell>
                                    </TableRow>
                                ) : sectors.length === 0 ? (
                                    <TableRow>
                                        <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">
                                            No sectors found.
                                        </TableCell>
                                    </TableRow>
                                ) : (
                                    sectors.map((sector) => (
                                        <TableRow key={sector.id}>
                                            <TableCell className="font-medium">{sector.name_en}</TableCell>
                                            <TableCell className="text-right font-arabic" dir="rtl">{sector.name_ar}</TableCell>
                                            <TableCell>{sector.name_fr}</TableCell>
                                            <TableCell><Badge variant="secondary" className="font-mono">{sector.slug}</Badge></TableCell>
                                            <TableCell>
                                                {sector.is_active ?
                                                    <Badge className="bg-green-100 text-green-800 hover:bg-green-100">Active</Badge> :
                                                    <Badge variant="destructive">Inactive</Badge>
                                                }
                                            </TableCell>
                                            <TableCell className="text-right">
                                                <DropdownMenu>
                                                    <DropdownMenuTrigger asChild>
                                                        <Button variant="ghost" className="h-8 w-8 p-0">
                                                            <span className="sr-only">Open menu</span>
                                                            <MoreHorizontal className="h-4 w-4" />
                                                        </Button>
                                                    </DropdownMenuTrigger>
                                                    <DropdownMenuContent align="end">
                                                        <DropdownMenuLabel>Actions</DropdownMenuLabel>
                                                        <DropdownMenuItem onClick={() => handleOpenDialog(sector)}>
                                                            <Pencil className="mr-2 h-4 w-4" /> Edit
                                                        </DropdownMenuItem>
                                                        <DropdownMenuSeparator />
                                                        <DropdownMenuItem onClick={() => handleDelete(sector.slug)} className="text-red-600 focus:text-red-700">
                                                            <Trash2 className="mr-2 h-4 w-4" /> Delete
                                                        </DropdownMenuItem>
                                                    </DropdownMenuContent>
                                                </DropdownMenu>
                                            </TableCell>
                                        </TableRow>
                                    ))
                                )}
                            </TableBody>
                        </Table>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
