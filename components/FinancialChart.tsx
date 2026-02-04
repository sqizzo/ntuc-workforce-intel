"use client";

import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

interface FinancialChartProps {
  data: Array<{
    date: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  }>;
  companyName: string;
  ticker: string;
  summary?: {
    company_name: string;
    sector: string;
    industry: string;
    employees: number;
    market_cap: number;
    pe_ratio: number;
    revenue: number;
    profit_margin: number;
    current_price: number;
    currency: string;
    country: string;
    description: string;
  };
  actualWorkforce?: {
    employee_count: number;
    affected_workers?: number;
    source_confidence: string;
    context: string;
    is_subsidiary_data: boolean;
  };
}

const FinancialChart: React.FC<FinancialChartProps> = ({
  data,
  companyName,
  ticker,
  summary,
  actualWorkforce,
}) => {
  // Format data for the chart
  const chartData = data.map((item) => ({
    date: new Date(item.date).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    }),
    close: parseFloat(item.close.toFixed(2)),
    volume: item.volume,
  }));

  // Calculate price change
  const firstPrice = data[0]?.close || 0;
  const lastPrice = data[data.length - 1]?.close || 0;
  const priceChange = lastPrice - firstPrice;
  const priceChangePercent = ((priceChange / firstPrice) * 100).toFixed(2);
  const isPositive = priceChange >= 0;

  // Format large numbers
  const formatNumber = (num: number, decimals = 2): string => {
    if (num >= 1e12) return `$${(num / 1e12).toFixed(decimals)}T`;
    if (num >= 1e9) return `$${(num / 1e9).toFixed(decimals)}B`;
    if (num >= 1e6) return `$${(num / 1e6).toFixed(decimals)}M`;
    if (num >= 1e3) return `$${(num / 1e3).toFixed(decimals)}K`;
    return `$${num.toFixed(decimals)}`;
  };

  const formatPercent = (num: number): string => {
    return `${(num * 100).toFixed(2)}%`;
  };

  return (
    <div className="space-y-6">
      {/* Price Chart */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h3 className="text-lg font-bold text-slate-900 mb-1 flex items-center">
              <i className="fas fa-chart-line text-blue-600 mr-2"></i>
              Stock Price Chart
            </h3>
            <p className="text-sm text-slate-500 font-mono">{ticker}</p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-slate-900">
              ${lastPrice.toFixed(2)}
            </div>
            <div
              className={`text-sm font-bold ${isPositive ? "text-green-600" : "text-red-600"}`}
            >
              {isPositive ? "+" : ""}
              {priceChange.toFixed(2)} ({isPositive ? "+" : ""}
              {priceChangePercent}%)
            </div>
          </div>
        </div>

        <div className="h-64 mb-4">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis
                dataKey="date"
                tick={{ fill: "#94a3b8", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tick={{ fill: "#94a3b8", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
                domain={["auto", "auto"]}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "white",
                  border: "1px solid #e2e8f0",
                  borderRadius: "8px",
                  fontSize: "12px",
                }}
                formatter={(value: any) => [`$${value}`, "Close Price"]}
              />
              <Legend wrapperStyle={{ fontSize: "12px", paddingTop: "10px" }} />
              <Line
                type="monotone"
                dataKey="close"
                stroke={isPositive ? "#10b981" : "#ef4444"}
                strokeWidth={2}
                dot={false}
                name="Close Price"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="grid grid-cols-4 gap-4 pt-4 border-t border-slate-100">
          <div>
            <div className="text-xs text-slate-500 mb-1">High</div>
            <div className="text-sm font-bold text-slate-900">
              ${Math.max(...data.map((d) => d.high)).toFixed(2)}
            </div>
          </div>
          <div>
            <div className="text-xs text-slate-500 mb-1">Low</div>
            <div className="text-sm font-bold text-slate-900">
              ${Math.min(...data.map((d) => d.low)).toFixed(2)}
            </div>
          </div>
          <div>
            <div className="text-xs text-slate-500 mb-1">Avg Volume</div>
            <div className="text-sm font-bold text-slate-900">
              {(
                data.reduce((sum, d) => sum + d.volume, 0) / data.length
              ).toLocaleString(undefined, { maximumFractionDigits: 0 })}
            </div>
          </div>
          <div>
            <div className="text-xs text-slate-500 mb-1">Period</div>
            <div className="text-sm font-bold text-slate-900">
              {data.length} days
            </div>
          </div>
        </div>
      </div>

      {/* Financial Summary */}
      {summary && (
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
          <h3 className="text-lg font-bold text-slate-900 mb-6 flex items-center">
            <i className="fas fa-chart-bar text-purple-600 mr-2"></i>
            Financial Summary
          </h3>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
            {/* Market Cap */}
            <div className="bg-linear-to-br from-blue-50 to-blue-100 p-4 rounded-xl">
              <div className="text-xs text-blue-700 font-bold mb-2 uppercase tracking-wide">
                Market Cap
              </div>
              <div className="text-xl font-bold text-blue-900">
                {formatNumber(summary.market_cap)}
              </div>
            </div>

            {/* Revenue */}
            <div className="bg-linear-to-br from-green-50 to-green-100 p-4 rounded-xl">
              <div className="text-xs text-green-700 font-bold mb-2 uppercase tracking-wide">
                Revenue
              </div>
              <div className="text-xl font-bold text-green-900">
                {formatNumber(summary.revenue)}
              </div>
            </div>

            {/* P/E Ratio */}
            <div className="bg-linear-to-br from-purple-50 to-purple-100 p-4 rounded-xl">
              <div className="text-xs text-purple-700 font-bold mb-2 uppercase tracking-wide">
                P/E Ratio
              </div>
              <div className="text-xl font-bold text-purple-900">
                {summary.pe_ratio ? summary.pe_ratio.toFixed(2) : "N/A"}
              </div>
            </div>

            {/* Profit Margin */}
            <div className="bg-linear-to-br from-orange-50 to-orange-100 p-4 rounded-xl">
              <div className="text-xs text-orange-700 font-bold mb-2 uppercase tracking-wide">
                Profit Margin
              </div>
              <div className="text-xl font-bold text-orange-900">
                {summary.profit_margin
                  ? formatPercent(summary.profit_margin)
                  : "N/A"}
              </div>
            </div>

            {/* Employees */}
            <div className="bg-linear-to-br from-cyan-50 to-cyan-100 p-4 rounded-xl relative">
              <div className="text-xs text-cyan-700 font-bold mb-2 uppercase tracking-wide flex items-center">
                <i className="fas fa-users mr-1"></i>
                Employees
              </div>
              <div className="text-xl font-bold text-cyan-900">
                {actualWorkforce && actualWorkforce.employee_count
                  ? `~${actualWorkforce.employee_count.toLocaleString()}`
                  : summary.employees
                    ? summary.employees.toLocaleString()
                    : "N/A"}
              </div>
              {actualWorkforce &&
                actualWorkforce.employee_count &&
                summary.employees &&
                actualWorkforce.employee_count !== summary.employees && (
                  <div className="text-xs text-cyan-600 mt-1">
                    Parent co: {summary.employees}
                  </div>
                )}
            </div>

            {/* Current Price */}
            <div className="bg-linear-to-br from-pink-50 to-pink-100 p-4 rounded-xl">
              <div className="text-xs text-pink-700 font-bold mb-2 uppercase tracking-wide">
                Current Price
              </div>
              <div className="text-xl font-bold text-pink-900">
                ${summary.current_price.toFixed(2)}
              </div>
            </div>
          </div>

          {/* Additional Info */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6 pt-6 border-t border-slate-100">
            <div>
              <div className="text-xs text-slate-500 font-bold mb-1">
                Sector
              </div>
              <div className="text-sm text-slate-900 font-medium">
                {summary.sector || "N/A"}
              </div>
            </div>
            <div>
              <div className="text-xs text-slate-500 font-bold mb-1">
                Industry
              </div>
              <div className="text-sm text-slate-900 font-medium">
                {summary.industry || "N/A"}
              </div>
            </div>
            <div>
              <div className="text-xs text-slate-500 font-bold mb-1">
                Country
              </div>
              <div className="text-sm text-slate-900 font-medium">
                {summary.country || "N/A"}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FinancialChart;
