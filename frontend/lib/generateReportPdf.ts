// ==============================================
// Professional PDF Report Generator
// ==============================================
// Generates a stylish, green-branded PDF report
// from the AI-generated dynamic layout data.

import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";

// ── Brand Colors ──
const COLORS = {
    primary: [5, 150, 105] as [number, number, number],       // #059669 emerald-600
    primaryDark: [4, 120, 87] as [number, number, number],     // #047857 emerald-700
    primaryDeep: [6, 78, 59] as [number, number, number],      // #064e3b emerald-900
    accent: [16, 185, 129] as [number, number, number],        // #10b981 emerald-500
    light: [209, 250, 229] as [number, number, number],        // #d1fae5 emerald-100
    ultraLight: [236, 253, 245] as [number, number, number],   // #ecfdf5 emerald-50
    white: [255, 255, 255] as [number, number, number],
    black: [15, 23, 42] as [number, number, number],           // slate-900
    gray: [100, 116, 139] as [number, number, number],         // slate-500
    grayLight: [226, 232, 240] as [number, number, number],    // slate-200
    amber: [245, 158, 11] as [number, number, number],         // amber-500
};

interface WidgetData {
    type: string;
    title?: string;
    subtitle?: string;
    data?: any;
    config?: Record<string, any>;
}

interface LayoutData {
    query: string;
    title: string;
    subtitle: string;
    icon: string;
    topic?: string;
    subtopic?: string;
    location?: string;
    location_name?: string;
    widgets: WidgetData[];
}

