import AdminLayout from "@/components/admin/AdminLayout";
import { Metadata } from "next";

export const metadata: Metadata = {
    title: "Admin Panel | Boussole",
    description: "Boussole Platform Administration",
};

export default function Layout({ children }: { children: React.ReactNode }) {
    return <AdminLayout>{children}</AdminLayout>;
}
