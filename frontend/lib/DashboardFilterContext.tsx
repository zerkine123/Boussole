"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { api } from "@/lib/api";

interface DashboardFilters {
    sector_slug?: string;
    wilaya_code?: string;
    year?: string;
}

interface DashboardFilterContextType {
    filters: DashboardFilters;
    setFilter: (key: keyof DashboardFilters, value: string | undefined) => void;
    clearFilters: () => void;

    // UI options
    availableSectors: any[];
    availableWilayas: any[];
}

const DashboardFilterContext = createContext<DashboardFilterContextType | undefined>(undefined);

export function DashboardFilterProvider({ children }: { children: ReactNode }) {
    const [filters, setFilters] = useState<DashboardFilters>({});
    const [availableSectors, setAvailableSectors] = useState<any[]>([]);
    const [availableWilayas, setAvailableWilayas] = useState<any[]>([]);

    useEffect(() => {
        const fetchFilterOptions = async () => {
            try {
                const token = localStorage.getItem('access_token');
                if (!token) return;

                const data = await api.getOnboardingData(token);
                if (data.available_sectors) setAvailableSectors(data.available_sectors);
                if (data.available_wilayas) setAvailableWilayas(data.available_wilayas);
            } catch (error) {
                console.error("Failed to fetch filter options:", error);
            }
        };
        fetchFilterOptions();
    }, []);

    const setFilter = (key: keyof DashboardFilters, value: string | undefined) => {
        setFilters((prev) => ({
            ...prev,
            [key]: value === "all" ? undefined : value,
        }));
    };

    const clearFilters = () => {
        setFilters({});
    };

    return (
        <DashboardFilterContext.Provider
            value={{
                filters, setFilter, clearFilters,
                availableSectors, availableWilayas
            }}
        >
            {children}
        </DashboardFilterContext.Provider>
    );
}

export function useDashboardFilters() {
    const context = useContext(DashboardFilterContext);
    if (context === undefined) {
        throw new Error("useDashboardFilters must be used within a DashboardFilterProvider");
    }
    return context;
}