export function generateReportPdf(layout: LayoutData) {
    const doc = new jsPDF({
        orientation: "portrait",
        unit: "mm",
        format: "a4",
    });

    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    const margin = 15;
    const contentWidth = pageWidth - margin * 2;
    let y = 0;

    // ── Helper: Check page break
    const checkPageBreak = (neededHeight: number) => {
        if (y + neededHeight > pageHeight - 20) {
            doc.addPage();
            y = 20;
            drawPageDecoration();
        }
    };

    // ── Helper: Draw subtle page decorations
    const drawPageDecoration = () => {
        // Top accent line
        doc.setFillColor(...COLORS.primary);
        doc.rect(0, 0, pageWidth, 3, "F");

        // Subtle corner accent bottom-right
        doc.setFillColor(...COLORS.ultraLight);
        doc.circle(pageWidth + 10, pageHeight + 10, 40, "F");

        // Page footer line
        doc.setDrawColor(...COLORS.grayLight);
        doc.setLineWidth(0.3);
        doc.line(margin, pageHeight - 12, pageWidth - margin, pageHeight - 12);

        // Footer text
        doc.setFont("helvetica", "normal");
        doc.setFontSize(7);
        doc.setTextColor(...COLORS.gray);
        doc.text(
            "Boussole — AI-Powered Market Intelligence Platform",
            margin,
            pageHeight - 8
        );
        doc.text(
            `Generated: ${new Date().toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })}`,
            pageWidth - margin,
            pageHeight - 8,
            { align: "right" }
        );
    };

    // ══════════════════════════════════════
    //  PAGE 1: Cover / Hero Section
    // ══════════════════════════════════════

    // Full green header block
    doc.setFillColor(...COLORS.primaryDeep);
    doc.rect(0, 0, pageWidth, 95, "F");

    // Gradient overlay effect (lighter green band)
    doc.setFillColor(...COLORS.primaryDark);
    doc.rect(0, 0, pageWidth, 3, "F");

    // Decorative circles (subtle watermark effect)
    doc.setFillColor(8, 90, 65); // slightly lighter than primaryDeep for subtle contrast
    doc.circle(pageWidth - 30, 25, 35, "F");
    doc.circle(pageWidth - 60, 55, 20, "F");
    doc.circle(30, 70, 25, "F");

    // Logo / Brand
    doc.setFont("helvetica", "bold");
    doc.setFontSize(10);
    doc.setTextColor(...COLORS.accent);
    y = 18;
    doc.text("BOUSSOLE", margin + 1, y);

    // Small tagline
    doc.setFont("helvetica", "normal");
    doc.setFontSize(7);
    doc.setTextColor(167, 243, 208); // emerald-300 for tagline
    doc.text("AI-Powered Market Intelligence", margin + 1, y + 5);

    // Main Title
    doc.setFont("helvetica", "bold");
    doc.setFontSize(22);
    doc.setTextColor(...COLORS.white);
    y = 45;
    const titleLines = doc.splitTextToSize(layout.title, contentWidth - 10);
    doc.text(titleLines, margin + 1, y);
    y += titleLines.length * 9;

    // Subtitle
    doc.setFont("helvetica", "normal");
    doc.setFontSize(10);
    doc.setTextColor(209, 250, 229);
    const subtitleLines = doc.splitTextToSize(layout.subtitle, contentWidth - 10);
    doc.text(subtitleLines, margin + 1, y + 3);
    y = 95;

    // Report metadata bar
    doc.setFillColor(...COLORS.ultraLight);
    doc.rect(0, y, pageWidth, 16, "F");
    doc.setDrawColor(...COLORS.light);
    doc.setLineWidth(0.3);
    doc.line(0, y + 16, pageWidth, y + 16);

    doc.setFont("helvetica", "normal");
    doc.setFontSize(7.5);
    doc.setTextColor(...COLORS.primaryDark);

    const metaItems = [
        `📋 Report Type: AI-Generated Analysis`,
        `🔍 Query: "${layout.query}"`,
        layout.topic ? `📁 Topic: ${layout.topic}` : null,
        layout.location_name ? `📍 Location: ${layout.location_name}` : null,
    ].filter(Boolean) as string[];

    let metaX = margin;
    metaItems.forEach((item) => {
        doc.text(item, metaX, y + 10);
        metaX += doc.getTextWidth(item) + 12;
        if (metaX > pageWidth - margin - 30) {
            metaX = margin;
        }
    });

    y += 24;

    // Page decoration for first page
    drawPageDecoration();

    // ══════════════════════════════════════
    //  CONTENT: Render each widget
    // ══════════════════════════════════════

    for (const widget of layout.widgets) {
        switch (widget.type) {
            case "hero":
                // Already rendered as the cover — skip
                break;

            case "kpi_grid":
                renderKPIGrid(doc, widget, margin, contentWidth, y, checkPageBreak);
                y += 42;
                break;

            case "bar_chart":
                checkPageBreak(70);
                renderBarChartTable(doc, widget, margin, contentWidth, y);
                y += 12 + (widget.data?.length || 0) * 8 + 18;
                break;

            case "line_chart":
                checkPageBreak(70);
                renderLineChartTable(doc, widget, margin, contentWidth, y);
                y += 12 + (widget.data?.length || 0) * 8 + 18;
                break;

            case "insight_card":
                checkPageBreak(60);
                renderInsights(doc, widget, margin, contentWidth, y);
                y += 12 + (widget.data?.length || 0) * 12 + 10;
                break;

            default:
                break;
        }
    }

    // ── Final: Disclaimer
    checkPageBreak(30);
    y += 8;
    doc.setDrawColor(...COLORS.grayLight);
    doc.setLineWidth(0.3);
    doc.line(margin, y, pageWidth - margin, y);
    y += 6;
    doc.setFont("helvetica", "italic");
    doc.setFontSize(7);
    doc.setTextColor(...COLORS.gray);
    const disclaimer = "Disclaimer: This report was generated by Boussole's AI engine using publicly available data and statistical models. Figures are estimates and should be verified with official sources before making business decisions.";
    const disclaimerLines = doc.splitTextToSize(disclaimer, contentWidth);
    doc.text(disclaimerLines, margin, y);

    // ── Save
    const filename = `boussole-report-${layout.topic || "analysis"}-${Date.now()}.pdf`;
    doc.save(filename);
}

// ══════════════════════════════════════
//  Widget Renderers
// ══════════════════════════════════════

