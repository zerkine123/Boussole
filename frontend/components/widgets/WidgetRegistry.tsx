"use client";

import { DynamicKPICard } from "./DynamicKPICard";
import { DynamicLineChart } from "./DynamicLineChart";
import { DynamicBarChart } from "./DynamicBarChart";
import { DynamicChoroplethMap } from "./DynamicChoroplethMap";
import { DynamicDataTable } from "./DynamicDataTable";
import { DynamicRankingCard } from "./DynamicRankingCard";
import { DynamicGrowthIndicator } from "./DynamicGrowthIndicator";
import { DynamicInsightPanel } from "./DynamicInsightPanel";
import { DynamicFilterPanel } from "./DynamicFilterPanel";
import { DynamicExecutiveSnapshot } from "./DynamicExecutiveSnapshot";
import { DynamicPieChart } from "./DynamicPieChart";
import { DynamicStackedAreaChart } from "./DynamicStackedAreaChart";
import { DynamicRadarChart } from "./DynamicRadarChart";
import { DynamicComposedChart } from "./DynamicComposedChart";
import { DynamicScatterPlot } from "./DynamicScatterPlot";
import { DynamicTreemap } from "./DynamicTreemap";
import { DynamicFunnelChart } from "./DynamicFunnelChart";
import { DynamicComparisonCard } from "./DynamicComparisonCard";
import { DynamicGaugeCard } from "./DynamicGaugeCard";
import { DynamicMetricGrid } from "./DynamicMetricGrid";
import { DynamicSentimentTimeline } from "./DynamicSentimentTimeline";

export const WIDGET_REGISTRY: Record<string, React.FC<any>> = {
    kpi_card: DynamicKPICard,
    line_chart: DynamicLineChart,
    bar_chart: DynamicBarChart,
    choropleth_map: DynamicChoroplethMap,
    data_table: DynamicDataTable,
    ranking_card: DynamicRankingCard,
    growth_indicator: DynamicGrowthIndicator,
    insight_panel: DynamicInsightPanel,
    filter_panel: DynamicFilterPanel,
    executive_snapshot: DynamicExecutiveSnapshot,
    pie_chart: DynamicPieChart,
    stacked_area_chart: DynamicStackedAreaChart,
    radar_chart: DynamicRadarChart,
    composed_chart: DynamicComposedChart,
    scatter_plot: DynamicScatterPlot,
    treemap: DynamicTreemap,
    funnel_chart: DynamicFunnelChart,
    comparison_card: DynamicComparisonCard,
    gauge_card: DynamicGaugeCard,
    metric_grid: DynamicMetricGrid,
    sentiment_timeline: DynamicSentimentTimeline,
};

export function WidgetRenderer({ widget }: { widget: any }) {
    const Component = WIDGET_REGISTRY[widget.component];

    if (!Component) {
        console.warn(`[WidgetRegistry] Unknown component: ${widget.component}`);
        return (
            <div className="p-4 border border-dashed border-red-300 rounded-md bg-red-50 text-red-800 text-sm">
                Error: Unknown widget <b>{widget.component}</b>
            </div>
        );
    }

    return <Component {...widget} />;
}