function renderSectionTitle(
    doc: jsPDF,
    title: string,
    x: number,
    y: number
) {
    // Green accent bar
    doc.setFillColor(...COLORS.primary);
    doc.roundedRect(x, y, 3, 10, 1.5, 1.5, "F");

    doc.setFont("helvetica", "bold");
    doc.setFontSize(11);
    doc.setTextColor(...COLORS.black);
    doc.text(title, x + 7, y + 7);
}

function renderKPIGrid(
    doc: jsPDF,
    widget: WidgetData,
    margin: number,
    contentWidth: number,
    y: number,
    checkPageBreak: (h: number) => void
) {
    checkPageBreak(45);

    renderSectionTitle(doc, "Key Performance Indicators", margin, y);
    y += 16;

    const kpis: Array<{ label: string; value: string; trend: string; change: string }> =
        widget.data || [];

    const kpiWidth = (contentWidth - 6) / Math.min(kpis.length, 4);

    kpis.forEach((kpi, i) => {
        const kpiX = margin + i * (kpiWidth + 2);

        // KPI card background
        doc.setFillColor(...COLORS.ultraLight);
        doc.roundedRect(kpiX, y, kpiWidth - 2, 22, 2, 2, "F");

        // Left accent bar
        doc.setFillColor(...COLORS.primary);
        doc.roundedRect(kpiX, y, 2, 22, 1, 1, "F");

        // Label
        doc.setFont("helvetica", "normal");
        doc.setFontSize(7);
        doc.setTextColor(...COLORS.gray);
        doc.text(kpi.label.toUpperCase(), kpiX + 6, y + 6);

        // Value
        doc.setFont("helvetica", "bold");
        doc.setFontSize(14);
        doc.setTextColor(...COLORS.black);
        doc.text(kpi.value, kpiX + 6, y + 14);

        // Trend
        const trendColor = kpi.trend === "up"
            ? COLORS.primary
            : kpi.trend === "down"
                ? [239, 68, 68] as [number, number, number]
                : COLORS.gray;
        const trendIcon = kpi.trend === "up" ? "▲" : kpi.trend === "down" ? "▼" : "—";

        doc.setFont("helvetica", "bold");
        doc.setFontSize(7);
        doc.setTextColor(...trendColor);
        doc.text(`${trendIcon} ${kpi.change}`, kpiX + 6, y + 19);
    });
}

function renderBarChartTable(
    doc: jsPDF,
    widget: WidgetData,
    margin: number,
    contentWidth: number,
    y: number
) {
    renderSectionTitle(doc, widget.title || "Distribution", margin, y);
    y += 14;

    const data: Array<{ name: string; value: number }> = widget.data || [];

    // Find max for visual bars
    const maxVal = Math.max(...data.map((d) => d.value), 1);

    autoTable(doc, {
        startY: y,
        margin: { left: margin, right: margin },
        head: [["Category", "Value", ""]],
        body: data.map((d) => [
            d.name,
            d.value.toLocaleString(),
            "", // visual bar placeholder
        ]),
        theme: "plain",
        styles: {
            fontSize: 8,
            cellPadding: { top: 3, right: 4, bottom: 3, left: 4 },
            textColor: COLORS.black,
        },
        headStyles: {
            fillColor: COLORS.primaryDeep,
            textColor: COLORS.white,
            fontStyle: "bold",
            fontSize: 7.5,
        },
        alternateRowStyles: {
            fillColor: COLORS.ultraLight,
        },
        columnStyles: {
            0: { cellWidth: contentWidth * 0.35 },
            1: { cellWidth: contentWidth * 0.2, halign: "right", fontStyle: "bold" },
            2: { cellWidth: contentWidth * 0.45 },
        },
        didDrawCell: (hookData: any) => {
            // Draw green bar in the 3rd column for body rows
            if (hookData.section === "body" && hookData.column.index === 2) {
                const cellX = hookData.cell.x + 4;
                const cellY = hookData.cell.y + hookData.cell.height / 2 - 2.5;
                const maxBarWidth = hookData.cell.width - 8;
                const rowData = data[hookData.row.index];
                if (rowData) {
                    const barWidth = (rowData.value / maxVal) * maxBarWidth;

                    // Bar background
                    doc.setFillColor(...COLORS.light);
                    doc.roundedRect(cellX, cellY, maxBarWidth, 5, 1, 1, "F");

                    // Bar fill
                    doc.setFillColor(...COLORS.primary);
                    doc.roundedRect(cellX, cellY, barWidth, 5, 1, 1, "F");
                }
            }
        },
    });
}

function renderLineChartTable(
    doc: jsPDF,
    widget: WidgetData,
    margin: number,
    contentWidth: number,
    y: number
) {
    renderSectionTitle(doc, widget.title || "Trend Data", margin, y);
    y += 14;

    const data: Array<{ year: number; value: number }> = widget.data || [];

    // Calculate YoY change
    const tableData = data.map((d, i) => {
        const prev = i > 0 ? data[i - 1].value : null;
        const change = prev !== null
            ? ((d.value - prev) / prev * 100).toFixed(1)
            : "—";
        const changeStr = prev !== null
            ? (d.value >= prev ? `+${change}%` : `${change}%`)
            : "—";
        return [String(d.year), d.value.toLocaleString(), changeStr];
    });

    autoTable(doc, {
        startY: y,
        margin: { left: margin, right: margin },
        head: [["Year", "Value", "YoY Change"]],
        body: tableData,
        theme: "plain",
        styles: {
            fontSize: 8,
            cellPadding: { top: 3, right: 4, bottom: 3, left: 4 },
            textColor: COLORS.black,
        },
        headStyles: {
            fillColor: COLORS.primaryDeep,
            textColor: COLORS.white,
            fontStyle: "bold",
            fontSize: 7.5,
        },
        alternateRowStyles: {
            fillColor: COLORS.ultraLight,
        },
        columnStyles: {
            0: { cellWidth: contentWidth * 0.25, fontStyle: "bold" },
            1: { cellWidth: contentWidth * 0.4, halign: "right" },
            2: { cellWidth: contentWidth * 0.35, halign: "right" },
        },
        didDrawCell: (hookData: any) => {
            // Color the change column
            if (hookData.section === "body" && hookData.column.index === 2) {
                const val = tableData[hookData.row.index]?.[2];
                if (val && val.startsWith("+")) {
                    doc.setTextColor(...COLORS.primary);
                } else if (val && val.startsWith("-")) {
                    doc.setTextColor(239, 68, 68);
                }
            }
        },
    });
}

function renderInsights(
    doc: jsPDF,
    widget: WidgetData,
    margin: number,
    contentWidth: number,
    y: number
) {
    renderSectionTitle(doc, widget.title || "Key Insights", margin, y);
    y += 14;

    const insights: string[] = widget.data || [];

    // Insights background card
    doc.setFillColor(255, 251, 235); // amber-50
    doc.roundedRect(margin, y, contentWidth, insights.length * 12 + 6, 3, 3, "F");
    doc.setDrawColor(252, 211, 77); // amber-300
    doc.setLineWidth(0.3);
    doc.roundedRect(margin, y, contentWidth, insights.length * 12 + 6, 3, 3, "S");

    y += 6;

    insights.forEach((insight, i) => {
        // Numbered circle
        doc.setFillColor(...COLORS.amber);
        doc.circle(margin + 7, y + 2.5, 3.5, "F");
        doc.setFont("helvetica", "bold");
        doc.setFontSize(7);
        doc.setTextColor(...COLORS.white);
        doc.text(String(i + 1), margin + 7, y + 3.5, { align: "center" });

        // Insight text
        doc.setFont("helvetica", "normal");
        doc.setFontSize(8.5);
        doc.setTextColor(120, 53, 15); // amber-900
        const lines = doc.splitTextToSize(insight, contentWidth - 22);
        doc.text(lines, margin + 14, y + 3.5);
        y += Math.max(lines.length * 5, 10) + 2;
    });
}
